# Railway Deployment Checklist

## Step-by-Step Setup Guide

### 1. Database Setup ✅
- [x] PostgreSQL database created and running

### 2. Backend Service Setup

- [ ] Create backend service in Railway
  - Connect to GitHub repo
  - Root directory: `/` (root)
  - Railway auto-detects `backend/Dockerfile`

- [ ] Set environment variables:
  ```
  DATABASE_URL=<auto-set when you link PostgreSQL>
  OPENAI_API_KEY=sk-proj-...
  JWT_SECRET=<generate with: openssl rand -hex 32>
  BACKEND_CORS_ORIGINS=http://localhost:5173
  ```

- [ ] Link PostgreSQL database to backend service
  - Go to backend service → Variables
  - Click "New Variable" → "Add Reference"
  - Select PostgreSQL database
  - This auto-adds DATABASE_URL

- [ ] Deploy backend
  - Should see "Deployment successful"
  - Health check passes at `/health`

- [ ] Get backend URL
  - Copy the Railway URL (e.g., `https://your-backend.railway.app`)

### 3. Frontend Service Setup

- [ ] Create frontend service in Railway
  - Same GitHub repo
  - Root directory: `/` (root)
  - Railway auto-detects `frontend/Dockerfile`

- [ ] Set build argument (IMPORTANT: This is a BUILD argument, not environment variable)
  - Go to Settings → Build
  - Add Docker Build Argument:
    - Name: `VITE_API_BASE_URL`
    - Value: `https://your-backend.railway.app` (your actual backend URL)

- [ ] Deploy frontend
  - Railway builds and deploys
  - Should see nginx serving the app

- [ ] Get frontend URL
  - Copy the Railway URL (e.g., `https://your-frontend.railway.app`)

### 4. Connect Frontend to Backend

- [ ] Update backend CORS settings
  - Go to backend service → Variables
  - Update `BACKEND_CORS_ORIGINS`:
    ```
    https://your-frontend.railway.app,http://localhost:5173
    ```
  - Backend will auto-redeploy

### 5. Test Everything

- [ ] Test backend health:
  ```bash
  curl https://your-backend.railway.app/health
  ```
  Should return: `{"status":"ok"}`

- [ ] Test frontend:
  - Open `https://your-frontend.railway.app` in browser
  - Should see the login page
  - Try registering with demo credentials:
    - Email: `demo@example.com`
    - Password: `password123`

- [ ] Test file upload:
  - Login
  - Upload a PDF or audio file
  - Check if it processes correctly

## Common Issues & Solutions

### Backend won't start
- Check DATABASE_URL is set (link PostgreSQL database)
- Check OPENAI_API_KEY is set
- Check logs for specific errors

### Frontend can't connect to backend
- Verify VITE_API_BASE_URL build argument is set correctly
- Check BACKEND_CORS_ORIGINS includes frontend URL
- Check browser console for CORS errors

### CORS errors
- Make sure frontend URL is in BACKEND_CORS_ORIGINS
- Include both http and https if needed
- No trailing slashes in URLs

### Build fails
- Check Dockerfile paths are correct
- Verify all dependencies are in package.json/requirements.txt
- Check Railway build logs for specific errors

## Railway Project Structure

```
Your Railway Project
├── PostgreSQL Database
│   └── Provides: DATABASE_URL
│
├── Backend Service
│   ├── Dockerfile: backend/Dockerfile
│   ├── Config: railway.toml
│   └── Environment Variables:
│       ├── DATABASE_URL (from PostgreSQL)
│       ├── OPENAI_API_KEY
│       ├── JWT_SECRET
│       └── BACKEND_CORS_ORIGINS
│
└── Frontend Service
    ├── Dockerfile: frontend/Dockerfile
    ├── Config: frontend/railway.toml
    └── Build Arguments:
        └── VITE_API_BASE_URL
```

## URLs to Save

- Backend URL: `https://_____.railway.app`
- Frontend URL: `https://_____.railway.app`
- Database URL: (internal, auto-configured)

## Next Steps After Deployment

1. Test all features (upload, chat, timestamps)
2. Set up custom domain (optional)
3. Configure Redis for better rate limiting (optional)
4. Set up monitoring and alerts
5. Review logs regularly
