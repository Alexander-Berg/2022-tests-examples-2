import pytest


@pytest.mark.suspend_periodic_tasks('matching-periodic')
@pytest.mark.suspend_periodic_tasks('wms-shifts-sync-periodic')
@pytest.mark.suspend_periodic_tasks('shift-changes-checker-periodic')
@pytest.mark.pgsql('grocery_performer_mentorship', files=['mentorship.sql'])
async def test_checker(
        taxi_grocery_performer_mentorship,
        db,
        published_events,
        personal,
        mock_driver_profiles,
        collect_common_message_keys,
):
    await taxi_grocery_performer_mentorship.run_periodic_task(
        'shift-changes-checker-periodic',
    )
    assert await collect_common_message_keys(2) == {
        '123_102': {'mentorship_was_cancelled': {}},
        '123_002': {'mentors_slot_is_cancelled': {}},
    }
    mentorship = db.mentorship(('changes_counter',))
    assert mentorship.get('123_101') == {
        'newbie_id': '123_101',
        'newbie_shift_id': '1002',
        'mentor_id': '123_001',
        'mentor_shift_id': '1001',
        'status': 'assigned',
        'changes_counter': 0,
    }
    assert mentorship.get('123_102') == {
        'newbie_id': '123_102',
        'newbie_shift_id': '1004',
        'mentor_id': None,
        'mentor_shift_id': None,
        'status': 'pending',
        'changes_counter': 0,
    }
    assert mentorship.get('123_103') == {
        'newbie_id': '123_103',
        'newbie_shift_id': '1005',
        'mentor_id': None,
        'mentor_shift_id': None,
        'status': 'assigned',
        'changes_counter': 0,
    }
    assert (await published_events.collect_by_newbie(1)) == {
        '123_102 1004 dismatch': {
            'performer_id': '123_002',
            'shift_id': '1003',
        },
    }


@pytest.mark.parametrize(
    'db_state_sql',
    [
        'cancel_mentor_shift.sql',
        'cancel_by_close_newbie_shift.sql',
        'cancel_by_close_mentor_shift.sql',
        'cancel_newbie_shift.sql',
    ],
)
async def test_mentor_cancel(
        taxi_grocery_performer_mentorship,
        db,
        stq,
        published_events,
        personal,
        mock_driver_profiles,
        collect_common_message_keys,
        db_state_sql,
        load,
):
    db.execute(load(db_state_sql))
    await taxi_grocery_performer_mentorship.run_periodic_task(
        'shift-changes-checker-periodic',
    )
    assert await collect_common_message_keys(2) == {
        '123_101': {'mentorship_was_cancelled': {}},
        '123_001': {'mentors_slot_is_cancelled': {}},
    }
    mentorship = db.mentorship(('changes_counter',))
    assert mentorship.get('123_101') == {
        'newbie_id': '123_101',
        'newbie_shift_id': '1002',
        'mentor_id': None,
        'mentor_shift_id': None,
        'status': 'pending',
        'changes_counter': 0,
    }
    assert (await published_events.collect_by_newbie(1)) == {
        '123_101 1002 dismatch': {
            'performer_id': '123_001',
            'shift_id': '1001',
        },
    }
