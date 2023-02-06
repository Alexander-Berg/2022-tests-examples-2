import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = '/fleet/signal-device-api-admin/v1/events/feed'

DRIVER_STATUS_V2_RESPONSE1 = {
    'statuses': [
        {
            'park_id': 'p1',
            'driver_id': 'd1',
            'status': 'online',
            'updated_ts': 12345,
        },
        {
            'park_id': 'p1',
            'driver_id': 'd2',
            'status': 'busy',
            'updated_ts': 12345,
        },
    ],
}

DRIVER_STATUS_V2_RESPONSE2 = {
    'statuses': [
        {
            'park_id': 'p1',
            'driver_id': 'd2',
            'status': 'busy',
            'updated_ts': 12345,
            'orders': [{'id': 'x', 'status': 'driving'}],
        },
    ],
}

FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'data': {'car_id': 'car_0', 'number': 'О122КХ777'},
            'park_id_car_id': 'p1_car_0',
            'revision': '0_1574328384_71',
        },
    ],
}

EMPTY_FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'data': None,
            'park_id_car_id': 'p1_car_0',
            'revision': '0_1574328384_71',
        },
    ],
}


@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
async def test_ok_feed(taxi_signal_device_api_admin, mockserver):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return DRIVER_STATUS_V2_RESPONSE1

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks(request):
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
                    'specifications': ['taxi', 'signalq'],
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_fleet_vehicles(request):
        if 'p1_car_0' in request.json['id_in_set']:
            return FLEET_VEHICLES_RESPONSE
        return EMPTY_FLEET_VEHICLES_RESPONSE

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 2, 'park_id': 'p1'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'cursor': utils.get_encoded_events_cursor(
            '2020-02-27T12:00:00+00:00',
            '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
        ),
        'items': [
            {
                'device': {
                    'id': 'd58e753c44e548ce9edaec0e0ef9c8c1',
                    'is_online': False,
                    'serial_number': 'AB2',
                },
                'event': {
                    'event_at': '2020-10-01T12:00:00+00:00',
                    'id': '123a516f-29ff-4ebe-93eb-465bf0124e69',
                    'type': 'sleep',
                    'is_seen': False,
                    'is_critical': False,
                },
                'thread_id': (
                    utils.to_base64(
                        '||d58e753c44e548ce9edaec0e0ef9c8c1',
                    ).rstrip('=')
                ),
            },
            {
                'device': {
                    'id': 'd58e753c44e548ce9edaec0e0ef9c8c1',
                    'is_online': False,
                    'serial_number': 'AB2',
                },
                'work_status': 'busy',
                'event': {
                    'event_at': '2020-02-27T12:00:00+00:00',
                    'id': '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
                    'type': 'sleep',
                    'is_seen': False,
                    'is_critical': False,
                },
                'vehicle': {'plate_number': 'K123KK777'},
                'thread_id': (
                    utils.to_base64(
                        '|c1|d58e753c44e548ce9edaec0e0ef9c8c1',
                    ).rstrip('=')
                ),
            },
        ],
    }

    response2 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 2,
            'park_id': 'p1',
            'cursor': utils.get_encoded_events_cursor(
                '2020-02-27T12:00:00+00:00',
                '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
            ),
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response2.status_code == 200, response.text
    assert response2.json() == {
        'cursor': utils.get_encoded_events_cursor(
            '2020-01-02T12:00:00+00:00',
            '123a516f-29ff-4ebe-93eb-465bf0124e87',
        ),
        'items': [
            {
                'device': {
                    'id': 'd58e753c44e548ce9edaec0e0ef9c8c3',
                    'is_online': False,
                    'serial_number': 'AB3',
                },
                'event': {
                    'event_at': '2020-01-02T12:00:00+00:00',
                    'id': '123a516f-29ff-4ebe-93eb-465bf0124e87',
                    'type': 'sleep',
                    'is_seen': False,
                    'is_critical': False,
                },
                'thread_id': utils.to_base64(
                    '||d58e753c44e548ce9edaec0e0ef9c8c3',
                ).rstrip('='),
            },
        ],
    }

    response3 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 2,
            'park_id': 'p1',
            'cursor': utils.get_encoded_events_cursor(
                '2020-01-02T12:00:00+00:00',
                '123a516f-29ff-4ebe-93eb-465bf0124e87',
            ),
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response3.status_code == 200, response.text
    assert response3.json() == {
        'cursor': utils.get_encoded_events_cursor(
            '2020-01-02T12:00:00+00:00',
            '123a516f-29ff-4ebe-93eb-465bf0124e87',
        ).rstrip('='),
        'items': [],
    }


