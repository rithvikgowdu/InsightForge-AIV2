from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import utc_now, generate_uuid

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.issue import CollectedIssue
    from app.models.cluster import AnalysisCluster
    from app.models.opportunity import ProductOpportunity


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), default="github", nullable=False)
    repo_owner: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    repo_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    repo_url: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Status: QUEUED, RUNNING, COMPLETED, FAILED
    status: Mapped[str] = mapped_column(String(30), default="QUEUED", nullable=False, index=True)
    current_step: Mapped[str] = mapped_column(String(100), default="Queued for analysis", nullable=False)
    progress_pct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    total_issues_requested: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    total_issues_collected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_clusters: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_opportunities: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_fallback: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    analysis_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="analyses")
    issues: Mapped[List["CollectedIssue"]] = relationship(
        "CollectedIssue", back_populates="analysis", cascade="all, delete-orphan"
    )
    clusters: Mapped[List["AnalysisCluster"]] = relationship(
        "AnalysisCluster", back_populates="analysis", cascade="all, delete-orphan", order_by="desc(AnalysisCluster.size)"
    )
    opportunities: Mapped[List["ProductOpportunity"]] = relationship(
        "ProductOpportunity",
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="desc(ProductOpportunity.confidence_score)",
    )

    def __repr__(self) -> str:
        return f"<AnalysisRun(id={self.id}, repo='{self.repo_owner}/{self.repo_name}', status='{self.status}')>"

