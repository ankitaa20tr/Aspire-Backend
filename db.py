
from app.database.database import Base, engine
from app.database.models import User, SavedStrategy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully!")

if __name__ == "__main__":
    init_db()


# work --> 
# Create your database tables
# Sync  Python model definitions to  DB schema