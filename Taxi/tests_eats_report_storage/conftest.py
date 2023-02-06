# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name

import dataclasses

import pytest

from eats_report_storage_plugins import *  # noqa: F403 F401


@pytest.fixture
def mock_authorizer_200(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(status=200)


@pytest.fixture
def mock_authorizer_400(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'Error'},
        )


@pytest.fixture
def mock_authorizer_wo_details_403(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400, json={'code': '403', 'message': 'Error'},
        )


@pytest.fixture
def mock_authorizer_403(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': 'Error',
                'details': {
                    'permissions': ['permissions'],
                    'place_ids': [111],
                },
            },
        )


@pytest.fixture
def mock_authorizer_500(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(status=500)


def make_rating_response(place_id=1, show_rating=False):
    return {
        'places_rating_info': [
            {
                'place_id': place_id,
                'average_rating': 4.11111,
                'average_rating_delta': -1.55555,
                'user_rating': 4.55555,
                'user_rating_delta': 0.33333,
                'cancel_rating': 5.00000,
                'cancel_rating_delta': 0.00000,
                'show_rating': show_rating,
                'calculated_at': '2021-11-30',
            },
        ],
    }


@dataclasses.dataclass
class PlaceRating:
    place_id: int
    average_rating: float = 4.1
    cancel_rating: float = 4.1
    show_rating: bool = True


def make_place_rating(
        place_id: int, average_rating=4.1, cancel_rating=5.0, show_rating=True,
):
    return PlaceRating(place_id, average_rating, cancel_rating, show_rating)


def make_ratings_response(places=None):
    info = []
    for place in places:
        info.append(
            {
                'place_id': place.place_id,
                'average_rating': place.average_rating,
                'average_rating_delta': -1.55555,
                'user_rating': 4.55555,
                'user_rating_delta': 0.33333,
                'cancel_rating': place.cancel_rating,
                'cancel_rating_delta': 1.70000,
                'show_rating': place.show_rating,
                'calculated_at': '2021-11-30',
            },
        )

    return {'places_rating_info': info}


class RatingResponse:
    def __init__(self):
        self.data = {}

    def set_data(self, data):
        self.data = data


@pytest.fixture
def rating_response():
    return RatingResponse()


@pytest.fixture
def mock_eats_place_rating(mockserver, request, rating_response):
    class Mocks:
        @mockserver.json_handler(
            '/eats-place-rating/eats/v1/eats-place-rating'
            '/v1/places-rating-info',
        )
        @staticmethod
        def _mock_eats_place_rating(request):
            return mockserver.make_response(
                status=200, json=rating_response.data,
            )

    return Mocks()


def exp3_config_multi_places(
        disable_in_suggests: bool = False,
        disable_in_theme_blocks: bool = False,
):
    return pytest.mark.experiments3(
        name='eats_report_storage_multi_places',
        consumers=['eats_report_storage/partner_id'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'disable_in_suggests': disable_in_suggests,
                    'disable_in_theme_blocks': disable_in_theme_blocks,
                },
            },
        ],
        is_config=True,
    )


def exp3_config_promo_types():
    return pytest.mark.experiments3(
        name='eats_report_storage_promo_types',
        consumers=['eats_report_storage/partner_id'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'types': [
                        {'name': 'gift', 'ids': [25]},
                        {'name': 'discount_menu', 'ids': [5]},
                        {'name': 'discount_part', 'ids': [7]},
                        {'name': 'one_plus_one', 'ids': [2]},
                        {'name': 'discount', 'ids': [5, 7]},
                        {'name': 'free_delivery', 'ids': [1001]},
                        {'name': 'plus_happy_hours', 'ids': [1002]},
                        {'name': 'plus_first_orders', 'ids': [1003]},
                    ],
                },
            },
        ],
        is_config=True,
    )


@dataclasses.dataclass
class MetricConfig:
    metric_id: str
    data: dict


def exp3_config_metrics(metrics):
    clauses = []
    for (metric_id, config) in metrics:
        clauses.append(
            {
                'title': metric_id,
                'predicate': {
                    'init': {
                        'arg_name': 'metric_id',
                        'arg_type': 'string',
                        'value': metric_id,
                    },
                    'type': 'eq',
                },
                'value': config,
            },
        )
    return pytest.mark.experiments3(
        name='eats_report_storage_metrics',
        consumers=['eats_report_storage/metrics'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=clauses,
        default_value={
            'data_key': 'default',
            'granularity': [],
            'metric_id': 'default',
            'name': 'Метрика не найдена',
            'periods': [],
            'permissions': [],
        },
        is_config=True,
    )


def exp3_config_widgets(widgets):
    clauses = []
    for (widget_id, config) in widgets:
        clauses.append(
            {
                'title': widget_id,
                'predicate': {
                    'init': {
                        'arg_name': 'widget_id',
                        'arg_type': 'string',
                        'value': widget_id,
                    },
                    'type': 'eq',
                },
                'value': config,
            },
        )
    return pytest.mark.experiments3(
        name='eats_report_storage_widgets',
        consumers=['eats_report_storage/widgets'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=clauses,
        default_value={
            'title': 'Виджет не найден',
            'metrics': [],
            'widget_id': 'default',
            'chart_type': '',
            'description': 'Виджет не найден',
        },
        is_config=True,
    )


def exp3_config_sections(sections):
    return pytest.mark.experiments3(
        name='eats_report_storage_sections',
        consumers=['eats_report_storage/partner_id'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=sections,
        is_config=True,
    )


def exp3_config_switch_flag(switch_flag: str):
    return pytest.mark.experiments3(
        name='eats_report_storage_switch_metrics_config',
        consumers=['eats_report_storage/partner_id'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'switch_flag': switch_flag},
        is_config=True,
    )


@pytest.fixture(name='mock_catalog_storage')
def mock_catalog_storage(mockserver, request):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/'
        + 'eats-catalog-storage/v1/places/retrieve-by-ids',
    )
    async def _mock_catalog_storage(request):
        place_ids = request.json['place_ids']
        return {
            'places': [
                {
                    'id': p,
                    'name': 'place' + str(p),
                    'address': {'city': 'Moscow', 'short': 'address' + str(p)},
                    'type': 'native',
                    'region': {
                        'id': 1,
                        'geobase_ids': [],
                        'time_zone': 'Europe/Moscow',
                    },
                    'revision_id': 1,
                    'updated_at': '2022-04-22T11:44:47.385057+00:00',
                }
                for p in place_ids
            ],
            'not_found_place_ids': [],
        }

    return _mock_catalog_storage
