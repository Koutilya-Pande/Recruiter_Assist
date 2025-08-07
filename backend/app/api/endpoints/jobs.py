import time
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from beanie import PydanticObjectId
import logging

from app.models.job import Job
from app.schemas.job import (
    JobCreate, 
    JobUpdate, 
    JobResponse, 
    JobListResponse,
    JobParseRequest,
    JobParseResponse
)
from app.api.endpoints.auth import get_current_user
from app.models.auth import User


router = APIRouter()


@router.post("/", response_model=JobResponse, summary="Create a new job posting")
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new job posting.
    
    - **title**: Job title (required)
    - **company**: Company name (required)
    - **description**: Job description (required)
    - **location**: Job location (optional)
    - **type**: Job type - full-time, part-time, contract, internship (default: full-time)
    - **salary_min**: Minimum salary (optional)
    - **salary_max**: Maximum salary (optional)
    - **requirements**: Job requirements (optional)
    - **responsibilities**: Job responsibilities (optional)
    - **benefits**: Job benefits (optional)
    - **contact_email**: Contact email (optional)
    - **application_deadline**: Application deadline (optional)
    """
    try:
        # Get the job data
        job_dict = job_data.model_dump()
        
        # Convert application_deadline to datetime if it's a string
        if job_dict.get('application_deadline') and isinstance(job_dict['application_deadline'], str) and job_dict['application_deadline'].strip():
            try:
                job_dict['application_deadline'] = datetime.fromisoformat(job_dict['application_deadline'].replace('Z', '+00:00'))
            except ValueError:
                # If parsing fails, set to None
                job_dict['application_deadline'] = None
        elif job_dict.get('application_deadline') == '' or job_dict.get('application_deadline') is None:
            job_dict['application_deadline'] = None
        
        # Handle empty strings for optional fields
        for field in ['location', 'requirements', 'responsibilities', 'benefits', 'contact_email']:
            if job_dict.get(field) == '':
                job_dict[field] = None
        
        # Create job object
        job = Job(
            **job_dict,
            created_by=str(current_user.id),
            status="draft"  # Start as draft
        )
        
        # Save to database
        await job.insert()
        
        return JobResponse(
            id=str(job.id),
            **job.model_dump(exclude={"id"})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")


def parse_bool_param(value: Optional[str]) -> Optional[bool]:
    """Parse boolean parameter, handling empty strings"""
    if value is None or value == "":
        return None
    if value.lower() in ("true", "1", "yes", "on"):
        return True
    if value.lower() in ("false", "0", "no", "off"):
        return False
    return None

@router.get("/", response_model=JobListResponse, summary="Get all jobs")
async def get_jobs(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by status"),
    is_active: Optional[str] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in title, company, or description")
):
    """
    Get all jobs with optional filtering and pagination.
    
    - **page**: Page number (default: 1)
    - **size**: Page size (default: 10, max: 100)
    - **status**: Filter by job status (draft, published, closed)
    - **is_active**: Filter by active status
    - **search**: Search term for title, company, or description
    """
    try:
        start_time = time.time()
        
        # Parse boolean parameter
        is_active_bool = parse_bool_param(is_active)
        
        # Build query
        query = Job.find()
        
        # Add filters
        if status and status.strip():
            query = query.find(Job.status == status)
        if is_active_bool is not None:
            query = query.find(Job.is_active == is_active_bool)
        if search and search.strip():
            # Search in title, company, and description
            query = query.find(
                (Job.title.contains(search, case_sensitive=False)) |
                (Job.company.contains(search, case_sensitive=False)) |
                (Job.description.contains(search, case_sensitive=False))
            )
        
        # Get total count
        count_start = time.time()
        total = await query.count()
        count_time = time.time() - count_start
        
        # Apply pagination
        data_start = time.time()
        jobs = await query.skip((page - 1) * size).limit(size).to_list()
        data_time = time.time() - data_start
        
        total_time = time.time() - start_time
        
        # Log performance metrics
        logging.info(f"Jobs query performance - Total: {total_time:.3f}s, Count: {count_time:.3f}s, Data: {data_time:.3f}s, Results: {len(jobs)}")
        
        # Convert to response format
        job_responses = [
            JobResponse(
                id=str(job.id),
                **job.model_dump(exclude={"id"})
            ) for job in jobs
        ]
        
        return JobListResponse(
            jobs=job_responses,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {str(e)}")


@router.get("/{job_id}", response_model=JobResponse, summary="Get a specific job")
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific job by ID.
    """
    try:
        job = await Job.get(PydanticObjectId(job_id))
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobResponse(
            id=str(job.id),
            **job.model_dump(exclude={"id"})
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch job: {str(e)}")


@router.put("/{job_id}", response_model=JobResponse, summary="Update a job")
async def update_job(
    job_id: str,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a job posting.
    """
    try:
        job = await Job.get(PydanticObjectId(job_id))
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Update fields
        update_data = job_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)
        
        # Update timestamp
        job.updated_at = datetime.utcnow()
        
        # Save changes
        await job.save()
        
        return JobResponse(
            id=str(job.id),
            **job.model_dump(exclude={"id"})
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update job: {str(e)}")


@router.delete("/{job_id}", summary="Delete a job")
async def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a job posting.
    """
    try:
        job = await Job.get(PydanticObjectId(job_id))
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        await job.delete()
        
        return {"message": "Job deleted successfully"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")


@router.post("/parse", response_model=JobParseResponse, summary="Parse job description with AI")
async def parse_job_description(
    parse_request: JobParseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Parse a job description using AI to extract structured data.
    
    This endpoint takes raw job description text and uses AI to extract:
    - Job title
    - Company name
    - Location
    - Job type
    - Salary range
    - Requirements
    - Responsibilities
    - Benefits
    - Contact information
    """
    try:
        # For now, we'll implement a basic parsing logic
        # TODO: Integrate with actual AI service (Mistral, OpenAI, etc.)
        
        # Simple parsing logic as placeholder
        job_description = parse_request.job_description.lower()
        
        # Extract basic information (this is a simplified example)
        parsed_data = {
            "title": "",
            "company": "",
            "location": "",
            "type": "full-time",
            "salary_min": None,
            "salary_max": None,
            "description": parse_request.job_description,
            "requirements": "",
            "responsibilities": "",
            "benefits": "",
            "contact_email": "",
            "application_deadline": None,
            "confidence_score": 0.7,
            "parsed_fields": []
        }
        
        # Simple keyword extraction (replace with actual AI parsing)
        if "senior" in job_description:
            parsed_data["title"] = "Senior Software Engineer"
            parsed_data["parsed_fields"].append("title")
        
        if "remote" in job_description:
            parsed_data["location"] = "Remote"
            parsed_data["parsed_fields"].append("location")
        
        if "full-time" in job_description:
            parsed_data["type"] = "full-time"
            parsed_data["parsed_fields"].append("type")
        elif "part-time" in job_description:
            parsed_data["type"] = "part-time"
            parsed_data["parsed_fields"].append("type")
        
        # Extract salary information (basic regex)
        import re
        salary_pattern = r'\$?(\d{1,3}(?:,\d{3})*(?:k|K)?)'
        salaries = re.findall(salary_pattern, job_description)
        if len(salaries) >= 2:
            try:
                min_salary = int(salaries[0].replace(',', '').replace('k', '000').replace('K', '000'))
                max_salary = int(salaries[1].replace(',', '').replace('k', '000').replace('K', '000'))
                parsed_data["salary_min"] = min_salary
                parsed_data["salary_max"] = max_salary
                parsed_data["parsed_fields"].extend(["salary_min", "salary_max"])
            except ValueError:
                pass
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, job_description)
        if emails:
            parsed_data["contact_email"] = emails[0]
            parsed_data["parsed_fields"].append("contact_email")
        
        return JobParseResponse(**parsed_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse job description: {str(e)}")


@router.patch("/{job_id}/status", summary="Update job status")
async def update_job_status(
    job_id: str,
    status: str = Query(..., description="New status: draft, published, closed"),
    current_user: User = Depends(get_current_user)
):
    """
    Update the status of a job posting.
    
    - **status**: New status (draft, published, closed)
    """
    try:
        if status not in ["draft", "published", "closed"]:
            raise HTTPException(status_code=400, detail="Invalid status. Must be draft, published, or closed")
        
        job = await Job.get(PydanticObjectId(job_id))
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job.status = status
        job.updated_at = datetime.utcnow()
        await job.save()
        
        return {"message": f"Job status updated to {status}"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update job status: {str(e)}") 