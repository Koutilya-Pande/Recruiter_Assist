from datetime import datetime
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field


class Application(Document):
    """Job application model - links candidates to jobs"""
    
    # Relationships
    job_id: str = Field(..., description="Job ID that the candidate is applying for")
    candidate_id: str = Field(..., description="Candidate ID who is applying")
    
    # Application Details
    status: str = Field(default="pending", description="Application status: pending, reviewed, shortlisted, rejected, hired")
    applied_at: datetime = Field(default_factory=datetime.utcnow, description="When the candidate applied")
    
    # Recruiter Notes
    notes: Optional[str] = Field(None, description="Recruiter's notes about this candidate")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Recruiter's rating (1-5)")
    
    # Interview Details
    interview_scheduled: Optional[datetime] = Field(None, description="Interview date/time")
    interview_notes: Optional[str] = Field(None, description="Interview notes")
    
    # Metadata
    created_by: str = Field(..., description="User ID who created the application")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Settings:
        name = "applications"
        indexes = [
            "job_id",
            "candidate_id", 
            "status",
            "applied_at",
            "created_by"
        ]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "job_id": "507f1f77bcf86cd799439011",
                "candidate_id": "507f1f77bcf86cd799439012",
                "status": "pending",
                "notes": "Strong technical background, good fit for the role",
                "rating": 4,
                "interview_scheduled": "2024-01-15T10:00:00Z"
            }
        }
    }
    
    async def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        await self.save() 