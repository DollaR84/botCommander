from sqlalchemy import delete

from db.models import Bot

from barsik.db.gateways import BaseGateway


class DeleteBotGateway(BaseGateway[int, Bot]):

    async def delete_bot(self, bot_id: int) -> None:
        stmt = delete(Bot)
        stmt = stmt.where(Bot.id == bot_id)

        error_message = f"Error deleting bot id={bot_id}"
        await self.delete(stmt, error_message)
