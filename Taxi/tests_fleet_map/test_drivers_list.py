# pylint: disable=C0302
import copy

import pytest

ENDPOINT = '/fleet/map/v1/drivers/list'

HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': 'park1',
}

DRIVER_PROFILES_REQUEST = {
    'id_in_set': ['park1_driver_id'],
    'projection': ['data.uuid', 'data.car_id', 'data.full_name'],
}

DRIVER_PROFILES_RESPONSE = {
    'profiles': [
        {
            'data': {
                'full_name': {
                    'first_name': 'f',
                    'last_name': 'l',
                    'middle_name': 'm',
                },
                'car_id': 'car_id',
                'uuid': 'driver_id',
            },
            'park_driver_profile_id': 'park1_driver_id',
        },
    ],
}

CANDIDATES_REQUEST = {
    'driver_ids': ['park1_driver_id'],
    'data_keys': ['car_id', 'payment_methods', 'unique_driver_id'],
}

CANDIDATES_RESPONSE = {
    'drivers': [
        {
            'position': [13.360982, 52.545287],
            'id': 'park1_driver_id',
            'dbid': 'park1',
            'uuid': 'driver_id',
            'car_id': 'car_id',
            'payment_methods': ['cash'],
            'unique_driver_id': 'unique_driver_id',
        },
    ],
}

FLEET_VEHICLES_REQUEST = {
    'id_in_set': ['park1_car_id'],
    'projection': [
        'data.brand',
        'data.model',
        'data.number_normalized',
        'data.year',
    ],
}

FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'data': {
                'brand': 'b',
                'model': 'm',
                'number_normalized': 'nn',
                'year': 2020,
            },
            'park_id_car_id': 'park1_car_id',
        },
    ],
}

UNIQUE_DRIVERS_REQUEST = {'profile_id_in_set': ['park1_driver_id']}

UNIQUE_DRIVERS_RESPONSE = {
    'uniques': [
        {
            'park_driver_profile_id': 'park1_driver_id',
            'data': {'unique_driver_id': 'unique_driver_id'},
        },
    ],
}

UDRIVER_PHOTOS_REQUEST = {'unique_driver_ids': ['unique_driver_id']}

UDRIVER_PHOTOS_RESPONSE = {
    'actual_photos': [
        {
            'actual_photo': {
                'portrait_url': 'https://portrait_url',
                'avatar_url': 'https://avatar_url',
            },
            'unique_driver_id': 'unique_driver_id',
        },
    ],
}

DRIVER_STATUS_REQUEST = {
    'driver_ids': [{'park_id': 'park1', 'driver_id': 'driver_id'}],
}

DRIVER_STATUS_RESPONSE = {
    'statuses': [
        {
            'park_id': 'park1',
            'driver_id': 'driver_id',
            'status': 'online',
            'updated_ts': 1634290555458,
            'orders': [{'id': 'order_id', 'status': 'transporting'}],
        },
    ],
}

FLEET_TRANSACTIONS_API_REQUEST = {
    'query': {
        'park': {'id': 'park1', 'driver_profile': {'ids': ['driver_id']}},
        'balance': {'accrued_ats': ['2021-09-08T17:25:21+00:00']},
    },
}

FLEET_TRANSACTIONS_API_RESPONSE = {
    'driver_profiles': [
        {
            'driver_profile_id': 'driver_id',
            'balances': [
                {
                    'accrued_at': '2021-09-08T17:25:21+00:00',
                    'total_balance': '-1.0000',
                },
            ],
        },
    ],
}

DRIVER_ORDERS_REQUEST = {
    'query': {'park': {'id': 'park1', 'order': {'ids': ['order_id']}}},
}


