# pylint: disable=C0302
import copy

import pytest

ENDPOINT = '/fleet/map/v2/drivers/points'

HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': 'park1',
}

DRIVER_STATUS_REQUEST = {'park_id': 'park1'}

DRIVER_STATUS_RESPONSE = {
    'park_id': 'park1',
    'contractors': [
        {
            'profile_id': 'driver1',
            'status': 'busy',
            'updated_ts': 1636459068853,
            'orders': [{'status': 'driving'}],
        },
        {
            'profile_id': 'driver2',
            'status': 'online',
            'updated_ts': 1636459068853,
            'orders': [{'status': 'driving'}],
        },
        {
            'profile_id': 'driver3',
            'status': 'busy',
            'updated_ts': 1636459049414,
        },
        {
            'profile_id': 'driver4',
            'status': 'online',
            'updated_ts': 1636459176465,
        },
        {
            'profile_id': 'driver5',
            'status': 'offline',
            'updated_ts': 1636459417517,
        },
    ],
}

DRIVER_PROFILES_REQUEST = {
    'id_in_set': [
        'park1_driver1',
        'park1_driver2',
        'park1_driver3',
        'park1_driver4',
        'park1_driver5',
    ],
    'projection': ['data.uuid', 'data.full_name'],
}

DRIVER_PROFILES_RESPONSE = {
    'profiles': [
        {
            'data': {
                'uuid': 'driver1',
                'full_name': {
                    'last_name': 'Анатолиев',
                    'first_name': 'Анатолий',
                    'middle_name': 'Анатольевич',
                },
            },
            'park_driver_profile_id': 'park1_driver1',
        },
        {
            'data': {
                'uuid': 'driver2',
                'full_name': {
                    'last_name': 'Борисов',
                    'first_name': 'Борис',
                    'middle_name': 'Борисович',
                },
            },
            'park_driver_profile_id': 'park1_driver2',
        },
        {
            'data': {'uuid': 'driver3'},
            'park_driver_profile_id': 'park1_driver3',
        },
        {
            'data': {
                'uuid': 'driver4',
                'full_name': {
                    'last_name': 'Davidov',
                    'middle_name': 'Davidovich',
                },
            },
            'park_driver_profile_id': 'park1_driver4',
        },
        {
            'data': {
                'uuid': 'driver5',
                'full_name': {
                    'last_name': 'Дмитриев',
                    'first_name': 'Дмитрий',
                },
            },
            'park_driver_profile_id': 'park1_driver5',
        },
    ],
}


PARKS_REQUEST = [
    {
        'query': {
            'park': {
                'id': 'park1',
                'driver_profile': {'work_status': ['working']},
                'current_status': {
                    'status': [
                        'free',
                        'busy',
                        'in_order_free',
                        'in_order_busy',
                    ],
                },
                'car': {'categories': ['econom'], 'is_rental': True},
            },
            'text': 'дмит',
        },
        'limit': 1000,
        'offset': 0,
    },
    {
        'query': {
            'park': {
                'id': 'park1',
                'driver_profile': {'work_status': ['working']},
                'current_status': {
                    'status': [
                        'free',
                        'busy',
                        'in_order_free',
                        'in_order_busy',
                    ],
                },
                'car': {'categories': ['business'], 'is_rental': True},
            },
            'text': 'дмит',
        },
        'limit': 1000,
        'offset': 0,
    },
]

PARKS_RESPONSE = {
    'driver_profiles': [
        {'driver_profile': {'id': 'driver1'}},
        {'driver_profile': {'id': 'driver4'}},
    ],
    'offset': 0,
    'parks': [{'id': 'park1'}],
    'total': 2,
}

CANDIDATES_REQUEST = {
    'driver_ids': [
        'park1_driver1',
        'park1_driver2',
        'park1_driver3',
        'park1_driver4',
        'park1_driver5',
    ],
    'data_keys': ['payment_methods'],
}

