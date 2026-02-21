"""Tests for Task model"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from conversiontools.models.task import Task
from conversiontools.api.tasks import TasksAPI
from conversiontools.api.files import FilesAPI
from conversiontools.utils.errors import ConversionError

FILE_ID = "a" * 32
TASK_ID = "b" * 32


def make_task(status="PENDING", file_id=None, error=None, progress=0):
    tasks_api = MagicMock(spec=TasksAPI)
    files_api = MagicMock(spec=FilesAPI)
    return Task(
        task_id=TASK_ID,
        task_type="convert.xml_to_csv",
        tasks_api=tasks_api,
        files_api=files_api,
        status=status,
        file_id=file_id,
        error=error,
        conversion_progress=progress,
    ), tasks_api, files_api


class TestTaskProperties:
    def test_id_and_type(self):
        task, _, _ = make_task()
        assert task.id == TASK_ID
        assert task.type == "convert.xml_to_csv"

    def test_status_properties(self):
        task, _, _ = make_task("PENDING")
        assert task.is_running is True
        assert task.is_complete is False
        assert task.is_success is False
        assert task.is_error is False

    def test_success_properties(self):
        task, _, _ = make_task("SUCCESS", file_id=FILE_ID, progress=100)
        assert task.is_success is True
        assert task.is_complete is True
        assert task.is_running is False
        assert task.file_id == FILE_ID
        assert task.conversion_progress == 100

    def test_error_properties(self):
        task, _, _ = make_task("ERROR", error="conversion failed")
        assert task.is_error is True
        assert task.is_complete is True
        assert task.error == "conversion failed"

    def test_running_status(self):
        task, _, _ = make_task("RUNNING")
        assert task.is_running is True

    def test_to_dict(self):
        task, _, _ = make_task("SUCCESS", file_id=FILE_ID)
        d = task.to_dict()
        assert d["id"] == TASK_ID
        assert d["type"] == "convert.xml_to_csv"
        assert d["status"] == "SUCCESS"
        assert d["file_id"] == FILE_ID


class TestTaskGetStatus:
    def test_get_status_calls_api_and_updates(self):
        task, tasks_api, _ = make_task("PENDING")
        tasks_api.get_status.return_value = {
            "status": "SUCCESS", "file_id": FILE_ID, "error": None, "conversionProgress": 100,
        }
        result = task.get_status()
        assert result["status"] == "SUCCESS"
        assert task.status == "SUCCESS"
        assert task.file_id == FILE_ID
        tasks_api.get_status.assert_called_once_with(TASK_ID)

    def test_refresh_updates_status(self):
        task, tasks_api, _ = make_task("PENDING")
        tasks_api.get_status.return_value = {
            "status": "RUNNING", "file_id": None, "error": None, "conversionProgress": 50,
        }
        task.refresh()
        assert task.status == "RUNNING"
        assert task.conversion_progress == 50


class TestTaskWait:
    def test_wait_success(self):
        task, tasks_api, _ = make_task("PENDING")
        tasks_api.get_status.return_value = {
            "status": "SUCCESS", "file_id": FILE_ID, "error": None, "conversionProgress": 100,
        }
        with patch("conversiontools.models.task.poll_task_status_sync") as mock_poll:
            mock_poll.return_value = {
                "status": "SUCCESS", "file_id": FILE_ID, "error": None, "conversionProgress": 100,
            }
            task.wait()

        assert task.status == "SUCCESS"

    def test_wait_error_raises(self):
        task, _, _ = make_task("PENDING")
        with patch("conversiontools.models.task.poll_task_status_sync") as mock_poll:
            mock_poll.return_value = {
                "status": "ERROR", "file_id": None, "error": "file corrupt", "conversionProgress": 0,
            }
            with pytest.raises(ConversionError, match="file corrupt"):
                task.wait()

    def test_wait_passes_on_progress(self):
        task, _, _ = make_task("PENDING")
        on_progress = MagicMock()
        with patch("conversiontools.models.task.poll_task_status_sync") as mock_poll:
            mock_poll.return_value = {
                "status": "SUCCESS", "file_id": FILE_ID, "error": None, "conversionProgress": 100,
            }
            task.wait({"on_progress": on_progress})

        _, kwargs = mock_poll.call_args
        assert kwargs.get("on_progress") == on_progress or mock_poll.call_args[0][-1] == on_progress

    async def test_wait_async_success(self):
        task, _, _ = make_task("PENDING")
        with patch("conversiontools.models.task.poll_task_status_async") as mock_poll:
            mock_poll.return_value = {
                "status": "SUCCESS", "file_id": FILE_ID, "error": None, "conversionProgress": 100,
            }
            # Make mock_poll awaitable
            import asyncio
            mock_poll.return_value = mock_poll.return_value
            mock_poll.side_effect = None

            async def async_return(*args, **kwargs):
                return {"status": "SUCCESS", "file_id": FILE_ID, "error": None, "conversionProgress": 100}

            mock_poll.side_effect = async_return
            await task.wait_async()

        assert task.status == "SUCCESS"


class TestTaskDownloadTo:
    def test_download_to_without_progress(self, tmp_path):
        task, _, files_api = make_task("SUCCESS", file_id=FILE_ID)
        files_api.download_to.return_value = str(tmp_path / "output.csv")

        result = task.download_to(str(tmp_path / "output.csv"))

        assert result == str(tmp_path / "output.csv")
        files_api.download_to.assert_called_once_with(FILE_ID, str(tmp_path / "output.csv"), None)

    def test_download_to_with_progress(self, tmp_path):
        task, _, files_api = make_task("SUCCESS", file_id=FILE_ID)
        on_progress = MagicMock()
        files_api.download_to.return_value = str(tmp_path / "output.csv")

        task.download_to(str(tmp_path / "output.csv"), on_progress=on_progress)

        files_api.download_to.assert_called_once_with(FILE_ID, str(tmp_path / "output.csv"), on_progress)

    def test_download_to_no_file_id_raises(self):
        task, _, _ = make_task("PENDING")
        with pytest.raises(ConversionError):
            task.download_to("output.csv")

    async def test_download_to_async_with_progress(self, tmp_path):
        task, _, files_api = make_task("SUCCESS", file_id=FILE_ID)
        on_progress = MagicMock()
        files_api.download_to_async = AsyncMock(return_value=str(tmp_path / "output.csv"))

        result = await task.download_to_async(str(tmp_path / "output.csv"), on_progress=on_progress)

        files_api.download_to_async.assert_called_once_with(
            FILE_ID, str(tmp_path / "output.csv"), on_progress
        )
        assert result == str(tmp_path / "output.csv")


class TestTaskDownloadStream:
    def test_download_stream_yields_chunks(self):
        task, _, files_api = make_task("SUCCESS", file_id=FILE_ID)

        def mock_stream(_file_id):
            yield b"chunk1"
            yield b"chunk2"

        files_api.download_stream = mock_stream

        chunks = list(task.download_stream())

        assert chunks == [b"chunk1", b"chunk2"]

    def test_download_stream_no_file_id_raises(self):
        task, _, _ = make_task("PENDING")
        with pytest.raises(ConversionError):
            list(task.download_stream())

    async def test_download_stream_async_yields_chunks(self):
        task, _, files_api = make_task("SUCCESS", file_id=FILE_ID)

        async def mock_stream_async(_file_id):
            yield b"async1"
            yield b"async2"

        files_api.download_stream_async = mock_stream_async

        chunks = []
        async for chunk in task.download_stream_async():
            chunks.append(chunk)

        assert chunks == [b"async1", b"async2"]

    async def test_download_stream_async_no_file_id_raises(self):
        task, _, _ = make_task("PENDING")
        with pytest.raises(ConversionError):
            async for _ in task.download_stream_async():
                pass


class TestTaskDownloadBytes:
    def test_download_bytes(self):
        task, _, files_api = make_task("SUCCESS", file_id=FILE_ID)
        files_api.download_bytes.return_value = b"content"

        result = task.download_bytes()

        assert result == b"content"
        files_api.download_bytes.assert_called_once_with(FILE_ID)

    def test_download_bytes_no_file_id_raises(self):
        task, _, _ = make_task("PENDING")
        with pytest.raises(ConversionError):
            task.download_bytes()
