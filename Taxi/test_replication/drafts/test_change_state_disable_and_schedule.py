import datetime
import pathlib

import freezegun
import pytest

from replication.drafts import admin_run_draft


@pytest.mark.now('2020-12-04T21:00:00.000+0000')
async def test_auto_enable(replication_client, replication_ctx, load_json):
    state_ids = await _get_enabled_state_ids(replication_ctx)
    assert state_ids == [
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw1-arni',
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw1-hahn',
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw2-arni',
    ]
    await _process_draft(
        replication_ctx,
        replication_client,
        {
            'action': 'disable_and_schedule_enable',
            'event_id': 'event_name',
            'planned_ts': '2020-12-04T21:10:00.000+0000',
        },
    )

    state_ids = await _get_enabled_state_ids(replication_ctx)
    assert state_ids == []

    with freezegun.freeze_time() as timer:
        timer.tick(delta=datetime.timedelta(minutes=10))
        auto_enable_manager = replication_ctx.rule_keeper.auto_enable_manager
        await auto_enable_manager.enable_all_scheduled()

    state_ids = await _get_enabled_state_ids(replication_ctx)
    assert state_ids == [
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw1-arni',
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw1-hahn',
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw2-arni',
    ]


@pytest.mark.now('2020-12-04T21:00:00.000+0000')
async def test_auto_enable_remove(
        replication_client, replication_ctx, load_json,
):
    state_ids = await _get_enabled_state_ids(replication_ctx)
    assert state_ids == [
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw1-arni',
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw1-hahn',
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw2-arni',
    ]
    await _process_draft(
        replication_ctx,
        replication_client,
        {
            'action': 'disable_and_schedule_enable',
            'event_id': 'event_name',
            'planned_ts': '2020-12-04T21:10:00.000+0000',
        },
    )

    state_ids = await _get_enabled_state_ids(replication_ctx)
    assert state_ids == []

    await _process_draft(
        replication_ctx,
        replication_client,
        {
            'action': 'disable_and_schedule_enable',
            'event_id': 'event_name',
            'remove': True,
        },
    )
    auto_enable_manager = replication_ctx.rule_keeper.auto_enable_manager
    assert (await auto_enable_manager.get_scheduled_info()) == {}

    state_ids = await _get_enabled_state_ids(replication_ctx)
    assert state_ids == []


@pytest.mark.now('2020-12-04T21:00:00.000+0000')
async def test_auto_enable_reschedule(
        replication_client, replication_ctx, load_json,
):
    state_ids = await _get_enabled_state_ids(replication_ctx)
    assert state_ids == [
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw1-arni',
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw1-hahn',
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw2-arni',
    ]
    await _process_draft(
        replication_ctx,
        replication_client,
        {
            'action': 'disable_and_schedule_enable',
            'event_id': 'event_name',
            'planned_ts': '2020-12-04T21:10:00.000+0000',
        },
    )

    state_ids = await _get_enabled_state_ids(replication_ctx)
    assert state_ids == []

    await _process_draft(
        replication_ctx,
        replication_client,
        {
            'action': 'disable_and_schedule_enable',
            'event_id': 'event_name',
            'planned_ts': '2020-12-04T21:20:00.000+0000',
            'reschedule': True,
        },
    )
    auto_enable_manager = replication_ctx.rule_keeper.auto_enable_manager
    assert (await auto_enable_manager.get_scheduled_info()) == {
        'admin_draft_scope': {
            'event_name': {
                'admin_draft_raw1': '2020-12-04T21:20:00',
                'admin_draft_raw2': '2020-12-04T21:20:00',
            },
        },
    }

    state_ids = await _get_enabled_state_ids(replication_ctx)
    assert state_ids == []


async def _process_draft(replication_ctx, replication_client, payload):
    draft_data = {
        'draft_name': 'change_state',
        'rule_scope': 'admin_draft_scope',
        'target_names': ['admin_draft_raw1', 'admin_draft_raw2'],
        'payload': payload,
    }
    response = await replication_client.post(
        f'/admin/v1/drafts/check', json=draft_data,
    )
    assert response.status == 200, await response.text()
    await replication_ctx.rule_keeper.on_shutdown()
    await admin_run_draft.process_draft(replication_ctx, draft_data)


async def _get_enabled_state_ids(context):
    await context.rule_keeper.states_wrapper.refresh_cache()
    states = context.rule_keeper.states_wrapper.state_items(only_enabled=True)
    return sorted(list(state_id for state_id, _ in states))


@pytest.fixture
def test_env_id_setter(static_dir):
    return 'admin_drafts#' + pathlib.Path(static_dir).parent.stem
