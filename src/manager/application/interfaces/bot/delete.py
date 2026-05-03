from abc import abstractmethod
from typing import Protocol


class DeleteBotInterface(Protocol):

    @abstractmethod
    async def delete_bot(self, bot_id: int) -> None:
        ...
