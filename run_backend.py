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
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Get port from environment variable (Railway provides PORT)
        port = int(os.getenv("PORT", 8000))
        logger.info(f"Starting server on port {port}")
        
        # Don't use reload in production (Railway)
        reload = os.getenv("ENV", "production") == "development"
        
        # Log environment variables (without sensitive data)
        logger.info(f"ENV: {os.getenv('ENV', 'production')}")
        logger.info(f"DATABASE_URL set: {bool(os.getenv('DATABASE_URL'))}")
        logger.info(f"SECRET_KEY set: {bool(os.getenv('SECRET_KEY'))}")
        
        # Run the server
        uvicorn.run(
            "app.backend.main:app",
            host="0.0.0.0",
            port=port,
            reload=reload,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        raise

