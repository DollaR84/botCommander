from dataclasses import fields
from typing import Literal, Type, TypeVar

from pydantic import BaseModel as PydanticBaseModel

from barsik.db.domain.base import BaseModel as DomainBaseModel


DomainT = TypeVar("DomainT", bound=DomainBaseModel)
DtoT = TypeVar("DtoT", bound=PydanticBaseModel)


class Mapper:

    @staticmethod
    def to_domain(
            dto: PydanticBaseModel,
            domain_cls: Type[DomainT],
            *,
            exclude: set[str] | None = None,
            exclude_unset: bool = False,
            mode: Literal["json", "python"] = "python",
    ) -> DomainT:
        data = dto.model_dump(mode=mode, by_alias=True, exclude_unset=exclude_unset)
        domain_fields = {f.name for f in fields(domain_cls)}

        if exclude:
            domain_fields -= exclude

        return domain_cls(**{
            k: v for k, v in data.items() if k in domain_fields
        })

    @staticmethod
    def to_dto(
            dto_cls: Type[DtoT],
            data: DomainBaseModel,
            *,
            exclude: set | None = None,
            exclude_unset: bool = False,
    ) -> DtoT:
        dto_fields = set(dto_cls.model_fields.keys())

        return dto_cls(**{
            k: v for k, v in data.dict(exclude=exclude, exclude_unset=exclude_unset).items() if k in dto_fields
        })
