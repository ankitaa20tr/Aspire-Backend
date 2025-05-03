# source venvAnkitaTiwari/bin/activate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
from loguru import logger
Base = declarative_base()
load_dotenv()

# check
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("Oops! DATABASE_URL environment variable not set!")
    raise ValueError("DATABASE_URL environment variable not set!")


engine = create_engine(DATABASE_URL)

# Create session factory to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print("database wowowww")

