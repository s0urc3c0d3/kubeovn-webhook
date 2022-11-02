#!/usr/bin/python3
from os import path

import yaml

from kubernetes import client, config


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    api = client.CustomObjectsApi()
    api.list_cluster_custom_object(group="kubeovn.io",version="v1",plural="eips")["items"]


if __name__ == '__main__':
    main()
