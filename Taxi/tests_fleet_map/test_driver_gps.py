import datetime

import aiohttp.web
import dateutil.parser
import pytest

ENDPOINT = '/fleet/map/v1/driver/gps'

HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'login',
    'X-Yandex-UID': '123',
    'X-Park-Id': 'park_id',
}

SETTINGS = {
    'concurrency': 4,
    'batch_minutes': 6 * 60,
    'adjust': False,
    'distance_limit': 500,
}

ROUTE_REQUEST = {
    'route': [[37.605, 55.775], [37.61, 55.78]],
    'output': 'json',
    'request_path': True,
    'results': 1,
    'use_jams': False,
    'use_tolls': False,
}

ROUTE_RESPONSE = {
    'summary': {'duration': 7, 'length': 8},
    'paths': [
        [
            {'duration': 2, 'length': 3, 'position': [31.005, 50.775]},
            {'duration': 5, 'length': 8, 'position': [31.01, 50.770]},
        ],
    ],
}

FLEET_ORDERS_REQUEST = {
    'ids': [
        {'alias_id': '12345678901234567890123456789012', 'park_id': 'park_id'},
        {'alias_id': '11111sdckjsndclskncd2378', 'park_id': 'park_id'},
    ],
}

FLEET_ORDERS_RESPONSE = {
    'orders': [
        {
            'alias_id': '12345678901234567890123456789012',
            'order_id': 'saas_order_id1',
            'park_id': 'park_id',
            'short_id': 1234,
            'route': [
                {
                    'address': 'from_address',
                    'geopoint': [37.483712, 55.649038],
                },
                {'address': 'between'},
                {'address': 'to_address', 'geopoint': [37.483712, 55.649038]},
            ],
        },
        {
            'alias_id': '11111sdckjsndclskncd2378',
            'order_id': 'saas_order_id2',
            'park_id': 'park_id',
            'short_id': 2333,
            'route': [
                {'address': 'only one', 'geopoint': [37.483712, 55.649038]},
            ],
        },
    ],
}

ORDERS_REQUEST = {
    'limit': 300,
    'query': {
        'park': {
            'driver_profile': {'id': 'driver_id'},
            'id': 'park_id',
            'order': {
                'booked_at': {
                    'from': '2021-12-02T00:00:00+00:00',
                    'to': '2021-12-03T00:00:00+00:00',
                },
            },
        },
    },
}

ORDERS_RESPONSE = {
    'orders': [
        {
            'id': '12345678901234567890123456789012',
            'short_id': 12345,
            'status': 'complete',
            'created_at': '2021-12-02T21:00:50+00:00',
            'booked_at': '2021-12-02T21:04:50+00:00',
            'ended_at': '2021-12-02T21:20:50+00:00',
            'provider': 'platform',
            'amenities': [],
            'address_from': {
                'address': 'location address',
                'lat': 0.0,
                'lon': 0.0,
            },
            'events': [],
            'route_points': [
                {'address': 'point', 'lat': 12.12, 'lon': 13.343443},
                {'address': 'address to', 'lat': 12.01, 'lon': 13.343443},
            ],
            'db_id': 'park_id1',
            'driver_uuid': 'driver_profile_id1',
        },
        {
            'id': '11111sdckjsndclskncd2378',
            'short_id': 21343,
            'status': 'complete',
            'created_at': '2021-12-02T16:00:40+00:00',
            'booked_at': '2021-12-02T16:05:40+00:00',
            'ended_at': '2021-12-02T16:58:40+00:00',
            'provider': 'platform',
            'amenities': [],
            'address_from': {
                'address': 'location address2',
                'lat': 0.0,
                'lon': 0.0,
            },
            'events': [],
            'route_points': [],
            'db_id': 'park_id1',
            'driver_uuid': 'driver_profile_id1',
        },
    ],
    'limit': 300,
}

FLEET_PARKS_REQUEST = {'query': {'park': {'ids': ['park_id']}}}

TRACK = [
    {'timestamp': 1638463800, 'lat': 55.773782, 'lon': 37.605617, 'speed': 7},
    {'timestamp': 1638463900, 'lat': 55.770000, 'lon': 37.600000, 'speed': 3},
    {'timestamp': 1638472098, 'lat': 55.772000, 'lon': 37.602000},
    {'timestamp': 1638472105, 'lat': 55.771000, 'lon': 37.601000, 'speed': 5},
    {
        'timestamp': 1638479390,
        'lat': 55.775000,
        'lon': 37.605000,
        'speed': 9.12,
    },
    {
        'timestamp': 1638486012,
        'lat': 55.780000,
        'lon': 37.610000,
        'speed': -13.000023,
    },
]

CONTRACTOR_STATUS_HISTORY_RESPONSE = {
    'contractors': [{'park_id': 'park_id', 'profile_id': 'driver_id'}],
}


def _build_request(date_to):
    return {
        'contractor_profile_id': 'driver_id',
        'date_from': '2021-12-02T00:00:00+00:00',
        'date_to': date_to,
    }


def _iso_to_ts(iso):
    return int(datetime.datetime.timestamp(dateutil.parser.parse(iso)))


