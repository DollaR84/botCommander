from datetime import datetime
from json import JSONDecodeError
import logging

from adaptix import loader, Provider
from barsik.utils.http import BearerAuth, HttpSyncClient
from descanso import RestBuilder
import requests

from shared.config import LLMConfig

from .base import BaseModel
from .data import GrokModelData, GrokParamsData


logger = logging.getLogger(__name__)
rest = RestBuilder()


class RequestsClient(HttpSyncClient):

    def __init__(self, url: str, token: str):
        super().__init__(url, BearerAuth(token))

    def get_retort_recipe(self) -> list[Provider]:
        return super().get_retort_recipe() + [
            loader(datetime, lambda x: datetime.fromtimestamp(int(x))),
        ]

    @rest.get("models")  # type: ignore[call-arg]
    def get_models(self) -> list[GrokModelData]:
        raise NotImplementedError


class GrokModel(BaseModel):

    def __init__(self, config: LLMConfig):
        super().__init__(config)

        self._params = GrokParamsData()
        self._client = RequestsClient(self.config.base_url, self.config.api_key)

        self._models: list[GrokModelData] = []
        self._models_map: dict[str, GrokModelData] = {}
        self.load()

    def load(self) -> None:
        try:
            self._models = self._client.get_models()
            self._models_map = {model.id: model for model in self._models}
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else "Unknown"
            logger.error("❌ [Grok] HTTP Error: %s | Status: %s", e, status_code)
        except requests.exceptions.ConnectionError:
            logger.error("❌ [Grok] Connection Error: Check your network or API endpoint URL.")
        except requests.exceptions.Timeout:
            logger.error("❌ [Grok] Timeout Error: Grok API is not responding in time.")
        except (JSONDecodeError, TypeError, ValueError) as e:
            logger.error("❌ [Grok] Serialization Error: API response structure changed or invalid. Details: %s", e)
        except requests.exceptions.RequestException as e:
            logger.error("❌ [Grok] General Request Error: %s", e)
        except Exception:
            logger.exception("Failed to load list of available models Grok")

    def get_model_id(self) -> str:
        if not self._models:
            raise ValueError("no Grok AI models available")

        if self.config.model and self.config.model in self._models_map:
            return self.config.model
        return self._models[0].id
