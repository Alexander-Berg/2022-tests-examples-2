import copy

import pytest

from . import conftest
from . import experiments


DEFAULT_REQUEST = {
    'offer': '2018-08-01T12:59:23.231000+00:00',
    'place_info': {
        'place_id': 1,
        'region_id': 2,
        'brand_id': 3,
        'position': [38, 57],
        'type': 'native',
        'business_type': 'restaurant',
    },
    'user_info': {
        'position': [38.5, 57.5],
        'device_id': 'some_id',
        'user_id': 'user_id1',
        'personal_phone_id': '123',
    },
    'zone_info': {'zone_type': 'taxi'},
}


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_if_delivery_is_free()
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@pytest.mark.set_simple_pipeline_file(prefix='violates_region_limit_pipeline')
async def test_thresholds_region_limit(
        taxi_eda_delivery_price, set_region_max_price,
):
    """
    Проверяем, что к трешхолдам применяется лимит по региону
    """

    region_id = 2
    native_max_delivery_fee = 499
    taxi_max_delivery_fee = 499
    set_region_max_price(
        region_id, native_max_delivery_fee, taxi_max_delivery_fee,
    )

    request_body = copy.deepcopy(DEFAULT_REQUEST)
    request_body['place_info']['region_id'] = region_id

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', json=request_body,
    )
    assert response.status_code == 200

    data = response.json()
    fees = data['calculation_result']['result']['fees']
    assert fees == [
        {'delivery_cost': taxi_max_delivery_fee, 'order_price': 0},
        {'delivery_cost': 100, 'order_price': 500},
        {'delivery_cost': 0, 'order_price': 1000},
    ]


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@experiments.calc_if_delivery_is_free()
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.cart_weight_thresholds()
@pytest.mark.set_simple_pipeline_file(
    prefix='violates_region_limit_continuous_pipeline',
)
@pytest.mark.parametrize(
    'subtotal,delivery_fee,next_delivery_threshold',
    (
        pytest.param(
            '50',
            '300',
            {'amount_need': '650', 'next_cost': '200'},
            id='before_first_point',
        ),
        pytest.param(
            '100',
            '300',
            {'amount_need': '600', 'next_cost': '200'},
            id='on_first_point',
        ),
        pytest.param(
            '250',
            '300',
            {'amount_need': '450', 'next_cost': '200'},
            id='on_constant_lvl',
        ),
        pytest.param(
            '400',
            '300',
            {'amount_need': '300', 'next_cost': '200'},
            id='on_constant_lvl_2',
        ),
        pytest.param(
            '500',
            '300',
            {'amount_need': '200', 'next_cost': '200'},
            id='on_change_point',
        ),
        pytest.param(
            '750',
            '175',
            {'amount_need': '200', 'next_cost': '75'},
            id='on_incline',
        ),
    ),
)
async def test_continuous_region_limit(
        taxi_eda_delivery_price,
        set_region_max_price,
        subtotal,
        delivery_fee,
        next_delivery_threshold,
):
    """
    Проверяем, расчет непрерывной доставки в случае если прямая упирается в
    региональный лимит
    Исходная прямая проходит через точки (100, 500) (1100, 0)
    Прямая y = -0.5000 * x + 550.0000
    Но 500 выше регионального лимита 300
    """

    request = {
        'due': '2021-03-30T12:55:00+00:00',
        'offer': '2021-03-30T12:55:00+00:00',
        'place_info': {
            'place_id': '1',
            'region_id': '2',
            'brand_id': '3',
            'position': [38, 57],
            'type': 'native',
            'currency': {'sign': '$'},
            'business_type': 'restaurant',
        },
        'user_info': {
            'position': [38.5, 57.5],
            'device_id': 'some_id',
            'user_id': 'user_id1',
            'personal_phone_id': '123',
        },
        'cart_info': {'subtotal': str(subtotal)},
        'zone_info': {'zone_type': 'pedestrian'},
    }

    region_id = 2
    native_max_delivery_fee = 300
    taxi_max_delivery_fee = 300
    set_region_max_price(
        region_id, native_max_delivery_fee, taxi_max_delivery_fee,
    )

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=request,
        headers={'x-platform': 'ios_app', 'x-app-version': '5.20.0'},
    )
    assert response.status_code == 200

    data = response.json()
    cart_delivery_price = data['cart_delivery_price']
    assert cart_delivery_price['delivery_fee'] == delivery_fee
    assert (
        cart_delivery_price['next_delivery_threshold']
        == next_delivery_threshold
    )


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@experiments.calc_if_delivery_is_free()
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.cart_weight_thresholds()
@experiments.regional_limits_config('150.0')
@pytest.mark.set_simple_pipeline_file(
    prefix='violates_region_limit_continuous_pipeline',
)
async def test_regional_limit_config(
        taxi_eda_delivery_price, set_region_max_price,
):
    region_id = 2
    request = {
        'due': '2021-03-30T12:55:00+00:00',
        'offer': '2021-03-30T12:55:00+00:00',
        'place_info': {
            'place_id': '1',
            'region_id': str(region_id),
            'brand_id': '3',
            'position': [38, 57],
            'type': 'native',
            'currency': {'sign': '$'},
            'business_type': 'restaurant',
        },
        'user_info': {
            'position': [38.5, 57.5],
            'device_id': 'some_id',
            'user_id': 'user_id1',
            'personal_phone_id': '123',
        },
        'cart_info': {'subtotal': '450.0'},
        'zone_info': {'zone_type': 'pedestrian'},
    }

    set_region_max_price(region_id, 300, 300)

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=request,
        headers={'x-platform': 'ios_app', 'x-app-version': '5.20.0'},
    )
    assert response.status_code == 200

    cart_delivery_price = response.json()['cart_delivery_price']
    assert cart_delivery_price['delivery_fee'] == '150'
