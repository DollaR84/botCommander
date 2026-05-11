from dataclasses import dataclass
from typing import Type

from barsik.config.adapters.base import BaseConfigAdapter


@dataclass(frozen=True, slots=True)
class AdminConfig:
    username: str
    password_hash: str
    secret_key: str


class AdminConfigAdapter(BaseConfigAdapter[AdminConfig]):
    data: Type[AdminConfig] = AdminConfig
    secret_field_names = ("password_hash", "secret_key",)
