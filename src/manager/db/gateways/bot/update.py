from sqlalchemy import update

from db import domain
from db.models import Bot

from barsik.db.gateways import BaseGateway


class UpdateBotGateway(BaseGateway[int, Bot]):

    async def update_bot(self, bot_id: int, update_data: domain.UpdateBotModel) -> int:
        error_message = f"Error update bot info id={bot_id}"

        stmt = update(Bot)
        stmt = stmt.where(Bot.id == bot_id)
        stmt = stmt.values(**update_data.dict(exclude_unset=True))
        stmt = stmt.returning(Bot.id)

        return await self.update(stmt, error_message)
