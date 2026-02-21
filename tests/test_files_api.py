"""Tests for FilesAPI"""

import io
import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from conversiontools.api.files import FilesAPI
from conversiontools.api.http import HttpClient
from conversiontools.utils.errors import ValidationError

FILE_ID = "a" * 32


def make_http_client() -> HttpClient:
    client = MagicMock(spec=HttpClient)
    client.base_url = "https://api.conversiontools.io/v1"
    client.api_token = "test_token"
    client.user_agent = "conversiontools-python/2.0.0"
    client.timeout = 300.0
    return client


class TestUpload:
    def test_upload_file_path(self, tmp_path):
        http = make_http_client()
        http.post.return_value = {"error": None, "file_id": FILE_ID}
        api = FilesAPI(http)

        test_file = tmp_path / "test.xml"
        test_file.write_bytes(b"<root/>")

        with patch("conversiontools.api.files.httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.is_success = True
            mock_response.json.return_value = {"error": None, "file_id": FILE_ID}
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_class.return_value.__exit__ = MagicMock(return_value=False)

            file_id = api.upload(str(test_file))

        assert file_id == FILE_ID

    def test_upload_nonexistent_file_raises(self):
        api = FilesAPI(make_http_client())
        with pytest.raises(ValidationError, match="not found"):
            api.upload("/nonexistent/file.xml")

    def test_upload_directory_raises(self, tmp_path):
        api = FilesAPI(make_http_client())
        with pytest.raises(ValidationError, match="Not a file"):
            api.upload(str(tmp_path))

    def test_upload_bytes(self):
        api = FilesAPI(make_http_client())
        with patch("conversiontools.api.files.httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.is_success = True
            mock_response.json.return_value = {"error": None, "file_id": FILE_ID}
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_class.return_value.__exit__ = MagicMock(return_value=False)

            file_id = api.upload(b"binary data")

        assert file_id == FILE_ID

    def test_upload_stream(self):
        api = FilesAPI(make_http_client())
        stream = io.BytesIO(b"stream data")

        with patch("conversiontools.api.files.httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.is_success = True
            mock_response.json.return_value = {"error": None, "file_id": FILE_ID}
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_class.return_value.__exit__ = MagicMock(return_value=False)

            file_id = api.upload(stream)

        assert file_id == FILE_ID

    def test_upload_calls_on_progress(self, tmp_path):
        api = FilesAPI(make_http_client())
        test_file = tmp_path / "test.xml"
        test_file.write_bytes(b"<root/>")

        with patch("conversiontools.api.files.httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.is_success = True
            mock_response.json.return_value = {"error": None, "file_id": FILE_ID}
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_class.return_value.__exit__ = MagicMock(return_value=False)

            on_progress = MagicMock()
            api.upload(str(test_file), {"on_progress": on_progress})

        on_progress.assert_called_once()

    def test_upload_invalid_type_raises(self):
        api = FilesAPI(make_http_client())
        with pytest.raises(ValidationError):
            api.upload(12345)  # type: ignore


class TestGetInfo:
    def test_get_info(self):
        http = make_http_client()
        info = {"error": None, "file_id": FILE_ID, "name": "test.xml", "size": 1024}
        http.get.return_value = info
        api = FilesAPI(http)

        result = api.get_info(FILE_ID)

        assert result == info
        http.get.assert_called_once_with(f"/files/{FILE_ID}/info")

    def test_get_info_invalid_id_raises(self):
        api = FilesAPI(make_http_client())
        with pytest.raises(ValidationError):
            api.get_info("")

    def test_get_info_short_id_raises(self):
        api = FilesAPI(make_http_client())
        with pytest.raises(ValidationError):
            api.get_info("short")


class TestDownloadBytes:
    def test_download_bytes(self):
        http = make_http_client()
        mock_response = MagicMock()
        mock_response.content = b"file content"
        http.get.return_value = mock_response
        api = FilesAPI(http)

        result = api.download_bytes(FILE_ID)

        assert result == b"file content"
        http.get.assert_called_once_with(f"/files/{FILE_ID}", raw=True)


class TestDownloadStream:
    def test_download_stream_yields_chunks(self):
        api = FilesAPI(make_http_client())

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.headers = {}
        mock_response.iter_bytes.return_value = iter([b"chunk1", b"chunk2"])

        mock_stream_cm = MagicMock()
        mock_stream_cm.__enter__ = MagicMock(return_value=mock_response)
        mock_stream_cm.__exit__ = MagicMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream.return_value = mock_stream_cm

        mock_client_cm = MagicMock()
        mock_client_cm.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cm.__exit__ = MagicMock(return_value=False)

        with patch("conversiontools.api.files.httpx.Client", return_value=mock_client_cm):
            chunks = list(api.download_stream(FILE_ID))

        assert chunks == [b"chunk1", b"chunk2"]

    def test_download_stream_invalid_id_raises(self):
        api = FilesAPI(make_http_client())
        with pytest.raises(ValidationError):
            list(api.download_stream("bad"))

    async def test_download_stream_async_yields_chunks(self):
        api = FilesAPI(make_http_client())

        async def mock_aiter_bytes():
            for chunk in [b"async1", b"async2"]:
                yield chunk

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.headers = {}
        mock_response.aiter_bytes = mock_aiter_bytes

        mock_stream_cm = MagicMock()
        mock_stream_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_cm.__aexit__ = AsyncMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream.return_value = mock_stream_cm

        mock_client_cm = MagicMock()
        mock_client_cm.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cm.__aexit__ = AsyncMock(return_value=False)

        with patch("conversiontools.api.files.httpx.AsyncClient", return_value=mock_client_cm):
            chunks = []
            async for chunk in api.download_stream_async(FILE_ID):
                chunks.append(chunk)

        assert chunks == [b"async1", b"async2"]


class TestDownloadTo:
    def test_download_to_path(self, tmp_path):
        http = make_http_client()
        mock_response = MagicMock()
        mock_response.content = b"file content"
        mock_response.headers = {"content-disposition": 'attachment; filename="output.csv"'}
        http.get.return_value = mock_response
        api = FilesAPI(http)

        output = str(tmp_path / "output.csv")
        result = api.download_to(FILE_ID, output)

        assert result == output
        assert os.path.exists(output)
        with open(output, "rb") as f:
            assert f.read() == b"file content"

    def test_download_to_uses_content_disposition(self, tmp_path):
        http = make_http_client()
        mock_response = MagicMock()
        mock_response.content = b"data"
        mock_response.headers = {"content-disposition": 'attachment; filename="result.xml"'}
        http.get.return_value = mock_response
        api = FilesAPI(http)

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            result = api.download_to(FILE_ID)

        assert "result.xml" in result

    def test_download_to_with_on_progress(self, tmp_path):
        api = FilesAPI(make_http_client())

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.headers = {
            "content-length": "11",
            "content-disposition": 'attachment; filename="out.csv"',
        }
        mock_response.iter_bytes.return_value = iter([b"hello", b" world"])

        mock_stream_cm = MagicMock()
        mock_stream_cm.__enter__ = MagicMock(return_value=mock_response)
        mock_stream_cm.__exit__ = MagicMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream.return_value = mock_stream_cm

        mock_client_cm = MagicMock()
        mock_client_cm.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cm.__exit__ = MagicMock(return_value=False)

        progress_events = []
        output = str(tmp_path / "out.csv")

        with patch("conversiontools.api.files.httpx.Client", return_value=mock_client_cm):
            result = api.download_to(FILE_ID, output, on_progress=lambda p: progress_events.append(p))

        assert result == output
        assert len(progress_events) == 2
        assert progress_events[0]["loaded"] == 5
        assert progress_events[1]["loaded"] == 11
        assert progress_events[1]["total"] == 11
        assert progress_events[1]["percent"] == 100

    def test_download_to_with_on_progress_no_content_length(self, tmp_path):
        api = FilesAPI(make_http_client())

        mock_headers = MagicMock()
        mock_headers.get = lambda k, d=None: (
            'attachment; filename="out.csv"' if k == "content-disposition" else None
        )

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.headers = mock_headers
        mock_response.iter_bytes.return_value = iter([b"data"])

        mock_stream_cm = MagicMock()
        mock_stream_cm.__enter__ = MagicMock(return_value=mock_response)
        mock_stream_cm.__exit__ = MagicMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream.return_value = mock_stream_cm

        mock_client_cm = MagicMock()
        mock_client_cm.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cm.__exit__ = MagicMock(return_value=False)

        output = str(tmp_path / "out.csv")
        progress_events = []

        with patch("conversiontools.api.files.httpx.Client", return_value=mock_client_cm):
            result = api.download_to(FILE_ID, output, on_progress=lambda p: progress_events.append(p))

        assert result == output
        assert len(progress_events) == 1
        assert progress_events[0]["total"] is None

    def test_download_to_invalid_id_raises(self):
        api = FilesAPI(make_http_client())
        with pytest.raises(ValidationError):
            api.download_to("bad_id")

    async def test_download_to_async_with_progress(self, tmp_path):
        api = FilesAPI(make_http_client())

        async def mock_aiter_bytes():
            for chunk in [b"hello", b" world"]:
                yield chunk

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.headers = {
            "content-length": "11",
            "content-disposition": 'attachment; filename="out.csv"',
        }
        mock_response.aiter_bytes = mock_aiter_bytes

        mock_stream_cm = MagicMock()
        mock_stream_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_cm.__aexit__ = AsyncMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream.return_value = mock_stream_cm

        mock_client_cm = MagicMock()
        mock_client_cm.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cm.__aexit__ = AsyncMock(return_value=False)

        progress_events = []
        output = str(tmp_path / "out.csv")

        with patch("conversiontools.api.files.httpx.AsyncClient", return_value=mock_client_cm):
            result = await api.download_to_async(
                FILE_ID, output, on_progress=lambda p: progress_events.append(p)
            )

        assert result == output
        assert len(progress_events) == 2
        assert progress_events[1]["loaded"] == 11
