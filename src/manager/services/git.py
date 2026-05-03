import asyncio
from pathlib import Path
import shutil
import subprocess

from application import dto


class GitService:

    def __init__(self) -> None:
        self._locks: dict[str, asyncio.Lock] = {}

    async def ensure(self, bot: dto.Bot, bot_path: Path) -> None:
        lock = self._locks.get(bot.name)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[bot.name] = lock

        async with lock:
            await self._ensure_repo(bot, bot_path)

    async def _run_cmd(self, *args: str) -> subprocess.CompletedProcess:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
            )
        )

    async def _ensure_repo(self, bot: dto.Bot, bot_path: Path) -> None:
        git_dir = bot_path / ".git"
        branch = bot.branch or "main"

        if not bot_path.exists():
            try:
                await self._run_cmd("git", "clone", str(bot.url), str(bot_path))
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"git clone failed: {e.stderr}") from e

        elif not git_dir.exists():
            try:
                shutil.rmtree(bot_path)
            except Exception as e:
                raise RuntimeError("failed to remove invalid repo") from e

            try:
                await self._run_cmd("git", "clone", str(bot.url), str(bot_path))
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"git clone failed: {e.stderr}") from e

        else:
            try:
                await self._run_cmd("git", "-C", str(bot_path), "remote", "set-url", "origin", str(bot.url))
                await self._run_cmd("git", "-C", str(bot_path), "fetch", "origin")
                await self._run_cmd("git", "-C", str(bot_path), "checkout", branch)
                await self._run_cmd("git", "-C", str(bot_path), "reset", "--hard", f"origin/{branch}")
                await self._run_cmd("git", "-C", str(bot_path), "clean", "-fd")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"git fetch failed: {e.stderr}") from e
