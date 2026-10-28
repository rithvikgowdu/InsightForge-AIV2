from datetime import datetime, timezone
import traceback
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.models.analysis import AnalysisRun
from app.models.cluster import AnalysisCluster
from app.models.issue import CollectedIssue
from app.models.opportunity import ProductOpportunity
from app.repositories.analysis_repo import analysis_repo
from app.repositories.cluster_repo import cluster_repo
from app.repositories.issue_repo import issue_repo
from app.repositories.opportunity_repo import opportunity_repo
from app.services.clustering import clustering_service
from app.services.embeddings import embedding_service
from app.services.github_connector import github_connector
from app.services.llm_provider import llm_provider
from app.services.preprocessing import preprocessor


class AnalysisOrchestrator:
    def run_analysis_pipeline(self, db: Session, analysis_id: str) -> None:
        """
        Execute the end-to-end AI analysis pipeline.
        Must be invoked with a dedicated database session.
        """
        analysis = analysis_repo.get_by_id(db, analysis_id)
        if not analysis:
            logger.error(f"AnalysisRun '{analysis_id}' not found in database.")
            return

        owner = analysis.repo_owner
        repo = analysis.repo_name
        requested_limit = analysis.total_issues_requested
        include_closed = True
        if analysis.analysis_metadata and "include_closed" in analysis.analysis_metadata:
            include_closed = analysis.analysis_metadata["include_closed"]

        logger.info(f"Starting analysis {analysis_id} for {owner}/{repo} (limit={requested_limit})...")

        try:
            # -------------------------------------------------------------
            # Step 1: Validate Repository Access (Progress 15%)
            # -------------------------------------------------------------
            analysis_repo.update_progress(
                db,
                analysis_id,
                status="RUNNING",
                step="Verifying repository accessibility",
                progress_pct=15,
            )
            github_connector.validate_repository(owner, repo)

            # -------------------------------------------------------------
            # Step 2: Collect Real Issues from GitHub (Progress 35%)
            # -------------------------------------------------------------
            analysis_repo.update_progress(
                db,
                analysis_id,
                status="RUNNING",
                step=f"Collecting up to {requested_limit} issues from GitHub",
                progress_pct=35,
            )
            raw_issues = github_connector.fetch_issues(
                owner=owner,
                repo=repo,
                limit=requested_limit,
                include_closed=include_closed,
            )

            if not raw_issues:
                analysis_repo.update_progress(
                    db,
                    analysis_id,
                    status="COMPLETED",
                    step="Analysis completed (No issues found in repository)",
                    progress_pct=100,
                    error_message="The target repository currently has no public issues to analyze.",
                    total_collected=0,
                    total_clusters=0,
                    total_opportunities=0,
                )
                return

            # -------------------------------------------------------------
            # Step 3: Clean, Filter, and Deduplicate (Progress 50%)
            # -------------------------------------------------------------
            analysis_repo.update_progress(
                db,
                analysis_id,
                status="RUNNING",
                step="Cleaning and deduplicating issue text",
                progress_pct=50,
                total_collected=len(raw_issues),
            )
            valid_issues, clean_docs = preprocessor.preprocess_issues(raw_issues)

            if not valid_issues:
                analysis_repo.update_progress(
                    db,
                    analysis_id,
                    status="COMPLETED",
                    step="Analysis completed (Insufficient issue text to extract insights)",
                    progress_pct=100,
                    error_message="Collected issues did not contain enough descriptive text for semantic analysis.",
                    total_collected=len(raw_issues),
                    total_clusters=0,
                    total_opportunities=0,
                )
                return

            # -------------------------------------------------------------
            # Step 4: Semantic Embedding Generation (Progress 65%)
            # -------------------------------------------------------------
            analysis_repo.update_progress(
                db,
                analysis_id,
                status="RUNNING",
                step=f"Generating semantic embeddings for {len(valid_issues)} discussions",
                progress_pct=65,
            )
            embeddings = embedding_service.generate_embeddings(clean_docs)

            # -------------------------------------------------------------
            # Step 5: Semantic Clustering (Progress 78%)
            # -------------------------------------------------------------
            analysis_repo.update_progress(
                db,
                analysis_id,
                status="RUNNING",
                step="Clustering semantically related user problems",
                progress_pct=78,
            )
            cluster_groups = clustering_service.cluster_embeddings(embeddings)

            # -------------------------------------------------------------
            # Step 6: Cluster Summarization & Opportunity Synthesis (Progress 90%)
            # -------------------------------------------------------------
            analysis_repo.update_progress(
                db,
                analysis_id,
                status="RUNNING",
                step="Synthesizing cluster summaries and product opportunities",
                progress_pct=90,
            )

            db_clusters: List[AnalysisCluster] = []
            db_opportunities: List[ProductOpportunity] = []
            db_issues: List[CollectedIssue] = []

            any_fallback = False

            # Create a map of index -> issue dict
            index_to_issue = {i: valid_issues[i] for i in range(len(valid_issues))}
            issue_to_cluster_id: Dict[int, str] = {}

            for c_idx, c_info in enumerate(cluster_groups):
                member_indices = c_info["indices"]
                cluster_label = c_info["cluster_label"]
                cluster_issues = [index_to_issue[i] for i in member_indices if i in index_to_issue]

                if not cluster_issues:
                    continue

                # Run LLM or deterministic fallback
                synthesis = llm_provider.summarize_and_synthesize(
                    cluster_issues=cluster_issues,
                    repo_name=f"{owner}/{repo}",
                    cluster_index=c_idx,
                )

                if synthesis.get("is_fallback", False):
                    any_fallback = True

                cluster_obj = AnalysisCluster(
                    analysis_id=analysis_id,
                    cluster_label=cluster_label,
                    title=synthesis.get("cluster_title", f"Cluster #{c_idx+1}"),
                    summary=synthesis.get("cluster_summary", "Summary of related user discussions."),
                    size=len(cluster_issues),
                    recurring_themes=synthesis.get("recurring_themes", []),
                    sample_issue_ids=[iss.get("issue_number") for iss in cluster_issues[:5]],
                )
                db_clusters.append(cluster_obj)

                # Link member issues to this cluster ID
                for iss_idx in member_indices:
                    issue_to_cluster_id[iss_idx] = cluster_obj.id

                # Create associated product opportunity
                opp_obj = ProductOpportunity(
                    analysis_id=analysis_id,
                    cluster_id=cluster_obj.id,
                    title=synthesis.get("opportunity_title", f"Opportunity #{c_idx+1}"),
                    problem_statement=synthesis.get("problem_statement", ""),
                    business_opportunity=synthesis.get("business_opportunity", ""),
                    proposed_solution=synthesis.get("proposed_solution", ""),
                    target_customer_segment=synthesis.get("target_customer_segment", "General Users"),
                    suggested_mvp_features=synthesis.get("suggested_mvp_features", []),
                    market_potential=synthesis.get("market_potential", "Moderate"),
                    confidence_score=float(synthesis.get("confidence_score", 0.70)),
                    confidence_explanation=synthesis.get("confidence_explanation", ""),
                    supporting_evidence=synthesis.get("supporting_evidence", []),
                    supporting_doc_count=len(cluster_issues),
                    is_fallback=synthesis.get("is_fallback", True),
                )
                db_opportunities.append(opp_obj)

            # Prepare Issue models
            for idx, iss in enumerate(valid_issues):
                c_id = issue_to_cluster_id.get(idx)
                db_issues.append(
                    CollectedIssue(
                        analysis_id=analysis_id,
                        cluster_id=c_id,
                        source_id=str(iss.get("source_id")),
                        issue_number=int(iss.get("issue_number")),
                        title=iss.get("title", ""),
                        body=iss.get("body"),
                        clean_text=iss.get("clean_text"),
                        url=iss.get("url", ""),
                        state=iss.get("state", "open"),
                        author=iss.get("author"),
                        labels=iss.get("labels", []),
                        comments_count=iss.get("comments_count", 0),
                        source_created_at=iss.get("source_created_at"),
                    )
                )

            # -------------------------------------------------------------
            # Step 7: Persist All Records in Atomic Transaction (Progress 100%)
            # -------------------------------------------------------------
            analysis_repo.update_progress(
                db,
                analysis_id,
                status="RUNNING",
                step="Persisting structured opportunities and evidence",
                progress_pct=95,
            )

            cluster_repo.bulk_create(db, db_clusters)
            opportunity_repo.bulk_create(db, db_opportunities)
            issue_repo.bulk_create(db, db_issues)

            analysis_repo.update_progress(
                db,
                analysis_id,
                status="COMPLETED",
                step="Analysis completed successfully",
                progress_pct=100,
                is_fallback=any_fallback,
                total_collected=len(raw_issues),
                total_clusters=len(db_clusters),
                total_opportunities=len(db_opportunities),
            )

            logger.info(
                f"Analysis {analysis_id} finished successfully: "
                f"{len(db_clusters)} clusters, {len(db_opportunities)} opportunities."
            )

        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Analysis {analysis_id} failed with error: {str(e)}\n{error_trace}")
            
            user_msg = str(e)
            if "rate limit" in user_msg.lower():
                user_msg = "GitHub API rate limit reached. Please provide a GITHUB_TOKEN or try again later."

            analysis_repo.update_progress(
                db,
                analysis_id,
                status="FAILED",
                step="Analysis failed",
                progress_pct=100,
                error_message=user_msg,
            )


orchestrator = AnalysisOrchestrator()

