# AI-Powered Document & Multimedia Q&A

Full-stack assignment implementation for uploading PDFs, audio, and video, then asking AI-assisted questions over the extracted content.

## Features

- Upload PDF, audio, and video files
- Extract PDF text with `pypdf`
- Transcribe audio/video with OpenAI Whisper when `OPENAI_API_KEY` is configured
- Store files, extracted text, transcript segments, summaries, and chat history in PostgreSQL
- FAISS-backed vector search for uploaded content, with a TF-IDF fallback and optional OpenAI answer generator
- Summaries for uploaded content
- Topic timestamp extraction for audio/video
- Play button in the UI that jumps media playback to the cited timestamp
- Streaming chat endpoint using Server-Sent Events
- JWT authentication
- Redis-backed rate limiting when Redis is available
- Dockerfile, Docker Compose, and GitHub Actions CI
- Backend tests with coverage gate

## Tech Stack

- Backend: FastAPI, SQLAlchemy, PostgreSQL, Redis, OpenAI API
- Frontend: React, Vite
- Testing: Pytest, pytest-cov, httpx
- Infrastructure: Docker, Docker Compose, GitHub Actions

## Quick Start

### 1. Configure environment

Copy the example environment:

```bash
cp .env.example .env
```

Set `OPENAI_API_KEY` if you want real LLM answers and Whisper transcription. Without it, the app uses deterministic local fallbacks for development and tests.

### 2. Run with Docker Compose

```bash
docker compose up --build
```

Services:

- Frontend: <http://localhost:5173>
- Backend API: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>

### 3. Local backend development

On Windows, start both the backend and frontend with:

```bat
start-local.cmd
```

This opens the FastAPI backend on <http://127.0.0.1:8001> and the Vite frontend in separate terminals.

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
python -m pip install -r requirements-dev.txt
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=95
python -m uvicorn app.main:app --reload --port 8001
```

On Windows, you can also start the backend with `backend\run-backend-8001.cmd`, which uses the backend virtual environment explicitly.

### 4. Local frontend development

```bash
cd frontend
npm install
npm run dev
```

## Deploy Frontend on Vercel and Backend on Railway

This repo includes deployment config for Vercel frontend hosting and Railway backend hosting.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the complete split-deployment guide.

### Vercel Frontend

If you deploy from the project root, Vercel will use:

```text
Install Command: cd frontend && npm install
Build Command: cd frontend && npm run build
Output Directory: frontend/dist
```

Set this Vercel environment variable to your Railway backend URL:

```text
VITE_API_BASE_URL=https://your-railway-backend.up.railway.app
```

### Railway Backend

Deploy the `backend` folder on Railway. Railway will use:

- `backend/Dockerfile`
- `backend/railway.json`

Recommended Railway environment variables:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
REDIS_URL=redis://USER:PASSWORD@HOST:PORT
JWT_SECRET=replace-with-a-strong-secret
OPENAI_API_KEY=your-openai-api-key
BACKEND_CORS_ORIGINS=https://your-vercel-app.vercel.app
UPLOAD_DIR=/app/uploads
```

Railway provides `PORT` automatically, and the backend Dockerfile reads it.

## API Overview

All protected endpoints require:

```http
Authorization: Bearer <token>
```

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`

Payload:

```json
{
  "email": "user@example.com",
  "password": "strong-password"
}
```

### Files

- `POST /api/files/upload` uploads a PDF/audio/video file
- `GET /api/files` lists uploaded files
- `GET /api/files/{file_id}/summary` returns summary
- `GET /api/files/{file_id}/media` streams original media file

### Chat

- `POST /api/chat/ask`
- `GET /api/chat/stream?file_id=<id>&question=<question>`

Chat payload:

```json
{
  "file_id": 1,
  "question": "What are the main topics?"
}
```

### Timestamps

- `GET /api/files/{file_id}/timestamps?topic=pricing`

Returns transcript segments matching the topic for audio/video files.

## GitHub Actions

CI runs on every push and pull request:

- Backend lint-free test run with `pytest`
- Coverage threshold: 95%
- Frontend build

## Notes for Reviewers

The implementation is production-shaped but assignment-sized. When OpenAI credentials are missing, the backend still extracts PDF text and can answer from retrieved excerpts. Audio/video transcription falls back to a synthetic segment unless a sibling `.txt` transcript or API key is available, keeping the app runnable in constrained environments.
