from dishka import from_context, Provider, provide, Scope

from config import Config
from config.adapters import (
    AdminConfig, AdminConfigAdapter,
    DockerConfig, DockerConfigAdapter,
    FlaskConfig, FlaskConfigAdapter,
)
from barsik.utils.resolvers import get_config_section


class ConfigProvider(Provider):
    scope = Scope.APP

    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_admin_config(self, config: Config) -> AdminConfig:
        return get_config_section(config, AdminConfigAdapter)

    @provide(scope=Scope.APP)
    def get_docker_config(self, config: Config) -> DockerConfig:
        return get_config_section(config, DockerConfigAdapter)

    @provide(scope=Scope.APP)
    def get_flask_config(self, config: Config) -> FlaskConfig:
        return get_config_section(config, FlaskConfigAdapter)
