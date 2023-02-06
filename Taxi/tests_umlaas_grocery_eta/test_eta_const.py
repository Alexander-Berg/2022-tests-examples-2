import pytest

from tests_umlaas_grocery_eta import consts


DEPOT_NOT_FOUND = 'DepotNotFound'
OFFER_ID = 'offer_id'
COOKING_TIME = 5


async def test_depot_eta_404(taxi_umlaas_grocery_eta):
    # grocery_depots mock is empty
    response = await taxi_umlaas_grocery_eta.post(
        '/internal/umlaas-grocery-eta/v1/depot-eta',
        json={'depot_id': '1', 'transport_type': 'pedestrian'},
    )
    assert response.status == 404
    assert response.json()['code'] == DEPOT_NOT_FOUND
    assert response.headers['X-YaTaxi-Error-Code'] == DEPOT_NOT_FOUND


async def test_delivery_eta_404(taxi_umlaas_grocery_eta):
    # grocery_depots mock is empty
    response = await taxi_umlaas_grocery_eta.post(
        '/internal/umlaas-grocery-eta/v1/delivery-eta',
        params={'offer_id': OFFER_ID, 'request_type': 'checkout'},
        json={
            'depot_id': '1',
            'transport_type': 'pedestrian',
            'user_location': [52.56, 39.60],
        },
    )
    assert response.status == 404
    assert response.json()['code'] == DEPOT_NOT_FOUND
    assert response.headers['X-YaTaxi-Error-Code'] == DEPOT_NOT_FOUND


async def test_checkout_eta_404(taxi_umlaas_grocery_eta):
    # grocery_depots mock is empty
    response = await taxi_umlaas_grocery_eta.post(
        '/internal/umlaas-grocery-eta/v1/checkout-eta',
        params={'offer_id': OFFER_ID},
        json={
            'depot_id': '1',
            'user_location': [52.56, 39.60],
            'cart': {
                'cart_id': 'e6a59113-503c-4d3e-8c59-000000000020',
                'delivery_type': 'eats_dispatch',
                'items': [],
                'delivery_zone_type': 'pedestrian',
            },
        },
    )
    assert response.status == 404
    assert response.json()['code'] == DEPOT_NOT_FOUND
    assert response.headers['X-YaTaxi-Error-Code'] == DEPOT_NOT_FOUND


async def test_depot_eta_const_default(
        taxi_umlaas_grocery_eta, grocery_depots,
):
    grocery_depots.add_depot(1)
    response = await taxi_umlaas_grocery_eta.post(
        '/internal/umlaas-grocery-eta/v1/depot-eta',
        json={'depot_id': '1', 'transport_type': 'pedestrian'},
    )
    assert response.status == 200
    # hardcoded default value
    assert response.json()['cooking_time'] == 10 * consts.MINUTE


async def test_delivery_eta_const_default(
        taxi_umlaas_grocery_eta, grocery_depots,
):
    grocery_depots.add_depot(1)
    response = await taxi_umlaas_grocery_eta.post(
        '/internal/umlaas-grocery-eta/v1/delivery-eta',
        params={'offer_id': OFFER_ID, 'request_type': 'checkout'},
        json={
            'depot_id': '1',
            'transport_type': 'pedestrian',
            'user_location': [52.56, 39.60],
        },
    )
    assert response.status == 200
    # hardcoded default value
    assert response.json() == {
        'promise': {'max': 20 * consts.MINUTE, 'min': 10 * consts.MINUTE},
        'cooking_time': 10 * consts.MINUTE,
        'delivery_time': 5 * consts.MINUTE,
        'total_time': 15 * consts.MINUTE,
    }


@pytest.mark.parametrize('transport_type', ['pedestrian', 'yandex_taxi'])
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='grocery_eta',
    consumers=['umlaas-grocery-eta/depot-eta'],
    default_value={'const_prediction': {'cooking_time': COOKING_TIME}},
)
async def test_depot_eta_const_experiment_value(
        taxi_umlaas_grocery_eta, grocery_depots, transport_type,
):
    grocery_depots.add_depot(1)
    response = await taxi_umlaas_grocery_eta.post(
        '/internal/umlaas-grocery-eta/v1/depot-eta',
        json={'depot_id': '1', 'transport_type': transport_type},
    )
    assert response.status == 200
    assert response.json()['cooking_time'] == COOKING_TIME * consts.MINUTE


@pytest.mark.parametrize('transport_type', ['pedestrian', 'yandex_taxi'])
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='grocery_eta',
    consumers=['umlaas-grocery-eta/delivery-eta'],
    default_value={'const_prediction': {'cooking_time': COOKING_TIME}},
)
async def test_delivery_eta_const_experiment_value(
        taxi_umlaas_grocery_eta, grocery_depots, transport_type,
):
    grocery_depots.add_depot(1)
    response = await taxi_umlaas_grocery_eta.post(
        '/internal/umlaas-grocery-eta/v1/delivery-eta',
        params={'offer_id': OFFER_ID, 'request_type': 'checkout'},
        json={
            'depot_id': '1',
            'transport_type': transport_type,
            'user_location': [52.56, 39.60],
        },
    )
    assert response.status == 200
    assert response.json() == {
        'promise': {'max': 20 * consts.MINUTE, 'min': 10 * consts.MINUTE},
        'cooking_time': 5 * consts.MINUTE,
        'delivery_time': 10 * consts.MINUTE,
        'total_time': 20 * consts.MINUTE,
    }
