from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    roles: List[str] = []

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse 