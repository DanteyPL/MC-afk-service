from database import Base, engine
from models.user import User
# Import other models here as needed
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def init_db():
    print("Starting database initialization...")
    print(f"Creating tables for: {Base.metadata.tables.keys()}")
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully")

if __name__ == "__main__":
    init_db()
