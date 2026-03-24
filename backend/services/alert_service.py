from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from models.database import Alert, Student
from models.schemas import Alert as AlertSchema, AlertType, RiskLevel

class AlertService:
    def get_alerts(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        alert_type: Optional[AlertType] = None,
        severity: Optional[RiskLevel] = None,
        resolved: Optional[bool] = None,
        assigned_to: Optional[str] = None
    ) -> List[Alert]:
        """Get alerts with optional filtering"""
        query = db.query(Alert)
        
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        if severity:
            query = query.filter(Alert.severity == severity)
        if resolved is not None:
            query = query.filter(Alert.resolved == resolved)
        if assigned_to:
            query = query.filter(Alert.assigned_to == assigned_to)
            
        return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_alert(self, db: Session, alert_id: str) -> Optional[Alert]:
        """Get a specific alert by ID"""
        return db.query(Alert).filter(Alert.id == alert_id).first()
    
    def create_alert(self, db: Session, alert: AlertSchema) -> Alert:
        """Create a new alert"""
        db_alert = Alert(
            id=alert.id,
            student_id=alert.student_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            created_at=alert.created_at,
            resolved=alert.resolved,
            resolved_at=alert.resolved_at,
            assigned_to=alert.assigned_to,
            notes=alert.notes
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return db_alert
    
    def resolve_alert(self, db: Session, alert_id: str, notes: Optional[str] = None) -> Optional[Alert]:
        """Resolve an alert"""
        db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not db_alert:
            return None
            
        db_alert.resolved = True
        db_alert.resolved_at = datetime.utcnow()
        if notes:
            db_alert.notes = notes
            
        db.commit()
        db.refresh(db_alert)
        return db_alert
    
    def assign_alert(self, db: Session, alert_id: str, assigned_to: str) -> Optional[Alert]:
        """Assign an alert to a staff member"""
        db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not db_alert:
            return None
            
        db_alert.assigned_to = assigned_to
        db.commit()
        db.refresh(db_alert)
        return db_alert
    
    def get_student_alerts(self, db: Session, student_id: str, resolved: Optional[bool] = None) -> List[Alert]:
        """Get all alerts for a specific student"""
        query = db.query(Alert).filter(Alert.student_id == student_id)
        
        if resolved is not None:
            query = query.filter(Alert.resolved == resolved)
            
        return query.order_by(Alert.created_at.desc()).all()
    
    def get_alert_stats(self, db: Session) -> Dict[str, Any]:
        """Get alert statistics summary"""
        total_alerts = db.query(Alert).count()
        unresolved_alerts = db.query(Alert).filter(Alert.resolved == False).count()
        
        # Alerts by severity
        severity_stats = db.query(
            Alert.severity,
            func.count(Alert.id).label('count')
        ).group_by(Alert.severity).all()
        
        # Alerts by type
        type_stats = db.query(
            Alert.alert_type,
            func.count(Alert.id).label('count')
        ).group_by(Alert.alert_type).all()
        
        # Recent alerts (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_alerts = db.query(Alert).filter(Alert.created_at >= seven_days_ago).count()
        
        return {
            "total_alerts": total_alerts,
            "unresolved_alerts": unresolved_alerts,
            "resolved_alerts": total_alerts - unresolved_alerts,
            "recent_alerts_7_days": recent_alerts,
            "severity_distribution": {stat.severity: stat.count for stat in severity_stats},
            "type_distribution": {stat.alert_type: stat.count for stat in type_stats}
        }
    
    def get_alert_trends(self, db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get alert trends over specified period"""
        # Daily alert counts
        daily_counts = db.query(
            func.date(Alert.created_at).label('date'),
            func.count(Alert.id).label('count')
        ).filter(
            and_(
                Alert.created_at >= start_date,
                Alert.created_at <= end_date
            )
        ).group_by(func.date(Alert.created_at)).all()
        
        # Severity trends
        severity_trends = db.query(
            func.date(Alert.created_at).label('date'),
            Alert.severity,
            func.count(Alert.id).label('count')
        ).filter(
            and_(
                Alert.created_at >= start_date,
                Alert.created_at <= end_date
            )
        ).group_by(func.date(Alert.created_at), Alert.severity).all()
        
        # Type trends
        type_trends = db.query(
            func.date(Alert.created_at).label('date'),
            Alert.alert_type,
            func.count(Alert.id).label('count')
        ).filter(
            and_(
                Alert.created_at >= start_date,
                Alert.created_at <= end_date
            )
        ).group_by(func.date(Alert.created_at), Alert.alert_type).all()
        
        return {
            "daily_counts": [{"date": str(count.date), "count": count.count} for count in daily_counts],
            "severity_trends": [
                {"date": str(trend.date), "severity": trend.severity, "count": trend.count} 
                for trend in severity_trends
            ],
            "type_trends": [
                {"date": str(trend.date), "type": trend.alert_type, "count": trend.count} 
                for trend in type_trends
            ]
        }
    
    def create_auto_alert(
        self, 
        db: Session, 
        student_id: str, 
        alert_type: AlertType, 
        severity: RiskLevel, 
        message: str
    ) -> Alert:
        """Create an automatic alert (generated by system)"""
        import uuid
        
        alert = AlertSchema(
            id=str(uuid.uuid4()),
            student_id=student_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            created_at=datetime.utcnow()
        )
        
        return self.create_alert(db, alert)
    
    def get_critical_alerts(self, db: Session, limit: int = 50) -> List[Alert]:
        """Get critical alerts that need immediate attention"""
        return db.query(Alert)\
                 .filter(
                     and_(
                         Alert.severity.in_(['HIGH', 'CRITICAL']),
                         Alert.resolved == False
                     )
                 )\
                 .order_by(Alert.created_at.desc())\
                 .limit(limit)\
                 .all()
    
    def get_alert_resolution_time_stats(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Get alert resolution time statistics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        resolved_alerts = db.query(Alert)\
                           .filter(
                               and_(
                                   Alert.resolved == True,
                                   Alert.resolved_at >= start_date
                               )
                           ).all()
        
        if not resolved_alerts:
            return {"average_resolution_time_hours": 0, "total_resolved": 0}
        
        resolution_times = []
        for alert in resolved_alerts:
            if alert.resolved_at:
                resolution_time = alert.resolved_at - alert.created_at
                resolution_times.append(resolution_time.total_seconds() / 3600)  # Convert to hours
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return {
            "average_resolution_time_hours": round(avg_resolution_time, 2),
            "total_resolved": len(resolved_alerts),
            "min_resolution_time_hours": round(min(resolution_times), 2) if resolution_times else 0,
            "max_resolution_time_hours": round(max(resolution_times), 2) if resolution_times else 0
        }
