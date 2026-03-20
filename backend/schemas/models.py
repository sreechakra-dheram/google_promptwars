from pydantic import BaseModel
from typing import List, Optional

class AccidentReport(BaseModel):
    incident_type: str
    vehicle_count: int
    severity_score: int
    required_units: List[str]
    pii_detected: bool
    accident_detected: bool
    latitude: float
    longitude: float

class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[AccidentReport]
    error: Optional[str] = None
    frames_processed: int = 0
