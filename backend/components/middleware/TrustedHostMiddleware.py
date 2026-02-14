from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.middleware.trustedhost import TrustedHostMiddleware as StarletteTrustedHost

if TYPE_CHECKING:
    from fastapi import FastAPI

    from components.config.ComponentSettings import componentSettings


def create_trusted_host_middleware(app: FastAPI, config: componentSettings) -> StarletteTrustedHost:
    return StarletteTrustedHost(app, allowed_hosts=config.trusted_hosts)
