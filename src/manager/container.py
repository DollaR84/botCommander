from dishka import AsyncContainer, make_async_container
from dishka.integrations.flask import FlaskProvider

from barsik.config import BaseConfig
from barsik.providers import ConfigProvider as BarsikConfigProvider
from barsik.providers import RedisProvider, DBProvider as BarsikDBProvider

from config import Config
from providers import ApiProvider, AppProvider, ConfigProvider, DBProvider, ServiceProvider


def setup_container(config: Config) -> AsyncContainer:
    providers = [
        FlaskProvider(),
        RedisProvider(),
        ConfigProvider(),
        BarsikConfigProvider(),
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
