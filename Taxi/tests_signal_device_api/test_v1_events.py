# pylint: disable=C0302

import hashlib

import dateutil.parser
import ecdsa
import pytest

from tests_signal_device_api import common

ENDPOINT = 'v1/events'
FLEET_NOTIFICATIONS_ENDPOINT = (
    '/fleet-notifications/v1/notifications/external-message'
)

DEVICE_ID = 'device_id_test'
EVENT_ID = 'event_id_test'
EVENT_AT = '2020-02-17T23:08:00+01:00'

PARAMS = {'device_id': DEVICE_ID, 'timestamp': '2020-02-17T23:09:00Z'}
GNSS = {  # wrong special for test
    'lat': -99,
    'lon': 199,
    'speed_kmph': -4.4,
    'accuracy_m': -3.3,
    'direction_deg': -5.5,
}
EVENT = {
    'id': EVENT_ID,
    'at': EVENT_AT,
    'type': 'custom_event_type',
    'software_version': '1.0-2',
    'gnss': GNSS,
    'extra': '{payload}',
    'video_file_id': (
        '/77fdc498f9174eba9722aff77cdb0a38/mnt/sd/'
        'signalq/0000000000000000/2019-12-23T13-19-43Z_0.mp4'
    ),
    'external_video_file_id': 'some_file_2.mp4',
    'photo_file_id': (
        '/77fdc498f9174eba9722aff77cdb0a38/mnt/sd/'
        'signalq/0000000000000000/2019-12-23T13-19-44Z.jpeg'
    ),
    'external_photo_file_id': 'some_file_1.jpeg',
}


def assert_equals(actual, expected):
    assert isinstance(actual, (int, float))
    assert isinstance(expected, (int, float))
    assert actual == pytest.approx(expected)


def select_events(pgsql, device_id):
    fields = [
        'device_id',
        'created_at',
        'updated_at',
        'event_id',
        'software_version',
        'event_at',
        'event_type',
        'gnss_latitude',
        'gnss_longitude',
        'gnss_speed_kmph',
        'gnss_accuracy_m',
        'gnss_direction_deg',
        'video_file_id',
        'external_video_file_id',
        'photo_file_id',
        'external_photo_file_id',
        'signalled',
        'extra',
        'park_id',
        'car_id',
        'car_device_binding_id',
        'driver_profile_id',
        'driver_name',
        'vehicle_plate_number',
    ]
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT {} FROM signal_device_api.events '
        'WHERE device_id={}'.format(','.join(fields), device_id),
    )
    return [{k: v for (k, v) in zip(fields, event)} for event in list(db)]


