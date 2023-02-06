import datetime

import pytest

from tests_dispatch_airport import common
import tests_dispatch_airport.utils as utils

URL = '/v1/reposition_availability'
HEADERS = common.DEFAULT_DISPATCH_AIRPORT_HEADER


@pytest.mark.geoareas(filename='geoareas.json')
async def test_negative(taxi_dispatch_airport, taxi_config, mockserver):
    # bad request, empty driver_ids
    response = await taxi_dispatch_airport.post(
        URL, {'driver_ids': [], 'point': utils.OUT_POSITION}, headers=HEADERS,
    )
    assert response.status_code == 400
    r_json = response.json()
    assert r_json['code'] == 'BAD_REQUEST'

    # no target_airport_id:
    # - out of airport
    # - check_in zone waiting airport
    # - not check_in zone notification point
    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb']['distributive_zone_type'] = 'check_in'
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})
    await taxi_dispatch_airport.invalidate_caches()

    for point in [
            utils.OUT_POSITION,
            utils.WAITING_POSITION,
            utils.SVO_NOTIFICATION_POSITION,
    ]:
        response = await taxi_dispatch_airport.post(
            URL,
            {'driver_ids': ['dbid_uuid0'], 'point': point},
            headers=HEADERS,
        )
        assert response.status_code == 404
        r_json = response.json()
        assert r_json['code'] == 'ZONE_NOT_FOUND'

    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    del zones_config['ekb']['distributive_zone_type']
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_ZONES': zones_config,
            'DISPATCH_AIRPORT_WITHOUT_RFID_LABEL_AVAILABILITY': {
                'ekb': {'enabled_without_active_label': True},
            },
        },
    )
    await taxi_dispatch_airport.invalidate_caches()

    dp_timeout = True
    fv_timeout = True

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        nonlocal dp_timeout
        assert request.json['id_in_set'] == ['dbid_uuid0']
        assert request.json['projection'] == ['data.car_id']
        if dp_timeout:
            raise mockserver.TimeoutError()
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'dbid_uuid0',
                    'data': {'car_id': '123'},
                },
            ],
        }

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _fleet_vehicles(request):
        nonlocal fv_timeout
        assert request.json['id_in_set'] == ['dbid_123']
        assert request.json['projection'] == ['data.number_normalized']
        if fv_timeout:
            raise mockserver.TimeoutError()
        return {
            'vehicles': [
                {
                    'data': {'number_normalized': '0180MP178'},
                    'park_id_car_id': 'dbid_123',
                },
            ],
        }

    # failed driver-profiles
    response = await taxi_dispatch_airport.post(
        URL,
        {'driver_ids': ['dbid_uuid0'], 'point': utils.WAITING_POSITION},
        headers=HEADERS,
    )
    assert response.status_code == 500
    r_json = response.json()
    assert r_json['code'] == 'CAR_NUMBERS_FETCH_ERROR'

    dp_timeout = False
    # failed fleet-vehicles
    response = await taxi_dispatch_airport.post(
        URL,
        {'driver_ids': ['dbid_uuid0'], 'point': utils.WAITING_POSITION},
        headers=HEADERS,
    )
    assert response.status_code == 500
    r_json = response.json()
    assert r_json['code'] == 'CAR_NUMBERS_FETCH_ERROR'

    fv_timeout = False

    # configuration error 1
    response = await taxi_dispatch_airport.post(
        URL,
        {'driver_ids': ['dbid_uuid0'], 'point': utils.WAITING_POSITION},
        headers=HEADERS,
    )
    assert response.status_code == 500
    r_json = response.json()
    assert r_json['code'] == 'WRONG_CONFIGURATION'

    # configuration error 2
    zones_config = taxi_config.get(
        'DISPATCH_AIRPORT_WITHOUT_RFID_LABEL_AVAILABILITY',
    )
    zones_config['ekb'].update(
        {'start_local_time': '11:20', 'end_local_time': '10:20'},
    )
    taxi_config.set_values(
        {'DISPATCH_AIRPORT_WITHOUT_RFID_LABEL_AVAILABILITY': zones_config},
    )
    await taxi_dispatch_airport.invalidate_caches()
    response = await taxi_dispatch_airport.post(
        URL,
        {'driver_ids': ['dbid_uuid0'], 'point': utils.WAITING_POSITION},
        headers=HEADERS,
    )
    assert response.status_code == 500
    r_json = response.json()
    assert r_json['code'] == 'WRONG_CONFIGURATION'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'enabled,working_hours,timezone,allowed_by_schedule',
    [
        (False, None, None, None),
        # 10:30 - 19:30 by Europe/Moscow == 07:30 - 16:30 by UTC
        (
            True,
            {'start_local_time': '10:30', 'end_local_time': '19:30'},
            None,
            False,
        ),
        (
            True,
            {'start_local_time': '10:30', 'end_local_time': '19:30'},
            None,
            True,
        ),
        # 10:30 - 19:30 by Asia/Yekaterinburg == 05:30 - 14:30 by UTC
        (
            True,
            {'start_local_time': '10:30', 'end_local_time': '19:30'},
            {'timezone': 'Asia/Yekaterinburg'},
            False,
        ),
        (
            True,
            {'start_local_time': '10:30', 'end_local_time': '19:30'},
            {'timezone': 'Asia/Yekaterinburg'},
            True,
        ),
    ],
)
async def test_positive_by_rfid_labels(
        taxi_dispatch_airport,
        taxi_config,
        mocked_time,
        mockserver,
        enabled,
        working_hours,
        timezone,
        allowed_by_schedule,
):
    date = datetime.datetime(2021, 10, 4, 8, 00, 00)
    if not allowed_by_schedule:
        date = datetime.datetime(2021, 10, 4, 7, 00, 00)
    if timezone is not None:
        if allowed_by_schedule:
            date = datetime.datetime(2021, 10, 4, 6, 00, 00)
        else:
            date = datetime.datetime(2021, 10, 4, 5, 00, 00)

    mocked_time.set(date)

    settings = {'ekb': {'enabled_without_active_label': enabled}}
    if working_hours:
        settings['ekb'].update(working_hours)
    if timezone:
        settings['ekb'].update(timezone)
    taxi_config.set_values(
        {'DISPATCH_AIRPORT_WITHOUT_RFID_LABEL_AVAILABILITY': settings},
    )
    await taxi_dispatch_airport.invalidate_caches()

    # dbid_uuid0 - outdated active label (allowed if available by schedule)
    # dbid_uuid1 - without label (allowed if available by schedule)
    # dbid_uuid2 - with active label, allowed
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        assert set(request.json['id_in_set']) == set(
            ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
        )
        assert request.json['projection'] == ['data.car_id']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'dbid_uuid0',
                    'data': {'car_id': 'id35377'},
                },
                {
                    'park_driver_profile_id': 'dbid_uuid1',
                    'data': {'car_id': 'id54977'},
                },
                {
                    'park_driver_profile_id': 'dbid_uuid2',
                    'data': {'car_id': 'id1234'},
                },
            ],
        }

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _fleet_vehicles(request):
        assert set(request.json['id_in_set']) == set(
            ['dbid_id35377', 'dbid_id54977', 'dbid_id1234'],
        )
        assert request.json['projection'] == ['data.number_normalized']
        return {
            'vehicles': [
                {
                    'data': {'number_normalized': 'XE35377'},
                    'park_id_car_id': 'dbid_id35377',
                },
                {
                    'data': {'number_normalized': 'ХТ54977'},
                    'park_id_car_id': 'dbid_id54977',
                },
                {
                    'data': {'number_normalized': 'AB12345'},
                    'park_id_car_id': 'dbid_id1234',
                },
            ],
        }

    response = await taxi_dispatch_airport.post(
        URL,
        {
            'driver_ids': ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
            'point': utils.WAITING_POSITION,
        },
        headers=HEADERS,
    )
    r_json = response.json()
    r_json['allowed'].sort()
    r_json['forbidden'].sort(key=lambda x: x['driver_id'])
    if not enabled:
        assert r_json == {
            'allowed': ['dbid_uuid2'],
            'forbidden': [
                {'driver_id': 'dbid_uuid0', 'reason': 'OUTDATED_ACTIVE_LABEL'},
                {'driver_id': 'dbid_uuid1', 'reason': 'WITHOUT_ACTIVE_LABEL'},
            ],
        }
    elif working_hours or timezone:
        if allowed_by_schedule:
            assert r_json == {
                'allowed': ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
                'forbidden': [],
            }
        else:
            assert r_json == {
                'allowed': ['dbid_uuid2'],
                'forbidden': [
                    {
                        'driver_id': 'dbid_uuid0',
                        'reason': 'OUTDATED_ACTIVE_LABEL',
                    },
                    {
                        'driver_id': 'dbid_uuid1',
                        'reason': 'FORBIDDEN_BY_SCHEDULE',
                    },
                ],
            }


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['driver_events.sql'])
async def test_positive_by_entry_tracking(
        taxi_dispatch_airport, taxi_config, mockserver,
):
    settings = {
        'ekb': {
            'enter_accumulation_period': 30,
            'marked_area_type': 'terminal',
            'maximum_number_of_entries': 3,
        },
    }
    taxi_config.set_values({'DISPATCH_AIRPORT_AREA_ENTRY_TRACKING': settings})
    settings = {'enabled': True}
    taxi_config.set_values(
        {'DISPATCH_AIRPORT_REPOSITION_AVAILABILITY_ENTRY_LIMIT': settings},
    )
    await taxi_dispatch_airport.invalidate_caches()

    # dbid_uuid0 - allowed: without any enter events
    # dbid_uuid1 - allowed: with enter events less then enter limit
    # dbid_uuid2 - forbidden: with enter events equal to enter limit
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        assert set(request.json['id_in_set']) == set(
            ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
        )
        assert request.json['projection'] == ['data.car_id']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'dbid_uuid0',
                    'data': {'car_id': 'id1234'},
                },
                {
                    'park_driver_profile_id': 'dbid_uuid1',
                    'data': {'car_id': 'id2345'},
                },
                {
                    'park_driver_profile_id': 'dbid_uuid2',
                    'data': {'car_id': 'id3456'},
                },
            ],
        }

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _fleet_vehicles(request):
        assert set(request.json['id_in_set']) == set(
            ['dbid_id1234', 'dbid_id2345', 'dbid_id3456'],
        )
        assert request.json['projection'] == ['data.number_normalized']
        return {
            'vehicles': [
                {
                    'data': {'number_normalized': 'AB12345'},
                    'park_id_car_id': 'dbid_id1234',
                },
                {
                    'data': {'number_normalized': 'AB23456'},
                    'park_id_car_id': 'dbid_id2345',
                },
                {
                    'data': {'number_normalized': 'AB34567'},
                    'park_id_car_id': 'dbid_id3456',
                },
            ],
        }

    # all cases check
    response = await taxi_dispatch_airport.post(
        URL,
        {
            'driver_ids': ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
            'point': utils.WAITING_POSITION,
        },
        headers=HEADERS,
    )
    r_json = response.json()
    r_json['allowed'].sort()
    r_json['forbidden'].sort(key=lambda x: x['driver_id'])

    assert r_json == {
        'allowed': ['dbid_uuid0', 'dbid_uuid1'],
        'forbidden': [
            {'driver_id': 'dbid_uuid2', 'reason': 'EXCEED_NUMBER_OF_ENTRIES'},
        ],
    }

    # has anti-carousel disabled
    settings = {
        'enabled': True,
        'allowed_airports': ['ekb'],
        'allowed_zones': ['ekb'],
    }
    taxi_config.set_values(
        {'DISPATCH_AIRPORT_PARTNER_PROTOCOL_ANTI_CAROUSEL': settings},
    )
    await taxi_dispatch_airport.invalidate_caches()

    response = await taxi_dispatch_airport.post(
        URL,
        {
            'driver_ids': ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
            'point': utils.WAITING_POSITION,
        },
        headers=HEADERS,
    )
    r_json = response.json()
    r_json['allowed'].sort()
    r_json['forbidden'].sort(key=lambda x: x['driver_id'])

    assert r_json == {
        'allowed': ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
        'forbidden': [],
    }

    # has no entry settings
    settings = {
        'enabled': False,
        'allowed_airports': ['ekb'],
        'allowed_zones': ['ekb'],
    }
    taxi_config.set_values(
        {'DISPATCH_AIRPORT_PARTNER_PROTOCOL_ANTI_CAROUSEL': settings},
    )
    settings = {}
    taxi_config.set_values({'DISPATCH_AIRPORT_AREA_ENTRY_TRACKING': settings})
    await taxi_dispatch_airport.invalidate_caches()

    response = await taxi_dispatch_airport.post(
        URL,
        {
            'driver_ids': ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
            'point': utils.WAITING_POSITION,
        },
        headers=HEADERS,
    )
    r_json = response.json()
    r_json['allowed'].sort()
    r_json['forbidden'].sort(key=lambda x: x['driver_id'])

    assert r_json == {
        'allowed': ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
        'forbidden': [],
    }


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid_uuid1', 'airport_queue_ok'),
        ('dbid_uuid', 'dbid_uuid2', 'airport_queue_fraud_detected'),
    ],
    topic_relations=[
        ('airport_queue', 'airport_queue_ok'),
        ('airport_queue', 'airport_queue_fraud_detected'),
    ],
)
@pytest.mark.config(
    DISPATCH_AIRPORT_REPOSITION_AVAILABILITY_FORBIDDEN_TAGS=True,
    DISPATCH_AIRPORT_FORBIDDEN_TAGS=[
        {'reason': 'blacklist', 'tags': ['airport_queue_blacklist_driver']},
        {
            'reason': 'anti_fraud_tag',
            'tags': [
                'airport_queue_fraud_detected',
                'airport_queue_fraud_detected_short',
                'airport_queue_fraud_detected_long',
            ],
        },
    ],
)
async def test_positive_by_forbidden_tags(
        taxi_dispatch_airport, taxi_config, mockserver,
):
    # dbid_uuid0 - allowed: without any tags
    # dbid_uuid1 - allowed: with non kick tags
    # dbid_uuid2 - forbidden: have kick tag
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        assert set(request.json['id_in_set']) == set(
            ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
        )
        assert request.json['projection'] == ['data.car_id']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'dbid_uuid0',
                    'data': {'car_id': 'id1234'},
                },
                {
                    'park_driver_profile_id': 'dbid_uuid1',
                    'data': {'car_id': 'id2345'},
                },
                {
                    'park_driver_profile_id': 'dbid_uuid2',
                    'data': {'car_id': 'id3456'},
                },
            ],
        }

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _fleet_vehicles(request):
        assert set(request.json['id_in_set']) == set(
            ['dbid_id1234', 'dbid_id2345', 'dbid_id3456'],
        )
        assert request.json['projection'] == ['data.number_normalized']
        return {
            'vehicles': [
                {
                    'data': {'number_normalized': 'AB12345'},
                    'park_id_car_id': 'dbid_id1234',
                },
                {
                    'data': {'number_normalized': 'AB23456'},
                    'park_id_car_id': 'dbid_id2345',
                },
                {
                    'data': {'number_normalized': 'AB34567'},
                    'park_id_car_id': 'dbid_id3456',
                },
            ],
        }

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    def _driver_tags(http_request):
        assert http_request.json == {
            'drivers': [
                {'dbid': 'dbid', 'uuid': 'uuid0'},
                {'dbid': 'dbid', 'uuid': 'uuid1'},
                {'dbid': 'dbid', 'uuid': 'uuid2'},
            ],
        }
        return mockserver.make_response(
            json={
                'drivers': [
                    {
                        'dbid': 'dbid',
                        'uuid': 'uuid1',
                        'tags': ['airport_queue_ok'],
                    },
                    {
                        'dbid': 'dbid',
                        'uuid': 'uuid2',
                        'tags': ['airport_queue_fraud_detected'],
                    },
                ],
            },
        )

    await taxi_dispatch_airport.invalidate_caches()

    response = await taxi_dispatch_airport.post(
        URL,
        {
            'driver_ids': ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
            'point': utils.WAITING_POSITION,
        },
        headers=HEADERS,
    )
    r_json = response.json()
    r_json['allowed'].sort()
    r_json['forbidden'].sort(key=lambda x: x['driver_id'])

    assert r_json == {
        'allowed': ['dbid_uuid0', 'dbid_uuid1'],
        'forbidden': [
            {'driver_id': 'dbid_uuid2', 'reason': 'FORBIDDEN_BY_TAG'},
        ],
    }


