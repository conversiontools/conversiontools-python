"""
Task model - High-level interface for conversion tasks
"""

from typing import Optional, Dict, Any, TYPE_CHECKING
from ..types.config import TaskStatus, TaskStatusResponse, WaitOptions
from ..utils.errors import ConversionError
from ..utils.polling import poll_task_status_sync, poll_task_status_async

if TYPE_CHECKING:
    from ..api.tasks import TasksAPI
    from ..api.files import FilesAPI


class Task:
    """Task model for conversion tasks"""

    def __init__(
        self,
        task_id: str,
        task_type: str,
        tasks_api: "TasksAPI",
        files_api: "FilesAPI",
        status: TaskStatus = "PENDING",
        file_id: Optional[str] = None,
        error: Optional[str] = None,
        conversion_progress: int = 0,
        default_polling: Optional[Dict[str, float]] = None,
    ):
        self.id = task_id
        self.type = task_type
        self._status = status
        self._file_id = file_id
        self._error = error
        self._conversion_progress = conversion_progress
        self._tasks_api = tasks_api
        self._files_api = files_api
        self._default_polling = default_polling or {
            "interval": 5000,
            "max_interval": 30000,
            "backoff": 1.5,
        }

    @property
    def status(self) -> TaskStatus:
        """Get current status"""
        return self._status

    @property
    def file_id(self) -> Optional[str]:
        """Get result file ID"""
        return self._file_id

    @property
    def error(self) -> Optional[str]:
        """Get error message"""
        return self._error

    @property
    def conversion_progress(self) -> int:
        """Get conversion progress (0-100)"""
        return self._conversion_progress

    @property
    def is_complete(self) -> bool:
        """Check if task is complete (success or error)"""
        return self._status in ("SUCCESS", "ERROR")

    @property
    def is_success(self) -> bool:
        """Check if task succeeded"""
        return self._status == "SUCCESS"

    @property
    def is_error(self) -> bool:
        """Check if task failed"""
        return self._status == "ERROR"

    @property
    def is_running(self) -> bool:
        """Check if task is still running"""
        return self._status in ("PENDING", "RUNNING")

    def _update_from_response(self, response: TaskStatusResponse) -> None:
        """Update task state from API response"""
        self._status = response["status"]
        self._file_id = response["file_id"]
        self._error = response["error"]
        self._conversion_progress = response["conversionProgress"]

    def refresh(self) -> None:
        """Refresh task status from API (sync)"""
        response = self._tasks_api.get_status(self.id)
        self._update_from_response(response)

    async def refresh_async(self) -> None:
        """Refresh task status from API (async)"""
        response = await self._tasks_api.get_status_async(self.id)
        self._update_from_response(response)

    def get_status(self) -> TaskStatusResponse:
        """Get task status (sync)"""
        response = self._tasks_api.get_status(self.id)
        self._update_from_response(response)
        return response

    async def get_status_async(self) -> TaskStatusResponse:
        """Get task status (async)"""
        response = await self._tasks_api.get_status_async(self.id)
        self._update_from_response(response)
        return response

    def wait(self, options: Optional[WaitOptions] = None) -> None:
        """Wait for task to complete (sync)"""
        # Use provided options or defaults
        polling_interval = (
            options.get("polling_interval", self._default_polling["interval"])
            if options
            else self._default_polling["interval"]
        )
        max_polling_interval = (
            options.get("max_polling_interval", self._default_polling["max_interval"])
            if options
            else self._default_polling["max_interval"]
        )
        timeout = options.get("timeout", 0) if options else 0
        on_progress = options.get("on_progress") if options else None

        # Poll until complete
        final_status = poll_task_status_sync(
            lambda: self.get_status(),
            polling_interval,
            max_polling_interval,
            self._default_polling["backoff"],
            timeout,
            on_progress,
        )

        # Update internal state
        self._update_from_response(final_status)

        # Throw error if task failed
        if self._status == "ERROR":
            raise ConversionError(
                self._error or "Conversion failed",
                self.id,
                self._error,
            )

    async def wait_async(self, options: Optional[WaitOptions] = None) -> None:
        """Wait for task to complete (async)"""
        # Use provided options or defaults
        polling_interval = (
            options.get("polling_interval", self._default_polling["interval"])
            if options
            else self._default_polling["interval"]
        )
        max_polling_interval = (
            options.get("max_polling_interval", self._default_polling["max_interval"])
            if options
            else self._default_polling["max_interval"]
        )
        timeout = options.get("timeout", 0) if options else 0
        on_progress = options.get("on_progress") if options else None

        # Poll until complete
        final_status = await poll_task_status_async(
            lambda: self.get_status_async(),
            polling_interval,
            max_polling_interval,
            self._default_polling["backoff"],
            timeout,
            on_progress,
        )

        # Update internal state
        self._update_from_response(final_status)

        # Throw error if task failed
        if self._status == "ERROR":
            raise ConversionError(
                self._error or "Conversion failed",
                self.id,
                self._error,
            )

    def download_bytes(self) -> bytes:
        """Download result file as bytes (sync)"""
        if not self._file_id:
            raise ConversionError(
                "No result file available. Task may not be complete.",
                self.id,
            )

        return self._files_api.download_bytes(self._file_id)

    async def download_bytes_async(self) -> bytes:
        """Download result file as bytes (async)"""
        if not self._file_id:
            raise ConversionError(
                "No result file available. Task may not be complete.",
                self.id,
            )

        return await self._files_api.download_bytes_async(self._file_id)

    def download_to(self, output_path: Optional[str] = None) -> str:
        """Download result file to path (sync)"""
        if not self._file_id:
            raise ConversionError(
                "No result file available. Task may not be complete.",
                self.id,
            )

        return self._files_api.download_to(self._file_id, output_path)

    async def download_to_async(self, output_path: Optional[str] = None) -> str:
        """Download result file to path (async)"""
        if not self._file_id:
            raise ConversionError(
                "No result file available. Task may not be complete.",
                self.id,
            )

        return await self._files_api.download_to_async(self._file_id, output_path)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "type": self.type,
            "status": self._status,
            "file_id": self._file_id,
            "error": self._error,
            "conversion_progress": self._conversion_progress,
        }
