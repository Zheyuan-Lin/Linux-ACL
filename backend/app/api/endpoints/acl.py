from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import List, Optional
import logging

from app.services.acl_service import (
    get_acl, set_acl, remove_acl,
    PathAcl, AclEntry
)
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{path:path}", response_model=PathAcl)
async def read_acl(
    path: str = Path(..., description="Path to get ACL for"),
    current_user: User = Depends(get_current_user)
):
    """
    Get ACL information for a file or directory
    """
    try:
        result = await get_acl(path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting ACL for {path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting ACL: {str(e)}"
        )


@router.post("/{path:path}", response_model=bool)
async def update_acl(
    entries: List[AclEntry],
    path: str = Path(..., description="Path to update ACL for"),
    current_user: User = Depends(get_current_user)
):
    """
    Add or update ACL entries for a file or directory
    """
    try:
        result = await set_acl(path, entries)
        return result
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating ACL for {path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating ACL: {str(e)}"
        )


@router.delete("/{path:path}", response_model=bool)
async def delete_acl(
    entries: List[AclEntry],
    path: str = Path(..., description="Path to update ACL for"),
    current_user: User = Depends(get_current_user)
):
    """
    Remove ACL entries for a file or directory
    """
    try:
        result = await remove_acl(path, entries)
        return result
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error removing ACL for {path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing ACL: {str(e)}"
        )