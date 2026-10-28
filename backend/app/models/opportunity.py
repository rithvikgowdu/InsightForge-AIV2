from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import utc_now, generate_uuid

if TYPE_CHECKING:
    from app.models.analysis import AnalysisRun
    from app.models.cluster import AnalysisCluster


class ProductOpportunity(Base):
    __tablename__ = "product_opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    cluster_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("analysis_clusters.id", ondelete="SET NULL"), nullable=True, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    business_opportunity: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_solution: Mapped[str] = mapped_column(Text, nullable=False)
    target_customer_segment: Mapped[str] = mapped_column(String(255), nullable=False)
    
    suggested_mvp_features: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    market_potential: Mapped[str] = mapped_column(String(100), default="Moderate", nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.75, nullable=False)  # 0.0 to 1.0
    confidence_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    
    supporting_evidence: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    supporting_doc_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_fallback: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    analysis: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="opportunities")
    cluster: Mapped[Optional["AnalysisCluster"]] = relationship("AnalysisCluster", back_populates="opportunities")

    def __repr__(self) -> str:
        return f"<ProductOpportunity(id={self.id}, title='{self.title}', confidence={self.confidence_score})>"

