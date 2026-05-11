from flask import Flask
from dishka import AsyncContainer

from adapters.di import AsyncContainerFlask
from config.adapters import FlaskConfig

from .auth import AuthManager
from .routes import bp_auth, bp_bots, bp_root


class FlaskApp:

    def __init__(self, config: FlaskConfig):
        self.config = config
        self._app = Flask(__name__, template_folder=self.config.templates_dir)

        self._app.config.from_object(self.config)

    def post_init(self, container: AsyncContainer) -> None:
        AsyncContainerFlask(self.app, container)

        auth = container.get_sync(AuthManager)
        auth.init_app(self._app)

        self._register_routes()

    def _register_routes(self) -> None:
        self._app.register_blueprint(bp_root)
        self._app.register_blueprint(bp_auth)
        self._app.register_blueprint(bp_bots)

    @property
    def app(self) -> Flask:
        return self._app