async def send_status_ok(taxi_signal_device_api, pgsql, jwt_key):
    status = common.make_ok_status(True, True)
    json_body = common.make_ok_json_body(status, DEVICE_ID)
    response = await taxi_signal_device_api.post(
        'v1/status',
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                jwt_key, 'v1/status', {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200, response.text


SERIAL_NUMBER = 'SOMESERIAL1'


@pytest.mark.pgsql('signal_device_api_meta_db')
@pytest.mark.parametrize('signalled', [True, False])
async def test_ok(taxi_signal_device_api, signalled, pgsql, stq):
    jwt_key = common.add_device_return_private_key(
        pgsql, 1, device_id=DEVICE_ID, serial_number=SERIAL_NUMBER,
    )
    new_event = {**EVENT, 'signalled': signalled}
    for _ in range(0, 2):  # strict idempotency
        await send_status_ok(taxi_signal_device_api, pgsql, jwt_key)
        response = await taxi_signal_device_api.post(
            ENDPOINT,
            headers=common.make_jwt_headers(
                jwt_key, ENDPOINT, PARAMS, new_event,
            ),
            params=PARAMS,
            json=new_event,
        )
        assert response.status_code == 200, response.text
        assert response.json() == {'id': EVENT_ID}

        db_events = select_events(pgsql, 1)
        assert len(db_events) == 1, db_events

        db_event = db_events[0]
        assert db_event['device_id'] == 1
        assert db_event['event_id'] == EVENT_ID
        assert db_event['event_at'] == dateutil.parser.parse(EVENT['at'])
        assert db_event['event_type'] == new_event['type']
        assert db_event['video_file_id'] == new_event['video_file_id']
        assert (
            db_event['external_video_file_id']
            == new_event['external_video_file_id']
        )
        assert db_event['photo_file_id'] == new_event['photo_file_id']
        assert (
            db_event['external_photo_file_id']
            == new_event['external_photo_file_id']
        )
        assert db_event['extra'] == new_event['extra']
        assert db_event['software_version'] == new_event['software_version']
        assert db_event['signalled'] == new_event['signalled']

        common.assert_now(db_event['created_at'])
        common.assert_now(db_event['updated_at'])
        assert_equals(db_event['gnss_latitude'], GNSS['lat'])
        assert_equals(db_event['gnss_longitude'], GNSS['lon'])
        assert_equals(db_event['gnss_speed_kmph'], GNSS['speed_kmph'])
        assert_equals(db_event['gnss_accuracy_m'], GNSS['accuracy_m'])
        assert_equals(db_event['gnss_direction_deg'], GNSS['direction_deg'])

        assert db_event['park_id'] is None
        assert db_event['car_id'] is None
        assert db_event['car_device_binding_id'] is None
        assert db_event['driver_profile_id'] is None
        assert db_event['driver_name'] is None
        assert db_event['vehicle_plate_number'] is None

    assert stq.signal_device_api_tags.times_called == 0
    common.check_alr_inserted(
        pgsql, serial_number=SERIAL_NUMBER, field_affected='v1_events_at',
    )


@pytest.mark.config(
    SIGNAL_DEVICE_API_LB_DRIVEMATICS_EVENTS_PRODUCER_SETTINGS={
        'enabled': True,
        'throw_exception_on_fail': True,
    },
)
@pytest.mark.parametrize('is_drive_device', [True, False])
async def test_lb_producer_ok(
        taxi_signal_device_api, pgsql, testpoint, is_drive_device, stq,
):
    jwt_key = common.add_device_return_private_key(
        pgsql,
        1,
        device_id=DEVICE_ID,
        serial_number=SERIAL_NUMBER,
        is_drive_device=is_drive_device,
    )

    @testpoint('publish-times-called-check-testpoint')
    def publish_testpoint(arg):
        pass

    @testpoint('logbroker_publish')
    def logbroker_commit(data):
        pass

    new_event = {**EVENT, 'signalled': True}
    await send_status_ok(taxi_signal_device_api, pgsql, jwt_key)
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.make_jwt_headers(jwt_key, ENDPOINT, PARAMS, new_event),
        params=PARAMS,
        json=new_event,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'id': EVENT_ID}

    await publish_testpoint.wait_call()
    if is_drive_device:
        assert logbroker_commit.times_called == 1
    else:
        assert logbroker_commit.times_called == 0


def insert_boot(pgsql, boot_time):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        f"""
        INSERT INTO signal_device_api.events
        (
            device_id,
            created_at,
            updated_at,
            event_id,
            public_event_id,
            event_at,
            event_type,
            gnss_latitude,
            gnss_longitude,
            park_id
        )
        VALUES
        (
            1,
            '{boot_time}',
            '{boot_time}',
            '5exxx66e59637858xxx6d76c4322b394',
            '54b3d7ec-30f6-xxx6-94a8-afs6e8fe404c',
            '{boot_time}',
            'boot',
            54.99550072,
            72.94622044,
            'p1'
        )
    """,
    )


def insert_best_shot(pgsql, best_shot_time, event_id='test'):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        f"""
        INSERT INTO signal_device_api.events
        (
            device_id,
            created_at,
            updated_at,
            event_id,
            public_event_id,
            event_at,
            event_type,
            gnss_latitude,
            gnss_longitude,
            park_id
        )
        VALUES
        (
            1,
            '{best_shot_time}',
            '{best_shot_time}',
            '{event_id}',
            '{event_id}',
            '{best_shot_time}',
            'best_shot',
            54.99550072,
            72.94622044,
            'p1'
        )
    """,
    )
    db.execute(
        f"""
        INSERT INTO signal_device_api.statuses
        (
            id,
            cpu_temperature,
            disk_bytes_free_space,
            disk_bytes_total_space,
            root_bytes_free_space,
            root_bytes_total_space,
            ram_bytes_free_space,
            gps_position_lat,
            gps_position_lon,
            gnss_latitude,
            gnss_longitude,
            software_version,
            uptime_ms,
            sim_iccid,
            sim_phone_number,
            sim_imsi,
            status_at,
            created_at,
            updated_at,
            driver_detected,
            driver_detected_name,
            last_best_shot_at
        )
        VALUES
        (
            1,
            36,
            107374182,
            1073741824,
            107374183,
            1073741835,
            10737418,
            73.3242,
            54.9885,
            NULL,
            NULL,
            '2.31',
            90555,
            '89310410106543789301',
            '+7 (913) 617-82-58',
            '502130123456789',
            '{best_shot_time}',
            '2000-09-04T08:18:54',
            '{best_shot_time}',
            'test_driver',
            'test_driver_name',
            '{best_shot_time}'

        ) ON CONFLICT (id) DO UPDATE
            SET status_at = '{best_shot_time}',
            updated_at = '{best_shot_time}',
            last_best_shot_at = '{best_shot_time}';
        """,
    )


