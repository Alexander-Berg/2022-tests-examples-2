# pylint: disable=C0302
import pytest


ENDPOINT = 'fleet/fleet-orders/v1/orders/list'

TRANSACTIONS = [
    {
        'id': '964840029',
        'event_at': '2021-07-15T13:33:16.800951+00:00',
        'category_id': 'cash_collected',
        'category_name': 'Cash',
        'amount': '28.9000',
        'currency_code': 'EUR',
        'description': '',
        'created_by': {'identity': 'platform'},
        'driver_profile_id': 'some_driver_id',
        'order_id': 'order_alias_id1',
        'order': {'id': 'order_alias_id1', 'short_id': 845},
    },
    {
        'id': '964850029',
        'event_at': '2021-07-15T13:33:16.728889+00:00',
        'category_id': 'partner_ride_fee',
        'category_name': 'Partner ride fee',
        'amount': '-0.1445',
        'currency_code': 'EUR',
        'description': 'Taxi company fee for order Плац дер Републик, 1',
        'created_by': {'identity': 'platform'},
        'driver_profile_id': 'some_driver_id',
        'order_id': 'order_alias_id1',
        'order': {'id': 'order_alias_id1', 'short_id': 845},
    },
    {
        'id': '964840029',
        'event_at': '2021-07-15T13:33:16.800951+00:00',
        'category_id': 'cash_collected',
        'category_name': 'Cash',
        'amount': '28.9000',
        'currency_code': 'EUR',
        'description': '',
        'created_by': {'identity': 'platform'},
        'driver_profile_id': 'some_driver_id',
        'order_id': 'order_alias_id2',
        'order': {'id': 'order_alias_id2', 'short_id': 845},
    },
    {
        'id': '964850029',
        'event_at': '2021-07-15T13:33:16.728889+00:00',
        'category_id': 'partner_ride_fee',
        'category_name': 'Partner ride fee',
        'amount': '-0.1445',
        'currency_code': 'EUR',
        'description': 'Taxi company fee for order Плац дер Републик, 1',
        'created_by': {'identity': 'platform'},
        'driver_profile_id': 'some_driver_id',
        'order_id': 'order_alias_id2',
        'order': {'id': 'order_alias_id2', 'short_id': 845},
    },
]


def build_headers(park_id):
    headers = {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }

    return headers


class TransactionsContext:
    def __init__(self):
        self.transactions = []

    def set_transactions(self, transactions):
        self.transactions = transactions


@pytest.fixture(name='mock_fleet_transactions_api')
def _mock_fleet_transactions_api(mockserver):

    context = TransactionsContext()

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/orders/transactions/list',
    )
    def _v1_parks_orders_transactions_list(request):
        return {
            'transactions': [
                t
                for t in context.transactions
                if t['order_id']
                in request.json['query']['park']['order']['ids']
            ],
        }

    return context


class FleetParksContext:
    def __init__(self):
        self.parks = []

    def set_parks(self, parks):
        self.parks = parks


class DriverProfilesContext:
    def __init__(self):
        self.profiles = []

    def set_profiles(self, profiles):
        self.profiles = profiles


@pytest.fixture(name='mock_driver_profiles')
def _mock_driver_profiles(mockserver):

    context = DriverProfilesContext()

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _v1_driver_profiles_retrieve(request):
        return {'profiles': [t for t in context.profiles]}

    return context


@pytest.fixture(name='mock_fleet_parks')
def _mock_fleet_parks(mockserver):

    context = FleetParksContext()

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _v1_parks_list(request):
        return {'parks': [t for t in context.parks]}

    return context


class VehiclesContext:
    def __init__(self):
        self.vehicles = []

    def set_vehicles(self, vehicles):
        self.vehicles = vehicles


@pytest.fixture(name='mock_fleet_vehicles')
def _mock_fleet_vehicles(mockserver):

    context = VehiclesContext()

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _v1_vehicles_cache_retrieve(request):
        return {'vehicles': [t for t in context.vehicles]}

    return context


class UniqueDriversContext:
    def __init__(self):
        self.uniques = []

    def set_uniques(self, uniques):
        self.uniques = uniques


@pytest.fixture(name='mock_unique_drivers')
def _mock_unique_drivers(mockserver):

    context = UniqueDriversContext()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_driver_uniques_retrieve_by_profiles(request):
        return {'uniques': [t for t in context.uniques]}

    return context


class DriverPhotosContext:
    def __init__(self):
        self.actual_photos = []

    def set_actual_photos(self, actual_photos):
        self.actual_photos = actual_photos


@pytest.fixture(name='mock_udriver_photos')
def _mock_udriver_photos(mockserver):

    context = DriverPhotosContext()

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _driver_photos_v1_fleet_photos(request):
        return {'actual_photos': [t for t in context.actual_photos]}

    return context


@pytest.fixture(name='mock_fleet_customers')
def _mock_fleet_customers(mockserver):
    @mockserver.json_handler('/fleet-customers/v1/customers/names')
    def _fleet_customers_v1_customers_names(request):
        return {'customers': []}


