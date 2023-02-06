import datetime

import dateutil.parser
import pytest


ENDPOINT = 'fleet/signal-device-tracks/v1/device/tracks/retrieve'
MOCK_URL = '/fleet-tracking-system/v1/track'


USER_TICKET = (
    '3:user:CA4Q__________9_GhsKAggqECoaBH'
    'JlYWQaBXdyaXRlINKF2MwEKAM:FmLcx6glId9f'
    'VYjhFTD69vUVDyMcawZ0z7En9Q0g6fsioFNEq'
    'dMhvEyx4bl25SFWFjjVnGBs-pPOpPWsqC4JmHV'
    'STH8lFgoAqeOb5B3D5g1t20V0NwxuAU9EIzkQ'
    'eE8a6cMbi4r6-lvAkUZZmefXbMvQddk_r1pHBg'
    'S--V-qAU4'
)


def _iso_to_ts(iso):
    return int(datetime.datetime.timestamp(dateutil.parser.parse(iso)))


TRACK = [
    {'at': '2019-05-01T07:06:00+00:00', 'lat': 55.773000, 'lon': 37.605000},
    {'at': '2019-05-01T07:09:00+00:00', 'lat': 55.773782, 'lon': 37.605617},
    {'at': '2019-05-01T07:10:00+00:00', 'lat': 55.770000, 'lon': 37.600000},
    {'at': '2019-05-01T07:14:00+00:00', 'lat': 55.771000, 'lon': 37.601000},
    {'at': '2019-05-01T07:15:00+00:00', 'lat': 55.772000, 'lon': 37.602000},
    {'at': '2019-05-01T08:15:00+00:00', 'lat': 55.774000, 'lon': 37.604000},
    {'at': '2019-05-02T07:20:00+00:00', 'lat': 55.772000, 'lon': 37.602000},
    {'at': '2019-05-02T07:21:00+00:00', 'lat': 55.775000, 'lon': 37.605000},
    {'at': '2019-05-02T07:24:00+00:00', 'lat': 55.780000, 'lon': 37.610000},
    {'at': '2019-06-02T07:00:00+00:00', 'lat': 55.785000, 'lon': 37.615000},
]
QUERY_POSITIONS_TRACKS_POSITIONS_RESPONSE = [
    {
        'timestamp': _iso_to_ts(point['at']) * 1000,
        'sensors': {},
        'geodata': [
            {
                'positions': [{'lon': point['lon'], 'lat': point['lat']}],
                'time_shift': 0,
            },
        ],
    }
    for point in TRACK
]
TRACKS_POSITIONS = [
    {
        'timestamp': _iso_to_ts(point['at']),
        'lat': point['lat'],
        'lon': point['lon'],
    }
    for point in TRACK
]
CAMERA_POSITIONS = [
    {
        'positions': [
            {'gps_position': position} for position in TRACKS_POSITIONS[1:5]
        ],
    },
    {
        'positions': [
            {'gps_position': position} for position in TRACKS_POSITIONS[5:6]
        ],
    },
    {
        'positions': [
            {'gps_position': position} for position in TRACKS_POSITIONS[6:9]
        ],
    },
]

EXPECTED_SLEEP_EVENT = {
    'event_at': 1556694540,
    'event_id': 'xxx',
    'event_type': 'sleep',
    'gps_position': {
        'lat': 55.773782,
        'lon': 37.605617,
        'timestamp': 1556694540,
    },
    'thread_id': 'fHx4eHg',
}

EXPECTED_ALL_EVENTS = [
    EXPECTED_SLEEP_EVENT,
    {
        'event_at': 1556781660,
        'event_id': 'zzz',
        'event_type': 'seatbelt',
        'gps_position': {
            'lat': 55.775,
            'lon': 37.605,
            'timestamp': 1556781660,
        },
        'thread_id': 'fHx6eno',
    },
]


