from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from models.database import get_db, Alert, Student
from models.schemas import Alert as AlertSchema, AlertType, RiskLevel
from services.alert_service import AlertService

router = APIRouter()
alert_service = AlertService()

@router.get("/", response_model=List[AlertSchema])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    alert_type: Optional[AlertType] = None,
    severity: Optional[RiskLevel] = None,
    resolved: Optional[bool] = None,
    assigned_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all alerts with optional filtering"""
    return alert_service.get_alerts(
        db, 
        skip=skip, 
        limit=limit, 
        alert_type=alert_type, 
        severity=severity, 
        resolved=resolved, 
        assigned_to=assigned_to
    )

@router.get("/{alert_id}", response_model=AlertSchema)
async def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """Get a specific alert by ID"""
    alert = alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/", response_model=AlertSchema)
async def create_alert(alert: AlertSchema, db: Session = Depends(get_db)):
    """Create a new alert"""
    return alert_service.create_alert(db, alert)

@router.put("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str, 
    notes: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    """Resolve an alert"""
    resolved_alert = alert_service.resolve_alert(db, alert_id, notes)
    if not resolved_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert resolved successfully", "alert": resolved_alert}

@router.put("/{alert_id}/assign")
async def assign_alert(
    alert_id: str, 
    assigned_to: str, 
    db: Session = Depends(get_db)
):
    """Assign an alert to a staff member"""
    assigned_alert = alert_service.assign_alert(db, alert_id, assigned_to)
    if not assigned_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert assigned successfully", "alert": assigned_alert}

@router.get("/student/{student_id}", response_model=List[AlertSchema])
async def get_student_alerts(
    student_id: str,
    resolved: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all alerts for a specific student"""
    alerts = alert_service.get_student_alerts(db, student_id, resolved)
    return alerts

@router.get("/stats/summary")
async def get_alert_stats(db: Session = Depends(get_db)):
    """Get alert statistics summary"""
    stats = alert_service.get_alert_stats(db)
    return stats

@router.get("/stats/trends")
async def get_alert_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get alert trends over specified period"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    trends = alert_service.get_alert_trends(db, start_date, end_date)
    return {"period": {"start": start_date, "end": end_date}, "trends": trends}
