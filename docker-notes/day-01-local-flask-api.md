# Docker Task API

A small Flask Task API built as a hands-on project for revising Docker.  
The project will gradually evolve into a multi-container application with PostgreSQL, Docker networking, persistent volumes, Docker Compose, image registries, and CI/CD.

## Day 1 - Run the Flask API locally

### What I built
- Created a basic Flask Task API.
- Added an in-memory list to store tasks while the app is running.
- Added these endpoints:
  - `GET /health` - verifies that the API is running.
  - `GET /tasks` - returns all tasks.
  - `POST /tasks` - creates a new task.

### Files created
```text
docker-task-api/
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Run locally - Windows PowerShell
```powershell
.venv\Scripts\Activate.ps1
python app.py
```

The API runs at:

```text
http://localhost:5000
```

### Tests performed

Check API health:

```powershell
Invoke-RestMethod http://localhost:5000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

Create a task:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://localhost:5000/tasks" `
  -ContentType "application/json" `
  -Body '{"title":"Revise Docker"}'
```

List tasks:

```powershell
Invoke-RestMethod http://localhost:5000/tasks
```

### What passed
- Flask application started successfully on port `5000`.
- `GET /health` returned `{"status":"ok"}`.
- A task named `Revise Docker` was created successfully.
- `GET /tasks` returned the saved task.

### Issue encountered and resolution
- **Issue:** PowerShell’s `curl` behaves differently from standard curl and showed a security warning.
- **Resolution:** Used `Invoke-RestMethod` for API testing.

- **Issue:** Escaped JSON caused the `POST /tasks` request to return `title is required`.
- **Resolution:** Sent the JSON body using PowerShell single quotes:
  ```powershell
  -Body '{"title":"Revise Docker"}'
  ```

### Key learning
The task data is currently stored only in memory. If I stop and restart the Flask app, the tasks disappear. Later in this project, PostgreSQL and a Docker volume will provide persistent storage.

### Next step
Create a Dockerfile and run this same Flask Task API inside a Docker container.