# pylint: disable=redefined-outer-name
from typing import Optional

import pytest

from . import conftest
from . import experiments


def make_cart_request(
        subtotal: float,
        place_type: str = 'native',
        zone_type: str = 'pedestrian',
        offer: str = '2021-03-30T12:55:00+00:00',
        due: str = '2021-03-30T12:55:00+00:00',
        weight: Optional[int] = None,
) -> dict:
    request: dict = {
        'due': due,
        'offer': offer,
        'place_info': {
            'place_id': '1',
            'region_id': '2',
            'brand_id': '3',
            'position': [38, 57],
            'type': place_type,
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
        'zone_info': {'zone_type': zone_type},
    }

    if weight is not None:
        request['cart_info']['weight'] = weight

    return request


def make_headers():
    return {'x-platform': 'ios_app', 'x-app-version': '5.20.0'}


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.calc_if_delivery_is_free()
@pytest.mark.parametrize(
    'subtotal,expected_price,expected_next_delivery_threshold,'
    'expected_sum_to_free_delivery,expected_delivery_fee_range',
    (
        pytest.param(
            '250',
            '300',
            {'amount_need': '250', 'next_cost': '100'},
            '750',
            {'min': '0', 'max': '300'},
            marks=pytest.mark.set_simple_pipeline_file(prefix='default'),
            id='first threshdold',
        ),
        pytest.param(
            '750',
            '100',
            {'amount_need': '250', 'next_cost': '0'},
            '250',
            {'min': '0', 'max': '300'},
            marks=pytest.mark.set_simple_pipeline_file(prefix='default'),
            id='second threshdold',
        ),
        pytest.param(
            '100',
            '500',
            {'amount_need': '200', 'next_cost': '400'},
            '1000',
            {'min': '0', 'max': '500'},
            marks=pytest.mark.set_simple_pipeline_file(prefix='continuous'),
            id='continius one',
        ),
        pytest.param(
            '250',
            '425',
            {'amount_need': '200', 'next_cost': '325'},
            '850',
            {'min': '0', 'max': '500'},
            marks=pytest.mark.set_simple_pipeline_file(prefix='continuous'),
            id='continius two',
        ),
        pytest.param(
            '950',
            '75',
            {'amount_need': '150', 'next_cost': '0'},
            '150',
            {'min': '0', 'max': '500'},
            marks=pytest.mark.set_simple_pipeline_file(prefix='continuous'),
            id='continius next free',
        ),
    ),
)
@experiments.cart_service_fee('10.15')
@experiments.redis_experiment(enabled=True)
async def test_cart_delivery_price_surge(
        taxi_eda_delivery_price,
        surge_resolver,
        subtotal,
        expected_price,
        expected_next_delivery_threshold,
        expected_sum_to_free_delivery,
        expected_delivery_fee_range,
):
    native_info = {'deliveryFee': 0, 'loadLevel': 0, 'surgeLevel': 0}
    surge_resolver.native_info = native_info

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=make_cart_request(subtotal),
        headers=make_headers(),
    )

    assert response.status_code == 200

    data = response.json()
    cart_delivery_price = data['cart_delivery_price']

    assert cart_delivery_price['delivery_fee'] == expected_price
    assert (
        cart_delivery_price['next_delivery_threshold']
        == expected_next_delivery_threshold
    )
    assert cart_delivery_price['min_cart'] == '0'
    assert (
        cart_delivery_price['sum_to_free_delivery']
        == expected_sum_to_free_delivery
    )
    assert data['surge_result']['nativeInfo'] == native_info
    assert data['service_fee'] == '10.15'

    # проверяем Redis
    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=make_cart_request(subtotal),
        headers=make_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    cart_delivery_price = data['cart_delivery_price']
    assert cart_delivery_price['delivery_fee'] == expected_price
    assert (
        cart_delivery_price['next_delivery_threshold']
        == expected_next_delivery_threshold
    )
    assert (
        cart_delivery_price['delivery_fee_range']
        == expected_delivery_fee_range
    )


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    [
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
            'type': 'marketplace',
        },
    ],
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_if_delivery_is_free()
async def test_cart_marketplace(taxi_eda_delivery_price, surge_resolver):
    marketplace_info = {
        'additionalTimePercents': 0,
        'loadLevel': 0,
        'surgeLevel': 0,
    }

    surge_resolver.marketplaceInfo = marketplace_info

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=make_cart_request(100, 'marketplace'),
        headers=make_headers(),
    )

    assert response.status_code == 200

    data = response.json()
    assert 'cart_delivery_price' not in data


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    [
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
    ],
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.calc_if_delivery_is_free()
@pytest.mark.set_simple_pipeline_file(prefix='default')
async def test_surge_taxi(taxi_eda_delivery_price, surge_resolver):
    """
    Проверяем, что сурж не применяется для такси зон
    """

    native_info = {'deliveryFee': 100, 'loadLevel': 100, 'surgeLevel': 100}
    surge_resolver.native_info = native_info

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=make_cart_request(250, 'native', 'taxi'),
        headers=make_headers(),
    )

    assert response.status_code == 200

    data = response.json()
    assert data['cart_delivery_price']['delivery_fee'] == '300'
    assert data['surge_result']['nativeInfo'] == {
        'deliveryFee': 0,
        'loadLevel': 0,
        'surgeLevel': 0,
    }


