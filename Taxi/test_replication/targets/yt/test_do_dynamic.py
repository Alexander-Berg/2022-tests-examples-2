# pylint: disable=protected-access
import datetime

import pytest

from replication.drafts import admin_run_draft
from replication.targets.yt.raw_history import do_dynamic

PYTEST_YT_DATA = pytest.mark.yt(
    schemas=['yt_init_yt_tables.yaml'],
    static_table_data=['yt_fill_static_tables.yaml'],
    dyncamic_table_data=['yt_fill_dynamic_tables.yaml'],
)
YT_STATIC_TABLES_BEFORE = [
    '//home/taxi/unittests/test/test_raw_history/2021-11',
    '//home/taxi/unittests/test/test_raw_history/2021-12',
    '//home/taxi/unittests/test/test_raw_history/2022-01',
]


@pytest.mark.use_yt_local
@PYTEST_YT_DATA
async def test_do_dynamic(replication_ctx, yt_apply_force, yt_client):
    target = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        target_names=['test_raw_history_month'],
        target_unit_ids=['seneca-vla'],
    )[0].targets[0]
    tables = YT_STATIC_TABLES_BEFORE
    for table in tables:
        assert not yt_client.get(table + '/@dynamic')
    was_static_tables = await do_dynamic.do_dynamic(
        target._async_yt_client,
        target.meta,
        initial_stamp=datetime.datetime(2021, 11, 1, 1, 1),
    )
    assert sorted(was_static_tables) == tables
    for table in tables:
        assert yt_client.get(table + '/@dynamic')


@pytest.mark.use_yt_local
@PYTEST_YT_DATA
@pytest.mark.parametrize(
    'draft_payload, static_after, dynamic_after',
    [
        (
            {
                'action': 'init',
                'initial_stamp': '2021-11-01T01:01:00.000000+00:00',
            },
            [],
            YT_STATIC_TABLES_BEFORE,
        ),
        ({'action': 'enable'}, YT_STATIC_TABLES_BEFORE, []),
    ],
)
async def test_init_with_initial_stamp(
        replication_ctx,
        yt_apply_force,
        yt_client,
        draft_payload,
        static_after,
        dynamic_after,
):
    draft_data = {
        'draft_name': 'change_state',
        'rule_scope': 'test_raw_history',
        'payload': {'target_unit_ids': ['seneca-vla'], **draft_payload},
        'target_names': ['test_raw_history_month'],
    }
    await replication_ctx.rule_keeper.on_shutdown()
    await admin_run_draft.process_draft(replication_ctx, draft_data)
    for table in static_after:
        assert not yt_client.get(table + '/@dynamic')
    for table in dynamic_after:
        assert yt_client.get(table + '/@dynamic')
