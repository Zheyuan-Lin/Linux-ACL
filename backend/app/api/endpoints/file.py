from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Response
from fastapi.responses import StreamingResponse
import mimetypes
import os
from typing import List, Optional
import logging

from app.services.file_service import (
    list_directory, get_file_info, read_file, create_directory,
    FileInfo
)
from app.core.security import get_current_user
from app.models.user import User
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/browse/{path:path}", response_model=List[FileInfo])
async def browse_directory(
    path: str = Path("", description="Directory path to browse"),
    current_user: User = Depends(get_current_user)
):
    """
    List contents of a directory
    """
    try:
        result = await list_directory(path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except NotADirectoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error browsing directory {path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error browsing directory: {str(e)}"
        )


@router.get("/info/{path:path}", response_model=FileInfo)
async def get_file_or_dir_info(
    path: str = Path(..., description="Path to get info for"),
    current_user: User = Depends(get_current_user)
):
    """
    Get information about a file or directory
    """
    try:
        result = await get_file_info(path)
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
        logger.error(f"Error getting info for {path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting file info: {str(e)}"
        )


@router.get("/preview/{path:path}")
async def preview_file(
    path: str = Path(..., description="File path to preview"),
    current_user: User = Depends(get_current_user)
):
    """
    Preview a file (for supported file types)
    """
    try:
        # Check file extension
        file_ext = os.path.splitext(path)[1].lower().lstrip(".")
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{file_ext}' is not supported for preview"
            )
        
        # Get file contents
        content = await read_file(path)
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(path)
        if not mime_type:
            mime_type = "application/octet-stream"
        
        # Return file as streaming response
        return StreamingResponse(
            iter([content]),
            media_type=mime_type,
            headers={"Content-Disposition": f"inline; filename={os.path.basename(path)}"}
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except IsADirectoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error previewing file {path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error previewing file: {str(e)}"
        )


@router.post("/directory/{path:path}", response_model=FileInfo)
async def create_new_directory(
    path: str = Path(..., description="Directory path to create"),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new directory
    """
    try:
        result = await create_directory(path)
        return result
    except FileExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating directory {path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating directory: {str(e)}"
        )