@pytest.mark.parametrize(
    'first_request, first_response, second_response',
    [
        (
            {
                'cursor': (
                    'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9h'
                    'dCIsImRpciI6ImRlc2MifSwiY3JlYXRlZF9hdCI6eyJmcm9tIjoiMjAy'
                    'MS0wNC0zMFQyMTowMDowMCswMDowMCIsInRvIjoiMjAyMS0wNS0wOVQy'
                    'MTowMDowMCswMDowMCJ9fSwidmVyc2lvbiI6InYxIn0='
                ),
                'limit': 2,
            },
            {
                'orders': [
                    {
                        'id': 'order3',
                        'booked_at': '2021-05-05T17:20:00+00:00',
                        'created_at': '2021-05-05T17:20:00+00:00',
                        'status': 'created',
                        'tariff_class_id': 'econom',
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'is_park_creator': True,
                        'number': 3,
                    },
                    {
                        'id': 'order2',
                        'contractor': {
                            'affiliation': 'another_park',
                            'name': 'another park name',
                        },
                        'created_at': '2021-05-05T17:10:00+00:00',
                        'status': 'driving',
                        'tariff_class_id': 'econom',
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'is_park_creator': True,
                        'number': 2,
                        'vehicle': {
                            'brand': 'brand2',
                            'model': 'model2',
                            'number': 'number2',
                        },
                    },
                ],
                'next_cursor': (
                    'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9h'
                    'dCIsImRpciI6ImRlc2MifSwiY3JlYXRlZF9hdCI6eyJmcm9tIjoiMjAy'
                    'MS0wNC0zMFQyMTowMDowMCswMDowMCIsInRvIjoiMjAyMS0wNS0wOVQy'
                    'MTowMDowMCswMDowMCJ9fSwidmVyc2lvbiI6InYxIiwibGFzdF9pdGVt'
                    'Ijp7Im9sZGVyX3RoYW5fZGF0ZSI6IjIwMjEtMDUtMDVUMTc6MTA6MDAr'
                    'MDA6MDAiLCJvbGRlcl90aGFuX2lkIjoib3JkZXIyIn19'
                ),
            },
            {
                'orders': [
                    {
                        'id': 'order1',
                        'contractor': {
                            'affiliation': 'your_park',
                            'first_name': 'first_name',
                            'id': 'driver_id1',
                            'last_name': 'last_name',
                            'last_photo': 'avatar_url',
                            'middle_name': 'middle_name',
                        },
                        'created_at': '2021-05-05T17:00:00+00:00',
                        'status': 'transporting',
                        'tariff_class_id': 'econom',
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'is_park_creator': True,
                        'price': '28.9000',
                        'park_commission': '0.1445',
                        'number': 1,
                        'vehicle': {
                            'brand': 'brand1',
                            'model': 'model1',
                            'number': 'number1',
                            'id': 'car_id1',
                        },
                    },
                ],
            },
        ),
        (
            {
                'cursor': (
                    'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9h'
                    'dCIsImRpciI6ImFzYyJ9LCJjcmVhdGVkX2F0Ijp7fSwiYm9va2VkX2F0'
                    'Ijp7fX0sInZlcnNpb24iOiJ2MSJ9'
                ),
                'limit': 2,
            },
            {
                'orders': [
                    {
                        'id': 'order1',
                        'contractor': {
                            'affiliation': 'your_park',
                            'first_name': 'first_name',
                            'id': 'driver_id1',
                            'last_name': 'last_name',
                            'last_photo': 'avatar_url',
                            'middle_name': 'middle_name',
                        },
                        'created_at': '2021-05-05T17:00:00+00:00',
                        'status': 'transporting',
                        'tariff_class_id': 'econom',
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'is_park_creator': True,
                        'price': '28.9000',
                        'park_commission': '0.1445',
                        'number': 1,
                        'vehicle': {
                            'brand': 'brand1',
                            'model': 'model1',
                            'number': 'number1',
                            'id': 'car_id1',
                        },
                    },
                    {
                        'id': 'order2',
                        'contractor': {
                            'affiliation': 'another_park',
                            'name': 'another park name',
                        },
                        'created_at': '2021-05-05T17:10:00+00:00',
                        'status': 'driving',
                        'tariff_class_id': 'econom',
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'is_park_creator': True,
                        'number': 2,
                        'vehicle': {
                            'brand': 'brand2',
                            'model': 'model2',
                            'number': 'number2',
                        },
                    },
                ],
                'next_cursor': (
                    'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9h'
                    'dCIsImRpciI6ImFzYyJ9LCJjcmVhdGVkX2F0Ijp7fSwiYm9va2VkX2F0'
                    'Ijp7fX0sInZlcnNpb24iOiJ2MSIsImxhc3RfaXRlbSI6eyJvbGRlcl90'
                    'aGFuX2RhdGUiOiIyMDIxLTA1LTA1VDE3OjEwOjAwKzAwOjAwIiwib2xk'
                    'ZXJfdGhhbl9pZCI6Im9yZGVyMiJ9fQ=='
                ),
            },
            {
                'orders': [
                    {
                        'id': 'order3',
                        'booked_at': '2021-05-05T17:20:00+00:00',
                        'created_at': '2021-05-05T17:20:00+00:00',
                        'status': 'created',
                        'tariff_class_id': 'econom',
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'is_park_creator': True,
                        'number': 3,
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('fleet_orders', files=['orders1.sql'])
async def test_fleet_orders_two_requests_with_cursors(
        taxi_fleet_orders,
        mock_fleet_transactions_api,
        mock_fleet_vehicles,
        mock_fleet_parks,
        mock_driver_profiles,
        mock_unique_drivers,
        mock_udriver_photos,
        mock_fleet_customers,
        first_request,
        first_response,
        second_response,
):
    mock_fleet_transactions_api.set_transactions(TRANSACTIONS)

    vehicles = [
        {
            'data': {
                'car_id': 'car_id1',
                'brand': 'brand1',
                'model': 'model1',
                'number': 'number1',
            },
            'park_id_car_id': 'park_id1_car_id1',
        },
        {
            'data': {
                'car_id': 'car_id2',
                'brand': 'brand2',
                'model': 'model2',
                'number': 'number2',
            },
            'park_id_car_id': 'park_id2_car_id2',
        },
    ]
    mock_fleet_vehicles.set_vehicles(vehicles)

    parks = [
        {
            'id': 'park_id2',
            'login': 'login',
            'name': 'another park name',
            'is_active': True,
            'city_id': 'city',
            'locale': 'locale',
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'country_id': 'country',
            'demo_mode': False,
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        },
    ]
    mock_fleet_parks.set_parks(parks)

    driver_profiles = [
        {
            'data': {
                'full_name': {
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'middle_name': 'middle_name',
                },
                'uuid': 'driver_id1',
            },
            'park_driver_profile_id': 'park_id1_driver_id1',
        },
    ]
    mock_driver_profiles.set_profiles(driver_profiles)

    uniques = [
        {
            'data': {'unique_driver_id': 'unique_driver_id1'},
            'park_driver_profile_id': 'park_id1_driver_id1',
        },
    ]
    mock_unique_drivers.set_uniques(uniques)

    actual_photos = [
        {
            'actual_photo': {
                'portrait_url': 'portrait_url',
                'avatar_url': 'avatar_url',
            },
            'unique_driver_id': 'unique_driver_id1',
        },
    ]
    mock_udriver_photos.set_actual_photos(actual_photos)

    params = first_request

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id1'),
    )

    expected_json = first_response
    assert response.status_code == 200
    assert response.json() == expected_json

    params = {'cursor': response.json()['next_cursor'], 'limit': 2}

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id1'),
    )

    expected_json = second_response
    assert response.status_code == 200
    assert response.json() == expected_json


@pytest.mark.pgsql('fleet_orders', files=['orders1.sql'])
async def test_fleet_orders_by_number(
        taxi_fleet_orders,
        mock_fleet_transactions_api,
        mock_fleet_vehicles,
        mock_fleet_parks,
        mock_fleet_customers,
):
    mock_fleet_transactions_api.set_transactions(TRANSACTIONS)

    vehicles = [
        {
            'data': {
                'car_id': 'car_id2',
                'brand': 'brand2',
                'model': 'model2',
                'number': 'number2',
            },
            'park_id_car_id': 'park_id2_car_id2',
        },
    ]
    mock_fleet_vehicles.set_vehicles(vehicles)

    parks = [
        {
            'id': 'park_id2',
            'login': 'login',
            'name': 'another park name',
            'is_active': True,
            'city_id': 'city',
            'locale': 'locale',
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'country_id': 'country',
            'demo_mode': False,
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        },
    ]
    mock_fleet_parks.set_parks(parks)

    params = {
        'cursor': (
            'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hdC'
            'IsImRpciI6ImRlc2MifSwibnVtYmVyIjoyfSwidmVyc2lvbiI6InYxIn0='
        ),
    }

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id1'),
    )

    expected_json = {
        'orders': [
            {
                'id': 'order2',
                'contractor': {
                    'affiliation': 'another_park',
                    'name': 'another park name',
                },
                'created_at': '2021-05-05T17:10:00+00:00',
                'status': 'driving',
                'tariff_class_id': 'econom',
                'route': ['address_A', 'address_B1', 'address_B2'],
                'is_park_creator': True,
                'number': 2,
                'vehicle': {
                    'brand': 'brand2',
                    'model': 'model2',
                    'number': 'number2',
                },
            },
        ],
    }
    assert response.status_code == 200
    assert response.json() == expected_json


@pytest.mark.parametrize(
    'cursor,expected',
    [
        (
            (
                'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hdCIsI'
                'mRpciI6ImRlc2MifSwiY3JlYXRlZF9hdCI6eyJmcm9tIjoiMjAyMS0wNS0wNV'
                'QxNzoxMDowMCswMDowMCIsInRvIjoiMjAyMS0wNS0wNVQxNzoyMDowMCswMDo'
                'wMCJ9fSwidmVyc2lvbiI6InYxIn0=',
            ),
            {
                'orders': [
                    {
                        'id': 'order2',
                        'contractor': {
                            'affiliation': 'another_park',
                            'name': 'another park name',
                        },
                        'created_at': '2021-05-05T17:10:00+00:00',
                        'status': 'driving',
                        'tariff_class_id': 'econom',
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'is_park_creator': True,
                        'number': 2,
                        'vehicle': {
                            'brand': 'brand2',
                            'model': 'model2',
                            'number': 'number2',
                        },
                    },
                ],
            },
        ),
        (
            (
                'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hdCIsI'
                'mRpciI6ImFzYyJ9LCJjcmVhdGVkX2F0Ijp7ImZyb20iOiIyMDIxLTA1LTA1VD'
                'E3OjEwOjAwKzAwOjAwIn19LCJ2ZXJzaW9uIjoidjEifQ==',
            ),
            {
                'next_cursor': (
                    'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hd'
                    'CIsImRpciI6ImFzYyJ9LCJjcmVhdGVkX2F0Ijp7ImZyb20iOiIyMDIxLT'
                    'A1LTA1VDE3OjEwOjAwKzAwOjAwIn19LCJ2ZXJzaW9uIjoidjEiLCJsYXN'
                    '0X2l0ZW0iOnsib2xkZXJfdGhhbl9kYXRlIjoiMjAyMS0wNS0wNVQxNzox'
                    'MDowMCswMDowMCIsIm9sZGVyX3RoYW5faWQiOiJvcmRlcjIifX0='
                ),
                'orders': [
                    {
                        'id': 'order2',
                        'contractor': {
                            'affiliation': 'another_park',
                            'name': 'another park name',
                        },
                        'created_at': '2021-05-05T17:10:00+00:00',
                        'status': 'driving',
                        'tariff_class_id': 'econom',
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'is_park_creator': True,
                        'number': 2,
                        'vehicle': {
                            'brand': 'brand2',
                            'model': 'model2',
                            'number': 'number2',
                        },
                    },
                ],
            },
        ),
        (
            (
                'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hdCIsI'
                'mRpciI6ImRlc2MifSwiY3JlYXRlZF9hdCI6eyJ0byI6IjIwMjEtMDUtMDVUMT'
                'c6MTE6MDArMDA6MDAifX0sInZlcnNpb24iOiJ2MSJ9',
            ),
            {
                'next_cursor': (
                    'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hd'
                    'CIsImRpciI6ImRlc2MifSwiY3JlYXRlZF9hdCI6eyJ0byI6IjIwMjEtMD'
                    'UtMDVUMTc6MTE6MDArMDA6MDAifX0sInZlcnNpb24iOiJ2MSIsImxhc3R'
                    'faXRlbSI6eyJvbGRlcl90aGFuX2RhdGUiOiIyMDIxLTA1LTA1VDE3OjEw'
                    'OjAwKzAwOjAwIiwib2xkZXJfdGhhbl9pZCI6Im9yZGVyMiJ9fQ=='
                ),
                'orders': [
                    {
                        'id': 'order2',
                        'contractor': {
                            'affiliation': 'another_park',
                            'name': 'another park name',
                        },
                        'created_at': '2021-05-05T17:10:00+00:00',
                        'status': 'driving',
                        'tariff_class_id': 'econom',
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'is_park_creator': True,
                        'number': 2,
                        'vehicle': {
                            'brand': 'brand2',
                            'model': 'model2',
                            'number': 'number2',
                        },
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('fleet_orders', files=['orders1.sql'])
async def test_fleet_orders_by_created_at(
        taxi_fleet_orders,
        mock_fleet_transactions_api,
        mock_fleet_vehicles,
        mock_fleet_parks,
        mock_fleet_customers,
        cursor,
        expected,
):
    mock_fleet_transactions_api.set_transactions(TRANSACTIONS)

    vehicles = [
        {
            'data': {
                'car_id': 'car_id2',
                'brand': 'brand2',
                'model': 'model2',
                'number': 'number2',
            },
            'park_id_car_id': 'park_id2_car_id2',
        },
    ]
    mock_fleet_vehicles.set_vehicles(vehicles)

    parks = [
        {
            'id': 'park_id2',
            'login': 'login',
            'name': 'another park name',
            'is_active': True,
            'city_id': 'city',
            'locale': 'locale',
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'country_id': 'country',
            'demo_mode': False,
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        },
    ]
    mock_fleet_parks.set_parks(parks)

    params = {'cursor': cursor, 'limit': 1}

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id1'),
    )

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.pgsql('fleet_orders', files=['orders1.sql'])
async def test_fleet_orders_by_vehicle_id(
        taxi_fleet_orders,
        mock_fleet_transactions_api,
        mock_fleet_vehicles,
        mock_fleet_parks,
        mock_fleet_customers,
):
    mock_fleet_transactions_api.set_transactions(TRANSACTIONS)

    vehicles = [
        {
            'data': {
                'car_id': 'car_id2',
                'brand': 'brand2',
                'model': 'model2',
                'number': 'number2',
            },
            'park_id_car_id': 'park_id2_car_id2',
        },
    ]
    mock_fleet_vehicles.set_vehicles(vehicles)

    parks = [
        {
            'id': 'park_id2',
            'login': 'login',
            'name': 'another park name',
            'is_active': True,
            'city_id': 'city',
            'locale': 'locale',
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'country_id': 'country',
            'demo_mode': False,
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        },
    ]
    mock_fleet_parks.set_parks(parks)

    params = {
        'cursor': (
            'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hdCIsImRpc'
            'iI6ImRlc2MifSwiY3JlYXRlZF9hdCI6eyJmcm9tIjoiMjAyMS0wNC0zMFQyMTowMD'
            'owMCswMDowMCIsInRvIjoiMjAyMS0wNS0xMFQyMTowMDowMCswMDowMCJ9LCJ2ZWh'
            'pY2xlX2lkIjoiY2FyX2lkMiJ9LCJ2ZXJzaW9uIjoidjEifQ=='
        ),
    }

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id1'),
    )

    expected_json = {
        'orders': [
            {
                'id': 'order2',
                'contractor': {
                    'affiliation': 'another_park',
                    'name': 'another park name',
                },
                'created_at': '2021-05-05T17:10:00+00:00',
                'status': 'driving',
                'tariff_class_id': 'econom',
                'route': ['address_A', 'address_B1', 'address_B2'],
                'is_park_creator': True,
                'number': 2,
                'vehicle': {
                    'brand': 'brand2',
                    'model': 'model2',
                    'number': 'number2',
                },
            },
        ],
    }

    assert response.status_code == 200
    assert response.json() == expected_json


@pytest.mark.pgsql('fleet_orders', files=['orders1.sql'])
async def test_fleet_orders_by_driver_id(
        taxi_fleet_orders,
        mock_fleet_transactions_api,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_unique_drivers,
        mock_udriver_photos,
        mock_fleet_customers,
):
    mock_fleet_transactions_api.set_transactions(TRANSACTIONS)

    vehicles = [
        {
            'data': {
                'car_id': 'car_id1',
                'brand': 'brand1',
                'model': 'model1',
                'number': 'number1',
            },
            'park_id_car_id': 'park_id1_car_id1',
        },
        {
            'data': {
                'car_id': 'car_id2',
                'brand': 'brand2',
                'model': 'model2',
                'number': 'number2',
            },
            'park_id_car_id': 'park_id2_car_id2',
        },
    ]
    mock_fleet_vehicles.set_vehicles(vehicles)

    driver_profiles = [
        {
            'data': {
                'full_name': {
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'middle_name': 'middle_name',
                },
                'uuid': 'driver_id1',
            },
            'park_driver_profile_id': 'park_id1_driver_id1',
        },
    ]
    mock_driver_profiles.set_profiles(driver_profiles)

    uniques = [
        {
            'data': {'unique_driver_id': 'unique_driver_id1'},
            'park_driver_profile_id': 'park_id1_driver_id1',
        },
    ]
    mock_unique_drivers.set_uniques(uniques)

    actual_photos = [
        {
            'actual_photo': {
                'portrait_url': 'portrait_url',
                'avatar_url': 'avatar_url',
            },
            'unique_driver_id': 'unique_driver_id1',
        },
    ]
    mock_udriver_photos.set_actual_photos(actual_photos)

    params = {
        'cursor': (
            'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hdCIsImRpc'
            'iI6ImRlc2MifSwiY3JlYXRlZF9hdCI6eyJmcm9tIjoiMjAyMS0wNC0zMFQyMTowMD'
            'owMCswMDowMCIsInRvIjoiMjAyMS0wNS0wOVQyMTowMDowMCswMDowMCJ9LCJkcml'
            '2ZXJfaWQiOiJkcml2ZXJfaWQxIn0sInZlcnNpb24iOiJ2MSJ9'
        ),
    }

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id1'),
    )

    expected_json = {
        'orders': [
            {
                'id': 'order1',
                'contractor': {
                    'affiliation': 'your_park',
                    'first_name': 'first_name',
                    'id': 'driver_id1',
                    'last_name': 'last_name',
                    'last_photo': 'avatar_url',
                    'middle_name': 'middle_name',
                },
                'created_at': '2021-05-05T17:00:00+00:00',
                'status': 'transporting',
                'tariff_class_id': 'econom',
                'route': ['address_A', 'address_B1', 'address_B2'],
                'is_park_creator': True,
                'price': '28.9000',
                'park_commission': '0.1445',
                'number': 1,
                'vehicle': {
                    'brand': 'brand1',
                    'model': 'model1',
                    'number': 'number1',
                    'id': 'car_id1',
                },
            },
        ],
    }
    assert response.status_code == 200
    assert response.json() == expected_json


@pytest.mark.pgsql('fleet_orders', files=['orders1.sql'])
async def test_fleet_orders_get_status_rename(
        taxi_fleet_orders,
        mock_fleet_transactions_api,
        mock_fleet_vehicles,
        mock_fleet_parks,
        mock_driver_profiles,
        mock_unique_drivers,
        mock_udriver_photos,
        mock_fleet_customers,
):
    params = {
        'cursor': (
            'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hdCIsImRpc'
            'iI6ImRlc2MifSwiY3JlYXRlZF9hdCI6eyJmcm9tIjoiMjAyMS0wNC0zMFQyMTowMD'
            'owMCswMDowMCIsInRvIjoiMjAyMS0wNS0wOVQyMTowMDowMCswMDowMCJ9fSwidmV'
            'yc2lvbiI6InYxIn0='
        ),
        'limit': 3,
    }

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id1'),
    )

    expected_json = {
        'orders': [
            {
                'id': 'order3',
                'booked_at': '2021-05-05T17:20:00+00:00',
                'created_at': '2021-05-05T17:20:00+00:00',
                'status': 'created',
                'tariff_class_id': 'econom',
                'route': ['address_A', 'address_B1', 'address_B2'],
                'is_park_creator': True,
                'number': 3,
            },
            {
                'id': 'order2',
                'created_at': '2021-05-05T17:10:00+00:00',
                'status': 'driving',
                'tariff_class_id': 'econom',
                'route': ['address_A', 'address_B1', 'address_B2'],
                'is_park_creator': True,
                'number': 2,
            },
            {
                'id': 'order1',
                'created_at': '2021-05-05T17:00:00+00:00',
                'status': 'transporting',
                'tariff_class_id': 'econom',
                'route': ['address_A', 'address_B1', 'address_B2'],
                'is_park_creator': True,
                'number': 1,
            },
        ],
    }

    assert response.status_code == 200
    assert response.json() == expected_json


VEHICLES_RESPONSE = [
    {
        'data': {
            'car_id': 'car_id1',
            'brand': 'brand1',
            'model': 'model1',
            'number': 'number1',
        },
        'park_id_car_id': 'park_id1_car_id1',
    },
    {
        'data': {
            'car_id': 'car_id2',
            'brand': 'brand2',
            'model': 'model2',
            'number': 'number2',
        },
        'park_id_car_id': 'park_id2_car_id2',
    },
]

DRIVER_PROFILES_RESPONSE = [
    {
        'data': {
            'full_name': {
                'first_name': 'first_name',
                'last_name': 'last_name',
                'middle_name': 'middle_name',
            },
            'uuid': 'driver_id1',
        },
        'park_driver_profile_id': 'park_id1_driver_id1',
    },
]

PARKS_RESPONSE = [
    {
        'id': 'park_id2',
        'login': 'login',
        'name': 'another park name',
        'is_active': True,
        'city_id': 'city',
        'locale': 'locale',
        'is_billing_enabled': True,
        'is_franchising_enabled': False,
        'country_id': 'country',
        'demo_mode': False,
        'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
    },
]

UNIQUES_RESPONSE = [
    {
        'data': {'unique_driver_id': 'unique_driver_id1'},
        'park_driver_profile_id': 'park_id1_driver_id1',
    },
]

ACTUAL_PHOTOS_RESPONSE = [
    {
        'actual_photo': {
            'portrait_url': 'portrait_url',
            'avatar_url': 'avatar_url',
        },
        'unique_driver_id': 'unique_driver_id1',
    },
]


@pytest.mark.pgsql('fleet_orders', files=['orders3.sql'])
@pytest.mark.parametrize(
    'cursor,expected',
    [
        (
            (
                'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hdCIsI'
                'mRpciI6ImRlc2MifSwiY3JlYXRlZF9hdCI6eyJmcm9tIjoiMjAyMS0wNC0zMF'
                'QyMTowMDowMCswMDowMCIsInRvIjoiMjAyMS0wNS0wOVQyMTowMDowMCswMDo'
                'wMCJ9LCJzdGF0dXNlcyI6WyJ0cmFuc3BvcnRpbmciLCJkcml2aW5nIl19LCJ2'
                'ZXJzaW9uIjoidjEifQ==',
            ),
            {
                'orders': [
                    {
                        'id': 'order2',
                        'contractor': {
                            'affiliation': 'another_park',
                            'name': 'another park name',
                        },
                        'created_at': '2021-05-05T17:10:00+00:00',
                        'status': 'driving',
                        'tariff_class_id': 'econom',
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'is_park_creator': True,
                        'number': 2,
                        'vehicle': {
                            'brand': 'brand2',
                            'model': 'model2',
                            'number': 'number2',
                        },
                    },
                    {
                        'id': 'order1',
                        'contractor': {
                            'affiliation': 'your_park',
                            'first_name': 'first_name',
                            'id': 'driver_id1',
                            'last_name': 'last_name',
                            'last_photo': 'avatar_url',
                            'middle_name': 'middle_name',
                        },
                        'created_at': '2021-05-05T17:00:00+00:00',
                        'status': 'transporting',
                        'tariff_class_id': 'econom',
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'is_park_creator': True,
                        'price': '28.9000',
                        'park_commission': '0.1445',
                        'number': 1,
                        'vehicle': {
                            'brand': 'brand1',
                            'model': 'model1',
                            'number': 'number1',
                            'id': 'car_id1',
                        },
                    },
                ],
            },
        ),
        (
            (
                'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hdCIs'
                'ImRpciI6ImRlc2MifSwiY3JlYXRlZF9hdCI6eyJmcm9tIjoiMjAyMS0wNC0z'
                'MFQyMTowMDowMCswMDowMCIsInRvIjoiMjAyMS0wNS0wOVQyMTowMDowMCsw'
                'MDowMCJ9LCJzdGF0dXNlcyI6WyJjcmVhdGVkIl19LCJ2ZXJzaW9uIjoidjEi'
                'fQ=='
            ),
            {
                'orders': [
                    {
                        'created_at': '2021-05-05T17:23:00+00:00',
                        'id': 'order4',
                        'is_park_creator': True,
                        'number': 4,
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'status': 'created',
                        'tariff_class_id': 'econom',
                    },
                ],
            },
        ),
        (
            (
                'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hdCIsI'
                'mRpciI6ImRlc2MifSwiY3JlYXRlZF9hdCI6eyJmcm9tIjoiMjAyMS0wNC0zMF'
                'QyMTowMDowMCswMDowMCIsInRvIjoiMjAyMS0wNS0wOVQyMTowMDowMCswMDo'
                'wMCJ9LCJzdGF0dXNlcyI6WyJjYW5jZWxlZF9ieV9kcml2ZXIiXX0sInZlcnNp'
                'b24iOiJ2MSJ9'
            ),
            {
                'orders': [
                    {
                        'id': 'order3',
                        'created_at': '2021-05-05T17:20:00+00:00',
                        'is_park_creator': True,
                        'number': 3,
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'status': 'created',
                        'tariff_class_id': 'econom',
                    },
                ],
            },
        ),
    ],
)
async def test_fleet_orders_by_statuses(
        taxi_fleet_orders,
        mock_fleet_transactions_api,
        mock_fleet_vehicles,
        mock_fleet_parks,
        mock_driver_profiles,
        mock_unique_drivers,
        mock_udriver_photos,
        mock_fleet_customers,
        cursor,
        expected,
):
    mock_fleet_transactions_api.set_transactions(TRANSACTIONS)
    mock_fleet_vehicles.set_vehicles(VEHICLES_RESPONSE)
    mock_driver_profiles.set_profiles(DRIVER_PROFILES_RESPONSE)
    mock_fleet_parks.set_parks(PARKS_RESPONSE)
    mock_unique_drivers.set_uniques(UNIQUES_RESPONSE)
    mock_udriver_photos.set_actual_photos(ACTUAL_PHOTOS_RESPONSE)

    params = {'cursor': cursor}

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id1'),
    )

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.pgsql('fleet_orders', files=['orders4.sql'])
async def test_fleet_orders_scheduled(
        taxi_fleet_orders,
        mock_fleet_transactions_api,
        mock_fleet_vehicles,
        mock_fleet_parks,
        mock_driver_profiles,
        mock_unique_drivers,
        mock_udriver_photos,
        mock_fleet_customers,
):
    mock_fleet_transactions_api.set_transactions(TRANSACTIONS)
    mock_fleet_vehicles.set_vehicles(VEHICLES_RESPONSE)
    mock_driver_profiles.set_profiles(DRIVER_PROFILES_RESPONSE)
    mock_fleet_parks.set_parks(PARKS_RESPONSE)
    mock_unique_drivers.set_uniques(UNIQUES_RESPONSE)
    mock_udriver_photos.set_actual_photos(ACTUAL_PHOTOS_RESPONSE)

    # { "query": { "scheduled": true, "sort": { "dir": "desc",
    # "field": "order_created_at" } } }
    params = {
        'cursor': (
            'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hdCIs'
            'ImRpciI6ImRlc2MifSwic2NoZWR1bGVkIjp0cnVlfSwidmVyc2lvbiI6InYx'
            'In0='
        ),
    }

    expected = {
        'orders': [
            {
                'contractor': {
                    'affiliation': 'your_park',
                    'first_name': 'first_name',
                    'id': 'driver_id1',
                    'last_name': 'last_name',
                    'last_photo': 'avatar_url',
                    'middle_name': 'middle_name',
                },
                'created_at': '2021-05-05T17:00:00+00:00',
                'id': 'order1',
                'is_park_creator': True,
                'number': 1,
                'park_commission': '0.1445',
                'price': '28.9000',
                'route': ['address_A', 'address_B1', 'address_B2'],
                'status': 'transporting',
                'tariff_class_id': 'econom',
                'vehicle': {
                    'brand': 'brand1',
                    'id': 'car_id1',
                    'model': 'model1',
                    'number': 'number1',
                },
            },
        ],
    }

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id1'),
    )

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.pgsql('fleet_orders', files=['orders5.sql'])
@pytest.mark.parametrize(
    'cursor,expected',
    [
        (
            (
                'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfYm9va2VkX2F0IiwiZ'
                'GlyIjoiZGVzYyJ9LCJjdXN0b21lcl9waG9uZV9udW1iZXIiOiIrNDkxMTExMj'
                'IyMjIyIn0sInZlcnNpb24iOiJ2MSJ9',
            ),
            {
                'orders': [
                    {
                        'booked_at': '2021-02-08T01:00:00+00:00',
                        'created_at': '2021-02-08T12:00:00+00:00',
                        'id': 'order_id3',
                        'is_park_creator': False,
                        'number': 3,
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'status': 'driving',
                        'tariff_class_id': 'business',
                    },
                    {
                        'booked_at': '2021-02-07T23:00:00+00:00',
                        'created_at': '2021-02-08T12:00:00+00:00',
                        'id': 'order_id1',
                        'is_park_creator': False,
                        'number': 1,
                        'route': ['address_A', 'address_B1', 'address_B2'],
                        'status': 'driving',
                        'tariff_class_id': 'business',
                    },
                ],
            },
        ),
        (
            (
                'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfYm9va2VkX2F0IiwiZ'
                'GlyIjoiZGVzYyJ9LCJjdXN0b21lcl9waG9uZV9udW1iZXIiOiIrMTIzIn0sIn'
                'ZlcnNpb24iOiJ2MSJ9'
            ),
            {'orders': []},
        ),
    ],
)
async def test_fleet_orders_customer_phone_number(
        taxi_fleet_orders, mockserver, cursor, expected,
):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_v1_phones_find(request):
        if request.json['value'] == '+491111222222':
            return {'id': 'phone_id1', 'value': request.json['value']}

        return mockserver.make_response(
            json={'code': 'code', 'message': 'message'}, status=404,
        )

    params = {'cursor': cursor}

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id1'),
    )

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.pgsql('fleet_orders', files=['orders5.sql'])
async def test_fleet_orders_is_park_creator(taxi_fleet_orders):
    params = {
        'cursor': (
            'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfYm9va2VkX2F0IiwiZGl'
            'yIjoiYXNjIn0sImlzX3BhcmtfY3JlYXRvciI6ZmFsc2V9LCJ2ZXJzaW9uIjoidj'
            'EifQ=='
        ),
    }

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id1'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'orders': [
            {
                'booked_at': '2021-02-07T23:00:00+00:00',
                'created_at': '2021-02-08T12:00:00+00:00',
                'id': 'order_id1',
                'is_park_creator': False,
                'number': 1,
                'route': ['address_A', 'address_B1', 'address_B2'],
                'status': 'driving',
                'tariff_class_id': 'business',
            },
            {
                'booked_at': '2021-02-08T01:00:00+00:00',
                'created_at': '2021-02-08T12:00:00+00:00',
                'id': 'order_id3',
                'is_park_creator': False,
                'number': 3,
                'route': ['address_A', 'address_B1', 'address_B2'],
                'status': 'driving',
                'tariff_class_id': 'business',
            },
        ],
    }


