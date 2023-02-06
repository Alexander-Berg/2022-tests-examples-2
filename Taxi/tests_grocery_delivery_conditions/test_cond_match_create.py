from . import configs
from .plugins import keys


@configs.EXP3_CALC_SETTINGS
@configs.EXP3_STORE_SETTINGS
@configs.EXP3_DELIVERY_CONDITIONS
async def test_dummy(taxi_grocery_delivery_conditions):
    json = {'position': keys.DEFAULT_DEPOT_LOCATION, 'meta': {}}

    headers = {'X-Yandex-UID': '12345'}

    response = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create',
        json=json,
        headers=headers,
    )
    assert response.status_code == 200

    expected = keys.DEFAULT_DELIVERY_CONDITIONS['payload']
    data = response.json()['data']
    assert data['is_surge'] == expected['surge']
    assert data['promise_times']['total_eta_max'] == int(
        expected['max_eta_minutes'],
    )
    assert data['promise_times']['total_eta_min'] == int(
        expected['min_eta_minutes'],
    )
    assert data['steps'] == sorted(
        [
            {
                'cart_price': c['order_cost'],
                'delivery_price': c['delivery_cost'],
            }
            for c in expected['delivery_conditions']
        ],
        key=lambda step: step['cart_price'],
    )


@configs.EXP3_CALC_SETTINGS
@configs.EXP3_STORE_SETTINGS
async def test_duplicates_dummy(
        taxi_grocery_delivery_conditions, experiments3,
):
    req = {'position': keys.DEFAULT_DEPOT_LOCATION, 'meta': {}}

    experiments3.add_config(
        name='grocery-surge-delivery-conditions',
        consumers=['grocery-delivery-conditions/delivery_conditions'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={
            'enabled': True,
            'data': [keys.DEFAULT_DELIVERY_CONDITIONS],
        },
    )

    response1 = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create', json=req,
    )
    assert response1.status_code == 200

    req['position']['lat'] += 0.00005
    req['position']['lon'] -= 0.0001
    experiments3.add_config(
        name='grocery-surge-delivery-conditions',
        consumers=['grocery-delivery-conditions/delivery_conditions'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'enabled': True, 'data': []},
    )
    response2 = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create', json=req,
    )
    assert response2.status_code == 200
    assert response1.json()['data'] == response2.json()['data']
    assert (
        response1.json()['delivery_conditions_id']
        != response2.json()['delivery_conditions_id']
    )


@configs.EXP3_CALC_SETTINGS
@configs.EXP3_STORE_SETTINGS
async def test_external_id(taxi_grocery_delivery_conditions, experiments3):
    experiments3.add_config(
        name='grocery-surge-delivery-conditions',
        consumers=['grocery-delivery-conditions/delivery_conditions'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={
            'enabled': True,
            'data': [keys.DEFAULT_DELIVERY_CONDITIONS],
        },
    )
    await taxi_grocery_delivery_conditions.invalidate_caches()

    req = {
        'position': keys.DEFAULT_DEPOT_LOCATION,
        'meta': {},
        'external_id': {'id': 'qwerty', 'type': 'some'},
    }
    response1 = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create', json=req,
    )
    assert response1.status_code == 200

    experiments3.add_config(
        name='grocery-surge-delivery-conditions',
        consumers=['grocery-delivery-conditions/delivery_conditions'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'enabled': True, 'data': []},
    )
    await taxi_grocery_delivery_conditions.invalidate_caches()

    req['position']['lat'] += 0.0012
    req['position']['lon'] -= 0.001
    response2 = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create', json=req,
    )
    assert response2.status_code == 200
    assert response1.json() == response2.json()  # even id are eq
