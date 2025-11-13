"""
Files API - Upload, download, and manage files
"""

import os
import re
from pathlib import Path
from typing import Optional, Union, BinaryIO
from urllib.parse import quote
from ..types.config import FileUploadResponse, FileInfo, FileUploadOptions
from ..utils.errors import ValidationError
from ..utils.validation import validate_file_id
from ..utils.progress import create_progress_event
from .http import HttpClient


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
        import httpx

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
        import httpx

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

    def download_to(self, file_id: str, output_path: Optional[str] = None) -> str:
        """Download file to path (sync)"""
        validate_file_id(file_id)
        response = self.http.get(f"/files/{quote(file_id)}", raw=True)

        # Determine output filename
        filename = output_path
        if not filename:
            # Try to get filename from Content-Disposition header
            disposition = response.headers.get("content-disposition")
            if disposition:
                matches = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', disposition)
                if matches and matches.group(1):
                    filename = matches.group(1).strip('\'"')

            filename = filename or "result"

        # Ensure directory exists
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Write file
        with open(filename, "wb") as f:
            f.write(response.content)

        return filename

    async def download_to_async(
        self, file_id: str, output_path: Optional[str] = None
    ) -> str:
        """Download file to path (async)"""
        validate_file_id(file_id)
        response = await self.http.get_async(f"/files/{quote(file_id)}", raw=True)

        # Determine output filename
        filename = output_path
        if not filename:
            # Try to get filename from Content-Disposition header
            disposition = response.headers.get("content-disposition")
            if disposition:
                matches = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', disposition)
                if matches and matches.group(1):
                    filename = matches.group(1).strip('\'"')

            filename = filename or "result"

        # Ensure directory exists
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Write file
        with open(filename, "wb") as f:
            f.write(response.content)

        return filename
