"""
Retry utilities with exponential backoff
"""

import asyncio
import time
from typing import TypeVar, Callable, Awaitable, Optional, List
from .errors import NetworkError, TimeoutError

T = TypeVar("T")


def should_retry_error(
    error: Exception,
    retryable_statuses: List[int],
    should_retry_fn: Optional[Callable[[Exception], bool]] = None,
) -> bool:
    """Determine if an error should trigger a retry"""

    # Custom retry logic
    if should_retry_fn:
        return should_retry_fn(error)

    # Network errors should be retried
    if isinstance(error, (NetworkError, TimeoutError)):
        return True

    # HTTP status code based retry
    if hasattr(error, "status") and error.status in retryable_statuses:
        return True

    # Connection errors
    if isinstance(error, (ConnectionError, OSError)):
        return True

    return False


async def with_retry_async(
    fn: Callable[[], Awaitable[T]],
    retries: int,
    retry_delay: float,
    retryable_statuses: List[int],
    should_retry_fn: Optional[Callable[[Exception], bool]] = None,
) -> T:
    """Execute an async function with retry logic and exponential backoff"""

    last_error: Optional[Exception] = None
    attempt = 0

    while attempt <= retries:
        try:
            return await fn()
        except Exception as error:
            last_error = error
            attempt += 1

            # Don't retry if max attempts reached
            if attempt > retries:
                break

            # Check if error should trigger retry
            if not should_retry_error(error, retryable_statuses, should_retry_fn):
                raise

            # Calculate delay with exponential backoff
            delay = retry_delay * (2 ** (attempt - 1))

            # Wait before retrying
            await asyncio.sleep(delay / 1000)  # Convert to seconds

    # All retries exhausted
    if last_error:
        raise last_error
    raise RuntimeError("Retry failed without error")


def with_retry_sync(
    fn: Callable[[], T],
    retries: int,
    retry_delay: float,
    retryable_statuses: List[int],
    should_retry_fn: Optional[Callable[[Exception], bool]] = None,
) -> T:
    """Execute a sync function with retry logic and exponential backoff"""

    last_error: Optional[Exception] = None
    attempt = 0

    while attempt <= retries:
        try:
            return fn()
        except Exception as error:
            last_error = error
            attempt += 1

            # Don't retry if max attempts reached
            if attempt > retries:
                break

            # Check if error should trigger retry
            if not should_retry_error(error, retryable_statuses, should_retry_fn):
                raise

            # Calculate delay with exponential backoff
            delay = retry_delay * (2 ** (attempt - 1))

            # Wait before retrying
            time.sleep(delay / 1000)  # Convert to seconds

    # All retries exhausted
    if last_error:
        raise last_error
    raise RuntimeError("Retry failed without error")