CANDIDATES_RESPONSE = {
    'drivers': [
        {
            'position': [13.360982, 52.545287],
            'id': 'park1_driver1',
            'dbid': 'park1',
            'uuid': 'driver1',
            'payment_methods': ['cash'],
        },
        {
            'position': [0, 52.545287],
            'id': 'park1_driver2',
            'dbid': 'park1',
            'uuid': 'driver2',
            'payment_methods': ['corp'],
        },
        {
            'position': [0, 0],
            'id': 'park1_driver3',
            'dbid': 'park1',
            'uuid': 'driver3',
            'payment_methods': ['cash', 'card', 'corp', 'coupon'],
        },
        {
            'position': [13.360982, 0],
            'id': 'park1_driver4',
            'dbid': 'park1',
            'uuid': 'driver4',
            'payment_methods': ['cash', 'card'],
        },
        {
            'position': [13.360982, 52.545287],
            'id': 'park1_driver5',
            'dbid': 'park1',
            'uuid': 'driver5',
            'payment_methods': ['card'],
        },
    ],
}

DRIVER_TRACKSTORY_REQUEST = {
    'driver_ids': [
        'park1_driver1',
        'park1_driver2',
        'park1_driver3',
        'park1_driver4',
        'park1_driver5',
    ],
    'type': 'adjusted',
}

DRIVER_TRACKSTORY_RESPONSE = {
    'results': [
        {
            'driver_id': 'park1_driver1',
            'position': {
                'direction': 0,
                'lat': 52.545287,
                'lon': 13.360982,
                'speed': 0,
                'timestamp': 100,
            },
            'type': 'adjusted',
        },
        {
            'driver_id': 'park1_driver2',
            'position': {
                'direction': 45,
                'lat': 52.545287,
                'lon': 0,
                'speed': 10,
                'timestamp': 100,
            },
            'type': 'adjusted',
        },
        {
            'driver_id': 'park1_driver4',
            'position': {
                'direction': 180,
                'lat': 0,
                'lon': 13.360982,
                'speed': 30,
                'timestamp': 100,
            },
            'type': 'adjusted',
        },
        {
            'driver_id': 'park1_driver5',
            'position': {
                'direction': 270,
                'lat': 52.545287,
                'lon': 13.360982,
                'speed': 40,
                'timestamp': 100,
            },
            'type': 'adjusted',
        },
    ],
}

SERVICE_RESPONSE = {
    'items': [
        {'driver_id': 'driver3', 'status': 'busy'},
        {
            'driver_id': 'driver4',
            'coordinates': {'lon': 13.360982, 'lat': 0.0},
            'status': 'free',
        },
        {
            'driver_id': 'driver1',
            'coordinates': {'lon': 13.360982, 'lat': 52.545287},
            'status': 'in_order',
        },
        {
            'driver_id': 'driver2',
            'coordinates': {'lon': 0.0, 'lat': 52.545287},
            'status': 'in_order',
        },
    ],
    'totals': {
        'payment_method': {'only_cash': 1},
        'blocked': 0,
        'status': {'free': 1, 'busy': 1, 'in_order': 2},
        'total': 4,
    },
    'is_degraded': False,
}

SERVICE_RESPONSE_WITH_DIRECTION = {
    'items': [
        {'driver_id': 'driver3', 'status': 'busy'},
        {
            'driver_id': 'driver4',
            'coordinates': {'lon': 13.360982, 'lat': 0.0},
            'status': 'free',
            'direction': 180,
            'speed': 30.0,
        },
        {
            'driver_id': 'driver1',
            'coordinates': {'lon': 13.360982, 'lat': 52.545287},
            'status': 'in_order',
            'direction': 0,
            'speed': 0.0,
        },
        {
            'driver_id': 'driver2',
            'coordinates': {'lon': 0.0, 'lat': 52.545287},
            'status': 'in_order',
            'direction': 45,
            'speed': 10.0,
        },
    ],
    'totals': {
        'payment_method': {'only_cash': 1},
        'blocked': 0,
        'status': {'free': 1, 'busy': 1, 'in_order': 2},
        'total': 4,
    },
    'is_degraded': False,
}


DEFAULT_PARAMS = [
    (False, SERVICE_RESPONSE),
    (True, SERVICE_RESPONSE_WITH_DIRECTION),
]


