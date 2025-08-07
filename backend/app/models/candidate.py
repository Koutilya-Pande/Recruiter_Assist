from beanie import Document
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class Skill(BaseModel):
    """Individual skill with proficiency level"""
    name: str = Field(description="Skill name (e.g., Python, React)")
    proficiency: Optional[str] = Field(default=None, description="Proficiency level (Beginner, Intermediate, Advanced, Expert)")
    years_experience: Optional[float] = Field(default=None, description="Years of experience with this skill")

class Experience(BaseModel):
    """Work experience entry"""
    company: str = Field(description="Company name")
    position: str = Field(description="Job title")
    start_date: str = Field(description="Start date (YYYY-MM or YYYY)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM or YYYY) or 'Present'")
    description: Optional[str] = Field(default=None, description="Job description")
    achievements: Optional[List[str]] = Field(default=None, description="Key achievements")

class Education(BaseModel):
    """Education entry"""
    institution: str = Field(description="School/University name")
    degree: str = Field(description="Degree type (e.g., Bachelor's, Master's)")
    field_of_study: str = Field(description="Field of study (e.g., Computer Science)")
    start_date: Optional[str] = Field(default=None, description="Start date")
    end_date: Optional[str] = Field(default=None, description="End date or graduation year")
    gpa: Optional[float] = Field(default=None, description="GPA if available")

class ResumeExtraction(BaseModel):
    """Structured resume data extracted from PDF"""
    full_name: str = Field(description="Candidate's full name")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    location: Optional[str] = Field(default=None, description="Location/City")
    summary: Optional[str] = Field(default=None, description="Professional summary")
    skills: List[Skill] = Field(default=[], description="List of skills")
    experience: List[Experience] = Field(default=[], description="Work experience")
    education: List[Education] = Field(default=[], description="Education history")
    certifications: Optional[List[str]] = Field(default=None, description="Certifications")
    languages: Optional[List[str]] = Field(default=None, description="Languages known")

class Candidate(Document):
    """Candidate document in MongoDB"""
    filename: str = Field(description="Original PDF filename")
    full_name: str = Field(description="Candidate's full name")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    location: Optional[str] = Field(default=None, description="Location/City")
    summary: Optional[str] = Field(default=None, description="Professional summary")
    skills: List[Skill] = Field(default=[], description="List of skills")
    experience: List[Experience] = Field(default=[], description="Work experience")
    education: List[Education] = Field(default=[], description="Education history")
    certifications: Optional[List[str]] = Field(default=None, description="Certifications")
    languages: Optional[List[str]] = Field(default=None, description="Languages known")
    resume_url: Optional[str] = Field(default=None, description="Path to stored PDF file")
    job_id: Optional[str] = Field(None, description="Job ID if uploaded to specific job")
    uploaded_by: str = Field(description="User ID who uploaded the resume")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "candidates"
        indexes = [
            "filename",
            "email",
            "full_name",
            "job_id",
            "uploaded_by",
            "created_at"
        ]

class BatchExtractionResult(BaseModel):
    """Result of batch resume processing"""
    total_files: int
    succeeded: int
    failed: int
    failed_files: List[str]
    results: List[ResumeExtraction] 