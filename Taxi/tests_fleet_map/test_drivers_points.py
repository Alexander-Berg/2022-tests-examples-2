# pylint: disable=C0302
import pytest

ENDPOINT = '/fleet/map/v1/drivers/points'

HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': 'park_id',
}

DRIVER_STATUS_REQUEST = {'park_id': 'park_id'}

DRIVER_STATUS_RESPONSE = {
    'park_id': 'park_id',
    'contractors': [
        {
            'profile_id': 'driver_id1',
            'status': 'busy',
            'updated_ts': 1636459068853,
            'orders': [{'status': 'driving'}],
        },
        {
            'profile_id': 'driver_id2',
            'status': 'online',
            'updated_ts': 1636459068853,
            'orders': [{'status': 'driving'}],
        },
        {
            'profile_id': 'driver_id3',
            'status': 'busy',
            'updated_ts': 1636459049414,
        },
        {
            'profile_id': 'driver_id4',
            'status': 'online',
            'updated_ts': 1636459176465,
        },
        {
            'profile_id': 'driver_id5',
            'status': 'offline',
            'updated_ts': 1636459417517,
        },
    ],
}

DRIVER_PROFILES_REQUEST = {
    'id_in_set': [
        'park_id_driver_id1',
        'park_id_driver_id2',
        'park_id_driver_id3',
        'park_id_driver_id4',
        'park_id_driver_id5',
    ],
    'projection': ['data.uuid', 'data.rule_id'],
}

DRIVER_PROFILES_RESPONSE = {
    'profiles': [
        {
            'data': {'uuid': 'driver_id1', 'rule_id': 'work_rule_id1'},
            'park_driver_profile_id': 'park_id_driver_id1',
        },
        {
            'data': {'uuid': 'driver_id2', 'rule_id': 'work_rule_id2'},
            'park_driver_profile_id': 'park_id_driver_id2',
        },
        {
            'data': {'uuid': 'driver_id3', 'rule_id': 'work_rule_id2'},
            'park_driver_profile_id': 'park_id_driver_id3',
        },
        {
            'data': {'uuid': 'driver_id4', 'rule_id': 'work_rule_id1'},
            'park_driver_profile_id': 'park_id_driver_id4',
        },
        {
            'data': {'uuid': 'driver_id5', 'rule_id': 'work_rule_id2'},
            'park_driver_profile_id': 'park_id_driver_id5',
        },
    ],
}

CANDIDATES_REQUEST = {
    'driver_ids': [
        'park_id_driver_id1',
        'park_id_driver_id2',
        'park_id_driver_id3',
        'park_id_driver_id4',
        'park_id_driver_id5',
    ],
    'data_keys': ['payment_methods'],
}

CANDIDATES_RESPONSE = {
    'drivers': [
        {
            'position': [13.360982, 52.545287],
            'id': 'park_id_driver_id1',
            'dbid': 'park_id',
            'uuid': 'driver_id1',
            'payment_methods': ['cash'],
        },
        {
            'position': [0, 52.545287],
            'id': 'park_id_driver_id2',
            'dbid': 'park_id',
            'uuid': 'driver_id2',
            'payment_methods': ['corp'],
        },
        {
            'position': [0, 0],
            'id': 'park_id_driver_id3',
            'dbid': 'park_id',
            'uuid': 'driver_id3',
            'payment_methods': ['cash', 'card', 'corp', 'coupon'],
        },
        {
            'position': [13.360982, 0],
            'id': 'park_id_driver_id4',
            'dbid': 'park_id',
            'uuid': 'driver_id4',
            'payment_methods': ['cash', 'card'],
        },
        {
            'position': [13.360982, 52.545287],
            'id': 'park_id_driver_id5',
            'dbid': 'park_id',
            'uuid': 'driver_id5',
            'payment_methods': ['card'],
        },
    ],
}

SERVICE_RESPONSE = {
    'items': [
        {
            'driver_id': 'driver_id1',
            'coordinates': {'lon': 13.360982, 'lat': 52.545287},
            'status': 'in_order',
        },
        {
            'driver_id': 'driver_id2',
            'coordinates': {'lon': 0.0, 'lat': 52.545287},
            'status': 'in_order',
        },
        {'driver_id': 'driver_id3', 'status': 'busy'},
        {
            'driver_id': 'driver_id4',
            'coordinates': {'lon': 13.360982, 'lat': 0.0},
            'status': 'free',
        },
    ],
    'totals': {
        'payment_method': {'only_cash': 1},
        'blocked': 0,
        'status': {'free': 1, 'busy': 1, 'in_order': 2},
        'total': 4,
    },
}


