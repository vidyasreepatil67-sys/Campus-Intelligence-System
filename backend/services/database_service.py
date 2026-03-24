from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import os
import asyncio

from models.database import Base, get_db

class DatabaseService:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://user:password@localhost/campus_intelligence"
        )
    
    async def initialize(self):
        """Initialize database connection and create tables"""
        try:
            # Create database engine
            self.engine = create_engine(self.database_url)
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=self.engine
            )
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            print("Database initialized successfully")
            
        except SQLAlchemyError as e:
            print(f"Database initialization error: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            print("Database connections closed")
    
    def get_session(self):
        """Get database session"""
        if self.SessionLocal:
            return self.SessionLocal()
        raise RuntimeError("Database not initialized")
    
    async def health_check(self) -> dict:
        """Check database health"""
        try:
            session = self.get_session()
            # Simple query to test connection
            session.execute("SELECT 1")
            session.close()
            return {"status": "healthy", "message": "Database connection successful"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
    
    async def backup_database(self, backup_path: Optional[str] = None):
        """Create database backup"""
        # This would implement database-specific backup logic
        # For PostgreSQL, you might use pg_dump
        print(f"Database backup requested to: {backup_path}")
        return {"status": "backup_initiated", "path": backup_path}
    
    async def restore_database(self, backup_path: str):
        """Restore database from backup"""
        # This would implement database-specific restore logic
        print(f"Database restore requested from: {backup_path}")
        return {"status": "restore_initiated", "path": backup_path}
    
    async def migrate_database(self):
        """Run database migrations"""
        # This would implement migration logic using Alembic or similar
        print("Database migration initiated")
        return {"status": "migration_completed"}
    
    def get_connection_info(self) -> dict:
        """Get database connection information"""
        return {
            "database_url": self.database_url.split("@")[1] if "@" in self.database_url else "Unknown",
            "driver": self.engine.driver if self.engine else "Not connected",
            "pool_size": self.engine.pool.size() if self.engine else 0
        }
