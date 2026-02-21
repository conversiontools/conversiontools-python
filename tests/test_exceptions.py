"""Tests for exception classes"""

import pytest
from conversiontools.utils.errors import (
    ConversionToolsError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    FileNotFoundError,
    TaskNotFoundError,
    ConversionError,
    TimeoutError,
    NetworkError,
)


class TestConversionToolsError:
    def test_base_error_attributes(self):
        err = ConversionToolsError("something failed", "SOME_CODE", 500, {"detail": 1})
        assert str(err) == "something failed"
        assert err.message == "something failed"
        assert err.code == "SOME_CODE"
        assert err.status == 500
        assert err.response == {"detail": 1}

    def test_base_error_optional_fields(self):
        err = ConversionToolsError("msg", "CODE")
        assert err.status is None
        assert err.response is None


class TestAuthenticationError:
    def test_default_message(self):
        err = AuthenticationError()
        assert "authorized" in err.message.lower() or "token" in err.message.lower()
        assert err.code == "AUTHENTICATION_ERROR"
        assert err.status == 401

    def test_custom_message(self):
        err = AuthenticationError("custom auth error")
        assert err.message == "custom auth error"

    def test_is_base_error(self):
        assert isinstance(AuthenticationError(), ConversionToolsError)


class TestValidationError:
    def test_attributes(self):
        err = ValidationError("bad input")
        assert err.message == "bad input"
        assert err.code == "VALIDATION_ERROR"
        assert err.status == 400

    def test_with_response(self):
        err = ValidationError("bad input", {"field": "value"})
        assert err.response == {"field": "value"}


class TestRateLimitError:
    def test_attributes(self):
        limits = {"daily": {"limit": 100, "remaining": 0}}
        err = RateLimitError("quota exceeded", limits)
        assert err.message == "quota exceeded"
        assert err.code == "RATE_LIMIT_EXCEEDED"
        assert err.status == 429
        assert err.limits == limits

    def test_without_limits(self):
        err = RateLimitError("quota exceeded")
        assert err.limits is None


class TestFileNotFoundError:
    def test_default_message(self):
        err = FileNotFoundError()
        assert "file" in err.message.lower() or "not found" in err.message.lower()
        assert err.code == "FILE_NOT_FOUND"
        assert err.status == 404

    def test_with_file_id(self):
        err = FileNotFoundError("file not found", "abc123")
        assert err.file_id == "abc123"


class TestTaskNotFoundError:
    def test_attributes(self):
        err = TaskNotFoundError("task missing", "task_abc")
        assert err.code == "TASK_NOT_FOUND"
        assert err.status == 404
        assert err.task_id == "task_abc"


class TestConversionError:
    def test_attributes(self):
        err = ConversionError("conversion failed", "task123", "file corrupt")
        assert err.message == "conversion failed"
        assert err.code == "CONVERSION_ERROR"
        assert err.task_id == "task123"
        assert err.task_error == "file corrupt"

    def test_optional_fields(self):
        err = ConversionError("failed")
        assert err.task_id is None
        assert err.task_error is None


class TestTimeoutError:
    def test_default_message(self):
        err = TimeoutError()
        assert err.code == "TIMEOUT_ERROR"
        assert err.status == 408

    def test_with_timeout_value(self):
        err = TimeoutError("timed out", 30000)
        assert err.timeout == 30000


class TestNetworkError:
    def test_attributes(self):
        original = ConnectionError("refused")
        err = NetworkError("network failed", original)
        assert err.message == "network failed"
        assert err.code == "NETWORK_ERROR"
        assert err.original_error is original

    def test_without_original(self):
        err = NetworkError("network failed")
        assert err.original_error is None


class TestInheritanceHierarchy:
    def test_all_errors_inherit_base(self):
        errors = [
            AuthenticationError(),
            ValidationError("msg"),
            RateLimitError("msg"),
            FileNotFoundError(),
            TaskNotFoundError(),
            ConversionError("msg"),
            TimeoutError(),
            NetworkError("msg"),
        ]
        for err in errors:
            assert isinstance(err, ConversionToolsError)
            assert isinstance(err, Exception)
