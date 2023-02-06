import attr
import pytest

from replication.common.queue_mongo import indexes
from replication.common.yt_tools import dyntables
from replication.drafts import admin_run_draft
from replication.drafts import change_state


@pytest.mark.parametrize(
    'draft_data, expected_error, ensure_indexes_calls, create_dyntable_calls',
    [
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_pg',
                'target_names': ['test_sharded_pg_just_table'],
                'payload': {'action': 'init'},
            },
            None,
            1,
            2,
        ),
        pytest.param(
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_pg',
                'target_names': ['test_sharded_pg_just_table'],
                'payload': {'action': 'init'},
            },
            {
                'message': (
                    'Look for ERROR, WARNING level log entries '
                    'in draft cron logs'
                ),
                'code': 'replication-control-error',
                'reason': '["Replication not ready"]',
            },
            1,
            2,
            marks=[
                pytest.mark.config(
                    REPLICATION_WEB_CTL={
                        'admin': {'try_dry_run_in_init_draft': True},
                    },
                ),
            ],
        ),
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_ready_for_replication_pg',
                'target_names': [
                    'staging_test_yet_another_polygons_raw_pg',
                    'test_yet_another_polygons_raw_pg_raw',
                ],
                'payload': {'action': 'init'},
            },
            {
                'message': 'Rule is not ready for replication',
                'code': 'replication-control-error',
                'reason': (
                    '["Source \'postgres-test_yet_another_polygons_raw'
                    '_pg_shard0\' is not ready for replication: Replic'
                    'ation source table polygons is not indexed by rep'
                    'lication field created_at. Existing indexes: [[\''
                    'id\']]"]'
                ),
            },
            0,
            2,
        ),
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_pg',
                'target_names': [
                    'staging_test_conditioned_pg',
                    'test_conditioned_pg_just_table',
                    'staging_test_polygons_raw_pg',
                    'test_polygons_raw_pg_raw',
                ],
                'payload': {'action': 'enable'},
            },
            {
                'message': 'Rule is not ready for replication',
                'code': 'replication-control-error',
                'reason': (
                    '["Source \'postgres-test_polygons_raw_pg_shard0\' '
                    'is not ready for replication: '
                    'Replication source table polygons is not '
                    'indexed by replication field created_at. '
                    'Existing indexes: [[\'id\']]"]'
                ),
            },
            0,
            4,
        ),
    ],
)
@pytest.mark.pgsql('conditioned', files=['conditioned.sql'])
@pytest.mark.config(
    REPLICATION_SERVICE_CTL={
        'replication': {'source_check_before_start': True},
    },
)
async def test_ready_for_replication(
        replication_ctx,
        monkeypatch,
        draft_data,
        expected_error,
        no_sleep_in_queue_operations,
        ensure_indexes_calls,
        create_dyntable_calls,
):
    fake_calls_ctx = FakeCallsCtx()
    monkeypatch.setattr(
        indexes, 'ensure_indexes', fake_calls_ctx.ensure_indexes,
    )
    monkeypatch.setattr(
        dyntables, 'async_create_dyntable', fake_calls_ctx.create_dyntable,
    )
    await replication_ctx.rule_keeper.on_shutdown()
    if expected_error is not None:
        try:
            await admin_run_draft.process_draft(replication_ctx, draft_data)
        except (
            change_state.NotReadyForReplicationError,
            change_state.IllegalActionError,
        ) as exc:
            assert attr.asdict(exc.error_info) == expected_error
    else:
        await admin_run_draft.process_draft(replication_ctx, draft_data)
    assert fake_calls_ctx.ensure_indexes_calls == ensure_indexes_calls
    assert fake_calls_ctx.create_dyntable_calls == create_dyntable_calls


class FakeCallsCtx:
    ensure_indexes_calls = 0
    create_dyntable_calls = 0

    async def ensure_indexes(self, *args, **kwargs):
        self.ensure_indexes_calls += 1
        return 1

    async def create_dyntable(self, *args, **kwargs):
        self.create_dyntable_calls += 1


@pytest.mark.parametrize(
    'draft_data, rule_names, should_be_dropped',
    [
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_pg',
                'target_names': ['staging_test_conditioned_pg'],
                'payload': {'action': 'remove', 'drop_queue': True},
            },
            ['test_conditioned_pg'],
            True,
        ),
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_pg',
                'target_names': ['test_sharded_pg_just_table'],
                'payload': {'action': 'init'},
            },
            ['test_conditioned_pg'],
            False,
        ),
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_pg',
                'payload': {'action': 'remove'},
                'target_names': ['test_sharded_pg_just_table'],
            },
            ['test_conditioned_pg'],
            False,
        ),
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_pg',
                'payload': {'action': 'remove', 'drop_queue': True},
                'target_names': [
                    'staging_test_conditioned_pg',
                    'staging_test_polygons_no_raw',
                    'staging_test_sharded_pg',
                    'staging_test_polygons_raw_pg',
                ],
            },
            [
                'test_conditioned_pg',
                'test_polygons_no_raw',
                'test_sharded_pg',
                'test_polygons_raw_pg',
            ],
            True,
        ),
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_pg',
                'payload': {'action': 'remove', 'drop_queue': False},
                'target_names': [
                    'staging_test_conditioned_pg',
                    'staging_test_polygons_no_raw',
                    'staging_test_sharded_pg',
                    'staging_test_polygons_raw_pg',
                ],
            },
            [
                'test_conditioned_pg',
                'test_polygons_no_raw',
                'test_sharded_pg',
                'test_polygons_raw_pg',
            ],
            False,
        ),
    ],
)
async def test_drop_staging_collections(
        replication_ctx, draft_data, rule_names, should_be_dropped,
):
    rule_keeper = replication_ctx.rule_keeper
    for rule_name in rule_names:
        staging_coll_rule = rule_keeper.union_staging_db.get_queue(rule_name)
        staging_docs = await staging_coll_rule.union_find({}).to_list()
        assert staging_docs
    await replication_ctx.rule_keeper.on_shutdown()
    await admin_run_draft.process_draft(replication_ctx, draft_data)
    for rule_name in rule_names:
        staging_coll_rule = rule_keeper.union_staging_db.get_queue(rule_name)
        staging_docs = await staging_coll_rule.union_find({}).to_list()
        if should_be_dropped:
            assert not staging_docs
        else:
            assert staging_docs
