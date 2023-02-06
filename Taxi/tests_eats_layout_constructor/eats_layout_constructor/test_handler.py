import pytest

from . import configs
from . import experiments
from . import utils


@pytest.mark.experiments3(
    name='eats_layout_template',
    consumers=['layout-constructor/layout'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'layout_slug': 'layout_1'},
        },
    ],
)
@configs.layout_experiment_name(name='eats_layout_template')
@pytest.mark.parametrize(
    'layout_request,response_code',
    [
        pytest.param({}, 400, id='empty request'),
        pytest.param(
            {'region_id': 1},
            400,
            id='regions empty',
            marks=(pytest.mark.eats_regions_cache([])),
        ),
        pytest.param(
            {'location': {'latitude': 0.0, 'longitude': 0.0}},
            200,
            id='just location',
        ),
        pytest.param(
            {'region_id': 1, 'location': {'latitude': 0.0, 'longitude': 0.0}},
            200,
            id='location and region',
        ),
    ],
)
async def test_invalid_request_params(
        taxi_eats_layout_constructor,
        mockserver,
        layout_request,
        response_code,
):
    """EDACAT-51: проверяет, что в запросе должен присутствовать location."""

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return {'blocks': [], 'filters': [], 'sort': [], 'timepicker': []}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json=layout_request,
    )
    assert response.status_code == response_code


@pytest.mark.experiments3(
    name='eats_layout_template',
    consumers=['layout-constructor/layout'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'layout_slug': 'layout_1'},
        },
    ],
)
@configs.layout_experiment_name(name='eats_layout_template')
@pytest.mark.eats_regions_cache(
    [
        {
            'id': 2,
            'name': '2',
            'slug': '3',
            'genitive': '4',
            'isAvailable': True,
            'isDefault': False,
            'bbox': [11.11, 22.22, 33.33, 44.44],
            'center': [12.34, 56.78],
            'timezone': 'Europe/Moscow',
            'sort': 44343,
            'yandexRegionIds': [2, 4, 6, 8],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
        {
            'id': 1,
            'name': 'Москва',
            'slug': 'moscow',
            'genitive': 'в Москве',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [36.571501, 55.201432, 38.779148, 56.290749],
            'center': [37.642806, 55.724266],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [213, 216],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
    ],
)
async def test_regions_cache(taxi_eats_layout_constructor, mockserver):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        assert request.json['location'] == {
            'longitude': 37.642806,
            'latitude': 55.724266,
        }

        return {'blocks': [], 'filters': [], 'sort': [], 'timepicker': []}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'region_id': 1},
    )
    assert response.status_code == 200
    assert catalog.times_called == 1


@experiments.ENABLE_BRANDS_COUNT
@configs.keep_empty_layout()
@pytest.mark.layout(
    autouse=True,
    slug='count_layout',
    widgets=[
        utils.Widget(
            type='places_collection',
            name='Places collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
        ),
    ],
)
async def test_business_count(layout_constructor, mockserver, experiments3):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage/v1/brands/count',
    )
    def eats_catalog_storage(request):
        return {
            'business_count': [
                {'business': 'restaurant', 'count': 10},
                {'business': 'shop', 'count': 2123},
            ],
        }

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def eats_catalog(request):
        return {'blocks': [], 'filters': [], 'sort': [], 'timepicker': []}

    recorder = experiments3.record_match_tries('this_is_layout_experiment')

    response = await layout_constructor.post()

    assert response.status_code == 200
    assert eats_catalog.times_called == 1
    assert eats_catalog_storage.times_called == 1

    match_tries = await recorder.get_match_tries(ensure_ntries=1)

    kwargs = match_tries[0].kwargs

    assert kwargs['restaurant_count'] == 10
    assert kwargs['shop_count'] == 2123
