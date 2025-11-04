"""
Streamlit Frontend for Task Management System
"""

import streamlit as st
import requests
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Task Management System",
    page_icon="📋",
    layout="wide"
)

# API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None

# Authentication
def login(username: str, password: str):
    """Login and get token"""
    try:
        response = requests.post(
            f"{API_URL}/api/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data["access_token"]
            # Get user info
            user_response = requests.get(
                f"{API_URL}/api/me",
                headers={"Authorization": f"Bearer {st.session_state.token}"}
            )
            if user_response.status_code == 200:
                st.session_state.user = user_response.json()
            return True
        return False
    except:
        return False

def register(username: str, email: str, password: str, full_name: str = ""):
    """Register new user"""
    try:
        response = requests.post(
            f"{API_URL}/api/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name
            }
        )
        return response.status_code == 200
    except:
        return False

# Main app
if st.session_state.token is None:
    # Login/Register page
    st.title("📋 Task Management System")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if login(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            full_name = st.text_input("Full Name (optional)")
            submit = st.form_submit_button("Register")
            
            if submit:
                if register(username, email, password, full_name):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed")
else:
    # Main dashboard
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    st.title("📋 Task Management System")
    
    # Sidebar
    with st.sidebar:
        st.write(f"Welcome, **{st.session_state.user['username']}**!")
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
    
    # Projects
    st.subheader("Projects")
    
    # Create project
    with st.expander("➕ Create New Project"):
        with st.form("create_project"):
            project_name = st.text_input("Project Name")
            project_desc = st.text_area("Description")
            submit = st.form_submit_button("Create")
            
            if submit:
                response = requests.post(
                    f"{API_URL}/api/projects",
                    json={"name": project_name, "description": project_desc},
                    headers=headers
                )
                if response.status_code == 200:
                    st.success("Project created!")
                    st.rerun()
    
    # List projects
    try:
        projects_response = requests.get(f"{API_URL}/api/projects", headers=headers)
        if projects_response.status_code == 200:
            projects = projects_response.json()
            
            if projects:
                for project in projects:
                    with st.expander(f"📁 {project['name']}"):
                        st.write(project.get('description', 'No description'))
                        
                        # Tasks for this project
                        tasks_response = requests.get(
                            f"{API_URL}/api/tasks?project_id={project['id']}",
                            headers=headers
                        )
                        if tasks_response.status_code == 200:
                            tasks = tasks_response.json()
                            
                            # Create task
                            with st.form(f"create_task_{project['id']}"):
                                task_title = st.text_input("Task Title")
                                task_desc = st.text_area("Description")
                                submit = st.form_submit_button("Add Task")
                                
                                if submit:
                                    response = requests.post(
                                        f"{API_URL}/api/tasks",
                                        json={
                                            "title": task_title,
                                            "description": task_desc,
                                            "project_id": project['id']
                                        },
                                        headers=headers
                                    )
                                    if response.status_code == 200:
                                        st.success("Task created!")
                                        st.rerun()
                            
                            # List tasks
                            if tasks:
                                for task in tasks:
                                    st.write(f"- {task['title']} ({task['status']})")
                            else:
                                st.info("No tasks yet")
            else:
                st.info("No projects yet. Create one above!")
    except Exception as e:
        st.error(f"Error: {e}")

