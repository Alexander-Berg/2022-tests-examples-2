import pytest

from testsuite.utils import callinfo


@pytest.mark.suspend_periodic_tasks('matching-periodic')
@pytest.mark.suspend_periodic_tasks('wms-shifts-sync-periodic')
@pytest.mark.pgsql('grocery_performer_mentorship', files=['newbies.sql'])
async def test_matcher(
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
    # If you need logs for this test, run
    # (grep matcher.cpp /tmp/ya.log | cut -f7)
    await taxi_grocery_performer_mentorship.run_periodic_task(
        'matching-periodic',
    )
    assert await collect_common_message_keys(5, now_in_msk()) == {
        '123_001': {
            'mentor_has_a_newbie': {
                'newbie_first_name': 'Люк',
                'newbie_phone': '+79991012345',
                'newbie_shift_starts': 2,
            },
        },
        '123_002': {
            'mentor_has_a_newbie': {
                'newbie_first_name': 'Энакин',
                'newbie_phone': '+79991012345',
                'newbie_shift_starts': 4,
            },
        },
        '123_101': {
            'mentor_was_found': {
                'mentor_first_name': 'Йода',
                'mentor_phone': '+79991012345',
            },
        },
        '123_102': {
            'mentor_was_found': {
                'mentor_first_name': 'Оби-Ван',
                'mentor_phone': '+79991012345',
            },
        },
        '123_103': {'mentor_was_not_found': {}},
    }
    mentorship = db.mentorship()
    assert mentorship.get('123_101') == {
        'newbie_id': '123_101',
        'newbie_shift_id': '1002',
        'mentor_id': '123_001',
        'mentor_shift_id': '1001',
        'status': 'assigned',
    }
    assert mentorship.get('123_102') == {
        'newbie_id': '123_102',
        'newbie_shift_id': '1004',
        'mentor_id': '123_002',
        'mentor_shift_id': '1003',
        'status': 'assigned',
    }
    assert mentorship.get('123_103') == {
        'newbie_id': '123_103',
        'newbie_shift_id': '1005',
        'mentor_id': None,
        'mentor_shift_id': None,
        'status': 'assigned',
    }
    assert (await published_events.collect_by_newbie(2)) == {
        '123_101 1002 match': {'performer_id': '123_001', 'shift_id': '1001'},
        '123_102 1004 match': {'performer_id': '123_002', 'shift_id': '1003'},
    }


@pytest.mark.suspend_periodic_tasks('matching-periodic')
@pytest.mark.suspend_periodic_tasks('wms-shifts-sync-periodic')
@pytest.mark.pgsql(
    'grocery_performer_mentorship', files=['newbie_and_mentor.sql'],
)
async def test_matcher2(
        taxi_grocery_performer_mentorship, db, personal, mock_driver_profiles,
):
    # If you need logs for this test, run
    # (grep matcher.cpp /tmp/ya.log | cut -f7)
    async def run_matcher():
        await taxi_grocery_performer_mentorship.run_task(
            'distlock/matcher-task',
        )

    await run_matcher()
    mentorship = db.mentorship()
    assert mentorship.get('123_101') == {
        'newbie_id': '123_101',
        'newbie_shift_id': '1002',
        'mentor_id': '123_001',
        'mentor_shift_id': '1001',
        'status': 'assigned',
    }
    db.execute(
        'INSERT INTO grocery_performer_mentorship.'
        'mentorship(newbie_id, newbie_shift_id) '
        ' VALUES (\'123_102\', \'1004\'), '
        ' (\'123_103\', \'1005\') ',
    )
    await run_matcher()
    mentorship = db.mentorship()
    assert mentorship.get('123_102') == {
        'newbie_id': '123_102',
        'newbie_shift_id': '1004',
        'mentor_id': None,
        'mentor_shift_id': None,
        'status': 'assigned',
    }
    assert mentorship.get('123_103') == {
        'newbie_id': '123_103',
        'newbie_shift_id': '1005',
        'mentor_id': '123_003',
        'mentor_shift_id': '1006',
        'status': 'assigned',
    }


@pytest.mark.suspend_periodic_tasks('matching-periodic')
@pytest.mark.suspend_periodic_tasks('wms-shifts-sync-periodic')
@pytest.mark.pgsql(
    'grocery_performer_mentorship', files=['old_pending_record.sql'],
)
async def test_close(
        taxi_grocery_performer_mentorship,
        db,
        stq,
        personal,
        mock_driver_profiles,
        collect_common_message_keys,
):
    async def run_matcher():
        await taxi_grocery_performer_mentorship.run_task(
            'distlock/matcher-task',
        )

    await run_matcher()
    mentorship = db.mentorship()
    assert mentorship.get('101_101') == {
        'newbie_id': '101_101',
        'newbie_shift_id': None,
        'mentor_id': None,
        'mentor_shift_id': None,
        'status': 'assigned',
    }
    # has notification about fail to find
    assert await collect_common_message_keys(1) == {
        '101_101': {'mentor_was_not_found': {}},
    }
    # check that there is no second notification
    # no second search
    await run_matcher()
    try:
        await stq.grocery_performer_communications_common_message.wait_call(
            timeout=1.0,
        )
        assert False
    except callinfo.CallQueueError:
        pass


@pytest.mark.suspend_periodic_tasks('matching-periodic')
@pytest.mark.suspend_periodic_tasks('wms-shifts-sync-periodic')
async def test_big_match(
        taxi_grocery_performer_mentorship, db, mockserver, personal,
):
    shifts_values = []
    mentors_values = []
    mentorship_values = []
    courier_id = 1000
    newbie_id = 2000
    shift_id = 9000

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        return {
            'profiles': [
                (
                    {
                        'park_driver_profile_id': pd_pi,
                        'data': {
                            'full_name': {'first_name': 'Оби-Ван'},
                            'phone_pd_ids': [
                                {'pd_id': '9cc9e88b3aec4e699eb19c1cd54f23ad'},
                            ],
                        },
                    }
                )
                for pd_pi in request.json['id_in_set']
            ],
        }

    def shift(starts_at, closes_at, depot_id, performer_id):
        nonlocal shift_id
        closes_at_sign = '+'
        starts_at_sign = '+'
        shift_id += 1
        status = 'waiting'
        if starts_at < 0:
            status = 'in_progress'
            starts_at_sign = '-'
            starts_at = -starts_at
        if closes_at < 0:
            status = 'closed'
            closes_at_sign = '-'
            closes_at = -closes_at
        shifts_values.append(
            f'(\'{shift_id}\',\'{performer_id}\',\'FFF{depot_id}\','
            f'\'{depot_id}\','
            f'CURRENT_TIMESTAMP {starts_at_sign} '
            f'interval \'{starts_at} hour\','
            f'CURRENT_TIMESTAMP {closes_at_sign} '
            f'interval \'{closes_at} hour\','
            f'\'{status}\')',
        )
        return shift_id

    def mentor(performer_id):
        mentors_values.append(f'(\'{performer_id}\',0,\'active\')')

    def newbie(shift_id, newbie_id):
        mentorship_values.append(f'(\'{newbie_id}\', \'{shift_id}\')')

    for depot_id in range(100, 110):
        for day in range(-1, 2):
            day_hours = day * 24
            for hour in range(9, 22):
                courier_id += 1
                shift(
                    day_hours + hour,
                    day_hours + hour + 4,
                    depot_id,
                    courier_id,
                )
                if courier_id % 2 == 0:
                    mentor(courier_id)
        for hour in range(9, 22):
            newbie_id += 1
            newbie(shift(hour, hour + 4, depot_id, newbie_id), newbie_id)

    db.execute(
        'INSERT INTO grocery_performer_mentorship.mentors'
        '(mentor_id, mentor_shifts_count, status) VALUES '
        '{};'.format(', '.join(mentors_values)),
    )
    db.execute(
        'INSERT INTO grocery_performer_mentorship.shifts'
        '(shift_id, performer_id, depot_id, legacy_depot_id, started_at,'
        'closes_at, status) VALUES '
        '{};'.format(', '.join(shifts_values)),
    )
    db.execute(
        'INSERT INTO grocery_performer_mentorship.mentorship'
        '(newbie_id, newbie_shift_id) VALUES '
        '{};'.format(', '.join(mentorship_values)),
    )
    await taxi_grocery_performer_mentorship.run_task('distlock/matcher-task')
