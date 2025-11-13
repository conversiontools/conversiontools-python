"""
Main Conversion Tools API Client
"""

from typing import Optional, Dict, Any
from .types.config import (
    ConversionToolsConfig,
    RateLimits,
    UserInfo,
    ConversionInput,
)
from .api.http import HttpClient
from .api.files import FilesAPI
from .api.tasks import TasksAPI
from .api.config import ConfigAPI
from .models.task import Task
from .utils.validation import validate_api_token, validate_conversion_input
from .utils.progress import create_progress_event

# Package version
VERSION = "2.0.0"


class ConversionToolsClient:
    """Main Conversion Tools API Client"""

    def __init__(self, config: ConversionToolsConfig):
        """Initialize the Conversion Tools client"""

        # Validate API token
        validate_api_token(config["api_token"])

        # Set up configuration with defaults
        self.config: Dict[str, Any] = {
            "api_token": config["api_token"],
            "base_url": config.get("base_url", "https://api.conversiontools.io/v1"),
            "timeout": config.get("timeout", 300000),  # 5 minutes
            "retries": config.get("retries", 3),
            "retry_delay": config.get("retry_delay", 1000),
            "retryable_statuses": config.get(
                "retryable_statuses", [408, 500, 502, 503, 504]
            ),
            "polling_interval": config.get("polling_interval", 5000),
            "max_polling_interval": config.get("max_polling_interval", 30000),
            "polling_backoff": config.get("polling_backoff", 1.5),
            "webhook_url": config.get("webhook_url"),
            "on_upload_progress": config.get("on_upload_progress"),
            "on_download_progress": config.get("on_download_progress"),
            "on_conversion_progress": config.get("on_conversion_progress"),
        }

        # Initialize HTTP client
        self.http = HttpClient(
            api_token=self.config["api_token"],
            base_url=self.config["base_url"],
            timeout=self.config["timeout"],
            retries=self.config["retries"],
            retry_delay=self.config["retry_delay"],
            retryable_statuses=self.config["retryable_statuses"],
            user_agent=f"conversiontools-python/{VERSION}",
        )

        # Initialize API clients
        self.files = FilesAPI(self.http)
        self.tasks = TasksAPI(self.http)
        self._config_api = ConfigAPI(self.http)

    def convert(
        self,
        conversion_type: str,
        input: ConversionInput,
        output: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        wait: bool = True,
        callback_url: Optional[str] = None,
        polling: Optional[Dict[str, float]] = None,
    ) -> str:
        """
        Simple conversion method - upload, convert, wait, and download in one call (sync)

        Args:
            conversion_type: Conversion type (e.g., 'convert.xml_to_excel')
            input: Input file/URL/stream/buffer
            output: Output file path (optional, defaults to current directory)
            options: Conversion-specific options
            wait: Wait for completion (default: True)
            callback_url: Webhook URL for this specific task
            polling: Custom polling configuration

        Returns:
            Task ID if wait=False, or output file path if wait=True
        """
        # Validate and normalize input
        input_info = validate_conversion_input(input)

        file_id: Optional[str] = None
        task_options: Dict[str, Any] = options.copy() if options else {}

        # Handle different input types
        if input_info["type"] == "file_id":
            # Already uploaded file
            file_id = input_info["value"]
            task_options["file_id"] = file_id
        elif input_info["type"] == "url":
            # URL-based conversion
            task_options["url"] = input_info["value"]
        else:
            # Upload file first
            if input_info["type"] in ("path", "stream", "buffer"):
                upload_options = {}
                if self.config["on_upload_progress"]:
                    upload_options["on_progress"] = self.config["on_upload_progress"]

                file_id = self.files.upload(input_info["value"], upload_options)
                task_options["file_id"] = file_id

        # Create task
        task = self.create_task(
            conversion_type=conversion_type,
            options=task_options,
            callback_url=callback_url or self.config.get("webhook_url"),
        )

        # If not waiting, return task ID
        if not wait:
            return task.id

        # Wait for completion with progress updates
        wait_options = {
            "polling_interval": (polling or {}).get(
                "interval", self.config["polling_interval"]
            ),
            "max_polling_interval": (polling or {}).get(
                "max_interval", self.config["max_polling_interval"]
            ),
        }

        if self.config["on_conversion_progress"]:
            def on_progress(status: Dict[str, Any]) -> None:
                if self.config["on_conversion_progress"]:
                    self.config["on_conversion_progress"](
                        {
                            "loaded": status["conversionProgress"],
                            "total": 100,
                            "percent": status["conversionProgress"],
                            "status": status["status"],
                            "task_id": task.id,
                        }
                    )

            wait_options["on_progress"] = on_progress

        task.wait(wait_options)

        # Download result
        output_path = task.download_to(output)

        return output_path

    async def convert_async(
        self,
        conversion_type: str,
        input: ConversionInput,
        output: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        wait: bool = True,
        callback_url: Optional[str] = None,
        polling: Optional[Dict[str, float]] = None,
    ) -> str:
        """
        Simple conversion method - upload, convert, wait, and download in one call (async)

        Args:
            conversion_type: Conversion type (e.g., 'convert.xml_to_excel')
            input: Input file/URL/stream/buffer
            output: Output file path (optional, defaults to current directory)
            options: Conversion-specific options
            wait: Wait for completion (default: True)
            callback_url: Webhook URL for this specific task
            polling: Custom polling configuration

        Returns:
            Task ID if wait=False, or output file path if wait=True
        """
        # Validate and normalize input
        input_info = validate_conversion_input(input)

        file_id: Optional[str] = None
        task_options: Dict[str, Any] = options.copy() if options else {}

        # Handle different input types
        if input_info["type"] == "file_id":
            # Already uploaded file
            file_id = input_info["value"]
            task_options["file_id"] = file_id
        elif input_info["type"] == "url":
            # URL-based conversion
            task_options["url"] = input_info["value"]
        else:
            # Upload file first
            if input_info["type"] in ("path", "stream", "buffer"):
                upload_options = {}
                if self.config["on_upload_progress"]:
                    upload_options["on_progress"] = self.config["on_upload_progress"]

                file_id = await self.files.upload_async(input_info["value"], upload_options)
                task_options["file_id"] = file_id

        # Create task
        task = await self.create_task_async(
            conversion_type=conversion_type,
            options=task_options,
            callback_url=callback_url or self.config.get("webhook_url"),
        )

        # If not waiting, return task ID
        if not wait:
            return task.id

        # Wait for completion with progress updates
        wait_options = {
            "polling_interval": (polling or {}).get(
                "interval", self.config["polling_interval"]
            ),
            "max_polling_interval": (polling or {}).get(
                "max_interval", self.config["max_polling_interval"]
            ),
        }

        if self.config["on_conversion_progress"]:
            def on_progress(status: Dict[str, Any]) -> None:
                if self.config["on_conversion_progress"]:
                    self.config["on_conversion_progress"](
                        {
                            "loaded": status["conversionProgress"],
                            "total": 100,
                            "percent": status["conversionProgress"],
                            "status": status["status"],
                            "task_id": task.id,
                        }
                    )

            wait_options["on_progress"] = on_progress

        await task.wait_async(wait_options)

        # Download result
        output_path = await task.download_to_async(output)

        return output_path

    def create_task(
        self,
        conversion_type: str,
        options: Dict[str, Any],
        callback_url: Optional[str] = None,
    ) -> Task:
        """Create a conversion task (low-level API) (sync)"""
        request = {
            "type": conversion_type,
            "options": options,
        }
        if callback_url:
            request["callbackUrl"] = callback_url

        response = self.tasks.create(request)

        return Task(
            task_id=response["task_id"],
            task_type=conversion_type,
            tasks_api=self.tasks,
            files_api=self.files,
            status="PENDING",
            default_polling={
                "interval": self.config["polling_interval"],
                "max_interval": self.config["max_polling_interval"],
                "backoff": self.config["polling_backoff"],
            },
        )

    async def create_task_async(
        self,
        conversion_type: str,
        options: Dict[str, Any],
        callback_url: Optional[str] = None,
    ) -> Task:
        """Create a conversion task (low-level API) (async)"""
        request = {
            "type": conversion_type,
            "options": options,
        }
        if callback_url:
            request["callbackUrl"] = callback_url

        response = await self.tasks.create_async(request)

        return Task(
            task_id=response["task_id"],
            task_type=conversion_type,
            tasks_api=self.tasks,
            files_api=self.files,
            status="PENDING",
            default_polling={
                "interval": self.config["polling_interval"],
                "max_interval": self.config["max_polling_interval"],
                "backoff": self.config["polling_backoff"],
            },
        )

    def get_task(self, task_id: str) -> Task:
        """Get an existing task by ID (sync)"""
        response = self.tasks.get_status(task_id)

        return Task(
            task_id=task_id,
            task_type="",  # Type not available from status response
            tasks_api=self.tasks,
            files_api=self.files,
            status=response["status"],
            file_id=response["file_id"],
            error=response["error"],
            conversion_progress=response["conversionProgress"],
            default_polling={
                "interval": self.config["polling_interval"],
                "max_interval": self.config["max_polling_interval"],
                "backoff": self.config["polling_backoff"],
            },
        )

    async def get_task_async(self, task_id: str) -> Task:
        """Get an existing task by ID (async)"""
        response = await self.tasks.get_status_async(task_id)

        return Task(
            task_id=task_id,
            task_type="",  # Type not available from status response
            tasks_api=self.tasks,
            files_api=self.files,
            status=response["status"],
            file_id=response["file_id"],
            error=response["error"],
            conversion_progress=response["conversionProgress"],
            default_polling={
                "interval": self.config["polling_interval"],
                "max_interval": self.config["max_polling_interval"],
                "backoff": self.config["polling_backoff"],
            },
        )

    def get_rate_limits(self) -> Optional[RateLimits]:
        """Get rate limits from last API call"""
        return self.http.get_rate_limits()

    def get_user(self) -> UserInfo:
        """Get authenticated user information (sync)"""
        return self._config_api.get_user_info()

    async def get_user_async(self) -> UserInfo:
        """Get authenticated user information (async)"""
        return await self._config_api.get_user_info_async()

    def get_config(self) -> Dict[str, Any]:
        """Get API configuration (sync)"""
        return self._config_api.get_config()

    async def get_config_async(self) -> Dict[str, Any]:
        """Get API configuration (async)"""
        return await self._config_api.get_config_async()