CAMERA_POSITIONS_1 = [
    {
        'positions': [
            {'gps_position': position} for position in TRACKS_POSITIONS[1:5]
        ],
    },
    {
        'positions': [
            {'gps_position': position} for position in TRACKS_POSITIONS[5:6]
        ],
    },
]

NOW_1 = '2019-06-03T09:00:00+00:00'


@pytest.mark.now(NOW_1)
@pytest.mark.pgsql(
    'signal_device_tracks', files=['signal_device_tracks_db.sql'],
)
@pytest.mark.parametrize(
    'filter_, expected_events',
    [
        (None, EXPECTED_ALL_EVENTS),
        ({}, EXPECTED_ALL_EVENTS),
        ({'event_types': []}, []),
        ({'event_types': ['fart']}, []),
        (
            {'event_types': ['fart', 'sleep', 'another']},
            [EXPECTED_SLEEP_EVENT],
        ),
    ],
)
async def test_ok(
        taxi_signal_device_tracks, mockserver, filter_, expected_events,
):
    @mockserver.json_handler(MOCK_URL)
    async def _mock_driver_trackstory(request):
        request_data = request.query
        from_time = _iso_to_ts(request_data['from_time']) * 1000
        to_time = _iso_to_ts(request_data['to_time']) * 1000
        now = _iso_to_ts(NOW_1) * 1000
        assert (
            from_time <= to_time < now
        ), f'Incorrect parameters to trackstory'
        tracks_positions = [
            item
            for item in QUERY_POSITIONS_TRACKS_POSITIONS_RESPONSE
            if item['timestamp'] >= from_time and item['timestamp'] <= to_time
        ]
        return {'Verified': tracks_positions}

    body = {
        'serial_number': '123',
        'start_at': '2019-05-01T07:09:00+00:00',
        'end_at': '2019-05-02T07:24:00+00:00',
    }
    if filter_ is not None:
        body['filter'] = filter_

    response = await taxi_signal_device_tracks.post(
        ENDPOINT,
        headers={
            'X-Ya-User-Ticket': USER_TICKET,
            'X-Yandex-UID': '4242',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Park-Id': 'p1',
        },
        json=body,
    )

    assert response.status == 200, response.text

    assert response.json() == {
        'tracks': CAMERA_POSITIONS,
        'events': expected_events,
    }


NOW_2 = '2019-05-01T09:00:00+00:00'


@pytest.mark.now(NOW_2)
@pytest.mark.pgsql(
    'signal_device_tracks', files=['signal_device_tracks_db.sql'],
)
@pytest.mark.parametrize(
    'filter_, expected_events', [(None, [EXPECTED_SLEEP_EVENT])],
)
async def test_upper_bound(
        taxi_signal_device_tracks, mockserver, filter_, expected_events,
):
    @mockserver.json_handler(MOCK_URL)
    async def _mock_driver_trackstory(request):
        request_data = request.query
        from_time = _iso_to_ts(request_data['from_time']) * 1000
        to_time = _iso_to_ts(request_data['to_time']) * 1000
        now = _iso_to_ts(NOW_2) * 1000
        assert (
            from_time <= to_time < now
        ), f'Incorrect parameters to trackstory'
        tracks_positions = [
            item
            for item in QUERY_POSITIONS_TRACKS_POSITIONS_RESPONSE
            if item['timestamp'] >= from_time and item['timestamp'] <= to_time
        ]
        return {'Verified': tracks_positions}

    body = {
        'serial_number': '123',
        'start_at': '2019-05-01T07:09:00+00:00',
        'end_at': '2019-05-02T07:24:00+00:00',
    }
    if filter_ is not None:
        body['filter'] = filter_

    response = await taxi_signal_device_tracks.post(
        ENDPOINT,
        headers={
            'X-Ya-User-Ticket': USER_TICKET,
            'X-Yandex-UID': '4242',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Park-Id': 'p1',
        },
        json=body,
    )

    assert response.status == 200, response.text

    assert response.json() == {
        'tracks': CAMERA_POSITIONS_1,
        'events': expected_events,
    }
