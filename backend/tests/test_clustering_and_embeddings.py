import numpy as np
from app.services.clustering import ClusteringService
from app.services.embeddings import EmbeddingService


def test_tfidf_embedding_generation():
    service = EmbeddingService()
    texts = [
        "Database connection pool times out on high concurrency loads.",
        "PostgreSQL connection leak causes timeout and socket exhaustion.",
        "Add dark mode theme support to user settings dashboard.",
        "User profile interface needs dark theme toggle.",
    ]
    embeddings = service._generate_tfidf_embeddings(texts, target_dim=128)
    assert embeddings.shape == (4, 128)
    # Check L2 normalization
    norms = np.linalg.norm(embeddings, axis=1)
    np.testing.assert_allclose(norms, 1.0, rtol=1e-5)


def test_clustering_small_dataset():
    clustering = ClusteringService()
    # 2 identical and 2 orthogonal vectors
    vecs = np.array([
        [1.0, 0.0, 0.0],
        [0.95, 0.05, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.98, 0.02],
    ])
    clusters = clustering.cluster_embeddings(vecs)
    assert len(clusters) >= 1
    total_points = sum(c["size"] for c in clusters)
    assert total_points == 4


def test_clustering_edge_cases():
    clustering = ClusteringService()
    # 0 items
    assert clustering.cluster_embeddings(np.empty((0, 10))) == []

    # 1 item
    c1 = clustering.cluster_embeddings(np.array([[1.0, 0.0]]))
    assert len(c1) == 1
    assert c1[0]["size"] == 1

