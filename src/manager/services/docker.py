import asyncio
from functools import wraps
import json
from typing import Any, Awaitable, Callable, Optional, ParamSpec, TypeAlias

from barsik.storage import BaseStorage
import aiodocker
from flask import jsonify, Response

from application import dto
from config.adapters import DockerConfig

from .builder import DockerConfigBuilder
from .git import GitService


FlaskResponse: TypeAlias = Response | tuple[Response, int]
P = ParamSpec("P")


def docker_error_handler(
        default_errors: Optional[dict[Any, Any]] = None
) -> Callable[[Callable[P, Awaitable[FlaskResponse]]], Callable[P, Awaitable[FlaskResponse]]]:
    def decorator(func: Callable[P, Awaitable[FlaskResponse]]) -> Callable[P, Awaitable[FlaskResponse]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> FlaskResponse:
            try:
                return await func(*args, **kwargs)

            except (aiodocker.exceptions.DockerError, Exception) as e:
                if isinstance(e, aiodocker.exceptions.DockerError):
                    status_code = e.status
                    message = e.message
                else:
                    status_code = 500
                    message = str(e)

                custom = None
                if default_errors:
                    custom = default_errors.get(status_code)
                custom = jsonify(custom) if isinstance(custom, dict) else custom

                response = jsonify({"status": "error", "message": message}) if custom is None else custom
                return response, status_code

        return wrapper
    return decorator


class DockerService:

    def __init__(self, config: DockerConfig, storage: BaseStorage, git: GitService, builder: DockerConfigBuilder):
        self.config = config
        self._storage = storage
        self.git = git
        self.builder = builder

        self._client = aiodocker.Docker()

        async def _bg_prune() -> None:
            await self.prune()
        asyncio.create_task(_bg_prune())

    async def close(self) -> None:
        await self._client.close()

    @docker_error_handler()
    async def start(self, bot: dto.Bot) -> FlaskResponse:
        if not bot.is_active:
            return jsonify({"status": "error", "message": f"Bot '{bot.name}' is disabled in settings"}), 403

        bot_path = self.config.bots_dir / bot.name
        await self.git.ensure(bot, bot_path)
        config = self.builder(bot)

        try:
            container, is_running = await self.is_running(bot)
        except aiodocker.exceptions.DockerError as e:
            if e.status == 404:
                container = await self._client.containers.create(config, name=bot.name)
                is_running = False
            else:
                raise e

        if not is_running and container is not None:
            await container.start()

        container_id = container.id if container is not None else 0
        return jsonify({"status": "started", "id": container_id})

    @docker_error_handler()
    async def stop(self, bot: dto.Bot) -> FlaskResponse:
        try:
            container = await self._client.containers.get(bot.name)

            try:
                await container.stop(t=5)
            except aiodocker.exceptions.DockerError as e:
                if e.status != 304:
                    raise e

            await container.delete(force=True)
        except aiodocker.exceptions.DockerError as e:
            if e.status != 404:
                raise e

        await self._storage.delete(f"stats:{bot.name}")
        return jsonify({"bot": bot.name, "status": "stopped"})

    @docker_error_handler()
    async def update(self, bot: dto.Bot) -> FlaskResponse:
        await self.download(bot)

        try:
            container = await self._client.containers.get(bot.name)
            await container.restart()
            status = "updated and restarted"

        except aiodocker.exceptions.DockerError as e:
            status = "updated (but container not found)" if e.status == 404 else "update error"

        return jsonify({"status": "success", "details": status})

    @docker_error_handler({404: {"status": "offline", "memory": "0", "cpu": "0"}})
    async def get_stats(self, bot: dto.Bot) -> FlaskResponse:
        cache_key = f"stats:{bot.name}"
        cached_data = await self._storage.get(cache_key)
        if cached_data:
            return jsonify(json.loads(cached_data) if isinstance(cached_data, str) else cached_data)

        container = await self._client.containers.get(bot.name)
        stats_list = await container.stats(stream=False)
        stats = stats_list[0]
        mem_usage = stats.get("memory_stats", {}).get("usage", 0) / (1024 * 1024)

        cpu_stats = stats.get("cpu_stats", {})
        cpu_usage = cpu_stats.get("cpu_usage", {})
        precpu_stats = stats.get("precpu_stats", {})
        precpu_usage = precpu_stats.get("cpu_usage", {})
        cpu_delta = cpu_usage.get("total_usage", 0) - precpu_usage.get("total_usage", 0)
        system_delta = cpu_stats.get("system_cpu_usage", 0) - precpu_stats.get("system_cpu_usage", 0)
        cpu_percent = 0.0
        if system_delta > 0 and cpu_delta > 0:
            num_cpus = len(cpu_usage.get("percpu_usage", [1]))
            num_cpus = stats.get("online_cpus", num_cpus)
            cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0

        stats_data = {
            "cpu": f"{cpu_percent:.1f}%",
            "memory": f"{round(mem_usage, 2)} MB",
            "status": "running",
        }

        await self._storage.set(cache_key, json.dumps(stats_data), ex=10)
        return jsonify(stats_data)

    @docker_error_handler()
    async def get_logs(self, bot: dto.Bot) -> FlaskResponse:
        container = await self._client.containers.get(bot.name)
        raw_logs = await container.log(tail=100, stdout=True, stderr=True, timestamps=True)

        formatted_logs = []
        for line in raw_logs:
            clean_line = line.decode("utf-8", errors="ignore") if isinstance(line, bytes) else line
            formatted_logs.append(clean_line.rstrip() + "\n")

        return jsonify({
            "bot": bot.name,
            "logs": "".join(formatted_logs)
        })

    @docker_error_handler()
    async def prune(self) -> FlaskResponse:
        containers = await self._client.images.prune(filters={"dangling": False})
        images = await self._client.images.prune()
        networks = await self._client.networks.prune()

        return jsonify({
            "status": "success",
            "reclaimed_space": "done",
            "details": {
                "containers": containers.get("ContainersDeleted", []),
                "images": images.get("ImagesDeleted", []),
                "networks": networks.get("NetworksDeleted", []),
                "space_reclaimed": images.get("SpaceReclaimed", 0)
            }
        })

    async def sync_bots(self, bots: list[dto.Bot]) -> None:
        for bot in bots:
            try:
                container, is_running = await self.is_running(bot)

                if bot.is_active:
                    if container is None:
                        await self.start(bot)
                    elif not is_running:
                        await container.start()

                else:
                    await self.stop(bot)

            except aiodocker.exceptions.DockerError as e:
                if e.status == 404:
                    if bot.is_active:
                        await self.start(bot)

    async def is_running(self, bot: dto.Bot) -> tuple[aiodocker.containers.DockerContainer | None, bool]:
        try:
            container = await self._client.containers.get(bot.name)
        except aiodocker.exceptions.DockerError as e:
            if e.status == 404:
                return None, False
            raise e

        container_info = await container.show()
        return container, container_info["State"]["Running"]

    async def download(self, bot: dto.Bot) -> None:
        bot_path = self.config.bots_dir / bot.name
        await self.git.ensure(bot, bot_path)
