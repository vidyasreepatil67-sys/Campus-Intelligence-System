from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

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

# Sample data
students = [
    {
        "id": "1",
        "name": "John Doe",
        "email": "john.doe@university.edu",
        "student_id": "STU001",
        "department": "Computer Science",
        "year": 3,
        "gpa": 3.2,
        "risk_level": "MEDIUM",
        "last_assessment": "2024-03-20"
    },
    {
        "id": "2",
        "name": "Jane Smith",
        "email": "jane.smith@university.edu",
        "student_id": "STU002",
        "department": "Engineering",
        "year": 2,
        "gpa": 2.8,
        "risk_level": "HIGH",
        "last_assessment": "2024-03-22"
    }
]

alerts = [
    {
        "id": "1",
        "student_name": "John Doe",
        "type": "ACADEMIC_DECLINE",
        "severity": "HIGH",
        "message": "Significant drop in attendance over past 2 weeks",
        "created_at": "2024-03-23T10:30:00Z",
        "resolved": False
    },
    {
        "id": "2",
        "student_name": "Jane Smith",
        "type": "SUICIDE_RISK",
        "severity": "CRITICAL",
        "message": "High-risk indicators detected from behavioral patterns",
        "created_at": "2024-03-23T09:15:00Z",
        "resolved": False
    }
]

resources = [
    {
        "id": "1",
        "name": "Hostel Block A - Room 101",
        "type": "hostel_room",
        "location": "Main Campus",
        "capacity": 2,
        "current_utilization": 2,
        "utilization_rate": 100,
        "status": "active"
    },
    {
        "id": "2",
        "name": "Library - Study Area 1",
        "type": "study_area",
        "location": "Academic Building",
        "capacity": 50,
        "current_utilization": 35,
        "utilization_rate": 70,
        "status": "active"
    }
]

@app.get("/")
async def root():
    return {"message": "Campus Intelligence System API", "version": "1.0.0"}

@app.get("/api/students")
async def get_students():
    return students

@app.get("/api/alerts")
async def get_alerts():
    return alerts

@app.get("/api/resources")
async def get_resources():
    return resources

@app.get("/api/analytics/dashboard/overview")
async def get_dashboard_overview():
    return {
        "students": {
            "total": 1250,
            "at_risk": 87,
            "risk_percentage": 6.96
        },
        "alerts": {
            "total": 234,
            "critical_unresolved": 12
        },
        "resources": {
            "average_utilization": 78.5
        },
        "assessments": {
            "recent_weekly": 45
        },
        "interventions": {
            "active": 156
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": {"api": "running"}}

if __name__ == "__main__":
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8000, reload=True)