@pytest.mark.parametrize(
    'boot_time, best_shot_time, expected_driver_info',
    [
        (
            '2020-02-17T23:07:00+01:00',
            '2020-02-17T23:05:00+01:00',
            ('test_driver', 'test_driver_name'),
        ),
        (
            '2020-02-17T23:07:00+01:00',
            '2020-02-17T23:03:00+01:00',
            (None, None),
        ),
        (
            '2020-02-17T22:30:00+01:00',
            '2020-02-17T22:40:00+01:00',
            (None, None),
        ),
        (
            '2020-02-17T23:07:00+01:00',
            '2020-02-17T23:09:00+01:00',
            (None, None),
        ),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_bind_event_to_driver_best_shot(
        taxi_signal_device_api,
        pgsql,
        boot_time,
        best_shot_time,
        expected_driver_info,
):
    jwt_key = common.add_device_return_private_key(
        pgsql, 1, device_id=DEVICE_ID, serial_number=SERIAL_NUMBER,
    )
    insert_boot(pgsql, boot_time)
    insert_best_shot(pgsql, best_shot_time)
    new_event = {**EVENT}
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.make_jwt_headers(jwt_key, ENDPOINT, PARAMS, new_event),
        params=PARAMS,
        json=new_event,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'id': EVENT_ID}
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        """
        SELECT driver_profile_id, driver_name FROM signal_device_api.events
        WHERE device_id=1 AND event_type = 'custom_event_type'
        """,
    )
    assert list(db)[0] == expected_driver_info


@pytest.mark.parametrize(
    'best_shot_time, expected_driver_info',
    [
        (None, (None, None)),
        ('2020-02-17T23:07:20+01:00', ('test_driver', 'test_driver_name')),
        ('2020-02-17T23:08:20+01:00', (None, None)),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_unbind_event_at_boot(
        taxi_signal_device_api, pgsql, best_shot_time, expected_driver_info,
):
    jwt_key = common.add_device_return_private_key(
        pgsql, 1, device_id=DEVICE_ID, serial_number=SERIAL_NUMBER,
    )
    insert_boot(pgsql, '2020-02-17T23:00:00+01:00')
    insert_best_shot(pgsql, '2020-02-17T23:00:00+01:00')
    new_event = {**EVENT}
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.make_jwt_headers(jwt_key, ENDPOINT, PARAMS, new_event),
        params=PARAMS,
        json=new_event,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'id': EVENT_ID}
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        """
        SELECT driver_profile_id, driver_name FROM signal_device_api.events
        WHERE device_id=1 AND event_type = 'custom_event_type'
        """,
    )
    assert list(db)[0] == ('test_driver', 'test_driver_name')

    if best_shot_time is not None:
        insert_best_shot(pgsql, best_shot_time, 'test2')
    new_event = {**EVENT}
    new_event['at'] = '2020-02-17T23:09:00+01:00'
    new_event['id'] = 'event_id_test_boot'
    new_event['type'] = 'boot'
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.make_jwt_headers(jwt_key, ENDPOINT, PARAMS, new_event),
        params=PARAMS,
        json=new_event,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'id': 'event_id_test_boot'}
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        """
        SELECT driver_profile_id, driver_name FROM signal_device_api.events
        WHERE device_id=1 AND event_type = 'custom_event_type'
        """,
    )
    assert list(db)[0] == expected_driver_info


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_device_not_registered(taxi_signal_device_api):
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.MISSING_JWT_HEADER_FOR_UNREGISTERED,
        params=PARAMS,
        json=EVENT,
    )

    assert response.status_code == 400, response.text
    assert response.json() == common.response_400_not_registered(DEVICE_ID)


