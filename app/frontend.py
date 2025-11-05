"""
Streamlit Frontend for Task Management System
"""

import streamlit as st
import requests
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Task Management System",
    page_icon="📋",
    layout="wide"
)

# API URL - Set this in Railway environment variables
# For local: http://localhost:8000
# For Railway: Set API_URL to your backend service URL (e.g., https://your-backend.railway.app)
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

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
        # Validate required fields
        if not username or not email or not password:
            return False, "Please fill in all required fields (username, email, password)"
        
        response = requests.post(
            f"{API_URL}/api/register",
            json={
                "username": username.strip(),
                "email": email.strip(),
                "password": password,
                "full_name": full_name.strip() if full_name else None
            }
        )
        if response.status_code == 200:
            return True, "Registration successful!"
        else:
            # Try to get error details from response
            try:
                error_detail = response.json().get("detail", "Registration failed")
                if isinstance(error_detail, list):
                    # Pydantic validation errors
                    errors = []
                    for err in error_detail:
                        field = err.get("loc", [])[-1] if err.get("loc") else "unknown"
                        msg = err.get("msg", "Validation error")
                        errors.append(f"{field}: {msg}")
                    return False, "; ".join(errors)
                else:
                    return False, str(error_detail)
            except:
                return False, f"Registration failed: {response.status_code}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

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
            username = st.text_input("Username", placeholder="Enter username")
            email = st.text_input("Email", placeholder="user@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            full_name = st.text_input("Full Name (optional)", placeholder="Your full name")
            submit = st.form_submit_button("Register")
            
            if submit:
                success, message = register(username, email, password, full_name)
                if success:
                    st.success(message)
                    st.info("Please login with your credentials.")
                else:
                    st.error(message)
else:
    # Main dashboard
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Sidebar navigation
    with st.sidebar:
        st.title(f"👤 {st.session_state.user['username']}")
        if st.button("🚪 Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = "Dashboard"
            st.rerun()
        
        st.divider()
        
        # Navigation
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()
        if st.button("📋 Tasks", use_container_width=True):
            st.session_state.page = "Tasks"
            st.rerun()
        if st.button("📈 Analytics", use_container_width=True):
            st.session_state.page = "Analytics"
            st.rerun()
    
    # Main content area
    if st.session_state.page == "Dashboard":
        st.title("📊 Dashboard")
        
        # Quick stats
        try:
            analytics_response = requests.get(f"{API_URL}/api/analytics", headers=headers)
            if analytics_response.status_code == 200:
                analytics = analytics_response.json()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Tasks", analytics['total_tasks'])
                with col2:
                    st.metric("Completed Today", analytics['completed_today'])
                with col3:
                    st.metric("Completed This Week", analytics['completed_this_week'])
                with col4:
                    st.metric("Overdue Tasks", analytics['overdue_tasks'], delta=f"-{analytics['overdue_tasks']}")
                
                st.divider()
                
                # Tasks by status
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Tasks by Status")
                    status_data = analytics['tasks_by_status']
                    if sum(status_data.values()) > 0:
                        fig = px.pie(
                            values=list(status_data.values()),
                            names=list(status_data.keys()),
                            color_discrete_map={
                                "To Do": "#FF6B6B",
                                "In Progress": "#4ECDC4",
                                "Done": "#95E1D3"
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No tasks yet")
                
                with col2:
                    st.subheader("Tasks by Priority")
                    priority_data = analytics['tasks_by_priority']
                    if sum(priority_data.values()) > 0:
                        fig = px.bar(
                            x=list(priority_data.keys()),
                            y=list(priority_data.values()),
                            color=list(priority_data.keys()),
                            color_discrete_map={
                                "Low": "#3498db",
                                "Medium": "#f39c12",
                                "High": "#e74c3c",
                                "Urgent": "#c0392b"
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No tasks yet")
        except Exception as e:
            st.error(f"Error loading analytics: {e}")
        
        # Projects section
        st.divider()
        st.subheader("📁 Projects")
        
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
                            
                            # Get tasks for this project
                            tasks_response = requests.get(
                                f"{API_URL}/api/tasks?project_id={project['id']}",
                                headers=headers
                            )
                            if tasks_response.status_code == 200:
                                tasks = tasks_response.json()
                                st.write(f"**{len(tasks)} tasks** in this project")
                                
                                if tasks:
                                    for task in tasks[:5]:  # Show first 5
                                        status_emoji = {"To Do": "⏳", "In Progress": "🔄", "Done": "✅"}
                                        priority_color = {
                                            "Low": "🟢", "Medium": "🟡", "High": "🟠", "Urgent": "🔴"
                                        }
                                        st.write(
                                            f"{status_emoji.get(task['status'], '📌')} "
                                            f"{priority_color.get(task['priority'], '⚪')} "
                                            f"**{task['title']}** - {task['status']}"
                                        )
                                    if len(tasks) > 5:
                                        st.caption(f"... and {len(tasks) - 5} more tasks")
                else:
                    st.info("No projects yet. Create one above!")
        except Exception as e:
            st.error(f"Error: {e}")
    
    elif st.session_state.page == "Tasks":
        st.title("📋 Tasks")
        
        try:
            # Get all projects for filter
            projects_response = requests.get(f"{API_URL}/api/projects", headers=headers)
            projects = projects_response.json() if projects_response.status_code == 200 else []
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox(
                    "Filter by Status",
                    ["All", "To Do", "In Progress", "Done"],
                    key="status_filter"
                )
            with col2:
                priority_filter = st.selectbox(
                    "Filter by Priority",
                    ["All", "Low", "Medium", "High", "Urgent"],
                    key="priority_filter"
                )
            with col3:
                project_filter = st.selectbox(
                    "Filter by Project",
                    ["All"] + [p['name'] for p in projects],
                    key="project_filter"
                )
            
            # Get tasks
            tasks_response = requests.get(f"{API_URL}/api/tasks", headers=headers)
            if tasks_response.status_code == 200:
                all_tasks = tasks_response.json()
                
                # Apply filters
                filtered_tasks = all_tasks
                if status_filter != "All":
                    filtered_tasks = [t for t in filtered_tasks if t['status'] == status_filter]
                if priority_filter != "All":
                    filtered_tasks = [t for t in filtered_tasks if t['priority'] == priority_filter]
                if project_filter != "All":
                    project_id = next((p['id'] for p in projects if p['name'] == project_filter), None)
                    if project_id:
                        filtered_tasks = [t for t in filtered_tasks if t['project_id'] == project_id]
                
                st.write(f"**{len(filtered_tasks)} tasks** found")
                
                # Create new task
                with st.expander("➕ Create New Task"):
                    with st.form("create_task"):
                        project_names = {p['id']: p['name'] for p in projects}
                        selected_project = st.selectbox(
                            "Project",
                            options=list(project_names.keys()),
                            format_func=lambda x: project_names[x]
                        )
                        task_title = st.text_input("Task Title")
                        task_desc = st.text_area("Description")
                        task_priority = st.selectbox(
                            "Priority",
                            ["Low", "Medium", "High", "Urgent"]
                        )
                        task_status = st.selectbox(
                            "Status",
                            ["To Do", "In Progress", "Done"]
                        )
                        due_date = st.date_input("Due Date (optional)")
                        submit = st.form_submit_button("Create Task")
                        
                        if submit and task_title:
                            task_data = {
                                "title": task_title,
                                "description": task_desc,
                                "project_id": selected_project,
                                "priority": task_priority,
                                "status": task_status
                            }
                            if due_date:
                                task_data["due_date"] = datetime.combine(due_date, datetime.min.time()).isoformat()
                            
                            response = requests.post(
                                f"{API_URL}/api/tasks",
                                json=task_data,
                                headers=headers
                            )
                            if response.status_code == 200:
                                st.success("Task created!")
                                st.rerun()
                
                # Display tasks
                if filtered_tasks:
                    for task in filtered_tasks:
                        # Get project name
                        project_name = next((p['name'] for p in projects if p['id'] == task['project_id']), "Unknown")
                        
                        with st.container():
                            status_emoji = {"To Do": "⏳", "In Progress": "🔄", "Done": "✅"}
                            priority_color = {
                                "Low": "🟢", "Medium": "🟡", "High": "🟠", "Urgent": "🔴"
                            }
                            
                            col1, col2, col3 = st.columns([3, 2, 1])
                            with col1:
                                st.write(
                                    f"{status_emoji.get(task['status'], '📌')} "
                                    f"{priority_color.get(task['priority'], '⚪')} "
                                    f"**{task['title']}**"
                                )
                                st.caption(f"📁 {project_name}")
                                if task.get('description'):
                                    st.caption(task['description'][:100] + "..." if len(task.get('description', '')) > 100 else task['description'])
                            
                            with col2:
                                # Status update
                                current_status = task['status']
                                new_status = st.selectbox(
                                    "Status",
                                    ["To Do", "In Progress", "Done"],
                                    index=["To Do", "In Progress", "Done"].index(current_status),
                                    key=f"status_{task['id']}"
                                )
                                if new_status != current_status:
                                    response = requests.patch(
                                        f"{API_URL}/api/tasks/{task['id']}/status",
                                        json={"status": new_status},
                                        headers=headers
                                    )
                                    if response.status_code == 200:
                                        st.rerun()
                            
                            with col3:
                                # Priority update
                                current_priority = task['priority']
                                new_priority = st.selectbox(
                                    "Priority",
                                    ["Low", "Medium", "High", "Urgent"],
                                    index=["Low", "Medium", "High", "Urgent"].index(current_priority),
                                    key=f"priority_{task['id']}"
                                )
                                if new_priority != current_priority:
                                    response = requests.patch(
                                        f"{API_URL}/api/tasks/{task['id']}/priority",
                                        json={"priority": new_priority},
                                        headers=headers
                                    )
                                    if response.status_code == 200:
                                        st.rerun()
                                
                                # Delete button
                                if st.button("🗑️", key=f"delete_{task['id']}"):
                                    response = requests.delete(
                                        f"{API_URL}/api/tasks/{task['id']}",
                                        headers=headers
                                    )
                                    if response.status_code == 200:
                                        st.success("Task deleted!")
                                        st.rerun()
                            
                            # Task details
                            with st.expander("View Details & Comments"):
                                # Task info
                                st.write(f"**Status:** {task['status']}")
                                st.write(f"**Priority:** {task['priority']}")
                                if task.get('due_date'):
                                    due_date = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                                    st.write(f"**Due Date:** {due_date.strftime('%Y-%m-%d %H:%M')}")
                                st.write(f"**Created:** {datetime.fromisoformat(task['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')}")
                                
                                # Comments section
                                st.divider()
                                st.subheader("💬 Comments")
                                
                                # Get comments
                                comments_response = requests.get(
                                    f"{API_URL}/api/tasks/{task['id']}/comments",
                                    headers=headers
                                )
                                if comments_response.status_code == 200:
                                    comments = comments_response.json()
                                    
                                    # Display comments
                                    for comment in comments:
                                        st.write(f"**{datetime.fromisoformat(comment['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')}**")
                                        st.write(comment['content'])
                                        st.divider()
                                
                                # Add comment
                                with st.form(f"comment_form_{task['id']}"):
                                    comment_text = st.text_area("Add a comment")
                                    submit_comment = st.form_submit_button("Post Comment")
                                    if submit_comment and comment_text:
                                        response = requests.post(
                                            f"{API_URL}/api/comments",
                                            json={
                                                "content": comment_text,
                                                "task_id": task['id']
                                            },
                                            headers=headers
                                        )
                                        if response.status_code == 200:
                                            st.success("Comment added!")
                                            st.rerun()
                            
                            st.divider()
                else:
                    st.info("No tasks found with the selected filters.")
            else:
                st.error("Failed to load tasks")
        except Exception as e:
            st.error(f"Error: {e}")
    
    elif st.session_state.page == "Analytics":
        st.title("📈 Analytics Dashboard")
        
        try:
            analytics_response = requests.get(f"{API_URL}/api/analytics", headers=headers)
            if analytics_response.status_code == 200:
                analytics = analytics_response.json()
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Tasks", analytics['total_tasks'])
                with col2:
                    st.metric("Completed Today", analytics['completed_today'])
                with col3:
                    st.metric("Completed This Week", analytics['completed_this_week'])
                with col4:
                    st.metric("Overdue Tasks", analytics['overdue_tasks'])
                
                st.divider()
                
                # Charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Tasks by Status")
                    status_data = analytics['tasks_by_status']
                    if sum(status_data.values()) > 0:
                        fig = px.pie(
                            values=list(status_data.values()),
                            names=list(status_data.keys()),
                            color_discrete_map={
                                "To Do": "#FF6B6B",
                                "In Progress": "#4ECDC4",
                                "Done": "#95E1D3"
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No tasks yet")
                
                with col2:
                    st.subheader("Tasks by Priority")
                    priority_data = analytics['tasks_by_priority']
                    if sum(priority_data.values()) > 0:
                        fig = px.bar(
                            x=list(priority_data.keys()),
                            y=list(priority_data.values()),
                            color=list(priority_data.keys()),
                            color_discrete_map={
                                "Low": "#3498db",
                                "Medium": "#f39c12",
                                "High": "#e74c3c",
                                "Urgent": "#c0392b"
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No tasks yet")
                
                # Tasks by project
                st.divider()
                st.subheader("Tasks by Project")
                project_data = analytics['tasks_by_project']
                if project_data:
                    fig = px.bar(
                        x=list(project_data.keys()),
                        y=list(project_data.values()),
                        labels={'x': 'Project', 'y': 'Number of Tasks'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No projects with tasks yet")
                
                # Summary table
                st.divider()
                st.subheader("Summary")
                summary_data = {
                    "Metric": ["Total Tasks", "To Do", "In Progress", "Done", "Completed Today", "Completed This Week", "Overdue"],
                    "Value": [
                        analytics['total_tasks'],
                        analytics['tasks_by_status'].get('To Do', 0),
                        analytics['tasks_by_status'].get('In Progress', 0),
                        analytics['tasks_by_status'].get('Done', 0),
                        analytics['completed_today'],
                        analytics['completed_this_week'],
                        analytics['overdue_tasks']
                    ]
                }
                df = pd.DataFrame(summary_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.error("Failed to load analytics")
        except Exception as e:
            st.error(f"Error loading analytics: {e}")
