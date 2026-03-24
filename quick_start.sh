#!/bin/bash

# Campus Intelligence System - Quick Start Script
# This script helps you quickly set up and start the system

echo "🎓 Campus Intelligence System - Quick Start"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create virtual environment for backend
echo "📦 Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Go back to root directory
cd ..

# Install Node.js dependencies
echo "📚 Installing Node.js dependencies..."
cd frontend
npm install

# Go back to root directory
cd ..

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p ml-models/saved_models
mkdir -p uploads

echo "✅ Setup completed successfully!"
echo ""
echo "🚀 To start the system:"
echo "1. Configure your database in .env file"
echo "2. Start PostgreSQL and MongoDB services"
echo "3. Run the following commands in separate terminals:"
echo ""
echo "   Terminal 1 (Backend):"
echo "   cd backend && source venv/bin/activate && python main.py"
echo ""
echo "   Terminal 2 (Frontend):"
echo "   cd frontend && npm start"
echo ""
echo "🌐 Access the application at: http://localhost:3000"
echo "📚 API Documentation: http://localhost:8000/docs"
