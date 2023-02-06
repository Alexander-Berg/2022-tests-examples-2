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
        'calc_route_to_pin': False,
        'get_geo_offer_zone': False,
        'get_surge': False,
        'get_delivery_eta': True,
    },
    is_config=True,
)
@configs.EXP3_STORE_SETTINGS
@configs.EXP3_DELIVERY_CONDITIONS
async def test_umlass_answer_in_v1_match_create(
        taxi_grocery_delivery_conditions, mockserver,
):
    umlass_resp = {
        'total_time': 30,
        'cooking_time': 11,
        'delivery_time': 12,
        'promise': {'min': 10 * 60, 'max': 20 * 60},
    }

    @mockserver.json_handler(
        '/umlaas-grocery-eta/internal/umlaas-grocery-eta/v1/delivery-eta',
    )
    def _umlaas_grocery_eta(request):
        return umlass_resp

    json = {
        'position': keys.DEFAULT_DEPOT_LOCATION,
        'meta': {},
        'external_id': {'id': 'qwerty', 'type': 'some'},
    }

    headers = {'X-Yandex-UID': '12345'}

    response = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create',
        json=json,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()['meta']['delivery_eta'] == umlass_resp


@pytest.mark.experiments3(
    name='grocery_delivery_conditions_calc_settings',
    consumers=['grocery-delivery-conditions/user_order_info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'check_taxi_price': False,
        'calc_route_to_pin': False,
        'get_geo_offer_zone': False,
        'get_surge': False,
        'get_delivery_eta': False,
    },
    is_config=True,
)
@configs.EXP3_STORE_SETTINGS
@configs.EXP3_DELIVERY_CONDITIONS
async def test_umlass_answer_not_in_v1_match_create(
        taxi_grocery_delivery_conditions, mockserver,
):
    umlass_resp = {
        'total_time': 30,
        'cooking_time': 11,
        'delivery_time': 12,
        'promise': {'min': 10 * 60, 'max': 20 * 60},
    }

    @mockserver.json_handler(
        '/umlaas-grocery-eta/internal/umlaas-grocery-eta/v1/delivery-eta',
    )
    def _umlaas_grocery_eta(request):
        return umlass_resp

    json = {'position': keys.DEFAULT_DEPOT_LOCATION, 'meta': {}}

    headers = {'X-Yandex-UID': '12345'}

    response = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create',
        json=json,
        headers=headers,
    )
    assert response.status_code == 200
    assert 'delivery_eta' not in response.json()['meta']
