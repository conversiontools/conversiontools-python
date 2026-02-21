"""Tests for ConversionToolsClient"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from conversiontools.client import ConversionToolsClient, VERSION
from conversiontools.utils.errors import ValidationError

FILE_ID = "a" * 32
TASK_ID = "b" * 32
VALID_TOKEN = "ct_" + "x" * 32


class TestConstructor:
    def test_instantiates_with_valid_token(self):
        client = ConversionToolsClient({"api_token": VALID_TOKEN})
        assert client is not None

    def test_has_files_and_tasks_apis(self):
        client = ConversionToolsClient({"api_token": VALID_TOKEN})
        assert client.files is not None
        assert client.tasks is not None

    def test_raises_on_empty_token(self):
        with pytest.raises(ValidationError):
            ConversionToolsClient({"api_token": ""})

    def test_raises_on_whitespace_token(self):
        with pytest.raises(ValidationError):
            ConversionToolsClient({"api_token": "   "})

    def test_version_constant_format(self):
        assert isinstance(VERSION, str)
        parts = VERSION.split(".")
        assert len(parts) == 3
        for part in parts:
            assert part.isdigit()

    def test_accepts_custom_config(self):
        client = ConversionToolsClient({
            "api_token": VALID_TOKEN,
            "base_url": "https://custom.api.url",
            "timeout": 60000,
            "retries": 5,
            "polling_interval": 3000,
        })
        assert client is not None

    def test_accepts_progress_callbacks(self):
        on_upload = MagicMock()
        on_download = MagicMock()
        on_conversion = MagicMock()
        client = ConversionToolsClient({
            "api_token": VALID_TOKEN,
            "on_upload_progress": on_upload,
            "on_download_progress": on_download,
            "on_conversion_progress": on_conversion,
        })
        assert client.config["on_upload_progress"] is on_upload
        assert client.config["on_download_progress"] is on_download
        assert client.config["on_conversion_progress"] is on_conversion

    def test_default_user_agent_contains_version(self):
        client = ConversionToolsClient({"api_token": VALID_TOKEN})
        assert f"conversiontools-python/{VERSION}" in client.config["user_agent"]

    def test_custom_user_agent(self):
        client = ConversionToolsClient({
            "api_token": VALID_TOKEN,
            "user_agent": "myapp/1.0",
        })
        assert client.config["user_agent"] == "myapp/1.0"
        assert client.http.user_agent == "myapp/1.0"

    def test_accepts_webhook_url(self):
        client = ConversionToolsClient({
            "api_token": VALID_TOKEN,
            "webhook_url": "https://example.com/webhook",
        })
        assert client.config["webhook_url"] == "https://example.com/webhook"

    def test_get_rate_limits_initially_none(self):
        client = ConversionToolsClient({"api_token": VALID_TOKEN})
        assert client.get_rate_limits() is None


class TestConvert:
    def _make_client_with_mocks(self):
        client = ConversionToolsClient({"api_token": VALID_TOKEN})
        client.files.upload = MagicMock(return_value=FILE_ID)
        client.tasks.create = MagicMock(return_value={"error": None, "task_id": TASK_ID})
        client.tasks.get_status = MagicMock(return_value={
            "status": "SUCCESS", "file_id": FILE_ID, "error": None, "conversionProgress": 100,
        })
        client.files.download_to = MagicMock(return_value="output.csv")
        return client

    def test_convert_returns_output_path(self, tmp_path):
        client = self._make_client_with_mocks()

        test_file = tmp_path / "test.xml"
        test_file.write_text("<root/>")

        with patch("conversiontools.models.task.poll_task_status_sync") as mock_poll:
            mock_poll.return_value = {
                "status": "SUCCESS", "file_id": FILE_ID, "error": None, "conversionProgress": 100,
            }
            result = client.convert("convert.xml_to_csv", str(test_file), "output.csv")

        assert result == "output.csv"

    def test_convert_wires_on_download_progress(self, tmp_path):
        on_download_progress = MagicMock()
        client = ConversionToolsClient({
            "api_token": VALID_TOKEN,
            "on_download_progress": on_download_progress,
        })
        client.files.upload = MagicMock(return_value=FILE_ID)
        client.tasks.create = MagicMock(return_value={"error": None, "task_id": TASK_ID})
        client.files.download_to = MagicMock(return_value="output.csv")

        test_file = tmp_path / "test.xml"
        test_file.write_text("<root/>")

        with patch("conversiontools.models.task.poll_task_status_sync") as mock_poll:
            mock_poll.return_value = {
                "status": "SUCCESS", "file_id": FILE_ID, "error": None, "conversionProgress": 100,
            }
            client.convert("convert.xml_to_csv", str(test_file), "output.csv")

        # on_download_progress was passed to download_to
        call_args = client.files.download_to.call_args
        assert call_args[1].get("on_progress") is on_download_progress or \
               (len(call_args[0]) >= 3 and call_args[0][2] is on_download_progress)

    def test_convert_with_wait_false_returns_task_id(self, tmp_path):
        client = self._make_client_with_mocks()
        test_file = tmp_path / "test.xml"
        test_file.write_text("<root/>")

        result = client.convert("convert.xml_to_csv", str(test_file), wait=False)

        assert result == TASK_ID

    def test_convert_wires_on_upload_progress(self, tmp_path):
        on_upload = MagicMock()
        client = ConversionToolsClient({
            "api_token": VALID_TOKEN,
            "on_upload_progress": on_upload,
        })
        client.files.upload = MagicMock(return_value=FILE_ID)
        client.tasks.create = MagicMock(return_value={"error": None, "task_id": TASK_ID})
        client.files.download_to = MagicMock(return_value="output.csv")

        test_file = tmp_path / "test.xml"
        test_file.write_text("<root/>")

        with patch("conversiontools.models.task.poll_task_status_sync") as mock_poll:
            mock_poll.return_value = {
                "status": "SUCCESS", "file_id": FILE_ID, "error": None, "conversionProgress": 100,
            }
            client.convert("convert.xml_to_csv", str(test_file), "output.csv")

        upload_call = client.files.upload.call_args
        upload_opts = upload_call[0][1] if len(upload_call[0]) > 1 else upload_call[1].get("options", {})
        assert upload_opts.get("on_progress") is on_upload

    async def test_convert_async_wires_on_download_progress(self, tmp_path):
        on_download_progress = MagicMock()
        client = ConversionToolsClient({
            "api_token": VALID_TOKEN,
            "on_download_progress": on_download_progress,
        })
        client.files.upload_async = AsyncMock(return_value=FILE_ID)
        client.tasks.create_async = AsyncMock(return_value={"error": None, "task_id": TASK_ID})
        client.files.download_to_async = AsyncMock(return_value="output.csv")

        test_file = tmp_path / "test.xml"
        test_file.write_text("<root/>")

        with patch("conversiontools.models.task.poll_task_status_async") as mock_poll:
            async def async_return(*args, **kwargs):
                return {"status": "SUCCESS", "file_id": FILE_ID, "error": None, "conversionProgress": 100}
            mock_poll.side_effect = async_return

            await client.convert_async("convert.xml_to_csv", str(test_file), "output.csv")

        call_args = client.files.download_to_async.call_args
        passed_progress = call_args[1].get("on_progress") or (
            call_args[0][2] if len(call_args[0]) >= 3 else None
        )
        assert passed_progress is on_download_progress


class TestGetTask:
    def test_get_task_returns_task_object(self):
        client = ConversionToolsClient({"api_token": VALID_TOKEN})
        client.tasks.get_status = MagicMock(return_value={
            "status": "SUCCESS", "file_id": FILE_ID, "error": None, "conversionProgress": 100,
        })

        task = client.get_task(TASK_ID)

        assert task.id == TASK_ID
        assert task.status == "SUCCESS"
        assert task.file_id == FILE_ID
