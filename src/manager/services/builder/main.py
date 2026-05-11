from typing import Any

from application import dto
from config.adapters import DockerConfig

from .env import EnvBuilder


class DockerConfigBuilder:

    def __init__(self, config: DockerConfig, env_builder: EnvBuilder):
        self.config = config
        self.env_builder = env_builder

    def _get_labels(self, bot: dto.Bot) -> dict[str, str]:
        domain = f"{bot.name}.{self.config.domain}"
        return {
            "caddy": domain,
            "caddy.reverse_proxy": "{{upstreams 8080}}"
        }

    def _get_binds(self, bot: dto.Bot) -> list[str]:
        bot_path = self.config.bots_dir / bot.name
        return [
            f"{str(bot_path)}:/app:rw",
        ]

    def _get_restart_policy(self, bot: dto.Bot) -> dict[str, Any]:
        return {
            "Name": bot.restart_policy.value,
            "MaximumRetryCount": 5,
        }

    def _get_log_config(self) -> dict[str, Any]:
        return {
            "Type": "json-file",
            "Config": {
                "max-size": "10m",
                "max-file": "3"
            }
        }

    def _get_host_config(self, bot: dto.Bot) -> dict[str, Any]:
        return {
            "NetworkMode": self.config.network,
            "Binds": self._get_binds(bot),
            "RestartPolicy": self._get_restart_policy(bot),
            "Memory": bot.mem_limit_bytes,
            "MemoryReservation": bot.mem_reservation_bytes,
            "MemorySwap": bot.mem_limit_bytes,
            "CpuQuota": bot.cpu_quota,
            "CpuPeriod": bot.cpu_period,
            "StopTimeout": 10,
            "LogConfig": self._get_log_config(),
        }

    def _get_healthcheck(self) -> dict[str, Any]:
        return {
            "Test": ["CMD", "curl", "-f", "http://localhost:8080/health"],
            "Interval": 30 * 1000000000,
            "Timeout": 30 * 1000000000,
            "Retries": 3,
            "StartPeriod": 10 * 1000000000,
        }

    def __call__(self, bot: dto.Bot) -> dict[str, Any]:
        selected_image = f"bot-{bot.image_type.value}:latest"

        return {
            "Image": selected_image,
            "WorkingDir": self.config.work_path,
            "Cmd": ["python", "main.py"],
            "ExposedPorts": {"8080/tcp": {}},
            "Labels": self._get_labels(bot),
            "HostConfig": self._get_host_config(bot),
            "Env": self.env_builder(bot),
            "Healthcheck": self._get_healthcheck(),
        }
