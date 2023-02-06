import pytest


ENDPOINT = 'fleet/fleet-orders/v1/orders/schedule'


def build_headers(park_id):
    headers = {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }

    return headers


DRIVER0 = {
    'driver_profile': {
        'first_name': 'John',
        'last_name': 'Entwistl',
        'id': 'driver_id0',
    },
}

DRIVER1 = {
    'driver_profile': {
        'first_name': 'John',
        'middle_name': 'Paul',
        'last_name': 'Jones',
        'id': 'driver_id1',
    },
}

DRIVER2 = {
    'driver_profile': {
        'first_name': 'Roger',
        'last_name': 'Waters',
        'id': 'driver_id2',
    },
}

UNIQUES = [
    {
        'data': {'unique_driver_id': 'unique_driver_id1'},
        'park_driver_profile_id': 'park_id1_driver_id1',
    },
]

ACTUAL_PHOTOS = [
    {
        'actual_photo': {
            'portrait_url': 'portrait_url',
            'avatar_url': 'avatar_url',
        },
        'unique_driver_id': 'unique_driver_id1',
    },
]


class ParksContext:
    def __init__(self):
        self.profiles = None
        self.request = None
        self.failing = False

    def set_profiles(self, profiles):
        self.profiles = profiles

    def set_request(self, request):
        self.request = request

    def set_failing(self, failing):
        self.failing = failing


@pytest.fixture(name='mock_parks')
def _mock_personal(mockserver):

    context = ParksContext()

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _driver_profiles_list(request):
        if context.failing:
            return mockserver.make_response('fail', status=500)

        assert request.json == context.request

        return context.profiles

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


def make_profiles_list_request(limit, offset, text=None):
    query = {
        'park': {
            'driver_profile': {'work_status': ['working']},
            'id': 'park_id1',
        },
    }

    if text:
        query['text'] = text

    resp = {
        'fields': {
            'driver_profile': ['id', 'first_name', 'last_name', 'middle_name'],
        },
        'limit': limit,
        'offset': offset,
        'query': query,
        'sort_order': [
            {'direction': 'asc', 'field': 'driver_profile.last_name'},
            {'direction': 'asc', 'field': 'driver_profile.first_name'},
            {'direction': 'asc', 'field': 'driver_profile.middle_name'},
            {'direction': 'desc', 'field': 'driver_profile.hire_date'},
        ],
    }

    return resp


