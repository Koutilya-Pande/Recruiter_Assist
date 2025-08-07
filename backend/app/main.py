from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Recruiter Assist API...")
    await init_db()
    print("✅ Database connected!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Recruiter Assist API...")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered recruiting platform with resume parsing and job-candidate matching",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api.endpoints import auth, candidates, jobs, applications
app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["authentication"])
app.include_router(candidates.router, prefix=settings.API_V1_STR + "/candidates", tags=["candidates"])
app.include_router(jobs.router, prefix=settings.API_V1_STR + "/jobs", tags=["jobs"])
app.include_router(applications.router, prefix=settings.API_V1_STR + "/applications", tags=["applications"])

# We'll add these later
# from app.api.endpoints import jobs, upload, matching
# app.include_router(jobs.router, prefix=settings.API_V1_STR)
# app.include_router(upload.router, prefix=settings.API_V1_STR)
# app.include_router(matching.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Recruiter Assist API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "recruiter-assist-api"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    ) 