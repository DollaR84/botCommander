import logging
import random
from typing import Any, cast, Optional

from openai import AsyncOpenAI, APIConnectionError, APIStatusError, APITimeoutError, OpenAIError, RateLimitError

from shared.config import LLMConfig

from .adapters import BaseModel


logger = logging.getLogger(__name__)


class LLMService:

    def __init__(self, config: LLMConfig, system_instruction: str = ""):
        self.model = BaseModel.get(config.name, config)
        self.system_instruction = system_instruction

        self.client = AsyncOpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
        )

    def get_default_answer(self) -> str:
        return random.choice(["🙂", "😅", "🤔", "😐", "🙃", "😶", "🤷", "😄", "...", "ok",])

    async def generate_reply(self, bot_name: str, context: list[dict[str, str]], topic: Optional[str] = None) -> str:
        system_instruction = "\n\n".join([topic, self.system_instruction]) if topic else self.system_instruction
        messages: list[dict[str, str]] = [{"role": "system", "content": system_instruction}]

        for msg in context:
            role = "assistant" if msg.get("name") == bot_name else "user"
            content = f"{msg.get('name', 'Unknown')}: {msg.get('content', '')}"
            messages.append({"role": role, "content": content})

        try:
            model_name = self.model.get_model_id()
            logger.info("📡 [LLM] query to Model '%s' for bot %s...", model_name, bot_name)
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=cast(Any, messages),
                **self.model.params,
            )

            reply = response.choices[0].message.content
            if not reply:
                logger.warning("⚠️ [LLM] Model returned empty content!")
                return self.get_default_answer()

            reply = reply.strip() if reply else ""
            if reply.startswith(f"{bot_name}:"):
                reply = reply.replace(f"{bot_name}:", "")
            reply = reply.lstrip(",.:; ")

            return reply
        except RateLimitError:
            logger.error("🛑 [LLM] Rate limit exceeded! Check billing or limits.")
        except (APIConnectionError, APITimeoutError):
            logger.error("🌐 [LLM] Network issues or OpenAI timeout.")
        except APIStatusError as e:
            logger.error("🏢 [LLM] OpenAI server error: %s", e.status_code)
        except OpenAIError as e:
            logger.error("🧠 [LLM] OpenAI Specific Error: %s", str(e))
        except Exception:
            logger.exception("🔥 [LLM] Unexpected System Error")
        return self.get_default_answer()