@pytest.mark.parametrize(
    'show_trackstory_data, expected_response', DEFAULT_PARAMS,
)
async def test_default(
        taxi_fleet_map,
        mockserver,
        taxi_config,
        show_trackstory_data,
        expected_response,
):
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

    @mockserver.json_handler('/driver-trackstory/positions')
    def _positions(request):
        assert request.json == DRIVER_TRACKSTORY_REQUEST
        return DRIVER_TRACKSTORY_RESPONSE

    taxi_config.set_values(
        {'FLEET_MAP_SHOW_TRACKSTORY_DATA': show_trackstory_data},
    )
    await taxi_fleet_map.invalidate_caches()

    response = await taxi_fleet_map.post(ENDPOINT, headers=HEADERS, json={})

    assert response.status_code == 200
    assert response.json() == expected_response


async def test_no_drivers(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-status/v2/park/statuses')
    def _statuses(request):
        assert request.query == DRIVER_STATUS_REQUEST
        return {'park_id': 'park1', 'contractors': []}

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
        'is_degraded': False,
    }


@pytest.mark.config(FLEET_MAP_SHOW_TRACKSTORY_DATA=True)
async def test_no_trackstory(taxi_fleet_map, mockserver):
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

    @mockserver.json_handler('/driver-trackstory/positions')
    def _positions(request):
        assert request.json == DRIVER_TRACKSTORY_REQUEST
        return {'results': []}

    response = await taxi_fleet_map.post(ENDPOINT, headers=HEADERS, json={})

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'driver_id': 'driver3', 'status': 'busy'},
            {
                'driver_id': 'driver4',
                'coordinates': {'lon': 13.360982, 'lat': 0.0},
                'status': 'free',
            },
            {
                'driver_id': 'driver1',
                'coordinates': {'lon': 13.360982, 'lat': 52.545287},
                'status': 'in_order',
            },
            {
                'driver_id': 'driver2',
                'coordinates': {'lon': 0.0, 'lat': 52.545287},
                'status': 'in_order',
            },
        ],
        'totals': {
            'payment_method': {'only_cash': 1},
            'blocked': 0,
            'status': {'free': 1, 'busy': 1, 'in_order': 2},
            'total': 4,
        },
        'is_degraded': False,
    }


async def test_no_coordinates(taxi_fleet_map, mockserver):
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
        return {'drivers': []}

    response = await taxi_fleet_map.post(ENDPOINT, headers=HEADERS, json={})

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'driver_id': 'driver3', 'status': 'busy'},
            {'driver_id': 'driver4', 'status': 'free'},
            {'driver_id': 'driver1', 'status': 'in_order'},
            {'driver_id': 'driver2', 'status': 'in_order'},
        ],
        'totals': {
            'payment_method': {'only_cash': 0},
            'blocked': 0,
            'status': {'busy': 1, 'free': 1, 'in_order': 2},
            'total': 4,
        },
        'is_degraded': False,
    }


