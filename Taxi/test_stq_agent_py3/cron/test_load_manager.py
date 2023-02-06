import pytest

from stq_agent_py3.common import stq_config
from stq_agent_py3.crontasks.helpers import load_manager


@pytest.mark.config(
    STQ_AUTOBALANCING_SETTINGS={
        'cpu_tuning_enabled': True,
        'considerable_cpu_load_diff_prc': 10,
        'considerable_cpu_queue_load': 1,
    },
)
@pytest.mark.now('2019-01-01T20:00:30Z')
async def test_load_manager(cron_context, db):
    alive_by_queue = {
        'simple_queue': {'host1', 'host2', 'host3', 'host4'},
        'heavy_queue': {'host1', 'host2', 'host3'},
    }
    state = await stq_config.get_hosts_load_info(cron_context, alive_by_queue)
    configs_to_balance = await db.stq_config.find(
        {'_id': {'$in': ['simple_queue', 'heavy_queue']}},
    ).to_list(None)
    balancer_ctx = load_manager.GlobalWorkersManager(
        alive_by_queue,
        state,
        configs_to_balance,
        cron_context.config.STQ_AUTOBALANCING_SETTINGS,
    )
    res = balancer_ctx.get_sorted_by_load_desc('simple_queue', total=True)
    assert tuple(item.host for item in res) == (
        'host1',
        'host2',
        'host3',
        'host4',
    )
    res = balancer_ctx.get_sorted_by_load_desc('heavy_queue', total=True)
    assert tuple(item.host for item in res) == ('host2', 'host1', 'host3')
    balancer_ctx.change_instances_num('simple_queue', 'host1', -1, 'host3')
    res = balancer_ctx.get_sorted_by_load_desc('heavy_queue', total=True)
    assert tuple(item.host for item in res) == ('host1', 'host2', 'host3')
    balancer_ctx.change_instances_num('simple_queue', 'host1', 1)


@pytest.mark.now('2019-01-01T20:00:30Z')
async def test_load_manager_new_host(cron_context, db):
    alive_by_queue = {'queue_on_1_host': {'host1', 'host2'}}
    state = await stq_config.get_hosts_load_info(cron_context, alive_by_queue)
    configs_to_balance = await db.stq_config.find(
        {'_id': 'queue_on_1_host'},
    ).to_list(None)
    balancer_ctx = load_manager.GlobalWorkersManager(
        alive_by_queue,
        state,
        configs_to_balance,
        cron_context.config.STQ_AUTOBALANCING_SETTINGS,
    )
    balancer_ctx.change_instances_num('queue_on_1_host', 'host2', 1)
