from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class OpportunityResponse(BaseModel):
    id: str
    analysis_id: str
    cluster_id: Optional[str] = None
    title: str
    problem_statement: str
    business_opportunity: str
    proposed_solution: str
    target_customer_segment: str
    suggested_mvp_features: List[str] = Field(default_factory=list)
    market_potential: str
    confidence_score: float
    confidence_explanation: str
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    supporting_doc_count: int
    is_fallback: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

