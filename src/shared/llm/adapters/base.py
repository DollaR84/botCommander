from __future__ import annotations

from abc import abstractmethod
from typing import Any, Type

from barsik.adapters import BaseAdapter

from shared.config import LLMConfig

from .data import BaseParamsData


class BaseModel(BaseAdapter, is_abstract=True):
    _adapters: dict[str, Type[BaseModel]] = {}

    @classmethod
    def get(cls, name: str, *args: Any, **kwargs: Any) -> BaseModel:
        model_cls: Type[BaseModel] | None = cls.get_adapter(name)
        if model_cls is None:
            raise ValueError(f"Model '{name}' does not exist")

        return model_cls(*args, **kwargs)

    @classmethod
    def get_names(cls) -> list[str]:
        return list(sorted(cls.get_available_adapters_names()))

    def __init__(self, config: LLMConfig):
        self.config = config
        self._params: BaseParamsData

    @abstractmethod
    def __call__(self) -> str:
        raise NotImplementedError

    @property
    def params(self) -> dict[str, Any]:
        return self._params.dict()

    @abstractmethod
    def get_model_id(self) -> str:
        raise NotImplementedError
