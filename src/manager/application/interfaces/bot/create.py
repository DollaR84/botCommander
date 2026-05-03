from abc import abstractmethod
from typing import Protocol

from db import domain


class CreateBotInterface(Protocol):

    @abstractmethod
    async def create_bot(self, data: domain.CreateBotModel) -> int:
        ...

    @abstractmethod
    async def create_bots(self, data: list[domain.CreateBotModel]) -> list[int]:
        ...
