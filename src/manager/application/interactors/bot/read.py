from typing import Optional

from application import dto
from application import interfaces

from services.types import ImageType

from barsik.db import Mapper


class BaseGetBot:

    def __init__(self, gateway: interfaces.GetBotInterface):
        self.gateway = gateway


class GetBot(BaseGetBot):

    async def __call__(self, bot_id: int) -> Optional[dto.Bot]:
        domain_data = await self.gateway.get_bot(bot_id)
        return Mapper.to_dto(dto.Bot, domain_data) if domain_data else None


class GetBots(BaseGetBot):

    async def __call__(
            self,
            name: Optional[str] = None,
            image_type: Optional[ImageType] = None,
            is_active: Optional[bool] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> list[dto.Bot]:
        domain_data = await self.gateway.get_bots(name, image_type, is_active, offset, limit)
        return [
            Mapper.to_dto(dto.Bot, bot_data)
            for bot_data in domain_data
        ]


class GetBotsWithCount(BaseGetBot):

    async def __call__(
            self,
            name: Optional[str] = None,
            image_type: Optional[ImageType] = None,
            is_active: Optional[bool] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> dto.BotsWithCount:
        count = await self.gateway.get_count_bots(name, image_type, is_active)
        bots = await self.gateway.get_bots(name, image_type, is_active, offset, limit)

        return dto.BotsWithCount(
            bots=[
                Mapper.to_dto(dto.Bot, bot_data)
                for bot_data in bots
            ],
            count=count,
        )
