# Task Management System (Jira/Trello-like)

## Overview
A full-featured task management system similar to Jira/Trello with project management, task tracking, comments, attachments, and real-time updates.

## Features
- User authentication (JWT)
- Project management
- Task creation and tracking
- Task status workflow (To Do, In Progress, Done)
- Comments and attachments
- Priority levels
- Due dates
- User assignments
- Search and filtering
- Real-time updates
- Beautiful Streamlit UI
- Analytics Dashboard with charts

## Tech Stack
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Authentication**: JWT, bcrypt
- **ORM**: SQLAlchemy

## Local Development

### Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   python run_backend.py
   ```
   Backend will run on `http://localhost:8000`

5. Start the frontend (in a new terminal):
   ```bash
   streamlit run app/frontend.py
   ```
   Frontend will run on `http://localhost:8501`

## Railway Deployment

### Prerequisites
- Railway account
- Railway CLI installed (optional, can use web interface)

### Deployment Steps

#### Option 1: Using Railway Web Interface

1. **Create Backend Service:**
   - Go to [Railway](https://railway.app)
   - Create a new project
   - Add a new service from GitHub repository
   - Select your repository
   - In the service settings:
     - Set **Root Directory** to: `.` (root)
     - Set **Start Command** to: `python run_backend.py`
     - Add environment variables:
       - `SECRET_KEY`: Generate a random secret key (use `openssl rand -hex 32`)
       - `DATABASE_URL`: Railway will auto-provision PostgreSQL, use the provided URL
       - `PORT`: Railway sets this automatically
   - Railway will automatically detect and use `railway.toml`

2. **Create Frontend Service:**
   - In the same project, add another service
   - Use the same repository
   - In the service settings:
     - Set **Root Directory** to: `.` (root)
     - Set **Start Command** to: `streamlit run app/frontend.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
     - Add environment variables:
       - `API_URL`: Set this to your backend service's public URL (e.g., `https://your-backend.railway.app`)
       - `PORT`: Railway sets this automatically
   - Railway will automatically detect and use `railway-frontend.toml`

3. **Generate Public URLs:**
   - For both services, go to Settings → Generate Domain
   - Copy the backend URL and set it as `API_URL` in the frontend service

#### Option 2: Using Railway CLI

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login:
   ```bash
   railway login
   ```

3. Initialize project:
   ```bash
   railway init
   ```

4. Deploy backend:
   ```bash
   railway up --service backend
   ```

5. Deploy frontend:
   ```bash
   railway up --service frontend
   ```

### Environment Variables

#### Backend Service:
- `SECRET_KEY`: Secret key for JWT tokens (required)
- `DATABASE_URL`: PostgreSQL connection string (Railway auto-provisions)
- `PORT`: Port number (Railway sets automatically)

#### Frontend Service:
- `API_URL`: Backend service URL (e.g., `https://your-backend.railway.app`)
- `PORT`: Port number (Railway sets automatically)

### Database Setup

Railway automatically provisions PostgreSQL. The app will:
- Use `DATABASE_URL` from Railway
- Automatically create tables on first run
- Work with PostgreSQL out of the box

### Notes

- The backend service exposes the FastAPI app on port 8000 (or Railway's assigned port)
- The frontend service runs Streamlit and connects to the backend via `API_URL`
- Both services need to be in the same Railway project
- Make sure to set `API_URL` in the frontend service to point to your backend's public URL

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login and get token
- `GET /api/me` - Get current user info

### Projects
- `POST /api/projects` - Create project
- `GET /api/projects` - Get user's projects

### Tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks` - Get tasks (with filters: status, priority, project_id)
- `GET /api/tasks/{task_id}` - Get single task
- `PUT /api/tasks/{task_id}` - Update task
- `PATCH /api/tasks/{task_id}/status` - Update task status
- `PATCH /api/tasks/{task_id}/priority` - Update task priority
- `DELETE /api/tasks/{task_id}` - Delete task

### Comments
- `POST /api/comments` - Create comment
- `GET /api/tasks/{task_id}/comments` - Get task comments
- `DELETE /api/comments/{comment_id}` - Delete comment

### Analytics
- `GET /api/analytics` - Get analytics data

## License
MIT
