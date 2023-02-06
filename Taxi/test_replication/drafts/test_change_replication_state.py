import datetime

import pytest

from taxi.util import dates

from replication.drafts import admin_run_draft
from replication.drafts import exceptions

_SEQUENCE_STATE_ID = (
    'postgres-basic_source_postgres_raw_replicate_by_shard0-'
    'queue_mongo-staging_basic_source_postgres_raw_replicate_by'
)


async def _draft_handler(context, draft_data):
    params = {'draft_name': 'change_state', **draft_data}
    await context.rule_keeper.on_shutdown()
    return await admin_run_draft.process_draft(context, params)


@pytest.mark.parametrize('draft_handler', [_draft_handler])
@pytest.mark.parametrize(
    'input_json, expected_error_info',
    [
        (
            {
                'rule_scope': 'test_api_basestamp',
                'target_names': ['test_rule_struct'],
                'payload': {'action': 'disable'},
            },
            None,
        ),
        (
            {
                'rule_scope': 'test_pg',
                'target_names': ['test_sharded_pg_just_table'],
                'payload': {
                    'action': 'init',
                    'initial_stamp': dates.timestring(
                        datetime.datetime(2019, 1, 1), timezone='UTC',
                    ),
                },
            },
            None,
        ),
        (
            {
                'rule_scope': 'test_api_basestamp',
                'target_names': ['test_rule_struct'],
                'payload': {
                    'action': 'init',
                    'initial_stamp': dates.timestring(
                        datetime.datetime(2019, 1, 1), timezone='UTC',
                    ),
                },
            },
            None,
        ),
        (
            {
                'rule_scope': 'test_api_basestamp',
                'target_names': ['test_rule_struct'],
                'payload': {'action': 'remove', 'drop_queue': True},
            },
            None,
        ),
        (
            {
                'rule_scope': 'test_pg',
                'target_names': ['test_sharded_pg_just_table'],
                'payload': {'action': 'disable'},
            },
            exceptions.ErrorInfo(
                message=(
                    'Error while updating states, action disable. '
                    'Reason: State queue_mongo-staging_test_sharded_pg-'
                    'yt-test_sharded_pg_just_table-arni is already disabled. '
                    'To disable a rule, you must first switch it '
                    'to the enabled state.'
                ),
            ),
        ),
        (
            {
                'rule_scope': 'test_logbroker',
                'target_names': ['staging_test_logbroker'],
                'payload': {'action': 'enable'},
            },
            exceptions.ErrorInfo(
                message=(
                    'Error while updating states, action enable. '
                    'Reason: State postgres-test_logbroker_shard0'
                    '-queue_mongo-staging_test_logbroker is already '
                    'enabled. To restart, turn off the state by '
                    'performing the action: disable (the queue '
                    'will be saved). Then try turning it '
                    'on again.'
                ),
            ),
        ),
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'test_pg',
                'payload': {'action': 'init', 'initial_sequence_key': 20},
                'target_names': ['staging_test_conditioned_pg'],
            },
            exceptions.ErrorInfo(
                message='Incorrect input data',
                reason=(
                    'ReplicationStateTS(postgres-test_conditioned_pg_shard0-'
                    'queue_mongo-staging_test_conditioned_pg: '
                    'not initialized): '
                    '20 is incorrect new stamp for update, '
                    'expected datetime. This rule uses `initial_stamp` '
                    'for initialization. Please use it, and do not use '
                    '`initial_sequence_key` for this rule.'
                ),
            ),
        ),
        (
            {
                'draft_name': 'change_state',
                'rule_scope': 'all_sources',
                'payload': {'action': 'init', 'initial_sequence_key': 20},
                'target_names': [
                    'staging_basic_source_postgres_raw_replicate_by',
                ],
            },
            None,
        ),
    ],
)
async def test_change_state(
        replication_ctx, input_json, expected_error_info, draft_handler,
):
    if expected_error_info is None:
        await draft_handler(replication_ctx, input_json)
    else:
        with pytest.raises(exceptions.BaseError) as excinfo:
            await draft_handler(replication_ctx, input_json)
        assert excinfo.value.error_info == expected_error_info


async def test_sequence_key(replication_ctx):
    state = replication_ctx.rule_keeper.states_wrapper.get_state(
        replication_id=_SEQUENCE_STATE_ID,
    )
    assert not state.initialized
    await replication_ctx.rule_keeper.on_shutdown()
    await admin_run_draft.process_draft(
        replication_ctx,
        {
            'draft_name': 'change_state',
            'rule_scope': 'all_sources',
            'payload': {'action': 'init', 'initial_sequence_key': 20},
            'target_names': ['staging_basic_source_postgres_raw_replicate_by'],
        },
    )
    await state.refresh()
    assert state.initialized
    assert state.last_sequence_key == 20


@pytest.mark.parametrize('draft_handler', [_draft_handler])
async def test_change_state_reinit(
        replication_client, replication_ctx, load_json, draft_handler,
):
    state = replication_ctx.rule_keeper.states_wrapper.get_state(
        replication_id=(
            'queue_mongo-staging_test_api_basestamp-'
            'yt-test_api_basestamp_struct-arni'
        ),
    )
    assert state.last_synced
    assert state.current_stamp == datetime.datetime(2019, 4, 2, 3)

    api_state = replication_ctx.rule_keeper.states_wrapper.get_state(
        replication_id=(
            'api-test_api_basestamp-queue_mongo-staging_test_api_basestamp'
        ),
    )
    assert not api_state.initialized
    assert api_state.disabled

    async def _reinit():
        await draft_handler(
            replication_ctx,
            {
                'rule_scope': 'test_api_basestamp',
                'target_names': [
                    'test_api_basestamp_struct',
                    'staging_test_api_basestamp',
                ],
                'payload': {
                    'action': 'init',
                    'initial_stamp': dates.timestring(
                        datetime.datetime(2019, 1, 1), timezone='UTC',
                    ),
                },
            },
        )
        await state.refresh()
        # Sync at init iterative replication states
        assert state.last_synced is not None
        assert state.current_stamp == datetime.datetime(2019, 1, 1)

    await _reinit()
    await _reinit()

    await api_state.refresh()
    assert api_state.enabled
    assert api_state.last_synced is None
    assert api_state.current_stamp is None