async def test_filter_all(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-status/v2/park/statuses')
    def _statuses(request):
        assert request.query == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _list(request):
        assert request.json in PARKS_REQUEST
        return PARKS_RESPONSE

    driver_profiles_request = copy.deepcopy(DRIVER_PROFILES_REQUEST)
    driver_profiles_request['projection'].append('data.rule_id')

    driver_profiles_response = copy.deepcopy(DRIVER_PROFILES_RESPONSE)
    profiles = driver_profiles_response['profiles']
    profiles[0]['data']['rule_id'] = 'work_rule_id1'
    profiles[1]['data']['rule_id'] = 'work_rule_id2'
    profiles[2]['data']['rule_id'] = 'work_rule_id2'
    profiles[3]['data']['rule_id'] = 'work_rule_id1'
    profiles[4]['data']['rule_id'] = 'work_rule_id2'

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == driver_profiles_request
        return driver_profiles_response

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    @mockserver.json_handler('/driver-trackstory/positions')
    def _positions(request):
        assert request.json == DRIVER_TRACKSTORY_REQUEST
        return DRIVER_TRACKSTORY_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT,
        headers=HEADERS,
        json={
            'statuses': ['free', 'in_order'],
            'payment_methods': ['cash'],
            'work_rule_ids': ['work_rule_id1', 'work_rule_id100'],
            'search_text': 'дмит',
            'car': {'is_rental': True, 'categories': ['econom', 'business']},
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'driver_id': 'driver1',
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
        'is_degraded': False,
    }


async def test_sorting(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-status/v2/park/statuses')
    def _statuses(request):
        assert request.query == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return {
            'profiles': [
                {
                    'data': {
                        'uuid': 'driver1',
                        'full_name': {
                            'last_name': 'Дмитриев',
                            'first_name': 'Дмитрий',
                        },
                    },
                    'park_driver_profile_id': 'park1_driver1',
                },
                {
                    'data': {
                        'uuid': 'driver2',
                        'full_name': {
                            'last_name': 'Davidov',
                            'middle_name': 'Davidovich',
                        },
                    },
                    'park_driver_profile_id': 'park1_driver2',
                },
                {
                    'data': {'uuid': 'driver3'},
                    'park_driver_profile_id': 'park1_driver3',
                },
                {
                    'data': {
                        'uuid': 'driver4',
                        'full_name': {
                            'last_name': 'Борисов',
                            'first_name': 'Борис',
                            'middle_name': 'Борисович',
                        },
                    },
                    'park_driver_profile_id': 'park1_driver4',
                },
                {
                    'data': {
                        'uuid': 'driver5',
                        'full_name': {
                            'last_name': 'Анатолиев',
                            'first_name': 'Анатолий',
                            'middle_name': 'Анатольевич',
                        },
                    },
                    'park_driver_profile_id': 'park1_driver5',
                },
            ],
        }

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    response = await taxi_fleet_map.post(ENDPOINT, headers=HEADERS, json={})

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'driver_id': 'driver3', 'status': 'busy'},
            {
                'coordinates': {'lat': 52.545287, 'lon': 0.0},
                'driver_id': 'driver2',
                'status': 'in_order',
            },
            {
                'coordinates': {'lat': 0.0, 'lon': 13.360982},
                'driver_id': 'driver4',
                'status': 'free',
            },
            {
                'coordinates': {'lat': 52.545287, 'lon': 13.360982},
                'driver_id': 'driver1',
                'status': 'in_order',
            },
        ],
        'totals': {
            'payment_method': {'only_cash': 1},
            'blocked': 0,
            'status': {'busy': 1, 'free': 1, 'in_order': 2},
            'total': 4,
        },
        'is_degraded': False,
    }


async def test_search(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-status/v2/park/statuses')
    def _statuses(request):
        assert request.query == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _list(request):
        assert request.json in PARKS_REQUEST
        return PARKS_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT,
        headers=HEADERS,
        json={
            'search_text': 'дмит',
            'car': {'is_rental': True, 'categories': ['econom', 'business']},
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'coordinates': {'lat': 0.0, 'lon': 13.360982},
                'driver_id': 'driver4',
                'status': 'free',
            },
            {
                'coordinates': {'lat': 52.545287, 'lon': 13.360982},
                'driver_id': 'driver1',
                'status': 'in_order',
            },
        ],
        'totals': {
            'payment_method': {'only_cash': 1},
            'blocked': 0,
            'status': {'busy': 1, 'free': 1, 'in_order': 2},
            'total': 4,
        },
        'is_degraded': False,
    }


@pytest.mark.config(FLEET_MAP_DRIVERS_POINTS_DEGRADATION_ENABLE=True)
async def test_degradation(taxi_fleet_map, mockserver):
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
    assert response.json() == {
        'is_degraded': True,
        'items': [
            {
                'coordinates': {'lat': 52.545287, 'lon': 13.360982},
                'driver_id': 'driver1',
                'status': 'in_order',
            },
            {
                'coordinates': {'lat': 52.545287, 'lon': 0.0},
                'driver_id': 'driver2',
                'status': 'in_order',
            },
            {'driver_id': 'driver3', 'status': 'busy'},
            {
                'coordinates': {'lat': 0.0, 'lon': 13.360982},
                'driver_id': 'driver4',
                'status': 'free',
            },
        ],
        'totals': {
            'payment_method': {'only_cash': 1},
            'blocked': 0,
            'status': {'busy': 1, 'free': 1, 'in_order': 2},
            'total': 4,
        },
    }


