"""
Files API - Upload, download, and manage files
"""

import os
import re
import httpx
from pathlib import Path
from typing import Optional, Union, BinaryIO, Iterator, AsyncIterator, Callable
from urllib.parse import quote
from ..types.config import FileUploadResponse, FileInfo, FileUploadOptions, ProgressEvent
from ..utils.errors import ValidationError
from ..utils.validation import validate_file_id
from ..utils.progress import create_progress_event
from .http import HttpClient


def _extract_filename(disposition: Optional[str]) -> Optional[str]:
    """Extract filename from Content-Disposition header"""
    if not disposition:
        return None
    matches = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', disposition)
    if matches and matches.group(1):
        return matches.group(1).strip('\'"')
    return None


class FilesAPI:
    """Files API for upload, download, and file management"""

    def __init__(self, http: HttpClient):
        self.http = http

    def upload(
        self,
        file_input: Union[str, bytes, BinaryIO],
        options: Optional[FileUploadOptions] = None,
    ) -> str:
        """Upload a file (sync)"""
        file_data: bytes
        filename: Optional[str] = None

        # Handle different input types
        if isinstance(file_input, str):
            # File path
            if not os.path.exists(file_input):
                raise ValidationError(f"File not found: {file_input}")
            if not os.path.isfile(file_input):
                raise ValidationError(f"Not a file: {file_input}")

            with open(file_input, "rb") as f:
                file_data = f.read()
            filename = os.path.basename(file_input)

        elif isinstance(file_input, bytes):
            # Buffer
            file_data = file_input

        elif hasattr(file_input, "read"):
            # Stream/file object
            file_data = file_input.read()
            if hasattr(file_input, "name"):
                filename = os.path.basename(file_input.name)

        else:
            raise ValidationError("Invalid file input type")

        # Track progress if callback provided
        if options and options.get("on_progress"):
            on_progress = options["on_progress"]
            total = len(file_data)
            on_progress(create_progress_event(total, total))

        # Create multipart form data
        files = {"file": (filename or "file", file_data)}

        # Upload file using httpx directly with multipart
        url = f"{self.http.base_url}/files"
        headers = {"Authorization": f"Bearer {self.http.api_token}"}
        if self.http.user_agent:
            headers["User-Agent"] = self.http.user_agent

        with httpx.Client(timeout=self.http.timeout) as client:
            response = client.post(url, headers=headers, files=files)

        if not response.is_success:
            self.http._handle_error_response(response)

        result: FileUploadResponse = response.json()

        if result.get("error"):
            raise ValidationError(result["error"])

        return result["file_id"]

    async def upload_async(
        self,
        file_input: Union[str, bytes, BinaryIO],
        options: Optional[FileUploadOptions] = None,
    ) -> str:
        """Upload a file (async)"""
        file_data: bytes
        filename: Optional[str] = None

        # Handle different input types
        if isinstance(file_input, str):
            # File path
            if not os.path.exists(file_input):
                raise ValidationError(f"File not found: {file_input}")
            if not os.path.isfile(file_input):
                raise ValidationError(f"Not a file: {file_input}")

            with open(file_input, "rb") as f:
                file_data = f.read()
            filename = os.path.basename(file_input)

        elif isinstance(file_input, bytes):
            # Buffer
            file_data = file_input

        elif hasattr(file_input, "read"):
            # Stream/file object
            file_data = file_input.read()
            if hasattr(file_input, "name"):
                filename = os.path.basename(file_input.name)

        else:
            raise ValidationError("Invalid file input type")

        # Track progress if callback provided
        if options and options.get("on_progress"):
            on_progress = options["on_progress"]
            total = len(file_data)
            on_progress(create_progress_event(total, total))

        # Create multipart form data
        files = {"file": (filename or "file", file_data)}

        # Upload file using httpx directly with multipart
        url = f"{self.http.base_url}/files"
        headers = {"Authorization": f"Bearer {self.http.api_token}"}
        if self.http.user_agent:
            headers["User-Agent"] = self.http.user_agent

        async with httpx.AsyncClient(timeout=self.http.timeout) as client:
            response = await client.post(url, headers=headers, files=files)

        if not response.is_success:
            self.http._handle_error_response(response)

        result: FileUploadResponse = response.json()

        if result.get("error"):
            raise ValidationError(result["error"])

        return result["file_id"]

    def get_info(self, file_id: str) -> FileInfo:
        """Get file metadata (sync)"""
        validate_file_id(file_id)
        return self.http.get(f"/files/{quote(file_id)}/info")

    async def get_info_async(self, file_id: str) -> FileInfo:
        """Get file metadata (async)"""
        validate_file_id(file_id)
        return await self.http.get_async(f"/files/{quote(file_id)}/info")

    def download_bytes(self, file_id: str) -> bytes:
        """Download file as bytes (sync)"""
        validate_file_id(file_id)
        response = self.http.get(f"/files/{quote(file_id)}", raw=True)
        return response.content

    async def download_bytes_async(self, file_id: str) -> bytes:
        """Download file as bytes (async)"""
        validate_file_id(file_id)
        response = await self.http.get_async(f"/files/{quote(file_id)}", raw=True)
        return response.content

    def download_stream(self, file_id: str) -> Iterator[bytes]:
        """Download file as a byte stream (sync)"""
        validate_file_id(file_id)
        url = f"{self.http.base_url}/files/{quote(file_id)}"
        headers = {"Authorization": f"Bearer {self.http.api_token}"}
        if self.http.user_agent:
            headers["User-Agent"] = self.http.user_agent

        with httpx.Client(timeout=self.http.timeout) as client:
            with client.stream("GET", url, headers=headers) as response:
                if not response.is_success:
                    self.http._handle_error_response(response)
                self.http._extract_rate_limits(response.headers)
                yield from response.iter_bytes()

    async def download_stream_async(self, file_id: str) -> AsyncIterator[bytes]:
        """Download file as a byte stream (async)"""
        validate_file_id(file_id)
        url = f"{self.http.base_url}/files/{quote(file_id)}"
        headers = {"Authorization": f"Bearer {self.http.api_token}"}
        if self.http.user_agent:
            headers["User-Agent"] = self.http.user_agent

        async with httpx.AsyncClient(timeout=self.http.timeout) as client:
            async with client.stream("GET", url, headers=headers) as response:
                if not response.is_success:
                    self.http._handle_error_response(response)
                self.http._extract_rate_limits(response.headers)
                async for chunk in response.aiter_bytes():
                    yield chunk

    def download_to(
        self,
        file_id: str,
        output_path: Optional[str] = None,
        on_progress: Optional[Callable[[ProgressEvent], None]] = None,
    ) -> str:
        """Download file to path (sync)"""
        validate_file_id(file_id)

        if on_progress:
            url = f"{self.http.base_url}/files/{quote(file_id)}"
            headers = {"Authorization": f"Bearer {self.http.api_token}"}
            if self.http.user_agent:
                headers["User-Agent"] = self.http.user_agent

            with httpx.Client(timeout=self.http.timeout) as client:
                with client.stream("GET", url, headers=headers) as response:
                    if not response.is_success:
                        self.http._handle_error_response(response)
                    self.http._extract_rate_limits(response.headers)

                    filename = (
                        output_path
                        or _extract_filename(response.headers.get("content-disposition"))
                        or "result"
                    )
                    output_dir = os.path.dirname(filename)
                    if output_dir and not os.path.exists(output_dir):
                        os.makedirs(output_dir, exist_ok=True)

                    content_length = response.headers.get("content-length")
                    total = int(content_length) if content_length else None
                    loaded = 0

                    with open(filename, "wb") as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)
                            loaded += len(chunk)
                            on_progress(create_progress_event(loaded, total))

            return filename

        response = self.http.get(f"/files/{quote(file_id)}", raw=True)

        filename = output_path or _extract_filename(
            response.headers.get("content-disposition")
        ) or "result"

        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(filename, "wb") as f:
            f.write(response.content)

        return filename

    async def download_to_async(
        self,
        file_id: str,
        output_path: Optional[str] = None,
        on_progress: Optional[Callable[[ProgressEvent], None]] = None,
    ) -> str:
        """Download file to path (async)"""
        validate_file_id(file_id)

        if on_progress:
            url = f"{self.http.base_url}/files/{quote(file_id)}"
            headers = {"Authorization": f"Bearer {self.http.api_token}"}
            if self.http.user_agent:
                headers["User-Agent"] = self.http.user_agent

            async with httpx.AsyncClient(timeout=self.http.timeout) as client:
                async with client.stream("GET", url, headers=headers) as response:
                    if not response.is_success:
                        self.http._handle_error_response(response)
                    self.http._extract_rate_limits(response.headers)

                    filename = (
                        output_path
                        or _extract_filename(response.headers.get("content-disposition"))
                        or "result"
                    )
                    output_dir = os.path.dirname(filename)
                    if output_dir and not os.path.exists(output_dir):
                        os.makedirs(output_dir, exist_ok=True)

                    content_length = response.headers.get("content-length")
                    total = int(content_length) if content_length else None
                    loaded = 0

                    with open(filename, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
                            loaded += len(chunk)
                            on_progress(create_progress_event(loaded, total))

            return filename

        response = await self.http.get_async(f"/files/{quote(file_id)}", raw=True)

        filename = output_path or _extract_filename(
            response.headers.get("content-disposition")
        ) or "result"

        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(filename, "wb") as f:
            f.write(response.content)

        return filename
