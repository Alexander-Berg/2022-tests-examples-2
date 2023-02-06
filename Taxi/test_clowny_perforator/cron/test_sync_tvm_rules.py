import pytest

from clowny_perforator.generated.cron import run_cron
from clowny_perforator.internal import consts


@pytest.mark.config(
    CLOWNY_PERFORATOR_SYNC_RULES={'enabled': True, 'dry_run': False},
)
@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
async def test_sync_tvm_rules(
        cte_configs_mockserver, get_tvm_rules, cron_context,
):
    cte_configs_mockserver()
    await run_cron.main(
        ['clowny_perforator.crontasks.sync_tvm_rules', '-t', '0'],
    )

    async with cron_context.pg.primary.acquire() as conn:
        for env_type in consts.ENV_TYPES:
            generated = await _generate_tvm_rules(cron_context, conn, env_type)
            real_rules = get_tvm_rules(env_type)['value']
            assert _to_set(generated) == _to_set(real_rules)


def _to_set(rule_items):
    return {(rule['src'], rule['dst']) for rule in rule_items}


async def _generate_tvm_rules(context, conn, env_type):
    rules_items = await context.pstorage.rules.retrieve_rules(
        env_type=env_type, conn=conn,
    )
    return [
        {
            'src': rule['source']['tvm_name'],
            'dst': rule['destination']['tvm_name'],
        }
        for rule in rules_items
    ]
