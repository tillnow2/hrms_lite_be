import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'logs/hrms_lite.log',
                maxBytes=10485760,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("motor").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)
