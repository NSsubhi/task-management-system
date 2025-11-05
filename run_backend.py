"""
Backend server startup script
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable (Railway provides PORT)
    port = int(os.getenv("PORT", 8000))
    # Don't use reload in production (Railway)
    reload = os.getenv("ENV", "production") == "development"
    
    uvicorn.run("app.backend.main:app", host="0.0.0.0", port=port, reload=reload)

