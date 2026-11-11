# Docker Task API

A small Flask Task API used to revise Docker concepts step by step.

The project starts as a simple local Flask API and gradually evolves into a containerised, multi-container application using Docker, networking, volumes, Docker Compose, registries, and CI/CD.

## Current status

- Day 1: Built and tested the Flask API locally.
- Day 2: Built a Docker image and ran the API as a container.

## Tech stack

- Python
- Flask
- Docker

## Project structure

```text
docker-task-api/
├── app.py
├── requirements.txt
├── Dockerfile
├── .gitignore
├── README.md
└── notes/
    ├── day-01-local-flask-api.md
    └── day-02-docker-image-container.md