# pylint: disable=import-only-modules
# flake8: noqa F401

import pytest

DEFAULT_HEADERS = {'Accept-Language': 'en', 'X-Remote-IP': '12.34.56.78'}

AUTH_HEADERS_V1 = {
    'Accept-Language': 'ru',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '10.09 (2147483647)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}

TEST_SIMPLE_JSON_PERFORMER_RESULT = {
    'car_id': 'car_id1',
    'car_model': 'some_car_model',
    'car_number': 'some_car_number',
    'driver_id': 'driver_id1',
    'lookup_version': 1,
    'name': 'Kostya',
    'order_alias_id': '1234',
    'order_id': '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
    'park_clid': 'park_clid1',
    'park_id': 'park_id1',
    'park_name': 'some_park_name',
    'park_org_name': 'some_park_org_name',
    'phone_pd_id': 'phone_pd_id',
    'revision': 1,
    'tariff_class': 'cargo',
    'transport_type': 'electric_bicycle',
}

TIMER_CONFIG_ETA_TEXT = pytest.mark.experiments3(
    name='cargo_orders_taximeter_timers_settings',
    consumers=['cargo-orders/build-timer-action'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'eta': {
            'before_calculated': {},
            'after_calculated': {},
            'after_passed': {},
        },
        'waiting': {'free': {}, 'paid': {}, 'paid_end': {}},
    },
    is_config=True,
)
