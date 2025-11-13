"""
Tasks API - Create and manage conversion tasks
"""

import json
from typing import Optional, List
from urllib.parse import quote
from ..types.config import (
    TaskCreateRequest,
    TaskCreateResponse,
    TaskStatusResponse,
    TaskDetail,
    TaskStatus,
)
from ..utils.validation import validate_task_id, validate_conversion_type
from .http import HttpClient


class TasksAPI:
    """Tasks API for creating and managing conversion tasks"""

    def __init__(self, http: HttpClient):
        self.http = http

    def create(self, request: TaskCreateRequest) -> TaskCreateResponse:
        """Create a new conversion task (sync)"""
        validate_conversion_type(request["type"])

        response: TaskCreateResponse = self.http.post("/tasks", json.dumps(request))

        if response.get("error"):
            raise Exception(response["error"])

        return response

    async def create_async(self, request: TaskCreateRequest) -> TaskCreateResponse:
        """Create a new conversion task (async)"""
        validate_conversion_type(request["type"])

        response: TaskCreateResponse = await self.http.post_async(
            "/tasks", json.dumps(request)
        )

        if response.get("error"):
            raise Exception(response["error"])

        return response

    def get_status(self, task_id: str) -> TaskStatusResponse:
        """Get task status (sync)"""
        validate_task_id(task_id)
        return self.http.get(f"/tasks/{quote(task_id)}")

    async def get_status_async(self, task_id: str) -> TaskStatusResponse:
        """Get task status (async)"""
        validate_task_id(task_id)
        return await self.http.get_async(f"/tasks/{quote(task_id)}")

    def list(self, status: Optional[TaskStatus] = None) -> List[TaskDetail]:
        """List all tasks (sync)"""
        path = "/tasks"

        if status:
            path += f"?status={quote(status)}"

        response = self.http.get(path)

        if response.get("error"):
            raise Exception(response["error"])

        return response.get("data", [])

    async def list_async(self, status: Optional[TaskStatus] = None) -> List[TaskDetail]:
        """List all tasks (async)"""
        path = "/tasks"

        if status:
            path += f"?status={quote(status)}"

        response = await self.http.get_async(path)

        if response.get("error"):
            raise Exception(response["error"])

        return response.get("data", [])
