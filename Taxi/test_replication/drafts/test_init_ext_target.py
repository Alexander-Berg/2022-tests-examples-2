import datetime

import pytest

from taxi.util import dates

from replication.drafts import admin_run_draft


@pytest.mark.parametrize(
    'draft_data,last_ts',
    [
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_pg',
                'target_names': ['test_polygons_raw_pg_raw_ext'],
                'payload': {'action': 'init'},
            },
            datetime.datetime(2020, 4, 2, 2, 30, 0),
        ),
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_pg',
                'target_names': ['test_polygons_raw_pg_raw_ext'],
                'payload': {
                    'action': 'init',
                    'initial_stamp': dates.timestring(
                        datetime.datetime(2019, 1, 1), timezone='UTC',
                    ),
                },
            },
            datetime.datetime(2019, 1, 1, 0, 0, 0),
        ),
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_pg',
                'target_names': ['test_sharded_pg_ext_not_initialized'],
                'payload': {'action': 'init'},
            },
            None,
        ),
    ],
)
@pytest.mark.config(
    REPLICATION_SERVICE_CTL={
        'archiving': {'ttl_override': {'test_polygons_raw_pg': 1800}},
    },
)
async def test_init_ext_target(replication_ctx, draft_data, last_ts):
    await replication_ctx.rule_keeper.on_shutdown()
    await admin_run_draft.process_draft(replication_ctx, draft_data)
    state = [
        state[1]
        for state in replication_ctx.rule_keeper.states_wrapper.state_items(
            target_names=draft_data['target_names'],
        )
    ][0]
    assert state.current_ts == last_ts
