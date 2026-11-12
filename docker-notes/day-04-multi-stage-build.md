# Docker Day 4 - Multi-Stage Build and Image Optimisation

## Goal

Convert the Flask Task API Dockerfile from a single-stage build into a multi-stage build, then verify that the application still runs correctly.

## What I changed

- Replaced the single-stage Dockerfile with a multi-stage Dockerfile.
- Created a `builder` stage to install Python dependencies.
- Created a separate `runtime` stage for the final application image.
- Copied only installed dependencies from the builder stage into the runtime stage.
- Copied only `app.py` into the runtime stage.
- Rebuilt the image and recreated the container.
- Verified that the API and Docker health check still work.

## Multi-stage Dockerfile

```dockerfile
# Stage 1: install Python dependencies
FROM python:3.12-slim AS builder

WORKDIR /install

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install/deps -r requirements.txt


# Stage 2: final runtime image
FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /install/deps /usr/local

COPY app.py .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["python", "app.py"]
```

## What multi-stage build means

A multi-stage Dockerfile uses more than one `FROM` instruction.

```text
Stage 1: prepare/install dependencies
Stage 2: run the application
```

The first stage is called `builder`. It installs dependencies into a temporary location.

The second stage is the final runtime image. It starts from a fresh Python image and copies only the installed dependencies and application file needed to run the API.

```dockerfile
COPY --from=builder /install/deps /usr/local
```

This command copies dependencies from the `builder` stage into the final `runtime` stage.

## Why use multi-stage builds

Multi-stage builds help create cleaner production-style images.

Benefits:

- Separates build-time work from runtime requirements.
- Avoids keeping unnecessary build files in the final image.
- Makes the final Dockerfile more explicit.
- Reduces image size significantly in applications that need compilers, build tools, or development dependencies.
- Reduces the attack surface by including fewer unnecessary files.

For this small Flask application, the size improvement may be limited because Flask has few dependencies. The main learning was the builder/runtime pattern.

## Commands used

Build the updated image:

```powershell
docker build -t docker-task-api:latest .
```

Check image size:

```powershell
docker images docker-task-api
```

View image layers:

```powershell
docker history docker-task-api:latest
```

Remove the existing container:

```powershell
docker rm -f task-api
```

Run the new image:

```powershell
docker run -d --name task-api --restart unless-stopped -e PORT=5000 -p 5000:5000 docker-task-api:latest
```

Test the API:

```powershell
Invoke-RestMethod http://localhost:5000/health
```

Check container and health status:

```powershell
docker ps
docker inspect task-api --format "{{json .State.Health.Status}}"
```

## What passed

- The multi-stage Docker image built successfully.
- The `task-api` container started successfully from the rebuilt image.
- The Flask API health endpoint responded successfully.
- Docker health check completed successfully.
- Container status showed `healthy`.

## Key learning

A normal Dockerfile can do everything in one image stage. A multi-stage build separates preparation from runtime:

```text
requirements.txt
      ↓
Builder stage installs dependencies
      ↓
Runtime stage receives only needed dependencies + app code
      ↓
Final image runs Flask API
```

The Docker build command stays the same:

```powershell
docker build -t docker-task-api:latest .
```

The main difference is the Dockerfile design, not the command.

## Next step

Continue Kubernetes Day 2 by deploying the updated multi-stage Docker image to Minikube.

Steps:
1.kubectl get nodes
2.minikube image load docker-task-api:latest
3.minikube image ls | Select-String docker-task-api
4.kubectl apply -f k8s/deployment.yaml
5.kubectl get deployments
6.kubectl get pods