import pytest


@pytest.mark.pgsql(
    'grocery_performer_mentorship', files=['shifts.sql', 'newbies.sql'],
)
async def test_assign_with_record(
        taxi_grocery_performer_mentorship,
        db,
        stq,
        published_events,
        personal,
        mock_driver_profiles,
        add_depots,
        collect_common_message_keys,
        now_in_msk,
):
    # assign, when there is no previous mentor
    response = await taxi_grocery_performer_mentorship.post(
        '/internal/v1/mentorship/v1/assign',
        json={
            'newbie': {'performer_id': '123_101', 'shift_id': '1002'},
            'mentor': {'performer_id': '123_001', 'shift_id': '1001'},
        },
    )
    assert response.status_code == 204
    assert await collect_common_message_keys(2, now_in_msk()) == {
        '123_101': {
            'mentor_was_found': {
                'mentor_first_name': 'Йода',
                'mentor_phone': '+79991012345',
            },
        },
        '123_001': {
            'mentor_has_a_newbie': {
                'newbie_first_name': 'Люк',
                'newbie_phone': '+79991012345',
                'newbie_shift_starts': 2,
            },
        },
    }
    assert db.check_mentorship('123_101') == {
        'newbie_id': '123_101',
        'newbie_shift_id': '1002',
        'mentor_id': '123_001',
        'mentor_shift_id': '1001',
        'status': 'assigned',
    }
    assert (await published_events.collect_by_newbie(1)) == {
        '123_101 1002 match': {'performer_id': '123_001', 'shift_id': '1001'},
    }

    # assign, when there IS a previous mentor
    response = await taxi_grocery_performer_mentorship.post(
        '/internal/v1/mentorship/v1/assign',
        json={
            'newbie': {'performer_id': '123_101', 'shift_id': '1002'},
            'mentor': {'performer_id': '123_002', 'shift_id': '1003'},
        },
    )
    assert response.status_code == 204
    assert await collect_common_message_keys(3, now_in_msk()) == {
        '123_001': {'mentors_slot_is_cancelled': {}},
        '123_101': {
            'mentor_was_changed': {
                'mentor_first_name': 'Оби-Ван',
                'mentor_phone': '+79991012345',
            },
        },
        '123_002': {
            'mentor_has_a_newbie': {
                'newbie_first_name': 'Люк',
                'newbie_phone': '+79991012345',
                'newbie_shift_starts': 2,
            },
        },
    }
    assert db.check_mentorship('123_101') == {
        'newbie_id': '123_101',
        'newbie_shift_id': '1002',
        'mentor_id': '123_002',
        'mentor_shift_id': '1003',
        'status': 'assigned',
    }
    assert (await published_events.collect_by_newbie(2)) == {
        '123_101 1002 match': {'performer_id': '123_002', 'shift_id': '1003'},
        '123_101 1002 dismatch': {
            'performer_id': '123_001',
            'shift_id': '1001',
        },
    }

    # dismatch, when there is an previous mentor
    response = await taxi_grocery_performer_mentorship.post(
        '/internal/v1/mentorship/v1/assign',
        json={'newbie': {'performer_id': '123_101', 'shift_id': '1002'}},
    )
    assert response.status_code == 204
    assert await collect_common_message_keys(2) == {
        '123_002': {'mentors_slot_is_cancelled': {}},
        '123_101': {'mentorship_was_cancelled': {}},
    }
    assert db.check_mentorship('123_101') == {
        'newbie_id': '123_101',
        'newbie_shift_id': '1002',
        'mentor_id': None,
        'mentor_shift_id': None,
        'status': 'assigned',
    }
    assert (await published_events.collect_by_newbie(1)) == {
        '123_101 1002 dismatch': {
            'performer_id': '123_002',
            'shift_id': '1003',
        },
    }


@pytest.mark.pgsql('grocery_performer_mentorship', files=['shifts.sql'])
async def test_assign_without_record(
        taxi_grocery_performer_mentorship,
        db,
        stq,
        personal,
        mock_driver_profiles,
        add_depots,
        collect_common_message_keys,
        now_in_msk,
):
    response = await taxi_grocery_performer_mentorship.post(
        '/internal/v1/mentorship/v1/assign',
        json={
            'newbie': {'performer_id': '123_101', 'shift_id': '1002'},
            'mentor': {'performer_id': '123_001', 'shift_id': '1001'},
        },
    )
    assert response.status_code == 204
    assert await collect_common_message_keys(2, now_in_msk()) == {
        '123_101': {
            'mentor_was_found': {
                'mentor_first_name': 'Йода',
                'mentor_phone': '+79991012345',
            },
        },
        '123_001': {
            'mentor_has_a_newbie': {
                'newbie_first_name': 'Люк',
                'newbie_phone': '+79991012345',
                'newbie_shift_starts': 2,
            },
        },
    }
    assert db.check_mentorship('123_101') == {
        'newbie_id': '123_101',
        'newbie_shift_id': '1002',
        'mentor_id': '123_001',
        'mentor_shift_id': '1001',
        'status': 'assigned',
    }


@pytest.mark.pgsql(
    'grocery_performer_mentorship', files=['shifts.sql', 'newbies.sql'],
)
async def test_assign_shift_sync_lag(
        taxi_grocery_performer_mentorship,
        db,
        personal,
        mock_driver_profiles,
        collect_common_message_keys,
):
    response = await taxi_grocery_performer_mentorship.post(
        '/internal/v1/mentorship/v1/assign',
        json={
            'newbie': {'performer_id': '123_101', 'shift_id': '777'},
            'mentor': {'performer_id': '123_001', 'shift_id': '1001'},
        },
    )
    assert await collect_common_message_keys(2) == {
        '123_101': {
            'mentor_was_found': {
                'mentor_first_name': 'Йода',
                'mentor_phone': '+79991012345',
            },
        },
        '123_001': {
            'mentor_has_a_newbie': {
                'newbie_first_name': 'Люк',
                'newbie_phone': '+79991012345',
                'newbie_shift_starts': '1970-01-01T00:00',
            },
        },
    }
    assert response.status_code == 204
    assert db.check_mentorship('123_101') == {
        'newbie_id': '123_101',
        'newbie_shift_id': '777',
        'mentor_id': '123_001',
        'mentor_shift_id': '1001',
        'status': 'assigned',
    }
