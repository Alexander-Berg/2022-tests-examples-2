import pytest

from .plugins import keys


EXP3_CALC_SETTINGS = pytest.mark.experiments3(
    name='grocery_delivery_conditions_calc_settings',
    consumers=['grocery-delivery-conditions/user_order_info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'check_taxi_price': True,
        'calc_route_to_pin': False,
        'get_geo_offer_zone': False,
        'get_surge': False,
        'get_delivery_eta': False,
    },
    is_config=True,
)

EXP3_STORE_SETTINGS = pytest.mark.experiments3(
    name='grocery_delivery_conditions_store_settings',
    consumers=['grocery-delivery-conditions/common'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'geohash_precision': 8, 'match_prev_conditions_ttl': 5},
    is_config=True,
)

EXP3_DELIVERY_CONDITIONS = pytest.mark.experiments3(
    name='grocery-surge-delivery-conditions',
    consumers=['grocery-delivery-conditions/delivery_conditions'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'enabled': True,
        'data': [keys.DEFAULT_DELIVERY_CONDITIONS],
    },
    is_config=True,
)