def _build_track_response(request):
    result = []
    for track_item in TRACK:
        if track_item['timestamp'] > _iso_to_ts(
                request['from_time'],
        ) and track_item['timestamp'] < _iso_to_ts(request['to_time']):
            result.append(track_item)
    return result


def _build_park_response(specifications):
    park_response = {
        'parks': [
            {
                'id': 'park_id',
                'login': 'login',
                'is_active': True,
                'city_id': 'city',
                'locale': 'ru',
                'is_billing_enabled': True,
                'is_franchising_enabled': True,
                'demo_mode': False,
                'country_id': 'country_id',
                'name': 'park name',
                'org_name': 'park org name',
                'geodata': {'lat': 45, 'lon': 6, 'zoom': 9},
                'specifications': specifications,
            },
        ],
    }
    return park_response


@pytest.mark.parametrize(
    'request_date_from',
    [None, '2021-12-03T00:00:00+00:00', '2021-12-10T00:00:00+00:00'],
)
@pytest.mark.parametrize(
    ['events', 'expected_response_key', 'park_response'],
    [
        (
            [
                {
                    'timestamp': 1638463800,
                    'status': 'online',
                    'on_order': True,
                },
                {'timestamp': 1638472092, 'status': 'busy'},
                {'timestamp': 1638479388, 'status': 'busy', 'on_order': True},
                {'timestamp': 1638486000, 'status': 'online'},
            ],
            'simple',
            _build_park_response(['taxi']),
        ),
        (
            [
                {
                    'timestamp': 1638463800,
                    'status': 'online',
                    'on_order': True,
                },
                {'timestamp': 1638472092, 'status': 'busy'},
                {'timestamp': 1638479388, 'status': 'online'},
                {'timestamp': 1638486000, 'status': 'online'},
            ],
            'double_status',
            _build_park_response(['taxi']),
        ),
        (
            [
                {
                    'timestamp': 1638463800,
                    'status': 'online',
                    'on_order': True,
                },
                {'timestamp': 1638472092, 'status': 'busy'},
                {'timestamp': 1638479388, 'status': 'busy', 'on_order': True},
                {'timestamp': 1638482400, 'status': 'offline'},
                {'timestamp': 1638486000, 'status': 'online'},
            ],
            'offline',
            _build_park_response(['taxi']),
        ),
        (
            [
                {
                    'timestamp': 1638463800,
                    'status': 'online',
                    'on_order': True,
                },
                {'timestamp': 1638472092, 'status': 'busy'},
                {'timestamp': 1638479388, 'status': 'busy', 'on_order': True},
                {'timestamp': 1638486000, 'status': 'online'},
            ],
            'simple_saas',
            _build_park_response(['taxi', 'saas']),
        ),
    ],
)
@pytest.mark.config(FLEET_MAP_DRIVER_GPS_SETTINGS=SETTINGS)
@pytest.mark.now('2021-12-03T13:34:26+00:00')
async def test_ok(
        taxi_fleet_map,
        mockserver,
        load_json,
        events,
        expected_response_key,
        park_response,
        request_date_from,
):
    date_from = '2021-12-02T00:00:00+00:00'
    date_to = '2021-12-03T00:00:00+00:00'

    @mockserver.json_handler('/contractor-status-history/events')
    def _events(request):
        assert request.json == {
            'interval': {
                'from': _iso_to_ts(date_from),
                'to': _iso_to_ts(date_to),
            },
            'contractors': [{'park_id': 'park_id', 'profile_id': 'driver_id'}],
            'verbose': False,
        }
        CONTRACTOR_STATUS_HISTORY_RESPONSE['contractors'][0]['events'] = events
        return CONTRACTOR_STATUS_HISTORY_RESPONSE

    @mockserver.json_handler('/driver-trackstory/get_track')
    def _track(request):
        return {
            'id': 'park_id_driver_id',
            'track': _build_track_response(request.json),
        }

    @mockserver.json_handler('/tigraph-router/route')
    def _route(request):
        assert request.json == ROUTE_REQUEST
        return ROUTE_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    def _order_list(request):
        assert request.json == ORDERS_REQUEST
        return ORDERS_RESPONSE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return park_response

    @mockserver.json_handler(
        '/fleet-orders/internal/fleet-orders/v1/orders/bulk-retrieve-info',
    )
    def _order_info(request):
        assert request.json == FLEET_ORDERS_REQUEST
        return FLEET_ORDERS_RESPONSE

    response_ = load_json('service_response.json')[expected_response_key]

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json=_build_request(request_date_from),
    )
    assert response.status_code == 200
    assert response.json() == response_


@pytest.mark.now('2021-12-03T13:34:26+00:00')
async def test_403(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/contractor-status-history/events')
    def _events(request):
        return CONTRACTOR_STATUS_HISTORY_RESPONSE

    @mockserver.json_handler('/driver-trackstory/get_track')
    def _track(request):
        return aiohttp.web.json_response(
            {'code': 'too_long_interval', 'message': ''}, status=400,
        )

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json=_build_request(None),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'too_long_period',
        'message': 'Too long period interval',
    }
