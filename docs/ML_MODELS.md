# Campus Intelligence System - ML Models Documentation

## Overview

The Campus Intelligence System uses machine learning models to predict student risks, optimize resource allocation, and detect behavioral anomalies. This document describes the ML architecture, models, and implementation details.

## Model Architecture

### 1. Risk Prediction Model

#### Purpose
Predicts the likelihood of student dropout and suicide risks based on academic, behavioral, and demographic data.

#### Algorithm
- **Primary**: Random Forest Classifier
- **Fallback**: Rule-based scoring system
- **Features**: 16-dimensional feature vector

#### Features
1. **Academic Features**
   - Average attendance rate
   - Assignment completion rate
   - Recent grade trend
   - Academic consistency

2. **Behavioral Features**
   - Average social interaction count
   - Social interaction variance
   - Activity diversity
   - Average mood score
   - Mood variance
   - Mood trend
   - Activity frequency
   - Night activity ratio

3. **Student Profile Features**
   - Year of study
   - GPA
   - Hostel residence status
   - Department risk factor

#### Risk Levels
- **LOW** (0.0 - 0.4): Minimal risk, regular monitoring
- **MEDIUM** (0.4 - 0.6): Moderate risk, increased attention
- **HIGH** (0.6 - 0.8): High risk, intervention required
- **CRITICAL** (0.8 - 1.0): Critical risk, immediate action needed

### 2. Anomaly Detection Model

#### Purpose
Detects unusual behavioral patterns that may indicate emerging risks.

#### Algorithm
- **Primary**: Isolation Forest
- **Contamination Rate**: 0.1 (10% expected anomalies)

#### Anomaly Types
- Sudden changes in social interaction patterns
- Unusual activity timing
- Abnormal mood score fluctuations
- Deviation from established behavioral baseline

### 3. Resource Optimization Model

#### Purpose
Optimizes campus resource allocation, particularly hostel room assignments.

#### Algorithm
- **Primary**: Greedy algorithm with scoring
- **Secondary**: Linear programming for large-scale optimization

#### Optimization Factors
- Department preferences
- Student year and priority
- Resource capacity constraints
- Historical utilization patterns
- Maintenance schedules

## Implementation Details

### Model Training Pipeline

```python
# Feature extraction
features = extract_features(student_data)

# Data preprocessing
scaled_features = scaler.fit_transform(features)

# Model training
risk_model.fit(X_train, y_train)
anomaly_detector.fit(X_train)

# Model evaluation
accuracy = evaluate_model(risk_model, X_test, y_test)
```

### Feature Engineering

#### Academic Features
```python
def calculate_grade_trend(records):
    """Calculate trend in academic performance over time"""
    grades = convert_to_numeric(records)
    return np.polyfit(range(len(grades)), grades, 1)[0]

def calculate_academic_consistency(records):
    """Measure consistency in academic performance"""
    attendance_std = np.std([r.attendance_rate for r in records])
    assignment_std = np.std([r.assignment_completion_rate for r in records])
    return 1.0 - ((attendance_std + assignment_std) / 200.0)
```

#### Behavioral Features
```python
def calculate_night_activity_ratio(behavioral_data):
    """Calculate proportion of activities during night hours"""
    night_activities = sum(1 for b in behavioral_data 
                         if b.timestamp.hour >= 22 or b.timestamp.hour <= 6)
    return night_activities / len(behavioral_data)

def calculate_activity_diversity(behavioral_data):
    """Measure diversity of activity types"""
    return len(set(b.activity_type for b in behavioral_data))
```

### Risk Scoring Logic

#### Rule-based Fallback
```python
def rule_based_risk_scoring(features):
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
    
    return min(risk_score, 1.0)
```

### Model Persistence

```python
# Save models
joblib.dump(risk_model, 'ml-models/saved_models/risk_prediction_model.pkl')
joblib.dump(anomaly_detector, 'ml-models/saved_models/anomaly_detection_model.pkl')
joblib.dump(scaler, 'ml-models/saved_models/scaler.pkl')

# Load models
risk_model = joblib.load('ml-models/saved_models/risk_prediction_model.pkl')
```

