from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.database import User, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

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
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def has_role(required_roles: List[str]):
    """Check if user has required roles"""
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> bool:
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