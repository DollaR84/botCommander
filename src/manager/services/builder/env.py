from dataclasses import is_dataclass, fields
from typing import Any

from barsik.config.adapters.base import BaseConfigAdapter

from application import dto
from config import Config


class EnvBuilder:

    def __init__(self, config: Config):
        self.config: Config = config
        self._data: dict[str, Any] = {}

        def _walk(obj: Any, _prefix: str) -> None:
            for field in fields(obj):
                field_name = field.name
                value = getattr(obj, field_name)

                env_key = f"{_prefix}_{field_name}".upper()
                if is_dataclass(value):
                    _walk(value, _prefix)
                else:
                    self._data[env_key] = str(value)

        for adapter_cls in BaseConfigAdapter.get_adapters():
            prefix = adapter_cls.get_prefix()
            section_name = adapter_cls.get_section_name()

            section = getattr(self.config, section_name, None)
            if section is None:
                continue

            _walk(section, prefix)

    @property
    def ext_data(self) -> dict[str, str]:
        return {
            "REDIS_DB_NUM": "1",
            "PYTHONOPTIMIZE": "1",
            "PYTHONUNBUFFERED": "1",
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
