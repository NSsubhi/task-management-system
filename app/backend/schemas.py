"""
Pydantic schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import TaskStatus, Priority

# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

# Project schemas
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Task schemas
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    project_id: int
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: Priority
    project_id: int
    assignee_id: Optional[int]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Comment schemas
class CommentCreate(BaseModel):
    content: str
    task_id: int

class CommentResponse(BaseModel):
    id: int
    content: str
    task_id: int
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