@pytest.mark.config(DISPATCH_AIRPORT_REPOSITION_AVAILABILITY_QUEUED_STATE=True)
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('check_queued_drivers', [True, False])
async def test_positive_by_queued_state(
        taxi_dispatch_airport, mockserver, check_queued_drivers,
):
    # dbid_uuid0 - allowed: status entered
    # dbid_uuid1 - allowed: no driver in airport_drivers cashe
    # dbid_uuid2 - forbidden: status queued
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        assert set(request.json['id_in_set']) == set(
            ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
        )
        assert request.json['projection'] == ['data.car_id']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'dbid_uuid0',
                    'data': {'car_id': 'id1234'},
                },
                {
                    'park_driver_profile_id': 'dbid_uuid1',
                    'data': {'car_id': 'id2345'},
                },
                {
                    'park_driver_profile_id': 'dbid_uuid2',
                    'data': {'car_id': 'id3456'},
                },
            ],
        }

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _fleet_vehicles(request):
        assert set(request.json['id_in_set']) == set(
            ['dbid_id1234', 'dbid_id2345', 'dbid_id3456'],
        )
        assert request.json['projection'] == ['data.number_normalized']
        return {
            'vehicles': [
                {
                    'data': {'number_normalized': 'AB12345'},
                    'park_id_car_id': 'dbid_id1234',
                },
                {
                    'data': {'number_normalized': 'AB23456'},
                    'park_id_car_id': 'dbid_id2345',
                },
                {
                    'data': {'number_normalized': 'AB34567'},
                    'park_id_car_id': 'dbid_id3456',
                },
            ],
        }

    await taxi_dispatch_airport.invalidate_caches()

    response = await taxi_dispatch_airport.post(
        URL,
        {
            'driver_ids': ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
            'point': utils.WAITING_POSITION,
            'check_queued_drivers': check_queued_drivers,
        },
        headers=HEADERS,
    )
    r_json = response.json()
    r_json['allowed'].sort()
    r_json['forbidden'].sort(key=lambda x: x['driver_id'])

    if check_queued_drivers:
        assert r_json == {
            'allowed': ['dbid_uuid0', 'dbid_uuid1'],
            'forbidden': [
                {'driver_id': 'dbid_uuid2', 'reason': 'HAS_QUEUED_STATE'},
            ],
        }
    else:
        assert r_json == {
            'allowed': ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2'],
            'forbidden': [],
        }
