import typing

import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'external/signal-device-api-admin/v1/events/retrieve'

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

DRIVER_PROFILES_RESPONSE = {
    'driver_profiles': [DRIVER_PROFILE1, DRIVER_PROFILE2],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 2,
    'limit': 2,
}

FLEET_VEHICLES_RESPONSE = {
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
    'photo': {'is_media_uploaded': False},
    'video': {'is_media_uploaded': True},
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

EXPECTED_EVENTS = [
    EXPECTED_EVENT_SHORT_FORM1,
    EXPECTED_EVENT_SHORT_FORM2,
    EXPECTED_EVENT_SHORT_FORM3,
]

NO_EVENTS: typing.List[typing.Dict] = []


@pytest.mark.parametrize(
    'event_ids, expected_events',
    [
        (
            [
                '9f5a516f-29ff-4ebe-93eb-465bf0124e85',
                '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
                '5f5a516f-29ff-4ebe-93eb-465bf0124e85',
                'lol',
            ],
            EXPECTED_EVENTS,
        ),
        (
            ['kek', 'cheburek', '10f5a516f-29ff-4ebe-93eb-465bf0124e85'],
            NO_EVENTS,
        ),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.config(TVM_ENABLED=True)
async def test_events_retrieve(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        parks,
        event_ids,
        expected_events,
):

    fleet_vehicles.set_fleet_vehicles_response(FLEET_VEHICLES_RESPONSE)
    parks.set_driver_profiles_response(DRIVER_PROFILES_RESPONSE)

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'event_ids': event_ids},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
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
        if 'photo' in event:
            assert (
                event['photo']['is_media_uploaded']
                == expected_event['photo']['is_media_uploaded']
            )
        if 'video' in event:
            assert (
                event['video']['is_media_uploaded']
                == expected_event['video']['is_media_uploaded']
            )
