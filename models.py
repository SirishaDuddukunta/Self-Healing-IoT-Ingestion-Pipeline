from pydantic import BaseModel, Field
from typing import List, Dict, Any

class TelemetryData(BaseModel):
    sensor_id: str = Field(..., example="temp_sensor_01")
    timestamp: float = Field(..., example=1712345678.0)
    value: float = Field(..., example=23.5)
    metadata: Dict[str, Any] = {}

class IngestionResponse(BaseModel):
    status: str
    confidence_score: float
    data: TelemetryData
    logs: List[str]