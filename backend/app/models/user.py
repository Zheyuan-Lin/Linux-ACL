from typing import Optional, List
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user model"""
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Create user model - would include password for local auth"""
    pass


class User(UserBase):
    """User model with LDAP attributes"""
    id: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    groups: List[str] = []

    @property
    def institution(self) -> str:
        """Get user's institution from username"""
        return self.username.split('@')[1] if '@' in self.username else ''
    
    @property
    def user_id(self) -> str:
        """Get user's ID from username"""
        return self.username.split('@')[0] if '@' in self.username else self.username

    class Config:
        orm_mode = True