async def test_default(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-status/v2/park/statuses')
    def _statuses(request):
        assert request.query == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    response = await taxi_fleet_map.post(ENDPOINT, headers=HEADERS, json={})

    assert response.status_code == 200
    assert response.json() == SERVICE_RESPONSE


async def test_no_drivers(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-status/v2/park/statuses')
    def _statuses(request):
        assert request.query == DRIVER_STATUS_REQUEST
        return {'park_id': 'park_id', 'contractors': []}

    response = await taxi_fleet_map.post(ENDPOINT, headers=HEADERS, json={})

    assert response.status_code == 200
    assert response.json() == {
        'items': [],
        'totals': {
            'payment_method': {'only_cash': 0},
            'blocked': 0,
            'status': {'busy': 0, 'free': 0, 'in_order': 0},
            'total': 0,
        },
    }


async def test_no_coordinates(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-status/v2/park/statuses')
    def _statuses(request):
        assert request.query == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return {'drivers': []}

    response = await taxi_fleet_map.post(ENDPOINT, headers=HEADERS, json={})

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'driver_id': 'driver_id1', 'status': 'in_order'},
            {'driver_id': 'driver_id2', 'status': 'in_order'},
            {'driver_id': 'driver_id3', 'status': 'busy'},
            {'driver_id': 'driver_id4', 'status': 'free'},
        ],
        'totals': {
            'payment_method': {'only_cash': 0},
            'blocked': 0,
            'status': {'busy': 1, 'free': 1, 'in_order': 2},
            'total': 4,
        },
    }


@pytest.mark.parametrize(
    'service_request',
    [
        ({'filter': {}}),
        (
            {
                'filter': {
                    'work_rule_ids': [],
                    'payment_methods': [],
                    'statuses': [],
                },
            }
        ),
        ({'filter': {'payment_methods': [], 'statuses': []}}),
        ({'filter': {'work_rule_ids': [], 'statuses': []}}),
        ({'filter': {'work_rule_ids': [], 'payment_methods': []}}),
    ],
)
async def test_empty_filter(taxi_fleet_map, mockserver, service_request):
    @mockserver.json_handler('/driver-status/v2/park/statuses')
    def _statuses(request):
        assert request.query == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json=service_request,
    )

    assert response.status_code == 200
    assert response.json() == SERVICE_RESPONSE


async def test_filter_all(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-status/v2/park/statuses')
    def _statuses(request):
        assert request.query == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT,
        headers=HEADERS,
        json={
            'filter': {
                'statuses': ['free', 'in_order'],
                'payment_methods': ['cash'],
                'work_rule_ids': ['work_rule_id1', 'work_rule_id100'],
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'driver_id': 'driver_id1',
                'coordinates': {'lon': 13.360982, 'lat': 52.545287},
                'status': 'in_order',
            },
        ],
        'totals': {
            'payment_method': {'only_cash': 1},
            'blocked': 0,
            'status': {'free': 1, 'busy': 1, 'in_order': 2},
            'total': 4,
        },
    }


async def test_preset_status_in_order(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-status/v2/park/statuses')
    def _statuses(request):
        assert request.query == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json={'preset': 'status_in_order'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'coordinates': {'lat': 52.545287, 'lon': 13.360982},
                'driver_id': 'driver_id1',
                'status': 'in_order',
            },
            {
                'coordinates': {'lat': 52.545287, 'lon': 0.0},
                'driver_id': 'driver_id2',
                'status': 'in_order',
            },
        ],
        'totals': {
            'payment_method': {'only_cash': 1},
            'blocked': 0,
            'status': {'busy': 1, 'free': 1, 'in_order': 2},
            'total': 4,
        },
    }


async def test_preset_payment_method_only_cash(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-status/v2/park/statuses')
    def _statuses(request):
        assert request.query == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json={'preset': 'payment_method_only_cash'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'coordinates': {'lat': 52.545287, 'lon': 13.360982},
                'driver_id': 'driver_id1',
                'status': 'in_order',
            },
        ],
        'totals': {
            'payment_method': {'only_cash': 1},
            'blocked': 0,
            'status': {'busy': 1, 'free': 1, 'in_order': 2},
            'total': 4,
        },
    }
