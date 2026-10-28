from datetime import datetime
from typing import Dict
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    timestamp: datetime


class ReadyResponse(BaseModel):
    status: str
    version: str
    database: bool
    ai_pipeline: bool
    details: Dict[str, str]

