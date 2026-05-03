from typing import Optional

from pydantic import BaseModel, HttpUrl, Field

from services.types import ImageType, RestartPolicyType


class BaseBot(BaseModel):
    url: HttpUrl
    token: str

    branch: str = "main"
    bot_name: Optional[str] = None
    image_type: ImageType = ImageType.BASE

    cpu_quota_percents: int = 20
    cpu_period_percents: int = 100

    mem_reservation: int = 20
    mem_limit: int = 64

    restart_policy: RestartPolicyType = RestartPolicyType.UNLESS_STOPPED
    extra_env: dict[str, str] = Field(default_factory=dict)
    is_active: bool = True

    username: Optional[str] = None
    chat_id: Optional[int] = None


class Bot(BaseBot):
    id: int

    @property
    def mem_reservation_bytes(self) -> int:
        return self.mem_reservation * 1024 * 1024

    @property
    def mem_limit_bytes(self) -> int:
        return self.mem_limit * 1024 * 1024

    @property
    def cpu_quota(self) -> int:
        return self.cpu_quota_percents * 1000

    @property
    def cpu_period(self) -> int:
        return self.cpu_period_percents * 1000

    @property
    def name(self) -> str:
        return self.bot_name if self.bot_name else f"bot_{self.id}"

    @property
    def need_db(self) -> bool:
        return bool(int(self.extra_env.get("NEED_DB", "0")))

    @property
    def env_list(self) -> list[str]:
        extra_env: dict[str, str] = self.extra_env
        items = [f"{k}={v}" for k, v in extra_env.items()]
        items.append(f"BOT_ID={self.id}")
        items.append(f"BOT_TOKEN={self.token}")
        items.append(f"POSTGRES_DB_NAME={self.name}")
        return items


class BotsWithCount(BaseModel):
    bots: list[Bot] = Field(default_factory=list)
    count: int = 0


class CreateBot(BaseBot):
    pass


class UpdateBot(BaseModel):
    url: Optional[HttpUrl] = None
    token: Optional[str] = None
    branch: Optional[str] = None
    bot_name: Optional[str] = None
    image_type: Optional[ImageType] = None

    cpu_quota_percents: Optional[int] = None
    cpu_period_percents: Optional[int] = None

    mem_reservation: Optional[int] = None
    mem_limit: Optional[int] = None

    restart_policy: Optional[RestartPolicyType] = None
    extra_env: Optional[dict[str, str]] = None
    is_active: Optional[bool] = None

    username: Optional[str] = None
    chat_id: Optional[int] = None
