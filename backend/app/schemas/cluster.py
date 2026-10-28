from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict


class ClusterResponse(BaseModel):
    id: str
    analysis_id: str
    cluster_label: int
    title: str
    summary: str
    size: int
    recurring_themes: Optional[List[str]] = None
    sample_issue_ids: Optional[List[Any]] = None

    model_config = ConfigDict(from_attributes=True)

