Przygotowanie kontenera

cd src
docker build -t webhook .

Instalacja
kubectl apply -f deployment.yml
kubectl apply -f crds/eips.yml -f webhookmutate.yml
kubectl --namespace=webhook create secret tls webhook-certs --cert=keys/server.crt --key=keys/server.key

Jezeli potrzeba wymienic certy - trzeba wygenerowac nowe klucze do katalogu keys i podmienic cert w webhookmutate.yml oraz zaktualizowac secret/webhook-certs

Przyklady uzycia

Najpierw wgramy crdki

kubectl apply -f examples/eip1.yml -f examples/eip2.yml

Jeden z tych crd spowoduje dopisanie adnotacji od kubeovn do deploymentu nginx w namespace default:
[root@k8sic1 ~]# kubectl create deploy --image=nginx nginx
deployment.apps/nginx created
[root@k8sic1 ~]# kubectl get deploy/nginx -o yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    deployment.kubernetes.io/revision: "1"
  creationTimestamp: "2022-11-02T00:12:58Z"
  generation: 1
  labels:
    app: nginx
  name: nginx
  namespace: default
  resourceVersion: "2551671"
  uid: e091b49c-fe74-45d2-a243-c8d0165d995a
spec:
  progressDeadlineSeconds: 600
  replicas: 1
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: nginx
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      annotations:
        ovn.kubernetes.io/eip: 192.168.124.11
      creationTimestamp: null
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx
        imagePullPolicy: Always
        name: nginx
        resources: {}
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext: {}
      terminationGracePeriodSeconds: 30
status:
  availableReplicas: 1
  conditions:
  - lastTransitionTime: "2022-11-02T00:13:00Z"
    lastUpdateTime: "2022-11-02T00:13:00Z"
    message: Deployment has minimum availability.
    reason: MinimumReplicasAvailable
    status: "True"
    type: Available
  - lastTransitionTime: "2022-11-02T00:12:58Z"
    lastUpdateTime: "2022-11-02T00:13:00Z"
    message: ReplicaSet "nginx-6f694c84b5" has successfully progressed.
    reason: NewReplicaSetAvailable
    status: "True"
    type: Progressing
  observedGeneration: 1
  readyReplicas: 1
  replicas: 1
  updatedReplicas: 1

Jezeli jednak sprobujemy wgrac deployment z istniejaca adnotacja to webhook odrazu uwali taki deploymenmt:

[root@k8sic1 ~]# kubectl apply -f examples/snat-gateway-deploy.yml 
Error from server: error when creating "examples/snat-gateway-deploy.yml": admission webhook "webhook.webhook.svc" denied the request: KubeOVN EIP annotations are prohibited