@pytest.mark.pgsql('fleet_orders', files=['orders5.sql'])
async def test_fleet_orders_booked_at(taxi_fleet_orders, mock_fleet_customers):
    params = {
        'cursor': (
            'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfYm9va2VkX2F0IiwiZGl'
            'yIjoiZGVzYyJ9LCJib29rZWRfYXQiOnsiZnJvbSI6IjIwMjEtMDItMDhUMjM6MD'
            'A6MDArMDA6MDAiLCJ0byI6IjIwMjEtMDItMDlUMjM6MDA6MDArMDA6MDAifX0sI'
            'nZlcnNpb24iOiJ2MSJ9'
        ),
    }

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id1'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'orders': [
            {
                'booked_at': '2021-02-09T02:00:00+00:00',
                'created_at': '2021-02-08T12:00:00+00:00',
                'id': 'order_id4',
                'is_park_creator': False,
                'number': 4,
                'route': ['address_A', 'address_B1', 'address_B2'],
                'status': 'driving',
                'tariff_class_id': 'business',
            },
            {
                'booked_at': '2021-02-09T00:00:00+00:00',
                'created_at': '2021-02-08T12:00:00+00:00',
                'id': 'order_id2',
                'is_park_creator': False,
                'number': 2,
                'route': ['address_A', 'address_B1', 'address_B2'],
                'status': 'driving',
                'tariff_class_id': 'business',
            },
        ],
    }


