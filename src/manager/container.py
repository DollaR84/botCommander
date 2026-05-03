from dishka import AsyncContainer, make_async_container
from dishka.integrations.flask import FlaskProvider

from config import Config
from providers import ApiProvider, AppProvider, DBProvider, ServiceProvider

from barsik.providers import ConfigProvider, RedisProvider, DBProvider as BarsikDBProvider
from shared.config import BaseConfig


def setup_container(config: Config) -> AsyncContainer:
    providers = [
        FlaskProvider(),
        ConfigProvider(),
        RedisProvider(),
        BarsikDBProvider(),
        DBProvider(),
        ApiProvider(),
        AppProvider(),
        ServiceProvider()
    ]

    container = make_async_container(
        *providers,
        context={
            Config: config,
            BaseConfig: config,
        },
    )

    return container
