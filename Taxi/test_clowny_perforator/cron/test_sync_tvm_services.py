import pytest

from clowny_perforator.generated.cron import cron_context as context_module
from clowny_perforator.generated.cron import run_cron
from clowny_perforator.internal import consts


ContextType = context_module.Context


@pytest.mark.config(
    CLOWNY_PERFORATOR_SYNC_SERVICES={'enabled': True, 'dry_run': False},
)
async def test_sync_tvm_rules(
        cte_configs_mockserver, get_tvm_services, cron_context: ContextType,
):
    cte_configs_mockserver()
    await run_cron.main(
        ['clowny_perforator.crontasks.sync_tvm_services', '-t', '0'],
    )

    async with cron_context.pg.primary.acquire() as conn:
        for env_type in consts.ENV_TYPES:
            generated = await _generate_tvm_services(
                cron_context, conn, env_type,
            )
            real_services = get_tvm_services(env_type)['value']
            assert generated == real_services


async def _generate_tvm_services(context: ContextType, conn, env_type):
    services = await context.pstorage.services.retrieve_services(conn=conn)
    result = {}
    for service in services:
        tvm_id = None
        for env in service['environments']:
            if env['env_type'] == env_type:
                tvm_id = env['tvm_id']
                break
        if tvm_id:
            result[service['tvm_name']] = tvm_id
    return result
