from dishka import from_context, Provider, Scope, provide

from sqlalchemy.ext.asyncio import AsyncSession

from application import interfaces
from config import Config
from db import gateways
from db.admin import AdminDbConnector


class DBProvider(Provider):

    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_admin_db_connector(self, config: Config) -> AdminDbConnector:
        return AdminDbConnector(config.db, config.docker.bots_dir)

    @provide(scope=Scope.REQUEST)
    async def bot_creator(self, session: AsyncSession) -> interfaces.CreateBotInterface:
        return gateways.CreateBotGateway(session)

    @provide(scope=Scope.REQUEST)
    async def bot_deleter(self, session: AsyncSession) -> interfaces.DeleteBotInterface:
        return gateways.DeleteBotGateway(session)

    @provide(scope=Scope.REQUEST)
    async def bot_getter(self, session: AsyncSession) -> interfaces.GetBotInterface:
        return gateways.GetBotGateway(session)

    @provide(scope=Scope.REQUEST)
    async def bot_updater(self, session: AsyncSession) -> interfaces.UpdateBotInterface:
        return gateways.UpdateBotGateway(session)
