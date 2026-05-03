from flask import Flask
from dishka import AsyncContainer

from .functions import setup_flask_async_dishka, verify_dishka_routes


class AsyncContainerFlask:

    def __init__(self, app: Flask, container: AsyncContainer):
        self.app = app
        self.container = container

        self.setup()
        self.verify_routes()

    def setup(self) -> None:
        setup_flask_async_dishka(self.app, self.container)

    def verify_routes(self) -> None:
        verify_dishka_routes(self.app)
