from sqlalchemy import insert

from db import domain
from db.models import Bot

from barsik.db.gateways import BaseGateway


class CreateBotGateway(BaseGateway[int, Bot]):

    async def create_bot(self, data: domain.CreateBotModel) -> int:
        stmt = insert(Bot).values(**data.dict(exclude_unset=True)).returning(Bot.id)
        error_message = "Error creating new bot"

        return await self.create(stmt, error_message)

    async def create_bots(self, data: list[domain.CreateBotModel]) -> list[int]:
        bots_data = [
            item.dict(exclude_unset=True)
            for item in data
        ]
        error_message = "Error creating new bots"

        stmt = insert(Bot).values(bots_data).returning(Bot.id)
        return await self.create(stmt, error_message, is_multiple=True)
