# Kubernetes Day 3 - Expose Flask API with a NodePort Service

## Goal

Make the Flask Task API, which was already running inside the Kubernetes cluster, accessible from a browser or PowerShell.

## Starting point

Previously, the Flask application was deployed into Kubernetes.

```text
Docker image
→ Kubernetes Deployment
→ ReplicaSet
→ Pod
→ Flask container running on port 5000
```

The application was running inside a Pod, but the Pod IP is internal and can change when the Pod restarts. We needed a stable way to access the application.

## What I created

Created a Kubernetes Service:

```text
k8s/service.yaml
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: task-api-service
  labels:
    app: task-api
spec:
  type: NodePort
  selector:
    app: task-api
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
      nodePort: 30080
```

## Why a Service is needed

A Kubernetes Service provides a stable network entry point for Pods.

A Pod can restart and receive a different IP address:

```text
Old Pod IP: 10.244.0.3
New Pod IP: 10.244.0.4
```

Instead of accessing the Pod directly, the Service finds the correct Pod through labels and forwards traffic to it.

```text
task-api-service
→ finds Pods labelled app=task-api
→ forwards request to Flask application
```

## Service types

| Service type | Purpose |
|---|---|
| `ClusterIP` | Allows communication only inside the Kubernetes cluster. |
| `NodePort` | Exposes a Service through a port on the Kubernetes node. |
| `LoadBalancer` | Uses an external cloud load balancer. |
| `ExternalName` | Maps a Kubernetes Service name to an external DNS name. |

## Service selected

I used a `NodePort` Service:

```yaml
type: NodePort
```

I selected NodePort because this project is running locally in Minikube and I needed to access the Flask API from my Windows browser.

## Service YAML explanation

### Resource type

```yaml
apiVersion: v1
kind: Service
```

This creates a Kubernetes Service resource.

### Service name

```yaml
metadata:
  name: task-api-service
```

This gives the Service a stable name:

```text
task-api-service
```

Other Pods inside the Kubernetes cluster can use this name to reach the Flask API.

### Service type

```yaml
spec:
  type: NodePort
```

This exposes the Service through a port on the Minikube node, allowing requests from outside the cluster.

### Pod selector

```yaml
selector:
  app: task-api
```

The Service looks for Pods with this label:

```text
app=task-api
```

The Deployment created Pods with the same label:

```yaml
template:
  metadata:
    labels:
      app: task-api
```

This is how the Service knows which Pods should receive incoming traffic.

```text
Deployment creates Pod
Pod label: app=task-api
        ↓
Service selector: app=task-api
        ↓
Service sends requests to that Pod
```

### Ports

```yaml
ports:
  - protocol: TCP
    port: 5000
    targetPort: 5000
    nodePort: 30080
```

| Field | Meaning |
|---|---|
| `protocol: TCP` | HTTP requests use TCP. |
| `port: 5000` | The stable Service port inside the Kubernetes cluster. |
| `targetPort: 5000` | The port where Flask runs inside the Pod container. |
| `nodePort: 30080` | The external port opened on the Minikube node. |

## Request flow

When I open the `/health` endpoint in the browser, the request travels like this:

```text
Browser
→ Minikube accessible URL
→ NodePort 30080
→ task-api-service
→ Pod selected through app=task-api label
→ Flask container port 5000
→ /health endpoint
```

## Commands used

Create the Service:

```powershell
kubectl apply -f k8s/service.yaml
```

Output:

```text
service/task-api-service created
```

Check Services:

```powershell
kubectl get services
```

Output:

```text
NAME               TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)
task-api-service   NodePort    10.98.74.132   <none>        5000:30080/TCP
```

Check the endpoint selected by the Service:

```powershell
kubectl get endpoints task-api-service
```

Output:

```text
NAME               ENDPOINTS
task-api-service   10.244.0.4:5000
```

Get the URL accessible from Windows:

```powershell
minikube service task-api-service --url
```

Test in PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:<PORT>/health
```

Test in browser:

```text
http://127.0.0.1:<PORT>/health
```

## What passed

- `task-api-service` was created successfully.
- The Service type was `NodePort`.
- The selector `app: task-api` successfully matched the Flask Pod.
- Kubernetes created an endpoint that pointed to the Pod on port `5000`.
- The Flask `/health` endpoint was accessible from the browser.
- The browser returned:

```json
{
  "status": "ok"
}
```

## Important IP and port details

```text
10.98.74.132
```

This is the Service ClusterIP. It is stable but available only inside the Kubernetes cluster.

```text
10.244.0.4:5000
```

This is the Flask Pod endpoint. The Pod IP can change after restart.

```text
30080
```

This is the NodePort used to allow external traffic to enter through the Minikube node.

## Key learnings

- A Deployment creates and manages Pods, but does not provide a stable external address.
- A Service provides a stable way to access one or more Pods.
- A Service uses labels and selectors to find the right Pods.
- `NodePort` exposes an application outside a local Kubernetes cluster.
- `port`, `targetPort`, and `nodePort` have different roles.
- Pod IPs are temporary, while Services provide stable access.
- The `/health` endpoint returns JSON because the current project is an API, not a frontend application.

## Next step

Continue Docker Day 5: create a custom Docker bridge network, run PostgreSQL in a separate container, and learn container-to-container communication using the database container name.