"""Tests for polling utilities"""

import pytest
from unittest.mock import MagicMock
from conversiontools.utils.polling import (
    poll_sync,
    poll_async,
    poll_task_status_sync,
    poll_task_status_async,
)
from conversiontools.utils.errors import TimeoutError


class TestPollSync:
    def test_returns_immediately_when_condition_false(self):
        fn = MagicMock(return_value={"done": True})
        result = poll_sync(
            fn,
            should_continue=lambda r: not r["done"],
            interval=1,
            max_interval=10,
            backoff=1.5,
        )
        assert result == {"done": True}
        assert fn.call_count == 1

    def test_polls_until_condition_met(self):
        responses = [{"done": False}, {"done": False}, {"done": True}]
        fn = MagicMock(side_effect=responses)
        result = poll_sync(
            fn,
            should_continue=lambda r: not r["done"],
            interval=0,
            max_interval=0,
            backoff=1.0,
        )
        assert result == {"done": True}
        assert fn.call_count == 3

    def test_on_progress_called_for_non_terminal(self):
        responses = [{"status": "PENDING"}, {"status": "RUNNING"}, {"status": "SUCCESS"}]
        fn = MagicMock(side_effect=responses)
        progress_calls = []
        poll_sync(
            fn,
            should_continue=lambda r: r["status"] not in ("SUCCESS", "ERROR"),
            interval=0,
            max_interval=0,
            backoff=1.0,
            on_progress=lambda r: progress_calls.append(r),
        )
        assert len(progress_calls) == 2
        assert progress_calls[0]["status"] == "PENDING"
        assert progress_calls[1]["status"] == "RUNNING"

    def test_timeout_raises(self):
        fn = MagicMock(return_value={"status": "PENDING"})
        with pytest.raises(TimeoutError):
            poll_sync(
                fn,
                should_continue=lambda r: True,
                interval=0,
                max_interval=0,
                backoff=1.0,
                timeout=1,  # 1ms timeout, will expire immediately
            )


class TestPollAsync:
    async def test_returns_immediately(self):
        async def fn():
            return {"done": True}

        result = await poll_async(
            fn,
            should_continue=lambda r: not r["done"],
            interval=0,
            max_interval=0,
            backoff=1.0,
        )
        assert result == {"done": True}

    async def test_polls_until_done(self):
        call_count = 0

        async def fn():
            nonlocal call_count
            call_count += 1
            return {"done": call_count >= 3}

        result = await poll_async(
            fn,
            should_continue=lambda r: not r["done"],
            interval=0,
            max_interval=0,
            backoff=1.0,
        )
        assert result == {"done": True}
        assert call_count == 3

    async def test_timeout_raises(self):
        async def fn():
            return {"status": "PENDING"}

        with pytest.raises(TimeoutError):
            await poll_async(
                fn,
                should_continue=lambda r: True,
                interval=0,
                max_interval=0,
                backoff=1.0,
                timeout=1,  # 1ms
            )


class TestPollTaskStatusSync:
    def test_success_immediately(self):
        status = {"status": "SUCCESS", "file_id": "a" * 32, "error": None, "conversionProgress": 100}
        fn = MagicMock(return_value=status)
        result = poll_task_status_sync(fn, interval=0, max_interval=0, backoff=1.0)
        assert result["status"] == "SUCCESS"
        assert fn.call_count == 1

    def test_error_immediately(self):
        status = {"status": "ERROR", "file_id": None, "error": "failed", "conversionProgress": 0}
        fn = MagicMock(return_value=status)
        result = poll_task_status_sync(fn, interval=0, max_interval=0, backoff=1.0)
        assert result["status"] == "ERROR"
        assert fn.call_count == 1

    def test_polls_through_pending_and_running(self):
        responses = [
            {"status": "PENDING", "file_id": None, "error": None, "conversionProgress": 0},
            {"status": "RUNNING", "file_id": None, "error": None, "conversionProgress": 50},
            {"status": "SUCCESS", "file_id": "a" * 32, "error": None, "conversionProgress": 100},
        ]
        fn = MagicMock(side_effect=responses)
        result = poll_task_status_sync(fn, interval=0, max_interval=0, backoff=1.0)
        assert result["status"] == "SUCCESS"
        assert fn.call_count == 3

    def test_on_progress_callback(self):
        responses = [
            {"status": "PENDING", "file_id": None, "error": None, "conversionProgress": 0},
            {"status": "SUCCESS", "file_id": "a" * 32, "error": None, "conversionProgress": 100},
        ]
        fn = MagicMock(side_effect=responses)
        progress_events = []
        poll_task_status_sync(
            fn, interval=0, max_interval=0, backoff=1.0,
            on_progress=lambda s: progress_events.append(s),
        )
        assert len(progress_events) == 1
        assert progress_events[0]["status"] == "PENDING"


class TestPollTaskStatusAsync:
    async def test_success_immediately(self):
        status = {"status": "SUCCESS", "file_id": "a" * 32, "error": None, "conversionProgress": 100}

        async def fn():
            return status

        result = await poll_task_status_async(fn, interval=0, max_interval=0, backoff=1.0)
        assert result["status"] == "SUCCESS"

    async def test_polls_through_states(self):
        responses = [
            {"status": "PENDING", "file_id": None, "error": None, "conversionProgress": 0},
            {"status": "SUCCESS", "file_id": "a" * 32, "error": None, "conversionProgress": 100},
        ]
        idx = 0

        async def fn():
            nonlocal idx
            r = responses[idx]
            idx += 1
            return r

        result = await poll_task_status_async(fn, interval=0, max_interval=0, backoff=1.0)
        assert result["status"] == "SUCCESS"
        assert idx == 2
