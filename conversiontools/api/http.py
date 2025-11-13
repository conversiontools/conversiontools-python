"""
HTTP client with retry logic for Conversion Tools API
"""

import httpx
from typing import Optional, Dict, Any, Literal
from ..types.config import RateLimits
from ..utils.errors import (
    ConversionToolsError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    FileNotFoundError,
    TaskNotFoundError,
    NetworkError,
    TimeoutError,
)
from ..utils.retry import with_retry_sync, with_retry_async


DEFAULT_BASE_URL = "https://api.conversiontools.io/v1"
DEFAULT_TIMEOUT = 300000  # 5 minutes in milliseconds
DEFAULT_RETRIES = 3
DEFAULT_RETRY_DELAY = 1000  # milliseconds
DEFAULT_RETRYABLE_STATUSES = [408, 500, 502, 503, 504]


class HttpClient:
    """HTTP client with retry logic"""

    def __init__(
        self,
        api_token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        retryable_statuses: Optional[list[int]] = None,
        user_agent: Optional[str] = None,
    ):
        self.api_token = api_token
        self.base_url = base_url
        self.timeout = timeout / 1000  # Convert to seconds for httpx
        self.retries = retries
        self.retry_delay = retry_delay
        self.retryable_statuses = (
            retryable_statuses if retryable_statuses else DEFAULT_RETRYABLE_STATUSES
        )
        self.user_agent = user_agent
        self.last_rate_limits: Optional[RateLimits] = None

    def get_rate_limits(self) -> Optional[RateLimits]:
        """Get the last rate limits from API response headers"""
        return self.last_rate_limits

    def _extract_rate_limits(self, headers: httpx.Headers) -> None:
        """Extract rate limits from response headers"""
        limits: Dict[str, Any] = {}

        daily_limit = headers.get("x-ratelimit-limit-tasks")
        daily_remaining = headers.get("x-ratelimit-limit-tasks-remaining")
        if daily_limit and daily_remaining:
            limits["daily"] = {
                "limit": int(daily_limit),
                "remaining": int(daily_remaining),
            }

        monthly_limit = headers.get("x-ratelimit-limit-tasks-monthly")
        monthly_remaining = headers.get("x-ratelimit-limit-tasks-monthly-remaining")
        if monthly_limit and monthly_remaining:
            limits["monthly"] = {
                "limit": int(monthly_limit),
                "remaining": int(monthly_remaining),
            }

        file_size = headers.get("x-ratelimit-limit-filesize")
        if file_size:
            limits["file_size"] = int(file_size)

        if limits:
            self.last_rate_limits = limits  # type: ignore

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses"""
        status = response.status_code

        # Try to parse error message from response
        error_message: str
        error_data: Optional[Any] = None

        try:
            error_data = response.json()
            error_message = error_data.get("error") or response.reason_phrase
        except Exception:
            error_message = response.reason_phrase

        # Handle specific status codes
        if status == 401:
            raise AuthenticationError(error_message)
        elif status == 400:
            raise ValidationError(error_message, error_data)
        elif status == 404:
            # Determine if it's a file or task not found
            error_lower = error_message.lower()
            if "file" in error_lower:
                raise FileNotFoundError(error_message)
            elif "task" in error_lower:
                raise TaskNotFoundError(error_message)
            raise ConversionToolsError(error_message, "NOT_FOUND", 404)
        elif status == 429:
            raise RateLimitError(
                error_message
                or "Rate limit exceeded. Upgrade your plan at https://conversiontools.io/pricing",
                self.last_rate_limits,
            )
        elif status == 408:
            raise TimeoutError(error_message)
        else:
            raise ConversionToolsError(error_message, "HTTP_ERROR", status, error_data)

    def request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        body: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        raw: bool = False,
    ) -> Any:
        """Make an HTTP request with retry logic (sync)"""

        def make_request() -> Any:
            url = f"{self.base_url}{path}"

            # Prepare headers
            request_headers: Dict[str, str] = {
                "Authorization": f"Bearer {self.api_token}",
            }
            if self.user_agent:
                request_headers["User-Agent"] = self.user_agent
            if headers:
                request_headers.update(headers)

            # Add content-type for JSON bodies
            if body and isinstance(body, str):
                request_headers["Content-Type"] = "application/json"

            # Make request
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    if method == "GET":
                        response = client.get(url, headers=request_headers)
                    elif method == "POST":
                        response = client.post(url, headers=request_headers, content=body)
                    elif method == "PUT":
                        response = client.put(url, headers=request_headers, content=body)
                    elif method == "DELETE":
                        response = client.delete(url, headers=request_headers)
                    else:
                        raise ValueError(f"Unsupported method: {method}")

            except httpx.TimeoutException as e:
                raise TimeoutError(
                    f"Request timed out after {self.timeout}s", self.timeout * 1000
                )
            except httpx.RequestError as e:
                raise NetworkError(f"Network request failed: {str(e)}", e)

            # Extract rate limits from headers
            self._extract_rate_limits(response.headers)

            # Handle error responses
            if not response.is_success:
                self._handle_error_response(response)

            # Return raw response if requested
            if raw:
                return response

            # Parse JSON response
            data = response.json()

            # Check for error in response body
            if isinstance(data, dict) and data.get("error"):
                raise ConversionToolsError(
                    data["error"], "API_ERROR", response.status_code, data
                )

            return data

        return with_retry_sync(
            make_request,
            self.retries,
            self.retry_delay,
            self.retryable_statuses,
        )

    async def request_async(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        body: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        raw: bool = False,
    ) -> Any:
        """Make an HTTP request with retry logic (async)"""

        async def make_request() -> Any:
            url = f"{self.base_url}{path}"

            # Prepare headers
            request_headers: Dict[str, str] = {
                "Authorization": f"Bearer {self.api_token}",
            }
            if self.user_agent:
                request_headers["User-Agent"] = self.user_agent
            if headers:
                request_headers.update(headers)

            # Add content-type for JSON bodies
            if body and isinstance(body, str):
                request_headers["Content-Type"] = "application/json"

            # Make request
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    if method == "GET":
                        response = await client.get(url, headers=request_headers)
                    elif method == "POST":
                        response = await client.post(
                            url, headers=request_headers, content=body
                        )
                    elif method == "PUT":
                        response = await client.put(
                            url, headers=request_headers, content=body
                        )
                    elif method == "DELETE":
                        response = await client.delete(url, headers=request_headers)
                    else:
                        raise ValueError(f"Unsupported method: {method}")

            except httpx.TimeoutException as e:
                raise TimeoutError(
                    f"Request timed out after {self.timeout}s", self.timeout * 1000
                )
            except httpx.RequestError as e:
                raise NetworkError(f"Network request failed: {str(e)}", e)

            # Extract rate limits from headers
            self._extract_rate_limits(response.headers)

            # Handle error responses
            if not response.is_success:
                self._handle_error_response(response)

            # Return raw response if requested
            if raw:
                return response

            # Parse JSON response
            data = response.json()

            # Check for error in response body
            if isinstance(data, dict) and data.get("error"):
                raise ConversionToolsError(
                    data["error"], "API_ERROR", response.status_code, data
                )

            return data

        return await with_retry_async(
            make_request,
            self.retries,
            self.retry_delay,
            self.retryable_statuses,
        )

    def get(self, path: str, **kwargs: Any) -> Any:
        """Make a GET request (sync)"""
        return self.request("GET", path, **kwargs)

    def post(self, path: str, body: Optional[Any] = None, **kwargs: Any) -> Any:
        """Make a POST request (sync)"""
        return self.request("POST", path, body=body, **kwargs)

    async def get_async(self, path: str, **kwargs: Any) -> Any:
        """Make a GET request (async)"""
        return await self.request_async("GET", path, **kwargs)

    async def post_async(
        self, path: str, body: Optional[Any] = None, **kwargs: Any
    ) -> Any:
        """Make a POST request (async)"""
        return await self.request_async("POST", path, body=body, **kwargs)
