from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.issue import CollectedIssue


class IssueRepository:
    @staticmethod
    def bulk_create(db: Session, issues: List[CollectedIssue]) -> List[CollectedIssue]:
        db.add_all(issues)
        db.commit()
        return issues

    @staticmethod
    def get_by_analysis(db: Session, analysis_id: str, limit: int = 50) -> List[CollectedIssue]:
        return list(
            db.scalars(
                select(CollectedIssue)
                .where(CollectedIssue.analysis_id == analysis_id)
                .order_by(CollectedIssue.issue_number.desc())
                .limit(limit)
            ).all()
        )


issue_repo = IssueRepository()