DRIVER_ORDERS_RESPONSE = {
    'orders': [
        {
            'id': 'order_id',
            'order': {
                'short_id': 123,
                'status': 'driving',
                'booked_at': '2021-12-10T13:48:35+00:00',
                'provider': 'platform',
                'payment_method': 'cash',
                'created_at': '2021-12-10T13:37:04.783+00:00',
                'driving_at': '2021-12-10T13:37:05.991+00:00',
                'category': 'econom',
                'address_from': {
                    'address': 'AAA',
                    'lon': 37.483712,
                    'lat': 55.649038,
                },
                'address_to': {
                    'address': 'CCC',
                    'lon': 37.483712,
                    'lat': 55.649038,
                },
                'client_price': '0.0000',
                'route_points': [
                    {'address': 'BBB', 'lon': 37.483712, 'lat': 55.649038},
                ],
                'price': '0.0000',
                'receipt_details': [],
                'driver_profile_id': 'driver_id',
                'driver_profile': {'id': 'driver_id', 'name': 'f l m'},
                'vehicle': {
                    'id': 'car_id',
                    'name': 'b m',
                    'callsign': 'nn',
                    'number': 'nn',
                },
            },
        },
    ],
}

FLEET_PARKS_REQUEST = {'query': {'park': {'ids': ['park1']}}}

FLEET_PARKS_RESPONSE = {
    'parks': [
        {
            'id': 'park1',
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
            'specifications': ['taxi'],
        },
    ],
}

FLEET_PARKS_RESPONSE_SAAS = {
    'parks': [
        {
            'id': 'park1',
            'login': 'login',
            'is_active': True,
            'city_id': 'city',
            'locale': 'de',
            'is_billing_enabled': True,
            'is_franchising_enabled': True,
            'demo_mode': False,
            'country_id': 'country_id',
            'name': 'park name',
            'org_name': 'park org name',
            'geodata': {'lat': 45, 'lon': 6, 'zoom': 9},
            'specifications': ['taxi', 'saas'],
        },
    ],
}

FLEET_ORDERS_REQUEST = {'ids': [{'alias_id': 'order_id', 'park_id': 'park1'}]}

FLEET_ORDERS_RESPONSE = {
    'orders': [
        {
            'alias_id': 'order_id',
            'order_id': 'saas_order_id',
            'park_id': 'park1',
            'short_id': 1234,
            'route': [
                {'address': 'XXX', 'geopoint': [37.483712, 55.649038]},
                {'address': 'YYY'},
                {'address': 'ZZZ', 'geopoint': [37.483712, 55.649038]},
            ],
        },
    ],
}

SERVICE_REQUEST = {'driver_ids': ['driver_id'], 'with_order_field': True}

SERVICE_RESPONSE = {
    'items': [
        {
            'driver': {
                'avatar_url': 'https://avatar_url',
                'first_name': 'f',
                'id': 'driver_id',
                'last_name': 'l',
                'middle_name': 'm',
                'payment_methods': ['cash'],
                'status': 'in_order',
                'balance': '-1.0000',
            },
            'vehicle': {
                'brand': 'b',
                'id': 'car_id',
                'model': 'm',
                'number': 'nn',
                'year': 2020,
            },
            'order': {
                'id': 'order_id',
                'short_id': 123,
                'created_at': '2021-12-10T13:37:04.783+00:00',
                'booked_at': '2021-12-10T13:48:35+00:00',
                'driving_at': '2021-12-10T13:37:05.991+00:00',
                'route': [
                    {
                        'address': 'AAA',
                        'сoordinates': {'lon': 37.483712, 'lat': 55.649038},
                        'coordinates': {'lon': 37.483712, 'lat': 55.649038},
                    },
                    {
                        'address': 'BBB',
                        'сoordinates': {'lon': 37.483712, 'lat': 55.649038},
                        'coordinates': {'lon': 37.483712, 'lat': 55.649038},
                    },
                    {
                        'address': 'CCC',
                        'сoordinates': {'lon': 37.483712, 'lat': 55.649038},
                        'coordinates': {'lon': 37.483712, 'lat': 55.649038},
                    },
                ],
                'status': 'driving',
            },
        },
    ],
}

BLOCKLIST_RESPONSE = {
    'contractors': [
        {
            'park_contractor_profile_id': 'park1_driver_id',
            'data': {
                'is_blocked': True,
                'blocks': [
                    {
                        'block_id': '179fb561-b3d0-42da-b038-1edcf774566c',
                        'predicate_id': '44444444-4444-4444-4444-444444444444',
                        'kwargs': {
                            'park_id': 'park1s',
                            'license_id': 'license_pd_id1',
                        },
                        'status': 'active',
                        'till': '2022-02-15T11:00:00+00:00',
                        'mechanics': 'yango_temporary_block',
                    },
                ],
            },
        },
    ],
}