DRIVER_PROFILES_LIST_WITH_DRIVER = {
    'driver_profiles': [
        {
            'driver_profile': {
                'first_name': ' Petr ',
                'middle_name': ' D` ',
                'last_name': ' Ivanov ',
                'id': 'd1',
            },
        },
    ],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 300,
}


DRIVER_PROFILES_LIST_WITHOUT_DRIVER = {
    'driver_profiles': [],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 300,
}

DRIVER_PROFILES_LIST_MULTIPLE_DRIVERS = {
    'driver_profiles': [
        {
            'driver_profile': {
                'first_name': ' Petr ',
                'middle_name': ' D` ',
                'last_name': ' Ivanov ',
                'id': 'd1',
            },
        },
        {
            'driver_profile': {
                'first_name': ' Ivan ',
                'middle_name': ' X` ',
                'last_name': ' Petrov ',
                'id': 'd2',
            },
        },
    ],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 2,
    'limit': 300,
}

DRIVER_PROFILES_LIST_INACTIVE_DRIVERS = {
    'driver_profiles': [
        {
            'driver_profile': {
                'first_name': ' Petr ',
                'middle_name': ' D` ',
                'last_name': ' Ivanov ',
                'id': 'd1',
            },
        },
        {
            'driver_profile': {
                'first_name': ' Ivan ',
                'middle_name': ' X` ',
                'last_name': ' Petrov ',
                'id': 'd4',
            },
        },
    ],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 2,
    'limit': 300,
}


FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'data': {'car_id': 'car1', 'number': 'О122КХ777'},
            'park_id_car_id': 'p1_car1',
            'revision': '0_1574328384_71',
        },
    ],
}


EXPECTED_PARKS_REQUEST = {
    'fields': {'driver_profile': ['first_name', 'middle_name', 'last_name']},
    'limit': 100,
    'offset': 0,
    'query': {'park': {'car': {'id': ['car1']}, 'id': 'p1'}},
}

EXPECTED_FLEET_VEHICLES_REQUEST = {'id_in_set': ['p1_car1']}

DRIVER_STATUSES_ONE_ACTIVE = {
    'statuses': [
        {
            'park_id': 'p1',
            'driver_id': 'd1',
            'status': 'offline',
            'updated_ts': 12345,
        },
        {
            'park_id': 'p1',
            'driver_id': 'd2',
            'status': 'online',
            'updated_ts': 12345,
        },
    ],
}

DRIVER_STATUSES_NO_ACTIVE = {
    'statuses': [
        {
            'park_id': 'p1',
            'driver_id': 'd1',
            'status': 'offline',
            'updated_ts': 12345,
        },
        {
            'park_id': 'p1',
            'driver_id': 'd2',
            'status': 'offline',
            'updated_ts': 12345,
        },
    ],
}


