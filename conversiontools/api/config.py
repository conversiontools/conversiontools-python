"""
Config API - Get API configuration and user info
"""

from typing import Dict, Any
from ..types.config import UserInfo
from .http import HttpClient


class ConfigAPI:
    """Config API for getting API configuration and user information"""

    def __init__(self, http: HttpClient):
        self.http = http

    def get_user_info(self) -> UserInfo:
        """Get authenticated user information (sync)"""
        return self.http.get("/auth")

    async def get_user_info_async(self) -> UserInfo:
        """Get authenticated user information (async)"""
        return await self.http.get_async("/auth")

    def get_config(self) -> Dict[str, Any]:
        """Get API configuration (sync)"""
        return self.http.get("/config")

    async def get_config_async(self) -> Dict[str, Any]:
        """Get API configuration (async)"""
        return await self.http.get_async("/config")
