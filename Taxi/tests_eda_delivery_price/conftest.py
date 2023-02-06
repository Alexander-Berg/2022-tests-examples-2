# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=unused-variable
import json

from eats_catalog_storage_cache import (  # noqa: F403 F401
    eats_catalog_storage_cache,  # noqa: F403 F401
)
from eda_delivery_price_plugins import *  # noqa: F403 F401
import pytest


EATS_CATALOG_STORAGE_CACHE_DATA = [
    {
        'id': 1,
        'revision_id': 1,
        'updated_at': '2022-02-26T00:00:00.000000Z',
        'location': {'geo_point': [38.525496, 57.755680]},
        'region': {
            'id': 2,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 3,
            'slug': 'universe-cafe',
            'name': 'Universe Cafe',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
    },
    {
        'id': 2,
        'revision_id': 1,
        'updated_at': '2022-02-26T00:00:50.000000Z',
        'location': {'geo_point': [38.525496, 57.755680]},
        'region': {
            'id': 2,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 3,
            'slug': 'universe-cafe',
            'name': 'Universe Cafe',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
    },
    {
        'id': 3,
        'revision_id': 1,
        'updated_at': '2022-02-26T00:00:50.000000Z',
        'location': {'geo_point': [38.525486, 57.755690]},
        'region': {
            'id': 1,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 3,
            'slug': 'universe-cafe',
            'name': 'Universe Cafe',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'marketplace',
    },
    {
        'id': 4,
        'revision_id': 1,
        'updated_at': '2022-02-26T00:00:50.000000Z',
        'location': {'geo_point': [38.525486, 57.755690]},
        'region': {
            'id': 3,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 3,
            'slug': 'universe-shop',
            'name': 'Universe Shop',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'shop',
        'type': 'native',
    },
]


def do_nothing(*args, **kwargs):
    pass


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_catalog_storage_cache: [eats_catalog_storage_cache] '
        'fixture fo service cache',
    )
    config.addinivalue_line(
        'markers',
        'set_simple_pipeline_file: [set_simple_pipeline_file] '
        'sets pipeline file prefix',
    )


@pytest.fixture(name='eats-surge-resolver', autouse=True)
def simple_resolver_service(mockserver):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _eats_resolver_handler(request):
        return {}


@pytest.fixture(name='eats-eaters', autouse=True)
def simple_eater_service(mockserver):
    @mockserver.json_handler(
        '/eats-eaters/v1/eaters/find-by-personal-phone-id',
    )
    def handler(request):
        return {}


@pytest.fixture(name='eats-core', autouse=True)
def simple_core_service(mockserver):
    @mockserver.json_handler('/eats-core/v1/export/settings/regions-settings')
    def _handler(_):
        return mockserver.make_response(status=500)


@pytest.fixture(name='set_region_max_price')
def _set_region_max_price(mockserver):
    def set_region_max_price(
            region_id: int,
            native_max_delivery_fee: float,
            taxi_max_delivery_fee: float,
    ):
        @mockserver.json_handler(
            '/eats-core/v1/export/settings/regions-settings',
        )
        def _eats_core(_):
            return {
                'payload': {
                    'defaultMarketPlaceOffset': 0,
                    'defaultNativeOffset': -10,
                    'regionsOptions': [
                        {
                            'nativeMaxDeliveryFee': native_max_delivery_fee,
                            'offset': -10,
                            'regionId': region_id,
                            'yandexTaxiMaxDeliveryFee': taxi_max_delivery_fee,
                        },
                    ],
                    'storeOptions': {'minTime': 10, 'offset': 10},
                },
            }

    return set_region_max_price


@pytest.fixture(name='surge_resolver')
def surge_resolver(mockserver):
    class Context:
        def __init__(self):
            self.native_info = {
                'deliveryFee': 0,
                'loadLevel': 0,
                'surgeLevel': 0,
            }
            self.marketplace_info = {
                'additionalTimePercents': 0,
                'loadLevel': 0,
                'surgeLevel': 0,
            }
            self.request_assertion = do_nothing

            self.empty_response = False

        @property
        def times_called(self):
            return handler.times_called

    ctx = Context()

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def handler(request):
        if ctx.request_assertion:
            ctx.request_assertion(request)

        if ctx.empty_response:
            return []

        return [
            {
                'calculatorName': 'calc_surge_eats_2100m',
                'interval': {
                    'max': '2021-01-14T12:00:17+00:00',
                    'min': '2021-01-14T11:57:07+00:00',
                },
                'lavkaInfo': {
                    'loadLevel': 0,
                    'minimumOrder': 0,
                    'surgeLevel': 0,
                },
                'marketplaceInfo': ctx.marketplace_info,
                'nativeInfo': ctx.native_info,
                'placeId': 1,
                'zoneId': 0,
            },
        ]

    return ctx


@pytest.fixture(name='set_simple_pipeline_file', autouse=True)
def _set_simple_pipeline_file(admin_pipeline, request, load_json):
    """
    Задает файл с настройками пайплайна
    """

    def set_simple_pipeline_file(prefix: str):
        admin_pipeline.mock_single_pipeline(
            request,
            load_json,
            admin_pipeline.Config(
                prefix=prefix, consumers=['eda-delivery-price-surge'],
            ),
        )

    marker_prefix = None
    marker = request.node.get_closest_marker('set_simple_pipeline_file')
    if marker:
        marker_prefix = marker.kwargs.get('prefix')
    if marker_prefix:
        # Тут хак, чтобы задавать файлик красиво через декоратор
        # фикстура помечена как autouse, но на самом деле
        # задает файлик только если явно ее потом вызвать в коде
        # или если она используется как маркет, тогда вызов
        # происходит здесь
        set_simple_pipeline_file(marker_prefix)

    return set_simple_pipeline_file


@pytest.fixture(name='check_test_results')
def _check_test_results(taxi_eda_delivery_price, redis_store):
    async def do_check_test_results(
            test_id,
            handle,
            *,
            expected_status=None,
            expected_responses=None,
            expected_errors=None,
    ):
        redis_test_results = redis_store.get(f'test:{test_id}:results')
        response = await taxi_eda_delivery_price.get(
            handle, params={'test_id': test_id},
        )
        if redis_test_results is not None:
            redis_test_results = json.loads(redis_test_results)
            assert redis_test_results == {
                'status': expected_status,
                'responses': expected_responses or [],
                'errors': expected_errors or [],
            }
            assert response.status_code == 200
            assert response.json() == redis_test_results
        else:
            assert expected_status is None
            assert response.status_code == 404

    return do_check_test_results
