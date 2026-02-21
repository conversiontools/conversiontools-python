"""Tests for retry utilities"""

import pytest
from unittest.mock import MagicMock
from conversiontools.utils.retry import with_retry_sync, with_retry_async, should_retry_error
from conversiontools.utils.errors import NetworkError, ValidationError, TimeoutError


class TestShouldRetryError:
    def test_network_error_should_retry(self):
        err = NetworkError("connection refused")
        assert should_retry_error(err, [500]) is True

    def test_timeout_error_should_retry(self):
        err = TimeoutError("timed out")
        assert should_retry_error(err, [500]) is True

    def test_validation_error_should_not_retry(self):
        err = ValidationError("bad input")
        assert should_retry_error(err, [500]) is False

    def test_retryable_status_should_retry(self):
        err = MagicMock()
        err.status = 503
        assert should_retry_error(err, [500, 503]) is True

    def test_non_retryable_status_should_not_retry(self):
        err = MagicMock()
        err.status = 400
        assert should_retry_error(err, [500, 503]) is False

    def test_custom_retry_fn(self):
        err = ValueError("something")
        assert should_retry_error(err, [], lambda e: True) is True
        assert should_retry_error(err, [], lambda e: False) is False


class TestWithRetrySync:
    def test_success_on_first_attempt(self):
        fn = MagicMock(return_value=42)
        result = with_retry_sync(fn, retries=3, retry_delay=0, retryable_statuses=[500])
        assert result == 42
        assert fn.call_count == 1

    def test_retries_on_network_error(self):
        fn = MagicMock(side_effect=[NetworkError("fail"), NetworkError("fail"), 99])
        result = with_retry_sync(fn, retries=3, retry_delay=0, retryable_statuses=[500])
        assert result == 99
        assert fn.call_count == 3

    def test_no_retry_on_validation_error(self):
        fn = MagicMock(side_effect=ValidationError("bad input"))
        with pytest.raises(ValidationError):
            with_retry_sync(fn, retries=3, retry_delay=0, retryable_statuses=[500])
        assert fn.call_count == 1

    def test_exhausts_retries(self):
        fn = MagicMock(side_effect=NetworkError("always fails"))
        with pytest.raises(NetworkError):
            with_retry_sync(fn, retries=2, retry_delay=0, retryable_statuses=[500])
        assert fn.call_count == 3  # 1 initial + 2 retries

    def test_zero_retries_single_attempt(self):
        fn = MagicMock(side_effect=NetworkError("fail"))
        with pytest.raises(NetworkError):
            with_retry_sync(fn, retries=0, retry_delay=0, retryable_statuses=[500])
        assert fn.call_count == 1


class TestWithRetryAsync:
    async def test_success_on_first_attempt(self):
        async def fn():
            return 42
        result = await with_retry_async(fn, retries=3, retry_delay=0, retryable_statuses=[500])
        assert result == 42

    async def test_retries_on_network_error(self):
        call_count = 0

        async def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("fail")
            return "ok"

        result = await with_retry_async(fn, retries=3, retry_delay=0, retryable_statuses=[500])
        assert result == "ok"
        assert call_count == 3

    async def test_no_retry_on_validation_error(self):
        call_count = 0

        async def fn():
            nonlocal call_count
            call_count += 1
            raise ValidationError("bad")

        with pytest.raises(ValidationError):
            await with_retry_async(fn, retries=3, retry_delay=0, retryable_statuses=[500])
        assert call_count == 1

    async def test_exhausts_retries(self):
        async def fn():
            raise NetworkError("always fails")

        with pytest.raises(NetworkError):
            await with_retry_async(fn, retries=2, retry_delay=0, retryable_statuses=[500])
