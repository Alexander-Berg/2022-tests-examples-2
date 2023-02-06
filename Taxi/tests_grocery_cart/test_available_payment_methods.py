import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments


DEFAULT_SERVICE_TOKEN = 'food_payment_c808ddc93ffec050bf0624a4d3f3707c'
CART_ID = '00000000-0000-0000-0000-000000000001'
DEPOT_ID = 'depot-id'
WMS_DEPOT_ID = 'wms-depot-id-lpm'

# Maximum latitude 90 N and 90 S
# Minimum longitude 180 W
# Maximum longitude 180 E
SOME_LOCATION = [170.99999, 79.99999]

RUSSIA_LOCATION = [37.573177, 55.736245]
ISRAEL_LOCATION = [34.766311, 32.058213]

RUSSIA_COUNTRY_ID = 225
ISRAEL_COUNTRY_ID = 181

CONFIG_FLOW_VERSION = 'eats_payments'


def _add_depot(overlord_catalog, grocery_depots, country_iso3):
    overlord_catalog.add_depot(
        depot_id=WMS_DEPOT_ID,
        legacy_depot_id=DEPOT_ID,
        country_iso3=country_iso3,
        currency=country_iso3,
    )
    grocery_depots.add_depot(
        100,
        depot_id=WMS_DEPOT_ID,
        legacy_depot_id=DEPOT_ID,
        country_iso3=country_iso3,
        currency=country_iso3,
        location=SOME_LOCATION,
    )
    overlord_catalog.add_location(
        depot_id=WMS_DEPOT_ID,
        legacy_depot_id=DEPOT_ID,
        location=SOME_LOCATION,
    )


@pytest.mark.parametrize(
    'country_iso3, country_iso2, region_id',
    [('RUS', 'RU', RUSSIA_COUNTRY_ID), ('ISR', 'IL', ISRAEL_COUNTRY_ID)],
)
async def test_geo_data_from_depot(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_depots,
        country_iso3,
        country_iso2,
        region_id,
):
    _add_depot(overlord_catalog, grocery_depots, country_iso3)

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/available-payment-methods',
        headers=common.TAXI_HEADERS,
        json={
            'cart_id': CART_ID,
            'order_flow_version': 'grocery_flow_v1',
            'location': SOME_LOCATION,
        },
    )

    assert response.status_code == 200

    assert response.json()['region_id'] == region_id
    assert response.json()['currency'] == country_iso3
    assert response.json()['country_iso2'] == country_iso2


@pytest.mark.parametrize(
    'location, region_id, currency',
    [
        (RUSSIA_LOCATION, RUSSIA_COUNTRY_ID, 'RUB'),
        (ISRAEL_LOCATION, ISRAEL_COUNTRY_ID, 'ILS'),
    ],
)
async def test_geo_data_geobase_fallback(
        taxi_grocery_cart, overlord_catalog, location, region_id, currency,
):
    overlord_catalog.set_depot_not_found()

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/available-payment-methods',
        headers=common.TAXI_HEADERS,
        json={
            'cart_id': CART_ID,
            'order_flow_version': 'grocery_flow_v1',
            'location': location,
        },
    )

    assert response.status_code == 200

    assert response.json()['region_id'] == region_id
    assert response.json()['currency'] == currency


@pytest.mark.parametrize(
    'country_iso3, region_id',
    [('RUS', RUSSIA_COUNTRY_ID), ('ISR', ISRAEL_COUNTRY_ID)],
)
@pytest.mark.parametrize(
    'order_flow_version', [CONFIG_FLOW_VERSION, 'grocery_flow_v1'],
)
async def test_service_token_from_config(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_depots,
        experiments3,
        order_flow_version,
        country_iso3,
        region_id,
):
    _add_depot(overlord_catalog, grocery_depots, country_iso3)

    config_order_flow_version = CONFIG_FLOW_VERSION
    config_country_iso3 = 'RUS'

    experiments.grocery_service_token(
        experiments3, config_order_flow_version, config_country_iso3,
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/available-payment-methods',
        headers=common.TAXI_HEADERS,
        json={
            'cart_id': CART_ID,
            'order_flow_version': order_flow_version,
            'location': SOME_LOCATION,
        },
    )

    assert response.status_code == 200
    assert response.json()['region_id'] == region_id

    service_token = response.json()['service_token']
    if (
            order_flow_version == config_order_flow_version
            and country_iso3 == config_country_iso3
    ):
        assert service_token == experiments.SERVICE_TOKEN_FROM_CONFIG
    else:
        assert service_token == experiments.DEFAULT_SERVICE_TOKEN_FROM_CONFIG


@pytest.mark.parametrize(
    'location, region_id',
    [
        (RUSSIA_LOCATION, RUSSIA_COUNTRY_ID),
        (ISRAEL_LOCATION, ISRAEL_COUNTRY_ID),
    ],
)
@pytest.mark.parametrize(
    'order_flow_version', [CONFIG_FLOW_VERSION, 'grocery_flow_v1'],
)
async def test_service_token_from_config_fallback_geobase(
        taxi_grocery_cart,
        overlord_catalog,
        experiments3,
        order_flow_version,
        location,
        region_id,
):
    overlord_catalog.set_depot_not_found()

    config_order_flow_version = CONFIG_FLOW_VERSION
    config_country_iso3 = 'RUS'

    experiments.grocery_service_token(
        experiments3, config_order_flow_version, config_country_iso3,
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/available-payment-methods',
        headers=common.TAXI_HEADERS,
        json={
            'cart_id': CART_ID,
            'order_flow_version': order_flow_version,
            'location': location,
        },
    )

    assert response.status_code == 200
    assert response.json()['region_id'] == region_id

    service_token = response.json()['service_token']
    if (
            order_flow_version == config_order_flow_version
            and location == RUSSIA_LOCATION
    ):
        assert service_token == experiments.SERVICE_TOKEN_FROM_CONFIG
    else:
        assert service_token == experiments.DEFAULT_SERVICE_TOKEN_FROM_CONFIG