@pytest.mark.pgsql('fleet_orders', files=['orders6.sql'])
async def test_fleet_orders_customers(taxi_fleet_orders, mockserver):
    @mockserver.json_handler('/fleet-customers/v1/customers/names')
    def _fleet_customers_v1_customers_names(request):
        assert request.json == {
            'personal_phone_ids': [
                'valid_phone_id2',
                'valid_phone_id1',
                'valid_phone_id',
            ],
        }
        return {
            'customers': [
                {
                    'id': 'valid_id',
                    'personal_phone_id': 'valid_phone_id',
                    'name': 'valid_name',
                },
                {'id': 'valid_id1', 'personal_phone_id': 'valid_phone_id1'},
                {'id': 'valid_id1', 'personal_phone_id': 'valid_phone_id1'},
            ],
        }

    params = {
        'cursor': (
            'eyJxdWVyeSI6eyJzb3J0Ijp7ImZpZWxkIjoib3JkZXJfY3JlYXRlZF9hdCIsImR'
            'pciI6ImRlc2MifX0sInZlcnNpb24iOiJ2MSJ9'
        ),
    }

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=params, headers=build_headers('park_id'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'orders': [
            {
                'booked_at': '2021-02-07T23:00:00+00:00',
                'created_at': '2021-02-08T12:00:00+00:00',
                'id': 'not_creator_order_id',
                'is_park_creator': False,
                'number': 4,
                'route': ['address_A', 'address_B1', 'address_B2'],
                'status': 'driving',
                'tariff_class_id': 'business',
            },
            {
                'booked_at': '2021-02-07T23:00:00+00:00',
                'created_at': '2021-02-08T12:00:00+00:00',
                'customer': {'id': 'valid_id', 'name': 'valid_name'},
                'id': 'valid_order_id',
                'is_park_creator': True,
                'number': 1,
                'route': ['address_A', 'address_B1', 'address_B2'],
                'status': 'driving',
                'tariff_class_id': 'business',
            },
            {
                'booked_at': '2021-02-07T23:00:00+00:00',
                'created_at': '2021-02-08T12:00:00+00:00',
                'customer': {'id': 'valid_id1'},
                'id': 'valid_order_id1',
                'is_park_creator': True,
                'number': 2,
                'route': ['address_A', 'address_B1', 'address_B2'],
                'status': 'driving',
                'tariff_class_id': 'business',
            },
            {
                'booked_at': '2021-02-07T23:00:00+00:00',
                'created_at': '2021-02-08T12:00:00+00:00',
                'id': 'valid_order_id2',
                'is_park_creator': True,
                'number': 3,
                'route': ['address_A', 'address_B1', 'address_B2'],
                'status': 'driving',
                'tariff_class_id': 'business',
            },
            {
                'booked_at': '2021-02-07T23:00:00+00:00',
                'created_at': '2021-02-08T12:00:00+00:00',
                'id': 'phone_null_order_id',
                'is_park_creator': True,
                'number': 5,
                'route': ['address_A', 'address_B1', 'address_B2'],
                'status': 'expired',
                'tariff_class_id': 'business',
            },
        ],
    }
