from dataclasses import dataclass
from typing import Type

from barsik.config.adapters.base import BaseConfigAdapter


@dataclass(frozen=True, slots=True)
class FlaskConfig:
    templates_dir: str


class FlaskConfigAdapter(BaseConfigAdapter[FlaskConfig]):
    data: Type[FlaskConfig] = FlaskConfig
