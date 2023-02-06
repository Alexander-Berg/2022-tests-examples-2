import pytest


@pytest.mark.pgsql('grocery_performer_mentorship', files=['data.sql'])
async def test_notify(
        taxi_grocery_performer_mentorship, db, collect_common_message_keys,
):
    assert db.select(('notifications', 'status'), 'mentorship') == [
        {'notifications': '{}', 'status': 'assigned'},
    ]
    await taxi_grocery_performer_mentorship.run_periodic_task(
        'end-shift-processing-periodic',
    )
    assert await collect_common_message_keys(1) == {
        '123_001': {'mentors_slot_is_over': {}},
    }
    assert db.select(('notifications', 'status'), 'mentorship') == [
        {'notifications': '{mentor,newbie}', 'status': 'assigned'},
    ]


@pytest.mark.pgsql(
    'grocery_performer_mentorship', files=['from_assigned_to_closed.sql'],
)
async def test_close(taxi_grocery_performer_mentorship, db):
    assert db.select(('notifications', 'status'), 'mentorship') == [
        {'notifications': '{mentor,newbie}', 'status': 'assigned'},
    ]
    assert db.select(('mentor_shifts_count',), 'mentors') == [
        {'mentor_shifts_count': 0},
    ]
    await taxi_grocery_performer_mentorship.run_periodic_task(
        'end-shift-processing-periodic',
    )
    assert db.select(('notifications', 'status'), 'mentorship') == [
        {'notifications': '{mentor,newbie}', 'status': 'closed'},
    ]
    assert db.select(('mentor_shifts_count',), 'mentors') == [
        {'mentor_shifts_count': 1},
    ]
