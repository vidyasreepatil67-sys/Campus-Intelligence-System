from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

from models.database import Student, AcademicRecord, BehavioralData, RiskAssessment
from models.schemas import RiskAssessment as RiskAssessmentSchema, RiskLevel

class MLService:
    def __init__(self):
        self.risk_model = None
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        self.model_path = "ml-models/saved_models"
        os.makedirs(self.model_path, exist_ok=True)
    
    async def load_models(self):
        """Load pre-trained ML models"""
        try:
            # Load risk prediction model
            risk_model_path = os.path.join(self.model_path, "risk_prediction_model.pkl")
            if os.path.exists(risk_model_path):
                self.risk_model = joblib.load(risk_model_path)
            
            # Load anomaly detection model
            anomaly_model_path = os.path.join(self.model_path, "anomaly_detection_model.pkl")
            if os.path.exists(anomaly_model_path):
                self.anomaly_detector = joblib.load(anomaly_model_path)
            
            # Load scaler
            scaler_path = os.path.join(self.model_path, "scaler.pkl")
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                
        except Exception as e:
            print(f"Error loading models: {e}")
            # Initialize new models if loading fails
            self.risk_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
    
    async def generate_risk_assessment(self, db: Session, student_id: str) -> RiskAssessmentSchema:
        """Generate risk assessment for a student using ML models"""
        # Get student data
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError("Student not found")
        
        # Get academic records
        academic_records = db.query(AcademicRecord)\
                             .filter(AcademicRecord.student_id == student_id)\
                             .order_by(AcademicRecord.last_updated.desc())\
                             .limit(10).all()
        
        # Get behavioral data (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        behavioral_data = db.query(BehavioralData)\
                            .filter(
                                and_(
                                    BehavioralData.student_id == student_id,
                                    BehavioralData.timestamp >= start_date,
                                    BehavioralData.timestamp <= end_date
                                )
                            ).all()
        
        # Extract features
        features = self._extract_features(student, academic_records, behavioral_data)
        
        # Predict risk
        risk_score, risk_level, risk_factors = await self._predict_risk(features)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, risk_factors, features)
        
        # Create risk assessment
        import uuid
        assessment = RiskAssessmentSchema(
            id=str(uuid.uuid4()),
            student_id=student_id,
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=risk_factors,
            assessment_date=datetime.utcnow(),
            next_review_date=datetime.utcnow() + timedelta(days=30),
            recommendations=recommendations
        )
        
        # Save to database
        db_assessment = RiskAssessment(
            id=assessment.id,
            student_id=assessment.student_id,
            risk_level=assessment.risk_level,
            risk_score=assessment.risk_score,
            risk_factors=json.dumps(assessment.risk_factors),
            assessment_date=assessment.assessment_date,
            next_review_date=assessment.next_review_date,
            recommendations=json.dumps(assessment.recommendations)
        )
        
        db.add(db_assessment)
        db.commit()
        
        return assessment
    
    def _extract_features(self, student, academic_records, behavioral_data) -> Dict[str, float]:
        """Extract features from student data for ML prediction"""
        features = {}
        
        # Academic features
        if academic_records:
            features['avg_attendance'] = np.mean([r.attendance_rate for r in academic_records])
            features['avg_assignment_completion'] = np.mean([r.assignment_completion_rate for r in academic_records])
            features['recent_grade_trend'] = self._calculate_grade_trend(academic_records)
            features['academic_consistency'] = self._calculate_academic_consistency(academic_records)
        else:
            features['avg_attendance'] = 0.0
            features['avg_assignment_completion'] = 0.0
            features['recent_grade_trend'] = 0.0
            features['academic_consistency'] = 0.0
        
        # Behavioral features
        if behavioral_data:
            features['avg_social_interaction'] = np.mean([b.social_interaction_count for b in behavioral_data])
            features['social_interaction_variance'] = np.var([b.social_interaction_count for b in behavioral_data])
            features['activity_diversity'] = len(set(b.activity_type for b in behavioral_data))
            
            mood_scores = [b.mood_score for b in behavioral_data if b.mood_score is not None]
            if mood_scores:
                features['avg_mood_score'] = np.mean(mood_scores)
                features['mood_variance'] = np.var(mood_scores)
                features['mood_trend'] = self._calculate_mood_trend(behavioral_data)
            else:
                features['avg_mood_score'] = 5.0  # Neutral mood
                features['mood_variance'] = 0.0
                features['mood_trend'] = 0.0
                
            features['activity_frequency'] = len(behavioral_data) / 30.0  # Activities per day
            features['night_activity_ratio'] = self._calculate_night_activity_ratio(behavioral_data)
        else:
            features['avg_social_interaction'] = 0.0
            features['social_interaction_variance'] = 0.0
            features['activity_diversity'] = 0.0
            features['avg_mood_score'] = 5.0
            features['mood_variance'] = 0.0
            features['mood_trend'] = 0.0
            features['activity_frequency'] = 0.0
            features['night_activity_ratio'] = 0.0
        
        # Student profile features
        features['year'] = float(student.year)
        features['gpa'] = float(student.gpa) if student.gpa else 0.0
        features['has_hostel'] = 1.0 if student.hostel_room else 0.0
        
        # Department risk factor (based on historical data)
        dept_risk_map = {
            'Engineering': 0.3,
            'Medicine': 0.4,
            'Arts': 0.2,
            'Science': 0.25,
            'Business': 0.15
        }
        features['department_risk'] = dept_risk_map.get(student.department, 0.2)
        
        return features
    
    def _calculate_grade_trend(self, academic_records) -> float:
        """Calculate grade trend over time"""
        if len(academic_records) < 2:
            return 0.0
        
        # Convert grades to numeric values (simplified)
        grade_map = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
        numeric_grades = []
        
        for record in sorted(academic_records, key=lambda x: x.last_updated):
            if record.grade and record.grade in grade_map:
                numeric_grades.append(grade_map[record.grade])
        
        if len(numeric_grades) < 2:
            return 0.0
        
        # Calculate trend (positive = improving, negative = declining)
        trend = np.polyfit(range(len(numeric_grades)), numeric_grades, 1)[0]
        return float(trend)
    
    def _calculate_academic_consistency(self, academic_records) -> float:
        """Calculate academic performance consistency"""
        if not academic_records:
            return 0.0
        
        attendance_rates = [r.attendance_rate for r in academic_records]
        assignment_rates = [r.assignment_completion_rate for r in academic_records]
        
        # Lower variance = higher consistency
        attendance_consistency = 1.0 - (np.std(attendance_rates) / 100.0) if attendance_rates else 0.0
        assignment_consistency = 1.0 - (np.std(assignment_rates) / 100.0) if assignment_rates else 0.0
        
        return (attendance_consistency + assignment_consistency) / 2.0
    
    def _calculate_mood_trend(self, behavioral_data) -> float:
        """Calculate mood trend over time"""
        mood_data = [(b.timestamp, b.mood_score) for b in behavioral_data if b.mood_score is not None]
        
        if len(mood_data) < 2:
            return 0.0
        
        mood_data.sort(key=lambda x: x[0])
        moods = [score for _, score in mood_data]
        
        trend = np.polyfit(range(len(moods)), moods, 1)[0]
        return float(trend)
    
    def _calculate_night_activity_ratio(self, behavioral_data) -> float:
        """Calculate ratio of activities during night hours (10 PM - 6 AM)"""
        night_activities = sum(1 for b in behavioral_data if b.timestamp.hour >= 22 or b.timestamp.hour <= 6)
        total_activities = len(behavioral_data)
        
        return night_activities / total_activities if total_activities > 0 else 0.0
    
    async def _predict_risk(self, features: Dict[str, float]) -> tuple[float, RiskLevel, List[str]]:
        """Predict risk using ML models"""
        # Prepare feature vector
        feature_names = [
            'avg_attendance', 'avg_assignment_completion', 'recent_grade_trend', 'academic_consistency',
            'avg_social_interaction', 'social_interaction_variance', 'activity_diversity',
            'avg_mood_score', 'mood_variance', 'mood_trend', 'activity_frequency', 'night_activity_ratio',
            'year', 'gpa', 'has_hostel', 'department_risk'
        ]
        
        feature_vector = np.array([features.get(name, 0.0) for name in feature_names]).reshape(1, -1)
        
        # Scale features
        if hasattr(self.scaler, 'mean_'):
            feature_vector = self.scaler.transform(feature_vector)
        
        # Predict risk score
        if self.risk_model and hasattr(self.risk_model, 'predict_proba'):
            risk_proba = self.risk_model.predict_proba(feature_vector)[0]
            risk_score = risk_proba[1]  # Probability of being at risk
        else:
            # Fallback to rule-based scoring
            risk_score = self._rule_based_risk_scoring(features)
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(features, risk_score)
        
        return float(risk_score), risk_level, risk_factors
    
    def _rule_based_risk_scoring(self, features: Dict[str, float]) -> float:
        """Fallback rule-based risk scoring"""
        risk_score = 0.0
        
        # Academic factors
        if features['avg_attendance'] < 70:
            risk_score += 0.2
        if features['avg_assignment_completion'] < 60:
            risk_score += 0.2
        if features['recent_grade_trend'] < -0.1:
            risk_score += 0.15
        
        # Behavioral factors
        if features['avg_social_interaction'] < 2:
            risk_score += 0.15
        if features['avg_mood_score'] < 4:
            risk_score += 0.15
        if features['night_activity_ratio'] > 0.3:
            risk_score += 0.1
        
        # Personal factors
        if features['gpa'] < 2.0:
            risk_score += 0.1
        if features['year'] >= 3:  # Higher year students
            risk_score += 0.05
        
        return min(risk_score, 1.0)
    
    def _identify_risk_factors(self, features: Dict[str, float], risk_score: float) -> List[str]:
        """Identify specific risk factors based on features"""
        risk_factors = []
        
        if features['avg_attendance'] < 70:
            risk_factors.append("Low attendance rate")
        if features['avg_assignment_completion'] < 60:
            risk_factors.append("Poor assignment completion")
        if features['recent_grade_trend'] < -0.1:
            risk_factors.append("Declining academic performance")
        if features['avg_social_interaction'] < 2:
            risk_factors.append("Social isolation")
        if features['avg_mood_score'] < 4:
            risk_factors.append("Low mood indicators")
        if features['night_activity_ratio'] > 0.3:
            risk_factors.append("Irregular sleep patterns")
        if features['gpa'] < 2.0:
            risk_factors.append("Low academic performance")
        
        if not risk_factors and risk_score > 0.5:
            risk_factors.append("General risk indicators detected")
        
        return risk_factors
    
    def _generate_recommendations(self, risk_level: RiskLevel, risk_factors: List[str], features: Dict[str, float]) -> List[str]:
        """Generate personalized recommendations based on risk assessment"""
        recommendations = []
        
        # Academic recommendations
        if "Low attendance rate" in risk_factors:
            recommendations.append("Schedule academic counseling to address attendance concerns")
        if "Poor assignment completion" in risk_factors:
            recommendations.append("Provide time management and study skills support")
        if "Declining academic performance" in risk_factors:
            recommendations.append("Arrange tutoring and academic support services")
        
        # Social/behavioral recommendations
        if "Social isolation" in risk_factors:
            recommendations.append("Encourage participation in campus activities and student organizations")
        if "Low mood indicators" in risk_factors:
            recommendations.append("Schedule counseling session with mental health professional")
        if "Irregular sleep patterns" in risk_factors:
            recommendations.append("Provide wellness education on sleep hygiene and routine")
        
        # General recommendations based on risk level
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Immediate intervention required - assign case manager")
            recommendations.append("Schedule weekly check-ins with counselor")
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append("Monthly monitoring and follow-up recommended")
            recommendations.append("Consider peer mentorship program")
        
        # Department-specific recommendations
        if features['department_risk'] > 0.3:
            recommendations.append("Connect with department-specific support resources")
        
        return recommendations
    
    async def detect_anomalies(self, db: Session, student_id: str) -> List[Dict[str, Any]]:
        """Detect anomalous behavior patterns"""
        # Get recent behavioral data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        behavioral_data = db.query(BehavioralData)\
                            .filter(
                                and_(
                                    BehavioralData.student_id == student_id,
                                    BehavioralData.timestamp >= start_date,
                                    BehavioralData.timestamp <= end_date
                                )
                            ).all()
        
        if not behavioral_data:
            return []
        
        # Extract features for anomaly detection
        features = []
        for data in behavioral_data:
            feature_vector = [
                data.social_interaction_count,
                data.mood_score or 5.0,
                data.duration_minutes,
                data.timestamp.hour,
                1 if data.timestamp.hour >= 22 or data.timestamp.hour <= 6 else 0
            ]
            features.append(feature_vector)
        
        # Detect anomalies
        if self.anomaly_detector and len(features) > 0:
            anomalies = self.anomaly_detector.predict(features)
            anomaly_indices = np.where(anomalies == -1)[0]
            
            anomaly_details = []
            for idx in anomaly_indices:
                data = behavioral_data[idx]
                anomaly_details.append({
                    "timestamp": data.timestamp,
                    "activity_type": data.activity_type,
                    "anomaly_type": "behavioral_pattern",
                    "description": f"Unusual {data.activity_type} activity detected"
                })
            
            return anomaly_details
        
        return []
    
    async def train_models(self, db: Session):
        """Train ML models with historical data"""
        # This would be implemented with historical data
        # For now, we'll create a simple training process
        try:
            # Get training data
            students = db.query(Student).all()
            
            if len(students) < 10:
                print("Insufficient data for training models")
                return
            
            # Extract features and labels for all students
            X = []
            y = []
            
            for student in students:
                # Get student data
                academic_records = db.query(AcademicRecord)\
                                     .filter(AcademicRecord.student_id == student.id)\
                                     .all()
                
                behavioral_data = db.query(BehavioralData)\
                                    .filter(BehavioralData.student_id == student.id)\
                                    .all()
                
                # Extract features
                features = self._extract_features(student, academic_records, behavioral_data)
                feature_names = [
                    'avg_attendance', 'avg_assignment_completion', 'recent_grade_trend', 'academic_consistency',
                    'avg_social_interaction', 'social_interaction_variance', 'activity_diversity',
                    'avg_mood_score', 'mood_variance', 'mood_trend', 'activity_frequency', 'night_activity_ratio',
                    'year', 'gpa', 'has_hostel', 'department_risk'
                ]
                
                feature_vector = [features.get(name, 0.0) for name in feature_names]
                X.append(feature_vector)
                
                # Create label based on existing risk assessments
                latest_risk = db.query(RiskAssessment)\
                               .filter(RiskAssessment.student_id == student.id)\
                               .order_by(RiskAssessment.assessment_date.desc())\
                               .first()
                
                if latest_risk:
                    label = 1 if latest_risk.risk_level in ['HIGH', 'CRITICAL'] else 0
                else:
                    # Default label based on heuristics
                    label = 1 if features.get('avg_attendance', 0) < 70 else 0
                
                y.append(label)
            
            if len(X) > 0:
                X = np.array(X)
                y = np.array(y)
                
                # Scale features
                X_scaled = self.scaler.fit_transform(X)
                
                # Train risk prediction model
                self.risk_model.fit(X_scaled, y)
                
                # Train anomaly detection model
                self.anomaly_detector.fit(X_scaled)
                
                # Save models
                joblib.dump(self.risk_model, os.path.join(self.model_path, "risk_prediction_model.pkl"))
                joblib.dump(self.anomaly_detector, os.path.join(self.model_path, "anomaly_detection_model.pkl"))
                joblib.dump(self.scaler, os.path.join(self.model_path, "scaler.pkl"))
                
                print(f"Models trained successfully with {len(X)} samples")
        
        except Exception as e:
            print(f"Error training models: {e}")
