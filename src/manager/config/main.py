from barsik.config import BaseConfig

from .adapters import (
    AdminConfig,
    DockerConfig,
    FlaskConfig,
)


class Config(BaseConfig):

    admin: AdminConfig
    docker: DockerConfig
    flask: FlaskConfig
