import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.skills import router as skills_router
from app.api.resume import router as resume_router
from app.api.jobs import router as jobs_router
from app.api.history import router as history_router
from app.api.analysis import router as analysis_router
from app.api.dashboard import router as dashboard_router


# Create the FastAPI application
app = FastAPI(title="AI Resume Analyzer", description="An AI-powered resume analysis and job matching platform",
    version="1.0.0",)


# Allowed frontend origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
]

# Add deployed frontend URL from environment variables
FRONTEND_URL = os.getenv("FRONTEND_URL")

if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL.rstrip("/"))

# Configure CORS
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS",],
    allow_headers=["Content-Type", "Accept",],
)

# Add basic security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = ("camera=(), microphone=(), geolocation=()")

    return response

# Register API routers
app.include_router(resume_router)
app.include_router(skills_router)
app.include_router(dashboard_router)
app.include_router(jobs_router)
app.include_router(analysis_router)
app.include_router(history_router)

# Home endpoint
@app.get("/")
def home():
    return {"message": "Welcome to AI Resume Analyzer!", "status": "Backend is running successfully",}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy",}