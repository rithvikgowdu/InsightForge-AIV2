from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.models.analysis import AnalysisRun
from app.schemas.analysis import AnalysisCreate


class AnalysisRepository:
    @staticmethod
    def create(db: Session, user_id: int, analysis_in: AnalysisCreate) -> AnalysisRun:
        analysis = AnalysisRun(
            user_id=user_id,
            repo_owner=analysis_in.repo_owner,
            repo_name=analysis_in.repo_name,
            repo_url=analysis_in.repo_url,
            status="QUEUED",
            current_step="Queued for analysis",
            progress_pct=5,
            total_issues_requested=analysis_in.issue_limit,
            total_issues_collected=0,
            total_clusters=0,
            total_opportunities=0,
            is_fallback=False,
            analysis_metadata={"include_closed": analysis_in.include_closed},
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def get_by_id(db: Session, analysis_id: str) -> Optional[AnalysisRun]:
        return db.scalar(
            select(AnalysisRun)
            .where(AnalysisRun.id == analysis_id)
            .options(
                selectinload(AnalysisRun.clusters),
                selectinload(AnalysisRun.opportunities),
                selectinload(AnalysisRun.issues),
            )
        )

    @staticmethod
    def get_by_id_and_user(db: Session, analysis_id: str, user_id: int) -> Optional[AnalysisRun]:
        return db.scalar(
            select(AnalysisRun)
            .where(AnalysisRun.id == analysis_id, AnalysisRun.user_id == user_id)
            .options(
                selectinload(AnalysisRun.clusters),
                selectinload(AnalysisRun.opportunities),
                selectinload(AnalysisRun.issues),
            )
        )

    @staticmethod
    def get_user_history(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[AnalysisRun]:
        return list(
            db.scalars(
                select(AnalysisRun)
                .where(AnalysisRun.user_id == user_id)
                .order_by(AnalysisRun.created_at.desc())
                .offset(skip)
                .limit(limit)
            ).all()
        )

    @staticmethod
    def update_progress(
        db: Session,
        analysis_id: str,
        status: str,
        step: str,
        progress_pct: int,
        error_message: Optional[str] = None,
        is_fallback: Optional[bool] = None,
        total_collected: Optional[int] = None,
        total_clusters: Optional[int] = None,
        total_opportunities: Optional[int] = None,
    ) -> Optional[AnalysisRun]:
        analysis = db.scalar(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
        if not analysis:
            return None

        analysis.status = status
        analysis.current_step = step
        analysis.progress_pct = progress_pct
        if error_message is not None:
            analysis.error_message = error_message
        if is_fallback is not None:
            analysis.is_fallback = is_fallback
        if total_collected is not None:
            analysis.total_issues_collected = total_collected
        if total_clusters is not None:
            analysis.total_clusters = total_clusters
        if total_opportunities is not None:
            analysis.total_opportunities = total_opportunities
        if status in ("COMPLETED", "FAILED"):
            analysis.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def delete(db: Session, analysis: AnalysisRun) -> None:
        db.delete(analysis)
        db.commit()


analysis_repo = AnalysisRepository()