BLOCKLIST_RESPONSE_WITH_BLOCKS = {
    'contractors': [
        {
            'park_contractor_profile_id': 'park1_driver1',
            'data': {
                'is_blocked': True,
                'blocks': [
                    {
                        'block_id': '179fb561-b3d0-42da-b038-1edcf774566c',
                        'predicate_id': '44444444-4444-4444-4444-444444444444',
                        'kwargs': {
                            'park_id': 'park1',
                            'license_id': 'license_pd_id1',
                        },
                        'status': 'active',
                        'till': '2022-02-15T11:00:00+00:00',
                        'mechanics': 'yango_temporary_block',
                    },
                ],
            },
        },
        {
            'park_contractor_profile_id': 'park1_driver2',
            'data': {
                'is_blocked': True,
                'blocks': [
                    {
                        'block_id': '179fb562-b3d0-42da-b038-1edcf774566c',
                        'predicate_id': '44444444-4444-4444-4444-444444444444',
                        'kwargs': {
                            'park_id': 'park1',
                            'license_id': 'license_pd_id2',
                        },
                        'status': 'active',
                        'till': '2022-02-15T12:00:00+00:00',
                        'mechanics': 'some_other_block',
                    },
                ],
            },
        },
        {
            'park_contractor_profile_id': 'park1_driver3',
            'data': {'is_blocked': False},
        },
        {
            'park_contractor_profile_id': 'park1_driver4',
            'data': {'is_blocked': False},
        },
        {
            'park_contractor_profile_id': 'park1_driver5',
            'data': {'is_blocked': False},
        },
    ],
}

BLOCKLIST_RESPONSE_WITHOUT_BLOCKS = {
    'contractors': [
        {
            'park_contractor_profile_id': 'park1_driver1',
            'data': {'is_blocked': False},
        },
        {
            'park_contractor_profile_id': 'park1_driver2',
            'data': {'is_blocked': False},
        },
        {
            'park_contractor_profile_id': 'park1_driver3',
            'data': {'is_blocked': False},
        },
        {
            'park_contractor_profile_id': 'park1_driver4',
            'data': {'is_blocked': False},
        },
        {
            'park_contractor_profile_id': 'park1_driver5',
            'data': {'is_blocked': False},
        },
    ],
}


