# pylint: disable=import-error

from dap_tools.dap import dap_fixture  # noqa: F401 C5521
import pytest

ENDPOINT = '/driver/v1/fleet-orders-guarantee/v1/list'

UNIQUE_DRIVERS = [
    {
        'data': {'unique_driver_id': 'unique_driver_id1'},
        'park_driver_profile_id': 'park_id1_driver_id1',
    },
    {
        'data': {'unique_driver_id': 'unique_driver_id2'},
        'park_driver_profile_id': 'park_id1_driver_id2',
    },
    {
        'data': {'unique_driver_id': 'unique_driver_id3'},
        'park_driver_profile_id': 'park_id1_driver_id3',
    },
    {
        'data': {'unique_driver_id': 'unique_driver_id4'},
        'park_driver_profile_id': 'park_id2_driver_id4',
    },
]

TRANSLATIONS = {
    'preorder': {'en': 'Pre-order', 'ru': 'Предзаказ'},
    'from': {'en': 'From', 'ru': 'Откуда'},
    'to': {'en': 'To', 'ru': 'Куда'},
    'distance': {'en': 'Distance', 'ru': 'Расстояние'},
    'km': {'en': 'km', 'ru': 'км'},
}

PARKS_RESPONSE = {
    'city_id': 'city_id1',
    'country_id': 'country_id1',
    'demo_mode': False,
    'driver_partner_source': 'yandex',
    'id': 'park_id1',
    'is_active': True,
    'is_billing_enabled': False,
    'is_franchising_enabled': False,
    'locale': 'en',
    'login': 'login',
    'name': 'name',
    'tz_offset': 3,
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}


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


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


