from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import psutil
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from components.enums.HealthStatusEnum import healthStatus
from components.logger.LoggerFactory import loggerFactory

if TYPE_CHECKING:
    from components.config.ComponentSettings import componentSettings
    from components.database.PostgresEngine import postgresEngine
    from components.database.RedisEngine import redisEngine
    from components.http.HttpClientFactory import httpClientFactory


class healthCheck:

    def __init__(
        self,
        config: componentSettings,
        postgres: postgresEngine | None = None,
        redis: redisEngine | None = None,
        http_client: httpClientFactory | None = None,
    ) -> None:
        self._config = config
        self._postgres = postgres
        self._redis = redis
        self._http_client = http_client
        self._logger = loggerFactory.create("health_check")
        self._router = APIRouter(tags=["health"])
        self._setup_routes()

    def _setup_routes(self) -> None:
        @self._router.get("/health")
        async def health():
            result = await self.check_all()
            status_code = 200 if result["status"] == healthStatus.HEALTHY.value else 503
            return JSONResponse(content=result, status_code=status_code)

        @self._router.get("/health/detail")
        async def health_detail():
            result = await self.check_all()
            return JSONResponse(content=result)

        @self._router.get("/readyz")
        async def readiness():
            result = await self.check_all()
            if result["status"] == healthStatus.UNHEALTHY.value:
                return JSONResponse(content={"ready": False}, status_code=503)
            return JSONResponse(content={"ready": True})

    @property
    def router(self) -> APIRouter:
        return self._router

    async def check_postgres(self) -> dict:
        if self._postgres is None:
            return {"status": healthStatus.UNHEALTHY.value, "detail": "Not configured"}

        start = time.perf_counter()
        try:
            healthy = await self._postgres.health()
            latency_ms = (time.perf_counter() - start) * 1000

            if not healthy:
                return {"status": healthStatus.UNHEALTHY.value, "latency_ms": latency_ms}

            if latency_ms > self._config.health_pg_latency_critical:
                status = healthStatus.UNHEALTHY
            elif latency_ms > self._config.health_pg_latency_warn:
                status = healthStatus.DEGRADED
            else:
                status = healthStatus.HEALTHY

            return {"status": status.value, "latency_ms": round(latency_ms, 2)}
        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            return {"status": healthStatus.UNHEALTHY.value, "latency_ms": round(latency_ms, 2), "error": str(e)}

    async def check_redis(self) -> dict:
        if self._redis is None:
            return {"status": healthStatus.UNHEALTHY.value, "detail": "Not configured"}

        start = time.perf_counter()
        try:
            healthy = await self._redis.health()
            latency_ms = (time.perf_counter() - start) * 1000

            if not healthy:
                return {"status": healthStatus.UNHEALTHY.value, "latency_ms": latency_ms}

            if latency_ms > self._config.health_redis_latency_critical:
                status = healthStatus.UNHEALTHY
            elif latency_ms > self._config.health_redis_latency_warn:
                status = healthStatus.DEGRADED
            else:
                status = healthStatus.HEALTHY

            return {"status": status.value, "latency_ms": round(latency_ms, 2)}
        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            return {"status": healthStatus.UNHEALTHY.value, "latency_ms": round(latency_ms, 2), "error": str(e)}

    async def check_external(self, url: str) -> dict:
        if self._http_client is None:
            return {"status": healthStatus.UNHEALTHY.value, "detail": "HTTP client not configured"}

        start = time.perf_counter()
        try:
            status_code, _ = await self._http_client.head(url, timeout=10)
            latency_ms = (time.perf_counter() - start) * 1000

            if status_code >= 500:
                status = healthStatus.UNHEALTHY
            elif status_code >= 400:
                status = healthStatus.DEGRADED
            else:
                status = healthStatus.HEALTHY

            return {"status": status.value, "latency_ms": round(latency_ms, 2), "http_status": status_code}
        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            return {"status": healthStatus.UNHEALTHY.value, "latency_ms": round(latency_ms, 2), "error": str(e)}

    def check_system(self) -> dict:
        try:
            disk = psutil.disk_usage("/")
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)

            disk_percent = disk.percent
            memory_percent = memory.percent

            if disk_percent > 95 or memory_percent > 95 or cpu > 95:
                status = healthStatus.UNHEALTHY
            elif disk_percent > 85 or memory_percent > 85 or cpu > 85:
                status = healthStatus.DEGRADED
            else:
                status = healthStatus.HEALTHY

            return {
                "status": status.value,
                "disk_percent": disk_percent,
                "memory_percent": memory_percent,
                "cpu_percent": cpu,
            }
        except Exception as e:
            return {"status": healthStatus.UNHEALTHY.value, "error": str(e)}

    async def check_all(self) -> dict:
        checks = {}

        if self._postgres is not None:
            checks["postgres"] = await self.check_postgres()

        if self._redis is not None:
            checks["redis"] = await self.check_redis()

        for url in self._config.health_check_urls:
            checks[f"external:{url[:30]}"] = await self.check_external(url)

        checks["system"] = self.check_system()

        statuses = [c.get("status", healthStatus.UNHEALTHY.value) for c in checks.values()]

        if healthStatus.UNHEALTHY.value in statuses:
            overall = healthStatus.UNHEALTHY
        elif healthStatus.DEGRADED.value in statuses:
            overall = healthStatus.DEGRADED
        else:
            overall = healthStatus.HEALTHY

        return {
            "status": overall.value,
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
