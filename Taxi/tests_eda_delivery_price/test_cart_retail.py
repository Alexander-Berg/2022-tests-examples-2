import pytest

from . import conftest
from . import experiments


def make_retail_request(
        subtotal: int,
        place_type: str = 'native',
        zone_type: str = 'pedestrian',
        offer: str = '2021-03-30T12:55:00+00:00',
        due=('2021-03-30T13:00:00+00:00', '2021-03-30T14:00:00+00:00'),
) -> dict:
    return {
        'due': list(due),
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
    'expected_sum_to_free_delivery',
    (
        pytest.param(
            '250',
            '300',
            {'amount_need': '250', 'next_cost': '100'},
            '750',
            marks=pytest.mark.set_simple_pipeline_file(prefix='default'),
            id='first threshdold',
        ),
        pytest.param(
            '750',
            '100',
            {'amount_need': '250', 'next_cost': '0'},
            '250',
            marks=pytest.mark.set_simple_pipeline_file(prefix='default'),
            id='second threshdold',
        ),
        pytest.param(
            '100',
            '500',
            {'amount_need': '200', 'next_cost': '400'},
            '1000',
            marks=pytest.mark.set_simple_pipeline_file(prefix='continuous'),
            id='continius one',
        ),
        pytest.param(
            '250',
            '425',
            {'amount_need': '200', 'next_cost': '325'},
            '850',
            marks=pytest.mark.set_simple_pipeline_file(prefix='continuous'),
            id='continius two',
        ),
        pytest.param(
            '950',
            '75',
            {'amount_need': '150', 'next_cost': '0'},
            '150',
            marks=pytest.mark.set_simple_pipeline_file(prefix='continuous'),
            id='continius next free',
        ),
    ),
)
@experiments.cart_service_fee('10.15')
@experiments.redis_experiment(enabled=True)
async def test_retail_cart(
        taxi_eda_delivery_price,
        surge_resolver,
        subtotal,
        expected_price,
        expected_next_delivery_threshold,
        expected_sum_to_free_delivery,
):

    native_info = {'deliveryFee': 0, 'loadLevel': 0, 'surgeLevel': 0}
    surge_resolver.native_info = native_info

    response = await taxi_eda_delivery_price.post(
        '/internal/v1/retail-price-surge',
        json=make_retail_request(subtotal),
        headers=make_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    for slot_price in data['slots_price']:
        cart_delivery_price = slot_price['cart_delivery_price']
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
        assert slot_price['surge_result']['nativeInfo'] == native_info
    assert data['service_fee'] == '10.15'
