import datetime

import pytest

from replication.archiving import replication_settings


@pytest.mark.now('2020-07-18T15:26:00')
async def test_replication_settings_base(replication_ctx):
    event = replication_settings.get_event(
        replication_ctx.pluggy_deps.replication_settings,
    )

    await event.clean_archiving_states()
    states = await event.load_archiving_states(force=True)
    last_start_at = datetime.datetime(2020, 7, 18, 15, 0)
    assert states == {
        'arch_test_rule': replication_settings.ArchivingState(
            last_start_at=last_start_at,
        ),
        'two_days_in_progress': replication_settings.ArchivingState(
            last_start_at=datetime.datetime(2020, 7, 16, 15, 25),
            last_sync=datetime.datetime(2020, 7, 18, 15, 26),
        ),
    }

    state = states['arch_test_rule']
    assert state.last_sync is None
    assert state.last_start_at == last_start_at

    await event.sync_archiving_state(
        'arch_test_rule', last_start_at=last_start_at,
    )
    state = await _load_state(event, 'arch_test_rule')
    assert state.last_sync is not None

    with pytest.raises(replication_settings.RaceConditionError):
        await event.sync_archiving_state(
            'arch_test_rule',
            last_start_at=last_start_at + datetime.timedelta(minutes=5),
        )


@pytest.mark.now('2020-07-18T15:26:00')
async def test_replication_settings_new_event(replication_ctx):
    event = replication_settings.get_event(
        replication_ctx.pluggy_deps.replication_settings,
    )
    await event.load_archiving_states()

    new_id = 'new_id'
    started_at = await event.create_archiving_state(new_id)
    state = await _load_state(event, new_id)
    assert state.last_sync is None

    await event.sync_archiving_state(new_id, last_start_at=started_at)
    state = await _load_state(event, new_id)
    assert state.last_sync is not None
    assert state.last_failed is None

    await event.sync_archiving_state(
        new_id, last_start_at=started_at, failed=True,
    )
    state = await _load_state(event, new_id)
    assert state.last_sync is not None
    assert state.last_failed is not None


async def _load_state(event: replication_settings.ArchivingEvent, rule_name):
    states = await event.load_archiving_states(force=True)
    return states[rule_name]
