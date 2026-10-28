from datetime import datetime
from typing import Any, List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import utc_now, generate_uuid

if TYPE_CHECKING:
    from app.models.analysis import AnalysisRun
    from app.models.issue import CollectedIssue
    from app.models.opportunity import ProductOpportunity


class AnalysisCluster(Base):
    __tablename__ = "analysis_clusters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    cluster_label: Mapped[int] = mapped_column(Integer, nullable=False)  # -1 = outlier, 0..N = clusters
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    recurring_themes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    sample_issue_ids: Mapped[Optional[List[Any]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    analysis: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="clusters")
    issues: Mapped[List["CollectedIssue"]] = relationship("CollectedIssue", back_populates="cluster")
    opportunities: Mapped[List["ProductOpportunity"]] = relationship("ProductOpportunity", back_populates="cluster")

    def __repr__(self) -> str:
        return f"<AnalysisCluster(id={self.id}, label={self.cluster_label}, size={self.size}, title='{self.title}')>"

