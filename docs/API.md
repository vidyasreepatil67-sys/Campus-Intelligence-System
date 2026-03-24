# Campus Intelligence System - API Documentation

## Overview

The Campus Intelligence System API provides endpoints for student well-being monitoring, alert management, resource optimization, and analytics. The API is built using FastAPI and follows RESTful principles.

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com/api`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Students

#### Get All Students
```http
GET /api/students
```

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 100)
- `department` (string, optional): Filter by department
- `year` (integer, optional): Filter by year

**Response:**
```json
[
  {
    "id": "string",
    "name": "string",
    "email": "string",
    "student_id": "string",
    "department": "string",
    "year": 0,
    "gpa": 0.0,
    "enrollment_date": "2024-01-01T00:00:00",
    "hostel_room": "string",
    "contact_number": "string",
    "emergency_contact": "string"
  }
]
```

#### Get Student by ID
```http
GET /api/students/{student_id}
```

#### Create Student
```http
POST /api/students
```

**Request Body:**
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "student_id": "string",
  "department": "string",
  "year": 0,
  "gpa": 0.0,
  "enrollment_date": "2024-01-01T00:00:00",
  "hostel_room": "string",
  "contact_number": "string",
  "emergency_contact": "string"
}
```

#### Get Student Academic Records
```http
GET /api/students/{student_id}/academic-records
```

#### Get Student Risk Assessment
```http
GET /api/students/{student_id}/risk-assessment
```

#### Generate Risk Assessment
```http
POST /api/students/{student_id}/risk-assessment
```

#### Get Student Behavioral Data
```http
GET /api/students/{student_id}/behavioral-data
```

**Query Parameters:**
- `start_date` (datetime, optional): Start date for data range
- `end_date` (datetime, optional): End date for data range

### Alerts

#### Get All Alerts
```http
GET /api/alerts
```

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip
- `limit` (integer, optional): Maximum number of records to return
- `alert_type` (string, optional): Filter by alert type
- `severity` (string, optional): Filter by severity level
- `resolved` (boolean, optional): Filter by resolution status
- `assigned_to` (string, optional): Filter by assigned staff

#### Get Alert by ID
```http
GET /api/alerts/{alert_id}
```

#### Create Alert
```http
POST /api/alerts
```

**Request Body:**
```json
{
  "id": "string",
  "student_id": "string",
  "alert_type": "DROPOUT_RISK|SUICIDE_RISK|ACADEMIC_DECLINE|SOCIAL_ISOLATION|RESOURCE_MISUSE",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "message": "string",
  "created_at": "2024-01-01T00:00:00",
  "resolved": false,
  "resolved_at": null,
  "assigned_to": "string",
  "notes": "string"
}
```

#### Resolve Alert
```http
PUT /api/alerts/{alert_id}/resolve
```

**Request Body:**
```json
{
  "notes": "string"
}
```

#### Assign Alert
```http
PUT /api/alerts/{alert_id}/assign
```

**Request Body:**
```json
{
  "assigned_to": "string"
}
```

#### Get Student Alerts
```http
GET /api/alerts/student/{student_id}
```

#### Get Alert Statistics
```http
GET /api/alerts/stats/summary
```

#### Get Alert Trends
```http
GET /api/alerts/stats/trends
```

**Query Parameters:**
- `days` (integer, optional): Number of days to analyze (default: 30)

### Resources

#### Get All Resources
```http
GET /api/resources
```

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip
- `limit` (integer, optional): Maximum number of records to return
- `resource_type` (string, optional): Filter by resource type
- `location` (string, optional): Filter by location
- `status` (string, optional): Filter by status

#### Get Resource by ID
```http
GET /api/resources/{resource_id}
```

#### Create Resource
```http
POST /api/resources
```

**Request Body:**
```json
{
  "id": "string",
  "name": "string",
  "type": "string",
  "location": "string",
  "capacity": 0,
  "current_utilization": 0,
  "utilization_rate": 0.0,
  "status": "string",
  "maintenance_schedule": "2024-01-01T00:00:00"
}
```

#### Allocate Resource
```http
POST /api/resources/{resource_id}/allocate
```

**Request Body:**
```json
{
  "student_id": "string",
  "allocation_type": "string",
  "end_date": "2024-01-01T00:00:00"
}
```

#### Get Resource Utilization Summary
```http
GET /api/resources/utilization/summary
```

