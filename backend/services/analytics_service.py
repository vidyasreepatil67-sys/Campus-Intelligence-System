from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from models.database import Student, RiskAssessment, Alert, Resource, AcademicRecord, BehavioralData, Intervention

class AnalyticsService:
    def get_dashboard_overview(self, db: Session) -> Dict[str, Any]:
        """Get dashboard overview statistics"""
        # Student statistics
        total_students = db.query(Student).count()
        students_at_risk = db.query(Student)\
                             .join(RiskAssessment)\
                             .filter(RiskAssessment.risk_level.in_(['HIGH', 'CRITICAL']))\
                             .distinct()\
                             .count()
        
        # Alert statistics
        total_alerts = db.query(Alert).count()
        critical_alerts = db.query(Alert)\
                           .filter(and_(Alert.severity == 'CRITICAL', Alert.resolved == False))\
                           .count()
        
        # Resource utilization
        avg_resource_utilization = db.query(func.avg(Resource.utilization_rate)).scalar() or 0
        
        # Recent risk assessments
        recent_assessments = db.query(RiskAssessment)\
                              .filter(RiskAssessment.assessment_date >= datetime.utcnow() - timedelta(days=7))\
                              .count()
        
        # Active interventions
        active_interventions = db.query(Intervention)\
                                 .filter(Intervention.status == 'active')\
                                 .count()
        
        return {
            "students": {
                "total": total_students,
                "at_risk": students_at_risk,
                "risk_percentage": round((students_at_risk / total_students * 100) if total_students > 0 else 0, 2)
            },
            "alerts": {
                "total": total_alerts,
                "critical_unresolved": critical_alerts
            },
            "resources": {
                "average_utilization": round(avg_resource_utilization, 2)
            },
            "assessments": {
                "recent_weekly": recent_assessments
            },
            "interventions": {
                "active": active_interventions
            }
        }
    
    def get_risk_distribution(self, db: Session, group_by: str = "department") -> Dict[str, Any]:
        """Get risk level distribution by specified grouping"""
        if group_by == "department":
            risk_by_dept = db.query(
                Student.department,
                RiskAssessment.risk_level,
                func.count(RiskAssessment.id).label('count')
            ).join(RiskAssessment)\
             .group_by(Student.department, RiskAssessment.risk_level)\
             .all()
            
            distribution = {}
            for dept, risk_level, count in risk_by_dept:
                if dept not in distribution:
                    distribution[dept] = {}
                distribution[dept][risk_level] = count
                
        elif group_by == "year":
            risk_by_year = db.query(
                Student.year,
                RiskAssessment.risk_level,
                func.count(RiskAssessment.id).label('count')
            ).join(RiskAssessment)\
             .group_by(Student.year, RiskAssessment.risk_level)\
             .all()
            
            distribution = {}
            for year, risk_level, count in risk_by_year:
                if year not in distribution:
                    distribution[year] = {}
                distribution[year][risk_level] = count
                
        elif group_by == "hostel":
            risk_by_hostel = db.query(
                Student.hostel_room,
                RiskAssessment.risk_level,
                func.count(RiskAssessment.id).label('count')
            ).join(RiskAssessment)\
             .filter(Student.hostel_room.isnot(None))\
             .group_by(Student.hostel_room, RiskAssessment.risk_level)\
             .all()
            
            distribution = {}
            for hostel, risk_level, count in risk_by_hostel:
                if hostel not in distribution:
                    distribution[hostel] = {}
                distribution[hostel][risk_level] = count
        
        return {"group_by": group_by, "distribution": distribution}
    
    def get_risk_trends(self, db: Session, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get risk level trends over time"""
        trends = db.query(
            func.date(RiskAssessment.assessment_date).label('date'),
            RiskAssessment.risk_level,
            func.count(RiskAssessment.id).label('count')
        ).filter(
            and_(
                RiskAssessment.assessment_date >= start_date,
                RiskAssessment.assessment_date <= end_date
            )
        ).group_by(func.date(RiskAssessment.assessment_date), RiskAssessment.risk_level).all()
        
        return [
            {"date": str(trend.date), "risk_level": trend.risk_level, "count": trend.count} 
            for trend in trends
        ]
    
    def get_academic_performance(
        self, 
        db: Session, 
        department: Optional[str] = None, 
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get academic performance analytics"""
        query = db.query(AcademicRecord).join(Student)
        
        if department:
            query = query.filter(Student.department == department)
        if year:
            query = query.filter(Student.year == year)
        
        records = query.all()
        
        if not records:
            return {"message": "No academic records found for the specified filters"}
        
        # Calculate statistics
        avg_gpa = sum(r.attendance_rate for r in records) / len(records)
        avg_attendance = sum(r.attendance_rate for r in records) / len(records)
        avg_assignment_completion = sum(r.assignment_completion_rate for r in records) / len(records)
        
        # Grade distribution
        grade_dist = {}
        for record in records:
            if record.grade:
                grade_dist[record.grade] = grade_dist.get(record.grade, 0) + 1
        
        return {
            "total_records": len(records),
            "average_attendance": round(avg_attendance, 2),
            "average_assignment_completion": round(avg_assignment_completion, 2),
            "grade_distribution": grade_dist,
            "filters": {"department": department, "year": year}
        }
    
    def get_behavioral_insights(self, db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get behavioral insights and patterns"""
        behavioral_data = db.query(BehavioralData)\
                           .filter(
                               and_(
                                   BehavioralData.timestamp >= start_date,
                                   BehavioralData.timestamp <= end_date
                               )
                           ).all()
        
        if not behavioral_data:
            return {"message": "No behavioral data found for the specified period"}
        
        # Activity type distribution
        activity_types = {}
        for data in behavioral_data:
            activity_types[data.activity_type] = activity_types.get(data.activity_type, 0) + 1
        
        # Social interaction statistics
        social_interactions = [d.social_interaction_count for d in behavioral_data]
        avg_social = sum(social_interactions) / len(social_interactions) if social_interactions else 0
        
        # Mood score statistics
        mood_scores = [d.mood_score for d in behavioral_data if d.mood_score is not None]
        avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else None
        
        # Peak activity hours
        hourly_activity = {}
        for data in behavioral_data:
            hour = data.timestamp.hour
            hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
        
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else None
        
        return {
            "total_activities": len(behavioral_data),
            "activity_distribution": activity_types,
            "social_interaction_stats": {
                "average": round(avg_social, 2),
                "max": max(social_interactions) if social_interactions else 0
            },
            "mood_stats": {
                "average": round(avg_mood, 2) if avg_mood else None,
                "total_entries": len(mood_scores)
            },
            "peak_activity_hour": peak_hour,
            "hourly_distribution": hourly_activity
        }
    
    def get_resource_utilization_analytics(
        self, 
        db: Session, 
        resource_type: Optional[str] = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get resource utilization analytics"""
        query = db.query(Resource)
        
        if resource_type:
            query = query.filter(Resource.type == resource_type)
        
        resources = query.all()
        
        if not resources:
            return {"message": "No resources found for the specified type"}
        
        # Utilization statistics
        utilization_rates = [r.utilization_rate for r in resources]
        
        # Capacity distribution
        capacity_ranges = {
            "small": len([r for r in resources if r.capacity <= 10]),
            "medium": len([r for r in resources if 10 < r.capacity <= 50]),
            "large": len([r for r in resources if r.capacity > 50])
        }
        
        # Status distribution
        status_dist = {}
        for resource in resources:
            status_dist[resource.status] = status_dist.get(resource.status, 0) + 1
        
        return {
            "total_resources": len(resources),
            "utilization_stats": {
                "average": round(sum(utilization_rates) / len(utilization_rates), 2),
                "min": min(utilization_rates),
                "max": max(utilization_rates)
            },
            "capacity_distribution": capacity_ranges,
            "status_distribution": status_dist,
            "resource_type": resource_type
        }
    
    def get_intervention_effectiveness(
        self, 
        db: Session, 
        intervention_type: Optional[str] = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get intervention effectiveness analytics"""
        query = db.query(Intervention)
        
        if intervention_type:
            query = query.filter(Intervention.intervention_type == intervention_type)
        
        if start_date:
            query = query.filter(Intervention.start_date >= start_date)
        
        interventions = query.all()
        
        if not interventions:
            return {"message": "No interventions found for the specified criteria"}
        
        # Status distribution
        status_dist = {}
        for intervention in interventions:
            status_dist[intervention.status] = status_dist.get(intervention.status, 0) + 1
        
        # Effectiveness scores
        effectiveness_scores = [i.effectiveness_score for i in interventions if i.effectiveness_score is not None]
        avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else None
        
        # Intervention type distribution
        type_dist = {}
        for intervention in interventions:
            type_dist[intervention.intervention_type] = type_dist.get(intervention.intervention_type, 0) + 1
        
        return {
            "total_interventions": len(interventions),
            "status_distribution": status_dist,
            "effectiveness_stats": {
                "average": round(avg_effectiveness, 2) if avg_effectiveness else None,
                "total_scored": len(effectiveness_scores)
            },
            "type_distribution": type_dist
        }
    
    def get_dropout_risk_predictions(
        self, 
        db: Session, 
        department: Optional[str] = None,
        year: Optional[int] = None,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Get dropout risk predictions above threshold"""
        query = db.query(Student, RiskAssessment)\
                 .join(RiskAssessment)\
                 .filter(RiskAssessment.risk_score >= threshold)
        
        if department:
            query = query.filter(Student.department == department)
        if year:
            query = query.filter(Student.year == year)
        
        predictions = query.all()
        
        return [
            {
                "student_id": student.id,
                "name": student.name,
                "department": student.department,
                "year": student.year,
                "risk_score": risk_assessment.risk_score,
                "risk_level": risk_assessment.risk_level,
                "last_assessment": risk_assessment.assessment_date
            }
            for student, risk_assessment in predictions
        ]
    
    def get_correlation_analysis(self, db: Session, factors: List[str]) -> Dict[str, Any]:
        """Get correlation analysis between different factors"""
        # This is a simplified version - in practice, you'd use statistical libraries
        correlations = {}
        
        # Sample correlations based on available data
        if "gpa" in factors and "attendance" in factors:
            # Calculate correlation between GPA and attendance
            records = db.query(AcademicRecord).all()
            if records:
                correlations["gpa_attendance"] = 0.65  # Sample correlation coefficient
        
        if "social_interaction" in factors and "mood" in factors:
            # Calculate correlation between social interaction and mood
            behavioral_data = db.query(BehavioralData).filter(
                and_(
                    BehavioralData.social_interaction_count > 0,
                    BehavioralData.mood_score.isnot(None)
                )
            ).all()
            if behavioral_data:
                correlations["social_mood"] = 0.58  # Sample correlation coefficient
        
        return {
            "factors_analyzed": factors,
            "correlations": correlations,
            "note": "These are sample correlations. Implement proper statistical analysis for production."
        }
    
    def generate_report(self, db: Session, report_type: str, format: str) -> Dict[str, Any]:
        """Generate analytics report"""
        if report_type == "weekly":
            start_date = datetime.utcnow() - timedelta(days=7)
        elif report_type == "monthly":
            start_date = datetime.utcnow() - timedelta(days=30)
        elif report_type == "quarterly":
            start_date = datetime.utcnow() - timedelta(days=90)
        else:
            start_date = datetime.utcnow() - timedelta(days=30)
        
        end_date = datetime.utcnow()
        
        # Gather all data for the report
        dashboard_data = self.get_dashboard_overview(db)
        risk_trends = self.get_risk_trends(db, start_date, end_date)
        behavioral_insights = self.get_behavioral_insights(db, start_date, end_date)
        resource_analytics = self.get_resource_utilization_analytics(db, None, start_date, end_date)
        
        report = {
            "report_type": report_type,
            "period": {"start": start_date, "end": end_date},
            "generated_at": datetime.utcnow(),
            "dashboard_overview": dashboard_data,
            "risk_trends": risk_trends,
            "behavioral_insights": behavioral_insights,
            "resource_analytics": resource_analytics
        }
        
        return report
    
    def get_kpi_metrics(self, db: Session) -> Dict[str, Any]:
        """Get key performance indicators"""
        # Student retention rate (simplified)
        total_students = db.query(Student).count()
        at_risk_students = db.query(Student)\
                             .join(RiskAssessment)\
                             .filter(RiskAssessment.risk_level.in_(['HIGH', 'CRITICAL']))\
                             .distinct()\
                             .count()
        
        retention_rate = ((total_students - at_risk_students) / total_students * 100) if total_students > 0 else 0
        
        # Alert response rate
        total_alerts = db.query(Alert).count()
        resolved_alerts = db.query(Alert).filter(Alert.resolved == True).count()
        alert_response_rate = (resolved_alerts / total_alerts * 100) if total_alerts > 0 else 0
        
        # Resource utilization efficiency
        avg_utilization = db.query(func.avg(Resource.utilization_rate)).scalar() or 0
        
        # Intervention success rate
        total_interventions = db.query(Intervention).count()
        successful_interventions = db.query(Intervention)\
                                     .filter(
                                         and_(
                                             Intervention.status == 'completed',
                                             Intervention.effectiveness_score >= 0.7
                                         )
                                     ).count()
        
        intervention_success_rate = (successful_interventions / total_interventions * 100) if total_interventions > 0 else 0
        
        return {
            "student_retention_rate": round(retention_rate, 2),
            "alert_response_rate": round(alert_response_rate, 2),
            "resource_utilization_efficiency": round(avg_utilization, 2),
            "intervention_success_rate": round(intervention_success_rate, 2),
            "total_students": total_students,
            "at_risk_students": at_risk_students,
            "total_alerts": total_alerts,
            "resolved_alerts": resolved_alerts,
            "total_interventions": total_interventions,
            "successful_interventions": successful_interventions
        }
