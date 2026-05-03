from dishka import from_context, Provider, Scope, provide

from application import AuthManager
from config import Config


class ApiProvider(Provider):

    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_auth(self, config: Config) -> AuthManager:
        return AuthManager(config.admin)
