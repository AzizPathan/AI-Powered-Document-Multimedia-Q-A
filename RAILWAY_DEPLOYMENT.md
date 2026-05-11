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

## Frontend Deployment

### Option 1: Deploy Frontend to Railway (Recommended)

1. **Create a New Service in Railway**
   - In your Railway project, click "New Service"
   - Select "GitHub Repo"
   - Choose your repository: `AzizPathan/AI-Powered-Document-Multimedia-Q-A`
   - Railway will create a new service

2. **Configure the Frontend Service**
   - Service name: `frontend` (or any name you prefer)
   - Root directory: Leave as `/` (root)
   - Railway will auto-detect the Dockerfile

3. **Set Build Arguments**
   - Go to service Settings → Build
   - Add build argument:
     - Key: `VITE_API_BASE_URL`
     - Value: `https://your-backend.railway.app` (use your actual backend URL)

4. **Deploy**
   - Railway will automatically build using `frontend/Dockerfile`
   - The build process:
     - Installs dependencies
     - Builds the React app with Vite
     - Serves it with Nginx
   - Get your frontend URL: `https://your-frontend.railway.app`

5. **Update Backend CORS**
   - Go back to your backend service
   - Update `BACKEND_CORS_ORIGINS` environment variable
   - Add your frontend URL: `https://your-frontend.railway.app`
   - Example: `https://your-frontend.railway.app,http://localhost:5173`

### Option 2: Deploy Frontend to Vercel

If you prefer Vercel for the frontend:

1. **Connect Repository to Vercel**
   - Go to vercel.com
   - Import your GitHub repository
   - Root directory: `frontend`

2. **Configure Build Settings**
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Set Environment Variable**
   - Add: `VITE_API_BASE_URL=https://your-backend.railway.app`

4. **Deploy**
   - Vercel will build and deploy
   - Get your URL: `https://your-project.vercel.app`

5. **Update Backend CORS**
   - Add Vercel URL to `BACKEND_CORS_ORIGINS` in Railway backend

### Testing the Full Stack:

Once both are deployed:

```bash
# Test backend
curl https://your-backend.railway.app/health
# Should return: {"status":"ok"}

# Test frontend
# Open https://your-frontend.railway.app in browser
# You should see the login page
```

### Important Notes:

- **CORS Configuration**: Make sure your frontend URL is in `BACKEND_CORS_ORIGINS`
- **API URL**: The frontend needs `VITE_API_BASE_URL` set to your backend URL
- **Build Time**: The frontend build argument must be set BEFORE building (not as runtime env var)

## Current Status:

✅ PostgreSQL database is running
✅ Dockerfile is configured correctly  
✅ railway.toml is configured for both services
✅ Frontend Dockerfile updated for Railway deployment
⏳ Set environment variables in Railway backend service
⏳ Deploy backend service
⏳ Create frontend service in Railway
⏳ Set VITE_API_BASE_URL build argument in frontend
⏳ Update BACKEND_CORS_ORIGINS with frontend URL

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
