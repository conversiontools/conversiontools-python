"""Tests for validation utilities"""

import io
import pytest
from conversiontools.utils.validation import (
    validate_api_token,
    validate_conversion_type,
    validate_conversion_input,
    validate_file_id,
    validate_task_id,
    is_valid_url,
)
from conversiontools.utils.errors import ValidationError


class TestValidateApiToken:
    def test_valid_token(self):
        validate_api_token("ct_" + "a" * 32)  # should not raise

    def test_any_non_empty_string(self):
        validate_api_token("anytoken")  # should not raise

    def test_empty_string_raises(self):
        with pytest.raises(ValidationError):
            validate_api_token("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError):
            validate_api_token("   \t\n  ")

    def test_non_string_raises(self):
        with pytest.raises(ValidationError):
            validate_api_token(None)  # type: ignore


class TestValidateConversionType:
    def test_valid_type(self):
        validate_conversion_type("convert.xml_to_csv")  # should not raise

    def test_missing_prefix_raises(self):
        with pytest.raises(ValidationError, match="format"):
            validate_conversion_type("xml_to_csv")

    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            validate_conversion_type("")

    def test_non_string_raises(self):
        with pytest.raises(ValidationError):
            validate_conversion_type(None)  # type: ignore


class TestValidateFileId:
    def test_valid_file_id(self):
        validate_file_id("a" * 32)  # should not raise

    def test_valid_hex_id(self):
        validate_file_id("12345678901234567890123456789012")  # should not raise

    def test_too_short_raises(self):
        with pytest.raises(ValidationError):
            validate_file_id("abc123")

    def test_too_long_raises(self):
        with pytest.raises(ValidationError):
            validate_file_id("a" * 33)

    def test_invalid_chars_raises(self):
        with pytest.raises(ValidationError):
            validate_file_id("g" * 32)  # 'g' is not valid hex

    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            validate_file_id("")


class TestValidateTaskId:
    def test_valid_task_id(self):
        validate_task_id("b" * 32)  # should not raise

    def test_invalid_raises(self):
        with pytest.raises(ValidationError):
            validate_task_id("short")

    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            validate_task_id("")


class TestIsValidUrl:
    def test_valid_http_url(self):
        assert is_valid_url("http://example.com") is True

    def test_valid_https_url(self):
        assert is_valid_url("https://example.com/path?query=1") is True

    def test_no_scheme_is_invalid(self):
        assert is_valid_url("example.com") is False

    def test_empty_is_invalid(self):
        assert is_valid_url("") is False


class TestValidateConversionInput:
    def test_string_path(self):
        result = validate_conversion_input("/path/to/file.xml")
        assert result["type"] == "path"
        assert result["value"] == "/path/to/file.xml"

    def test_bytes_buffer(self):
        data = b"binary data"
        result = validate_conversion_input(data)
        assert result["type"] == "buffer"
        assert result["value"] == data

    def test_file_like_stream(self):
        stream = io.BytesIO(b"data")
        result = validate_conversion_input(stream)
        assert result["type"] == "stream"

    def test_dict_with_url(self):
        result = validate_conversion_input({"url": "https://example.com/file.xml"})
        assert result["type"] == "url"
        assert result["value"] == "https://example.com/file.xml"

    def test_dict_with_invalid_url_raises(self):
        with pytest.raises(ValidationError, match="URL"):
            validate_conversion_input({"url": "not-a-url"})

    def test_dict_with_path(self):
        result = validate_conversion_input({"path": "/tmp/file.xml"})
        assert result["type"] == "path"

    def test_dict_with_file_id(self):
        result = validate_conversion_input({"file_id": "a" * 32})
        assert result["type"] == "file_id"
        assert result["value"] == "a" * 32

    def test_dict_with_camelcase_file_id(self):
        result = validate_conversion_input({"fileId": "b" * 32})
        assert result["type"] == "file_id"
        assert result["value"] == "b" * 32

    def test_dict_with_buffer(self):
        data = b"binary"
        result = validate_conversion_input({"buffer": data})
        assert result["type"] == "buffer"

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            validate_conversion_input(None)

    def test_invalid_type_raises(self):
        with pytest.raises(ValidationError):
            validate_conversion_input(12345)  # type: ignore
