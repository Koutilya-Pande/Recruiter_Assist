from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from beanie import PydanticObjectId

from app.models.application import Application
from app.models.job import Job
from app.models.candidate import Candidate
from app.schemas.application import (
    ApplicationCreate, 
    ApplicationUpdate, 
    ApplicationResponse, 
    ApplicationListResponse,
    ApplicationWithDetails
)
from app.api.endpoints.auth import get_current_user
from app.models.auth import User


router = APIRouter()


@router.post("/", response_model=ApplicationResponse, summary="Create a new application")
async def create_application(
    application_data: ApplicationCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new job application (link candidate to job).
    """
    try:
        # Verify job exists
        job = await Job.get(PydanticObjectId(application_data.job_id))
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Verify candidate exists
        candidate = await Candidate.get(PydanticObjectId(application_data.candidate_id))
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Check if application already exists
        existing_application = await Application.find_one(
            Application.job_id == application_data.job_id,
            Application.candidate_id == application_data.candidate_id
        )
        if existing_application:
            raise HTTPException(status_code=400, detail="Application already exists")
        
        # Create application object
        application = Application(
            **application_data.model_dump(),
            created_by=str(current_user.id)
        )
        
        # Save to database
        await application.insert()
        
        return ApplicationResponse(
            id=str(application.id),
            **application.model_dump(exclude={"id"})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create application: {str(e)}")


@router.get("/", response_model=ApplicationListResponse, summary="Get all applications")
async def get_applications(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    candidate_id: Optional[str] = Query(None, description="Filter by candidate ID"),
    status: Optional[str] = Query(None, description="Filter by application status")
):
    """
    Get all applications with optional filtering and pagination.
    """
    try:
        # Build query
        query = Application.find()
        
        # Add filters
        if job_id:
            query = query.find(Application.job_id == job_id)
        if candidate_id:
            query = query.find(Application.candidate_id == candidate_id)
        if status:
            query = query.find(Application.status == status)
        
        # Get total count
        total = await query.count()
        
        # Apply pagination
        applications = await query.skip((page - 1) * size).limit(size).to_list()
        
        # Convert to response format
        application_responses = [
            ApplicationResponse(
                id=str(app.id),
                **app.model_dump(exclude={"id"})
            ) for app in applications
        ]
        
        return ApplicationListResponse(
            applications=application_responses,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch applications: {str(e)}")


@router.get("/{application_id}", response_model=ApplicationWithDetails, summary="Get a specific application")
async def get_application(
    application_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific application with job and candidate details.
    """
    try:
        application = await Application.get(PydanticObjectId(application_id))
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Get job and candidate details
        job = await Job.get(PydanticObjectId(application.job_id))
        candidate = await Candidate.get(PydanticObjectId(application.candidate_id))
        
        if not job or not candidate:
            raise HTTPException(status_code=404, detail="Job or candidate not found")
        
        # Create response with details
        response_data = application.model_dump()
        response_data.update({
            "job_title": job.title,
            "job_company": job.company,
            "candidate_name": candidate.full_name,
            "candidate_email": candidate.email
        })
        
        return ApplicationWithDetails(**response_data)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch application: {str(e)}")


@router.put("/{application_id}", response_model=ApplicationResponse, summary="Update an application")
async def update_application(
    application_id: str,
    application_data: ApplicationUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update an application (e.g., change status, add notes, schedule interview).
    """
    try:
        application = await Application.get(PydanticObjectId(application_id))
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update fields
        update_data = application_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(application, field, value)
        
        # Update timestamp
        application.updated_at = datetime.utcnow()
        
        # Save changes
        await application.save()
        
        return ApplicationResponse(
            id=str(application.id),
            **application.model_dump(exclude={"id"})
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update application: {str(e)}")


@router.delete("/{application_id}", summary="Delete an application")
async def delete_application(
    application_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an application.
    """
    try:
        application = await Application.get(PydanticObjectId(application_id))
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        await application.delete()
        
        return {"message": "Application deleted successfully"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete application: {str(e)}")


@router.get("/job/{job_id}", response_model=ApplicationListResponse, summary="Get applications for a specific job")
async def get_job_applications(
    job_id: str,
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by application status")
):
    """
    Get all applications for a specific job.
    """
    try:
        # Verify job exists
        job = await Job.get(PydanticObjectId(job_id))
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Build query
        query = Application.find(Application.job_id == job_id)
        
        # Add status filter
        if status:
            query = query.find(Application.status == status)
        
        # Get total count
        total = await query.count()
        
        # Apply pagination
        applications = await query.skip((page - 1) * size).limit(size).to_list()
        
        # Convert to response format
        application_responses = [
            ApplicationResponse(
                id=str(app.id),
                **app.model_dump(exclude={"id"})
            ) for app in applications
        ]
        
        return ApplicationListResponse(
            applications=application_responses,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch job applications: {str(e)}") 