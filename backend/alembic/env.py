from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlmodel import SQLModel, create_engine

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.domain.config.Settings import settings
from src.domain.models.ApiKeyModel import apiKeyModel
from src.domain.models.PasswordResetModel import passwordResetModel
from src.domain.models.RefreshTokenModel import refreshTokenModel
from src.domain.models.SessionModel import sessionModel
from src.domain.models.UserModel import userModel
from src.domain.models.VerificationModel import verificationModel

_MODELS = [
    userModel,
    sessionModel,
    refreshTokenModel,
    apiKeyModel,
    verificationModel,
    passwordResetModel,
]

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

app_settings = settings()
sync_url = app_settings.database_url.replace("+asyncpg", "+psycopg")


def run_migrations_offline() -> None:
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(sync_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
