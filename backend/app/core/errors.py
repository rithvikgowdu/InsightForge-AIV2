from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


class InsightForgeException(Exception):
    """Base application exception."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundException(InsightForgeException):
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND, details=details)


class AuthenticationError(InsightForgeException):
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="AUTHENTICATION_FAILED", status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class PermissionDeniedError(InsightForgeException):
    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="PERMISSION_DENIED", status_code=status.HTTP_403_FORBIDDEN, details=details)


class DuplicateEntityError(InsightForgeException):
    def __init__(self, message: str = "Resource already exists", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="DUPLICATE_ENTITY", status_code=status.HTTP_409_CONFLICT, details=details)


class GitHubAPIError(InsightForgeException):
    def __init__(self, message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="GITHUB_API_ERROR", status_code=status_code, details=details)


class AnalysisPipelineError(InsightForgeException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="ANALYSIS_PIPELINE_ERROR", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details)


async def insightforge_exception_handler(request: Request, exc: InsightForgeException) -> JSONResponse:
    logger.warning(f"Handled application exception: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "code": exc.code,
            "details": exc.details,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled server error on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please try again later.",
            "code": "INTERNAL_SERVER_ERROR",
        },
    )

