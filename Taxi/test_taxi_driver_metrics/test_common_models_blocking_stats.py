import pytest

from taxi_driver_metrics.common.models import blocking_stats
from taxi_driver_metrics.common.models import BlockingType


RULE_NAME = 'super_rule'
TST_ZONE = 'buhara'


@pytest.mark.config(
    DRIVER_METRICS_MONGO_TRANSFER_RULES={'source': 'metal_and_mdb_prefer_mdb'},
)
async def test_all(stq3_context):
    params = {'app': stq3_context, 'zone': TST_ZONE, 'rule_id': RULE_NAME}

    params_set = {**params, 'blocking_type': BlockingType.BY_ACTIONS}

    res = await blocking_stats.get_counter(
        stq3_context, 'super_rule', 'fake_zone',
    )

    assert res == 0

    await blocking_stats.decrement_counter(**params)

    res = await blocking_stats.get_counter(**params)

    assert res == 0

    await blocking_stats.increment_counter(**params_set)

    await blocking_stats.increment_counter(**params_set)

    res = await blocking_stats.get_counter(**params)

    assert res == 2

    res = await blocking_stats.get_actions_stats_by_zones(stq3_context)
    assert res
    assert res[0][1] == 2
    assert res[0][0] == TST_ZONE

    await blocking_stats.decrement_counter(**params)

    res = await blocking_stats.get_counter(**params)

    assert res == 1

    res = await blocking_stats.get_blocking_stats_by_types(stq3_context)
    assert res
    assert res[0][1] == 1
    assert res[0][0] == BlockingType.BY_ACTIONS.value

    res = await blocking_stats.get_blocking_stats_by_rules(stq3_context)
    assert res
    assert res[0][1] == 1
    assert res[0][0] == RULE_NAME

    await blocking_stats.decrement_counter(**params)
    await blocking_stats.decrement_counter(**params)

    res = await blocking_stats.get_counter(**params)

    assert res == 0
