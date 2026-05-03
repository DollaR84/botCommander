from typing import AsyncGenerator

from barsik.storage import BaseStorage
from dishka import from_context, Provider, Scope, provide

from config import Config
from services.docker import DockerService
from services.git import GitService
from services.builder import EnvBuilder, DockerConfigBuilder


class ServiceProvider(Provider):

    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_env_builder(self) -> EnvBuilder:
        return EnvBuilder()

    @provide(scope=Scope.APP)
    async def get_docker_builder(self, config: Config, env_builder: EnvBuilder) -> DockerConfigBuilder:
        return DockerConfigBuilder(config.docker, env_builder)

    @provide(scope=Scope.APP)
    async def get_git(self) -> GitService:
        return GitService()

    @provide(scope=Scope.APP)
    async def get_docker(
            self,
            config: Config,
            storage: BaseStorage,
            git: GitService,
            builder: DockerConfigBuilder,
    ) -> AsyncGenerator[DockerService, None]:
        service = DockerService(config.docker, storage, git, builder)
        yield service
        await service.close()
