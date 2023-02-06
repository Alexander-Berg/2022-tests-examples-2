# pylint: disable=import-error

from dap_tools.dap import dap_fixture  # noqa: F401 C5521
import pytest

ENDPOINT = '/driver/v1/fleet-orders-guarantee/v1/available-orders/list'

TRANSLATIONS = {
    'preorder': {'en': 'Pre-order', 'ru': 'Предзаказ'},
    'from': {'en': 'From', 'ru': 'Откуда'},
    'to': {'en': 'To', 'ru': 'Куда'},
    'distance': {'en': 'Distance', 'ru': 'Расстояние'},
    'km': {'en': 'km', 'ru': 'км'},
    'price': {'en': 'Price', 'ru': 'Цена'},
    'activity': {'en': 'Activity', 'ru': 'Активность'},
    'tariff_class': {'en': 'Tariff', 'ru': 'Тариф'},
    'econom': {'en': 'Econom', 'ru': 'Эконом'},
}

PARKS_RESPONSE = {
    'city_id': 'city_id',
    'country_id': 'country_id',
    'demo_mode': False,
    'driver_partner_source': 'yandex',
    'id': 'park_id',
    'is_active': True,
    'is_billing_enabled': False,
    'is_franchising_enabled': False,
    'locale': 'en',
    'login': 'login',
    'name': 'name',
    'tz_offset': 3,
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}


@pytest.mark.pgsql(
    'fleet_orders_guarantee',
    files=['guarantee_order.sql', 'order_candidates.sql'],
)
@pytest.mark.translations(
    taximeter_backend_fleet_orders_guarantee=TRANSLATIONS,
)
async def test_ok(taxi_fleet_orders_guarantee, dap, load_json, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks')
    def _mock_parks(request):
        return PARKS_RESPONSE

    taxi_fleet_orders_guarantee = dap.create_driver_wrapper(
        taxi_fleet_orders_guarantee,
        driver_uuid='driver_id',
        driver_dbid='park_id',
        user_agent='Taximeter 9.1 (1234)',
    )

    query = {
        'interval': {
            'from': '2021-09-02T17:00:00+00:00',
            'to': '2021-09-02T19:00:00+00:00',
        },
    }

    response = await taxi_fleet_orders_guarantee.post(
        ENDPOINT, json=query, headers={'Accept-Language': 'ru'},
    )

    expected_response = load_json('test_ok.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.pgsql(
    'fleet_orders_guarantee',
    files=['guarantee_order.sql', 'order_candidates.sql'],
)
@pytest.mark.translations(
    taximeter_backend_fleet_orders_guarantee=TRANSLATIONS,
)
async def test_ok_default_locale_and_empty_locations_to(
        taxi_fleet_orders_guarantee, dap, load_json, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks')
    def _mock_parks(request):
        return PARKS_RESPONSE

    taxi_fleet_orders_guarantee = dap.create_driver_wrapper(
        taxi_fleet_orders_guarantee,
        driver_uuid='driver_id',
        driver_dbid='park_id',
        user_agent='Taximeter 9.1 (1234)',
    )

    query = {
        'interval': {
            'from': '2021-09-02T19:00:00+00:00',
            'to': '2021-09-02T20:30:00+00:00',
        },
    }

    response = await taxi_fleet_orders_guarantee.post(
        ENDPOINT, json=query, headers={'Accept-Language': 'de'},
    )

    expected_response = load_json('test_ok_empty_locations_to.json')
    assert response.status_code == 200
    assert response.json() == expected_response


async def test_failed_invalid_interval(
        taxi_fleet_orders_guarantee, dap, load_json, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks')
    def _mock_parks(request):
        return PARKS_RESPONSE

    taxi_fleet_orders_guarantee = dap.create_driver_wrapper(
        taxi_fleet_orders_guarantee,
        driver_uuid='driver_id',
        driver_dbid='park_id',
        user_agent='Taximeter 9.1 (1234)',
    )

    query = {
        'interval': {
            'from': '2021-09-02T23:00:00+00:00',
            'to': '2021-09-02T19:00:00+00:00',
        },
    }

    response = await taxi_fleet_orders_guarantee.post(
        ENDPOINT, json=query, headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_interval',
        'message': '"from" must be less then "to"',
    }
