# Railway Deployment Guide

## Quick Start

### 1. Prepare Your Repository
Make sure all files are committed and pushed to GitHub.

### 2. Deploy Backend Service

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repository
4. Railway will detect it's a Python project
5. In **Settings**:
   - **Start Command**: `python run_backend.py`
   - **Healthcheck Path**: `/health`
6. Add **Environment Variables**:
   - `SECRET_KEY`: Generate with `openssl rand -hex 32` or use [this generator](https://randomkeygen.com/)
   - `DATABASE_URL`: Railway will auto-provision PostgreSQL - use the provided URL
7. Click **Generate Domain** to get a public URL (e.g., `https://your-backend.railway.app`)

### 3. Deploy Frontend Service

1. In the same Railway project, click **+ New Service** → **GitHub Repo**
2. Select the same repository
3. In **Settings**:
   - **Start Command**: `streamlit run app/frontend.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
   - **Healthcheck Path**: `/`
4. Add **Environment Variables**:
   - `API_URL`: Set to your backend's public URL (from step 2)
   - Example: `https://your-backend.railway.app`
5. Click **Generate Domain** to get a public URL

### 4. Verify Deployment

1. Visit your frontend URL
2. Register a new account
3. Create a project and tasks
4. Check the Analytics dashboard

## Troubleshooting

### Backend Issues
- Check logs in Railway dashboard
- Verify `SECRET_KEY` is set
- Verify `DATABASE_URL` is set (Railway auto-provisions this)
- Check that port is correctly set (Railway uses `$PORT`)

### Frontend Issues
- Verify `API_URL` points to your backend service URL
- Check that backend is running and accessible
- Verify CORS is enabled (already configured in backend)

### Database Issues
- Railway auto-provisions PostgreSQL
- Tables are created automatically on first run
- If issues occur, check `DATABASE_URL` format

## Environment Variables Reference

### Backend
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host:port/dbname
PORT=8000
```

### Frontend
```
API_URL=https://your-backend.railway.app
PORT=8501
```

## Cost
Railway offers a free tier with $5 credit per month. This should be sufficient for small to medium usage.

