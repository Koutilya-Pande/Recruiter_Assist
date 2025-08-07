import os
import PyPDF2
import tempfile
import json
import logging
from typing import List, Tuple, Optional
from fastapi import UploadFile
from app.models.candidate import ResumeExtraction, Skill, Experience, Education
from app.config import settings
from mistralai import Mistral
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeExtractor:
    """Service for extracting structured data from resume PDFs using LLM"""
    
    def __init__(self, MISTRAL_API_KEY: Optional[str] = None):
        self.upload_dir = "uploads/resumes"
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Initialize Mistral client
        if MISTRAL_API_KEY:
            logger.info(f"Using provided Mistral API key: {MISTRAL_API_KEY[:10]}...")
            self.client = Mistral(api_key=MISTRAL_API_KEY)
        elif settings.MISTRAL_API_KEY:
            logger.info(f"Using settings Mistral API key: {settings.MISTRAL_API_KEY[:10]}...")
            self.client = Mistral(api_key=settings.MISTRAL_API_KEY)
        else:
            # Try to get from environment variable
            api_key = os.getenv("MISTRAL_API_KEY")
            if api_key:
                logger.info(f"Using environment Mistral API key: {api_key[:10]}...")
                self.client = Mistral(api_key=api_key)
            else:
                logger.error("No Mistral API key found!")
                self.client = None
        
        # Test the client
        if self.client:
            try:
                logger.info("Testing Mistral client...")
                # Try a simple test call
                test_response = self.client.chat.complete(
                    model="mistral-small-latest",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                logger.info("Mistral client test successful!")
            except Exception as e:
                logger.error(f"Mistral client test failed: {e}")
                self.client = None
        
        logger.info(f"Mistral client initialized: {self.client is not None}")
    
    def extract_text_from_pdf(self, file_path: str) -> Tuple[str, int]:
        """Extract text from PDF using PyPDF2"""
        try:
            logger.info(f"Extracting text from PDF: {file_path}")
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                logger.info(f"PDF has {num_pages} pages")
                
                extracted_text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    extracted_text += page_text + "\n"
                    logger.info(f"Page {page_num + 1}: {len(page_text)} characters")
                
                final_text = extracted_text.strip()
                logger.info(f"Total extracted text length: {len(final_text)} characters")
                logger.info(f"First 500 characters: {final_text[:500]}")
                logger.info(f"Last 500 characters: {final_text[-500:]}")
                
                return final_text, num_pages
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_resume_data(self, extracted_text: str, num_pages: int) -> ResumeExtraction:
        """Extract structured resume data from text using LLM parsing"""
        logger.info(f"Starting LLM extraction for {num_pages} page(s)")
        logger.info(f"Input text length: {len(extracted_text)} characters")
        
        if self.client is None:
            logger.warning("Mistral client not available, falling back to basic parsing")
            return self._fallback_extraction(extracted_text, num_pages)
        
        logger.info("Mistral client is available, attempting LLM extraction...")
        
        prompt = f"""
        Extract the following information from the resume text below and return it as a valid JSON object:
        {{
            "full_name": "candidate's full name",
            "email": "email address if available",
            "phone": "phone number if available", 
            "location": "location/city if available",
            "summary": "professional summary if available",
            "skills": [
                {{
                    "name": "skill name",
                    "proficiency": "proficiency level if mentioned",
                    "years_experience": "years of experience if mentioned"
                }}
            ],
            "experience": [
                {{
                    "company": "company name",
                    "position": "job title",
                    "start_date": "start date",
                    "end_date": "end date or 'Present'",
                    "description": "job description",
                    "achievements": ["achievement1", "achievement2"]
                }}
            ],
            "education": [
                {{
                    "institution": "school/university name",
                    "degree": "degree type",
                    "field_of_study": "field of study",
                    "start_date": "start date if available",
                    "end_date": "end date if available",
                    "gpa": "gpa if available"
                }}
            ],
            "certifications": ["certification1", "certification2"],
            "languages": ["language1", "language2"]
        }}

        Resume Text:
        {extracted_text}
        """

        try:
            logger.info("Sending request to Mistral API...")
            logger.info(f"Prompt length: {len(prompt)} characters")
            
            # First try with structured output
            try:
                logger.info("Attempting structured output...")
                response = self.client.chat.parse(
                    model="mistral-small-latest",
                    messages=[
                        {"role": "system", "content": "You are a resume parsing model. Extract structured information from resumes and return it as valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format=ResumeExtraction,
                    temperature=0
                )
                
                logger.info("Received structured response from Mistral API")
                
                # Handle the response - it might be a string or a structured object
                content = response.choices[0].message.content
                
                if isinstance(content, str):
                    # If it's a string, try to parse it as JSON
                    logger.info("Response is a string, attempting JSON parsing")
                    try:
                        import json
                        parsed_data = json.loads(content)
                        # Convert the parsed data to ResumeExtraction model
                        resume_data = ResumeExtraction(**parsed_data)
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.error(f"Failed to parse JSON response: {e}")
                        logger.error(f"Raw response content: {content[:500]}...")
                        raise Exception(f"Invalid JSON response from LLM: {e}")
                else:
                    # If it's already a structured object
                    logger.info("Response is already a structured object")
                    resume_data = content
                    
            except Exception as structured_error:
                logger.warning(f"Structured output failed: {structured_error}")
                logger.info("Trying regular chat completion...")
                
                # Fallback to regular chat completion
                response = self.client.chat.complete(
                    model="mistral-small-latest",
                    messages=[
                        {"role": "system", "content": "You are a resume parsing model. Extract structured information from resumes and return it as valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )
                
                logger.info("Received regular response from Mistral API")
                
                # Parse the JSON response
                content = response.choices[0].message.content
                logger.info(f"Raw response: {content[:200]}...")
                
                try:
                    import json
                    parsed_data = json.loads(content)
                    # Convert the parsed data to ResumeExtraction model
                    resume_data = ResumeExtraction(**parsed_data)
                except (json.JSONDecodeError, TypeError) as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.error(f"Raw response content: {content[:500]}...")
                    raise Exception(f"Invalid JSON response from LLM: {e}")
            
            logger.info(f"LLM extraction successful:")
            logger.info(f"  - Name: {resume_data.full_name}")
            logger.info(f"  - Email: {resume_data.email}")
            logger.info(f"  - Phone: {resume_data.phone}")
            logger.info(f"  - Skills count: {len(resume_data.skills)}")
            logger.info(f"  - Experience count: {len(resume_data.experience)}")
            logger.info(f"  - Education count: {len(resume_data.education)}")
            
            return resume_data
            
        except Exception as e:
            logger.error(f"LLM parsing failed: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Falling back to basic parsing")
            return self._fallback_extraction(extracted_text, num_pages)
    
    def _fallback_extraction(self, extracted_text: str, num_pages: int) -> ResumeExtraction:
        """Fallback to basic parsing if LLM fails"""
        logger.info("Using fallback extraction method")
        lines = extracted_text.split('\n')
        logger.info(f"Processing {len(lines)} lines of text")
        
        # Basic extraction logic (original implementation)
        full_name = self._extract_name(lines)
        email = self._extract_email(lines)
        phone = self._extract_phone(lines)
        location = self._extract_location(lines)
        summary = self._extract_summary(lines)
        skills = self._extract_skills(lines)
        experience = self._extract_experience(lines)
        education = self._extract_education(lines)
        
        logger.info(f"Fallback extraction results:")
        logger.info(f"  - Name: {full_name}")
        logger.info(f"  - Email: {email}")
        logger.info(f"  - Phone: {phone}")
        logger.info(f"  - Skills count: {len(skills)}")
        logger.info(f"  - Experience count: {len(experience)}")
        logger.info(f"  - Education count: {len(education)}")
        
        return ResumeExtraction(
            full_name=full_name or "Unknown",
            email=email,
            phone=phone,
            location=location,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education
        )
    
    def _extract_name(self, lines: List[str]) -> str:
        """Extract candidate name from first few lines"""
        logger.info("Extracting name from first 5 lines")
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            logger.info(f"  Line {i+1}: '{line}'")
            if line and len(line.split()) <= 4:  # Likely a name
                logger.info(f"  Found name: '{line}'")
                return line
        logger.warning("No name found in first 5 lines")
        return "Unknown"
    
    def _extract_email(self, lines: List[str]) -> str:
        """Extract email address"""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for line in lines:
            emails = re.findall(email_pattern, line)
            if emails:
                logger.info(f"Found email: {emails[0]}")
                return emails[0]
        logger.warning("No email found")
        return None
    
    def _extract_phone(self, lines: List[str]) -> str:
        """Extract phone number"""
        import re
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        for line in lines:
            phones = re.findall(phone_pattern, line)
            if phones:
                logger.info(f"Found phone: {phones[0]}")
                return phones[0]
        logger.warning("No phone found")
        return None
    
    def _extract_location(self, lines: List[str]) -> str:
        """Extract location/city"""
        location_keywords = ['location', 'city', 'address', 'based in']
        for line in lines:
            line_lower = line.lower()
            for keyword in location_keywords:
                if keyword in line_lower:
                    logger.info(f"Found location: '{line.strip()}'")
                    return line.strip()
        logger.warning("No location found")
        return None
    
    def _extract_summary(self, lines: List[str]) -> str:
        """Extract professional summary"""
        summary_keywords = ['summary', 'objective', 'profile', 'about']
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for keyword in summary_keywords:
                if keyword in line_lower:
                    logger.info(f"Found summary section at line {i+1}")
                    # Get next few lines as summary
                    summary_lines = []
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].strip():
                            summary_lines.append(lines[j].strip())
                    summary = ' '.join(summary_lines)
                    logger.info(f"Summary: {summary[:100]}...")
                    return summary
        logger.warning("No summary found")
        return None
    
    def _extract_skills(self, lines: List[str]) -> List[Skill]:
        """Extract skills from resume"""
        skills = []
        skill_keywords = ['skills', 'technologies', 'programming', 'languages', 'tools']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for keyword in skill_keywords:
                if keyword in line_lower:
                    logger.info(f"Found skills section at line {i+1}")
                    # Extract skills from next few lines
                    for j in range(i+1, min(i+10, len(lines))):
                        skill_line = lines[j].strip()
                        if skill_line and not any(kw in skill_line.lower() for kw in ['experience', 'education', 'work']):
                            # Split by common separators
                            skill_items = skill_line.replace(',', ' ').replace(';', ' ').split()
                            for skill in skill_items:
                                if len(skill) > 2:  # Filter out very short items
                                    skills.append(Skill(name=skill))
                                    logger.info(f"  Found skill: {skill}")
        logger.info(f"Total skills found: {len(skills)}")
        return skills
    
    def _extract_experience(self, lines: List[str]) -> List[Experience]:
        """Extract work experience"""
        experience = []
        exp_keywords = ['experience', 'work history', 'employment']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for keyword in exp_keywords:
                if keyword in line_lower:
                    logger.info(f"Found experience section at line {i+1}")
                    # Simple extraction - you might want to enhance this
                    for j in range(i+1, min(i+20, len(lines))):
                        exp_line = lines[j].strip()
                        if exp_line and len(exp_line) > 10:
                            # Basic parsing - you can enhance this
                            exp = Experience(
                                company="Company Name",
                                position="Position",
                                start_date="2020",
                                end_date="Present",
                                description=exp_line
                            )
                            experience.append(exp)
                            logger.info(f"  Found experience: {exp_line[:50]}...")
        logger.info(f"Total experience entries found: {len(experience)}")
        return experience
    
    def _extract_education(self, lines: List[str]) -> List[Education]:
        """Extract education information"""
        education = []
        edu_keywords = ['education', 'academic', 'degree', 'university']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for keyword in edu_keywords:
                if keyword in line_lower:
                    logger.info(f"Found education section at line {i+1}")
                    # Simple extraction - you might want to enhance this
                    for j in range(i+1, min(i+10, len(lines))):
                        edu_line = lines[j].strip()
                        if edu_line and len(edu_line) > 10:
                            edu = Education(
                                institution="Institution",
                                degree="Degree",
                                field_of_study="Field of Study"
                            )
                            education.append(edu)
                            logger.info(f"  Found education: {edu_line[:50]}...")
        logger.info(f"Total education entries found: {len(education)}")
        return education
    
    async def process_resume(self, file: UploadFile, uploaded_by: str) -> ResumeExtraction:
        """Process a single resume file"""
        logger.info(f"Processing resume: {file.filename}")
        logger.info(f"File size: {file.size} bytes")
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
            logger.info(f"Saved temporary file: {temp_file_path}")
        
        try:
            # Extract text from PDF
            extracted_text, num_pages = self.extract_text_from_pdf(temp_file_path)
            
            # Extract structured data using LLM
            resume_data = self.extract_resume_data(extracted_text, num_pages)
            
            logger.info(f"Resume processing completed for: {file.filename}")
            return resume_data
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}") 