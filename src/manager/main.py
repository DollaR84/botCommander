import logging

from barsik.utils.cache import get_config
from flask import Flask

from application import FlaskApp
from config import Config
from container import setup_container


def get_app() -> Flask:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s  %(process)-7s %(module)-20s %(message)s',
    )

    config: Config = get_config(Config)
    _app = FlaskApp(config.flask)

    container = setup_container(config)
    _app.post_init(container)
    return _app.app


app = get_app()
