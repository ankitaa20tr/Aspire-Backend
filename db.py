#  python3 -m db
import sys
import os
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import UUID
from app.database.database import Base, engine
from app.database.models import User, SavedStrategy, Conversation, Message
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Create all database tables defined in the models."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        
        # List the tables that were created
        table_names = Base.metadata.tables.keys()
        logger.info(f"Created tables: {', '.join(table_names)}")
        return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        logger.error("❌ DATABASE_URL environment variable is not set!")
        logger.info("Please make sure your .env file exists and contains DATABASE_URL")
        sys.exit(1)
    
    success = init_db()
    if success:
        logger.info("Database initialization complete! You can now start the server.")
    else:
        logger.error("Failed to initialize the database. Please check the error messages above.")
        sys.exit(1)



# work --> 
# Create your database tables
# Sync  Python model definitions to  DB schema