#### Get Optimization Recommendations
```http
GET /api/resources/optimization/recommendations
```

#### Get Hostel Availability
```http
GET /api/resources/hostel/availability
```

**Query Parameters:**
- `capacity_min` (integer, optional): Minimum capacity
- `capacity_max` (integer, optional): Maximum capacity

#### Optimize Hostel Allocation
```http
POST /api/resources/hostel/optimize-allocation
```

### Analytics

#### Get Dashboard Overview
```http
GET /api/analytics/dashboard/overview
```

#### Get Risk Distribution
```http
GET /api/analytics/risk/distribution
```

**Query Parameters:**
- `group_by` (string, optional): Group by field (department|year|hostel)

#### Get Risk Trends
```http
GET /api/analytics/risk/trends
```

**Query Parameters:**
- `days` (integer, optional): Number of days to analyze (default: 30)

#### Get Academic Performance
```http
GET /api/analytics/academic/performance
```

**Query Parameters:**
- `department` (string, optional): Filter by department
- `year` (integer, optional): Filter by year

#### Get Behavioral Insights
```http
GET /api/analytics/behavioral/insights
```

**Query Parameters:**
- `days` (integer, optional): Number of days to analyze (default: 30)

#### Get Resource Utilization Analytics
```http
GET /api/analytics/resource/utilization
```

**Query Parameters:**
- `resource_type` (string, optional): Filter by resource type
- `days` (integer, optional): Number of days to analyze (default: 30)

#### Get Intervention Effectiveness
```http
GET /api/analytics/intervention/effectiveness
```

**Query Parameters:**
- `intervention_type` (string, optional): Filter by intervention type
- `days` (integer, optional): Number of days to analyze (default: 90)

#### Get Dropout Risk Predictions
```http
GET /api/analytics/predictions/dropout-risk
```

**Query Parameters:**
- `department` (string, optional): Filter by department
- `year` (integer, optional): Filter by year
- `threshold` (float, optional): Risk threshold (default: 0.7)

#### Get Correlation Analysis
```http
GET /api/analytics/correlations/analysis
```

**Query Parameters:**
- `factors` (array, optional): Factors to analyze

#### Generate Report
```http
GET /api/analytics/reports/generate
```

**Query Parameters:**
- `report_type` (string, optional): Report type (weekly|monthly|quarterly)
- `format` (string, optional): Output format (json|pdf|csv)

#### Get KPI Metrics
```http
GET /api/analytics/kpi/metrics
```

## Data Models

### Student
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "student_id": "string",
  "department": "string",
  "year": 0,
  "gpa": 0.0,
  "enrollment_date": "2024-01-01T00:00:00",
  "hostel_room": "string",
  "contact_number": "string",
  "emergency_contact": "string"
}
```

### Risk Assessment
```json
{
  "id": "string",
  "student_id": "string",
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "risk_score": 0.0,
  "risk_factors": ["string"],
  "assessment_date": "2024-01-01T00:00:00",
  "next_review_date": "2024-01-01T00:00:00",
  "recommendations": ["string"]
}
```

### Alert
```json
{
  "id": "string",
  "student_id": "string",
  "alert_type": "DROPOUT_RISK|SUICIDE_RISK|ACADEMIC_DECLINE|SOCIAL_ISOLATION|RESOURCE_MISUSE",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "message": "string",
  "created_at": "2024-01-01T00:00:00",
  "resolved": false,
  "resolved_at": null,
  "assigned_to": "string",
  "notes": "string"
}
```

### Resource
```json
{
  "id": "string",
  "name": "string",
  "type": "string",
  "location": "string",
  "capacity": 0,
  "current_utilization": 0,
  "utilization_rate": 0.0,
  "status": "string",
  "maintenance_schedule": "2024-01-01T00:00:00"
}
```

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

Error Response Format:
```json
{
  "detail": "Error message description",
  "status_code": 400
}
```

## Rate Limiting

API requests are limited to 100 requests per minute per IP address.

## WebSocket Support

Real-time updates are available through WebSocket connections:

```
ws://localhost:8000/ws/notifications
```

## Pagination

List endpoints support pagination using `skip` and `limit` parameters.

## Filtering and Sorting

Most list endpoints support filtering and sorting through query parameters.

## SDKs and Libraries

Official SDKs are available for:
- Python
- JavaScript/TypeScript
- Java

## Support

For API support and questions, contact the development team or refer to the documentation.
