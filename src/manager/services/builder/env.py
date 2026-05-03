from typing import Any

from barsik.utils.cache import get_config
from pydantic import BaseModel

from application import dto
from shared.config import BaseBotConfig


class EnvBuilder:

    def __init__(self) -> None:
        _temp_config: BaseBotConfig = get_config(BaseBotConfig)
        self._data: dict[str, Any] = {}

        def _walk(obj: BaseModel) -> None:
            prefix = obj.model_config.get("env_prefix", "")
            for field_name in obj.model_fields:
                value = getattr(obj, field_name)
                if isinstance(value, BaseModel):
                    _walk(value)
                else:
                    env_key = f"{prefix}{field_name}".upper()
                    self._data[env_key] = str(value)

        _walk(_temp_config)

    @property
    def ext_data(self) -> dict[str, str]:
        return {
            "REDIS_DB_NUM": "1",
            "PYTHONOPTIMIZE": "1",
            "PYTHONUNBUFFERED": "1",
            "PYTHONPATH": "/app:/app/shared",
        }

    @property
    def data(self) -> dict[str, Any]:
        return self._data | self.ext_data

    def extend(self, bot: dto.Bot) -> dict[str, Any]:
        return self.data | bot.extra_env

    def __call__(self, bot: dto.Bot) -> list[str]:
        data = self.extend(bot)
        data_list = [f"{k}={v}" for k, v in data.items()]

        return list(set(data_list))
