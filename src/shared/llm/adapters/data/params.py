from dataclasses import dataclass

from barsik.dto.base import BaseData


@dataclass(slots=True)
class BaseParamsData(BaseData):
    max_tokens: int = 200
    temperature: float = 0.85


@dataclass(slots=True)
class GrokParamsData(BaseParamsData):
    pass


@dataclass(slots=True)
class GroqParamsData(BaseParamsData):
    presence_penalty: float = 0.6
    frequency_penalty: float = 0.5
