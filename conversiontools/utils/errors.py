"""
Error classes for Conversion Tools API Client
"""

from typing import Optional, Dict, Any


class ConversionToolsError(Exception):
    """Base error class for all Conversion Tools API errors"""

    def __init__(
        self,
        message: str,
        code: str,
        status: Optional[int] = None,
        response: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.response = response


class AuthenticationError(ConversionToolsError):
    """Authentication error - Invalid or missing API token"""

    def __init__(self, message: str = "Not authorized - Invalid or missing API token"):
        super().__init__(message, "AUTHENTICATION_ERROR", 401)


class ValidationError(ConversionToolsError):
    """Validation error - Invalid request parameters"""

    def __init__(self, message: str, response: Optional[Any] = None):
        super().__init__(message, "VALIDATION_ERROR", 400, response)


class RateLimitError(ConversionToolsError):
    """Rate limit error - Quota exceeded"""

    def __init__(
        self,
        message: str,
        limits: Optional[Dict[str, Dict[str, int]]] = None,
    ):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429)
        self.limits = limits


class FileNotFoundError(ConversionToolsError):
    """File not found error"""

    def __init__(self, message: str = "File not found", file_id: Optional[str] = None):
        super().__init__(message, "FILE_NOT_FOUND", 404)
        self.file_id = file_id


class TaskNotFoundError(ConversionToolsError):
    """Task not found error"""

    def __init__(self, message: str = "Task not found", task_id: Optional[str] = None):
        super().__init__(message, "TASK_NOT_FOUND", 404)
        self.task_id = task_id


class ConversionError(ConversionToolsError):
    """Conversion error - Task failed during conversion"""

    def __init__(
        self,
        message: str,
        task_id: Optional[str] = None,
        task_error: Optional[str] = None,
    ):
        super().__init__(message, "CONVERSION_ERROR")
        self.task_id = task_id
        self.task_error = task_error


class TimeoutError(ConversionToolsError):
    """Timeout error - Request or operation timed out"""

    def __init__(
        self, message: str = "Operation timed out", timeout: Optional[float] = None
    ):
        super().__init__(message, "TIMEOUT_ERROR", 408)
        self.timeout = timeout


class NetworkError(ConversionToolsError):
    """Network error - Connection issues"""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "NETWORK_ERROR")
        self.original_error = original_error