@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
@pytest.mark.parametrize(
    'schedule_params, schedule_response, profiles_request, profiles_response',
    [
        (
            {
                # {'query': {'interval': {'from': '2021-02-09T00:00:00+03:00',
                # 'to': '2021-02-10T00:00:00+03:00'}}}
                'cursor': (
                    'eyJxdWVyeSI6eyJpbnRlcnZhbCI6eyJmcm9tIjoiMjAyMS0wMi0wOFQ'
                    'yMTowMDowMCswMDowMCIsInRvIjoiMjAyMS0wMi0wOVQyMTowMDowMC'
                    'swMDowMCJ9LCJvZmZzZXQiOjB9LCJ2ZXJzaW9uIjoidjEifQ=='
                ),
                'limit': 2,
            },
            {
                'drivers': [
                    {
                        'id': 'driver_id0',
                        'name': 'John  Entwistl',
                        'orders': [],
                    },
                    {
                        'id': 'driver_id1',
                        'name': 'John Paul Jones',
                        'orders': [
                            {
                                'finish_at': '2021-02-09T17:23:00+00:00',
                                'id': 'order1',
                                'start_at': '2021-02-09T16:56:00+00:00',
                                'status': 'created',
                            },
                        ],
                    },
                ],
                # {'query': {'interval': {'from': '2021-02-09T00:00:00+03:00',
                # 'to': '2021-02-10T00:00:00+03:00'}, 'offset': 2}}
                'next_cursor': (
                    'eyJxdWVyeSI6eyJpbnRlcnZhbCI6eyJmcm9tIjoiMjAyMS0wMi0wOFQ'
                    'yMTowMDowMCswMDowMCIsInRvIjoiMjAyMS0wMi0wOVQyMTowMDowMC'
                    'swMDowMCJ9LCJvZmZzZXQiOjJ9LCJ2ZXJzaW9uIjoidjEifQ=='
                ),
            },
            make_profiles_list_request(2, 0),
            {
                'driver_profiles': [DRIVER0, DRIVER1],
                'limit': 2,
                'offset': 0,
                'parks': [{'id': 'park_id1'}],
                'total': 3,
            },
        ),
        (
            {
                # {'query': {'interval': {'from': '2021-02-09T00:00:00+03:00',
                # 'to': '2021-02-10T00:00:00+03:00'}, 'offset': 2}}
                'cursor': (
                    'eyJxdWVyeSI6eyJpbnRlcnZhbCI6eyJmcm9tIjoiMjAyMS0wMi0wOFQ'
                    'yMTowMDowMCswMDowMCIsInRvIjoiMjAyMS0wMi0wOVQyMTowMDowMC'
                    'swMDowMCJ9LCJvZmZzZXQiOjJ9LCJ2ZXJzaW9uIjoidjEifQ=='
                ),
                'limit': 2,
            },
            {
                'drivers': [
                    {
                        'id': 'driver_id2',
                        'name': 'Roger  Waters',
                        'orders': [
                            {
                                'finish_at': '2021-02-09T17:35:00+00:00',
                                'id': 'order5',
                                'start_at': '2021-02-09T17:20:00+00:00',
                                'status': 'completed',
                            },
                            {
                                'finish_at': '2021-02-09T15:50:00+00:00',
                                'id': 'order2',
                                'start_at': '2021-02-09T15:20:00+00:00',
                                'status': 'completed',
                            },
                        ],
                    },
                ],
            },
            make_profiles_list_request(2, 2),
            {
                'driver_profiles': [DRIVER2],
                'limit': 2,
                'offset': 2,
                'parks': [{'id': 'park_id1'}],
                'total': 3,
            },
        ),
        (
            {
                # {'query': {'interval': {'from': '2021-02-09T00:00:00+03:00',
                # 'to': '2021-02-10T00:00:00+03:00'}, 'filter': 'john'}}
                'cursor': (
                    'eyJxdWVyeSI6eyJpbnRlcnZhbCI6eyJmcm9tIjoiMjAyMS0wMi0wOFQ'
                    'yMTowMDowMCswMDowMCIsInRvIjoiMjAyMS0wMi0wOVQyMTowMDowMC'
                    'swMDowMCJ9LCJmaWx0ZXIiOiJqb2huIiwib2Zmc2V0IjowfSwidmVyc'
                    '2lvbiI6InYxIn0='
                ),
                'limit': 1,
            },
            {
                'drivers': [
                    {
                        'id': 'driver_id0',
                        'name': 'John  Entwistl',
                        'orders': [],
                    },
                ],
                'next_cursor': (
                    'eyJxdWVyeSI6eyJpbnRlcnZhbCI6eyJmcm9tIjoiMjAyMS0wMi0wOFQ'
                    'yMTowMDowMCswMDowMCIsInRvIjoiMjAyMS0wMi0wOVQyMTowMDowMC'
                    'swMDowMCJ9LCJmaWx0ZXIiOiJqb2huIiwib2Zmc2V0IjoxfSwidmVyc'
                    '2lvbiI6InYxIn0='
                ),
            },
            make_profiles_list_request(1, 0, 'john'),
            {
                'driver_profiles': [DRIVER0],
                'limit': 1,
                'offset': 0,
                'parks': [{'id': 'park_id1'}],
                'total': 2,
            },
        ),
    ],
)
@pytest.mark.config(FLEET_ORDERS_DEFAULT_ORDER_DURATION_MINUTES=15)
async def test_fleet_orders_schedule_ok(
        taxi_fleet_orders,
        schedule_params,
        schedule_response,
        profiles_request,
        profiles_response,
        mock_parks,
        mock_unique_drivers,
        mock_udriver_photos,
):
    mock_parks.set_request(profiles_request)
    mock_parks.set_profiles(profiles_response)
    mock_unique_drivers.set_uniques(UNIQUES)
    mock_udriver_photos.set_actual_photos(ACTUAL_PHOTOS)

    response = await taxi_fleet_orders.get(
        ENDPOINT, params=schedule_params, headers=build_headers('park_id1'),
    )

    assert response.json() == schedule_response
