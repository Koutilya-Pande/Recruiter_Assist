from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ApplicationBase(BaseModel):
    """Base application schema with common fields"""
    job_id: str = Field(..., description="Job ID that the candidate is applying for")
    candidate_id: str = Field(..., description="Candidate ID who is applying")
    status: str = Field(default="pending", description="Application status")
    notes: Optional[str] = Field(None, description="Recruiter's notes about this candidate")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Recruiter's rating (1-5)")
    interview_scheduled: Optional[datetime] = Field(None, description="Interview date/time")
    interview_notes: Optional[str] = Field(None, description="Interview notes")


class ApplicationCreate(ApplicationBase):
    """Schema for creating a new application"""
    pass


class ApplicationUpdate(BaseModel):
    """Schema for updating an application"""
    status: Optional[str] = None
    notes: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    interview_scheduled: Optional[datetime] = None
    interview_notes: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    """Schema for application response"""
    id: str = Field(..., description="Application ID")
    applied_at: datetime = Field(..., description="When the candidate applied")
    created_by: str = Field(..., description="User ID who created the application")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True
    }


class ApplicationListResponse(BaseModel):
    """Schema for application list response"""
    applications: list[ApplicationResponse]
    total: int
    page: int
    size: int


class ApplicationWithDetails(ApplicationResponse):
    """Schema for application with job and candidate details"""
    job_title: str = Field(..., description="Job title")
    job_company: str = Field(..., description="Job company")
    candidate_name: str = Field(..., description="Candidate name")
    candidate_email: Optional[str] = Field(None, description="Candidate email") 