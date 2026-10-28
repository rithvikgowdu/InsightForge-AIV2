from typing import List, Optional
import numpy as np
from app.core.config import settings
from app.core.logging import logger


class EmbeddingService:
    def __init__(self):
        self._model = None
        self._model_loaded = False
        self._model_name = settings.EMBEDDING_MODEL_NAME

    def _get_model(self):
        """Lazy load the sentence transformer model with graceful fallback."""
        if self._model_loaded:
            return self._model

        if settings.USE_LIGHTWEIGHT_EMBEDDINGS:
            self._model_loaded = True
            return None

        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer model '{self._model_name}'...")
            self._model = SentenceTransformer(self._model_name)
            logger.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.warning(
                f"SentenceTransformer model could not be loaded ({str(e)}). "
                "Activating deterministic TF-IDF vectorizer fallback."
            )
            self._model = None

        self._model_loaded = True
        return self._model

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate normalized semantic embeddings for a list of texts.
        Returns a numpy array of shape (N, D).
        """
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        model = self._get_model()

        if model is not None:
            try:
                embeddings = model.encode(
                    texts,
                    batch_size=32,
                    show_progress_bar=False,
                    normalize_embeddings=True,
                )
                return np.asarray(embeddings, dtype=np.float32)
            except Exception as e:
                logger.warning(f"Error during neural embedding inference: {str(e)}. Using TF-IDF fallback.")

        # Deterministic TF-IDF Fallback
        return self._generate_tfidf_embeddings(texts)

    def _generate_tfidf_embeddings(self, texts: List[str], target_dim: int = 384) -> np.ndarray:
        """Deterministic TF-IDF embedding fallback with zero-padding/truncation to fixed dimension."""
        from sklearn.feature_extraction.text import TfidfVectorizer

        vectorizer = TfidfVectorizer(
            max_features=target_dim,
            stop_words="english",
            token_pattern=r"(?u)\b\w+\b",
        )
        try:
            matrix = vectorizer.fit_transform(texts).toarray()
            # If vocab is smaller than target_dim, pad with zeros
            if matrix.shape[1] < target_dim:
                pad_width = ((0, 0), (0, target_dim - matrix.shape[1]))
                matrix = np.pad(matrix, pad_width, mode="constant")
            elif matrix.shape[1] > target_dim:
                matrix = matrix[:, :target_dim]
        except ValueError:
            # All texts contained only stopwords or empty
            matrix = np.zeros((len(texts), target_dim), dtype=np.float32)

        # L2 Normalize
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = (matrix / norms).astype(np.float32)
        return normalized

    @staticmethod
    def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity between two normalized vectors."""
        dot = np.dot(v1, v2)
        return float(np.clip(dot, -1.0, 1.0))


embedding_service = EmbeddingService()

