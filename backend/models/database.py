from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    student_id = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    gpa = Column(Float)
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    hostel_room = Column(String)
    contact_number = Column(String)
    emergency_contact = Column(String)
    
    # Relationships
    academic_records = relationship("AcademicRecord", back_populates="student")
    behavioral_data = relationship("BehavioralData", back_populates="student")
    risk_assessments = relationship("RiskAssessment", back_populates="student")
    alerts = relationship("Alert", back_populates="student")
    interventions = relationship("Intervention", back_populates="student")

class AcademicRecord(Base):
    __tablename__ = "academic_records"
    
    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    course_id = Column(String, nullable=False)
    semester = Column(String, nullable=False)
    grade = Column(String)
    attendance_rate = Column(Float, nullable=False)
    assignment_completion_rate = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="academic_records")

class BehavioralData(Base):
    __tablename__ = "behavioral_data"
    
    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    activity_type = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    location = Column(String)
    social_interaction_count = Column(Integer, default=0)
    mood_score = Column(Integer)
    
    # Relationships
    student = relationship("Student", back_populates="behavioral_data")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    risk_level = Column(String, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_factors = Column(Text)  # JSON string
    assessment_date = Column(DateTime, default=datetime.utcnow)
    next_review_date = Column(DateTime, nullable=False)
    recommendations = Column(Text)  # JSON string
    
    # Relationships
    student = relationship("Student", back_populates="risk_assessments")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    assigned_to = Column(String)
    notes = Column(Text)
    
    # Relationships
    student = relationship("Student", back_populates="alerts")

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    location = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    current_utilization = Column(Integer, default=0)
    utilization_rate = Column(Float, default=0.0)
    status = Column(String, default="active")
    maintenance_schedule = Column(DateTime)
    
    # Relationships
    allocations = relationship("ResourceAllocation", back_populates="resource")

class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"
    
    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False)
    allocation_type = Column(String, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    status = Column(String, default="active")
    allocation_score = Column(Float, default=0.0)
    
    # Relationships
    resource = relationship("Resource", back_populates="allocations")

class Intervention(Base):
    __tablename__ = "interventions"
    
    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    intervention_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    assigned_counselor = Column(String, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    status = Column(String, default="active")
    effectiveness_score = Column(Float)
    
    # Relationships
    student = relationship("Student", back_populates="interventions")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/campus_intelligence")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
