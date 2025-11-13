"""
Progress tracking utilities
"""

from typing import Optional, Dict, Any, Callable


def create_progress_event(loaded: int, total: Optional[int] = None) -> Dict[str, Any]:
    """Create a progress event object"""
    event: Dict[str, Any] = {
        "loaded": loaded,
        "total": total,
    }

    if total and total > 0:
        event["percent"] = round((loaded / total) * 100)

    return event


def calculate_percent(loaded: int, total: int) -> int:
    """Calculate percentage"""
    if total <= 0:
        return 0
    return round((loaded / total) * 100)
