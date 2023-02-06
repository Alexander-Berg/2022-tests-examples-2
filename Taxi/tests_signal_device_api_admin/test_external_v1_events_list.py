import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'external/signal-device-api-admin/v1/events/list'

DRIVER_PROFILE1 = {
    'driver_profile': {
        'first_name': 'Petr',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723306794',
            'number': '7723306794',
        },
        'id': 'd1',
        'phones': ['+79265975310'],
    },
}

DRIVER_PROFILE2 = {
    'driver_profile': {
        'first_name': 'Petr',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723306794',
            'number': '7723306794',
        },
        'id': 'd2',
        'phones': ['+79265975310'],
    },
}

DRIVER_PROFILES_RESPONSE1 = {
    'driver_profiles': [DRIVER_PROFILE1],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 1,
}

DRIVER_PROFILES_RESPONSE2 = {
    'driver_profiles': [DRIVER_PROFILE1, DRIVER_PROFILE2],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 2,
    'limit': 2,
}

FLEET_VEHICLES_RESPONSE1 = {
    'vehicles': [
        {
            'data': {
                'car_id': 'c1',
                'number': 'K444AB55',
                'brand': 'lol',
                'model': 'kek',
            },
            'park_id_car_id': 'p1_c1',
            'revision': '0_1574328384_71',
        },
    ],
}

FLEET_VEHICLES_RESPONSE2 = {
    'vehicles': [
        {
            'data': {
                'car_id': 'c1',
                'number': 'K444AB55',
                'brand': 'lol',
                'model': 'kek',
            },
            'park_id_car_id': 'p1_c1',
            'revision': '0_1574328384_71',
        },
        {
            'data': {
                'car_id': 'c2',
                'number': 'K444AB55',
                'brand': 'lol',
                'model': 'kek',
            },
            'park_id_car_id': 'p1_c2',
            'revision': '0_1574328384_71',
        },
    ],
}


@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.config(TVM_ENABLED=True)
async def test_events_list_pagination(
        taxi_signal_device_api_admin, mockserver,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request, test_number=[0]):  # pylint: disable=W0102
        answers = [
            DRIVER_PROFILES_RESPONSE1,
            DRIVER_PROFILES_RESPONSE2,
            DRIVER_PROFILES_RESPONSE2,
        ]
        test_number[0] += 1
        return answers[test_number[0] - 1]

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_fleet_vehicles(
            request, test_number=[0],
    ):  # pylint: disable=W0102
        answers = [
            FLEET_VEHICLES_RESPONSE1,
            FLEET_VEHICLES_RESPONSE1,
            FLEET_VEHICLES_RESPONSE2,
        ]
        test_number[0] += 1
        return answers[test_number[0] - 1]

    response1 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 1},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response1.status_code == 200, response1.text

    resp = response1.json()
    assert resp['cursor'] == utils.get_encoded_events_cursor(
        '2020-02-27T13:02:00+00:00', '4f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )
    assert len(resp['events']) == 1
    event = resp['events'][0]
    assert event['id'] == '4f5a516f-29ff-4ebe-93eb-465bf0124e85'
    assert event['type'] == 'driver_lost'
    assert event['resolution'] == 'wrong_driver'

    response2 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 4, 'cursor': resp['cursor']},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response2.status_code == 200, response2.text
    resp = response2.json()
    assert len(resp['events']) == 4
    assert resp['cursor'] == utils.get_encoded_events_cursor(
        '2020-02-27T11:05:00+00:00', '6f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )

    response3 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'cursor': resp['cursor']},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response3.status_code == 200, response3.text
    resp = response3.json()
    assert len(resp['events']) == 2
    assert 'cursor' not in resp
    assert resp['events'][-1]['event_at'] == '2020-02-26T23:55:00+00:00'


EXPECTED_EVENT_SHORT_FORM1 = {
    'event_at': '2020-02-27T12:00:00+00:00',
    'id': '9f5a516f-29ff-4ebe-93eb-465bf0124e85',
    'type': 'sleep',
    'vehicle': {
        'id': 'c1',
        'plate_number': 'K444AB55',
        'brand': 'lol',
        'model': 'kek',
    },
}

EXPECTED_EVENT_SHORT_FORM2 = {
    'event_at': '2020-02-27T12:00:00+00:00',
    'id': '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
    'type': 'sleep',
    'vehicle': {
        'id': 'c1',
        'plate_number': 'K444AB55',
        'brand': 'lol',
        'model': 'kek',
    },
    'driver': {
        'first_name': 'Petr',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'id': 'd2',
        'license_number': '7723306794',
        'phones': ['+79265975310'],
    },
}

EXPECTED_EVENT_SHORT_FORM3 = {
    'event_at': '2020-02-27T11:02:00+00:00',
    'id': '5f5a516f-29ff-4ebe-93eb-465bf0124e85',
    'type': 'driver_lost',
    'vehicle': {
        'id': 'c1',
        'plate_number': 'K444AB55',
        'brand': 'lol',
        'model': 'kek',
    },
    'driver': {
        'first_name': 'Petr',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'id': 'd1',
        'license_number': '7723306794',
        'phones': ['+79265975310'],
    },
}

EXPECTED_EVENTS1 = [
    EXPECTED_EVENT_SHORT_FORM1,
    EXPECTED_EVENT_SHORT_FORM2,
    EXPECTED_EVENT_SHORT_FORM3,
]


@pytest.mark.parametrize(
    'period, serial_ids_filter, expected_code, expected_events',
    [
        (
            {
                'from': '2021-04-10T00:00:00+03:00',
                'to': '2020-04-10T00:00:00+03:00',
            },
            None,
            400,
            None,
        ),
        (
            {'from': '2020-02-27T00:00:00+00', 'to': '2020-02-27T13:00:00+00'},
            {'serial_numbers': ['AB2', 'AB3', 'AB1337']},
            200,
            EXPECTED_EVENTS1,
        ),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.config(TVM_ENABLED=True)
async def test_events_list_period_with_filter(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        parks,
        period,
        serial_ids_filter,
        expected_code,
        expected_events,
):

    fleet_vehicles.set_fleet_vehicles_response(FLEET_VEHICLES_RESPONSE2)
    parks.set_driver_profiles_response(DRIVER_PROFILES_RESPONSE2)

    request_body = {}
    if period:
        request_body['period'] = period
    if serial_ids_filter:
        request_body['filter'] = serial_ids_filter
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=request_body,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == expected_code, response.text
    if expected_code == 400:
        return
    response_json = response.json()
    response_events = response_json['events']
    assert len(response_events) == len(expected_events)
    for event, expected_event in zip(response_events, expected_events):
        assert (
            event['event_at'] == expected_event['event_at']
            and event['id'] == expected_event['id']
            and event['type'] == expected_event['type']
        )
        if 'driver' in event:
            assert event['driver'] == expected_event['driver']
        if 'vehicle' in event:
            assert event['vehicle'] == expected_event['vehicle']
