from datetime import datetime
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field


class Job(Document):
    """Job posting model"""
    
    # Basic Information
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    type: str = Field(default="full-time", description="Job type: full-time, part-time, contract, internship")
    
    # Salary Information
    salary_min: Optional[int] = Field(None, description="Minimum salary")
    salary_max: Optional[int] = Field(None, description="Maximum salary")
    
    # Job Details
    description: str = Field(..., description="Job description")
    requirements: Optional[str] = Field(None, description="Job requirements")
    responsibilities: Optional[str] = Field(None, description="Job responsibilities")
    benefits: Optional[str] = Field(None, description="Job benefits")
    
    # Contact and Application
    contact_email: Optional[str] = Field(None, description="Contact email")
    application_deadline: Optional[datetime] = Field(None, description="Application deadline")
    
    # Metadata
    created_by: str = Field(..., description="User ID who created the job")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    is_active: bool = Field(default=True, description="Whether the job posting is active")
    
    # Status
    status: str = Field(default="draft", description="Job status: draft, published, closed")
    
    class Settings:
        name = "jobs"
        indexes = [
            "title",
            "company", 
            "location",
            "type",
            "created_by",
            "status",
            "is_active"
        ]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "New York, NY",
                "type": "full-time",
                "salary_min": 80000,
                "salary_max": 120000,
                "description": "We are looking for a senior software engineer...",
                "requirements": "5+ years of experience with Python, JavaScript...",
                "responsibilities": "Lead development of new features...",
                "benefits": "Health insurance, 401k, flexible PTO...",
                "contact_email": "hr@techcorp.com",
                "application_deadline": "2024-12-31T23:59:59Z",
                "status": "published"
            }
        }
    }
    
    async def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        await self.save() 