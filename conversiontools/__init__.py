"""
Conversion Tools API Client v2

Modern Python library for converting files using the
Conversion Tools API at https://conversiontools.io

Example:
    >>> from conversiontools import ConversionToolsClient
    >>>
    >>> client = ConversionToolsClient({
    ...     'api_token': 'your-api-token'
    ... })
    >>>
    >>> # Simple conversion
    >>> client.convert(
    ...     'convert.xml_to_excel',
    ...     'data.xml',
    ...     'result.xlsx'
    ... )
"""

__version__ = "2.0.0"

# Main client
from .client import ConversionToolsClient

# Models
from .models import Task

# Types
from .types import (
    TaskStatus,
    ProgressEvent,
    ConversionProgressEvent,
    RateLimitInfo,
    RateLimits,
    ConversionToolsConfig,
    ConversionInput,
    ConvertOptions,
    WaitOptions,
    TaskStatusResponse,
    TaskCreateRequest,
    TaskCreateResponse,
    FileUploadResponse,
    FileInfo,
    FileUploadOptions,
    UserInfo,
    FileSource,
    FileResult,
    TaskDetail,
)

# Errors
from .utils import (
    ConversionToolsError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    FileNotFoundError,
    TaskNotFoundError,
    ConversionError,
    TimeoutError,
    NetworkError,
)

__all__ = [
    # Version
    "__version__",
    # Main client
    "ConversionToolsClient",
    # Models
    "Task",
    # Types
    "TaskStatus",
    "ProgressEvent",
    "ConversionProgressEvent",
    "RateLimitInfo",
    "RateLimits",
    "ConversionToolsConfig",
    "ConversionInput",
    "ConvertOptions",
    "WaitOptions",
    "TaskStatusResponse",
    "TaskCreateRequest",
    "TaskCreateResponse",
    "FileUploadResponse",
    "FileInfo",
    "FileUploadOptions",
    "UserInfo",
    "FileSource",
    "FileResult",
    "TaskDetail",
    # Errors
    "ConversionToolsError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "FileNotFoundError",
    "TaskNotFoundError",
    "ConversionError",
    "TimeoutError",
    "NetworkError",
]
