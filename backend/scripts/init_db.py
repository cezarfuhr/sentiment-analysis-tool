"""
Database initialization script
Creates all tables and optionally adds sample data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import engine, Base, SessionLocal
from app.models.database import User, APIKey, Analysis, TrendData
from app.services.auth_service import auth_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully!")


def create_sample_data():
    """Create sample user and API key for testing"""
    db = SessionLocal()

    try:
        # Check if sample user already exists
        existing_user = db.query(User).filter(User.username == "demo").first()
        if existing_user:
            logger.info("Sample user already exists")
            return

        # Create sample user
        logger.info("Creating sample user...")
        user = auth_service.create_user(
            db,
            username="demo",
            email="demo@example.com",
            password="demo123"
        )
        logger.info(f"Sample user created: username='demo', password='demo123'")

        # Create sample API key
        api_key = auth_service.create_api_key(
            db,
            user_id=user.id,
            name="Demo API Key",
            rate_limit=1000
        )
        logger.info(f"Sample API key created: {api_key.key}")

    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()

    # Optionally create sample data
    if "--with-samples" in sys.argv:
        create_sample_data()

    logger.info("Database initialization complete!")
