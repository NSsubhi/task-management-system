"""
Frontend server startup script for Railway
"""
import os
import sys
import subprocess

if __name__ == "__main__":
    # Get port from environment variable (Railway provides PORT)
    port = os.getenv("PORT", "8501")
    
    # Run Streamlit with proper arguments
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "app/frontend.py",
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ]
    
    # Run the command (this will block until Streamlit exits)
    subprocess.run(cmd)