@pytest.mark.now('2021-09-08T17:25:21+00:00')
@pytest.mark.parametrize(
    ['show_blocked', 'should_be_blocked'],
    [
        pytest.param(
            True,
            True,
            marks=pytest.mark.config(
                FLEET_MAP_BLOCK_MECHANICS_TO_SHOW=['yango_temporary_block'],
            ),
        ),
        pytest.param(
            True,
            True,
            marks=pytest.mark.config(FLEET_MAP_BLOCK_MECHANICS_TO_SHOW=[]),
        ),
        pytest.param(
            True,
            False,
            marks=pytest.mark.config(
                FLEET_MAP_BLOCK_MECHANICS_TO_SHOW=['some_block'],
            ),
        ),
        pytest.param(False, False),
    ],
)
async def test_default(
        taxi_fleet_map, mockserver, show_blocked, should_be_blocked,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return DRIVER_ORDERS_RESPONSE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    @mockserver.json_handler('/blocklist/admin/blocklist/v1/contractor/blocks')
    def _blocklist(request):
        assert request.json == {'contractors': ['park1_driver_id']}
        return BLOCKLIST_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT,
        headers=HEADERS,
        json=dict({'show_blocked': True}, **SERVICE_REQUEST)
        if show_blocked
        else SERVICE_REQUEST,
    )

    resp = copy.deepcopy(SERVICE_RESPONSE)
    if show_blocked:
        resp['items'][0]['driver']['is_blocked'] = should_be_blocked

    assert response.status_code == 200
    assert response.json() == resp


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_default_saas(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return DRIVER_ORDERS_RESPONSE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE_SAAS

    @mockserver.json_handler(
        '/fleet-orders/internal/fleet-orders/v1/orders/bulk-retrieve-info',
    )
    def _order_info(request):
        assert request.json == FLEET_ORDERS_REQUEST
        return FLEET_ORDERS_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json=SERVICE_REQUEST,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    service_response['items'][0]['order']['id'] = 'saas_order_id'
    service_response['items'][0]['order']['short_id'] = 1234
    service_response['items'][0]['order']['route'] = [
        {
            'address': 'XXX',
            'сoordinates': {'lon': 37.483712, 'lat': 55.649038},
            'coordinates': {'lon': 37.483712, 'lat': 55.649038},
        },
        {'address': 'YYY'},
        {
            'address': 'ZZZ',
            'сoordinates': {'lon': 37.483712, 'lat': 55.649038},
            'coordinates': {'lon': 37.483712, 'lat': 55.649038},
        },
    ]
    assert response.status_code == 200
    assert response.json() == service_response


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_default_with_order_field_false(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json={'driver_ids': ['driver_id']},
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    del service_response['items'][0]['order']
    assert response.status_code == 200
    assert response.json() == service_response


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_without_drivers(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return {'driver_profiles': []}

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json=SERVICE_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == {'items': []}


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_without_positions(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return {'drivers': []}

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_by_profiles(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == UNIQUE_DRIVERS_REQUEST
        return UNIQUE_DRIVERS_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return DRIVER_ORDERS_RESPONSE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json=SERVICE_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'driver': {
                    'avatar_url': 'https://avatar_url',
                    'first_name': 'f',
                    'id': 'driver_id',
                    'last_name': 'l',
                    'middle_name': 'm',
                    'status': 'in_order',
                    'balance': '-1.0000',
                },
                'vehicle': {
                    'brand': 'b',
                    'id': 'car_id',
                    'model': 'm',
                    'number': 'nn',
                    'year': 2020,
                },
                'order': {
                    'id': 'order_id',
                    'short_id': 123,
                    'created_at': '2021-12-10T13:37:04.783+00:00',
                    'booked_at': '2021-12-10T13:48:35+00:00',
                    'driving_at': '2021-12-10T13:37:05.991+00:00',
                    'route': [
                        {
                            'address': 'AAA',
                            'сoordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                            'coordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                        },
                        {
                            'address': 'BBB',
                            'сoordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                            'coordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                        },
                        {
                            'address': 'CCC',
                            'сoordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                            'coordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                        },
                    ],
                    'status': 'driving',
                },
            },
        ],
    }


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_without_unique_ids(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return {'drivers': []}

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_by_profiles(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == UNIQUE_DRIVERS_REQUEST
        return {'uniques': []}

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return {'actual_photos': []}

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return DRIVER_ORDERS_RESPONSE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json=SERVICE_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'driver': {
                    'first_name': 'f',
                    'id': 'driver_id',
                    'last_name': 'l',
                    'middle_name': 'm',
                    'status': 'in_order',
                    'balance': '-1.0000',
                },
                'vehicle': {
                    'brand': 'b',
                    'id': 'car_id',
                    'model': 'm',
                    'number': 'nn',
                    'year': 2020,
                },
                'order': {
                    'id': 'order_id',
                    'short_id': 123,
                    'created_at': '2021-12-10T13:37:04.783+00:00',
                    'booked_at': '2021-12-10T13:48:35+00:00',
                    'driving_at': '2021-12-10T13:37:05.991+00:00',
                    'route': [
                        {
                            'address': 'AAA',
                            'сoordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                            'coordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                        },
                        {
                            'address': 'BBB',
                            'сoordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                            'coordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                        },
                        {
                            'address': 'CCC',
                            'сoordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                            'coordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                        },
                    ],
                    'status': 'driving',
                },
            },
        ],
    }


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_without_vehicle(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return {'drivers': []}

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return {'vehicles': []}

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_by_profiles(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == UNIQUE_DRIVERS_REQUEST
        return UNIQUE_DRIVERS_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return DRIVER_ORDERS_RESPONSE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json=SERVICE_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'driver': {
                    'avatar_url': 'https://avatar_url',
                    'first_name': 'f',
                    'id': 'driver_id',
                    'last_name': 'l',
                    'middle_name': 'm',
                    'status': 'in_order',
                    'balance': '-1.0000',
                },
                'vehicle': {'id': 'car_id'},
                'order': {
                    'id': 'order_id',
                    'short_id': 123,
                    'created_at': '2021-12-10T13:37:04.783+00:00',
                    'booked_at': '2021-12-10T13:48:35+00:00',
                    'driving_at': '2021-12-10T13:37:05.991+00:00',
                    'route': [
                        {
                            'address': 'AAA',
                            'сoordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                            'coordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                        },
                        {
                            'address': 'BBB',
                            'сoordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                            'coordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                        },
                        {
                            'address': 'CCC',
                            'сoordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                            'coordinates': {
                                'lon': 37.483712,
                                'lat': 55.649038,
                            },
                        },
                    ],
                    'status': 'driving',
                },
            },
        ],
    }


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_driver_status_free(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return {
            'statuses': [
                {
                    'park_id': 'park1',
                    'driver_id': 'driver_id',
                    'status': 'online',
                    'updated_ts': 1634290555458,
                },
            ],
        }

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return {'driver_profiles': []}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json=SERVICE_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'driver': {
                    'avatar_url': 'https://avatar_url',
                    'first_name': 'f',
                    'id': 'driver_id',
                    'last_name': 'l',
                    'middle_name': 'm',
                    'payment_methods': ['cash'],
                    'status': 'free',
                },
                'vehicle': {
                    'brand': 'b',
                    'id': 'car_id',
                    'model': 'm',
                    'number': 'nn',
                    'year': 2020,
                },
            },
        ],
    }


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_with_order(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return {'orders': []}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json=SERVICE_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'driver': {
                    'avatar_url': 'https://avatar_url',
                    'first_name': 'f',
                    'id': 'driver_id',
                    'last_name': 'l',
                    'middle_name': 'm',
                    'payment_methods': ['cash'],
                    'status': 'in_order',
                    'balance': '-1.0000',
                },
                'vehicle': {
                    'brand': 'b',
                    'id': 'car_id',
                    'model': 'm',
                    'number': 'nn',
                    'year': 2020,
                },
            },
        ],
    }
