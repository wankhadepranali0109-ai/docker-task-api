# Day 2 - Docker Image and Container

## Goal

Package the Flask Task API into a Docker image and run it as a Docker container.

The Flask API was already working locally from Day 1. Today’s goal was to run the same application through Docker so that the app is packaged with its runtime and dependencies.

---

## What I built

- Created a `Dockerfile`.
- Used the official `python:3.12-slim` base image.
- Set `/app` as the working directory inside the container.
- Copied `requirements.txt` into the image.
- Installed Python dependencies inside the image.
- Copied the Flask application code into the image.
- Exposed port `5000`.
- Set the container startup command to run the Flask app.
- Built the Docker image with the tag `docker-task-api:latest`.
- Ran the image as a container named `task-api`.
- Published local port `5000` to container port `5000`.
- Tested the containerised Flask API from the host machine.

---

## Dockerfile used

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

---

## Dockerfile explanation

### `FROM python:3.12-slim`

This sets the base image.

Instead of manually installing Python inside the container, I started from an official Python image. The `slim` version is smaller than the full Python image, so it is better for simple applications.

---

### `WORKDIR /app`

This sets the working directory inside the image/container.

After this instruction, Docker runs following commands from `/app`.

So this:

```dockerfile
COPY requirements.txt .
```

means:

```text
copy requirements.txt into /app
```

---

### `COPY requirements.txt .`

This copies only the dependency file first.

This is useful because Docker builds images in layers. If `requirements.txt` does not change, Docker can reuse the cached dependency installation layer instead of reinstalling packages every time.

---

### `RUN pip install --no-cache-dir -r requirements.txt`

This installs the Python dependencies listed in `requirements.txt`.

Breakdown:

| Part | Meaning |
|---|---|
| `RUN` | Execute this command while building the image. |
| `pip install` | Install Python packages. |
| `-r requirements.txt` | Read package names from `requirements.txt`. |
| `--no-cache-dir` | Do not store pip’s downloaded package cache inside the image. |

`--no-cache-dir` helps keep the Docker image smaller. It does not disable Docker’s build cache; it only disables pip’s internal package download cache.

---

### `COPY . .`

This copies the rest of the project files into the image.

In this project, it copies files such as:

```text
app.py
README.md
.gitignore
```

Later, `.dockerignore` will be added so unnecessary files like `.venv/` are not sent to Docker during build.

---

### `EXPOSE 5000`

This documents that the application listens on port `5000` inside the container.

Important learning:

```dockerfile
EXPOSE 5000
```

does not automatically make the app available on the laptop.

The port is actually published using:

```powershell
docker run -p 5000:5000 ...
```

---

### `CMD ["python", "app.py"]`

This is the default command that runs when the container starts.

It starts the Flask application inside the container.

---

## Commands used

### Build the Docker image

```powershell
docker build -t docker-task-api:latest .
```

Meaning:

| Part | Meaning |
|---|---|
| `docker build` | Build a Docker image. |
| `-t docker-task-api:latest` | Tag the image with a name and version. |
| `.` | Use the current directory as the build context. |

The image created was:

```text
docker-task-api:latest
```

---

### List Docker images

```powershell
docker images
```

This confirms that the image was created successfully.

Expected image:

```text
docker-task-api   latest
```

---

### Run the image as a container

```powershell
docker run --name task-api -p 5000:5000 docker-task-api:latest
```

Meaning:

| Part | Meaning |
|---|---|
| `docker run` | Create and start a new container from an image. |
| `--name task-api` | Give the container a readable name. |
| `-p 5000:5000` | Map host port `5000` to container port `5000`. |
| `docker-task-api:latest` | Image used to create the container. |

Port mapping:

```text
localhost:5000 on laptop → port 5000 inside container
```

---

### Start an existing stopped container

```powershell
docker start task-api
```

This starts an already-created container.

Important difference:

```text
docker run   = create + start a new container
docker start = start an existing stopped container
```

---

### Show running containers

```powershell
docker ps
```

This shows only currently running containers.

When the container was running, it showed:

```text
docker-task-api:latest   Up   0.0.0.0:5000->5000/tcp   task-api
```

---

### Show all containers

```powershell
docker ps -a
```

This shows both running and stopped containers.

This is useful when `docker ps` shows nothing, but a container still exists in stopped state.

---

### View container logs

```powershell
docker logs task-api
```

This shows the output produced by the application inside the container.

For this Flask app, logs showed the Flask server starting and listening on port `5000`.

---

### Enter the running container

```powershell
docker exec -it task-api sh
```

This opened a shell inside the running container.

Meaning:

| Part | Meaning |
|---|---|
| `docker exec` | Run a command inside an existing running container. |
| `-i` | Keep input open. |
| `-t` | Allocate an interactive terminal. |
| `task-api` | Container name. |
| `sh` | Shell program to run inside the container. |

Inside the container, useful inspection commands are:

```sh
ls
python --version
cat requirements.txt
```

