from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import utc_now, generate_uuid

if TYPE_CHECKING:
    from app.models.analysis import AnalysisRun
    from app.models.cluster import AnalysisCluster


class CollectedIssue(Base):
    __tablename__ = "collected_issues"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    cluster_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("analysis_clusters.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    source_id: Mapped[str] = mapped_column(String(100), nullable=False)  # GitHub issue number/id
    issue_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clean_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="open", nullable=False)
    author: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    labels: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    comments_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    source_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    analysis: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="issues")
    cluster: Mapped[Optional["AnalysisCluster"]] = relationship("AnalysisCluster", back_populates="issues")

    def __repr__(self) -> str:
        return f"<CollectedIssue(id={self.id}, number=#{self.issue_number}, title='{self.title[:30]}')>"

