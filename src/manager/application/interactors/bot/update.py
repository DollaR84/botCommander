from application import dto
from application import interfaces

from db import domain

from shared.db import Mapper


class UpdateBot:

    def __init__(self, gateway: interfaces.UpdateBotInterface):
        self.gateway = gateway

    async def __call__(self, bot_id: int, update_data: dto.UpdateBot) -> int:
        domain_data: domain.UpdateBotModel = Mapper.to_domain(update_data, domain.UpdateBotModel, exclude_unset=True)
        return await self.gateway.update_bot(bot_id, domain_data)
