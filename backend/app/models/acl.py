from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime


class PermissionType(str, Enum):
    """Permission types for ACL entries"""
    READ = "r"
    WRITE = "w"
    EXECUTE = "x"


class EntityType(str, Enum):
    """Entity types for ACL entries"""
    USER = "user"
    GROUP = "group"
    MASK = "mask"
    OTHER = "other"


class AclPermission(BaseModel):
    """Model for ACL permissions"""
    read: bool = False
    write: bool = False
    execute: bool = False
    
    def to_string(self) -> str:
        """Convert permissions to string format (e.g., 'rwx')"""
        result = ""
        result += "r" if self.read else "-"
        result += "w" if self.write else "-"
        result += "x" if self.execute else "-"
        return result
    
    @classmethod
    def from_string(cls, perms_str: str) -> "AclPermission":
        """Create permissions from string format (e.g., 'rwx')"""
        if not perms_str or len(perms_str) != 3:
            return cls(read=False, write=False, execute=False)
        
        return cls(
            read=perms_str[0] == "r",
            write=perms_str[1] == "w",
            execute=perms_str[2] == "x"
        )


class AclEntryDetail(BaseModel):
    """Detailed model for an ACL entry"""
    type: EntityType
    name: str = ""  # Empty for OTHER or default entries
    permissions: AclPermission
    default: bool = False  # Whether this is a default ACL


class AclEntry(BaseModel):
    """Simplified model for an ACL entry (for API requests)"""
    type: str
    name: str = ""
    permissions: str
    default: bool = False
    
    @validator('type')
    def validate_type(cls, v: str) -> str:
        if v not in [e.value for e in EntityType]:
            raise ValueError(f"Invalid entity type: {v}")
        return v
    
    @validator('permissions')
    def validate_permissions(cls, v: str) -> str:
        if not v or len(v) != 3:
            raise ValueError("Permissions must be a 3-character string (e.g., 'rwx', 'r--')")
        
        for i, c in enumerate(v):
            expected = ["r", "-", "w", "-", "x", "-"][i * 2:i * 2 + 2]
            if c not in expected:
                raise ValueError(f"Invalid permission at position {i}: {c}")
        
        return v
    
    def to_detail(self) -> AclEntryDetail:
        """Convert to detailed ACL entry"""
        return AclEntryDetail(
            type=EntityType(self.type),
            name=self.name,
            permissions=AclPermission.from_string(self.permissions),
            default=self.default
        )


class PathAclDetail(BaseModel):
    """Detailed model for all ACL entries for a path"""
    path: str
    owner: str
    group: str
    entries: List[AclEntryDetail]
    default_entries: Optional[List[AclEntryDetail]] = None
    is_directory: bool = False


class AclChangeRequest(BaseModel):
    """Model for requesting ACL changes"""
    entries_to_add: List[AclEntry] = Field(default_factory=list)
    entries_to_remove: List[AclEntry] = Field(default_factory=list)
    recursive: bool = False  # Whether to apply changes recursively


class AclAuditLogEntry(BaseModel):
    """Model for ACL audit log entries"""
    timestamp: datetime
    user: str
    path: str
    action: str  # "add", "remove", "modify"
    entries_before: Optional[List[AclEntry]] = None
    entries_after: Optional[List[AclEntry]] = None
    success: bool
    error_message: Optional[str] = None