# Deployment Guide

This project is set up for a split deployment:

- Frontend: Vercel
- Backend API: Railway

## 1. Deploy Backend on Railway

Create a Railway service from the `backend` folder.

Railway files:

- `backend/Dockerfile`
- `backend/railway.json`

Recommended Railway variables:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
REDIS_URL=redis://USER:PASSWORD@HOST:PORT
OPENAI_API_KEY=your-openai-api-key
JWT_SECRET=replace-with-a-strong-secret
BACKEND_CORS_ORIGINS=https://your-vercel-app.vercel.app
UPLOAD_DIR=/app/uploads
```

Railway automatically provides `PORT`. The Dockerfile uses that port in production.

After deploy, verify:

```text
https://your-railway-backend.up.railway.app/health
```

Expected response:

```json
{"status":"ok"}
```

## 2. Deploy Frontend on Vercel

Use either option.

Option A, root project:

```text
Root Directory: .
Install Command: cd frontend && npm install
Build Command: cd frontend && npm run build
Output Directory: frontend/dist
```

Option B, frontend folder:

```text
Root Directory: frontend
Install Command: npm install
Build Command: npm run build
Output Directory: dist
```

Vercel file for option B:

- `frontend/vercel.json`

Required Vercel variable:

```text
VITE_API_BASE_URL=https://your-railway-backend.up.railway.app
```

Do not add a trailing slash.

## 3. Connect CORS

After Vercel gives you the frontend URL, set this on Railway:

```text
BACKEND_CORS_ORIGINS=https://your-vercel-app.vercel.app
```

If you have multiple frontend domains, separate them with commas:

```text
BACKEND_CORS_ORIGINS=https://your-vercel-app.vercel.app,https://your-custom-domain.com
```

## 4. Important Notes

- Do not commit `.env`.
- Rotate any OpenAI key that was ever exposed in local files or screenshots.
- Railway file uploads stored in `/app/uploads` are not durable unless you attach persistent storage. For production, use object storage for uploaded media.
