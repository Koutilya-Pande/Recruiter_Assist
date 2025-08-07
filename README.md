# Recruiter Assist

AI-powered recruiting platform with resume parsing and job-candidate matching.

## Tech Stack

**Backend:**
- FastAPI (Python 3.9+)
- MongoDB Atlas
- JWT Authentication
- Pydantic for data validation
- Background tasks with Celery/Redis

**Frontend:**
- React 18
- TypeScript
- Tailwind CSS
- React Query for state management
- React Router for navigation

**AI/ML:**
- spaCy for NLP
- PyPDF2/pdfplumber for PDF processing
- Sentence transformers for semantic matching

## Project Structure

```
recruiter-assist/
├── backend/                    # FastAPI backend
├── frontend/                   # React frontend
├── shared/                     # Shared types/schemas
├── docs/                      # Documentation
├── scripts/                   # Deployment/setup scripts
└── docker-compose.yml         # Local development
```

## Quick Start

1. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Environment Variables:**
   - Copy `.env.example` to `.env` in both directories
   - Configure MongoDB Atlas connection
   - Set JWT secret keys

## Features

- 🔐 Role-based authentication (Admin, Recruiter, Hiring Manager)
- 💼 Job creation and management
- 📄 PDF resume upload and parsing
- 🤖 AI-powered candidate-job matching
- 👥 Candidate management
- 📊 Analytics dashboard
- 🔍 Advanced search and filtering

## API Documentation

Once running, visit: `http://localhost:8000/docs`