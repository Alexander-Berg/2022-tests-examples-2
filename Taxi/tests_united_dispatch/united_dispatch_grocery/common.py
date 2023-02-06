import pytest

NOW = '2020-02-02T00:00:00+00:00'
FIVE_MINUTES_AGO = '2020-02-01T23:55:00+00:00'
NOW_PAST_ONE_HOUR = '2020-02-02T01:00:00+00:00'

VALID_CUSTOM_CTX = {
    'depot_id': '123',
    'dispatch_id': '111',
    'order_id': '222-grocery',
    'dispatch_wave': 0,
    'weight': 0.0,
    'created': FIVE_MINUTES_AGO,
    'delivery_flags': {},
    'region_id': 1,
}

BIG_WEIGHT_CUSTOM_CTX = {
    'depot_id': '123',
    'dispatch_id': '111',
    'order_id': '222-grocery',
    'dispatch_wave': 0,
    'weight': 9000.0,
    'created': FIVE_MINUTES_AGO,
    'delivery_flags': {},
    'region_id': 1,
}

FOR_EACH_ALGORITHM = pytest.mark.parametrize(
    ['algorithm'],
    [('match_couriers_to_orders_v1',), ('match_couriers_to_orders_v2',)],
)


def set_candidate_limits(
        *,
        max_weight=25000,
        max_volume=1000,
        max_distance=10000,
        speed=2.3,
        dropoff_time=300,
):
    return pytest.mark.experiments3(
        name='united_dispatch_grocery_candidate_properties',
        consumers=['united-dispatch/grocery_candidate_kwargs'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'max_weight': max_weight,
            'max_volume': max_volume,
            'max_distance': max_distance,
            'speed': speed,
            'dropoff_time': dropoff_time,
        },
        is_config=True,
    )


def set_common_limits(
        *,
        max_orders=2,
        max_grocery_orders=2,
        max_market_orders=2,
        cte_limit=60 * 60 * 60,
        distance_diff_limit=100000,
):
    return pytest.mark.experiments3(
        name='united_dispatch_grocery_common_limits',
        consumers=['united-dispatch/grocery_algorithm_kwargs'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'max_orders': max_orders,
            'max_grocery_orders': max_grocery_orders,
            'max_market_orders': max_market_orders,
            'cte_limit': cte_limit,
            'distance_diff_limit': distance_diff_limit,
        },
        is_config=True,
    )