@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
async def test_ok_feed_group_by_driver(
        taxi_signal_device_api_admin, mockserver,
):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return DRIVER_STATUS_V2_RESPONSE1

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks(request):
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
                    'specifications': ['taxi', 'signalq'],
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 1, 'group_by': 'driver_profile_id'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'cursor': utils.get_encoded_events_cursor(
            '2020-02-27T13:02:00+00:00',
            '4f5a516f-29ff-4ebe-93eb-465bf0124e85',
        ),
        'items': [
            {
                'device': {
                    'id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
                    'is_online': True,
                    'serial_number': 'AB1',
                },
                'work_status': 'online',
                'event': {
                    'event_at': '2020-02-27T13:02:00+00:00',
                    'id': '4f5a516f-29ff-4ebe-93eb-465bf0124e85',
                    'type': 'driver_lost',
                    'is_seen': False,
                    'is_critical': False,
                },
                'vehicle': {'plate_number': 'K444AB55'},
                'driver': {
                    'driver_name': 'Иванов Петр',
                    'driver_profile_id': 'd1',
                },
                'thread_id': (
                    utils.to_base64(
                        'd1||e58e753c44e548ce9edaec0e0ef9c8c1',
                    ).rstrip('=')
                ),
            },
        ],
    }

    response2 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 1,
            'group_by': 'driver_profile_id',
            'cursor': utils.get_encoded_events_cursor(
                '2020-02-27T13:02:00+00:00',
                '4f5a516f-29ff-4ebe-93eb-465bf0124e85',
            ),
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response2.status_code == 200, response.text
    assert response2.json() == {
        'cursor': utils.get_encoded_events_cursor(
            '2020-02-27T12:00:00+00:00',
            '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
        ),
        'items': [
            {
                'device': {
                    'id': 'd58e753c44e548ce9edaec0e0ef9c8c1',
                    'is_online': False,
                    'serial_number': 'AB2',
                },
                'driver': {
                    'driver_name': 'Петров Иван',
                    'driver_profile_id': 'd2',
                },
                'work_status': 'busy',
                'event': {
                    'event_at': '2020-02-27T12:00:00+00:00',
                    'id': '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
                    'type': 'sleep',
                    'is_seen': False,
                    'is_critical': False,
                },
                'vehicle': {'plate_number': 'K123KK777'},
                'thread_id': utils.to_base64(
                    'd2||d58e753c44e548ce9edaec0e0ef9c8c1',
                ).rstrip('='),
            },
        ],
    }

    response3 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 2,
            'group_by': 'driver_profile_id',
            'cursor': utils.get_encoded_events_cursor(
                '2020-02-27T12:00:00+00:00',
                '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
            ),
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response3.status_code == 200, response.text
    assert response3.json() == {
        'cursor': utils.get_encoded_events_cursor(
            '2020-02-27T12:00:00+00:00',
            '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
        ).rstrip('='),
        'items': [],
    }


