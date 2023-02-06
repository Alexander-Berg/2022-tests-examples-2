import pytest

from clownductor.internal.param_defs import service_config
from clownductor.internal.param_defs import subsystems


@pytest.fixture
def get_remote_params(web_context):
    async def _wrapper(
            service_id: int, branch_id: int, system_name: str,
    ) -> subsystems.Subsystem:
        config = (
            await web_context.service_manager.parameters.get_service_config(
                service_id=service_id, branch_id=branch_id, is_remote=True,
            )
        )
        return config.get_subsystem(system_name)

    return _wrapper


@pytest.fixture
def set_remote_params(web_context, get_branch):
    async def _wrapper(
            service_id: int,
            branch_id: int,
            config: service_config.ServiceConfig,
    ):
        await web_context.service_manager.parameters.save_branch_values(
            service_id=service_id,
            branch=(await get_branch(branch_id))[0],
            service_config=config,
            is_remote=True,
        )

    return _wrapper


@pytest.fixture
def set_service_params(web_context, get_branch):
    async def _wrapper(
            service_id: int,
            branch_id: int,
            config: service_config.ServiceConfig,
    ):
        await web_context.service_manager.parameters.save_branch_values(
            service_id=service_id,
            branch=(await get_branch(branch_id))[0],
            service_config=config,
        )

    return _wrapper


@pytest.fixture
def set_service_general_params(web_context, get_branch):
    async def _wrapper(service_id: int, config: service_config.ServiceConfig):
        await web_context.service_manager.parameters.save_general_values(
            service_id=service_id, service_config=config,
        )

    return _wrapper


@pytest.fixture
def make_empty_config():
    def _wrapper() -> service_config.ServiceConfig:
        return service_config.ServiceConfig.make_empty()

    return _wrapper
