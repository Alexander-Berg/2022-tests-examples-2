# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_grocery_cart import common
from tests_grocery_cart import helpers
from tests_grocery_cart.plugins import keys


def _metric(name):
    return f'grocery_cart_{name}'


CREATED_CARTS = _metric('created_carts')
CHECKED_OUT_CARTS = _metric('unavailable_for_check_out_carts')


CART_ID = '00000000-0000-0000-0000-d98013100500'
OFFER_ID = 'offer-id'
CART_VERSION = 4
DEPOT_ID = '2809'


@pytest.fixture(name='run_cart_update')
def _run_cart_update(taxi_grocery_cart):
    async def _run():
        await taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/update',
            json={
                'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
                'items': [],
            },
            headers=common.TAXI_HEADERS,
        )

    return _run


@pytest.fixture(name='run_cart_checkout')
def _run_cart_checkout(taxi_grocery_cart):
    async def _run(cart, overlord_catalog):
        item_id = 'item_id_1'
        quantity = 2
        price = '345'

        overlord_catalog.add_product(
            product_id=item_id, price=price, in_stock='2',
        )

        await cart.modify({item_id: {'q': quantity, 'p': price}})
        json = {
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': cart.cart_id,
            'cart_version': cart.cart_version,
            'offer_id': cart.offer_id,
        }
        await taxi_grocery_cart.post(
            '/internal/v2/cart/checkout',
            headers=common.TAXI_HEADERS,
            json=json,
        )

    return _run


@pytest.mark.parametrize(
    'country_iso3,region_id', [('RUS', 47), ('ISR', 131), ('FRA', 10502)],
)
async def test_created_carts(
        taxi_grocery_cart,
        pgsql,
        taxi_grocery_cart_monitor,
        run_cart_update,
        country_iso3,
        region_id,
        grocery_depots,
):
    grocery_depots.add_depot(
        100,
        legacy_depot_id=DEPOT_ID,
        country_iso3=country_iso3,
        region_id=region_id,
    )
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        100,
        legacy_depot_id=DEPOT_ID,
        location=keys.DEFAULT_DEPOT_LOCATION_OBJ,
        country_iso3=country_iso3,
        region_id=region_id,
    )
    await taxi_grocery_cart.invalidate_caches()

    country_name = helpers.get_country(country_iso3)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_cart_monitor,
            sensor=CREATED_CARTS,
            labels={'country': country_name},
    ) as collector:
        await run_cart_update()

    metric = collector.get_single_collected_metric()

    assert metric.value == 1
    assert metric.labels == {
        'country': country_name,
        'city_name': helpers.get_city_by_region_id(region_id),
        'sensor': CREATED_CARTS,
    }


@pytest.mark.parametrize(
    'country_iso3,region_id', [('RUS', 47), ('ISR', 131), ('FRA', 10502)],
)
async def test_checked_out_carts(
        taxi_grocery_cart,
        pgsql,
        cart,
        overlord_catalog,
        taxi_grocery_cart_monitor,
        run_cart_checkout,
        country_iso3,
        region_id,
        grocery_depots,
):
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        100,
        legacy_depot_id=DEPOT_ID,
        location=keys.DEFAULT_DEPOT_LOCATION_OBJ,
        country_iso3=country_iso3,
        region_id=region_id,
    )
    await taxi_grocery_cart.invalidate_caches()

    country_name = helpers.get_country(country_iso3)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_cart_monitor,
            sensor=CHECKED_OUT_CARTS,
            labels={'country': country_name},
    ) as collector:
        await run_cart_checkout(cart, overlord_catalog)

    metric = collector.get_single_collected_metric()

    assert metric.value == 1
    assert metric.labels == {
        'country': country_name,
        'city_name': helpers.get_city_by_region_id(region_id),
        'reason': 'no_reason',
        'sensor': CHECKED_OUT_CARTS,
    }
