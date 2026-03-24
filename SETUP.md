# Campus Intelligence System - Setup Guide

## Overview

The Campus Intelligence System is an AI-powered platform designed to proactively identify and prevent student dropout and suicide risks while optimizing campus resource utilization. This guide will help you set up and deploy the system.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **npm**: 8.0 or higher
- **PostgreSQL**: 12.0 or higher
- **MongoDB**: 4.4 or higher
- **Redis**: 6.0 or higher (optional, for caching)

### Hardware Requirements
- **RAM**: Minimum 8GB, Recommended 16GB
- **Storage**: Minimum 50GB free space
- **CPU**: Multi-core processor recommended

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd campus-intelligence-system
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Database Setup
1. **PostgreSQL Setup**:
   ```bash
   # Create database
   createdb campus_intelligence
   
   # Create user (optional)
   createuser campus_user
   psql -c "ALTER USER campus_user PASSWORD 'your_password';"
   psql -c "GRANT ALL PRIVILEGES ON DATABASE campus_intelligence TO campus_user;"
   ```

2. **MongoDB Setup**:
   ```bash
   # Start MongoDB service
   mongod --dbpath /path/to/your/db
   ```

#### Environment Configuration
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your configuration:
   - Database URLs
   - Secret keys
   - Email settings
   - API keys

#### Initialize Database
```bash
cd backend
python -c "from models.database import create_tables; create_tables()"
```

### 3. Frontend Setup

#### Install Node.js Dependencies
```bash
cd frontend
npm install
```

#### Build Frontend (for production)
```bash
npm run build
```

### 4. Start the Services

#### Development Mode
1. **Start Backend**:
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend** (in separate terminal):
   ```bash
   cd frontend
   npm start
   ```

#### Production Mode
1. **Start Backend with Gunicorn**:
   ```bash
   cd backend
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

2. **Serve Frontend**:
   ```bash
   cd frontend
   serve -s build -l 3000
   ```

## Configuration

### Database Configuration
- **PostgreSQL**: Configure in `DATABASE_URL` environment variable
- **MongoDB**: Configure in `MONGODB_URL` environment variable

### ML Model Configuration
- Models are stored in `ml-models/saved_models/`
- Initial models will be created on first run
- Retrain models periodically with historical data

### Email Configuration
Configure SMTP settings in `.env` for alert notifications:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## API Documentation

Once the backend is running, access the API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Key Features

### Student Well-being Monitoring
- Risk assessment using ML algorithms
- Behavioral pattern analysis
- Academic performance tracking
- Social engagement monitoring

### Campus Resource Optimization
- Hostel room allocation optimization
- Facility utilization tracking
- Energy consumption monitoring
- Predictive maintenance scheduling

### Real-time Alerts
- Automated risk detection
- Multi-level alert system
- Staff assignment and tracking
- Intervention management

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Frontend Build Errors**:
   - Clear npm cache: `npm cache clean --force`
   - Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

3. **ML Model Loading Errors**:
   - Check `ml-models/saved_models/` directory
   - Ensure sufficient disk space
   - Verify Python ML libraries are installed

4. **Port Conflicts**:
   - Backend default: 8000
   - Frontend default: 3000
   - Change ports if conflicts occur

### Log Files
- Backend logs: `logs/campus_intelligence.log`
- Frontend logs: Browser console
- Database logs: PostgreSQL/MongoDB logs

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **Database Security**: Use strong passwords and limit access
3. **API Security**: Implement proper authentication and authorization
4. **Data Privacy**: Ensure compliance with student data protection regulations

## Performance Optimization

1. **Database Indexing**: Add indexes to frequently queried fields
2. **Caching**: Use Redis for session management and data caching
3. **Load Balancing**: Deploy multiple backend instances for high traffic
4. **CDN**: Use CDN for static assets in production

## Monitoring and Maintenance

1. **Health Checks**: Monitor `/health` endpoint
2. **Model Retraining**: Schedule periodic ML model updates
3. **Database Maintenance**: Regular backups and optimization
4. **Log Rotation**: Implement log rotation to manage disk space

## Support

For technical support:
1. Check the troubleshooting section
2. Review log files for error messages
3. Consult the API documentation
4. Contact the development team

## License

This project is licensed under the MIT License. See LICENSE file for details.
