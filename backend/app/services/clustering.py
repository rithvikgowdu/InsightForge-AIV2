from typing import Any, Dict, List
import numpy as np
from sklearn.cluster import AgglomerativeClustering, DBSCAN
from sklearn.metrics.pairwise import cosine_distances
from app.core.logging import logger


class ClusteringService:
    def cluster_embeddings(
        self,
        embeddings: np.ndarray,
        eps: float = 0.42,
        min_samples: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Cluster normalized embedding vectors into groups of semantically related issues.
        Returns a list of cluster dictionaries containing cluster_label and member indices.
        """
        n_samples = embeddings.shape[0]

        if n_samples == 0:
            return []

        # Trivial edge cases
        if n_samples == 1:
            return [{"cluster_label": 0, "indices": [0], "size": 1}]

        if n_samples == 2:
            dist = cosine_distances(embeddings[0:1], embeddings[1:2])[0][0]
            if dist < 0.45:
                return [{"cluster_label": 0, "indices": [0, 1], "size": 2}]
            else:
                return [
                    {"cluster_label": 0, "indices": [0], "size": 1},
                    {"cluster_label": 1, "indices": [1], "size": 1},
                ]

        # Small dataset strategy (3 to 6 items): use Agglomerative clustering
        if n_samples <= 6:
            n_clusters = max(1, min(3, n_samples // 2))
            agg = AgglomerativeClustering(
                n_clusters=n_clusters,
                metric="cosine",
                linkage="average",
            )
            labels = agg.fit_predict(embeddings)
            return self._build_clusters_from_labels(labels)

        # Standard strategy: DBSCAN with cosine metric
        try:
            dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine")
            labels = dbscan.fit_predict(embeddings)

            # Check if DBSCAN labeled almost everything as noise (-1)
            noise_count = np.sum(labels == -1)
            unique_clusters = set(labels) - {-1}

            # If DBSCAN formed zero clusters or noise is > 75%, fallback to Agglomerative
            if len(unique_clusters) == 0 or (noise_count / n_samples) > 0.75:
                logger.info("DBSCAN produced high noise; falling back to AgglomerativeClustering.")
                k = max(2, min(8, n_samples // 4))
                agg = AgglomerativeClustering(
                    n_clusters=k,
                    metric="cosine",
                    linkage="average",
                )
                labels = agg.fit_predict(embeddings)

            return self._build_clusters_from_labels(labels)

        except Exception as e:
            logger.warning(f"Error during clustering execution ({str(e)}). Applying fallback partitioning.")
            # Deterministic chunking fallback
            k = max(1, n_samples // 4)
            labels = np.array([i % k for i in range(n_samples)])
            return self._build_clusters_from_labels(labels)

    def _build_clusters_from_labels(self, labels: np.ndarray) -> List[Dict[str, Any]]:
        """Organize label array into structured cluster dictionaries."""
        cluster_map: Dict[int, List[int]] = {}

        for idx, lbl in enumerate(labels):
            lbl_int = int(lbl)
            if lbl_int not in cluster_map:
                cluster_map[lbl_int] = []
            cluster_map[lbl_int].append(idx)

        # Separate regular clusters from noise (-1)
        clusters: List[Dict[str, Any]] = []
        noise_indices = cluster_map.pop(-1, [])

        # Sort clusters by size descending
        for label, idxs in sorted(cluster_map.items(), key=lambda x: len(x[1]), reverse=True):
            clusters.append({
                "cluster_label": label,
                "indices": idxs,
                "size": len(idxs),
            })

        # If noise exists, either distribute to nearest or keep as an outlier group
        if noise_indices:
            clusters.append({
                "cluster_label": -1,
                "indices": noise_indices,
                "size": len(noise_indices),
            })

        return clusters


clustering_service = ClusteringService()

