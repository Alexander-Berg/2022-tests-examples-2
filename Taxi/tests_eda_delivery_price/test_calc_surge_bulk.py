# pylint: disable=redefined-outer-name

import copy
import json

import pytest

from . import conftest
from . import experiments


SURGE_RESPONSE = [
    {
        'placeId': 1,
        'nativeInfo': {
            'surgeLevel': 1,
            'loadLevel': 50,
            'deliveryFee': 100.0,
            'show_radius': 33.0,
        },
        'marketplaceInfo': {
            'surgeLevel': 0,
            'loadLevel': 0,
            'additionalTimePercents': 35,
        },
        'lavkaInfo': {'surgeLevel': 0, 'loadLevel': 0, 'minimumOrder': 15},
    },
    {
        'placeId': 2,
        'nativeInfo': {'surgeLevel': 1, 'loadLevel': 75, 'deliveryFee': 50.0},
        'marketplaceInfo': {
            'surgeLevel': 0,
            'loadLevel': 0,
            'additionalTimePercents': 35,
        },
        'lavkaInfo': {'surgeLevel': 0, 'loadLevel': 0, 'minimumOrder': 15},
    },
]


@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2022-02-26T00:00:00.000000Z',
            'location': {'geo_point': [38.525496, 57.755680]},
            'region': {
                'id': 1,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 0,
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
                'id': 1,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 0,
                'slug': 'universe-cafe',
                'name': 'Universe Cafe',
                'picture_scale_type': 'aspect_fit',
            },
            'business': 'restaurant',
            'type': 'marketplace',
        },
    ],
)
@pytest.mark.experiments3(filename='calc_settings.json')
async def test_calc_surge_bulk_def(
        taxi_eda_delivery_price, mockserver, load_json,
):
    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(request):
        return {'tags': ['yandex', 'manager']}

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _eats_orders_handler(request):
        assert request.json['placeIds'] == [1, 2]
        return SURGE_RESPONSE

    response = await taxi_eda_delivery_price.post(
        '/v1/calc-surge-bulk',
        data=json.dumps(
            {
                'placeIds': [1, 2],
                'ts': '2018-08-01T12:59:23.231000+00:00',
                'user_id': '1',
                'region_id': 1,
            },
        ),
    )

    response = response.json()
    expected = SURGE_RESPONSE
    assert response['result'] == expected


@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2022-02-26T00:00:00.000000Z',
            'location': {'geo_point': [38.525496, 57.755680]},
            'region': {
                'id': 1,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 0,
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
                'id': 1,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 0,
                'slug': 'universe-cafe',
                'name': 'Universe Cafe',
                'picture_scale_type': 'aspect_fit',
            },
            'business': 'restaurant',
            'type': 'marketplace',
        },
    ],
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.calc_if_delivery_is_free()
@pytest.mark.parametrize('use_places_soa', [False, True])
async def test_calc_new_surge_bulk_def(
        taxi_eda_delivery_price, mockserver, load_json, use_places_soa,
):
    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _eats_orders_handler(request):
        assert request.json['placeIds'] == [1, 2]
        return SURGE_RESPONSE

    if use_places_soa:
        places = {
            'places': [],
            'places_soa': {
                'ids': [1, 2],
                'surge_types': ['native', 'marketplace'],
                'brand_ids': [0, 0],
            },
        }
    else:
        places = {
            'places': [
                {'id': 1, 'surge_type': 'native', 'brand_id': 0},
                {'id': 2, 'surge_type': 'marketplace', 'brand_id': 0},
            ],
        }

    response = await taxi_eda_delivery_price.post(
        '/v2/calc-surge-bulk',
        data=json.dumps(
            {
                **places,
                'ts': '2018-08-01T12:59:23.231000+00:00',
                'region_id': 1,
            },
        ),
    )

    promo_response = await taxi_eda_delivery_price.post(
        '/v1/user-promo', data=json.dumps({'region_id': 1}),
    )
    promo_response = promo_response.json()

    response = response.json()

    surge_main = copy.deepcopy(SURGE_RESPONSE)

    del surge_main[0]['marketplaceInfo']
    del surge_main[0]['lavkaInfo']
    del surge_main[1]['nativeInfo']
    del surge_main[1]['lavkaInfo']

    expected = []
    for surge in surge_main:
        expected.append({'surge': surge})

    # add deprecated tags
    promo_response['tags'] = []

    assert response['user_info'] == promo_response
    assert response['places_info'] == expected


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_new_user_promotion',
    consumers=['eda-delivery-price/is-new-user'],
    clauses=[],
    default_value={'free_surge': True, 'retail_free_delivery': False},
)
async def test_calc_surge_bulk_in_exp(
        taxi_eda_delivery_price, mockserver, load_json,
):
    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _eats_orders_handler(request):
        assert request.json['placeIds'] == [1, 2]
        return SURGE_RESPONSE

    response = await taxi_eda_delivery_price.post(
        '/v1/calc-surge-bulk',
        data=json.dumps(
            {
                'placeIds': [1, 2],
                'ts': '2018-08-01T12:59:23.231000+00:00',
                'user_id': '1',
                'region_id': 1,
            },
        ),
    )

    response = response.json()

    assert response['result'] == [
        {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 0,
                'loadLevel': 0,
                'deliveryFee': 0.0,
                'show_radius': 33.0,
            },
            'marketplaceInfo': {
                'surgeLevel': 0,
                'loadLevel': 0,
                'additionalTimePercents': 35,
            },
            'lavkaInfo': {'surgeLevel': 0, 'loadLevel': 0, 'minimumOrder': 15},
        },
        {
            'placeId': 2,
            'nativeInfo': {
                'surgeLevel': 0,
                'loadLevel': 0,
                'deliveryFee': 0.0,
            },
            'marketplaceInfo': {
                'surgeLevel': 0,
                'loadLevel': 0,
                'additionalTimePercents': 35,
            },
            'lavkaInfo': {'surgeLevel': 0, 'loadLevel': 0, 'minimumOrder': 15},
        },
    ]


