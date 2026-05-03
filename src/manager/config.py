from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.config import BaseConfig


class FlaskConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FLASK_")

    templates_dir: str


class DockerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DOCKER_")

    domain: str
    work_path: str
    dir_bots: str = "bots"
    dir_shared: str = "shared"
    network: str = "bot_network"

    @property
    def bots_dir(self) -> Path:
        return Path(self.work_path) / self.dir_bots

    @property
    def shared_dir(self) -> Path:
        return Path(self.work_path) / self.dir_shared


class AdminConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ADMIN_")

    username: str
    password_hash: str
    secret_key: str


class Config(BaseConfig):
    model_config = SettingsConfigDict(env_nested_delimiter="__", extra="ignore")

    flask: FlaskConfig = Field(default_factory=FlaskConfig)
    docker: DockerConfig = Field(default_factory=DockerConfig)
    admin: AdminConfig = Field(default_factory=AdminConfig)
