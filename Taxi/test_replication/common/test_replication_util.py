# pylint: disable=protected-access
import datetime

import pytest

from replication.common import replication_util
from replication.foundation import consts
from replication.foundation import declarations


@pytest.mark.now(datetime.datetime(2018, 3, 1, 10).isoformat())
async def test_get_target_ids(replication_ctx):
    rules_storage = replication_ctx.rule_keeper.rules_storage
    rule: declarations.ReplicationGroup = rules_storage.get_rules_list(
        rule_name='test_rule', source_types=[consts.SOURCE_TYPE_QUEUE_MONGO],
    )[0]

    assert replication_util.get_target_ids(replication_ctx, rule) == {}

    states = []
    for target in rule.targets:
        state = replication_ctx.rule_keeper.states_wrapper.get_state(
            rule.source.id, target.id,
        )
        states.append(state)
        init_kw = {}
        if target.id == 'yt-test_rule_struct-arni':
            init_kw['initial_ts'] = datetime.datetime(2018, 2, 28, 10)
        elif target.id == 'yt-test_rule_bson-arni':
            pass  # auto initial_ts (None)
        else:
            init_kw['initial_ts'] = None  # force no-initial-ts

        await state.init(**init_kw)

    await replication_ctx.rule_keeper.states_wrapper.refresh()
    assert replication_util.get_target_ids(replication_ctx, rule) == {
        'yt-test_rule_bson-arni': None,
        'yt-test_rule_bson-hahn': None,
        'yt-test_rule_struct-arni': datetime.datetime(2018, 2, 28, 10),
        'yt-test_rule_struct-hahn': None,
    }
