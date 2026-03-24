from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, Enum):
    DROPOUT_RISK = "dropout_risk"
    SUICIDE_RISK = "suicide_risk"
    ACADEMIC_DECLINE = "academic_decline"
    SOCIAL_ISOLATION = "social_isolation"
    RESOURCE_MISUSE = "resource_misuse"

class Student(BaseModel):
    id: str
    name: str
    email: str
    student_id: str
    department: str
    year: int
    gpa: Optional[float] = None
    enrollment_date: datetime
    hostel_room: Optional[str] = None
    contact_number: Optional[str] = None
    emergency_contact: Optional[str] = None

class AcademicRecord(BaseModel):
    student_id: str
    course_id: str
    semester: str
    grade: Optional[str] = None
    attendance_rate: float
    assignment_completion_rate: float
    last_updated: datetime

class BehavioralData(BaseModel):
    student_id: str
    timestamp: datetime
    activity_type: str
    duration_minutes: int
    location: Optional[str] = None
    social_interaction_count: int = 0
    mood_score: Optional[int] = Field(None, ge=1, le=10)

class RiskAssessment(BaseModel):
    student_id: str
    risk_level: RiskLevel
    risk_score: float = Field(ge=0, le=1)
    risk_factors: List[str]
    assessment_date: datetime
    next_review_date: datetime
    recommendations: List[str]

class Alert(BaseModel):
    id: str
    student_id: str
    alert_type: AlertType
    severity: RiskLevel
    message: str
    created_at: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None

class Resource(BaseModel):
    id: str
    name: str
    type: str
    location: str
    capacity: int
    current_utilization: int
    utilization_rate: float
    status: str
    maintenance_schedule: Optional[datetime] = None

class ResourceAllocation(BaseModel):
    student_id: str
    resource_id: str
    allocation_type: str
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str
    allocation_score: float

class Intervention(BaseModel):
    id: str
    student_id: str
    intervention_type: str
    description: str
    assigned_counselor: str
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str
    effectiveness_score: Optional[float] = None
