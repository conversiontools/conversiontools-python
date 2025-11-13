"""
Smart polling utilities with exponential backoff
"""

import asyncio
import time
from typing import TypeVar, Callable, Awaitable, Optional, Any, Dict
from .errors import TimeoutError

T = TypeVar("T")


async def poll_async(
    fn: Callable[[], Awaitable[T]],
    should_continue: Callable[[T], bool],
    interval: float,
    max_interval: float,
    backoff: float,
    timeout: float = 0,
    on_progress: Optional[Callable[[T], None]] = None,
) -> T:
    """Poll an async function until a condition is met"""

    start_time = time.time()
    current_interval = interval
    result: T

    while True:
        # Execute the function
        result = await fn()

        # Check if we should stop polling
        if not should_continue(result):
            return result

        # Check timeout
        if timeout > 0:
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            if elapsed >= timeout:
                raise TimeoutError(f"Polling timed out after {timeout}ms", timeout)

        # Call progress callback
        if on_progress:
            on_progress(result)

        # Wait before next poll
        await asyncio.sleep(current_interval / 1000)  # Convert to seconds

        # Increase interval with backoff (capped at max_interval)
        current_interval = min(current_interval * backoff, max_interval)


def poll_sync(
    fn: Callable[[], T],
    should_continue: Callable[[T], bool],
    interval: float,
    max_interval: float,
    backoff: float,
    timeout: float = 0,
    on_progress: Optional[Callable[[T], None]] = None,
) -> T:
    """Poll a sync function until a condition is met"""

    start_time = time.time()
    current_interval = interval
    result: T

    while True:
        # Execute the function
        result = fn()

        # Check if we should stop polling
        if not should_continue(result):
            return result

        # Check timeout
        if timeout > 0:
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            if elapsed >= timeout:
                raise TimeoutError(f"Polling timed out after {timeout}ms", timeout)

        # Call progress callback
        if on_progress:
            on_progress(result)

        # Wait before next poll
        time.sleep(current_interval / 1000)  # Convert to seconds

        # Increase interval with backoff (capped at max_interval)
        current_interval = min(current_interval * backoff, max_interval)


async def poll_task_status_async(
    get_status: Callable[[], Awaitable[Dict[str, Any]]],
    interval: float,
    max_interval: float,
    backoff: float,
    timeout: float = 0,
    on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """Poll task status until completion (async)"""

    def should_continue(status: Dict[str, Any]) -> bool:
        # Continue polling if task is pending or running
        return status.get("status") in ("PENDING", "RUNNING")

    return await poll_async(
        get_status, should_continue, interval, max_interval, backoff, timeout, on_progress
    )


def poll_task_status_sync(
    get_status: Callable[[], Dict[str, Any]],
    interval: float,
    max_interval: float,
    backoff: float,
    timeout: float = 0,
    on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """Poll task status until completion (sync)"""

    def should_continue(status: Dict[str, Any]) -> bool:
        # Continue polling if task is pending or running
        return status.get("status") in ("PENDING", "RUNNING")

    return poll_sync(
        get_status, should_continue, interval, max_interval, backoff, timeout, on_progress
    )