@pytest.mark.parametrize(
    ['block_filter', 'blocklist_response', 'expected_response'],
    [
        (
            'any',
            BLOCKLIST_RESPONSE_WITHOUT_BLOCKS,
            {
                'is_degraded': False,
                'items': [
                    {'driver_id': 'driver3', 'status': 'busy'},
                    {
                        'coordinates': {'lat': 0.0, 'lon': 13.360982},
                        'driver_id': 'driver4',
                        'status': 'free',
                    },
                    {
                        'coordinates': {'lat': 52.545287, 'lon': 13.360982},
                        'driver_id': 'driver1',
                        'status': 'in_order',
                    },
                    {
                        'coordinates': {'lat': 52.545287, 'lon': 0.0},
                        'driver_id': 'driver2',
                        'status': 'in_order',
                    },
                ],
                'totals': {
                    'payment_method': {'only_cash': 1},
                    'blocked': 0,
                    'status': {'busy': 1, 'free': 1, 'in_order': 2},
                    'total': 4,
                },
            },
        ),
        (
            'any',
            BLOCKLIST_RESPONSE_WITH_BLOCKS,
            {
                'is_degraded': False,
                'items': [
                    {'driver_id': 'driver3', 'status': 'busy'},
                    {
                        'coordinates': {'lat': 0.0, 'lon': 13.360982},
                        'driver_id': 'driver4',
                        'status': 'free',
                    },
                    {
                        'coordinates': {'lat': 52.545287, 'lon': 13.360982},
                        'driver_id': 'driver1',
                        'is_blocked': True,
                        'status': 'in_order',
                    },
                    {
                        'coordinates': {'lat': 52.545287, 'lon': 0.0},
                        'driver_id': 'driver2',
                        'is_blocked': True,
                        'status': 'in_order',
                    },
                ],
                'totals': {
                    'payment_method': {'only_cash': 1},
                    'blocked': 2,
                    'status': {'busy': 1, 'free': 1, 'in_order': 2},
                    'total': 4,
                },
            },
        ),
        pytest.param(
            'any',
            BLOCKLIST_RESPONSE_WITH_BLOCKS,
            {
                'is_degraded': False,
                'items': [
                    {'driver_id': 'driver3', 'status': 'busy'},
                    {
                        'coordinates': {'lat': 0.0, 'lon': 13.360982},
                        'driver_id': 'driver4',
                        'status': 'free',
                    },
                    {
                        'coordinates': {'lat': 52.545287, 'lon': 13.360982},
                        'driver_id': 'driver1',
                        'is_blocked': True,
                        'status': 'in_order',
                    },
                    {
                        'coordinates': {'lat': 52.545287, 'lon': 0.0},
                        'driver_id': 'driver2',
                        'status': 'in_order',
                    },
                ],
                'totals': {
                    'payment_method': {'only_cash': 1},
                    'blocked': 1,
                    'status': {'busy': 1, 'free': 1, 'in_order': 2},
                    'total': 4,
                },
            },
            marks=pytest.mark.config(
                FLEET_MAP_BLOCK_MECHANICS_TO_SHOW=['yango_temporary_block'],
            ),
        ),
        pytest.param(
            'blocked',
            BLOCKLIST_RESPONSE_WITH_BLOCKS,
            {
                'is_degraded': False,
                'items': [
                    {
                        'coordinates': {'lat': 52.545287, 'lon': 13.360982},
                        'driver_id': 'driver1',
                        'is_blocked': True,
                        'status': 'in_order',
                    },
                ],
                'totals': {
                    'payment_method': {'only_cash': 1},
                    'blocked': 1,
                    'status': {'busy': 0, 'free': 0, 'in_order': 1},
                    'total': 1,
                },
            },
            marks=pytest.mark.config(
                FLEET_MAP_BLOCK_MECHANICS_TO_SHOW=['yango_temporary_block'],
            ),
        ),
        pytest.param(
            'not_blocked',
            BLOCKLIST_RESPONSE_WITH_BLOCKS,
            {
                'is_degraded': False,
                'items': [
                    {'driver_id': 'driver3', 'status': 'busy'},
                    {
                        'coordinates': {'lat': 0.0, 'lon': 13.360982},
                        'driver_id': 'driver4',
                        'status': 'free',
                    },
                    {
                        'coordinates': {'lat': 52.545287, 'lon': 0.0},
                        'driver_id': 'driver2',
                        'status': 'in_order',
                    },
                ],
                'totals': {
                    'payment_method': {'only_cash': 0},
                    'blocked': 0,
                    'status': {'busy': 1, 'free': 1, 'in_order': 1},
                    'total': 3,
                },
            },
            marks=pytest.mark.config(
                FLEET_MAP_BLOCK_MECHANICS_TO_SHOW=['yango_temporary_block'],
            ),
        ),
    ],
)
async def test_default_with_blocks(
        taxi_fleet_map,
        mockserver,
        blocklist_response,
        expected_response,
        block_filter,
):
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

    @mockserver.json_handler('/driver-trackstory/positions')
    def _positions(request):
        assert request.json == DRIVER_TRACKSTORY_REQUEST
        return DRIVER_TRACKSTORY_RESPONSE

    @mockserver.json_handler('/blocklist/admin/blocklist/v1/contractor/blocks')
    def _blocklist(request):
        assert request.json == {
            'contractors': [
                'park1_driver1',
                'park1_driver2',
                'park1_driver3',
                'park1_driver4',
                'park1_driver5',
            ],
        }
        return blocklist_response

    await taxi_fleet_map.invalidate_caches()

    response = await taxi_fleet_map.post(
        ENDPOINT,
        headers=HEADERS,
        json={'show_blocked': True, 'block_status': block_filter},
    )

    assert response.status_code == 200
    assert response.json() == expected_response
