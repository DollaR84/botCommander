from application import dto
from application import interfaces

from db import domain

from shared.db import Mapper


class BaseCreateBot:

    def __init__(self, gateway: interfaces.CreateBotInterface):
        self.gateway = gateway


class CreateBot(BaseCreateBot):

    async def __call__(
            self,
            data: dto.CreateBot,
    ) -> int:
        domain_data: domain.CreateBotModel = Mapper.to_domain(data, domain.CreateBotModel)
        return await self.gateway.create_bot(domain_data)


class CreateBots(BaseCreateBot):

    async def __call__(
            self,
            data: list[dto.CreateBot],
    ) -> list[int]:
        domain_data: list[domain.CreateBotModel] = [
            Mapper.to_domain(bot, domain.CreateBotModel)
            for bot in data
        ]
        return await self.gateway.create_bots(domain_data)
