# Docker Task API

A small Flask Task API used to revise Docker concepts step by step.

The project starts as a simple local Flask API and gradually evolves into a containerised, multi-container application using Docker, networking, volumes, Docker Compose, registries, and CI/CD.

## Current status

### Docker
- Day 1: Built and tested the Flask API locally.
- Day 2: Built a Docker image and ran the API as a container.
- Day 3: Improved the container with `.dockerignore`, environment variables, restart policy, and Docker health check.
- Day 4: Converted the Flask image into a multi-stage build and verified the optimised image runs successfully.

### Kubernetes
- Day 1: Set up Minikube local cluster using Docker driver and bridge CNI.

## Tech stack

- Python
- Flask
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
│   └── day-04-multi-stage-build.md
└── k8s-notes/
    └── day-01-local-cluster.md
```

## Learning notes

### Docker

- [Docker Day 1 - Local Flask API](docker-notes/day-01-local-flask-api.md)
- [Docker Day 2 - Docker image and container](docker-notes/day-02-docker-image-container.md)
- [Docker Day 3 - Container improvements](docker-notes/day-03-container-improvements.md)
- [Docker Day 4 - Multi-stage build and image optimisation](docker-notes/day-04-multi-stage-build.md)

### Kubernetes

- [Kubernetes Day 1 - Local cluster setup](k8s-notes/day-01-local-cluster.md)