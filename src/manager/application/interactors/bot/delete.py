from application import interfaces


class DeleteBot:

    def __init__(self, gateway: interfaces.DeleteBotInterface):
        self.gateway = gateway

    async def __call__(self, bot_id: int) -> None:
        await self.gateway.delete_bot(bot_id)
