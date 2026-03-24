from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from models.database import Student, AcademicRecord, BehavioralData, RiskAssessment, Intervention
from models.schemas import Student as StudentSchema, AcademicRecord as AcademicRecordSchema, RiskAssessment as RiskAssessmentSchema

class StudentService:
    def get_students(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        department: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Student]:
        """Get students with optional filtering"""
        query = db.query(Student)
        
        if department:
            query = query.filter(Student.department == department)
        if year:
            query = query.filter(Student.year == year)
            
        return query.offset(skip).limit(limit).all()
    
    def get_student(self, db: Session, student_id: str) -> Optional[Student]:
        """Get a specific student by ID"""
        return db.query(Student).filter(Student.id == student_id).first()
    
    def create_student(self, db: Session, student: StudentSchema) -> Student:
        """Create a new student"""
        db_student = Student(
            id=student.id,
            name=student.name,
            email=student.email,
            student_id=student.student_id,
            department=student.department,
            year=student.year,
            gpa=student.gpa,
            enrollment_date=student.enrollment_date,
            hostel_room=student.hostel_room,
            contact_number=student.contact_number,
            emergency_contact=student.emergency_contact
        )
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    
    def update_student(self, db: Session, student_id: str, student: StudentSchema) -> Optional[Student]:
        """Update student information"""
        db_student = db.query(Student).filter(Student.id == student_id).first()
        if not db_student:
            return None
            
        for field, value in student.dict(exclude_unset=True).items():
            setattr(db_student, field, value)
            
        db.commit()
        db.refresh(db_student)
        return db_student
    
    def get_academic_records(self, db: Session, student_id: str) -> List[AcademicRecord]:
        """Get academic records for a student"""
        return db.query(AcademicRecord).filter(AcademicRecord.student_id == student_id).all()
    
    def add_academic_record(self, db: Session, student_id: str, record: AcademicRecordSchema) -> AcademicRecord:
        """Add academic record for a student"""
        db_record = AcademicRecord(
            student_id=student_id,
            course_id=record.course_id,
            semester=record.semester,
            grade=record.grade,
            attendance_rate=record.attendance_rate,
            assignment_completion_rate=record.assignment_completion_rate,
            last_updated=record.last_updated
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    
    def get_latest_risk_assessment(self, db: Session, student_id: str) -> Optional[RiskAssessment]:
        """Get latest risk assessment for a student"""
        return db.query(RiskAssessment)\
                 .filter(RiskAssessment.student_id == student_id)\
                 .order_by(RiskAssessment.assessment_date.desc())\
                 .first()
    
    def get_behavioral_data(
        self, 
        db: Session, 
        student_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[BehavioralData]:
        """Get behavioral data for a student within date range"""
        return db.query(BehavioralData)\
                 .filter(
                     and_(
                         BehavioralData.student_id == student_id,
                         BehavioralData.timestamp >= start_date,
                         BehavioralData.timestamp <= end_date
                     )
                 )\
                 .order_by(BehavioralData.timestamp.desc())\
                 .all()
    
    def get_interventions(self, db: Session, student_id: str) -> List[Intervention]:
        """Get interventions for a student"""
        return db.query(Intervention)\
                 .filter(Intervention.student_id == student_id)\
                 .order_by(Intervention.start_date.desc())\
                 .all()
    
    def create_intervention(self, db: Session, student_id: str, intervention_data: Dict[str, Any]) -> Intervention:
        """Create new intervention for a student"""
        db_intervention = Intervention(
            id=intervention_data.get("id"),
            student_id=student_id,
            intervention_type=intervention_data["intervention_type"],
            description=intervention_data["description"],
            assigned_counselor=intervention_data["assigned_counselor"],
            start_date=intervention_data.get("start_date", datetime.utcnow()),
            end_date=intervention_data.get("end_date"),
            status=intervention_data.get("status", "active")
        )
        db.add(db_intervention)
        db.commit()
        db.refresh(db_intervention)
        return db_intervention
    
    def get_students_at_risk(self, db: Session, risk_level: str = "HIGH") -> List[Student]:
        """Get students at specified risk level"""
        return db.query(Student)\
                 .join(RiskAssessment)\
                 .filter(RiskAssessment.risk_level == risk_level)\
                 .distinct()\
                 .all()
    
    def get_student_statistics(self, db: Session, student_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a student"""
        student = self.get_student(db, student_id)
        if not student:
            return {}
        
        # Academic stats
        academic_records = self.get_academic_records(db, student_id)
        avg_attendance = sum(r.attendance_rate for r in academic_records) / len(academic_records) if academic_records else 0
        avg_assignment_completion = sum(r.assignment_completion_rate for r in academic_records) / len(academic_records) if academic_records else 0
        
        # Risk assessment
        latest_risk = self.get_latest_risk_assessment(db, student_id)
        
        # Behavioral stats (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        behavioral_data = self.get_behavioral_data(db, student_id, start_date, end_date)
        avg_social_interaction = sum(b.social_interaction_count for b in behavioral_data) / len(behavioral_data) if behavioral_data else 0
        
        return {
            "student_id": student_id,
            "name": student.name,
            "department": student.department,
            "year": student.year,
            "gpa": student.gpa,
            "academic_stats": {
                "average_attendance": avg_attendance,
                "average_assignment_completion": avg_assignment_completion,
                "total_records": len(academic_records)
            },
            "risk_assessment": {
                "risk_level": latest_risk.risk_level if latest_risk else None,
                "risk_score": latest_risk.risk_score if latest_risk else None,
                "last_assessment": latest_risk.assessment_date if latest_risk else None
            },
            "behavioral_stats": {
                "average_social_interaction": avg_social_interaction,
                "total_activities": len(behavioral_data)
            }
        }