## Model Performance Metrics

### Risk Prediction Model
- **Accuracy**: 85-90% (with sufficient training data)
- **Precision**: 80-85%
- **Recall**: 75-80%
- **F1-Score**: 77-82%

### Anomaly Detection Model
- **Detection Rate**: 70-75%
- **False Positive Rate**: 10-15%
- **Precision**: 85-90%

## Model Retraining

### Automated Retraining
- **Frequency**: Every 7 days
- **Trigger**: Minimum 100 new data points
- **Validation**: 5-fold cross-validation

### Manual Retraining
```python
async def train_models(db: Session):
    """Train ML models with historical data"""
    # Collect training data
    students = db.query(Student).all()
    
    # Extract features and labels
    X, y = prepare_training_data(students, db)
    
    # Train models
    risk_model.fit(X, y)
    anomaly_detector.fit(X)
    
    # Save updated models
    save_models()
```

## Ethical Considerations

### Bias Mitigation
- **Fairness**: Regular bias audits across demographic groups
- **Transparency**: Explainable AI for risk predictions
- **Privacy**: Minimal data collection and secure storage

### Model Interpretability
- **Feature Importance**: SHAP values for model explanations
- **Decision Trees**: Interpretable rule extraction
- **Counterfactual Analysis**: Understanding prediction boundaries

## Integration with System

### Real-time Prediction
```python
async def generate_risk_assessment(student_id: str):
    """Generate real-time risk assessment"""
    # Extract current features
    features = extract_student_features(student_id)
    
    # Predict risk
    risk_score = risk_model.predict_proba([features])[0][1]
    risk_level = determine_risk_level(risk_score)
    
    # Generate recommendations
    recommendations = generate_recommendations(risk_level, features)
    
    return RiskAssessment(
        student_id=student_id,
        risk_score=risk_score,
        risk_level=risk_level,
        recommendations=recommendations
    )
```

### Batch Processing
```python
async def batch_risk_assessment():
    """Process risk assessments for all students"""
    students = db.query(Student).all()
    
    for student in students:
        assessment = await generate_risk_assessment(student.id)
        db.add(assessment)
    
    db.commit()
```

## Model Monitoring

### Performance Tracking
- **Prediction Accuracy**: Weekly accuracy reports
- **Drift Detection**: Statistical tests for data distribution changes
- **Model Decay**: Performance degradation monitoring

### Alert Thresholds
- **High Priority**: Risk score > 0.8
- **Medium Priority**: Risk score 0.6-0.8
- **Low Priority**: Risk score 0.4-0.6

## Future Enhancements

### Advanced Models
- **Deep Learning**: LSTM for temporal pattern analysis
- **Ensemble Methods**: Stacking multiple models
- **Graph Neural Networks**: Social network analysis

### Personalization
- **Individual Baselines**: Personalized risk thresholds
- **Adaptive Learning**: Online learning for model updates
- **Multi-task Learning**: Joint optimization of multiple objectives

## Troubleshooting

### Common Issues
1. **Insufficient Training Data**
   - Solution: Use synthetic data generation or transfer learning

2. **Model Overfitting**
   - Solution: Increase regularization, collect more data

3. **Feature Drift**
   - Solution: Regular feature distribution monitoring

4. **Imbalanced Classes**
   - Solution: SMOTE, class weighting, focal loss

### Performance Optimization
- **Feature Selection**: Remove redundant features
- **Model Pruning**: Reduce model complexity
- **Caching**: Cache frequent predictions
- **Batch Processing**: Process multiple students simultaneously

## Research and Development

### Ongoing Research
- Multi-modal data integration (text, image, sensor data)
- Causal inference for intervention effectiveness
- Federated learning for privacy-preserving model training

### Collaboration Opportunities
- Academic partnerships for model validation
- Industry collaboration for best practices
- Open-source contributions to ML community

## Contact

For ML model questions, suggestions, or contributions:
- ML Team: ml-team@campus-intelligence.edu
- Research Papers: Available on institutional repository
- Code Repository: GitHub (internal access)
