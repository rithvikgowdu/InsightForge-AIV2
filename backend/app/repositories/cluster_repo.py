from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.cluster import AnalysisCluster


class ClusterRepository:
    @staticmethod
    def bulk_create(db: Session, clusters: List[AnalysisCluster]) -> List[AnalysisCluster]:
        db.add_all(clusters)
        db.commit()
        return clusters

    @staticmethod
    def get_by_analysis(db: Session, analysis_id: str) -> List[AnalysisCluster]:
        return list(
            db.scalars(
                select(AnalysisCluster)
                .where(AnalysisCluster.analysis_id == analysis_id)
                .order_by(AnalysisCluster.size.desc())
            ).all()
        )


cluster_repo = ClusterRepository()

