from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
from typing import List, Optional
import asyncio

from api.routes import students, alerts, resources, analytics
from services.database_service import DatabaseService
from services.ml_service import MLService

app = FastAPI(
    title="Campus Intelligence System API",
    description="AI-powered system for student well-being monitoring and campus resource optimization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
db_service = DatabaseService()
ml_service = MLService()

# Include routers
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(resources.router, prefix="/api/resources", tags=["resources"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.on_event("startup")
async def startup_event():
    """Initialize database connections and ML models"""
    await db_service.initialize()
    await ml_service.load_models()
    print("Campus Intelligence System started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources"""
    await db_service.close()
    print("Campus Intelligence System shutdown complete")

@app.get("/")
async def root():
    return {"message": "Campus Intelligence System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "services": {"database": "connected", "ml_models": "loaded"}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
