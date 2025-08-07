from datetime import datetime
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field, EmailStr


class User(Document):
    """User model for authentication"""
    
    email: EmailStr = Indexed(unique=True)
    hashed_password: str
    full_name: str
    role: str = Field(default="user", description="User role: user, admin, recruiter")
    is_active: bool = Field(default=True, description="Whether the user is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "role",
            "is_active"
        ]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "admin@example.com",
                "full_name": "Admin User",
                "role": "admin",
                "is_active": True
            }
        }
    }
    
    async def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        await self.save() 