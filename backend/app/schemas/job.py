from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class JobBase(BaseModel):
    """Base job schema with common fields"""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    type: str = Field(default="full-time", description="Job type")
    salary_min: int = Field(..., description="Minimum salary")
    salary_max: int = Field(..., description="Maximum salary")
    description: str = Field(..., description="Job description")
    requirements: Optional[str] = Field(None, description="Job requirements")
    responsibilities: Optional[str] = Field(None, description="Job responsibilities")
    benefits: Optional[str] = Field(None, description="Job benefits")
    contact_email: Optional[str] = Field(None, description="Contact email")
    application_deadline: Optional[datetime] = Field(None, description="Application deadline")


class JobCreate(JobBase):
    """Schema for creating a new job"""
    pass


class JobUpdate(BaseModel):
    """Schema for updating a job"""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    contact_email: Optional[str] = None
    application_deadline: Optional[datetime] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class JobResponse(JobBase):
    """Schema for job response"""
    id: str = Field(..., description="Job ID")
    created_by: str = Field(..., description="User ID who created the job")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Whether the job posting is active")
    status: str = Field(..., description="Job status")
    
    # Override salary fields to be integers in response
    salary_min: int = Field(..., description="Minimum salary")
    salary_max: int = Field(..., description="Maximum salary")
    
    model_config = {
        "from_attributes": True
    }


class JobListResponse(BaseModel):
    """Schema for job list response"""
    jobs: List[JobResponse]
    total: int
    page: int
    size: int


class JobParseRequest(BaseModel):
    """Schema for AI job parsing request"""
    job_description: str = Field(..., description="Raw job description text to parse")


class JobParseResponse(JobBase):
    """Schema for AI job parsing response"""
    confidence_score: Optional[float] = Field(None, description="AI parsing confidence score")
    parsed_fields: List[str] = Field(..., description="List of fields that were successfully parsed")
    
    # Override salary fields to be integers in response
    salary_min: int = Field(..., description="Minimum salary")
    salary_max: int = Field(..., description="Maximum salary") 