@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=[
        {
            'event_type': 'sleep',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'distraction',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'driver_lost',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'tired',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.parametrize(
    'event_types, are_items_empty, period, match_text, expected_code',
    [
        (None, False, None, None, 200),
        (
            ['sleep', 'driver_lost'],
            False,
            {
                'from': '2021-04-10T00:00:00+03:00',
                'to': '2020-04-10T00:00:00+03:00',
            },
            'Петров',
            400,
        ),
        (
            ['tired', 'driver_lost'],
            True,
            {
                'from': '2020-02-27T11:06:00+03:00',
                'to': '2020-04-10T00:00:00+03:00',
            },
            'Петров',
            200,
        ),
    ],
)
async def test_feed_filtered_no_work_status(
        taxi_signal_device_api_admin,
        mockserver,
        event_types,
        are_items_empty,
        period,
        match_text,
        expected_code,
):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return DRIVER_STATUS_V2_RESPONSE2

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks(request):
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
                    'specifications': ['signalq'],
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    body = {
        'limit': 2,
        'park_id': 'p1',
        'period': period,
        'filter': {'match_text': match_text},
    }
    if event_types:
        body['filter']['event_types'] = event_types

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=body,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == expected_code, response.text
    if response.status_code != 200:
        return

    if are_items_empty:
        assert response.json() == {'cursor': '', 'items': []}
        return

    assert response.json() == {
        'cursor': utils.get_encoded_events_cursor(
            '2020-02-27T12:00:00+00:00',
            '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
        ),
        'items': [
            {
                'device': {
                    'id': 'd58e753c44e548ce9edaec0e0ef9c8c1',
                    'is_online': False,
                    'serial_number': 'AB2',
                },
                'event': {
                    'event_at': '2020-10-01T12:00:00+00:00',
                    'id': '123a516f-29ff-4ebe-93eb-465bf0124e69',
                    'type': 'sleep',
                    'is_seen': False,
                    'is_critical': False,
                },
                'thread_id': (
                    utils.to_base64(
                        '||d58e753c44e548ce9edaec0e0ef9c8c1',
                    ).rstrip('=')
                ),
            },
            {
                'device': {
                    'id': 'd58e753c44e548ce9edaec0e0ef9c8c1',
                    'is_online': False,
                    'serial_number': 'AB2',
                },
                'event': {
                    'event_at': '2020-02-27T12:00:00+00:00',
                    'id': '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
                    'type': 'sleep',
                    'is_seen': False,
                    'is_critical': False,
                },
                'vehicle': {'plate_number': 'K123KK777'},
                'thread_id': (
                    utils.to_base64(
                        '|c1|d58e753c44e548ce9edaec0e0ef9c8c1',
                    ).rstrip('=')
                ),
            },
        ],
    }


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': web_common.DEMO_DEVICES,
        'events': web_common.DEMO_EVENTS,
        'vehicles': web_common.DEMO_VEHICLES,
        'groups': web_common.DEMO_GROUPS,
        'drivers': web_common.DEMO_DRIVERS,
    },
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=web_common.get_demo_whitelist(  # noqa: E501 line too long
        ['tired', 'seatbelt'],
    ),
)
@pytest.mark.parametrize(
    'text, event_types, group_id, group_by,' 'expected_code, expected_events',
    [
        (
            'Rom',
            ['tired', 'ushel v edu', 'seatbelt', 'brosil signalq'],
            None,
            None,
            200,
            [web_common.DEMO_EVENTS[1]],
        ),
        (
            None,
            [
                'brosil signalq',
                'ushel v edu',
                'sleep',
                'tired',
                'kak teper zhit',
            ],
            'g1',
            'driver_profile_id',
            200,
            [web_common.DEMO_EVENTS[5]],
        ),
    ],
)
async def test_demo_events_feed(
        taxi_signal_device_api_admin,
        text,
        event_types,
        group_id,
        group_by,
        expected_code,
        expected_events,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('no such park'),
                    'specifications': ['taxi'],
                },
            ],
        }

    filter_ = {}
    if event_types:
        filter_['event_types'] = event_types
    if group_id:
        filter_['group_id'] = group_id
    if text:
        filter_['match_text'] = text

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 2, 'filter': filter_, 'group_by': group_by},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == expected_code, response.text

    response_json = response.json()
    response_events = response_json['items']
    assert len(response_events) == len(expected_events)
    for event, expected_event in zip(response_events, expected_events):
        assert (
            event['event']['id'] == expected_event['id']
            and event['event']['type'] == expected_event['event_type']
        )
