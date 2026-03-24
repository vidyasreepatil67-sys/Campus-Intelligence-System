from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from models.database import get_db, Student, RiskAssessment, Alert, Resource
from services.analytics_service import AnalyticsService

router = APIRouter()
analytics_service = AnalyticsService()

@router.get("/dashboard/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get dashboard overview statistics"""
    overview = analytics_service.get_dashboard_overview(db)
    return overview

@router.get("/risk/distribution")
async def get_risk_distribution(
    group_by: str = Query("department", regex="^(department|year|hostel)$"),
    db: Session = Depends(get_db)
):
    """Get risk level distribution by specified grouping"""
    distribution = analytics_service.get_risk_distribution(db, group_by)
    return {"group_by": group_by, "distribution": distribution}

@router.get("/risk/trends")
async def get_risk_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get risk level trends over time"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    trends = analytics_service.get_risk_trends(db, start_date, end_date)
    return {"period": {"start": start_date, "end": end_date}, "trends": trends}

@router.get("/academic/performance")
async def get_academic_performance(
    department: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get academic performance analytics"""
    performance = analytics_service.get_academic_performance(db, department, year)
    return {"filters": {"department": department, "year": year}, "performance": performance}

@router.get("/behavioral/insights")
async def get_behavioral_insights(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get behavioral insights and patterns"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    insights = analytics_service.get_behavioral_insights(db, start_date, end_date)
    return {"period": {"start": start_date, "end": end_date}, "insights": insights}

@router.get("/resource/utilization")
async def get_resource_utilization_analytics(
    resource_type: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get resource utilization analytics"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    utilization = analytics_service.get_resource_utilization_analytics(
        db, resource_type, start_date, end_date
    )
    return {"period": {"start": start_date, "end": end_date}, "utilization": utilization}

@router.get("/intervention/effectiveness")
async def get_intervention_effectiveness(
    intervention_type: Optional[str] = None,
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get intervention effectiveness analytics"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    effectiveness = analytics_service.get_intervention_effectiveness(
        db, intervention_type, start_date, end_date
    )
    return {"period": {"start": start_date, "end": end_date}, "effectiveness": effectiveness}

@router.get("/predictions/dropout-risk")
async def get_dropout_risk_predictions(
    department: Optional[str] = None,
    year: Optional[int] = None,
    threshold: float = Query(0.7, ge=0, le=1),
    db: Session = Depends(get_db)
):
    """Get dropout risk predictions"""
    predictions = analytics_service.get_dropout_risk_predictions(
        db, department, year, threshold
    )
    return {"filters": {"department": department, "year": year, "threshold": threshold}, "predictions": predictions}

@router.get("/correlations/analysis")
async def get_correlation_analysis(
    factors: List[str] = Query(["gpa", "attendance", "social_interaction"]),
    db: Session = Depends(get_db)
):
    """Get correlation analysis between different factors"""
    correlations = analytics_service.get_correlation_analysis(db, factors)
    return {"factors": factors, "correlations": correlations}

@router.get("/reports/generate")
async def generate_report(
    report_type: str = Query("monthly", regex="^(weekly|monthly|quarterly)$"),
    format: str = Query("json", regex="^(json|pdf|csv)$"),
    db: Session = Depends(get_db)
):
    """Generate analytics report"""
    report = analytics_service.generate_report(db, report_type, format)
    return {"report_type": report_type, "format": format, "report": report}

@router.get("/kpi/metrics")
async def get_kpi_metrics(db: Session = Depends(get_db)):
    """Get key performance indicators"""
    kpis = analytics_service.get_kpi_metrics(db)
    return kpis
