from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Indicator(BaseModel):
    type: str # e.g., 'ip', 'email', 'crypto_wallet', 'domain', 'hash'
    value: str
    metadata: Optional[dict] = {}

class ThreatLog(BaseModel):
    url: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    risk_score: int = 0
    threat_category: str
    confidence: float
    extracted_indicators: List[Indicator] = []
    content_snippet: str

class Alert(BaseModel):
    threat_log_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str # 'HIGH', 'CRITICAL'
    message: str
    read: bool = False
