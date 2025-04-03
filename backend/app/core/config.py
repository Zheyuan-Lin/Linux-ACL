import os
import secrets
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # LDAP Settings
    LDAP_SERVER: str = "localhost"  # Default for development
    LDAP_PORT: int = 389
    LDAP_BASE_DN: str = "dc=example,dc=com"
    LDAP_USER_DN_TEMPLATE: str = "uid={username},ou={institution},dc=example,dc=com"
    LDAP_BIND_USER: Optional[str] = None
    LDAP_BIND_PASSWORD: Optional[str] = None
    
    # File System Settings
    BASE_DIRECTORY: str = "/data"
    ALLOWED_EXTENSIONS: List[str] = ["csv", "txt", "pdf", "jpg", "jpeg", "png"]
    MAX_FILE_SIZE_MB: int = 100
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()