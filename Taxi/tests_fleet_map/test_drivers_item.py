# pylint: disable=C0302
import copy
import typing

import pytest

ENDPOINT = '/fleet/map/v1/drivers/item'

HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': 'park1',
}

DRIVER_PROFILES_REQUEST = {
    'id_in_set': ['park1_driver1'],
    'projection': [
        'data.work_status',
        'data.full_name',
        'data.license.pd_id',
        'data.phone_pd_ids',
        'data.car_id',
    ],
}

DRIVER_PROFILES_RESPONSE = {
    'profiles': [
        {
            'data': {
                'work_status': 'working',
                'full_name': {
                    'first_name': 'f',
                    'last_name': 'l',
                    'middle_name': 'm',
                },
                'license': {'pd_id': 'license_pd_id'},
                'phone_pd_ids': [{'pd_id': 'phone_pd_id'}],
                'car_id': 'car1',
            },
            'park_driver_profile_id': 'park1_driver1',
        },
    ],
}

PERSONAL_PHONES_REQUEST = {
    'items': [{'id': 'phone_pd_id'}],
    'primary_replica': False,
}

PERSONAL_PHONES_RESPONSE = {
    'items': [{'id': 'phone_pd_id', 'value': 'phone_value'}],
}

PERSONAL_DRIVER_LICENSES_REQUEST = {
    'items': [{'id': 'license_pd_id'}],
    'primary_replica': False,
}

PERSONAL_DRIVER_LICENSES_RESPONSE = {
    'items': [{'id': 'license_pd_id', 'value': 'license_value'}],
}

CANDIDATES_REQUEST = {
    'driver_ids': ['park1_driver1'],
    'data_keys': ['car_id', 'payment_methods', 'unique_driver_id'],
}

CANDIDATES_RESPONSE = {
    'drivers': [
        {
            'position': [13.360982, 52.545287],
            'id': 'park1_driver1',
            'dbid': 'park1',
            'uuid': 'driver1',
            'car_id': 'car1',
            'payment_methods': ['cash'],
            'unique_driver_id': 'unique_driver_id',
        },
    ],
}

DRIVER_STATUS_REQUEST = {
    'driver_ids': [{'park_id': 'park1', 'driver_id': 'driver1'}],
}

