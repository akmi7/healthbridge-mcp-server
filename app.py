import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel

app = FastAPI(title="HealthBridge Lab Results MCP Server")

# Secure Mock Database - HIPAA-safe (No Patient Names stored here)
LAB_RESULTS_DB = {
    "PT-1092": [
        {"date": "2026-05-12", "test": "HbA1c", "result": "5.6%", "status": "Normal"},
        {"date": "2026-05-12", "test": "Fasting Plasma Glucose", "result": "94 mg/dL", "status": "Normal"}
    ],
    "PT-4401": [
        {"date": "2026-04-18", "test": "Lipid Panel - Total Cholesterol", "result": "220 mg/dL", "status": "High"},
        {"date": "2026-04-18", "test": "Triglycerides", "result": "160 mg/dL", "status": "Borderline High"}
    ]
}

# Secure verification token matching Salesforce Named Credentials
API_SECRET_KEY = os.getenv("HEALTHBRIDGE_MCP_KEY", "HB-Secure-Secret-2026")

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token structure")
    token = authorization.split(" ")[1]
    if token != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized access to HealthBridge records")
    return token

class LabResultSchema(BaseModel):
    date: str
    test: str
    result: str
    status: str

@app.get("/tools/get_lab_results", response_model=List[LabResultSchema])
def get_lab_results(patient_id: str, token: str = Depends(verify_token)):
    if patient_id not in LAB_RESULTS_DB:
        raise HTTPException(status_code=404, detail="Requested Patient ID records not found")
    return LAB_RESULTS_DB[patient_id]
