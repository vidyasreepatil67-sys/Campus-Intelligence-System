from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from models.database import Resource, ResourceAllocation, Student
from models.schemas import Resource as ResourceSchema, ResourceAllocation as ResourceAllocationSchema

class ResourceService:
    def get_resources(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        resource_type: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Resource]:
        """Get resources with optional filtering"""
        query = db.query(Resource)
        
        if resource_type:
            query = query.filter(Resource.type == resource_type)
        if location:
            query = query.filter(Resource.location == location)
        if status:
            query = query.filter(Resource.status == status)
            
        return query.offset(skip).limit(limit).all()
    
    def get_resource(self, db: Session, resource_id: str) -> Optional[Resource]:
        """Get a specific resource by ID"""
        return db.query(Resource).filter(Resource.id == resource_id).first()
    
    def create_resource(self, db: Session, resource: ResourceSchema) -> Resource:
        """Create a new resource"""
        db_resource = Resource(
            id=resource.id,
            name=resource.name,
            type=resource.type,
            location=resource.location,
            capacity=resource.capacity,
            current_utilization=resource.current_utilization,
            utilization_rate=resource.utilization_rate,
            status=resource.status,
            maintenance_schedule=resource.maintenance_schedule
        )
        db.add(db_resource)
        db.commit()
        db.refresh(db_resource)
        return db_resource
    
    def update_resource(self, db: Session, resource_id: str, resource: ResourceSchema) -> Optional[Resource]:
        """Update resource information"""
        db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not db_resource:
            return None
            
        for field, value in resource.dict(exclude_unset=True).items():
            setattr(db_resource, field, value)
            
        # Update utilization rate if current utilization changed
        if hasattr(resource, 'current_utilization') and resource.capacity:
            db_resource.utilization_rate = (resource.current_utilization / resource.capacity) * 100
            
        db.commit()
        db.refresh(db_resource)
        return db_resource
    
    def get_resource_allocations(self, db: Session, resource_id: str) -> List[ResourceAllocation]:
        """Get allocations for a specific resource"""
        return db.query(ResourceAllocation)\
                 .filter(ResourceAllocation.resource_id == resource_id)\
                 .order_by(ResourceAllocation.start_date.desc())\
                 .all()
    
    def allocate_resource(
        self, 
        db: Session, 
        resource_id: str, 
        student_id: str, 
        allocation_type: str, 
        end_date: Optional[datetime] = None
    ) -> Optional[ResourceAllocation]:
        """Allocate a resource to a student"""
        resource = self.get_resource(db, resource_id)
        if not resource:
            return None
            
        # Check if resource has capacity
        if resource.current_utilization >= resource.capacity:
            return None
            
        import uuid
        db_allocation = ResourceAllocation(
            id=str(uuid.uuid4()),
            student_id=student_id,
            resource_id=resource_id,
            allocation_type=allocation_type,
            start_date=datetime.utcnow(),
            end_date=end_date,
            status="active"
        )
        
        # Update resource utilization
        resource.current_utilization += 1
        resource.utilization_rate = (resource.current_utilization / resource.capacity) * 100
        
        db.add(db_allocation)
        db.commit()
        db.refresh(db_allocation)
        return db_allocation
    
    def release_allocation(self, db: Session, allocation_id: str) -> bool:
        """Release a resource allocation"""
        allocation = db.query(ResourceAllocation).filter(ResourceAllocation.id == allocation_id).first()
        if not allocation:
            return False
            
        # Update resource utilization
        resource = db.query(Resource).filter(Resource.id == allocation.resource_id).first()
        if resource and resource.current_utilization > 0:
            resource.current_utilization -= 1
            resource.utilization_rate = (resource.current_utilization / resource.capacity) * 100
        
        allocation.status = "released"
        allocation.end_date = datetime.utcnow()
        
        db.commit()
        return True
    
    def get_utilization_summary(self, db: Session) -> Dict[str, Any]:
        """Get resource utilization summary"""
        total_resources = db.query(Resource).count()
        active_resources = db.query(Resource).filter(Resource.status == "active").count()
        
        # Overall utilization
        utilization_stats = db.query(
            func.avg(Resource.utilization_rate).label('average_utilization'),
            func.min(Resource.utilization_rate).label('min_utilization'),
            func.max(Resource.utilization_rate).label('max_utilization')
        ).first()
        
        # Utilization by type
        type_utilization = db.query(
            Resource.type,
            func.avg(Resource.utilization_rate).label('avg_utilization'),
            func.count(Resource.id).label('count')
        ).group_by(Resource.type).all()
        
        # Overutilized resources (>90%)
        overutilized = db.query(Resource).filter(Resource.utilization_rate > 90).count()
        
        # Underutilized resources (<30%)
        underutilized = db.query(Resource).filter(Resource.utilization_rate < 30).count()
        
        return {
            "total_resources": total_resources,
            "active_resources": active_resources,
            "average_utilization": round(utilization_stats.average_utilization or 0, 2),
            "min_utilization": round(utilization_stats.min_utilization or 0, 2),
            "max_utilization": round(utilization_stats.max_utilization or 0, 2),
            "overutilized_count": overutilized,
            "underutilized_count": underutilized,
            "utilization_by_type": {
                stat.type: {
                    "average_utilization": round(stat.avg_utilization, 2),
                    "count": stat.count
                } for stat in type_utilization
            }
        }
    
    def get_optimization_recommendations(self, db: Session) -> List[Dict[str, Any]]:
        """Get resource optimization recommendations"""
        recommendations = []
        
        # Find underutilized resources
        underutilized = db.query(Resource).filter(Resource.utilization_rate < 30).all()
        for resource in underutilized:
            recommendations.append({
                "type": "underutilization",
                "resource_id": resource.id,
                "resource_name": resource.name,
                "current_utilization": resource.utilization_rate,
                "recommendation": f"Consider repurposing or consolidating {resource.name} (current utilization: {resource.utilization_rate:.1f}%)"
            })
        
        # Find overutilized resources
        overutilized = db.query(Resource).filter(Resource.utilization_rate > 90).all()
        for resource in overutilized:
            recommendations.append({
                "type": "overutilization",
                "resource_id": resource.id,
                "resource_name": resource.name,
                "current_utilization": resource.utilization_rate,
                "recommendation": f"Consider expanding capacity or adding similar resources to {resource.name} (current utilization: {resource.utilization_rate:.1f}%)"
            })
        
        # Check for maintenance needs
        upcoming_maintenance = db.query(Resource)\
                                 .filter(
                                     and_(
                                         Resource.maintenance_schedule.isnot(None),
                                         Resource.maintenance_schedule <= datetime.utcnow() + timedelta(days=30)
                                     )
                                 ).all()
        
        for resource in upcoming_maintenance:
            recommendations.append({
                "type": "maintenance",
                "resource_id": resource.id,
                "resource_name": resource.name,
                "maintenance_date": resource.maintenance_schedule,
                "recommendation": f"Scheduled maintenance for {resource.name} on {resource.maintenance_schedule}"
            })
        
        return recommendations
    
    def get_available_hostel_rooms(
        self, 
        db: Session, 
        capacity_min: Optional[int] = None, 
        capacity_max: Optional[int] = None
    ) -> List[Resource]:
        """Get available hostel rooms"""
        query = db.query(Resource)\
                  .filter(
                      and_(
                          Resource.type == "hostel_room",
                          Resource.current_utilization < Resource.capacity,
                          Resource.status == "active"
                      )
                  )
        
        if capacity_min:
            query = query.filter(Resource.capacity >= capacity_min)
        if capacity_max:
            query = query.filter(Resource.capacity <= capacity_max)
            
        return query.all()
    
    def optimize_hostel_allocation(self, db: Session) -> Dict[str, Any]:
        """Run hostel allocation optimization algorithm"""
        # Get all students without hostel allocation
        students_needing_hostel = db.query(Student)\
                                   .filter(Student.hostel_room.is_(None))\
                                   .all()
        
        # Get available hostel rooms
        available_rooms = self.get_available_hostel_rooms(db)
        
        allocations_made = []
        optimization_score = 0
        
        # Simple allocation algorithm - prioritize by year and department
        sorted_students = sorted(students_needing_hostel, key=lambda x: (-x.year, x.department))
        
        for student in sorted_students:
            # Find best matching room (same department preference if possible)
            best_room = None
            best_score = 0
            
            for room in available_rooms:
                if room.current_utilization < room.capacity:
                    # Score based on department matching and availability
                    score = 0
                    if student.department.lower() in room.name.lower():
                        score += 10
                    score += (room.capacity - room.current_utilization) * 5
                    
                    if score > best_score:
                        best_score = score
                        best_room = room
            
            if best_room:
                allocation = self.allocate_resource(
                    db, best_room.id, student.id, "hostel_allocation"
                )
                if allocation:
                    allocations_made.append({
                        "student_id": student.id,
                        "student_name": student.name,
                        "room_id": best_room.id,
                        "room_name": best_room.name
                    })
                    optimization_score += best_score
        
        return {
            "allocations_made": len(allocations_made),
            "optimization_score": optimization_score,
            "details": allocations_made
        }
    
    def get_resource_analytics(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Get resource analytics over specified period"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Resource allocation trends
        allocation_trends = db.query(
            func.date(ResourceAllocation.start_date).label('date'),
            func.count(ResourceAllocation.id).label('allocations')
        ).filter(
            ResourceAllocation.start_date >= start_date
        ).group_by(func.date(ResourceAllocation.start_date)).all()
        
        # Most utilized resources
        top_resources = db.query(Resource)\
                          .filter(Resource.status == "active")\
                          .order_by(Resource.utilization_rate.desc())\
                          .limit(10).all()
        
        return {
            "period": {"start": start_date, "end": end_date},
            "allocation_trends": [
                {"date": str(trend.date), "allocations": trend.allocations} 
                for trend in allocation_trends
            ],
            "top_utilized_resources": [
                {
                    "id": resource.id,
                    "name": resource.name,
                    "type": resource.type,
                    "utilization_rate": resource.utilization_rate,
                    "capacity": resource.capacity
                } for resource in top_resources
            ]
        }
