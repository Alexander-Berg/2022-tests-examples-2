import pytest

from . import utils


@pytest.mark.parametrize(
    'has_weight',
    [
        pytest.param(True, id='with_weight'),
        pytest.param(False, id='without_weight'),
    ],
)
async def test_eta(
        mockserver,
        taxi_eats_cart,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
        load_json,
        has_weight,
):
    eats_order_stats()
    core_resp = local_services.core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    if not has_weight:
        for item in core_resp['place_menu_items']:
            del item['measure']
    local_services.core_items_response = core_resp
    local_services.set_place_slug('place123')
    local_services.core_items_request = ['232323', '2']

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eta')
    def cart_eta(request):
        assert request.query['request_type'] == 'default'
        assert request.query['service_name'] == 'eats-cart'
        req = request.json['requested_times'][0]
        assert 'cart' in req
        expected_cart = [
            {
                'item': {
                    'id': 232323,
                    'weight': {'mass': 1.0, 'type': 'kg'},
                    'price': 50.0,
                    'currency': '₽',
                    'name': 'Сет Плов и долма',
                },
                'quantity': 2,
            },
        ]
        if not has_weight:
            for item in expected_cart:
                item['item']['weight']['mass'] = 0
        assert expected_cart == req['cart']
        return {
            'exp_list': [],
            'request_id': 'request_id',
            'provider': 'testsuite',
            'predicted_times': [
                {
                    'id': 123,
                    'times': {
                        'total_time': 65,
                        'cooking_time': 20,
                        'delivery_time': 45,
                        'boundaries': {'min': 50, 'max': 60},
                    },
                },
            ],
        }

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(),
        json=dict(item_id=232323, **utils.ITEM_PROPERTIES),
    )

    assert cart_eta.times_called == 1

    assert response.status_code == 200

    eats_cart_cursor.execute(utils.SELECT_CART)
    carts = eats_cart_cursor.fetchall()

    assert len(carts) == 1
    cart = carts[0]
    assert cart['delivery_time'] == '(50,60)'

    resp = response.json()['cart']
    assert resp['delivery_time'] == {'max': 60, 'min': 50}
