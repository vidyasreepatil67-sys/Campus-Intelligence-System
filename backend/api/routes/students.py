from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from models.database import get_db, Student, AcademicRecord, BehavioralData, RiskAssessment, Intervention
from models.schemas import Student as StudentSchema, AcademicRecord as AcademicRecordSchema, RiskAssessment as RiskAssessmentSchema
from services.student_service import StudentService
from services.ml_service import MLService

router = APIRouter()
student_service = StudentService()
ml_service = MLService()

@router.get("/", response_model=List[StudentSchema])
async def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all students with optional filtering"""
    return student_service.get_students(db, skip=skip, limit=limit, department=department, year=year)

@router.get("/{student_id}", response_model=StudentSchema)
async def get_student(student_id: str, db: Session = Depends(get_db)):
    """Get a specific student by ID"""
    student = student_service.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.post("/", response_model=StudentSchema)
async def create_student(student: StudentSchema, db: Session = Depends(get_db)):
    """Create a new student"""
    return student_service.create_student(db, student)

@router.put("/{student_id}", response_model=StudentSchema)
async def update_student(student_id: str, student: StudentSchema, db: Session = Depends(get_db)):
    """Update student information"""
    updated_student = student_service.update_student(db, student_id, student)
    if not updated_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated_student

@router.get("/{student_id}/academic-records", response_model=List[AcademicRecordSchema])
async def get_academic_records(student_id: str, db: Session = Depends(get_db)):
    """Get academic records for a specific student"""
    records = student_service.get_academic_records(db, student_id)
    if not records:
        raise HTTPException(status_code=404, detail="Student not found or no academic records")
    return records

@router.post("/{student_id}/academic-records", response_model=AcademicRecordSchema)
async def add_academic_record(
    student_id: str, 
    record: AcademicRecordSchema, 
    db: Session = Depends(get_db)
):
    """Add academic record for a student"""
    return student_service.add_academic_record(db, student_id, record)

@router.get("/{student_id}/risk-assessment", response_model=RiskAssessmentSchema)
async def get_risk_assessment(student_id: str, db: Session = Depends(get_db)):
    """Get latest risk assessment for a student"""
    assessment = student_service.get_latest_risk_assessment(db, student_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="No risk assessment found")
    return assessment

@router.post("/{student_id}/risk-assessment", response_model=RiskAssessmentSchema)
async def create_risk_assessment(student_id: str, db: Session = Depends(get_db)):
    """Generate new risk assessment for a student"""
    # Check if student exists
    student = student_service.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Generate risk assessment using ML service
    assessment = await ml_service.generate_risk_assessment(db, student_id)
    return assessment

@router.get("/{student_id}/behavioral-data")
async def get_behavioral_data(
    student_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get behavioral data for a student within date range"""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    data = student_service.get_behavioral_data(db, student_id, start_date, end_date)
    return {"student_id": student_id, "behavioral_data": data, "period": {"start": start_date, "end": end_date}}

@router.get("/{student_id}/interventions")
async def get_interventions(student_id: str, db: Session = Depends(get_db)):
    """Get interventions for a student"""
    interventions = student_service.get_interventions(db, student_id)
    return {"student_id": student_id, "interventions": interventions}

@router.post("/{student_id}/interventions")
async def create_intervention(student_id: str, intervention_data: dict, db: Session = Depends(get_db)):
    """Create new intervention for a student"""
    return student_service.create_intervention(db, student_id, intervention_data)
