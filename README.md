# HNG Stage 2 DevOps — Job Processing System

A containerized microservices application with a full CI/CD pipeline.

## Services
| Service  | Description                          | Port |
|----------|--------------------------------------|------|
| Frontend | Node.js UI for submitting/tracking jobs | 3000 |
| API      | FastAPI backend that creates jobs    | 8000 (internal) |
| Worker   | Python worker that processes jobs    | — |
| Redis    | Queue and job storage                | internal only |

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (v24+)
- [Docker Compose](https://docs.docker.com/compose/) (v2+)
- Git

## Quick Start (from scratch)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR-USERNAME/hng14-stage2-devops.git
cd hng14-stage2-devops

# 2. Copy environment template
cp .env.example .env
# (No changes needed for local development)

# 3. Build and start all services
docker compose up --build

# 4. Open your browser
open http://localhost:3000
```

## What a Successful Startup Looks Like
[+] Running 4/4
✔ Container redis     Healthy
✔ Container api       Healthy
✔ Container worker    Started
✔ Container frontend  Healthy

You'll see the frontend at `http://localhost:3000`. Submit a job, and
within ~3 seconds it should show as "completed".

## Running Tests Locally

```bash
cd api
pip install -r requirements.txt
pytest tests/ -v --cov=.
```

## Stopping

```bash
docker compose down        # Stop containers
docker compose down -v     # Stop and delete all data
```

## CI/CD Pipeline

Every push triggers: **lint → test → build → security scan → integration test**  
Pushes to `main` also trigger: **deploy**

See `.github/workflows/ci-cd.yml` for full pipeline definition.

STEP 8 — Push Everything to GitHub
bash# From your repo root:

# Stage all new files
git add .

# Verify .env is NOT in the list (it should show nothing for .env)
git status

# Commit
git commit -m "feat: containerize app, fix bugs, add CI/CD pipeline"

# Push to your fork
git push origin main

🗺️ Quick Summary — What Each File Does
FileWhat it doesapi/DockerfileBuilds the API into a container (multi-stage, non-root)worker/DockerfileBuilds the worker into a containerfrontend/DockerfileBuilds the frontend into a containerdocker-compose.ymlStarts ALL services together with correct networking.github/workflows/ci-cd.ymlThe robot pipeline: lint→test→build→scan→deployapi/tests/test_api.py6 automated tests for the API (Redis mocked).env.exampleTemplate for secrets (safe to commit).gitignoreEnsures .env is never accidentally committedFIXES.mdDocuments all 10 bugs found and fixedREADME.mdExplains how to run the project