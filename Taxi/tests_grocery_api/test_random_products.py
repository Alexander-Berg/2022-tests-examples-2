import decimal

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import common
from . import const
from . import experiments

# pylint: disable=invalid-name
Decimal = decimal.Decimal

METRIC_NAME = 'grocery_api_random_products_found'


@pytest.fixture(name='get_random_products')
async def _get_random_products(taxi_grocery_api, load_json, overlord_catalog):
    async def _do(threshold, stocks=None, status_code=200):
        location = const.LOCATION

        common.prepare_overlord_catalog_json(
            load_json, overlord_catalog, location, product_stocks=stocks,
        )

        response = await taxi_grocery_api.post(
            '/lavka/v1/api/v1/modes/random-products',
            json={'position': {'location': location}, 'threshold': threshold},
            headers={'Accept-Language': 'ru'},
        )

        assert response.status_code == status_code
        return response.json()

    return _do


async def test_response(get_random_products, experiments3):
    experiments.random_products(
        experiments3, upper_shift='1', prefetch_limit=10,
    )
    response = await get_random_products(threshold='2')
    assert response['products'][0] == {
        'available': True,
        'description': 'product-1-description',
        'id': 'product-1',
        'image_url_template': 'product-1-image-url-template',
        'image_url_templates': ['product-1-image-url-template'],
        'pricing': {'price': '2', 'price_template': '2 $SIGN$$CURRENCY$'},
        'quantity_limit': '5',
        'title': 'product-1-title',
        'long_title': 'product-1-long-title',
        'private_label': True,
        'type': 'good',
    }


# проверяем, что если поднять upper_shift, то добавляется более дорогой
# продукт - product-2.
@pytest.mark.parametrize(
    'upper_shift, prefetched_item_ids',
    [('1', ['product-1']), ('4', ['product-1', 'product-2'])],
)
async def test_random_products_upper_shift(
        get_random_products,
        experiments3,
        testpoint,
        upper_shift,
        prefetched_item_ids,
):
    lower_shift = '0'
    experiments.random_products(
        experiments3,
        lower_shift=lower_shift,
        upper_shift=upper_shift,
        prefetch_limit=10,
    )

    @testpoint('prefetched_items')
    def prefetched_items(items):
        assert sorted(items) == prefetched_item_ids

    threshold = '2'
    response = await get_random_products(threshold=threshold)
    assert response['products']

    _check_products_price(
        response['products'], threshold, lower_shift, upper_shift,
    )

    assert prefetched_items.times_called == 1


# проверяем, что если поднять lower_shift, то выкидывается product-1, у
# которого цена становится слишком маленькой.
@pytest.mark.parametrize(
    'lower_shift, prefetched_item_ids',
    [
        ('0', ['product-1', 'product-2', 'product-3']),
        ('2', ['product-2', 'product-3']),
    ],
)
async def test_random_products_lower_shift(
        get_random_products,
        experiments3,
        testpoint,
        lower_shift,
        prefetched_item_ids,
):
    upper_shift = '9999'
    experiments.random_products(
        experiments3,
        lower_shift=lower_shift,
        upper_shift=upper_shift,
        prefetch_limit=10,
    )

    @testpoint('prefetched_items')
    def prefetched_items(items):
        assert sorted(items) == prefetched_item_ids

    threshold = '2'
    response = await get_random_products(threshold=threshold)
    assert response['products']

    _check_products_price(
        response['products'], threshold, lower_shift, upper_shift,
    )

    assert prefetched_items.times_called == 1


async def test_no_items_found(get_random_products, experiments3, testpoint):
    experiments.random_products(
        experiments3, upper_shift='0', prefetch_limit=10,
    )

    @testpoint('prefetched_items')
    def prefetched_items(items):
        assert sorted(items) == []

    threshold = '10000'
    response = await get_random_products(threshold=threshold)
    assert not response['products']

    assert prefetched_items.times_called == 1


@pytest.mark.parametrize(
    'discount_value, is_found', [('0.01', True), ('1', False)],
)
async def test_discount(
        get_random_products,
        grocery_p13n,
        experiments3,
        testpoint,
        discount_value,
        is_found,
):
    experiments.random_products(
        experiments3, upper_shift='1', prefetch_limit=10,
    )

    @testpoint('prefetched_items')
    def prefetched_items(items):
        assert len(items) == 1

    grocery_p13n.add_modifier(product_id='product-1', value=discount_value)

    threshold = '2'
    response = await get_random_products(threshold=threshold)
    assert bool(response['products']) == is_found

    assert prefetched_items.times_called == 1


@pytest.mark.parametrize('in_stock', [0, 1])
async def test_no_stocks(
        get_random_products, experiments3, testpoint, in_stock,
):
    experiments.random_products(
        experiments3, upper_shift='1', prefetch_limit=10,
    )

    @testpoint('prefetched_items')
    def prefetched_items(items):
        # когда делаем prefetch, то товар находится. Потому что остатки не
        # учитываются в этот момент
        assert len(items) == 1

    product_1_price = '2'

    stocks = [
        {
            'in_stock': str(in_stock),
            'product_id': 'product-1',
            'quantity_limit': str(in_stock),
        },
    ]

    response = await get_random_products(
        threshold=product_1_price, stocks=stocks,
    )

    # товар либо есть, либо нет в зависимости от остатков
    assert bool(response['products']) == bool(in_stock)

    assert prefetched_items.times_called == 1


@pytest.mark.parametrize('in_stock', [0, 1])
async def test_metric(
        taxi_grocery_api_monitor, get_random_products, experiments3, in_stock,
):
    prefetch_limit = 10
    experiments.random_products(
        experiments3, upper_shift='1', prefetch_limit=prefetch_limit,
    )

    product_1_price = '2'

    stocks = [
        {
            'in_stock': str(in_stock),
            'product_id': 'product-1',
            'quantity_limit': str(in_stock),
        },
    ]

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_api_monitor, sensor=METRIC_NAME,
    ) as collector:
        await get_random_products(threshold=product_1_price, stocks=stocks)

    metric = collector.get_single_collected_metric()

    assert metric.value == 1
    assert metric.labels == {
        'country': 'Russia',
        'prefetch_limit': str(prefetch_limit),
        'found_count': str(in_stock),
        'sensor': METRIC_NAME,
    }


def _check_products_price(products, threshold, lower_shift, upper_shift):
    for product in products:
        price = product['pricing']['price']

        lower = Decimal(lower_shift) + Decimal(threshold)
        upper = lower + Decimal(upper_shift)

        assert lower <= Decimal(price) <= upper
