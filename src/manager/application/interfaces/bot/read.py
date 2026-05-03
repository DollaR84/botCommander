from abc import abstractmethod
from typing import Optional, Protocol

from db import domain

from services.types import ImageType


class GetBotInterface(Protocol):

    @abstractmethod
    async def get_bot(self, bot_id: int) -> Optional[domain.BotModel]:
        ...

    @abstractmethod
    async def get_bots(
            self,
            name: Optional[str] = None,
            image_type: Optional[ImageType] = None,
            is_active: Optional[bool] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> list[domain.BotModel]:
        ...

    @abstractmethod
    async def get_count_bots(
            self,
            name: Optional[str] = None,
            image_type: Optional[ImageType] = None,
            is_active: Optional[bool] = None,
    ) -> int:
        ...
