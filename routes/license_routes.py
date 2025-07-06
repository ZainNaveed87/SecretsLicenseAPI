from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta
from utils import get_connection

router = APIRouter()

class LicenseRequest(BaseModel):
    customer_name: str
    days_valid: int

class LicenseVerifyRequest(BaseModel):
    license_key: str

@router.post("/generate_license")
def generate_license(data: LicenseRequest):
    conn = get_connection()
    cursor = conn.cursor()

    license_key = str(uuid.uuid4())
    expiry_date = (datetime.now() + timedelta(days=data.days_valid)).strftime("%Y-%m-%d")

    try:
        cursor.execute(
            "INSERT INTO licenses (customer_name, license_key, expiry_date, is_active) VALUES (?, ?, ?, ?)",
            (data.customer_name, license_key, expiry_date, 1)  # 1 means active
        )
        conn.commit()
        return {"license_key": license_key, "expiry_date": expiry_date}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.post("/verify_license")
def verify_license(data: LicenseVerifyRequest):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT expiry_date, is_active FROM licenses WHERE license_key = ?",
        (data.license_key.strip(),)  # Ensure no whitespace issues
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        expiry_date, is_active = result
        expiry_date_obj = datetime.strptime(expiry_date, "%Y-%m-%d")
        if not is_active:
            return {"status": "inactive", "message": "License is inactive."}
        if datetime.now() > expiry_date_obj:
            return {"status": "expired", "message": "License expired."}
        return {"status": "valid", "message": "License is valid."}
    else:
        raise HTTPException(status_code=404, detail="License not found.")

# ✅ Duplicate route for clients using /validate
@router.post("/validate")
def validate_license(data: LicenseVerifyRequest):
    return verify_license(data)