@pytest.fixture(name='mock_routes')
def _mock_routes(mockserver, load_binary):
    class RoutesContext:
        def __init__(self):
            self.geopoints = []
            self.v2_route_use_count = 0

        def set_geopoints(self, geopoints):
            self.geopoints = geopoints

    context = RoutesContext()

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        context.v2_route_use_count += 1
        rll = _rll_to_array(request.args['rll'])
        assert rll == context.geopoints
        return mockserver.make_response(
            response=load_binary('maps_response.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    return context


@pytest.mark.translations(
    taximeter_backend_fleet_orders_guarantee=TRANSLATIONS,
)
@pytest.mark.now('2021-09-02T20:30:00+03:00')
@pytest.mark.pgsql('fleet_orders_guarantee', files=['orders.sql'])
@pytest.mark.parametrize(
    'interval, park_id, driver_id, accept_language, expected_response, '
    'status_code',
    [
        pytest.param(
            {
                'from': '2021-09-02T20:59:00+03:00',
                'to': '2021-09-02T21:01:00+03:00',
            },
            'park_id1',
            'driver_id1',
            'ru',
            {
                'orders': [
                    {
                        'order_id': 'order_id1',
                        'booked_at': '2021-09-02T18:00:00+00:00',
                        'created_at': '2021-09-02T16:00:00+00:00',
                        'location_from': {
                            'coordinates': [13.388378, 52.519894],
                            'address': 'ул. Ленина',
                        },
                        'locations_to': [
                            {
                                'coordinates': [13.396846, 52.502811],
                                'address': 'ул. Маркса',
                            },
                            {
                                'coordinates': [13.397283, 52.503113],
                                'address': 'ул. Энгельса',
                            },
                        ],
                        'navigation_available': True,
                        'distance': 5491,
                        'estimated_time': 7,
                        'comment': 'Call the apartment and I will come down',
                        'user_interface': {
                            'items': [
                                {
                                    'type': 'default',
                                    'accent': True,
                                    'horizontal_divider_type': 'bottom',
                                    'title': 'Предзаказ',
                                    'reverse': False,
                                },
                                {
                                    'left_icon': {
                                        'icon_type': 'point',
                                        'tint_color': '#e35d45',
                                    },
                                    'reverse': True,
                                    'subtitle': 'ул. Ленина',
                                    'title': 'Откуда',
                                    'horizontal_divider_type': 'bottom_icon',
                                    'type': 'icon_detail',
                                    'detail': '21:00',
                                },
                                {
                                    'left_icon': {'icon_type': 'point'},
                                    'reverse': True,
                                    'subtitle': 'ул. Маркса',
                                    'title': 'Куда',
                                    'horizontal_divider_type': 'bottom_icon',
                                    'type': 'icon_detail',
                                },
                                {
                                    'left_icon': {'icon_type': 'point'},
                                    'reverse': True,
                                    'subtitle': 'ул. Энгельса',
                                    'title': 'Куда',
                                    'horizontal_divider_type': 'bottom_icon',
                                    'type': 'icon_detail',
                                },
                                {
                                    'left_icon': {'icon_type': 'route'},
                                    'reverse': True,
                                    'subtitle': '5.5 км',
                                    'title': 'Расстояние',
                                    'horizontal_divider_type': 'bottom_icon',
                                    'type': 'icon_detail',
                                },
                                {
                                    'title': (
                                        'Call the apartment and '
                                        'I will come down'
                                    ),
                                    'horizontal_divider_type': 'bottom_bold',
                                    'type': 'message_bubble',
                                },
                            ],
                        },
                    },
                ],
            },
            200,
            id='correct_request_ru',
        ),
        pytest.param(
            {
                'from': '2021-09-02T20:59:00+03:00',
                'to': '2021-09-02T21:01:00+03:00',
            },
            'park_id1',
            'driver_id1',
            'en',
            {
                'orders': [
                    {
                        'order_id': 'order_id1',
                        'booked_at': '2021-09-02T18:00:00+00:00',
                        'created_at': '2021-09-02T16:00:00+00:00',
                        'location_from': {
                            'coordinates': [13.388378, 52.519894],
                            'address': 'ул. Ленина',
                        },
                        'locations_to': [
                            {
                                'coordinates': [13.396846, 52.502811],
                                'address': 'ул. Маркса',
                            },
                            {
                                'coordinates': [13.397283, 52.503113],
                                'address': 'ул. Энгельса',
                            },
                        ],
                        'navigation_available': True,
                        'distance': 5491,
                        'estimated_time': 7,
                        'comment': 'Call the apartment and I will come down',
                        'user_interface': {
                            'items': [
                                {
                                    'type': 'default',
                                    'accent': True,
                                    'horizontal_divider_type': 'bottom',
                                    'title': 'Pre-order',
                                    'reverse': False,
                                },
                                {
                                    'left_icon': {
                                        'icon_type': 'point',
                                        'tint_color': '#e35d45',
                                    },
                                    'reverse': True,
                                    'subtitle': 'ул. Ленина',
                                    'title': 'From',
                                    'horizontal_divider_type': 'bottom_icon',
                                    'type': 'icon_detail',
                                    'detail': '21:00',
                                },
                                {
                                    'left_icon': {'icon_type': 'point'},
                                    'reverse': True,
                                    'subtitle': 'ул. Маркса',
                                    'title': 'To',
                                    'horizontal_divider_type': 'bottom_icon',
                                    'type': 'icon_detail',
                                },
                                {
                                    'left_icon': {'icon_type': 'point'},
                                    'reverse': True,
                                    'subtitle': 'ул. Энгельса',
                                    'title': 'To',
                                    'horizontal_divider_type': 'bottom_icon',
                                    'type': 'icon_detail',
                                },
                                {
                                    'left_icon': {'icon_type': 'route'},
                                    'reverse': True,
                                    'subtitle': '5.5 km',
                                    'title': 'Distance',
                                    'horizontal_divider_type': 'bottom_icon',
                                    'type': 'icon_detail',
                                },
                                {
                                    'title': (
                                        'Call the apartment and '
                                        'I will come down'
                                    ),
                                    'horizontal_divider_type': 'bottom_bold',
                                    'type': 'message_bubble',
                                },
                            ],
                        },
                    },
                ],
            },
            200,
            id='correct_request_en',
        ),
        pytest.param(
            {
                'from': '2021-09-02T00:00:00+03:00',
                'to': '2021-09-04T00:00:00+03:00',
            },
            'park_id3',
            'driver_id5',
            'ru',
            {'orders': []},
            200,
            id='incorrect_park_driver_ids',
        ),
        pytest.param(
            {
                'from': '2021-09-04T00:00:00+03:00',
                'to': '2021-09-02T00:00:00+03:00',
            },
            'park_id1',
            'driver_id1',
            'ru',
            {
                'code': '400',
                'message': (
                    '\'interval.from\' must be less than \'interval.to\''
                ),
            },
            400,
            id='interval_to_less_than_from',
        ),
        pytest.param(
            {
                'from': '2021-09-04T00:00:00+03:00',
                'to': '2021-09-04T00:00:00+03:00',
            },
            'park_id1',
            'driver_id1',
            'ru',
            {
                'code': '400',
                'message': (
                    '\'interval.from\' must be less than \'interval.to\''
                ),
            },
            400,
            id='interval_to_equals_from',
        ),
        pytest.param(
            {'from': '', 'to': ''},
            'park_id1',
            'driver_id1',
            'ru',
            {'code': '400'},
            400,
            id='empty_interval',
        ),
    ],
)
async def test_driver_v1_fleet_orders_guarantee_v1_list(
        taxi_fleet_orders_guarantee,
        dap,
        mockserver,
        interval,
        park_id,
        driver_id,
        accept_language,
        expected_response,
        status_code,
        mock_unique_drivers,
        mock_routes,
):
    @mockserver.json_handler('/fleet-parks/v1/parks')
    def _mock_parks(request):
        return PARKS_RESPONSE

    taxi_fleet_orders_guarantee = dap.create_driver_wrapper(
        taxi_fleet_orders_guarantee,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent='Taximeter 9.1 (1234)',
    )

    query = {'interval': interval}

    mock_unique_drivers.set_uniques(UNIQUE_DRIVERS)
    mock_routes.set_geopoints(
        [
            [13.388378, 52.519894],
            [13.396846, 52.502811],
            [13.397283, 52.503113],
        ],
    )

    response = await taxi_fleet_orders_guarantee.post(
        ENDPOINT, json=query, headers={'Accept-Language': accept_language},
    )

    assert response.status_code == status_code

    if 'code' in expected_response and 'message' not in expected_response:
        assert response.json()['code'] == expected_response['code']
    else:
        assert response.json() == expected_response
