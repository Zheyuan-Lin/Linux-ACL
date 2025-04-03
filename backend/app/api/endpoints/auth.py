from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    get_current_user,
    is_project_member,
    has_role,
    verify_password,
    create_access_token
)
from app.models.database import User, Project
from app.schemas.auth import UserResponse, TokenResponse

router = APIRouter()
logger = logging.getLogger(__name__)

def get_project_member_checker(project_id: int, min_access_level: str = "read"):
    return Depends(is_project_member(project_id, min_access_level))

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            username=user.username,
            email=user.email,
            roles=[role.name for role in user.roles]
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        username=current_user.username,
        email=current_user.email,
        roles=[role.name for role in current_user.roles]
    )

@router.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_project_member_checker(project_id))
):
    """Get project details if user has access"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.post("/projects")
async def create_project(
    project: Project,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: bool = Depends(has_role(["pi"]))
):
    """Create a new project (PI only)"""
    db_project = Project(
        name=project.name,
        description=project.description,
        storage_path=project.storage_path,
        pi_id=current_user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project