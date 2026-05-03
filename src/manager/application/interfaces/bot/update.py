from abc import abstractmethod
from typing import Protocol

from db import domain


class UpdateBotInterface(Protocol):

    @abstractmethod
    async def update_bot(self, bot_id: int, update_data: domain.UpdateBotModel) -> int:
        ...
