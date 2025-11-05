# Railway Deployment Checklist

## ✅ Pre-Deployment Checklist

- [x] All code committed to Git
- [x] Repository pushed to GitHub
- [x] Railway configuration files created
- [x] Environment variables documented

## 🚀 Deployment Steps

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Create a new project

### Step 2: Deploy Backend Service

1. **Add Service from GitHub:**
   - Click "New" → "GitHub Repo"
   - Select your repository
   - Railway will auto-detect Python

2. **Configure Service:**
   - Service name: `backend` (or any name)
   - Root directory: `.` (root)
   - Start command: `python run_backend.py`

3. **Add Environment Variables:**
   ```
   SECRET_KEY=<generate-random-key>
   ```
   Generate secret key: `openssl rand -hex 32` or use online generator

4. **Add PostgreSQL Database:**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will auto-provision
   - Copy the `DATABASE_URL` (Railway sets this automatically)

5. **Generate Public Domain:**
   - Go to Settings → Generate Domain
   - Copy the URL (e.g., `https://your-backend.railway.app`)
   - This is your backend URL

### Step 3: Deploy Frontend Service

1. **Add Another Service:**
   - In the same project, click "New" → "GitHub Repo"
   - Select the same repository

2. **Configure Service:**
   - Service name: `frontend` (or any name)
   - Root directory: `.` (root)
   - Start command: `streamlit run app/frontend.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`

3. **Add Environment Variables:**
   ```
   API_URL=https://your-backend.railway.app
   ```
   Replace with your actual backend URL from Step 2

4. **Generate Public Domain:**
   - Go to Settings → Generate Domain
   - This is your frontend URL

### Step 4: Verify Deployment

1. Visit your frontend URL
2. You should see the login page
3. Register a new account
4. Create a project
5. Add tasks
6. Check analytics dashboard

## 🔧 Troubleshooting

### Backend won't start
- Check logs in Railway dashboard
- Verify `SECRET_KEY` is set
- Verify `DATABASE_URL` is set (auto-set by Railway)
- Check that port is correct (Railway uses `$PORT`)

### Frontend can't connect to backend
- Verify `API_URL` in frontend service matches backend URL
- Check backend is running (visit backend URL + `/health`)
- Verify CORS is enabled (already configured)

### Database errors
- Verify PostgreSQL is provisioned
- Check `DATABASE_URL` format
- Tables are auto-created on first run

## 📝 Important Notes

1. **Two Services Required:**
   - Backend (FastAPI) - one service
   - Frontend (Streamlit) - another service
   - Both in the same Railway project

2. **Environment Variables:**
   - Backend needs: `SECRET_KEY`, `DATABASE_URL` (auto-set)
   - Frontend needs: `API_URL` (set to backend URL)

3. **Database:**
   - Railway auto-provisions PostgreSQL
   - `DATABASE_URL` is automatically set
   - Tables are created automatically

4. **Cost:**
   - Railway free tier: $5/month credit
   - Should be sufficient for small-medium usage

## 🎯 Quick Commands

### Generate Secret Key (for SECRET_KEY)
```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

### Test Backend Health
Visit: `https://your-backend.railway.app/health`

Should return: `{"status":"healthy"}`

## 📚 Additional Resources

- Railway Docs: https://docs.railway.app
- FastAPI Docs: https://fastapi.tiangolo.com
- Streamlit Docs: https://docs.streamlit.io

