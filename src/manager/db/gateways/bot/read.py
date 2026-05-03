from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.sql import Select

from db import domain
from db.models import Bot

from services.types import ImageType

from barsik.db.gateways import BaseGateway


class GetBotGateway(BaseGateway[int, Bot]):

    async def get_bot(self, bot_id: int) -> Optional[domain.BotModel]:
        error_message = f"Error get bot id={bot_id}"

        stmt = select(Bot)
        stmt = stmt.where(Bot.id == bot_id)

        bot = await self.get(stmt, error_message)
        return domain.BotModel(**bot.to_dict()) if bot else None

    async def get_bots(
            self,
            name: Optional[str] = None,
            image_type: Optional[ImageType] = None,
            is_active: Optional[bool] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> list[domain.BotModel]:
        error_message = "Error get bots"
        stmt = select(Bot)

        stmt = self._build_conditions(stmt, name, image_type, is_active)
        stmt = stmt.order_by(Bot.id.desc())

        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        bots = await self.get(stmt, error_message, is_multiple=True)
        return [
            domain.BotModel(**bot.to_dict())
            for bot in bots
        ]

    async def get_count_bots(
            self,
            name: Optional[str] = None,
            image_type: Optional[ImageType] = None,
            is_active: Optional[bool] = None,
    ) -> int:
        error_message = "error getting bots count"
        stmt = select(func.count(Bot.id))  # pylint: disable=not-callable
        stmt = self._build_conditions(stmt, name, image_type, is_active)
        return await self.get_count(stmt, error_message)

    def _build_conditions(
            self,
            stmt: Select,
            name: Optional[str] = None,
            image_type: Optional[ImageType] = None,
            is_active: Optional[bool] = None,
    ) -> Select:
        if name:
            stmt = stmt.where(Bot.bot_name.icontains(name))

        if image_type:
            stmt = stmt.where(Bot.image_type == image_type)

        if is_active:
            stmt = stmt.where(Bot.is_active.is_(is_active))

        return stmt
