from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.core.errors import EntityNotFoundException, PermissionDeniedError
from app.models.user import User
from app.repositories.analysis_repo import analysis_repo
from app.repositories.issue_repo import issue_repo
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisDetailResponse,
    AnalysisHistoryItem,
    AnalysisResponse,
    AnalysisStatusResponse,
)
from app.schemas.cluster import ClusterResponse
from app.schemas.issue import IssueResponse
from app.schemas.opportunity import OpportunityResponse
from app.services.background_worker import background_worker

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_analysis(
    analysis_in: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a GitHub repository for deep issue clustering and product opportunity synthesis.
    Executes asynchronously in the background.
    """
    analysis = analysis_repo.create(db, user_id=current_user.id, analysis_in=analysis_in)
    background_worker.dispatch_analysis(analysis.id)
    return AnalysisResponse.model_validate(analysis)


@router.get("/history", response_model=List[AnalysisHistoryItem])
def get_analysis_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve list of previous analysis runs for the authenticated user."""
    runs = analysis_repo.get_user_history(db, user_id=current_user.id, skip=skip, limit=limit)
    return [AnalysisHistoryItem.model_validate(r) for r in runs]


@router.get("/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis_detail(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full details, clusters, and structured product opportunities for an analysis."""
    analysis = analysis_repo.get_by_id(db, analysis_id)
    if not analysis:
        raise EntityNotFoundException(f"Analysis '{analysis_id}' was not found.")

    if analysis.user_id != current_user.id:
        raise PermissionDeniedError("You do not have permission to access this analysis.")

    # Fetch sample issues
    issues = issue_repo.get_by_analysis(db, analysis_id, limit=25)

    return AnalysisDetailResponse(
        id=analysis.id,
        repo_owner=analysis.repo_owner,
        repo_name=analysis.repo_name,
        repo_url=analysis.repo_url,
        status=analysis.status,
        current_step=analysis.current_step,
        progress_pct=analysis.progress_pct,
        total_issues_requested=analysis.total_issues_requested,
        total_issues_collected=analysis.total_issues_collected,
        total_clusters=analysis.total_clusters,
        total_opportunities=analysis.total_opportunities,
        error_message=analysis.error_message,
        is_fallback=analysis.is_fallback,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
        clusters=[ClusterResponse.model_validate(c) for c in (analysis.clusters or [])],
        opportunities=[OpportunityResponse.model_validate(o) for o in (analysis.opportunities or [])],
        sample_issues=[IssueResponse.model_validate(i) for i in issues],
    )


@router.get("/{analysis_id}/status", response_model=AnalysisStatusResponse)
def get_analysis_status(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lightweight polling endpoint to check current execution status and progress."""
    analysis = analysis_repo.get_by_id(db, analysis_id)
    if not analysis:
        raise EntityNotFoundException(f"Analysis '{analysis_id}' was not found.")

    if analysis.user_id != current_user.id:
        raise PermissionDeniedError("You do not have permission to access this analysis.")

    return AnalysisStatusResponse.model_validate(analysis)


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an analysis run owned by the authenticated user."""
    analysis = analysis_repo.get_by_id_and_user(db, analysis_id, current_user.id)
    if not analysis:
        raise EntityNotFoundException(f"Analysis '{analysis_id}' was not found.")

    analysis_repo.delete(db, analysis)
    return None

