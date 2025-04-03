from datetime import datetime, timedelta
from typing import Any, Union, Optional, List

from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.database import User, ProjectMember

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[datetime] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


def has_role(required_roles: List[str]):
    """Check if user has required roles"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> bool:
        user_roles = {role.name for role in current_user.roles}
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return True
    return role_checker


def is_project_member(project_id: int, min_access_level: Optional[str] = None):
    """Check if user is a member of the project with sufficient access level"""
    async def project_member_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> bool:
        # PI always has access
        if any(role.name == "pi" for role in current_user.roles):
            return True
            
        membership = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id
            )
            .first()
        )
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a project member"
            )
            
        if min_access_level:
            access_levels = {"read": 0, "write": 1, "admin": 2}
            if access_levels[membership.access_level] < access_levels[min_access_level]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires {min_access_level} access"
                )
                
        return True
    return project_member_checker