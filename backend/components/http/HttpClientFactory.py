from __future__ import annotations

from typing import TYPE_CHECKING, Any

import aiohttp
import structlog

from components.exceptions.BaseException import baseException, serviceUnavailableException
from components.logger.LoggerFactory import loggerFactory

if TYPE_CHECKING:
    from components.config.ComponentSettings import componentSettings


class httpClientFactory:

    def __init__(
        self,
        config: componentSettings,
        service_name: str = "unknown",
    ) -> None:
        self._config = config
        self._service_name = service_name
        self._session: aiohttp.ClientSession | None = None
        self._logger = loggerFactory.create("http_client")

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self._config.http_client_timeout)
            connector = aiohttp.TCPConnector(limit=self._config.http_client_max_connections)
            self._session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return self._session

    def _get_headers(self, headers: dict | None = None) -> dict:
        ctx = structlog.contextvars.get_contextvars()
        default_headers = {
            "X-Service-Name": self._service_name,
        }
        if "correlation_id" in ctx:
            default_headers["X-Correlation-ID"] = ctx["correlation_id"]
        if headers:
            default_headers.update(headers)
        return default_headers

    async def request(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        data: Any = None,
        json: dict | None = None,
        timeout: int | None = None,
    ) -> dict | bytes:
        session = await self._ensure_session()
        request_headers = self._get_headers(headers)
        request_timeout = aiohttp.ClientTimeout(total=timeout) if timeout else None

        try:
            async with session.request(
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                data=data,
                json=json,
                timeout=request_timeout,
            ) as response:
                content_type = response.headers.get("Content-Type", "")

                if "application/json" in content_type:
                    return await response.json()
                return await response.read()

        except aiohttp.ClientConnectorError as e:
            self._logger.error("connection_error", url=url, error=str(e))
            raise serviceUnavailableException(f"Failed to connect to {url}: {e}")
        except aiohttp.ClientTimeout as e:
            self._logger.error("timeout_error", url=url, error=str(e))
            raise serviceUnavailableException(f"Request to {url} timed out")
        except aiohttp.ClientError as e:
            self._logger.error("client_error", url=url, error=str(e))
            raise baseException(f"HTTP client error: {e}")

    async def get(
        self,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        timeout: int | None = None,
    ) -> dict | bytes:
        return await self.request("GET", url, headers=headers, params=params, timeout=timeout)

    async def post(
        self,
        url: str,
        headers: dict | None = None,
        data: Any = None,
        json: dict | None = None,
        timeout: int | None = None,
    ) -> dict | bytes:
        return await self.request("POST", url, headers=headers, data=data, json=json, timeout=timeout)

    async def put(
        self,
        url: str,
        headers: dict | None = None,
        data: Any = None,
        json: dict | None = None,
        timeout: int | None = None,
    ) -> dict | bytes:
        return await self.request("PUT", url, headers=headers, data=data, json=json, timeout=timeout)

    async def delete(
        self,
        url: str,
        headers: dict | None = None,
        timeout: int | None = None,
    ) -> dict | bytes:
        return await self.request("DELETE", url, headers=headers, timeout=timeout)

    async def head(
        self,
        url: str,
        headers: dict | None = None,
        timeout: int | None = None,
    ) -> tuple[int, dict]:
        session = await self._ensure_session()
        request_headers = self._get_headers(headers)
        request_timeout = aiohttp.ClientTimeout(total=timeout) if timeout else None

        try:
            async with session.head(
                url,
                headers=request_headers,
                timeout=request_timeout,
            ) as response:
                return response.status, dict(response.headers)
        except aiohttp.ClientError as e:
            self._logger.error("head_error", url=url, error=str(e))
            raise serviceUnavailableException(f"HEAD request to {url} failed: {e}")

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None
