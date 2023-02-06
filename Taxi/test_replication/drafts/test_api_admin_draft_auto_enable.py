import datetime
import pathlib

import freezegun
import pytest

from replication import core_context
from replication.drafts import admin_run_draft


@pytest.mark.now('2020-12-04T21:00:00.000+0000')
async def test_admin_draft_auto_enable_reschedule(
        replication_client, replication_ctx, load_json,
):
    draft_data = {
        'draft_name': 'disable_and_schedule_enable',
        'payload': {
            'event_id': 'event_name-admin_draft_raw2-future',
            'planned_ts': '2020-12-04T21:10:00.000+0000',
            'reschedule': True,
            'target_types': ['yt'],
        },
    }
    await _process_draft(replication_client, replication_ctx, draft_data)

    with freezegun.freeze_time() as timer:
        timer.tick(delta=datetime.timedelta(minutes=10))
        scheduled_info = await _enable_all_scheduled(replication_ctx)
        assert scheduled_info == {}

    state_ids = await _get_enabled_state_ids(replication_ctx)
    assert state_ids == [
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw1-arni',
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw2-arni',
    ]


@pytest.mark.now('2020-12-04T21:00:00.000+0000')
async def test_admin_draft_auto_enable(
        replication_client, replication_ctx, load_json,
):
    state_ids = await _get_enabled_state_ids(replication_ctx)
    assert state_ids == [
        'queue_mongo-staging_admin_draft-yt-admin_draft_raw1-arni',
    ]
    auto_enable_manager = replication_ctx.rule_keeper.auto_enable_manager
    scheduled_info = await auto_enable_manager.get_scheduled_info()
    assert scheduled_info == _ORIGINAL_SCHEDULE_INFO

    draft_data = {
        'draft_name': 'disable_and_schedule_enable',
        'payload': {
            'event_id': 'new_event_id',
            'planned_ts': '2020-12-04T21:10:00.000+0000',
            'target_unit_ids': ['arni', 'hahn'],
            'target_types': ['yt'],
        },
    }
    await _process_draft(replication_client, replication_ctx, draft_data)

    await _after_auto_enable(replication_ctx)


async def _process_draft(replication_client, replication_ctx, draft_data):
    response = await replication_client.post(
        f'/admin/v1/drafts/check', json=draft_data,
    )
    assert response.status == 200, await response.text()
    await replication_ctx.rule_keeper.on_shutdown()
    await admin_run_draft.process_draft(replication_ctx, draft_data)


_ORIGINAL_EVENTS = {
    'event_name-admin_draft_raw2-future': {
        'admin_draft_raw2': '2020-12-20T21:00:00',
    },
}
_ORIGINAL_SCHEDULE_INFO = {'admin_draft_scope': _ORIGINAL_EVENTS}


async def _get_enabled_state_ids(context):
    await context.rule_keeper.states_wrapper.refresh_cache()
    states = context.rule_keeper.states_wrapper.state_items(only_enabled=True)
    return sorted(list(state_id for state_id, _ in states))


async def _enable_all_scheduled(context):
    auto_enable_manager = context.rule_keeper.auto_enable_manager
    await auto_enable_manager.enable_all_scheduled()
    return await auto_enable_manager.get_scheduled_info()


async def _after_auto_enable(context: core_context.TasksCoreData):
    state_ids = await _get_enabled_state_ids(context)
    assert state_ids == []

    auto_enable_manager = context.rule_keeper.auto_enable_manager

    scheduled_info = await auto_enable_manager.get_scheduled_info()
    assert scheduled_info == {
        'admin_draft_scope': {
            **_ORIGINAL_EVENTS,
            'new_event_id': {'admin_draft_raw1': '2020-12-04T21:10:00'},
        },
    }

    scheduled_info = await _enable_all_scheduled(context)
    assert scheduled_info == {
        'admin_draft_scope': {
            **_ORIGINAL_EVENTS,
            'new_event_id': {'admin_draft_raw1': '2020-12-04T21:10:00'},
        },
    }

    with freezegun.freeze_time() as timer:
        timer.tick(delta=datetime.timedelta(minutes=10))
        scheduled_info = await _enable_all_scheduled(context)
        assert scheduled_info == _ORIGINAL_SCHEDULE_INFO

        state_ids = await _get_enabled_state_ids(context)
        assert state_ids == [
            'queue_mongo-staging_admin_draft-yt-admin_draft_raw1-arni',
        ]

    with freezegun.freeze_time() as timer:
        timer.tick(delta=datetime.timedelta(days=20))
        scheduled_info = await _enable_all_scheduled(context)
        assert scheduled_info == {}

        state_ids = await _get_enabled_state_ids(context)
        assert state_ids == [
            'queue_mongo-staging_admin_draft-yt-admin_draft_raw1-arni',
            'queue_mongo-staging_admin_draft-yt-admin_draft_raw2-arni',
        ]


@pytest.fixture
def test_env_id_setter(static_dir):
    return 'admin_drafts#' + pathlib.Path(static_dir).parent.stem
