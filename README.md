# Docker and Kubernetes Task API
A small Flask Task API used to revise Docker and Kubernetes through a connected, hands-on learning project.

The project begins as a local Flask API, then evolves into a containerised application using Docker. It will progressively include image optimisation, networking, PostgreSQL, persistent storage, Docker Compose, registries, and CI/CD.

The same application is also deployed and operated on Kubernetes using Minikube. The Kubernetes track will cover Deployments, Pods, ReplicaSets, Services, ConfigMaps, Secrets, health probes, persistent volumes, scaling, rolling updates, Ingress, Helm/Kustomize, and CI/CD.

Each learning task builds on the previous one and is documented in the Docker and Kubernetes notes folders.

## Current status

### Docker
- Day 1: Built and tested the Flask API locally.
- Day 2: Built a Docker image and ran the API as a container.
- Day 3: Improved the container with `.dockerignore`, environment variables, restart policy, and Docker health check.
- Day 4: Converted the Flask image into a multi-stage build and verified the optimised image runs successfully.
- Day 5: Created a custom Docker bridge network and connected the Flask API container to PostgreSQL using Docker DNS.

### Kubernetes
- Day 1: Set up Minikube local cluster using Docker driver and bridge CNI.
- Day 2: Loaded the local Docker image into Minikube and deployed the Flask Task API using a Kubernetes Deployment.
- Day 3: Exposed the Flask API with a NodePort Service and accessed the `/health` endpoint from the browser.

## Tech stack

- Python
- Flask
- PostgreSQL
- Docker
- Kubernetes
- Minikube

## Project structure

```text
docker-task-api/
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── README.md
├── docker-notes/
│   ├── day-01-local-flask-api.md
│   ├── day-02-docker-image-container.md
│   ├── day-03-container-improvements.md
│   ├── day-04-multi-stage-build.md
│   └── day-05-docker-networking.md
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
└── k8s-notes/
    ├── day-01-local-cluster.md
    ├── day-02-deployment.md
    └── day-03-service.md
```

## Learning notes

### Docker

- [Docker Day 1 - Local Flask API](docker-notes/day-01-local-flask-api.md)
- [Docker Day 2 - Docker image and container](docker-notes/day-02-docker-image-container.md)
- [Docker Day 3 - Container improvements](docker-notes/day-03-container-improvements.md)
- [Docker Day 4 - Multi-stage build and image optimisation](docker-notes/day-04-multi-stage-build.md)
- [Docker Day 5 - Custom bridge networking with PostgreSQL](docker-notes/day-05-docker-networking.md)

### Kubernetes

- [Kubernetes Day 1 - Local cluster setup](k8s-notes/day-01-local-cluster.md)
- [Kubernetes Day 2 - Deploy Flask API with a Deployment](k8s-notes/day-02-deployment.md)
- [Kubernetes Day 3 - Expose Flask API with a NodePort Service](k8s-notes/day-03-service.md)