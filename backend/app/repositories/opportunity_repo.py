from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.opportunity import ProductOpportunity


class OpportunityRepository:
    @staticmethod
    def bulk_create(db: Session, opportunities: List[ProductOpportunity]) -> List[ProductOpportunity]:
        db.add_all(opportunities)
        db.commit()
        return opportunities

    @staticmethod
    def get_by_analysis(db: Session, analysis_id: str) -> List[ProductOpportunity]:
        return list(
            db.scalars(
                select(ProductOpportunity)
                .where(ProductOpportunity.analysis_id == analysis_id)
                .order_by(ProductOpportunity.confidence_score.desc())
            ).all()
        )


opportunity_repo = OpportunityRepository()