@pytest.mark.config(SIGNAL_DEVICE_API_DRIVER_STATUS_RESOLUTION_ENABLED=True)
@pytest.mark.pgsql('signal_device_api_meta_db', ['car_binding.sql'])
@pytest.mark.parametrize(
    'device_pk_id, device_public_id, '
    'parks_response, fleet_vehicles_response, driver_statuses_response, '
    'expected_parks_request, expected_fleet_vehicles_request, '
    'expected_denormalized',
    [
        pytest.param(
            1,
            'has_driver',
            DRIVER_PROFILES_LIST_WITH_DRIVER,
            FLEET_VEHICLES_RESPONSE,
            DRIVER_STATUSES_ONE_ACTIVE,
            EXPECTED_PARKS_REQUEST,
            EXPECTED_FLEET_VEHICLES_REQUEST,
            {
                'park_id': 'p1',
                'car_id': 'car1',
                'car_device_binding_id': '2',
                'driver_profile_id': 'd1',
                'driver_name': 'Ivanov Petr D`',
                'vehicle_plate_number': 'О122КХ777',
            },
            id='has_driver',
        ),
        pytest.param(
            1,
            'has_car',
            DRIVER_PROFILES_LIST_WITHOUT_DRIVER,
            FLEET_VEHICLES_RESPONSE,
            DRIVER_STATUSES_ONE_ACTIVE,
            EXPECTED_PARKS_REQUEST,
            EXPECTED_FLEET_VEHICLES_REQUEST,
            {
                'park_id': 'p1',
                'car_id': 'car1',
                'car_device_binding_id': '2',
                'driver_profile_id': None,
                'driver_name': None,
                'vehicle_plate_number': 'О122КХ777',
            },
            id='without_driver',
        ),
        pytest.param(
            2,
            'has_no_car',
            None,
            None,
            DRIVER_STATUSES_ONE_ACTIVE,
            None,
            None,
            {
                'park_id': 'p1',
                'car_id': None,
                'car_device_binding_id': None,
                'driver_profile_id': None,
                'driver_name': None,
                'vehicle_plate_number': None,
            },
            id='has_driver',
        ),
        pytest.param(
            3,
            'inactive_camera',
            None,
            None,
            DRIVER_STATUSES_ONE_ACTIVE,
            None,
            None,
            {
                'park_id': None,
                'car_id': None,
                'car_device_binding_id': None,
                'driver_profile_id': None,
                'driver_name': None,
                'vehicle_plate_number': None,
            },
            id='inactive_camera',
        ),
        pytest.param(
            1,
            'has_driver',
            DRIVER_PROFILES_LIST_MULTIPLE_DRIVERS,
            FLEET_VEHICLES_RESPONSE,
            DRIVER_STATUSES_ONE_ACTIVE,
            EXPECTED_PARKS_REQUEST,
            EXPECTED_FLEET_VEHICLES_REQUEST,
            {
                'park_id': 'p1',
                'car_id': 'car1',
                'car_device_binding_id': '2',
                'driver_profile_id': 'd2',
                'driver_name': 'Petrov Ivan X`',
                'vehicle_plate_number': 'О122КХ777',
            },
            id='has_two_drivers',
        ),
        pytest.param(
            1,
            'has_car',
            DRIVER_PROFILES_LIST_MULTIPLE_DRIVERS,
            FLEET_VEHICLES_RESPONSE,
            DRIVER_STATUSES_NO_ACTIVE,
            EXPECTED_PARKS_REQUEST,
            EXPECTED_FLEET_VEHICLES_REQUEST,
            {
                'park_id': 'p1',
                'car_id': 'car1',
                'car_device_binding_id': '2',
                'driver_profile_id': None,
                'driver_name': None,
                'vehicle_plate_number': 'О122КХ777',
            },
            id='without_active_drivers',
        ),
    ],
)
async def test_binding(
        taxi_signal_device_api,
        pgsql,
        mockserver,
        fleet_vehicles,
        parks,
        device_pk_id,
        device_public_id,
        parks_response,
        fleet_vehicles_response,
        driver_statuses_response,
        expected_parks_request,
        expected_fleet_vehicles_request,
        expected_denormalized,
):
    if fleet_vehicles_response:
        fleet_vehicles.set_fleet_vehicles_response(fleet_vehicles_response)
    if parks_response:
        parks.set_parks_response(parks_response)

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _mock_driver_statuses(request):
        return driver_statuses_response

    jwt_key = common.add_device_return_private_key(
        pgsql, device_pk_id, device_public_id,
    )
    params = {
        'device_id': device_public_id,
        'timestamp': '2020-02-17T23:09:00Z',
    }

    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.make_jwt_headers(jwt_key, ENDPOINT, params, EVENT),
        params=params,
        json=EVENT,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'id': EVENT_ID}

    if expected_fleet_vehicles_request:
        assert fleet_vehicles.fleet_vehicles.times_called == 1
        fleet_vehicles_request = fleet_vehicles.fleet_vehicles.next_call()[
            'request'
        ].json
        assert fleet_vehicles_request == expected_fleet_vehicles_request
    else:
        assert fleet_vehicles.fleet_vehicles.times_called == 0

    if expected_parks_request:
        assert parks.parks.times_called == 1
        parks_request = parks.parks.next_call()['request'].json
        assert parks_request == expected_parks_request
    else:
        assert parks.parks.times_called == 0

    db_events = select_events(pgsql, device_pk_id)
    assert len(db_events) == 1, db_events

    db_event = db_events[0]
    assert db_event['device_id'] == device_pk_id
    assert db_event['event_id'] == EVENT_ID
    assert db_event['event_at'] == dateutil.parser.parse(EVENT['at'])
    assert db_event['event_type'] == EVENT['type']
    assert db_event['video_file_id'] == EVENT['video_file_id']
    assert db_event['photo_file_id'] == EVENT['photo_file_id']
    assert db_event['extra'] == EVENT['extra']

    common.assert_now(db_event['created_at'])
    common.assert_now(db_event['updated_at'])
    assert_equals(db_event['gnss_latitude'], GNSS['lat'])
    assert_equals(db_event['gnss_speed_kmph'], GNSS['speed_kmph'])
    assert_equals(db_event['gnss_longitude'], GNSS['lon'])
    assert_equals(db_event['gnss_accuracy_m'], GNSS['accuracy_m'])
    assert_equals(db_event['gnss_direction_deg'], GNSS['direction_deg'])

    denormalized_part = {
        k: v for k, v in db_event.items() if k in expected_denormalized
    }
    assert denormalized_part == expected_denormalized


