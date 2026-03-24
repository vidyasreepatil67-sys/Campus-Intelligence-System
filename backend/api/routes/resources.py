from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from models.database import get_db, Resource, ResourceAllocation, Student
from models.schemas import Resource as ResourceSchema, ResourceAllocation as ResourceAllocationSchema
from services.resource_service import ResourceService

router = APIRouter()
resource_service = ResourceService()

@router.get("/", response_model=List[ResourceSchema])
async def get_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resource_type: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all resources with optional filtering"""
    return resource_service.get_resources(
        db, 
        skip=skip, 
        limit=limit, 
        resource_type=resource_type, 
        location=location, 
        status=status
    )

@router.get("/{resource_id}", response_model=ResourceSchema)
async def get_resource(resource_id: str, db: Session = Depends(get_db)):
    """Get a specific resource by ID"""
    resource = resource_service.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.post("/", response_model=ResourceSchema)
async def create_resource(resource: ResourceSchema, db: Session = Depends(get_db)):
    """Create a new resource"""
    return resource_service.create_resource(db, resource)

@router.put("/{resource_id}", response_model=ResourceSchema)
async def update_resource(
    resource_id: str, 
    resource: ResourceSchema, 
    db: Session = Depends(get_db)
):
    """Update resource information"""
    updated_resource = resource_service.update_resource(db, resource_id, resource)
    if not updated_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return updated_resource

@router.get("/{resource_id}/allocations", response_model=List[ResourceAllocationSchema])
async def get_resource_allocations(resource_id: str, db: Session = Depends(get_db)):
    """Get allocations for a specific resource"""
    allocations = resource_service.get_resource_allocations(db, resource_id)
    return allocations

@router.post("/{resource_id}/allocate")
async def allocate_resource(
    resource_id: str,
    student_id: str,
    allocation_type: str,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Allocate a resource to a student"""
    allocation = resource_service.allocate_resource(
        db, resource_id, student_id, allocation_type, end_date
    )
    if not allocation:
        raise HTTPException(status_code=400, detail="Resource allocation failed")
    return {"message": "Resource allocated successfully", "allocation": allocation}

@router.put("/allocations/{allocation_id}/release")
async def release_allocation(allocation_id: str, db: Session = Depends(get_db)):
    """Release a resource allocation"""
    success = resource_service.release_allocation(db, allocation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return {"message": "Resource allocation released successfully"}

@router.get("/utilization/summary")
async def get_utilization_summary(db: Session = Depends(get_db)):
    """Get resource utilization summary"""
    summary = resource_service.get_utilization_summary(db)
    return summary

@router.get("/optimization/recommendations")
async def get_optimization_recommendations(db: Session = Depends(get_db)):
    """Get resource optimization recommendations"""
    recommendations = resource_service.get_optimization_recommendations(db)
    return {"recommendations": recommendations}

@router.get("/hostel/availability")
async def get_hostel_availability(
    capacity_min: Optional[int] = None,
    capacity_max: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get available hostel rooms"""
    rooms = resource_service.get_available_hostel_rooms(db, capacity_min, capacity_max)
    return {"available_rooms": rooms}

@router.post("/hostel/optimize-allocation")
async def optimize_hostel_allocation(db: Session = Depends(get_db)):
    """Run hostel allocation optimization algorithm"""
    optimization_result = resource_service.optimize_hostel_allocation(db)
    return optimization_result
