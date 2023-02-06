import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v2/events/list'

GNSS_1 = {
    'lat': 54.99250000,
    'lon': 73.36861111,
    'speed_kmph': 34.437895,
    'accuracy_m': 0.61340,
    'direction_deg': 245.895,
}
EVENT_1 = {
    'device_id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
    'device_serial_number': 'AB1',
    'id': '34b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    'event_uploaded_at': '2020-02-27T13:00:00+00:00',
    'event_at': '2020-02-27T12:00:00+00:00',
    'type': 'sleep',
    'gnss': GNSS_1,
    'vehicle': {'plate_number': 'K444AB55', 'id': 'c1'},
    'resolution': 'hide',
}

EVENT_2 = {
    'device_id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
    'device_serial_number': 'AB1',
    'id': '1233d7ec-30f6-43cf-94a8-11dbv8ae404c',
    'event_uploaded_at': '2020-02-27T13:00:00+00:00',
    'event_at': '2020-02-27T12:10:00+00:00',
    'type': 'sleep',
    'gnss': GNSS_1,
    'vehicle': {'plate_number': 'K444AB55', 'id': 'c1'},
}

GNSS_2 = {  # we check this one for photo
    'lat': 54.99550072,
    'lon': 72.94622044,
}
EVENT_3 = {
    'device_id': '4306de3dfd82406d81ea3c098c80e9ba',
    'device_serial_number': 'AB12FE45DD',
    'id': '54b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    'event_uploaded_at': '2020-02-27T23:55:00+00:00',
    'event_at': '2020-02-26T23:55:00+00:00',
    'type': 'sleep',
    'gnss': GNSS_2,
    'vehicle': {'plate_number': 'K123KK777', 'id': 'c2'},
}

EVENT_4 = {
    'device_id': '4306de3dfd82406d81ea3c098c80e9ba',
    'device_serial_number': 'AB12FE45DD',
    'id': 'aaaad7ec-30f6-43cf-94a8-911bc8fe404c',
    'event_uploaded_at': '2020-02-27T23:55:00+00:00',
    'event_at': '2020-02-26T23:55:00+00:00',
    'type': 'sleep',
    'gnss': GNSS_2,
    'vehicle': {'plate_number': 'K123KK777', 'id': 'c2'},
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(SIGNAL_DEVICE_API_ADMIN_V2_EVENTS_LIMIT=100)
@pytest.mark.parametrize(
    'park_id, device_id, period_from, period_to, expected_events',
    [
        (
            'p1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:00:00+00:00',
            [EVENT_1],
        ),
        (
            'p1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:20:00+00:00',
            [EVENT_2, EVENT_1],
        ),
    ],
)
async def test_v2_events(
        taxi_signal_device_api_admin,
        park_id,
        device_id,
        period_from,
        period_to,
        expected_events,
):
    thread_id = utils.to_base64(f'||{device_id}')
    query = {
        'period': {'from': period_from, 'to': period_to},
        'thread_id': thread_id,
    }
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=query, headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'events': expected_events}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(SIGNAL_DEVICE_API_ADMIN_V2_EVENTS_LIMIT=1)
@pytest.mark.parametrize(
    'park_id, device_id, period_from, '
    'period_to, expected_events1, expected_events2',
    [
        (
            'p1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:20:00+00:00',
            [EVENT_2],
            [EVENT_1],
        ),
        (
            'p1',
            '4306de3dfd82406d81ea3c098c80e9ba',
            '2020-02-26T23:55:00+00:00',
            '2020-02-26T23:55:00+00:00',
            [EVENT_4],
            [EVENT_3],
        ),
    ],
)
async def test_v2_events_with_cursor(
        taxi_signal_device_api_admin,
        park_id,
        device_id,
        period_from,
        period_to,
        expected_events1,
        expected_events2,
):
    thread_id = utils.to_base64(f'||{device_id}')
    query = {
        'period': {'from': period_from, 'to': period_to},
        'thread_id': thread_id,
    }
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=query, headers=headers,
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    last_event = expected_events1[-1]
    cursor = utils.get_encoded_events_cursor(
        last_event['event_at'], last_event['id'],
    )
    assert utils.decode_cursor_from_resp_json(
        response_json,
    ) == utils.decode_cursor_from_event(last_event)
    assert response.json() == {'events': expected_events1, 'cursor': cursor}

    query['cursor'] = cursor
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=query, headers=headers,
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    last_event = expected_events2[-1]
    cursor = utils.get_encoded_events_cursor(
        last_event['event_at'], last_event['id'],
    )
    assert utils.decode_cursor_from_resp_json(
        response_json,
    ) == utils.decode_cursor_from_event(last_event)
    assert response.json() == {'events': expected_events2, 'cursor': cursor}

    query['cursor'] = cursor
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=query, headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'events': []}
