"""
FastAPI Backend for Task Management System
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

try:
    from .database import engine, get_db, Base
    from .models import User, Project, Task, Comment, TaskStatus, Priority
    from .schemas import (
        UserCreate, UserResponse, Token, LoginRequest,
        ProjectCreate, ProjectResponse,
        TaskCreate, TaskResponse, TaskStatusUpdate, TaskPriorityUpdate,
        CommentCreate, CommentResponse,
        AnalyticsResponse
    )
    from .auth import (
        get_password_hash, verify_password,
        create_access_token, decode_access_token,
        ACCESS_TOKEN_EXPIRE_MINUTES
    )
except ImportError:
    from app.backend.database import engine, get_db, Base
    from app.backend.models import User, Project, Task, Comment, TaskStatus, Priority
    from app.backend.schemas import (
        UserCreate, UserResponse, Token, LoginRequest,
        ProjectCreate, ProjectResponse,
        TaskCreate, TaskResponse, TaskStatusUpdate, TaskPriorityUpdate,
        CommentCreate, CommentResponse,
        AnalyticsResponse
    )
    from app.backend.auth import (
        get_password_hash, verify_password,
        create_access_token, decode_access_token,
        ACCESS_TOKEN_EXPIRE_MINUTES
    )

# Create tables
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Task Management API",
    description="Jira/Trello-like task management system",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# Helper functions
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from token"""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

# Routes
@app.get("/")
async def root():
    return {"message": "Task Management API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Auth routes
@app.post("/api/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if user exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get token"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

# Project routes
@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new project"""
    db_project = Project(
        name=project.name,
        description=project.description,
        owner_id=current_user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/api/projects", response_model=List[ProjectResponse])
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's projects"""
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    return projects

# Task routes
@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new task"""
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/api/tasks", response_model=List[TaskResponse])
async def get_tasks(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks with optional filters"""
    query = db.query(Task).join(Project).filter(Project.owner_id == current_user.id)
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if status:
        try:
            status_enum = TaskStatus(status)
            query = query.filter(Task.status == status_enum)
        except ValueError:
            pass
    if priority:
        try:
            priority_enum = Priority(priority)
            query = query.filter(Task.priority == priority_enum)
        except ValueError:
            pass
    
    tasks = query.all()
    return tasks

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single task"""
    db_task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task"""
    db_task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for key, value in task.dict().items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@app.patch("/api/tasks/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task status only"""
    db_task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.status = status_update.status
    db.commit()
    db.refresh(db_task)
    return db_task

@app.patch("/api/tasks/{task_id}/priority", response_model=TaskResponse)
async def update_task_priority(
    task_id: int,
    priority_update: TaskPriorityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task priority only"""
    db_task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.priority = priority_update.priority
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/api/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete task"""
    db_task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

# Comment routes
@app.post("/api/comments", response_model=CommentResponse)
async def create_comment(
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new comment"""
    # Verify task exists and belongs to user
    task = db.query(Task).join(Project).filter(
        Task.id == comment.task_id,
        Project.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_comment = Comment(
        content=comment.content,
        task_id=comment.task_id,
        author_id=current_user.id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/api/tasks/{task_id}/comments", response_model=List[CommentResponse])
async def get_task_comments(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comments for a task"""
    # Verify task exists and belongs to user
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    comments = db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at.desc()).all()
    return comments

@app.delete("/api/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete comment"""
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Only allow deleting own comments
    if db_comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

# Analytics route
@app.get("/api/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics data"""
    # Get all tasks for user's projects
    tasks = db.query(Task).join(Project).filter(Project.owner_id == current_user.id).all()
    
    # Count by status
    tasks_by_status = {}
    for status in TaskStatus:
        tasks_by_status[status.value] = sum(1 for t in tasks if t.status == status)
    
    # Count by priority
    tasks_by_priority = {}
    for priority in Priority:
        tasks_by_priority[priority.value] = sum(1 for t in tasks if t.priority == priority)
    
    # Count by project
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    tasks_by_project = {p.name: sum(1 for t in tasks if t.project_id == p.id) for p in projects}
    
    # Overdue tasks
    now = datetime.utcnow()
    overdue_tasks = sum(1 for t in tasks if t.due_date and t.due_date < now and t.status != TaskStatus.DONE)
    
    # Completed today
    today = datetime.utcnow().date()
    completed_today = sum(1 for t in tasks if t.status == TaskStatus.DONE and t.updated_at.date() == today)
    
    # Completed this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    completed_this_week = sum(1 for t in tasks if t.status == TaskStatus.DONE and t.updated_at >= week_ago)
    
    return AnalyticsResponse(
        total_tasks=len(tasks),
        tasks_by_status=tasks_by_status,
        tasks_by_priority=tasks_by_priority,
        tasks_by_project=tasks_by_project,
        overdue_tasks=overdue_tasks,
        completed_today=completed_today,
        completed_this_week=completed_this_week
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