@pytest.mark.config(
    SIGNAL_DEVICE_API_DRIVER_VIOLATION_TAG_SETTINGS_V2={
        'always': {
            'violations_time': 2147483647,
            'violation_tag': 'driver_with_signalq_rules_violation',
            'violation_tag_ttl': 10800,
            'violations_count': 2,
            'violations': ['custom_event_type'],
        },
        'night': {
            'violations_time': 2147483647,
            'violation_tag': 'driver_with_signalq_rules_violation_night',
            'violation_tag_ttl': 3600,
            'violations_count': 2,
            'violations': ['custom_event_type'],
        },
    },
)
@pytest.mark.pgsql('signal_device_api_meta_db', ['car_binding.sql'])
@pytest.mark.parametrize('violated', [True, False])
async def test_driver_tags(
        taxi_signal_device_api,
        violated,
        pgsql,
        stq,
        stq_runner,
        fleet_vehicles,
        parks,
        mockserver,
):
    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        assert 'remove' not in request.json
        assert append['entity_type'] == 'dbid_uuid'
        assert len(append['tags']) == 2
        assert append['tags'] == [
            {
                'name': 'driver_with_signalq_rules_violation_night',
                'entity': 'p1_d1',
                'ttl': 3600,
            },
            {
                'name': 'driver_with_signalq_rules_violation',
                'entity': 'p1_d1',
                'ttl': 10800,
            },
        ]
        return {}

    fleet_vehicles.set_fleet_vehicles_response(FLEET_VEHICLES_RESPONSE)
    parks.set_parks_response(DRIVER_PROFILES_LIST_WITH_DRIVER)

    jwt_key = common.add_device_return_private_key(pgsql, 1, DEVICE_ID)

    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.make_jwt_headers(jwt_key, ENDPOINT, PARAMS, EVENT),
        params=PARAMS,
        json=EVENT,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'id': EVENT_ID}

    if not violated:
        assert stq.signal_device_api_tags.times_called == 0
        return

    new_event = {**EVENT, 'id': 'some_new_id'}
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.make_jwt_headers(jwt_key, ENDPOINT, PARAMS, new_event),
        params=PARAMS,
        json=new_event,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'id': 'some_new_id'}

    assert stq.signal_device_api_tags.times_called == 1
    tags_call = stq.signal_device_api_tags.next_call()
    await stq_runner.signal_device_api_tags.call(
        task_id=tags_call['id'],
        args=tags_call['args'],
        kwargs=tags_call['kwargs'],
    )
    assert _tags.times_called == 1


PRIVATE_KEY_FOR_TEST = (
    b'-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIOq/qJSRdhq9NE5rrf8VI0raTbd14IFd'
    b'cXFNADfELguUoAoGCCqGSM49\n'
    b'AwEHoUQDQgAEJdQTDj8OBfNV/+PVW2sQ/AcOX3bAPJU+PgROBTZFloOOrBB7jvKO\n'
    b'g+xM1iPHeaPjGO+r8xrrTrbA4FqxgopVFQ==\n-----END EC PRIVATE KEY-----\n'
)


