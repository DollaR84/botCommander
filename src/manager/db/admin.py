import asyncio
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from alembic import command
from alembic.config import Config

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from barsik.config.adapters import PostgresConfig

from application import dto


class AdminDbConnector:

    def __init__(self, config: PostgresConfig, bots_dir: Path):
        self.config = config
        self.bots_dir = bots_dir

    @contextmanager
    def _db_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        conn = psycopg2.connect(
            dbname="postgres",
            user=self.config.username,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        try:
            yield conn
        finally:
            conn.close()

    def _sync_create_database(self, db_name: str) -> None:
        with self._db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
                if not cur.fetchone():
                    cur.execute(f'CREATE DATABASE "{db_name}"')

    def _sync_drop_database(self, db_name: str) -> None:
        with self._db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{db_name}' AND pid <> pg_backend_pid();
                """)
                cur.execute(f'DROP DATABASE IF EXISTS "{db_name}"')

    def _sync_deploy_bot_schema(self, bot_name: str) -> None:
        config = self.config
        bot_db_uri = f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{bot_name}"
        bot_path = self.bots_dir / bot_name

        alembic_cfg = Config(str(bot_path / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", bot_db_uri)
        command.upgrade(alembic_cfg, "head")

    async def prepare_bot_db_environment(self, bot: dto.Bot) -> None:
        loop = asyncio.get_running_loop()

        try:
            if bot.need_db:
                await loop.run_in_executor(None, self._sync_create_database, bot.name)
                await loop.run_in_executor(None, self._sync_deploy_bot_schema, bot.name)
            else:
                await loop.run_in_executor(None, self._sync_drop_database, bot.name)
        except Exception as e:
            await loop.run_in_executor(None, self._sync_drop_database, bot.name)
            raise e
