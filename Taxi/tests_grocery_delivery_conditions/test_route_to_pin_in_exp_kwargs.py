import pytest

from . import configs
from .plugins import keys


@pytest.mark.experiments3(
    name='grocery_delivery_conditions_calc_settings',
    consumers=['grocery-delivery-conditions/user_order_info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'check_taxi_price': False,
        'calc_route_to_pin': True,
        'get_geo_offer_zone': False,
        'get_surge': False,
        'get_delivery_eta': False,
    },
    is_config=True,
)
@configs.EXP3_STORE_SETTINGS
@configs.EXP3_DELIVERY_CONDITIONS
async def test_route_to_pin_in_exp_kwargs(
        taxi_grocery_delivery_conditions, mockserver, experiments3,
):
    route_to_pin = 10

    @mockserver.json_handler(
        '/grocery-routing/internal/grocery-routing/v1/route',
    )
    def _get_route(_request):
        return {'distance': route_to_pin, 'eta': 60}

    experiments3.add_config(
        name='grocery_delivery_conditions_user_type',
        consumers=['grocery-delivery-conditions/user_order_info_extended'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'type': 'string'},
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_delivery_conditions_user_type',
    )

    json = {'position': keys.DEFAULT_DEPOT_LOCATION, 'meta': {}}

    headers = {'X-Yandex-UID': '12345'}

    response = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create',
        json=json,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()['meta']['route_to_pin'] == route_to_pin
    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    matched_kwargs = match_tries[0].kwargs

    assert matched_kwargs['route_to_pin'] == route_to_pin
