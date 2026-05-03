from dataclasses import dataclass, field
from typing import Optional

from services.types import ImageType, RestartPolicyType

from barsik.db.domain.base import BaseModel


@dataclass(slots=True, kw_only=True)
class BaseBotModel(BaseModel):
    url: str
    token: str

    branch: str = "main"
    bot_name: Optional[str] = None
    image_type: ImageType = ImageType.BASE

    mem_reservation: int = 20
    mem_limit: int = 64

    cpu_quota_percents: int = 20
    cpu_period_percents: int = 100

    restart_policy: RestartPolicyType = RestartPolicyType.UNLESS_STOPPED
    is_active: bool = True
    extra_env: dict[str, str] = field(default_factory=dict)

    chat_id: Optional[int] = None
    username: Optional[str] = None


@dataclass(slots=True, kw_only=True)
class BotModel(BaseBotModel):
    id: int


@dataclass(slots=True, kw_only=True)
class CreateBotModel(BaseBotModel):
    pass


@dataclass(slots=True)
class UpdateBotModel(BaseModel):
    url: Optional[str] = None
    token: Optional[str] = None
    branch: Optional[str] = None
    bot_name: Optional[str] = None
    image_type: Optional[ImageType] = None

    mem_reservation: Optional[int] = None
    mem_limit: Optional[int] = None

    cpu_quota_percents: Optional[int] = None
    cpu_period_percents: Optional[int] = None

    restart_policy: Optional[RestartPolicyType] = None
    is_active: Optional[bool] = None
    extra_env: Optional[dict[str, str]] = None

    chat_id: Optional[int] = None
    username: Optional[str] = None