@pytest.mark.now('2021-03-30T12:40:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.calc_if_delivery_is_free()
@experiments.surge_planned(120)
@pytest.mark.set_simple_pipeline_file(prefix='default')
@pytest.mark.parametrize(
    'due,resolver_times_called,expected_delivery_fee,expected_surge_level',
    (
        pytest.param(
            '2021-03-30T13:30:00+00:00',
            1,
            '200',  # 100 as middle threshold + 100 as surge
            100,
            id='apply_surge_on_preorder',
        ),
        pytest.param(
            '2021-03-30T14:30:00+00:00',
            0,
            '300',
            0,
            id='out_of_surge_asap_interval',
        ),
    ),
)
async def test_surge_preorder(
        taxi_eda_delivery_price,
        surge_resolver,
        due,
        resolver_times_called,
        expected_delivery_fee,
        expected_surge_level,
):
    """
    Проверяем, что сурж применяется для предзаказа
    """

    native_info = {'deliveryFee': 100, 'loadLevel': 100, 'surgeLevel': 100}
    surge_resolver.native_info = native_info

    offer = '2021-03-30T12:00:00+00:00'

    def surge_assertion(request):
        assert request.json['ts'] == offer

    surge_resolver.request_assertion = surge_assertion

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=make_cart_request(250, 'native', offer=offer, due=due),
        headers=make_headers(),
    )

    assert response.status_code == 200
    assert surge_resolver.times_called == resolver_times_called
    data = response.json()

    assert data['cart_delivery_price']['delivery_fee'] == expected_delivery_fee
    native_info = data['surge_result']['nativeInfo']
    assert native_info['surgeLevel'] == expected_surge_level


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.calc_if_delivery_is_free()
@pytest.mark.set_simple_pipeline_file(prefix='default')
async def test_no_native_info(taxi_eda_delivery_price, surge_resolver):
    """
    Проверяем, работоспособность если сурж не пришел или NativeInfo пустое
    """

    surge_resolver.native_info = {}
    surge_resolver.marketplace_info = {}

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=make_cart_request(250, 'native'),
        headers=make_headers(),
    )

    assert response.status_code == 200
    assert surge_resolver.times_called == 1

    surge_resolver.empty_response = True

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=make_cart_request(250, 'native'),
        headers=make_headers(),
    )
    assert response.status_code == 200
    assert surge_resolver.times_called == 2


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.calc_if_delivery_is_free()
@pytest.mark.set_simple_pipeline_file(prefix='default')
async def test_bad_request(taxi_eda_delivery_price):
    """
    Проверяем ошибку парсинга нецелочисленных id
    """

    body = {
        'offer': '2018-08-01T12:59:23.231000+00:00',
        'place_info': {
            'place_id': 'invalid_place_id',
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
        'cart_info': {'subtotal': '100'},
        'zone_info': {'zone_type': 'pedestrian'},
    }

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=body,
        headers=make_headers(),
    )

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == 'Failed to parse request.body.place_info'


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.calc_if_delivery_is_free()
@pytest.mark.set_simple_pipeline_file(prefix='surge')
@pytest.mark.parametrize(
    'subtotal,expected_price,expected_next_delivery_threshold,'
    'expected_surge_fee',
    (
        pytest.param(
            '250',
            '525',
            {'amount_need': '200', 'next_cost': '425'},
            100,
            id='less_than_middle_point',
        ),
        pytest.param(
            '1000',
            '150',
            {'amount_need': '100', 'next_cost': '20'},
            100,
            id='close_to_last_point',
        ),
        pytest.param('1500', '20', None, 20, id='greater_than_last_point'),
    ),
)
async def test_continuous_surge(
        taxi_eda_delivery_price,
        surge_resolver,
        subtotal,
        expected_price,
        expected_next_delivery_threshold,
        expected_surge_fee,
):
    """
    Проверяем применение суржа по прямой из пайплана
    ожидаем что до 1000 будет прибавляться 100 к основной цене
    после 1000 будет 20
    """

    native_info = {'deliveryFee': 10, 'loadLevel': 10, 'surgeLevel': 10}
    surge_resolver.native_info = native_info

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=make_cart_request(subtotal),
        headers=make_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    cart_delivery_price = data['cart_delivery_price']

    assert cart_delivery_price['delivery_fee'] == expected_price
    assert (
        cart_delivery_price.get('next_delivery_threshold')
        == expected_next_delivery_threshold
    )
    assert cart_delivery_price['min_cart'] == '0'
    assert 'sum_to_free_delivery' not in cart_delivery_price
    assert (
        data['surge_result']['nativeInfo']['deliveryFee'] == expected_surge_fee
    )


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.calc_if_delivery_is_free()
@pytest.mark.set_simple_pipeline_file(prefix='surge_free')
async def test_continuous_surge_free_delivery(
        taxi_eda_delivery_price, surge_resolver,
):
    """
    Проверяем сурж при достижении бесплатной доставки
    """

    subtotal = 1500
    load_level = 10
    surge_level = 10
    native_info = {
        'deliveryFee': 10,
        'loadLevel': load_level,
        'surgeLevel': surge_level,
    }
    surge_resolver.native_info = native_info

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=make_cart_request(subtotal),
        headers=make_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    cart_delivery_price = data['cart_delivery_price']

    assert cart_delivery_price['delivery_fee'] == '0'
    assert 'next_delivery_threshold' not in cart_delivery_price
    assert cart_delivery_price['min_cart'] == '0'
    assert 'sum_to_free_delivery' not in cart_delivery_price
    assert data['surge_result']['nativeInfo'] == {
        'deliveryFee': 0,
        'loadLevel': load_level,
        'surgeLevel': surge_level,
    }


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.calc_if_delivery_is_free()
@experiments.continuous_carrot(step=300)
@pytest.mark.set_simple_pipeline_file(prefix='continuous')
@pytest.mark.parametrize(
    'subtotal,expected_next_delivery_threshold',
    (
        pytest.param(
            100, {'amount_need': '300', 'next_cost': '350'}, id='generic',
        ),
        pytest.param(
            1050,
            {'amount_need': '50', 'next_cost': '0'},
            id='close_to_last_order_price',
        ),
        pytest.param(1500, None, id='close_to_last_order_price'),
    ),
)
async def test_continuous_carrot(
        taxi_eda_delivery_price,
        surge_resolver,
        subtotal,
        expected_next_delivery_threshold,
):
    """
    Проверяем, логику формирования next_delivery_threshold
    при включении эксперимент eda_delivery_price_continuous_carrot
    """

    native_info = {'deliveryFee': 0, 'loadLevel': 0, 'surgeLevel': 0}
    surge_resolver.native_info = native_info

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=make_cart_request(subtotal),
        headers=make_headers(),
    )

    assert response.status_code == 200

    data = response.json()
    cart_delivery_price = data['cart_delivery_price']
    assert (
        cart_delivery_price.get('next_delivery_threshold')
        == expected_next_delivery_threshold
    )


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.calc_if_delivery_is_free()
@pytest.mark.set_simple_pipeline_file(prefix='continuous')
@pytest.mark.parametrize(
    'expected_delivery_fee,expected_next_delivery_threshold',
    (
        pytest.param(
            '400.01',
            {'amount_need': '200', 'next_cost': '300.01'},
            marks=experiments.continuous_round('two_signs'),
            id='two_signs',
        ),
        pytest.param(
            '401',
            {'amount_need': '200', 'next_cost': '301'},
            marks=experiments.continuous_round('ceil'),
            id='ceil',
        ),
        pytest.param(
            '409',
            {'amount_need': '200', 'next_cost': '309'},
            marks=experiments.continuous_round('to_nine'),
            id='to_nine',
        ),
    ),
)
async def test_continuous_round(
        taxi_eda_delivery_price,
        surge_resolver,
        expected_delivery_fee,
        expected_next_delivery_threshold,
):
    """
    Проверяет, что политика округления цен
    управляется экспериментом
    eda_delivery_price_continuous_round
    """

    subtotal = 299.99
    native_info = {'deliveryFee': 0, 'loadLevel': 0, 'surgeLevel': 0}
    surge_resolver.native_info = native_info

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=make_cart_request(subtotal),
        headers=make_headers(),
    )

    assert response.status_code == 200

    data = response.json()
    cart_delivery_price = data['cart_delivery_price']

    assert cart_delivery_price['delivery_fee'] == expected_delivery_fee
    assert (
        cart_delivery_price['next_delivery_threshold']
        == expected_next_delivery_threshold
    )


