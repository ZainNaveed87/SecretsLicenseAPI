from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ===== DATABASE CONFIG =====
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ===== LICENSE TABLE =====
class License(Base):
    __tablename__ = "licenses"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    license_key = Column(String, unique=True, nullable=False)
    expiry_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)

# Create table if not exist
Base.metadata.create_all(bind=engine)

# ===== FASTAPI ROUTER =====
router = APIRouter()

class LicenseRequest(BaseModel):
    customer_name: str
    days_valid: int

class LicenseVerifyRequest(BaseModel):
    license_key: str

@router.post("/generate_license")
def generate_license(data: LicenseRequest):
    session = SessionLocal()
    try:
        license_key = str(uuid.uuid4())
        expiry_date = datetime.now().date() + timedelta(days=data.days_valid)

        new_license = License(
            customer_name=data.customer_name,
            license_key=license_key,
            expiry_date=expiry_date,
            is_active=True
        )
        session.add(new_license)
        session.commit()
        return {"license_key": license_key, "expiry_date": expiry_date.isoformat()}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()

@router.post("/verify_license")
def verify_license(data: LicenseVerifyRequest):
    session = SessionLocal()
    try:
        license = session.query(License).filter(License.license_key == data.license_key.strip()).first()
        if not license:
            raise HTTPException(status_code=404, detail="License not found.")

        if not license.is_active:
            return {"status": "inactive", "message": "License is inactive."}
        if datetime.now().date() > license.expiry_date:
            return {"status": "expired", "message": "License expired."}
        return {"status": "valid", "message": "License is valid."}
    finally:
        session.close()

# ✅ Duplicate route for clients using /validate
@router.post("/validate")
def validate_license(data: LicenseVerifyRequest):
    return verify_license(data)
