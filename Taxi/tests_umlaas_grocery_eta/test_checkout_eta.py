import pytest

from tests_umlaas_grocery_eta import consts


URL = '/internal/umlaas-grocery-eta/v1/checkout-eta'
CONSUMER = 'umlaas-grocery-eta/delivery-eta'


def exp3_decorator(value):
    return pytest.mark.experiments3(
        name='grocery_eta',
        consumers=[CONSUMER],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        is_config=True,
        default_value=value,
    )


def exp3_without_external(ml_resource):
    return exp3_decorator(
        {
            'ml_model': {
                'ml_model_resource_name': ml_resource,
                'sources': {},
                'cooking_time': {'lower_bound': 6, 'upper_bound': 60},
                'delivery_time': {'upper_bound': 60},
                'total_time': {'upper_bound': 100500, 'window_width': 10},
            },
        },
    )


@exp3_without_external('grocery_eta_pedestrian_zone_resources_v2')
async def test_checkout_eta_cart_is_provided_to_ml_request(
        taxi_umlaas_grocery_eta, grocery_depots, testpoint,
):
    @testpoint('checkout-eta-ml-request')
    def checkout_eta_ml_request(ml_request):
        pass

    grocery_depots.add_depot(consts.DEPOT_ID, auto_add_zone=False)
    cart = {
        'cart_id': 'e6a59113-503c-4d3e-8c59-000000000020',
        'delivery_type': 'eats_dispatch',
        'items': [
            {
                'id': 'item0',
                'product_key': {'shelf_type': 'store', 'id': 'item0_id'},
                'title': 'сырок больше не Александров',
                'quantity': '4',
                'width': 40,
                'height': 40,
                'depth': 150,
                'gross_weight': 125,
            },
        ],
        'delivery_zone_type': 'pedestrian',
        'logistic_tags': ['hot', 'just_tag'],
    }
    response = await taxi_umlaas_grocery_eta.post(
        URL,
        json={
            'depot_id': str(consts.DEPOT_ID),
            'transport_type': 'pedestrian',
            'user_location': consts.USER_LOCATION,
            'cart': cart,
        },
        params={'offer_id': '1abc1'},
    )
    assert response.status == 200
    data = response.json()
    assert data == {
        'cooking_time': 6 * consts.MINUTE,
        'promise': {'min': 0, 'max': 10 * consts.MINUTE},
        'delivery_time': 0,
        'total_time': 6 * consts.MINUTE + 0,  # + delivery_time
    }

    ml_request = (await checkout_eta_ml_request.wait_call())['ml_request']
    assert ml_request, 'error retrieving ML request'
    assert 'cart' in ml_request
    assert cart == ml_request['cart']
