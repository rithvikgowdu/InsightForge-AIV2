import threading
from app.core.database import get_db_context
from app.core.logging import logger
from app.services.orchestrator import orchestrator


class BackgroundWorker:
    """
    Manages asynchronous analysis task execution in isolated database contexts.
    Ensures HTTP requests return immediately without blocking on network/AI operations.
    """

    @staticmethod
    def _run_task(analysis_id: str) -> None:
        logger.info(f"BackgroundWorker executing pipeline for analysis_id={analysis_id}")
        try:
            with get_db_context() as db:
                orchestrator.run_analysis_pipeline(db, analysis_id)
        except Exception as e:
            logger.exception(f"Unexpected error in background worker thread: {str(e)}")

    def dispatch_analysis(self, analysis_id: str) -> None:
        """Spawn worker thread to run analysis asynchronously with fresh DB context."""
        thread = threading.Thread(
            target=self._run_task,
            args=(analysis_id,),
            name=f"Worker-Analysis-{analysis_id[:8]}",
            daemon=True,
        )
        thread.start()
        logger.info(f"Dispatched background thread {thread.name} for analysis {analysis_id}")


background_worker = BackgroundWorker()

