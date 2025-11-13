"""
Type definitions for Conversion Tools API Client
"""

from typing import Optional, Dict, Any, Callable, Union, BinaryIO, Literal
from typing_extensions import TypedDict, NotRequired


# Task status type
TaskStatus = Literal["PENDING", "RUNNING", "SUCCESS", "ERROR"]


class ProgressEvent(TypedDict):
    """Progress event for uploads/downloads"""

    loaded: int
    total: NotRequired[Optional[int]]
    percent: NotRequired[int]


class ConversionProgressEvent(ProgressEvent):
    """Progress event for conversion tasks"""

    status: TaskStatus
    task_id: str


class RateLimitInfo(TypedDict):
    """Rate limit information"""

    limit: int
    remaining: int


class RateLimits(TypedDict, total=False):
    """Rate limits from response headers"""

    daily: RateLimitInfo
    monthly: RateLimitInfo
    file_size: int


class ConversionToolsConfig(TypedDict, total=False):
    """Configuration for ConversionToolsClient"""

    api_token: str  # Required
    base_url: str
    timeout: float
    retries: int
    retry_delay: float
    retryable_statuses: list[int]
    polling_interval: float
    max_polling_interval: float
    polling_backoff: float
    webhook_url: str
    on_upload_progress: Callable[[ProgressEvent], None]
    on_download_progress: Callable[[ProgressEvent], None]
    on_conversion_progress: Callable[[ConversionProgressEvent], None]


# Conversion input types
ConversionInput = Union[
    str,  # File path
    bytes,  # Buffer
    BinaryIO,  # Stream/file object
    Dict[str, Any],  # Explicit dict with path/url/stream/buffer/file_id
]


class ConvertOptions(TypedDict, total=False):
    """Options for convert() method"""

    type: str  # Required - conversion type
    input: ConversionInput  # Required
    output: str
    options: Dict[str, Any]
    wait: bool
    callback_url: str
    polling: Dict[str, float]


class WaitOptions(TypedDict, total=False):
    """Options for task.wait()"""

    polling_interval: float
    max_polling_interval: float
    timeout: float
    on_progress: Callable[[Dict[str, Any]], None]


class TaskStatusResponse(TypedDict):
    """Task status response from API"""

    error: Optional[str]
    status: TaskStatus
    file_id: Optional[str]
    conversionProgress: int


class TaskCreateRequest(TypedDict, total=False):
    """Task creation request"""

    type: str  # Required
    options: Dict[str, Any]  # Required
    callbackUrl: str


class TaskCreateResponse(TypedDict):
    """Task creation response"""

    error: Optional[str]
    task_id: str
    sandbox: NotRequired[bool]
    message: NotRequired[str]


class FileUploadResponse(TypedDict):
    """File upload response"""

    error: Optional[str]
    file_id: str


class FileInfo(TypedDict):
    """File info response"""

    preview: bool
    size: int
    name: str
    previewData: NotRequired[list[str]]


class FileUploadOptions(TypedDict, total=False):
    """File upload options"""

    on_progress: Callable[[ProgressEvent], None]


class UserInfo(TypedDict):
    """User info response"""

    error: Optional[str]
    email: str


class FileSource(TypedDict):
    """File source information in task details"""

    id: str
    name: str
    size: int
    exists: bool


class FileResult(TypedDict):
    """File result information in task details"""

    id: str
    name: str
    size: int
    exists: bool


class TaskDetail(TypedDict):
    """Detailed task information"""

    id: str
    type: str
    status: TaskStatus
    error: Optional[str]
    url: Optional[str]
    dateCreated: str
    dateFinished: Optional[str]
    conversionProgress: int
    fileSource: NotRequired[FileSource]
    fileResult: NotRequired[FileResult]