@pytest.mark.config(
    SIGNAL_DEVICE_API_BEST_SHOT_PROCESSING_V3={
        'enabled': True,
        'max_etalon_similarity': 0.8,
        'min_etalon_similarity': 0.4,
        'stq_reschedule_delay_ms': 500,
        'best_shot_uploaded_max_interval_hours': 120,
        'max_reschedule_counter': 60,
    },
)
@pytest.mark.pgsql('signal_device_api_meta_db', ['best_shot_data.sql'])
@pytest.mark.parametrize(
    'is_anonymous, is_uploaded, is_gray_zone',
    [
        (True, True, False),
        (False, True, False),
        (True, False, False),
        (True, True, True),
    ],
)
async def test_best_shot(
        taxi_signal_device_api,
        testpoint,
        pgsql,
        stq,
        stq_runner,
        fleet_vehicles,
        parks,
        mockserver,
        is_anonymous,
        is_uploaded,
        is_gray_zone,
):
    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profiles/identify',
    )
    def _etalons(request):
        profile_type = 'park_driver_profile_id'
        if is_anonymous:
            profile_type = 'anonymous'
        similarity = 0.95
        if is_gray_zone:
            similarity = 0.6
        return {
            'etalons_profiles': [
                {
                    'etalon': {'id': 'xxx', 'version': 1},
                    'similarity': similarity,
                    'profiles': [
                        {
                            'provider': 'signalq',
                            'profile_meta': {
                                'park_id': 'p1',
                                'device_serial': 'd1',
                                'car_id': 'c1',
                            },
                            'profile': {'id': 'p1_123', 'type': profile_type},
                        },
                    ],
                },
                {
                    'etalon': {'id': 'yyy', 'version': 2},
                    'similarity': similarity - 0.02,
                    'profiles': [
                        {
                            'provider': 'signalq',
                            'profile_meta': {
                                'park_id': 'p1',
                                'device_serial': 'd2',
                                'car_id': 'c2',
                            },
                            'profile': {'id': 'p1_124', 'type': profile_type},
                        },
                    ],
                },
            ],
        }

    @testpoint('get_gray_zone_log')
    def get_gray_zone_log(data):
        return data

    await taxi_signal_device_api.enable_testpoints()

    fleet_vehicles.set_fleet_vehicles_response(FLEET_VEHICLES_RESPONSE)
    if is_gray_zone:
        parks.set_parks_response(DRIVER_PROFILES_LIST_WITHOUT_DRIVER)
    else:
        parks.set_parks_response(DRIVER_PROFILES_LIST_WITH_DRIVER)

    jwt_key = ecdsa.SigningKey.from_pem(
        PRIVATE_KEY_FOR_TEST, hashfunc=hashlib.sha256,
    )
    best_shot = {**EVENT, 'type': 'best_shot'}
    common.add_photo(
        pgsql,
        2,
        best_shot['photo_file_id'],
        228,
        '2019-04-19T13:40:32Z',
        is_uploaded,
        '2019-04-19T13:40:32Z',
    )

    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.make_jwt_headers(
            jwt_key,
            ENDPOINT,
            {**PARAMS, 'device_id': 'device_id_test2'},
            best_shot,
        ),
        params={**PARAMS, 'device_id': 'device_id_test2'},
        json=best_shot,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'id': EVENT_ID}

    assert stq.signal_device_api_best_shots.times_called == 1
    best_shot_call = stq.signal_device_api_best_shots.next_call()
    await stq_runner.signal_device_api_best_shots.call(
        task_id=best_shot_call['id'],
        args=best_shot_call['args'],
        kwargs=best_shot_call['kwargs'],
    )

    if not is_uploaded:
        assert _etalons.times_called == 0
        return

    assert _etalons.times_called == 1

    if is_gray_zone:
        expected_log = (
            'Photo /77fdc498f9174eba9722aff77cdb0a38/mnt/sd/signalq'
            '/0000000000000000/2019-12-23T13-19-44Z.jpeg with '
            's3_photo_path: some_path is in the gray zone. The most similar '
            'profile\'s id: p1_123, provider: signalq, similarity: 0.6'
        )
        log = await get_gray_zone_log.wait_call()
        assert log['data'] == {'message': expected_log}
    cursor = pgsql['signal_device_api_meta_db'].cursor()
    cursor.execute(
        'SELECT driver_detected, driver_detected_name '
        'FROM signal_device_api.statuses '
        'WHERE id=2',
    )

    if is_gray_zone:
        driver_id = None
        driver_name = None
    elif is_anonymous:
        driver_id = 'anonymous_p1_123'
        driver_name = None
    else:
        driver_id = '123'
        driver_name = 'Ivanov Petr D`'

    result = list(row for row in cursor)
    assert result[0] == (driver_id, driver_name)

    cursor.execute(
        'SELECT driver_profile_id, driver_name '
        'FROM signal_device_api.events '
        'ORDER BY event_id DESC',
    )
    result = list(row for row in cursor)

    # Too old event
    assert result[-1] == (None, None)
    result.pop()
    for driver_info in result:
        assert driver_info == (driver_id, driver_name)

    cursor.close()


