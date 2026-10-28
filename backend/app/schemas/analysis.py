from datetime import datetime
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas.cluster import ClusterResponse
from app.schemas.issue import IssueResponse
from app.schemas.opportunity import OpportunityResponse


class AnalysisCreate(BaseModel):
    repo_owner: Optional[str] = None
    repo_name: Optional[str] = None
    repo_url: Optional[str] = None
    issue_limit: int = Field(default=50, ge=5, le=150)
    include_closed: bool = True

    @model_validator(mode="after")
    def parse_and_validate_repo(self) -> "AnalysisCreate":
        # If repo_url is provided, extract owner and name
        if self.repo_url and (not self.repo_owner or not self.repo_name):
            url = self.repo_url.strip()
            # Handle forms like:
            # https://github.com/owner/repo
            # github.com/owner/repo
            # owner/repo
            match = re.search(r"(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git|/)?$", url)
            if match:
                self.repo_owner = match.group(1).strip()
                self.repo_name = match.group(2).strip()
            elif "/" in url and not url.startswith("http"):
                parts = url.split("/")
                if len(parts) == 2 and parts[0] and parts[1]:
                    self.repo_owner = parts[0].strip()
                    self.repo_name = parts[1].strip()

        if not self.repo_owner or not self.repo_name:
            raise ValueError("Both repository owner and repository name are required (or a valid GitHub URL).")

        # Basic sanitation
        self.repo_owner = self.repo_owner.strip().replace("@", "")
        self.repo_name = self.repo_name.strip()
        
        # Build canonical repo_url
        self.repo_url = f"https://github.com/{self.repo_owner}/{self.repo_name}"
        return self


class AnalysisStatusResponse(BaseModel):
    id: str
    status: str
    current_step: str
    progress_pct: int
    total_issues_requested: int
    total_issues_collected: int
    total_clusters: int
    total_opportunities: int
    error_message: Optional[str] = None
    is_fallback: bool
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisResponse(BaseModel):
    id: str
    repo_owner: str
    repo_name: str
    repo_url: str
    status: str
    current_step: str
    progress_pct: int
    total_issues_requested: int
    total_issues_collected: int
    total_clusters: int
    total_opportunities: int
    error_message: Optional[str] = None
    is_fallback: bool
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisDetailResponse(AnalysisResponse):
    clusters: List[ClusterResponse] = Field(default_factory=list)
    opportunities: List[OpportunityResponse] = Field(default_factory=list)
    sample_issues: List[IssueResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AnalysisHistoryItem(BaseModel):
    id: str
    repo_owner: str
    repo_name: str
    repo_url: str
    status: str
    current_step: str
    progress_pct: int
    total_issues_collected: int
    total_clusters: int
    total_opportunities: int
    is_fallback: bool
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

