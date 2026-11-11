# Kubernetes Day 1 - Local Cluster Setup

## Goal

Set up and verify a local Kubernetes cluster using Minikube so that the Flask Task API can later be deployed into Kubernetes.

The objective for Day 1 was not to deploy the application yet.  
The objective was to make sure the Kubernetes environment itself was working.

---

## What I did

- Verified that `kubectl` was installed.
- Checked the current Kubernetes context.
- Tried to connect to the current Kubernetes cluster.
- Found that the current context was `minikube`.
- Started Minikube.
- Checked the Kubernetes cluster information.
- Checked the node status.
- Found that the Minikube node was initially `NotReady`.
- Investigated system Pods using `kubectl get pods -A`.
- Found that the default networking component was failing.
- Recreated Minikube using Docker driver and bridge CNI.
- Verified that the Minikube node became `Ready`.

---

## Commands used

### Check kubectl client version

```powershell
kubectl version --client
```

Output:

```text
Client Version: v1.36.1
Kustomize Version: v5.8.1
```

---

### Check current Kubernetes context

```powershell
kubectl config current-context
```

Output:

```text
minikube
```

This showed that `kubectl` was configured to talk to the Minikube cluster.

---

### Check cluster information

```powershell
kubectl cluster-info
```

Initial result:

```text
Unable to connect to the server: dial tcp 127.0.0.1:49211: connectex: No connection could be made because the target machine actively refused it.
```

This meant that the current context was `minikube`, but the Minikube cluster/API server was not running or not reachable.

---

### Start Minikube

```powershell
minikube start
```

Minikube started, but there was a warning:

```text
Failing to connect to https://registry.k8s.io/ from inside the minikube container
```

After this, `kubectl cluster-info` worked and showed that the Kubernetes control plane was reachable.


### Check node status

```powershell
kubectl get nodes
```

Initial output:

```text
NAME       STATUS     ROLES           AGE   VERSION
minikube   NotReady   control-plane   8d    v1.37.0
```

This showed that the cluster existed, but the node was not healthy yet.

---

### Check all Pods across namespaces

```powershell
kubectl get pods -A
```

Output showed:

```text
NAMESPACE     NAME                               READY   STATUS             RESTARTS
kube-system   coredns-559f6c778d-g2xnr           0/1     Pending            0
kube-system   kindnet-sgsf2                      0/1     ImagePullBackOff   0
kube-system   storage-provisioner                0/1     Pending            0
```

This helped identify that the cluster networking component was failing.

---

### Recreate Minikube with bridge CNI

The default networking component `kindnet` failed with image pull errors.  
To fix this, Minikube was recreated with the Docker driver and bridge CNI:

```powershell
minikube delete
minikube start --driver=docker --cni=bridge
```

Output included:

```text
Configuring bridge CNI (Container Networking Interface)
Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

---

### Verify node status again

```powershell
kubectl get nodes
```

Final successful output:

```text
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   16s   v1.37.0
```

This confirmed that the local Kubernetes cluster was ready.

---

## What passed

- `kubectl` was installed successfully.
- The current context was identified as `minikube`.
- Minikube was started.
- Kubernetes control plane became reachable.
- The node issue was diagnosed using `kubectl get pods -A`.
- Recreating Minikube with bridge CNI fixed the node readiness issue.
- Final node status became `Ready`.

---

## Issues encountered and fixes

### Issue 1 - Kubernetes API server was not reachable

Initial command:

```powershell
kubectl cluster-info
```

Error:

```text
Unable to connect to the server: dial tcp 127.0.0.1:49211: connectex: No connection could be made because the target machine actively refused it.
```

### Reason

`kubectl` was pointing to the `minikube` context, but the Minikube cluster was not running or the API server was not reachable.

### Fix

Started Minikube:

```powershell
minikube start
```

After this, the Kubernetes control plane became reachable.

---

### Issue 2 - Minikube node was NotReady

Command:

```powershell
kubectl get nodes
```

Output:

```text
minikube   NotReady
```

### Reason

The cluster networking component was not working correctly.

This was identified using:

```powershell
kubectl get pods -A
```

The important failing Pod was:

```text
kindnet   ImagePullBackOff
```

Because the CNI/networking component was failing, the node could not become fully ready and other Pods such as CoreDNS stayed `Pending`.

---

### Issue 3 - kindnet failed with ImagePullBackOff / ErrImagePull

The system Pods showed:

```text
kindnet   ImagePullBackOff
```

or:

```text
kindnet   ErrImagePull
```

### Reason

Minikube could not pull the networking image needed for `kindnet`.

There was also this warning during startup:

```text
Failing to connect to https://registry.k8s.io/ from inside the minikube container
```

This suggested that the Minikube container had trouble reaching external registries.

### Fix

Recreated Minikube with bridge CNI instead of the failing default networking setup:

```powershell
minikube delete
minikube start --driver=docker --cni=bridge
```

After that, the node became ready.

---

## Key Kubernetes concepts learned

### `kubectl`

`kubectl` is the command-line tool used to communicate with a Kubernetes cluster.

Examples:

```powershell
kubectl get nodes
kubectl get pods -A
kubectl cluster-info
```

---

### Kubernetes context

A context tells `kubectl` which cluster to talk to.

Command used:

```powershell
kubectl config current-context
```

Output:

```text
minikube
```

This meant that all `kubectl` commands were being sent to the Minikube cluster.

---

### Minikube

Minikube runs a local Kubernetes cluster on a development machine.

In this setup, Minikube was started using the Docker driver, meaning the Kubernetes cluster runs inside Docker.

---

### Node

A node is a machine where Kubernetes runs workloads.

In Minikube, there is usually one node:

```text
minikube
```

The node must be `Ready` before applications should be deployed.

---

### Control plane

The control plane manages the Kubernetes cluster.

When this command worked:

```powershell
kubectl cluster-info
```

it showed that the Kubernetes control plane was reachable.

---

### Namespace

A namespace is a logical grouping inside Kubernetes.

The command:

```powershell
kubectl get pods -A
```

means:

```text
show Pods from all namespaces
```

System components run in the `kube-system` namespace.

---

### Pod

A Pod is the smallest deployable unit in Kubernetes.

System components such as CoreDNS, kube-proxy, and kindnet run as Pods.

---

### CNI

CNI means **Container Network Interface**.

Kubernetes uses CNI plugins to provide networking for Pods.

CNI is responsible for things like:

- assigning Pod IP addresses,
- allowing Pods to communicate,
- enabling cluster networking.

Without a working CNI, the node can stay `NotReady`.

---

### Bridge CNI

Bridge CNI is a simpler networking setup that connects Pods through a bridge network.

It was used because the default `kindnet` CNI image could not be pulled.

Command used:

```powershell
minikube start --driver=docker --cni=bridge
```

---

### ImagePullBackOff

`ImagePullBackOff` means Kubernetes tried to pull a container image but failed, and is now waiting before retrying.

In this case, `kindnet` had `ImagePullBackOff`, which affected the whole cluster networking setup.

---

### Pending

`Pending` means Kubernetes has not been able to fully schedule or start the Pod.

CoreDNS and storage-provisioner were stuck in `Pending` because the node/networking setup was not healthy.

---

## Important learning

A Kubernetes cluster should not be used for application deployment until the node is `Ready`.

The most important Day 1 success check was:

```powershell
kubectl get nodes
```

Final successful result:

```text
minikube   Ready
```

---

## Final status

Kubernetes local cluster is now ready.

Final verified state:

```text
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   16s   v1.37.0
```

---

## Next step

Load the local Docker image `docker-task-api:latest` into Minikube and deploy it as a Kubernetes Deployment.