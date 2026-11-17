# Docker Day 5 - Custom Bridge Networking with PostgreSQL

## Goal

Learn how separate Docker containers communicate privately using a custom Docker bridge network.

The Flask Task API was already running in a Docker container. Today, a PostgreSQL database was added as a separate container, and both containers were connected through the same private Docker network.

---

## Starting point

Before Day 5, the project looked like this:

```text
Flask Task API
→ Docker image
→ task-api container
→ accessible at localhost:5000
```

The Flask app currently stores tasks in a Python list, so task data is temporary. PostgreSQL was added to prepare for moving task storage into a real database in a later task.

---

## What I created

Created a custom Docker network:

```text
task-api-network
```

The setup now looks like this:

```text
task-api container
      ↓
task-api-network
      ↓
task-db PostgreSQL container
```

---

## Why a custom Docker network is needed

Docker containers are isolated from each other. The Flask API and PostgreSQL database are separate containers, so they need a private network to communicate.

A custom bridge network provides:

- private container-to-container communication;
- Docker DNS resolution using container names;
- better isolation because the database does not need to be exposed to the laptop;
- a setup similar to what Docker Compose will automate later.

The Flask API will eventually connect to PostgreSQL using:

```text
task-db:5432
```

instead of using a changing IP address.

---

## Docker network types

| Network type | Purpose |
|---|---|
| `bridge` | Private network for containers running on one Docker host. |
| `host` | Container shares the host machine’s network directly. |
| `none` | Container has no network access. |
| `overlay` | Connects containers across multiple Docker hosts. |
| `macvlan` | Gives containers IP addresses similar to physical devices on a local network. |

For this project, custom `bridge` networking is the correct choice because the Flask API and PostgreSQL are both running on the same laptop.

---

## Create custom Docker network

Command used:

```powershell
docker network create task-api-network
```

Verify all Docker networks:

```powershell
docker network ls
```

Relevant output:

```text
NETWORK ID     NAME               DRIVER    SCOPE
c2bc981b7fa3   task-api-network   bridge    local
```

### Meaning

| Field | Meaning |
|---|---|
| `task-api-network` | Name of the custom network. |
| `bridge` | Driver used to create the private local network. |
| `local` | The network exists only on this laptop’s Docker host. |

---

## Connect Flask API container to the network

The existing Flask API container was connected to the new custom network:

```powershell
docker network connect task-api-network task-api
```

This attached the already-running `task-api` container to `task-api-network`.

---

## Start PostgreSQL container

PostgreSQL was started on the same custom Docker network:

```powershell
docker run -d --name task-db `
  --network task-api-network `
  -e POSTGRES_DB=tasks `
  -e POSTGRES_USER=taskuser `
  -e POSTGRES_PASSWORD=taskpassword `
  postgres:16
```

### Command explanation

| Part | Meaning |
|---|---|
| `docker run` | Create and start a new container from an image. |
| `-d` | Run the container in detached/background mode. |
| `--name task-db` | Give the database container the name `task-db`. |
| `--network task-api-network` | Attach PostgreSQL to the custom bridge network. |
| `-e` | Set an environment variable inside the container. |
| `POSTGRES_DB=tasks` | Create an initial PostgreSQL database called `tasks`. |
| `POSTGRES_USER=taskuser` | Create a PostgreSQL user called `taskuser`. |
| `POSTGRES_PASSWORD=taskpassword` | Set the password for `taskuser`. This password is only for local learning and must not be committed as a real secret. |
| `postgres:16` | Use the official PostgreSQL Docker image, version 16. |

---

## What `-e` means

`-e` means environment variable.

It passes configuration into the container when it is created.

The official PostgreSQL image reads these environment variables when it starts for the first time and uses them to initialise the database.

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

---

## PostgreSQL connection details

The Flask app will later connect to PostgreSQL with:

```text
Host: task-db
Port: 5432
Database: tasks
Username: taskuser
Password: taskpassword
```

The important part is:

```text
Host: task-db
```

Because both containers are on the same custom bridge network, Docker DNS can resolve the container name `task-db`.

---

## Why PostgreSQL port 5432 was not published

The PostgreSQL container was started without:

```powershell
-p 5432:5432
```

This was intentional.

The database should not be directly exposed to the browser or laptop for this task. It should be accessed privately by the Flask API over the Docker network.

```text
task-api → task-api-network → task-db:5432
```

The Flask API itself remains publicly accessible through:

```text
localhost:5000
```

---

## Verify that both containers joined the network

Command used:

```powershell
docker network inspect task-api-network
```

Relevant output:

```text
Containers:
task-api → 172.18.0.2
task-db  → 172.18.0.3
```

This confirms that both containers are attached to the same private network.

```text
task-api container → 172.18.0.2
task-db container  → 172.18.0.3
```

The exact internal IP addresses may differ.

Important: this does not yet prove that the containers communicated. It proves that both containers are connected to the same network and are able to communicate.

---

## Verify PostgreSQL is ready

Command used:

```powershell
docker logs task-db
```

Important output:

```text
database system is ready to accept connections
```

This confirmed that PostgreSQL completed its initial setup and is listening on port `5432`.

---

## PostgreSQL log explanation

The PostgreSQL logs showed the following process:

1. PostgreSQL created its internal data directory:

   ```text
   /var/lib/postgresql/data
   ```

2. It created configuration files and internal database folders.

3. It initialised the database cluster.

4. It created the initial database:

   ```text
   CREATE DATABASE
   ```

5. It temporarily stopped the setup server after initialisation.

6. It started the normal long-running PostgreSQL server.

7. PostgreSQL began listening on port `5432`.

8. PostgreSQL confirmed:

   ```text
   database system is ready to accept connections
   ```

The log messages about checkpoints are normal PostgreSQL maintenance. They mean the database is saving changes safely to disk.

---

## Verify Docker DNS between containers

To prove that the Flask API container can find PostgreSQL by its container name, open a shell inside the Flask API container:

```powershell
docker exec -it task-api sh
```

Then run:

```sh
python -c "import socket; print(socket.gethostbyname('task-db'))"
```

Expected output:

```text
172.18.x.x
```

The IP may be different, but it should match the internal IP of `task-db` shown by `docker network inspect`.

Exit the container:

```sh
exit
```

### What this proves

```text
task-api container
→ asks Docker DNS: "Where is task-db?"
→ Docker resolves task-db to PostgreSQL container IP
→ task-api can connect privately to task-db:5432
```

This is better than using a hard-coded IP address because container IP addresses may change when containers are recreated.

---

## What passed

- Created custom Docker network `task-api-network`.
- Confirmed that the network uses the `bridge` driver.
- Connected the existing `task-api` container to the new network.
- Created the PostgreSQL container named `task-db`.
- Connected `task-db` to the same custom network.
- PostgreSQL initialised the `tasks` database successfully.
- PostgreSQL logs showed that it was ready to accept connections.
- `docker network inspect` showed both containers in `task-api-network`.
- Docker DNS resolved `task-db` from inside the `task-api` container.

---

## Key learning

A custom Docker bridge network allows containers to communicate privately using container names instead of fixed IP addresses.

```text
task-api → task-db:5432
```

This is safer, clearer, and more reliable than exposing the database to the host machine or hard-coding container IP addresses.

Docker Compose will automate much of this later by creating a shared network for services automatically.

---

## Next step

Update the Flask Task API so `/tasks` reads and writes task data in PostgreSQL instead of using the in-memory Python list.