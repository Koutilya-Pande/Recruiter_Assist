from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import os
import shutil
from datetime import datetime
import logging

from app.config import settings
from app.models.candidate import Candidate, ResumeExtraction, BatchExtractionResult
from app.services.resume_extractor import ResumeExtractor
from app.api.endpoints.auth import verify_token

# Set up logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# JWT token security
security = HTTPBearer()

# Initialize resume extractor
resume_extractor = ResumeExtractor()

@router.post("/debug-extract")
async def debug_resume_extraction(
    file: UploadFile = File(...),
    payload: dict = Depends(verify_token)
):
    """
    Debug endpoint to test resume extraction and see what PyPDF2 extracts
    """
    try:
        logger.info(f"Debug extraction for file: {file.filename}")
        
        # Save file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Extract text from PDF
            extracted_text, num_pages = resume_extractor.extract_text_from_pdf(temp_file_path)
            
            # Try LLM extraction
            try:
                resume_data = resume_extractor.extract_resume_data(extracted_text, num_pages)
                llm_success = True
            except Exception as e:
                logger.error(f"LLM extraction failed: {e}")
                resume_data = None
                llm_success = False
            
            return {
                "filename": file.filename,
                "file_size": len(content),
                "num_pages": num_pages,
                "extracted_text_length": len(extracted_text),
                "extracted_text_preview": extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text,
                "llm_extraction_success": llm_success,
                "llm_results": resume_data.dict() if resume_data else None,
                "debug_info": {
                    "first_10_lines": extracted_text.split('\n')[:10],
                    "last_10_lines": extracted_text.split('\n')[-10:],
                    "total_lines": len(extracted_text.split('\n'))
                }
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Debug extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Debug extraction failed: {str(e)}")

@router.post("/upload", response_model=BatchExtractionResult)
async def upload_resumes(
    files: List[UploadFile] = File(...),
    job_id: str = None,  # Optional job ID for job-specific uploads
    payload: dict = Depends(verify_token)
):
    """
    Upload one or more resume PDFs and extract structured data from each.
    Returns a summary with counters and results.
    """
    uploaded_by = payload.get("sub")  # User email from JWT
    results = []
    failed_files = []
    
    logger.info(f"Starting batch upload of {len(files)} files")
    
    for file in files:
        try:
            logger.info(f"Processing file: {file.filename}")
            
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                logger.warning(f"File {file.filename} is not a PDF")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} is not a PDF"
                )
            
            # Normalize filename
            normalized_filename = file.filename.strip().lower()
            
            # Check if file already processed
            existing_candidate = await Candidate.find_one({"filename": normalized_filename})
            if existing_candidate:
                logger.info(f"File already processed: {file.filename}")
                results.append(ResumeExtraction(
                    full_name=existing_candidate.full_name,
                    email=existing_candidate.email,
                    phone=existing_candidate.phone,
                    location=existing_candidate.location,
                    summary=existing_candidate.summary,
                    skills=existing_candidate.skills,
                    experience=existing_candidate.experience,
                    education=existing_candidate.education
                ))
                continue
            
            logger.info(f"Extracting data from: {file.filename}")
            
            # Extract resume data
            resume_data = await resume_extractor.process_resume(file, uploaded_by)
            
            logger.info(f"Extraction completed for {file.filename}:")
            logger.info(f"  - Name: {resume_data.full_name}")
            logger.info(f"  - Email: {resume_data.email}")
            logger.info(f"  - Skills: {len(resume_data.skills)}")
            logger.info(f"  - Experience: {len(resume_data.experience)}")
            logger.info(f"  - Education: {len(resume_data.education)}")
            
            # Save PDF file
            file_path = os.path.join(resume_extractor.upload_dir, normalized_filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create candidate document
            candidate = Candidate(
                filename=file.filename,
                full_name=resume_data.full_name,
                email=resume_data.email,
                phone=resume_data.phone,
                location=resume_data.location,
                summary=resume_data.summary,
                skills=resume_data.skills,
                experience=resume_data.experience,
                education=resume_data.education,
                certifications=resume_data.certifications,
                languages=resume_data.languages,
                resume_url=file_path,
                job_id=job_id,  # Job-specific upload
                uploaded_by=uploaded_by
            )
            
            # Save to database
            await candidate.insert()
            logger.info(f"Saved candidate to database: {candidate.id}")
            
            results.append(resume_data)
            logger.info(f"Successfully processed: {file.filename}")
            
        except Exception as e:
            logger.error(f"Failed to process {file.filename}: {e}")
            failed_files.append(file.filename)
    
    logger.info(f"Batch upload completed:")
    logger.info(f"  - Total files: {len(files)}")
    logger.info(f"  - Succeeded: {len(results)}")
    logger.info(f"  - Failed: {len(failed_files)}")
    if failed_files:
        logger.error(f"Failed files: {failed_files}")
    
    return BatchExtractionResult(
        total_files=len(files),
        succeeded=len(results),
        failed=len(failed_files),
        failed_files=failed_files,
        results=results
    )

@router.get("/all")
async def get_all_candidates(
    job_id: str = None,  # Optional filter by job
    payload: dict = Depends(verify_token)
):
    """Get all candidates with summary information"""
    try:
        # Build query
        query = Candidate.find()
        
        # Filter by job if specified
        if job_id:
            query = query.find(Candidate.job_id == job_id)
        
        candidates = await query.to_list()
        summary_list = []
        
        for candidate in candidates:
            summary = {
                "id": str(candidate.id),
                "filename": candidate.filename,
                "full_name": candidate.full_name,
                "email": candidate.email,
                "phone": candidate.phone,
                "location": candidate.location,
                "skills_count": len(candidate.skills),
                "experience_count": len(candidate.experience),
                "education_count": len(candidate.education),
                "uploaded_by": candidate.uploaded_by,
                "created_at": candidate.created_at.isoformat()
            }
            summary_list.append(summary)
        
        logger.info(f"Returning {len(summary_list)} candidate summaries")
        return summary_list
        
    except Exception as e:
        logger.error(f"Failed to fetch candidates: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch candidates")

@router.get("/{candidate_id}")
async def get_candidate(candidate_id: str, payload: dict = Depends(verify_token)):
    """Get detailed information for a specific candidate"""
    try:
        candidate = await Candidate.get(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        return {
            "id": str(candidate.id),
            "filename": candidate.filename,
            "full_name": candidate.full_name,
            "email": candidate.email,
            "phone": candidate.phone,
            "location": candidate.location,
            "summary": candidate.summary,
            "skills": candidate.skills,
            "experience": candidate.experience,
            "education": candidate.education,
            "certifications": candidate.certifications,
            "languages": candidate.languages,
            "resume_url": candidate.resume_url,
            "uploaded_by": candidate.uploaded_by,
            "created_at": candidate.created_at.isoformat(),
            "updated_at": candidate.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch candidate {candidate_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch candidate")

@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: str, payload: dict = Depends(verify_token)):
    """Delete a candidate and their resume file"""
    try:
        candidate = await Candidate.get(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Delete resume file if it exists
        if candidate.resume_url and os.path.exists(candidate.resume_url):
            os.remove(candidate.resume_url)
        
        # Delete from database
        await candidate.delete()
        
        return {"message": "Candidate deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete candidate {candidate_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete candidate")

@router.get("/search/{query}")
async def search_candidates(query: str, payload: dict = Depends(verify_token)):
    """Search candidates by name, skills, or other criteria"""
    try:
        # Simple search implementation
        # You can enhance this with more sophisticated search
        candidates = await Candidate.find({
            "$or": [
                {"full_name": {"$regex": query, "$options": "i"}},
                {"skills.name": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}}
            ]
        }).to_list()
        
        results = []
        for candidate in candidates:
            results.append({
                "id": str(candidate.id),
                "full_name": candidate.full_name,
                "email": candidate.email,
                "skills": [skill.name for skill in candidate.skills],
                "created_at": candidate.created_at.isoformat()
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to search candidates: {e}")
        raise HTTPException(status_code=500, detail="Failed to search candidates") 