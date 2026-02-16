# Implementation Plan - Burnar

## User Review Required

> [!IMPORTANT]
> **Web Framework Choice**:
> **FastAPI** has been selected over Starlette/Flask.
> It provides modern async capabilities, automatic OpenAPI docs (useful for maintenance), and high performance.

> [!IMPORTANT]
> **Data Persistence Strategy**:
> **File-Based Storage** with a background cleanup task (or check-on-access).
> Metadata stored in simple JSON files alongside content.
> **Concurrency**: Use **Portalocker** for cross-platform file locking to prevent race conditions.
> *Reasoning*: Zero external dependencies simplifies the "copy to docroot" deployment.

> [!NOTE]
> **Production Deployment (Docroot)**:
> App will be designed to handle dynamic `root_path` (mounting at `/burnar/`, `/`, etc.) transparently.
> **Deployment Script**: `bin/deploy.ps1` (PowerShell Core) for cross-platform compatibility.

## Proposed Changes

### Project Structure
```text
burnar/
├── app/
│   ├── templates/      # Jinja2 templates (minimal UI)
│   ├── static/         # CSS/JS
│   ├── __init__.py
│   ├── main.py         # App entry point (FastAPI)
│   ├── storage.py      # Storage logic (File-based + Portalocker)
│   └── crypto.py       # Encryption logic
├── bin/                # Scripts
│   ├── deploy.ps1      # Production deployment
│   ├── dev-start.ps1   # Local dev start
│   ├── dev-stop.ps1    # Local dev stop
│   └── dev-restart.ps1 # Local dev restart
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml      # uv dependencies
└── README.md
```

### 1. Core Application [NEW]
- **Framework**: FastAPI
- **Dependencies**: `jinja2` (templating), `cryptography` (encryption), `uvicorn` (server), `python-multipart` (file uploads), `portalocker` (file locking).
- **Features**:
    - `GET /`: Returns web app main page html.
    - `POST /create`: Encrypts content, generates a UUID and retrieval link.
    - `GET /secret/{uuid}`: Shows "Click to reveal" (prevent bots).
    - `POST /secret/{uuid}`: Decrypts and shows content. Deletes from storage immediately (Burn).

### 2. Docker Integration [NEW]
- **Dockerfile**: Optimized python image.
- **docker-compose.yml**:
    - Service `burnar`: Mounts local dir for dev. Exposes port **8248**.
    - Command: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8248`

### 3. Scripts [NEW]
- `bin/deploy.ps1`: Production deployment steps.
- `bin/dev-start.ps1`: Starts docker compose (or uvicorn locally).
- `bin/dev-stop.ps1`: Stops docker compose.
- `bin/dev-restart.ps1`: Restarts the dev environment.

## Verification Plan

### Automated Tests
- `uv run pytest` for unit tests (storage, encryption, burn logic).
- Integration tests using FastAPI `TestClient`.

### Manual Verification
- **Local**: Run `bin/dev-start.ps1`, access `http://localhost:8248`.
- **Subpath Simulation**: Configurable via env var in `dev-start` script.