DRIVER_STATUS_RESPONSE = {
    'statuses': [
        {
            'park_id': 'park1',
            'driver_id': 'driver1',
            'status': 'online',
            'updated_ts': 1634290555458,
            'orders': [{'id': 'order_id', 'status': 'transporting'}],
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

DRIVER_ORDERS_REQUEST = {
    'query': {'park': {'id': 'park1', 'order': {'ids': ['order_id']}}},
}

DRIVER_ORDERS_RESPONSE = {
    'orders': [
        {
            'id': 'order_id',
            'order': {
                'short_id': 123,
                'status': 'transporting',
                'booked_at': '2021-12-10T13:37:04+00:00',
                'provider': 'platform',
                'payment_method': 'cash',
                'created_at': '2021-12-10T13:37:03.783+00:00',
                'driving_at': '2021-12-10T13:37:05.991+00:00',
                'waited_at': '2021-12-10T13:37:06.991+00:00',
                'transporting_at': '2021-12-10T13:37:07.991+00:00',
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
                'driver_profile_id': 'driver1',
                'driver_profile': {'id': 'driver1', 'name': 'f l m'},
                'vehicle': {
                    'id': 'car1',
                    'name': 'b m',
                    'callsign': 'nn',
                    'number': 'nn',
                },
                'price': '428.0000',
                'receipt_details': [
                    {
                        'name': 'waiting',
                        'price': '0.0000',
                        'price_for_one': '0.0000',
                        'count': 0,
                    },
                    {
                        'name': 'waiting_in_transit',
                        'price': '0.0000',
                        'price_for_one': '0.0000',
                        'count': 0,
                    },
                ],
                'mileage': '0.0000',
                'fixed_price': {'show': True, 'price': '428.0000'},
            },
        },
    ],
}

DRIVER_ORDERS_TRACK_REQUEST = {'park_id': 'park1', 'order_id': 'order_id'}

DRIVER_ORDERS_TRACK_RESPONSE = {
    'track': [
        {
            'tracked_at': '2021-12-10T13:37:05.991+00:00',
            'location': {'lat': 55.6490364074701, 'lon': 37.483711},
            'speed': 0.0,
            'order_status': 'driving',
        },
        {
            'tracked_at': '2021-12-10T13:37:06.991+00:00',
            'location': {'lat': 55.6490364074702, 'lon': 37.483712},
            'speed': 0.0,
            'order_status': 'waiting',
        },
        {
            'tracked_at': '2021-12-10T13:37:07.991+00:00',
            'location': {'lat': 55.6490364074703, 'lon': 37.483713},
            'speed': 0.0,
            'order_status': 'transporting',
        },
        {
            'tracked_at': '2021-12-10T13:37:07.992+00:00',
            'location': {'lat': 55.6490364074704, 'lon': 37.483714},
            'speed': 0.0,
            'order_status': 'transporting',
        },
    ],
}

FLEET_VEHICLES_REQUEST = {
    'id_in_set': ['park1_car1'],
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
            'park_id_car_id': 'park1_car1',
        },
    ],
}

UNIQUE_DRIVERS_REQUEST = {'profile_id_in_set': ['park1_driver1']}

UNIQUE_DRIVERS_RESPONSE = {
    'uniques': [
        {
            'park_driver_profile_id': 'park1_driver1',
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

FLEET_TRANSACTIONS_API_REQUEST = {
    'query': {
        'park': {'id': 'park1', 'driver_profile': {'ids': ['driver1']}},
        'balance': {'accrued_ats': ['2021-09-08T17:25:21+00:00']},
    },
}

FLEET_TRANSACTIONS_API_RESPONSE = {
    'driver_profiles': [
        {
            'driver_profile_id': 'driver1',
            'balances': [
                {
                    'accrued_at': '2021-09-08T17:25:21+00:00',
                    'total_balance': '-1.0000',
                },
            ],
        },
    ],
}

DRIVER_TRACKSTORY_REQUEST = {'driver_id': 'park1_driver1', 'type': 'adjusted'}

DRIVER_TRACKSTORY_RESPONSE = {
    'position': {
        'direction': 45,
        'lat': 52.545287,
        'lon': 13.360982,
        'speed': 10.0,
        'timestamp': 100,
    },
    'type': 'adjusted',
}

SERVICE_REQUEST = {'driver_id': 'driver1'}

SERVICE_RESPONSE = {
    'coordinates': {'lon': 13.360982, 'lat': 52.545287},
    'driver': {
        'id': 'driver1',
        'first_name': 'f',
        'last_name': 'l',
        'middle_name': 'm',
        'status': 'in_order',
        'payment_methods': ['cash'],
        'avatar_url': 'https://avatar_url',
        'phone': 'phone_value',
        'license': 'license_value',
        'balance': '-1.0000',
    },
    'vehicle': {
        'id': 'car1',
        'brand': 'b',
        'model': 'm',
        'number': 'nn',
        'year': 2020,
    },
    'order': {
        'id': 'order_id',
        'short_id': 123,
        'created_at': '2021-12-10T13:37:03.783+00:00',
        'booked_at': '2021-12-10T13:37:04+00:00',
        'driving_at': '2021-12-10T13:37:05.991+00:00',
        'waited_at': '2021-12-10T13:37:06.991+00:00',
        'transporting_at': '2021-12-10T13:37:07.991+00:00',
        'status': 'transporting',
        'payment_method': 'cash',
        'category': 'econom',
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
        'track': {
            'driving': [
                {
                    'lat': 55.6490364074701,
                    'lon': 37.483711,
                    'tracked_at': 1639143425,
                },
            ],
            'waiting': [
                {
                    'lat': 55.6490364074702,
                    'lon': 37.483712,
                    'tracked_at': 1639143426,
                },
            ],
            'transporting': [
                {
                    'lat': 55.6490364074703,
                    'lon': 37.483713,
                    'tracked_at': 1639143427,
                },
                {
                    'lat': 55.6490364074704,
                    'lon': 37.483714,
                    'tracked_at': 1639143427,
                },
            ],
        },
        'actual_time': 2,
        'price': '428.0000',
        'fixed_price': '428.0000',
        'mileage': '0.0000',
    },
}

SERVICE_RESPONSE_WITH_DIRECTION: typing.Dict[str, object] = {
    **SERVICE_RESPONSE,
    'direction': 45,
    'speed': 10.0,
}

BLOCKLIST_RESPONSE_WITHOUT_BLOCK = {
    'contractors': [
        {
            'park_contractor_profile_id': 'park1_driver1',
            'data': {'is_blocked': False},
        },
    ],
}

BLOCKLIST_RESPONSE_WITH_BLOCK = {
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

DEFAULT_PARAMS = [
    (False, SERVICE_RESPONSE),
    (True, SERVICE_RESPONSE_WITH_DIRECTION),
]


@pytest.mark.now('2021-09-08T17:25:21+00:00')
@pytest.mark.parametrize(
    'show_trackstory_data, expected_response', DEFAULT_PARAMS,
)
@pytest.mark.parametrize(
    ['show_blocked', 'blocklist_response', 'should_be_blocked'],
    [
        pytest.param(False, {}, False),
        pytest.param(True, BLOCKLIST_RESPONSE_WITHOUT_BLOCK, False),
        pytest.param(True, BLOCKLIST_RESPONSE_WITH_BLOCK, True),
        pytest.param(
            True,
            BLOCKLIST_RESPONSE_WITH_BLOCK,
            True,
            marks=pytest.mark.config(
                FLEET_MAP_BLOCK_MECHANICS_TO_SHOW=['yango_temporary_block'],
            ),
        ),
        pytest.param(
            True,
            BLOCKLIST_RESPONSE_WITH_BLOCK,
            False,
            marks=pytest.mark.config(
                FLEET_MAP_BLOCK_MECHANICS_TO_SHOW=['some_other_block'],
            ),
        ),
    ],
)
async def test_default(
        taxi_fleet_map,
        mockserver,
        taxi_config,
        show_trackstory_data,
        expected_response,
        show_blocked,
        blocklist_response,
        should_be_blocked,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        assert request.json == PERSONAL_PHONES_REQUEST
        return PERSONAL_PHONES_RESPONSE

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _driver_licenses_bulk_retrieve(request):
        assert request.json == PERSONAL_DRIVER_LICENSES_REQUEST
        return PERSONAL_DRIVER_LICENSES_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return DRIVER_ORDERS_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/track')
    def _orderstrack(request):
        assert request.query == DRIVER_ORDERS_TRACK_REQUEST
        return DRIVER_ORDERS_TRACK_RESPONSE

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    @mockserver.json_handler('/driver-trackstory/position')
    def _position(request):
        assert request.json == DRIVER_TRACKSTORY_REQUEST
        return DRIVER_TRACKSTORY_RESPONSE

    @mockserver.json_handler('/blocklist/admin/blocklist/v1/contractor/blocks')
    def _blocklist(request):
        assert request.json == {'contractors': ['park1_driver1']}
        return blocklist_response

    taxi_config.set_values(
        {'FLEET_MAP_SHOW_TRACKSTORY_DATA': show_trackstory_data},
    )
    await taxi_fleet_map.invalidate_caches()

    response = await taxi_fleet_map.get(
        ENDPOINT,
        headers=HEADERS,
        params=dict({'show_blocked': True}, **SERVICE_REQUEST)
        if show_blocked
        else SERVICE_REQUEST,
    )

    exp_resp = copy.deepcopy(expected_response)
    if should_be_blocked:
        exp_resp['driver']['is_blocked'] = True

    assert response.status_code == 200
    assert response.json() == exp_resp


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_default_saas(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        assert request.json == PERSONAL_PHONES_REQUEST
        return PERSONAL_PHONES_RESPONSE

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _driver_licenses_bulk_retrieve(request):
        assert request.json == PERSONAL_DRIVER_LICENSES_REQUEST
        return PERSONAL_DRIVER_LICENSES_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

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

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return DRIVER_ORDERS_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/track')
    def _orderstrack(request):
        assert request.query == DRIVER_ORDERS_TRACK_REQUEST
        return DRIVER_ORDERS_TRACK_RESPONSE

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    response = await taxi_fleet_map.get(
        ENDPOINT, headers=HEADERS, params=SERVICE_REQUEST,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    service_response['order']['id'] = 'saas_order_id'
    service_response['order']['short_id'] = 1234
    service_response['order']['route'] = [
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
async def test_default_support(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return DRIVER_ORDERS_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/track')
    def _orderstrack(request):
        assert request.query == DRIVER_ORDERS_TRACK_REQUEST
        return DRIVER_ORDERS_TRACK_RESPONSE

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    headers = copy.deepcopy(HEADERS)
    headers['X-Ya-User-Ticket-Provider'] = 'yandex_team'

    response = await taxi_fleet_map.get(
        ENDPOINT, headers=headers, params=SERVICE_REQUEST,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    del service_response['driver']['phone']
    del service_response['driver']['license']

    assert response.status_code == 200
    assert response.json() == service_response


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_driver_not_found(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return {'profiles': [{'park_driver_profile_id': 'park1_driver1'}]}

    response = await taxi_fleet_map.get(
        ENDPOINT, headers=HEADERS, params=SERVICE_REQUEST,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'DRIVER_NOT_FOUND',
        'message': 'Driver not found',
    }


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_without_order(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        assert request.json == PERSONAL_PHONES_REQUEST
        return PERSONAL_PHONES_RESPONSE

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _driver_licenses_bulk_retrieve(request):
        assert request.json == PERSONAL_DRIVER_LICENSES_REQUEST
        return PERSONAL_DRIVER_LICENSES_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return {'orders': []}

    @mockserver.json_handler('/driver-orders/v1/parks/orders/track')
    def _orderstrack(request):
        assert request.query == DRIVER_ORDERS_TRACK_REQUEST
        return DRIVER_ORDERS_TRACK_RESPONSE

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    response = await taxi_fleet_map.get(
        ENDPOINT, headers=HEADERS, params=SERVICE_REQUEST,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    del service_response['order']

    assert response.status_code == 200
    assert response.json() == service_response


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_order_without_track(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        assert request.json == PERSONAL_PHONES_REQUEST
        return PERSONAL_PHONES_RESPONSE

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _driver_licenses_bulk_retrieve(request):
        assert request.json == PERSONAL_DRIVER_LICENSES_REQUEST
        return PERSONAL_DRIVER_LICENSES_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return DRIVER_ORDERS_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/track')
    def _orderstrack(request):
        assert request.query == DRIVER_ORDERS_TRACK_REQUEST
        return mockserver.make_response('Wrong method', status=500)

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    response = await taxi_fleet_map.get(
        ENDPOINT, headers=HEADERS, params=SERVICE_REQUEST,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    del service_response['order']['track']
    assert response.status_code == 200
    assert response.json() == service_response


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_driver_status_not_in_order(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        assert request.json == PERSONAL_PHONES_REQUEST
        return PERSONAL_PHONES_RESPONSE

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _driver_licenses_bulk_retrieve(request):
        assert request.json == PERSONAL_DRIVER_LICENSES_REQUEST
        return PERSONAL_DRIVER_LICENSES_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return {
            'statuses': [
                {
                    'park_id': 'park1',
                    'driver_id': 'driver1',
                    'status': 'busy',
                    'updated_ts': 1634290555458,
                },
            ],
        }

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

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    response = await taxi_fleet_map.get(
        ENDPOINT, headers=HEADERS, params=SERVICE_REQUEST,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    del service_response['order']
    service_response['driver']['status'] = 'busy'

    assert response.status_code == 200
    assert response.json() == service_response


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_driver_status_offline(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        assert request.json == PERSONAL_PHONES_REQUEST
        return PERSONAL_PHONES_RESPONSE

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _driver_licenses_bulk_retrieve(request):
        assert request.json == PERSONAL_DRIVER_LICENSES_REQUEST
        return PERSONAL_DRIVER_LICENSES_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return {
            'statuses': [
                {
                    'park_id': 'park1',
                    'driver_id': 'driver1',
                    'status': 'offline',
                    'updated_ts': 1634290555458,
                    'orders': [{'id': 'order_id', 'status': 'transporting'}],
                },
            ],
        }

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return CANDIDATES_RESPONSE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return DRIVER_ORDERS_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/track')
    def _orderstrack(request):
        assert request.query == DRIVER_ORDERS_TRACK_REQUEST
        return DRIVER_ORDERS_TRACK_RESPONSE

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == FLEET_VEHICLES_REQUEST
        return FLEET_VEHICLES_RESPONSE

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _photos(request):
        assert request.json == UDRIVER_PHOTOS_REQUEST
        return UDRIVER_PHOTOS_RESPONSE

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    response = await taxi_fleet_map.get(
        ENDPOINT, headers=HEADERS, params=SERVICE_REQUEST,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    service_response['driver']['status'] = 'offline'

    assert response.status_code == 200
    assert response.json() == service_response


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_without_position(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        assert request.json == PERSONAL_PHONES_REQUEST
        return PERSONAL_PHONES_RESPONSE

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _driver_licenses_bulk_retrieve(request):
        assert request.json == PERSONAL_DRIVER_LICENSES_REQUEST
        return PERSONAL_DRIVER_LICENSES_RESPONSE

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return DRIVER_STATUS_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return {'drivers': []}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _orders_list(request):
        assert request.json == DRIVER_ORDERS_REQUEST
        return DRIVER_ORDERS_RESPONSE

    @mockserver.json_handler('/driver-orders/v1/parks/orders/track')
    def _orderstrack(request):
        assert request.query == DRIVER_ORDERS_TRACK_REQUEST
        return DRIVER_ORDERS_TRACK_RESPONSE

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

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return FLEET_TRANSACTIONS_API_RESPONSE

    response = await taxi_fleet_map.get(
        ENDPOINT, headers=HEADERS, params=SERVICE_REQUEST,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    del service_response['driver']['payment_methods']
    del service_response['coordinates']

    assert response.status_code == 200
    assert response.json() == service_response


@pytest.mark.now('2021-09-08T17:25:21+00:00')
async def test_without_fallbacks(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-map'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        assert request.json == PERSONAL_PHONES_REQUEST
        return PERSONAL_PHONES_RESPONSE

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _driver_licenses_bulk_retrieve(request):
        assert request.json == PERSONAL_DRIVER_LICENSES_REQUEST
        return PERSONAL_DRIVER_LICENSES_RESPONSE

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == CANDIDATES_REQUEST
        return {'drivers': []}

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _statuses(request):
        assert request.json == DRIVER_STATUS_REQUEST
        return {'statuses': []}

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
        return {'actual_photos': []}

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        assert request.json == FLEET_TRANSACTIONS_API_REQUEST
        return {'driver_profiles': []}

    response = await taxi_fleet_map.get(
        ENDPOINT, headers=HEADERS, params=SERVICE_REQUEST,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    del service_response['order']
    del service_response['driver']['status']
    del service_response['driver']['payment_methods']
    del service_response['driver']['avatar_url']
    del service_response['driver']['balance']
    del service_response['coordinates']

    assert response.status_code == 200
    assert response.json() == service_response
