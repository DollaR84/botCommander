from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PGBouncerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PGBOUNCER_")

    use: bool = False
    host: str
    port: int = 6432

    @field_validator("port")
    @classmethod
    def validate_port(cls, value: int) -> int:
        if not 0 < value < 65535:
            raise ValueError("invalid PGBouncer port")
        return value


class DBConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    username: str
    password: str
    db_name: str
    host: str
    port: int = 5432
    debug: bool = False

    is_async: bool = True
    ssl: bool = False
    url: Optional[str] = None

    bouncer: PGBouncerConfig = Field(default_factory=PGBouncerConfig)

    @field_validator("port")
    @classmethod
    def validate_port(cls, value: int) -> int:
        if not 0 < value < 65535:
            raise ValueError("invalid db postgres port")
        return value

    @property
    def uri(self) -> str:
        host = self.bouncer.host if self.bouncer.use else self.host
        port = self.bouncer.port if self.bouncer.use else self.port

        uri = f"postgresql+asyncpg://{self.username}:{self.password}@{host}:{port}/{self.db_name}"
        return self.url if self.url else uri

    @property
    def sync_uri(self) -> str:
        host = self.bouncer.host if self.bouncer.use else self.host
        port = self.bouncer.port if self.bouncer.use else self.port

        uri = f"postgresql://{self.username}:{self.password}@{host}:{port}/{self.db_name}"
        return self.url if self.url else uri

    @property
    def direct_uri(self) -> str:
        uri = f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        return self.url if self.url else uri


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str
    port: int = 6379

    url: Optional[str] = None
    db_num: Optional[int] = None

    @field_validator("port")
    @classmethod
    def validate_port(cls, value: int) -> int:
        if not 0 < value < 65535:
            raise ValueError("invalid redis port")
        return value


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", extra="ignore")

    db: DBConfig = Field(default_factory=DBConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
