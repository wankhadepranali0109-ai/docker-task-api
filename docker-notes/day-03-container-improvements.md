# Docker Day 3 - Container Improvements

## Goal

Improve the Dockerised Flask Task API container by making it cleaner, configurable, observable, restartable, and self-checking.

In Day 2, the Flask API was successfully packaged into a Docker image and run as a container.  
In Day 3, the goal was to improve how that container is built and operated.

---

## What I changed

- Added a `.dockerignore` file.
- Rebuilt the Docker image after adding `.dockerignore`.
- Ran the container in detached/background mode.
- Passed `PORT=5000` into the container as an environment variable.
- Recreated the container with a restart policy.
- Added a Docker `HEALTHCHECK` instruction to the Dockerfile.
- Verified that Docker reports the container health as `healthy`.
- Practised inspecting container status, logs, restart policy, and health status.

---

## Files changed

```text
docker-task-api/
├── .dockerignore
├── Dockerfile
└── notes/
    └── docker-day-03-container-improvements.md
```

---

## `.dockerignore`

### File created

```text
.dockerignore
```

### Content used

```gitignore
.venv
__pycache__
*.pyc
.git
.gitignore
README.md
notes
.env
```

---

## Why `.dockerignore` is needed

When Docker builds an image, it sends the project folder to the Docker daemon as the **build context**.

If unnecessary files are not ignored, Docker may send files such as:

- `.venv`
- Git history
- notes
- cache files
- local environment files

This can make builds:

- slower,
- larger,
- less secure,
- less clean.

`.dockerignore` works like `.gitignore`, but for Docker builds.

It tells Docker:

> Do not include these files/folders in the build context.

---

## Rebuilding the image

After adding `.dockerignore`, the image was rebuilt:

```powershell
docker build -t docker-task-api:latest .
```

### Meaning

| Part | Meaning |
|---|---|
| `docker build` | Build a Docker image. |
| `-t docker-task-api:latest` | Tag the image as `docker-task-api:latest`. |
| `.` | Use the current project folder as the build context. |

---

## Running the container in detached mode

The container was recreated using:

```powershell
docker rm -f task-api
docker run -d --name task-api --restart unless-stopped -e PORT=5000 -p 5000:5000 docker-task-api:latest
```

---

## Command breakdown

| Part | Meaning |
|---|---|
| `docker rm -f task-api` | Remove the existing `task-api` container if it exists. |
| `docker run` | Create and start a new container. |
| `-d` | Run in detached/background mode. |
| `--name task-api` | Name the container `task-api`. |
| `--restart unless-stopped` | Restart the container automatically unless it was manually stopped. |
| `-e PORT=5000` | Pass environment variable `PORT=5000` into the container. |
| `-p 5000:5000` | Map host port `5000` to container port `5000`. |
| `docker-task-api:latest` | Image used to create the container. |

---

## Why detached mode is useful

Without detached mode, the container runs in the foreground and the terminal is blocked.

Example:

```powershell
docker run --name task-api -p 5000:5000 docker-task-api:latest
```

With detached mode:

```powershell
docker run -d --name task-api -p 5000:5000 docker-task-api:latest
```

The container keeps running in the background, and the terminal remains usable.

---

## Environment variable usage

The app reads the port from an environment variable:

```python
port = int(os.getenv("PORT", "5000"))
```

This means:

- if `PORT` is provided, use it,
- otherwise use default port `5000`.

The container was run with:

```powershell
-e PORT=5000
```

This sets the environment variable inside the container.

---

## Why environment variables are useful

Environment variables make applications configurable without changing code.

For example:

```powershell
-e PORT=5000
```

Later the same idea can be used for:

```text
DATABASE_HOST
DATABASE_USER
DATABASE_PASSWORD
APP_ENV
```

This is important for Docker Compose and Kubernetes because configuration should come from the environment, not be hardcoded.

---

## Port mapping

The app listens on port `5000` inside the container.

This command:

```powershell
-p 5000:5000
```

means:

```text
host/laptop port 5000 → container port 5000
```

So this works from the laptop:

```text
http://localhost:5000
```

---

## Restart policy

The container was created with:

```powershell
--restart unless-stopped
```

### Meaning

Docker should restart the container automatically if it stops unexpectedly, unless I manually stopped it.

---

## Why restart policy is useful

A container normally keeps running as long as the main process inside it keeps running.

But problems can happen:

- the app crashes,
- Docker Desktop restarts,
- the laptop restarts,
- the container exits unexpectedly.

Without restart policy:

```text
container crashes → stays stopped
```

With restart policy:

```text
container crashes → Docker starts it again
```

---

## Restart policy behaviour

| Situation | No restart policy | `unless-stopped` |
|---|---|---|
| App keeps running normally | Container stays running | Container stays running |
| App crashes | Container stays stopped | Docker restarts it |
| Docker Desktop restarts | May stay stopped | Starts again |
| Laptop restarts and Docker opens | May stay stopped | Starts again |
| Manually stopped with `docker stop` | Stops | Stops and respects manual stop |

---

## Verifying restart policy

Command used:

```powershell
docker inspect task-api --format "{{.HostConfig.RestartPolicy.Name}}"
```

Expected result:

```text
unless-stopped
```

---

## Docker health check

A Docker health check was added to the `Dockerfile`.

