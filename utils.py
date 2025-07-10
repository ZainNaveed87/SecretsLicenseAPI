from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime, timedelta

# ====== DATABASE CONNECTION SETUP ======

# For Render deployment: Set DATABASE_URL as environment variable in Render dashboard
# For local testing: fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ====== LICENSE TABLE MODEL ======
class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    license_key = Column(String, unique=True, nullable=False)
    expiry_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)

# ====== DATABASE INITIALIZATION ======
def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized with License table.")

# ====== GET DATABASE SESSION ======
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ====== CLI INIT CHECK ======
if __name__ == "__main__":
    initialize_database()
