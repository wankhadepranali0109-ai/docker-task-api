# Kubernetes Day 2 - Deploy Flask API with a Deployment

## Goal

Deploy the existing Dockerised Flask Task API into the local Minikube Kubernetes cluster.

The Docker image was built and tested locally first. The goal was then to run the same image inside Kubernetes as a Pod managed by a Deployment.

---

## What I did

- Confirmed the Minikube node was `Ready`.
- Loaded the local Docker image into Minikube.
- Created a Kubernetes Deployment manifest.
- Applied the Deployment.
- Verified the Deployment, ReplicaSet, and Pod.
- Viewed Deployment details and application logs.
- Entered the running Pod using `kubectl exec`.

---

## Load Docker image into Minikube

Command used:

```powershell
minikube image load docker-task-api:latest
```

This copies the image built in local Docker Desktop into Minikube’s internal image store.

Verified using:

```powershell
minikube image ls
```

Relevant output:

```text
docker.io/library/docker-task-api:latest
```

Minikube adds the `docker.io/library/` prefix to local image names. It still refers to the same image:

```text
docker-task-api:latest
```

---

## Deployment manifest

Created:

```text
k8s/deployment.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-api-deployment
  labels:
    app: task-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: task-api
  template:
    metadata:
      labels:
        app: task-api
    spec:
      containers:
        - name: task-api
          image: docker-task-api:latest
          imagePullPolicy: Never
          ports:
            - containerPort: 5000
          env:
            - name: PORT
              value: "5000"
```

---

## Deployment YAML explanation

### Resource type

```yaml
apiVersion: apps/v1
kind: Deployment
```

This creates a Kubernetes Deployment. A Deployment manages Pods and works to keep the requested number of replicas running.

### Name and label

```yaml
metadata:
  name: task-api-deployment
  labels:
    app: task-api
```

- `name` identifies the Deployment.
- `labels` are tags used to organise and connect Kubernetes resources.

### Desired replicas

```yaml
spec:
  replicas: 1
```

Kubernetes should keep one Pod running.

### Selector and Pod labels

```yaml
selector:
  matchLabels:
    app: task-api
```

The Deployment manages Pods with the label:

```text
app: task-api
```

```yaml
template:
  metadata:
    labels:
      app: task-api
```

This is the Pod template. The labels must match the selector so the Deployment can manage the Pods it creates.

### Container definition

```yaml
containers:
  - name: task-api
    image: docker-task-api:latest
```

Each Pod runs one container named `task-api`, created from the Docker image `docker-task-api:latest`.

### Image pull policy

```yaml
imagePullPolicy: Never
```

This applies only to the `task-api` container image.

It tells Kubernetes:

> Do not pull this image from Docker Hub or another registry. Use only the image already loaded into Minikube.

This is why the image was loaded first:

```powershell
minikube image load docker-task-api:latest
```

### Container port

```yaml
ports:
  - containerPort: 5000
```

This documents that Flask listens on port `5000` inside the container.

It does not expose the application outside the cluster. A Kubernetes Service will be required for that.

### Environment variable

```yaml
env:
  - name: PORT
    value: "5000"
```

This passes `PORT=5000` into the container. The Flask app reads this variable to choose its listening port.

---

## Apply Deployment

Command used:

```powershell
kubectl apply -f k8s/deployment.yaml
```

Output:

```text
deployment.apps/task-api-deployment created
```

---

## Verification commands

```powershell
kubectl get deployments
kubectl get pods
kubectl get rs
kubectl describe deployment task-api-deployment
kubectl logs deployment/task-api-deployment
```

---

## What passed

Deployment status:

```text
NAME                  READY   UP-TO-DATE   AVAILABLE
task-api-deployment   1/1     1            1
```

Pod status:

```text
NAME                                   READY   STATUS    RESTARTS
task-api-deployment-6f658d49c9-ssbbh   1/1     Running   0
```

Deployment details showed:

```text
Replicas: 1 desired | 1 updated | 1 total | 1 available | 0 unavailable
Available: True
Progressing: True
```

The ReplicaSet was created successfully:

```text
task-api-deployment-6f658d49c9   1   1   1
```

Flask logs confirmed the app started inside the Pod:

```text
Running on http://10.244.0.3:5000
```

`10.244.0.3` is the Pod’s internal cluster IP.

---

## Kubernetes resource flow

```text
Deployment
  → ReplicaSet
    → Pod
      → task-api container
        → docker-task-api:latest image
```

### Deployment

Declares the desired application state, such as one replica.

### ReplicaSet

Ensures the requested number of Pods exists.

### Pod

The smallest deployable Kubernetes unit. It runs the Flask container.

---

## Inspecting inside the Pod

Command used:

```powershell
kubectl exec -it deployment/task-api-deployment -- sh
```

Explanation:

| Part | Meaning |
|---|---|
| `kubectl exec` | Runs a command inside a running Pod container. |
| `-it` | Opens an interactive terminal. |
| `deployment/task-api-deployment` | Selects a Pod managed by the Deployment. |
| `--` | Separates `kubectl` options from the command inside the Pod. |
| `sh` | Opens a shell inside the container. |

Useful commands inside the Pod:

```sh
echo $PORT
python --version
ls
pwd
```

Exit the Pod shell:

```sh
exit
```

---


## Key learnings

- A Deployment describes the desired state of an application.
- A Deployment creates/manages a ReplicaSet.
- A ReplicaSet ensures the requested number of Pods exists.
- A Pod runs the actual container.
- `kubectl apply -f` creates or updates Kubernetes resources from YAML.
- `imagePullPolicy: Never` uses only an image already loaded into Minikube.
- `containerPort` documents the container’s port but does not expose the app outside the cluster.
- `kubectl logs` shows application logs.
- `kubectl describe` shows resource configuration, state, and events.
- `kubectl exec -it ... -- sh` opens a shell inside a running Pod.
- Pod IPs are internal and not stable. A Service provides a stable endpoint.

---

## Next step - Kubernetes Day 3: Expose the API with a Service

Create a Kubernetes Service to provide a stable network endpoint for the Flask Task API.

The Service will select Pods with this label:

```yaml
app: task-api
```

It will forward incoming traffic to the Flask container on port `5000`.

Create:

```text
k8s/service.yaml
```

Then:

```powershell
kubectl apply -f k8s/service.yaml
kubectl get services
kubectl get endpoints task-api-service
```

The aim is to make the `/health` endpoint accessible from the browser or PowerShell using a stable Service address, instead of relying on the changing Pod IP.