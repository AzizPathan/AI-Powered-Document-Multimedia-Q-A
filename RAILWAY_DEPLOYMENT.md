# Railway Deployment Guide

## Database Setup (PostgreSQL)

Your PostgreSQL database is already running! Railway automatically provides the `DATABASE_URL` variable.

## Backend Service Environment Variables

Set these environment variables in your Railway backend service:

### Required Variables:

1. **DATABASE_URL** (automatically set by Railway when you connect the PostgreSQL database)
   - Format: `postgresql://user:password@host:port/database`
   - Railway sets this automatically when you link the database

2. **OPENAI_API_KEY**
   - Your OpenAI API key
   - Get it from: https://platform.openai.com/api-keys
   - Example: `sk-proj-...`

3. **JWT_SECRET**
   - A secure random string for JWT token signing
   - Generate one: `openssl rand -hex 32` or use any random string
   - Example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

4. **BACKEND_CORS_ORIGINS**
   - Comma-separated list of allowed frontend URLs
   - Include your Railway frontend URL
   - Example: `https://your-frontend.railway.app,http://localhost:5173`

### Optional Variables:

5. **REDIS_URL** (optional, for rate limiting)
   - If you add a Redis service: `redis://redis.railway.internal:6379/0`
   - If not set, uses in-memory rate limiting

6. **UPLOAD_DIR** (optional)
   - Default: `uploads` (relative path works fine in Railway)
   - Railway has persistent storage

7. **RATE_LIMIT_PER_MINUTE** (optional)
   - Default: `60`
   - Number of requests allowed per minute per user

## Deployment Steps:

1. **Create PostgreSQL Database** ✅ (Already done!)
   - Your database is running and initialized

2. **Create Backend Service**
   - Connect to your GitHub repository
   - Railway will auto-detect the Dockerfile
   - Set root directory to: `/` (root of repo)

3. **Set Environment Variables**
   - Go to your backend service → Variables tab
   - Add all required variables listed above
   - Connect the PostgreSQL database (this sets DATABASE_URL automatically)

4. **Deploy**
   - Railway will automatically build and deploy
   - Check the deployment logs for any errors
   - Health check endpoint: `/health`

5. **Get Backend URL**
   - Railway provides a public URL like: `https://your-backend.railway.app`
   - Use this URL for your frontend's `VITE_API_BASE_URL`

## Frontend Deployment (Optional)

If deploying frontend to Railway:

1. **Create Frontend Service**
   - Connect to same GitHub repository
   - Set root directory to: `frontend`

2. **Set Environment Variable**
   - `VITE_API_BASE_URL=https://your-backend.railway.app`

3. **Deploy**
   - Railway will build and serve the frontend

## Troubleshooting:

- **Port Issues**: Fixed! The Dockerfile now properly uses Railway's PORT variable
- **Database Connection**: Make sure DATABASE_URL is set (automatic when database is linked)
- **CORS Errors**: Add your frontend URL to BACKEND_CORS_ORIGINS
- **Health Check Fails**: Check logs for startup errors (missing env vars, database connection issues)

## Testing:

Once deployed, test these endpoints:

```bash
# Health check
curl https://your-backend.railway.app/health

# Should return: {"status":"ok"}
```

## Current Status:

✅ PostgreSQL database is running
✅ Dockerfile is configured correctly
✅ railway.toml is configured
⏳ Set environment variables in Railway backend service
⏳ Deploy backend service
