from dataclasses import dataclass
from pathlib import Path
from typing import Type

from barsik.config.adapters.base import BaseConfigAdapter


@dataclass(frozen=True, slots=True)
class DockerConfig:
    domain: str
    work_path: str
    dir_bots: str = "bots"
    network: str = "bot_network"

    @property
    def bots_dir(self) -> Path:
        return Path(self.work_path) / self.dir_bots


class DockerConfigAdapter(BaseConfigAdapter[DockerConfig]):
    data: Type[DockerConfig] = DockerConfig