WHITELIST = [
    {
        'event_type': 'seatbelt',
        'is_critical': True,
        'is_violation': False,
        'fixation_config_path': 'some_path',
    },
]


@pytest.mark.config(
    SIGNAL_DEVICE_API_EVENTS_NOTIFICATIONS={'enabled': True},
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=WHITELIST,
)
@pytest.mark.pgsql('signal_device_api_meta_db', ['best_shot_data.sql'])
async def test_notifications(
        taxi_signal_device_api,
        pgsql,
        stq,
        stq_runner,
        fleet_vehicles,
        parks,
        mockserver,
):
    @mockserver.json_handler(FLEET_NOTIFICATIONS_ENDPOINT)
    def _notify_via_tg(request):
        user_ids = request.json['destinations']
        assert {'park_id': 'p1', 'user_id': 'user1'} in user_ids
        assert {'park_id': 'p1', 'user_id': 'superuser'} in user_ids
        assert len(user_ids) == 2
        return {}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    'city_id': 'CITY_ID',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': 'p1',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'LOGIN',
                    'name': 'NAME',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    fleet_vehicles.set_fleet_vehicles_response(FLEET_VEHICLES_RESPONSE)
    parks.set_parks_response(DRIVER_PROFILES_LIST_WITH_DRIVER)

    jwt_key = ecdsa.SigningKey.from_pem(
        PRIVATE_KEY_FOR_TEST, hashfunc=hashlib.sha256,
    )
    crit_event = {**EVENT, 'type': 'seatbelt'}

    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.make_jwt_headers(
            jwt_key,
            ENDPOINT,
            {**PARAMS, 'device_id': 'device_id_test2'},
            crit_event,
        ),
        params={**PARAMS, 'device_id': 'device_id_test2'},
        json=crit_event,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'id': EVENT_ID}

    assert stq.signal_device_api_events_notifications.times_called == 1
    notifications_call = stq.signal_device_api_events_notifications.next_call()

    assert notifications_call['kwargs']['event_notifications_request'] == {
        'car_number': 'О122КХ777',
        'driver_name': 'Ivanov Petr D`',
        'event_type': 'seatbelt',
        'park_id': 'p1',
        'serial_number': '5987958976',
    }

    await stq_runner.signal_device_api_events_notifications.call(
        task_id=notifications_call['id'],
        args=notifications_call['args'],
        kwargs=notifications_call['kwargs'],
    )


@pytest.mark.config(SIGNAL_DEVICE_API_EVENTS_NOTIFICATIONS={'enabled': True})
@pytest.mark.pgsql(
    'signal_device_api_meta_db', ['best_shot_data_no_notifications.sql'],
)
async def test_notifications_disabled(
        taxi_signal_device_api,
        pgsql,
        stq,
        stq_runner,
        fleet_vehicles,
        parks,
        mockserver,
):
    @mockserver.json_handler(FLEET_NOTIFICATIONS_ENDPOINT)
    def _notify_via_tg(request):
        return {}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    'city_id': 'CITY_ID',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': 'p1',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'LOGIN',
                    'name': 'NAME',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    fleet_vehicles.set_fleet_vehicles_response(FLEET_VEHICLES_RESPONSE)
    parks.set_parks_response(DRIVER_PROFILES_LIST_WITH_DRIVER)

    jwt_key = ecdsa.SigningKey.from_pem(
        PRIVATE_KEY_FOR_TEST, hashfunc=hashlib.sha256,
    )
    crit_event = {**EVENT, 'type': 'seatbelt'}

    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.make_jwt_headers(
            jwt_key,
            ENDPOINT,
            {**PARAMS, 'device_id': 'device_id_test2'},
            crit_event,
        ),
        params={**PARAMS, 'device_id': 'device_id_test2'},
        json=crit_event,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'id': EVENT_ID}

    assert stq.signal_device_api_events_notifications.times_called == 0
