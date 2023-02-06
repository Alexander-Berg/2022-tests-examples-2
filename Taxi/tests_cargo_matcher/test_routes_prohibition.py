import copy
from typing import Any
from typing import Dict

import pytest


HEADERS = {'Accept-Language': 'ru'}

ROUTES_PROHIBITION_REQUEST: Dict[str, Any] = {
    'route_points': [
        {'coordinates': [37.1, 55.1]},
        {'coordinates': [37.2, 55.3]},
    ],
    'tariffs': ['express', 'cargo'],
}

INTERNATIONAL_ORDER_PROHIBITION_EXP_VAL = {
    'countries': [
        {
            'country': 'kg',
            'tanker_key_order_to_country': (
                'estimating.international_orders_prohibition_to_kg'
            ),
            'tanker_key_order_from_country': (
                'estimating.international_orders_prohibition_from_kg'
            ),
            'tariffs': ['express', 'cargo', 'cargocorp'],
        },
    ],
}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_matcher_international_orders_prohibition',
    consumers=['cargo-matcher/international-orders-prohibition'],
    clauses=[],
    is_config=True,
    default_value=INTERNATIONAL_ORDER_PROHIBITION_EXP_VAL,
)
@pytest.mark.parametrize(
    'index, coordinates, result',
    [
        ([], [], []),
        (
            [0],
            [[74.61, 42.87], None],
            [
                {
                    'prohibition_reason': (
                        'estimating.international_orders_prohibition_from_kg'
                    ),
                    'tariff': 'express',
                },
                {
                    'prohibition_reason': (
                        'estimating.international_orders_prohibition_from_kg'
                    ),
                    'tariff': 'cargo',
                },
            ],
        ),
        (
            [1],
            [None, [74.61, 42.87]],
            [
                {
                    'prohibition_reason': (
                        'estimating.international_orders_prohibition_to_kg'
                    ),
                    'tariff': 'express',
                },
                {
                    'prohibition_reason': (
                        'estimating.international_orders_prohibition_to_kg'
                    ),
                    'tariff': 'cargo',
                },
            ],
        ),
        ([0, 1], [[74.61, 42.87], [74.61, 42.865]], []),
    ],
)
async def test_routes_prohibition(
        mockserver,
        taxi_cargo_matcher,
        index: list,
        coordinates: list,
        result: str,
):
    request = copy.deepcopy(ROUTES_PROHIBITION_REQUEST)
    for i in index:
        request['route_points'][i]['coordinates'] = coordinates[i]
    response = await taxi_cargo_matcher.post(
        '/v1/routes-prohibition', json=request, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'forbidden_tariffs': result}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_matcher_international_orders_prohibition',
    consumers=['cargo-matcher/international-orders-prohibition'],
    clauses=[],
    is_config=True,
    default_value=INTERNATIONAL_ORDER_PROHIBITION_EXP_VAL,
)
@pytest.mark.parametrize(
    'index, coordinates, result, code',
    [([0], [[42.295469, 69.484073], None], {'code': 'bad_request'}, 400)],
)
async def test_bad_coordinates_routes_prohibition(
        mockserver,
        taxi_cargo_matcher,
        index: list,
        coordinates: list,
        result: dict,
        code: int,
):
    request = copy.deepcopy(ROUTES_PROHIBITION_REQUEST)
    for i in index:
        request['route_points'][i]['coordinates'] = coordinates[i]
    response = await taxi_cargo_matcher.post(
        '/v1/routes-prohibition', json=request, headers=HEADERS,
    )
    assert response.status_code == code
    assert response.json()['code'] == result['code']
    assert 'message' in response.json()