@pytest.mark.now('2022-03-23T12:00:00+00:00')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.calc_if_delivery_is_free()
@pytest.mark.parametrize(
    'subtotal,weight,expected_price,expected_next_delivery_threshold,'
    'expected_sum_to_free_delivery,expected_weight_fee,'
    'expected_delivery_fee_range',
    (
        pytest.param(
            '250',
            200,
            '300',
            {'amount_need': '250', 'next_cost': '100'},
            '750',
            '0',
            {'min': '0', 'max': '300'},
            marks=pytest.mark.set_simple_pipeline_file(
                prefix='weights_thresholds',
            ),
            id='First threshold with zero weight fees',
        ),
        pytest.param(
            '250',
            5000,
            '300',
            {'amount_need': '250', 'next_cost': '100'},
            '750',
            '40',
            {'min': '0', 'max': '300'},
            marks=pytest.mark.set_simple_pipeline_file(
                prefix='weights_thresholds',
            ),
            id='First threshold with real weight fees',
        ),
        pytest.param(
            '750',
            5000,
            '100',
            {'amount_need': '250', 'next_cost': '0'},
            '250',
            '40',
            {'min': '0', 'max': '300'},
            marks=pytest.mark.set_simple_pipeline_file(
                prefix='weights_thresholds',
            ),
            id='Second threshold with real weight fees',
        ),
        pytest.param(
            '100',
            5000,
            '500',
            {'amount_need': '200', 'next_cost': '400'},
            '1000',
            '40',
            {'min': '0', 'max': '500'},
            marks=pytest.mark.set_simple_pipeline_file(
                prefix='weights_continuous',
            ),
            id='Continuous one with weight fees',
        ),
        pytest.param(
            '950',
            5000,
            '75',
            {'amount_need': '150', 'next_cost': '0'},
            '150',
            '40',
            {'min': '0', 'max': '500'},
            marks=pytest.mark.set_simple_pipeline_file(
                prefix='weights_continuous',
            ),
            id='Continuous next free with weight fees',
        ),
    ),
)
@experiments.cart_service_fee('10.15')
@experiments.redis_experiment(enabled=True)
async def test_cart_delivery_price_surge_with_cart_weight(
        taxi_eda_delivery_price,
        surge_resolver,
        subtotal,
        weight,
        expected_price,
        expected_weight_fee,
        expected_next_delivery_threshold,
        expected_sum_to_free_delivery,
        expected_delivery_fee_range,
):
    native_info = {'deliveryFee': 0, 'loadLevel': 0, 'surgeLevel': 0}
    surge_resolver.native_info = native_info

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/cart-delivery-price-surge',
        json=make_cart_request(subtotal=subtotal, weight=weight),
        headers=make_headers(),
    )
    assert response.status_code == 200

    data = response.json()
    cart_delivery_price = data['cart_delivery_price']

    assert cart_delivery_price['weight_fee'] == expected_weight_fee
    assert cart_delivery_price['delivery_fee'] == expected_price
    assert (
        cart_delivery_price['next_delivery_threshold']
        == expected_next_delivery_threshold
    )
    assert cart_delivery_price['min_cart'] == '0'
    assert (
        cart_delivery_price['sum_to_free_delivery']
        == expected_sum_to_free_delivery
    )
