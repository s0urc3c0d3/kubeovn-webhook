import base64
import copy
import http
import json
import random

import jsonpatch
from flask import Flask, jsonify, request
import logging
from os import path

import yaml

from kubernetes import client, config

app = Flask(__name__)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route("/mutate", methods=["POST"])
def mutate():
    config.load_incluster_config()

    allowed = True
    try:
        for container_spec in request.json["request"]["object"]["spec"]["template"]["metadata"]["annotations"]:
            if "ovn.kubernetes.io/eip" in container_spec:
                allowed = False
    except KeyError:
        pass
    if (not allowed):
        return jsonify(
            {
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "allowed": False,
                    "uid": request.json["request"]["uid"],
                    "status": {"message": "KubeOVN EIP annotations are prohibited"},
                }
            }
        )

    api = client.CustomObjectsApi()
    eips = api.list_cluster_custom_object(group="kubeovn.io",version="v1",plural="eips")["items"]
    
    spec = request.json["request"]["object"]
    modified_spec = copy.deepcopy(spec)
    ns = request.json["request"]["namespace"]
    deployment_name = request.json["request"]["object"]["metadata"]["name"]
    try:
        for i in eips:
            if (i["spec"]["deployment"] == deployment_name and i["spec"]["namespace"] == ns):
                exists = 0
                for j in modified_spec["spec"]["template"]["metadata"]:
    	            if ("annotations" in j):
                        exists = 1
                if (exists == 0 ):
                    modified_spec["spec"]["template"]["metadata"]["annotations"] = {}
                modified_spec["spec"]["template"]["metadata"]["annotations"]["ovn.kubernetes.io/eip"] = str(
                    i["spec"]["ip"]
                )
    except KeyError:
        pass
    patch = jsonpatch.JsonPatch.from_diff(spec, modified_spec)
    if (patch.to_string() == '[]'):
        return jsonify(
            {
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "allowed": True,
                    "uid": request.json["request"]["uid"],
                    "status": {"message": "No EIP was added"},
                }
            }
        )
    return jsonify(
        {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "allowed": True,
                "uid": request.json["request"]["uid"],
                "patch": base64.b64encode(str(patch).encode()).decode(),
                "patchType": "JSONPatch",
            }
        }
    )


@app.route("/health", methods=["GET"])
def health():
    return ("", http.HTTPStatus.NO_CONTENT)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=443, debug=True)  # pragma: no cover