This helps confirm:
- the application files exist inside the container,
- Python is available inside the container,
- dependencies are installed,
- the container has its own isolated filesystem.

Exit the container shell:

```sh
exit
```

---

### Stop the container

```powershell
docker stop task-api
```

This stops the running container gracefully.

---

## API tests performed

### Health check

```powershell
Invoke-RestMethod http://localhost:5000/health
```

Expected result:

```powershell
status
------
ok
```

---

### Create a task

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://localhost:5000/tasks" `
  -ContentType "application/json" `
  -Body '{"title":"Run Flask app in Docker"}'
```

Expected result:

```powershell
done  id title
----  -- -----
False 1  Run Flask app in Docker
```

---

### List tasks

```powershell
Invoke-RestMethod http://localhost:5000/tasks
```

Expected result:

```powershell
done  id title
----  -- -----
False 1  Run Flask app in Docker
```

---

## What passed

- Docker Desktop started successfully.
- Docker image `docker-task-api:latest` was built successfully.
- The image appeared in the Docker image list.
- The container `task-api` was created successfully.
- Flask started inside the container.
- Port mapping worked from local port `5000` to container port `5000`.
- `GET /health` worked through Docker.
- `POST /tasks` created a task through the containerised API.
- `GET /tasks` returned the created task.
- `docker start task-api` restarted the stopped container successfully.
- `docker ps` showed the container running after restart.

---

## Issues encountered and fixes

### Issue 1 - Docker daemon was not running

While building the image, this error appeared:

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
```

Reason:

Docker CLI was available, but Docker Desktop / Docker Engine was not running.

Fix:

Started Docker Desktop and waited for the engine to finish loading. After that, the build command worked.

---

### Issue 2 - Tried to stop an image instead of a container

I tried to stop values from the image list:

```powershell
docker stop df7b20dbe0a9
docker stop flask-todo-app:1.1
```

This failed because those referred to images, not running containers.

Learning:

Docker images and containers are different.

| Concept | Meaning | Example command |
|---|---|---|
| Image | Packaged app/template | `docker images` |
| Container | Running/stopped instance of an image | `docker ps -a` |

Correct command to stop a running container:

```powershell
docker stop <container-id-or-name>
```

Correct command to remove an image:

```powershell
docker rmi <image-name>
```

---



An image can still be “in use” if stopped containers were created from it. Stopped containers still reference the image.

---

### Issue 3 - `docker ps` showed no running containers after initial test

After testing the API, this command showed no running containers:

```powershell
docker ps
```

Reason:

The container had stopped after the foreground `docker run` session ended.

Fix:

Started the same container again:

```powershell
docker start task-api
```

Then confirmed:

```powershell
docker ps
```

---

## Important Docker concepts revised

### Image vs container

An image is a packaged application.

A container is a running or stopped instance of an image.

```text
Dockerfile → docker build → Image → docker run → Container
```

---

### Build context

The final `.` in this command is the build context:

```powershell
docker build -t docker-task-api:latest .
```

It tells Docker to send the current project folder to the Docker daemon for building the image.

Later, `.dockerignore` will be added to avoid sending unnecessary files like `.venv/`.

---

### Port mapping

The Flask app listens on port `5000` inside the container.

This option:

```powershell
-p 5000:5000
```

maps:

```text
host/laptop port 5000 → container port 5000
```

Without `-p`, the app may run inside the container but would not be easily accessible from the browser or PowerShell on the laptop.

---

### Foreground vs background container

Running without `-d`:

```powershell
docker run --name task-api -p 5000:5000 docker-task-api:latest
```

runs the container in the foreground. Logs appear directly in the terminal.

Running with `-d`:

```powershell
docker run -d --name task-api -p 5000:5000 docker-task-api:latest
```

runs the container in detached/background mode.

---

### `docker run` vs `docker start`

```text
docker run   → creates a new container from an image and starts it
docker start → starts an existing stopped container
```

If a container named `task-api` already exists, `docker run --name task-api ...` will fail unless the old container is removed.

Remove existing container:

```powershell
docker rm -f task-api
```

---

### Temporary in-memory data

The Flask app currently stores tasks in a Python list.

That means:
- tasks exist while the app process is running,
- data can disappear when the container stops or restarts,
- data is not yet persistent.

This will be improved later using PostgreSQL and Docker volumes.

---

## Evidence

- Image built: `docker-task-api:latest`
- Container name: `task-api`
- Port mapping: `0.0.0.0:5000->5000/tcp`
- Health endpoint passed: `http://localhost:5000/health`
- Task created: `Run Flask app in Docker`
- Running container confirmed with `docker ps`

---

## Final learning summary

Today I learned how to package a working Flask application into a Docker image and run it as a container.

I also revised:
- Dockerfile basics,
- image creation,
- container creation,
- port mapping,
- logs,
- container inspection,
- stopped vs running containers,
- image vs container difference,
- why persistent storage is needed later.

---

## Next step

Improve the Docker setup by adding:
- `.dockerignore`
- environment variables
- container logs
- restart policy
- Docker health check