@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 228,
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
    ],
)
@pytest.mark.experiments3(filename='calc_settings.json')
async def test_calc_surge_bulk_no_answer(taxi_eda_delivery_price, mockserver):
    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return None

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _surge_handler(_):
        return [{'value': 'here'}]

    response = await taxi_eda_delivery_price.post(
        '/v1/calc-surge-bulk',
        data=json.dumps(
            {
                'placeIds': [228],
                'ts': '2018-08-01T12:59:23.231000+00:00',
                'user_id': '1',
                'region_id': 1,
            },
        ),
    )

    response = response.json()

    assert response['result'] == [
        {
            'placeId': 228,
            'nativeInfo': {
                'surgeLevel': 0,
                'loadLevel': 0,
                'deliveryFee': 0.0,
            },
            'marketplaceInfo': {
                'surgeLevel': 0,
                'loadLevel': 0,
                'additionalTimePercents': 0,
            },
            'lavkaInfo': {'surgeLevel': 0, 'loadLevel': 0, 'minimumOrder': 0},
        },
    ]


@pytest.fixture()
def mock_admin_pipeline_bulk(admin_pipeline, request, load_json):
    admin_pipeline.mock_single_pipeline(
        request,
        load_json,
        admin_pipeline.Config(
            prefix='delivery_price_pipeline_2',
            consumers=['eda-delivery-price-surge'],
        ),
    )


@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
            'region': {
                'id': 2,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'business': 'restaurant',
            'type': 'native',
        },
    ],
)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.yt(
    static_table_data=[
        'yt_countries.yaml',
        'yt_regions.yaml',
        'yt_continuous_commission.yaml',
        'yt_settings_data.yaml',
    ],
)
@pytest.mark.geoareas(filename='db_geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='db_tariffs.json')
@pytest.mark.config(
    EDA_DELIVERY_PRICE_MAIN={
        'switchback_exp_interval_minutes': 40,
        'switchback_time_offset_minutes': 3,
    },
)
async def test_approximate_price(taxi_eda_delivery_price, mockserver):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _eats_orders_handler(request):
        assert request.json['placeIds'] == [1]
        return [
            {
                'placeId': 1,
                'nativeInfo': {
                    'surgeLevel': 1,
                    'loadLevel': 50,
                    'deliveryFee': 9.0,
                },
            },
        ]

    places = {'places': [{'id': 1, 'surge_type': 'native', 'brand_id': 0}]}
    response = await taxi_eda_delivery_price.post(
        '/v2/calc-surge-bulk',
        data=json.dumps(
            {
                **places,
                'ts': '2018-08-01T12:59:23.231000+00:00',
                'region_id': 1,
                'position': [47.525496503606774, 55.75568074159372],
                'calculatate_price': True,
            },
        ),
    )

    response.json()['places_info'] = [
        {
            'delivery_price': 209.0,
            'surge': {
                'nativeInfo': {
                    'deliveryFee': 9.0,
                    'loadLevel': 50,
                    'surgeLevel': 1,
                },
                'placeId': 1,
            },
        },
    ]

    # check different distance
    response = await taxi_eda_delivery_price.post(
        '/v2/calc-surge-bulk',
        data=json.dumps(
            {
                **places,
                'ts': '2018-08-01T12:59:23.231000+00:00',
                'region_id': 1,
                'position': [47.555496503606774, 55.75568074159372],
                'calculatate_price': True,
            },
        ),
    )

    response.json()['places_info'] = [
        {
            'delivery_price': 249.0,
            'surge': {
                'nativeInfo': {
                    'deliveryFee': 9.0,
                    'loadLevel': 50,
                    'surgeLevel': 1,
                },
                'placeId': 1,
            },
        },
    ]


@pytest.mark.now('2021-03-30T12:40:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.surge_planned(120)
async def test_calc_surge_bulk_preorder(
        taxi_eda_delivery_price, surge_resolver,
):
    """
    Проверяем, что если разница между текущим временем и
    временем предзаказа л
    """

    native_info = {'deliveryFee': 100, 'loadLevel': 100, 'surgeLevel': 100}
    surge_resolver.native_info = native_info

    offer = '2021-03-30T12:35:00+00:00'
    due = '2021-03-30T13:00:00+00:00'

    def surge_assertion(request):
        assert request.json['ts'] == offer

    surge_resolver.request_assertion = surge_assertion

    response = await taxi_eda_delivery_price.post(
        '/v2/calc-surge-bulk',
        data=json.dumps(
            {
                'places': [{'id': 1, 'surge_type': 'native', 'brand_id': 0}],
                'ts': offer,
                'due': due,
                'region_id': 1,
                'position': [47.525496503606774, 55.75568074159372],
            },
        ),
    )

    assert response.status_code == 200
    assert surge_resolver.times_called == 1
