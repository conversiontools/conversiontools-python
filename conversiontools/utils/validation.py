"""
Input validation utilities
"""

import re
from typing import Dict, Any, Union, BinaryIO
from urllib.parse import urlparse
from .errors import ValidationError


def validate_conversion_type(conversion_type: str) -> None:
    """Validate conversion type format"""
    if not conversion_type or not isinstance(conversion_type, str):
        raise ValidationError("Conversion type is required and must be a string")

    # Check if it follows the pattern convert.source_to_target
    if not conversion_type.startswith("convert."):
        raise ValidationError(
            f'Invalid conversion type format: "{conversion_type}". '
            'Expected format: "convert.source_to_target"'
        )


def validate_conversion_input(
    conversion_input: Any,
) -> Dict[str, Any]:
    """Validate and normalize conversion input"""
    if not conversion_input:
        raise ValidationError("Input is required")

    # String input = file path
    if isinstance(conversion_input, str):
        return {"type": "path", "value": conversion_input}

    # Bytes input = buffer
    if isinstance(conversion_input, bytes):
        return {"type": "buffer", "value": conversion_input}

    # File-like object = stream
    if hasattr(conversion_input, "read"):
        return {"type": "stream", "value": conversion_input}

    # Object input (dict)
    if isinstance(conversion_input, dict):
        # Explicit path
        if "path" in conversion_input and isinstance(conversion_input["path"], str):
            return {"type": "path", "value": conversion_input["path"]}

        # URL
        if "url" in conversion_input and isinstance(conversion_input["url"], str):
            if not is_valid_url(conversion_input["url"]):
                raise ValidationError(f"Invalid URL: {conversion_input['url']}")
            return {"type": "url", "value": conversion_input["url"]}

        # Stream
        if "stream" in conversion_input and conversion_input["stream"]:
            return {"type": "stream", "value": conversion_input["stream"]}

        # Buffer
        if "buffer" in conversion_input and isinstance(
            conversion_input["buffer"], bytes
        ):
            return {
                "type": "buffer",
                "value": conversion_input["buffer"],
                "filename": conversion_input.get("filename"),
            }

        # File ID
        if "file_id" in conversion_input and isinstance(
            conversion_input["file_id"], str
        ):
            return {"type": "file_id", "value": conversion_input["file_id"]}

        # Also support fileId (camelCase)
        if "fileId" in conversion_input and isinstance(conversion_input["fileId"], str):
            return {"type": "file_id", "value": conversion_input["fileId"]}

    raise ValidationError(
        "Invalid input format. Expected: str, bytes, file-like, "
        '{ "path" }, { "url" }, { "stream" }, { "buffer" }, or { "file_id" }'
    )


def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_api_token(token: str) -> None:
    """Validate API token"""
    if not token or not isinstance(token, str):
        raise ValidationError("API token is required and must be a string")

    if not token.strip():
        raise ValidationError("API token cannot be empty")


def validate_file_id(file_id: str) -> None:
    """Validate file ID format"""
    if not file_id or not isinstance(file_id, str):
        raise ValidationError("File ID is required and must be a string")

    # File IDs are typically 32-character hex strings
    if not re.match(r"^[a-f0-9]{32}$", file_id, re.IGNORECASE):
        raise ValidationError(
            f'Invalid file ID format: "{file_id}". '
            "Expected 32-character hexadecimal string"
        )


def validate_task_id(task_id: str) -> None:
    """Validate task ID format"""
    if not task_id or not isinstance(task_id, str):
        raise ValidationError("Task ID is required and must be a string")

    # Task IDs are typically 32-character hex strings
    if not re.match(r"^[a-f0-9]{32}$", task_id, re.IGNORECASE):
        raise ValidationError(
            f'Invalid task ID format: "{task_id}". '
            "Expected 32-character hexadecimal string"
        )
