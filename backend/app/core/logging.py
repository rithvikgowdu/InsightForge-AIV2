import logging
import sys
from app.core.config import settings

def setup_logging() -> logging.Logger:
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    logger = logging.getLogger("insightforge")
    logger.setLevel(level)
    return logger

logger = setup_logging()

