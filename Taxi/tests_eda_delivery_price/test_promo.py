import json

import pytest


@pytest.mark.parametrize(
    'eda,retail', [(True, True), (True, False), (False, True), (False, False)],
)
async def test_promo(
        taxi_eda_delivery_price,
        mockserver,
        load_json,
        eda,
        retail,
        experiments3,
):
    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(request):
        return {'tags': ['yandex', 'manager']}

    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eats_new_user_promotion',
        consumers=['eda-delivery-price/is-new-user'],
        clauses=[],
        default_value={
            'show_eda_free_delivery': eda,
            'free_surge': eda,
            'retail_free_delivery': retail,
        },
    )
    await taxi_eda_delivery_price.invalidate_caches()

    response = await taxi_eda_delivery_price.post(
        '/v1/user-promo', data=json.dumps({'region_id': 1}),
    )

    response = response.json()

    assert response == {
        'is_eda_new_user': eda,
        'is_retail_new_user': retail,
        'any_free_delivery': False,
    }

    response_bulk = await taxi_eda_delivery_price.post(
        '/v2/calc-surge-bulk',
        data=json.dumps(
            {
                'places': [],
                'ts': '2018-08-01T12:59:23.231000+00:00',
                'region_id': 1,
            },
        ),
    )

    # add deprecated tags
    response['tags'] = []
    assert response == response_bulk.json()['user_info']


@pytest.mark.parametrize('eda', [True, False])
async def test_promo_without_retail(
        taxi_eda_delivery_price, mockserver, load_json, eda, experiments3,
):
    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(request):
        return None

    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eats_new_user_promotion',
        consumers=['eda-delivery-price/is-new-user'],
        clauses=[],
        default_value={
            'show_eda_free_delivery': eda,
            'free_surge': eda,
            'retail_free_delivery': False,
        },
    )

    await taxi_eda_delivery_price.invalidate_caches()

    response = await taxi_eda_delivery_price.post(
        '/v1/user-promo', data=json.dumps({'region_id': 1}),
    )

    response = response.json()

    assert response == {
        'is_eda_new_user': eda,
        'is_retail_new_user': False,
        'any_free_delivery': False,
    }

    response_bulk = await taxi_eda_delivery_price.post(
        '/v2/calc-surge-bulk',
        data=json.dumps(
            {
                'places': [],
                'ts': '2018-08-01T12:59:23.231000+00:00',
                'region_id': 1,
            },
        ),
    )

    # add deprecated tags
    response['tags'] = []
    assert response == response_bulk.json()['user_info']


SURGE_RESPONSE = [
    {
        'placeId': 1,
        'nativeInfo': {'surgeLevel': 1, 'loadLevel': 1, 'deliveryFee': 100.0},
        'marketplaceInfo': {
            'surgeLevel': 0,
            'loadLevel': 0,
            'additionalTimePercents': 35,
        },
        'lavkaInfo': {'surgeLevel': 0, 'loadLevel': 0, 'minimumOrder': 15},
    },
    {
        'placeId': 2,
        'nativeInfo': {'surgeLevel': 1, 'loadLevel': 1, 'deliveryFee': 50.0},
        'marketplaceInfo': {
            'surgeLevel': 0,
            'loadLevel': 0,
            'additionalTimePercents': 35,
        },
        'lavkaInfo': {'surgeLevel': 0, 'loadLevel': 0, 'minimumOrder': 15},
    },
]

ZERO_RESPONSE = [
    {
        'placeId': 1,
        'nativeInfo': {'surgeLevel': 0, 'loadLevel': 0, 'deliveryFee': 0.0},
        'marketplaceInfo': {
            'surgeLevel': 0,
            'loadLevel': 0,
            'additionalTimePercents': 35,
        },
        'lavkaInfo': {'surgeLevel': 0, 'loadLevel': 0, 'minimumOrder': 15},
    },
    {
        'placeId': 2,
        'nativeInfo': {'surgeLevel': 0, 'loadLevel': 0, 'deliveryFee': 0.0},
        'marketplaceInfo': {
            'surgeLevel': 0,
            'loadLevel': 0,
            'additionalTimePercents': 35,
        },
        'lavkaInfo': {'surgeLevel': 0, 'loadLevel': 0, 'minimumOrder': 15},
    },
]
