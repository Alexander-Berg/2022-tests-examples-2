import pytest

from dashboards.internal import types
from dashboards.internal.models import configs
from dashboards.internal.models import service_branches


@pytest.fixture(name='add_config')
def _add_config():
    async def _wrapper(
            context: types.AnyContext,
            service_branch_id: int,
            bare_config: configs.BareConfig,
            status: str,
    ) -> configs.Config:
        config = await configs.Configs.insert_one_with_handlers(
            context,
            context.pg.primary,
            bare_config,
            configs.ConfigStatus(status),
        )
        await service_branches.ServiceBranches.create_link_to_config(
            context,
            context.pg.primary,
            service_branch_id=service_branch_id,
            config_id=config.id,
        )
        return config

    return _wrapper
