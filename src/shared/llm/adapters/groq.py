from shared.config import LLMConfig

from .base import BaseModel
from .data import GroqParamsData


class GroqModel(BaseModel):

    def __init__(self, config: LLMConfig):
        super().__init__(config)

        self._params = GroqParamsData()

    def get_model_id(self) -> str:
        if not self.config.model:
            raise ValueError("no set Groq AI model in .env")

        return self.config.model
