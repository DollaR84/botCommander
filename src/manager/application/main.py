import asyncio

from flask import Flask
from dishka import AsyncContainer

from adapters.di import AsyncContainerFlask
from config import FlaskConfig

from .auth import AuthManager
from .routes import bp_auth, bp_bots, bp_root


class FlaskApp:

    def __init__(self, config: FlaskConfig):
        self.config = config
        self._app = Flask(__name__, template_folder=self.config.templates_dir)

        self._app.config.from_object(self.config)

    def post_init(self, container: AsyncContainer) -> None:
        async def init_auth() -> None:
            async with container() as state:
                auth_service = await state.get(AuthManager)
                auth_service.init_app(self._app)

        asyncio.run(init_auth())
        self._register_routes()

        AsyncContainerFlask(self.app, container)

    def _register_routes(self) -> None:
        self._app.register_blueprint(bp_root)
        self._app.register_blueprint(bp_auth)
        self._app.register_blueprint(bp_bots)

    @property
    def app(self) -> Flask:
        return self._app
