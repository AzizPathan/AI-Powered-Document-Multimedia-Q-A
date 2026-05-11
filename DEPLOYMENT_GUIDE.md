# Complete Deployment Guide: Vercel Frontend + Railway Backend

## Overview

- **Frontend**: Deployed on Vercel (React + Vite)
- **Backend**: Deployed on Railway (FastAPI + Python)
- **Database**: PostgreSQL on Railway
- **Connection**: Frontend calls backend API via HTTPS

---

## Part 1: Deploy Backend on Railway

### Step 1: Create PostgreSQL Database

1. Go to [Railway](https://railway.app)
2. Create a new project
3. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
4. Railway will automatically provision the database
5. Note: `DATABASE_URL` will be automatically available

### Step 2: Deploy Backend Service

1. In the same Railway project, click **"+ New"** → **"GitHub Repo"**
2. Connect your GitHub account and select your repository
3. Railway will auto-detect the Dockerfile

### Step 3: Configure Backend Environment Variables

In your Railway backend service, go to **Variables** tab and add:

```env
# Automatically set when you connect PostgreSQL database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Required: Your OpenAI API key
OPENAI_API_KEY=sk-proj-your-key-here

# Required: Secure random string for JWT
JWT_SECRET=your-secure-random-string-here

# Required: Allow your Vercel frontend domain
BACKEND_CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173

# Optional: Redis for rate limiting
REDIS_URL=redis://redis.railway.internal:6379/0

# Optional: Rate limiting (default: 60)
RATE_LIMIT_PER_MINUTE=60
```

**Important**: To connect the database:
- Click **"New Variable"** → **"Add Reference"**
- Select your PostgreSQL database
- This automatically adds `DATABASE_URL`

### Step 4: Get Your Backend URL

1. Go to your backend service **Settings** tab
2. Under **"Networking"**, click **"Generate Domain"**
3. Copy the URL (e.g., `https://your-backend.railway.app`)
4. Save this URL - you'll need it for Vercel!

---

## Part 2: Deploy Frontend on Vercel

### Step 1: Prepare Vercel Configuration

Your `vercel.json` is already configured! It should look like this:

```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Step 2: Deploy to Vercel

**Option A: Using Vercel Dashboard**

1. Go to [Vercel](https://vercel.com)
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository
4. Vercel will auto-detect the configuration
5. Click **"Deploy"**

**Option B: Using Vercel CLI**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# For production
vercel --prod
```

### Step 3: Configure Frontend Environment Variables

In Vercel project settings, go to **Settings** → **Environment Variables** and add:

```env
VITE_API_BASE_URL=https://your-backend.railway.app
```

**Important**: 
- Replace `https://your-backend.railway.app` with your actual Railway backend URL
- No trailing slash!
- This variable is used at build time, so you need to redeploy after adding it

### Step 4: Redeploy Frontend

After adding the environment variable:
1. Go to **Deployments** tab
2. Click the **"..."** menu on the latest deployment
3. Click **"Redeploy"**

---

## Part 3: Connect Frontend to Backend

### Update Backend CORS Settings

1. Go back to Railway backend service
2. Update `BACKEND_CORS_ORIGINS` variable to include your Vercel URL:

```env
BACKEND_CORS_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app,http://localhost:5173
```

**Note**: Include all Vercel preview URLs if needed:
- Production: `https://your-app.vercel.app`
- Preview: `https://your-app-git-branch.vercel.app`
- Local dev: `http://localhost:5173`

### Test the Connection

1. Open your Vercel URL: `https://your-app.vercel.app`
2. Try to register/login
3. Upload a file
4. Ask a question

If you see CORS errors, double-check the `BACKEND_CORS_ORIGINS` variable in Railway.

---

## Part 4: Environment Variables Summary

### Railway Backend Variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | `postgresql://...` | Auto-set when database connected |
| `OPENAI_API_KEY` | ✅ | `sk-proj-...` | Your OpenAI API key |
| `JWT_SECRET` | ✅ | `random-string-123` | Secure random string |
| `BACKEND_CORS_ORIGINS` | ✅ | `https://app.vercel.app` | Comma-separated frontend URLs |
| `REDIS_URL` | ❌ | `redis://...` | Optional for rate limiting |
| `RATE_LIMIT_PER_MINUTE` | ❌ | `60` | Optional rate limit |

### Vercel Frontend Variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | ✅ | `https://backend.railway.app` | Your Railway backend URL |

---

## Part 5: Troubleshooting

### Backend Issues

**Problem**: Health check fails
- **Solution**: Check Railway logs for errors
- Verify all required environment variables are set
- Ensure `DATABASE_URL` is connected

**Problem**: Database connection error
- **Solution**: Make sure PostgreSQL database is linked to backend service
- Check `DATABASE_URL` format: `postgresql://user:pass@host:port/dbname`

**Problem**: Port binding error
- **Solution**: Already fixed! Dockerfile uses `${PORT:-8000}`

### Frontend Issues

**Problem**: "Cannot reach the backend API"
- **Solution**: Check `VITE_API_BASE_URL` is set correctly in Vercel
- Verify Railway backend is running and accessible
- Test backend directly: `curl https://your-backend.railway.app/health`

**Problem**: CORS errors
- **Solution**: Add your Vercel URL to `BACKEND_CORS_ORIGINS` in Railway
- Include both production and preview URLs
- No trailing slashes!

**Problem**: 404 on refresh
- **Solution**: Already fixed! `vercel.json` has rewrites configured

### Connection Issues

**Problem**: Frontend can't connect to backend
1. Test backend health: `curl https://your-backend.railway.app/health`
2. Should return: `{"status":"ok"}`
3. Check browser console for CORS errors
4. Verify `VITE_API_BASE_URL` in Vercel matches Railway backend URL
5. Verify `BACKEND_CORS_ORIGINS` in Railway includes Vercel URL

---

## Part 6: Local Development

### Backend (Railway)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Frontend (Vercel)
```bash
cd frontend
npm install
npm run dev
```

Create `frontend/.env.local`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8001
```

---

## Part 7: Deployment Checklist

### Before Deploying

- [ ] Backend code pushed to GitHub
- [ ] Frontend code pushed to GitHub
- [ ] `vercel.json` configured
- [ ] `railway.toml` configured
- [ ] `.dockerignore` created

### Railway Backend

- [ ] PostgreSQL database created
- [ ] Backend service connected to GitHub
- [ ] Database linked to backend service
- [ ] `DATABASE_URL` automatically set
- [ ] `OPENAI_API_KEY` added
- [ ] `JWT_SECRET` added
- [ ] `BACKEND_CORS_ORIGINS` added (with Vercel URL)
- [ ] Backend domain generated
- [ ] Health check passes: `/health` returns `{"status":"ok"}`

### Vercel Frontend

- [ ] Project imported from GitHub
- [ ] `VITE_API_BASE_URL` set to Railway backend URL
- [ ] Deployed successfully
- [ ] Can access frontend URL
- [ ] Can register/login
- [ ] Can upload files
- [ ] Can ask questions

---

## Part 8: Useful Commands

### Check Backend Health
```bash
curl https://your-backend.railway.app/health
```

### Check Backend CORS
```bash
curl -H "Origin: https://your-app.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://your-backend.railway.app/api/auth/register
```

### Redeploy Vercel
```bash
vercel --prod
```

### View Railway Logs
```bash
railway logs
```

---

## Quick Reference URLs

- **Railway Dashboard**: https://railway.app/dashboard
- **Vercel Dashboard**: https://vercel.com/dashboard
- **OpenAI API Keys**: https://platform.openai.com/api-keys

---

## Support

If you encounter issues:
1. Check Railway backend logs
2. Check Vercel deployment logs
3. Check browser console for errors
4. Verify all environment variables are set correctly
5. Test backend health endpoint directly
