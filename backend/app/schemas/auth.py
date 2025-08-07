from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    """Registration request schema"""
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    """User response schema"""
    email: str
    full_name: str
    role: str

class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    token_type: str
    user: UserResponse 