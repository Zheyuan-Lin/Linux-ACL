import logging
import sys
import os
from typing import Dict, Any, Optional
from pathlib import Path

from app.core.config import settings


def setup_logging() -> None:
    """Configure logging for the application"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist and a log file is specified
    if settings.LOG_FILE:
        log_dir = os.path.dirname(settings.LOG_FILE)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Base logging configuration
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default",
                "level": log_level,
            },
        },
        "loggers": {
            "app": {"handlers": ["console"], "level": log_level, "propagate": False},
            "uvicorn": {"handlers": ["console"], "level": log_level, "propagate": False},
            "uvicorn.access": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
        },
        "root": {"handlers": ["console"], "level": log_level},
    }
    
    # Add file handler if log file is specified
    if settings.LOG_FILE:
        logging_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.LOG_FILE,
            "formatter": "default",
            "level": log_level,
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
        }
        
        # Add file handler to loggers
        for logger_name in ["app", "uvicorn", "uvicorn.access", "root"]:
            logging_config["loggers"].setdefault(logger_name, {})
            logging_config["loggers"][logger_name].setdefault("handlers", []).append("file")
    
    # Configure logging
    from logging.config import dictConfig
    dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return logging.getLogger(name)