### Dockerfile section

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"
```

This was added before:

```dockerfile
CMD ["python", "app.py"]
```

---

## What the health check does

The health check asks Docker to regularly check whether the Flask app is responding.

It calls:

```text
http://localhost:5000/health
```

from inside the container.

If the endpoint responds successfully, Docker marks the container as:

```text
healthy
```

If the endpoint repeatedly fails, Docker marks it as:

```text
unhealthy
```

---

## Health check options

| Option | Meaning |
|---|---|
| `--interval=30s` | Run the health check every 30 seconds. |
| `--timeout=5s` | Wait up to 5 seconds for a response. |
| `--retries=3` | Mark unhealthy after 3 failed attempts. |
| `CMD python -c ...` | Run a Python one-liner to call the `/health` endpoint. |

---

## Why health checks are useful

A container can be running, but the application inside may not actually be working.

For example:

- Flask process is running but `/health` is not responding.
- The app is stuck.
- The server started but is not handling requests.
- A dependency/config issue broke the app.

Without health check, Docker mainly knows:

```text
container process is running
```

With health check, Docker knows:

```text
application inside the container is responding correctly
```

---

## Running vs healthy

| Status | Meaning |
|---|---|
| `Up` | The container process is running. |
| `healthy` | The app inside passed the health check. |
| `unhealthy` | The container is running, but the app health check failed. |

Important learning:

> A running container is not always a healthy container.

---

## Relation to Kubernetes

Docker health checks prepare for Kubernetes probes.

Kubernetes has similar concepts:

| Docker | Kubernetes |
|---|---|
| `HEALTHCHECK` | liveness/readiness/startup probes |
| `healthy` | pod ready/healthy |
| `unhealthy` | pod may be restarted or removed from traffic |

Later in Kubernetes:

- **liveness probe** will check if the app should be restarted,
- **readiness probe** will check if the app should receive traffic,
- **startup probe** can help slow-starting apps.

---

## Verifying health status

After rebuilding and recreating the container:

```powershell
docker ps
```

Initially showed:

```text
Up 9 seconds (health: starting)
```

After waiting:

```text
Up 2 minutes (healthy)
```

Health status was also checked using:

```powershell
docker inspect task-api --format "{{json .State.Health.Status}}"
```

Result:

```text
"healthy"
```

---

## Useful commands practised

### Rebuild image

```powershell
docker build -t docker-task-api:latest .
```

### Remove old container

```powershell
docker rm -f task-api
```

### Run improved container

```powershell
docker run -d --name task-api --restart unless-stopped -e PORT=5000 -p 5000:5000 docker-task-api:latest
```

### Check running containers

```powershell
docker ps
```

### Check logs

```powershell
docker logs task-api
```

### Follow logs

```powershell
docker logs -f task-api
```

### Inspect restart policy

```powershell
docker inspect task-api --format "{{.HostConfig.RestartPolicy.Name}}"
```

### Inspect health status

```powershell
docker inspect task-api --format "{{json .State.Health.Status}}"
```

### Enter container

```powershell
docker exec -it task-api sh
```

### Check environment variable inside container

```sh
echo $PORT
```

### Exit container

```sh
exit
```

---

## What passed

- `.dockerignore` was added successfully.
- Docker image rebuilt successfully.
- Container was recreated successfully.
- Container ran in detached mode.
- Environment variable `PORT=5000` was passed into the container.
- API still worked through `http://localhost:5000`.
- Restart policy was added successfully.
- Docker health check was added to the Dockerfile.
- Container initially showed `health: starting`.
- After waiting, container showed `healthy`.
- `docker inspect` confirmed the health status as `"healthy"`.

---

## Evidence

### Running container

```text
CONTAINER ID   IMAGE                    STATUS
608d41cd1561   docker-task-api:latest   Up 2 minutes (healthy)
```

### Health status

```powershell
docker inspect task-api --format "{{json .State.Health.Status}}"
```

Output:

```text
"healthy"
```

### Port mapping

```text
0.0.0.0:5000->5000/tcp
```

---

## Issues encountered

### Issue - Wrong restart flag used initially

Incorrect command:

```powershell
--restart-unless-stopped
```

This failed because Docker does not have a flag with that exact name.

Correct command:

```powershell
--restart unless-stopped
```

Learning:

`--restart` is the flag, and `unless-stopped` is the value.

---

## Key learnings

- `.dockerignore` reduces unnecessary build context.
- Docker images should not include local virtual environments, notes, Git history, or secrets.
- Environment variables make containers configurable.
- Port mapping connects host ports to container ports.
- Detached mode allows the container to run in the background.
- Restart policies help containers recover from crashes or Docker restarts.
- `docker inspect` can show low-level container configuration.
- `docker logs` helps observe application output.
- `HEALTHCHECK` tells Docker how to test if the application is actually responding.
- A container can be running but unhealthy.
- Health checks are an important bridge concept before Kubernetes probes.

---

## Final summary

Today I improved the Docker container from a basic running container into a more realistic service container.

The container now:
- uses a cleaner build context,
- runs in the background,
- accepts configuration through environment variables,
- has a restart policy,
- exposes the API through port mapping,
- reports application health through Docker health checks.

---

## Next step

Improve the Docker image by converting the Dockerfile into a multi-stage build.

The goal is to separate build-time dependencies from runtime requirements, reduce image size, and understand how Docker layers affect final images.

In the next session:

create a multi-stage Dockerfile,
rebuild the image,
compare image size before and after,
verify the Flask API still runs correctly,
document what changed and why.
