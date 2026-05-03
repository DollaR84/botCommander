from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .base import BaseConfig


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOT_")

    id: int
    token: str


class TelegramConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TELEGRAM_")

    api_id: int
    api_hash: str

    workdir: str = "/app/sessions/"


class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLM_")

    name: str
    base_url: str
    api_key: str
    model: str


class BaseBotConfig(BaseConfig):
    model_config = SettingsConfigDict(env_nested_delimiter="__", extra="ignore")

    bot: BotConfig = Field(default_factory=BotConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
