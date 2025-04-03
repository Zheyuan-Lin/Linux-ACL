import os
import subprocess
import shlex
from typing import List, Dict, Any, Optional, Tuple
import logging
from pydantic import BaseModel, validator

from app.core.config import settings
from app.utils.shell import run_command, CommandResult

logger = logging.getLogger(__name__)


class AclEntry(BaseModel):
    """Model representing a single ACL entry"""
    type: str  # "user" or "group"
    name: str  # username or group name
    permissions: str  # rwx format: "r--", "rw-", etc.
    default: bool = False  # Whether this is a default ACL
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ["user", "group"]:
            raise ValueError(f"Type must be 'user' or 'group', not '{v}'")
        return v
    
    @validator('permissions')
    def validate_permissions(cls, v):
        if not all(c in 'rwx-' for c in v) or len(v) != 3:
            raise ValueError(f"Permissions must be in format 'rwx', not '{v}'")
        return v


class PathAcl(BaseModel):
    """Model representing all ACL entries for a path"""
    path: str
    owner: str
    group: str
    entries: List[AclEntry]
    default_entries: Optional[List[AclEntry]] = None


async def get_acl(path: str) -> PathAcl:
    """
    Get ACL information for a path using getfacl
    
    Args:
        path: Path to get ACL for
        
    Returns:
        PathAcl object containing ACL information
    """
    # Ensure path is within allowed base directory
    full_path = os.path.normpath(os.path.join(settings.BASE_DIRECTORY, path.lstrip("/")))
    if not full_path.startswith(settings.BASE_DIRECTORY):
        raise ValueError(f"Path {path} is outside of base directory")
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Path {full_path} does not exist")
    
    # Run getfacl command
    result = await run_command(f"getfacl -c {shlex.quote(full_path)}")
    if result.returncode != 0:
        logger.error(f"Error getting ACL for {full_path}: {result.stderr}")
        raise RuntimeError(f"Error getting ACL: {result.stderr}")
    
    # Parse getfacl output
    return parse_getfacl_output(result.stdout, full_path)


def parse_getfacl_output(output: str, path: str) -> PathAcl:
    """
    Parse the output of getfacl to extract ACL information
    
    Args:
        output: getfacl command output
        path: Path the ACL is for
        
    Returns:
        PathAcl object containing ACL information
    """
    lines = output.strip().split("\n")
    
    # Initialize owner and group
    owner = ""
    group = ""
    entries = []
    default_entries = []
    
    for line in lines:
        line = line.strip()
        if line.startswith("user:") and ":" not in line[5:]:
            # Owner entry (e.g., "user::rwx")
            owner = "root"  # Default, would be extracted from ls -l in a real implementation
            permissions = line.split(":")[-1]
            entries.append(AclEntry(type="user", name=owner, permissions=permissions))
        elif line.startswith("group:") and ":" not in line[6:]:
            # Group entry (e.g., "group::r-x")
            group = "root"  # Default, would be extracted from ls -l in a real implementation
            permissions = line.split(":")[-1]
            entries.append(AclEntry(type="group", name=group, permissions=permissions))
        elif line.startswith("user:") and ":" in line[5:]:
            # Named user entry (e.g., "user:john:rwx")
            parts = line.split(":")
            name = parts[1]
            permissions = parts[2]
            entries.append(AclEntry(type="user", name=name, permissions=permissions))
        elif line.startswith("group:") and ":" in line[6:]:
            # Named group entry (e.g., "group:admins:rwx")
            parts = line.split(":")
            name = parts[1]
            permissions = parts[2]
            entries.append(AclEntry(type="group", name=name, permissions=permissions))
        elif line.startswith("default:"):
            # Default ACL entry (e.g., "default:user:john:rwx")
            parts = line.split(":")
            entry_type = parts[1]  # user or group
            
            if len(parts) == 3:  # default owner/group/other entry
                name = ""
                permissions = parts[2]
            else:  # named entry
                name = parts[2]
                permissions = parts[3]
            
            default_entries.append(
                AclEntry(type=entry_type, name=name, permissions=permissions, default=True)
            )
    
    return PathAcl(
        path=path,
        owner=owner,
        group=group,
        entries=entries,
        default_entries=default_entries
    )


async def set_acl(path: str, entries: List[AclEntry]) -> bool:
    """
    Set ACL entries for a path using setfacl
    
    Args:
        path: Path to set ACL for
        entries: List of AclEntry objects to set
        
    Returns:
        True if successful, raises exception otherwise
    """
    # Ensure path is within allowed base directory
    full_path = os.path.normpath(os.path.join(settings.BASE_DIRECTORY, path.lstrip("/")))
    if not full_path.startswith(settings.BASE_DIRECTORY):
        raise ValueError(f"Path {path} is outside of base directory")
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Path {full_path} does not exist")
    
    # Build setfacl commands for each entry
    for entry in entries:
        cmd_parts = ["setfacl"]
        
        # Handle default ACLs
        if entry.default:
            cmd_parts.append("-d")
        
        # Set the ACL
        acl_spec = f"{entry.type}:{entry.name}:{entry.permissions}"
        cmd_parts.extend(["-m", acl_spec])
        cmd_parts.append(shlex.quote(full_path))
        
        # Run the command
        cmd = " ".join(cmd_parts)
        result = await run_command(cmd)
        
        if result.returncode != 0:
            logger.error(f"Error setting ACL for {full_path}: {result.stderr}")
            raise RuntimeError(f"Error setting ACL: {result.stderr}")
    
    return True


async def remove_acl(path: str, entries: List[AclEntry]) -> bool:
    """
    Remove ACL entries for a path using setfacl
    
    Args:
        path: Path to modify ACL for
        entries: List of AclEntry objects to remove
        
    Returns:
        True if successful, raises exception otherwise
    """
    # Ensure path is within allowed base directory
    full_path = os.path.normpath(os.path.join(settings.BASE_DIRECTORY, path.lstrip("/")))
    if not full_path.startswith(settings.BASE_DIRECTORY):
        raise ValueError(f"Path {path} is outside of base directory")
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Path {full_path} does not exist")
    
    # Build setfacl commands for each entry
    for entry in entries:
        cmd_parts = ["setfacl"]
        
        # Handle default ACLs
        if entry.default:
            cmd_parts.append("-d")
        
        # Remove the ACL
        acl_spec = f"{entry.type}:{entry.name}"
        cmd_parts.extend(["-x", acl_spec])
        cmd_parts.append(shlex.quote(full_path))
        
        # Run the command
        cmd = " ".join(cmd_parts)
        result = await run_command(cmd)
        
        if result.returncode != 0:
            logger.error(f"Error removing ACL for {full_path}: {result.stderr}")
            raise RuntimeError(f"Error removing ACL: {result.stderr}")
    
    return True