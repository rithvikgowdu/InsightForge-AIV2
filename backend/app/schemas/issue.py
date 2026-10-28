from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class IssueResponse(BaseModel):
    id: str
    source_id: str
    issue_number: int
    title: str
    body: Optional[str] = None
    clean_text: Optional[str] = None
    url: str
    state: str
    author: Optional[str] = None
    labels: Optional[List[str]] = None
    comments_count: int
    source_created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

