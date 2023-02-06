import copy

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks import grocery_cart as mock_grocery_cart
import pytest


from tests_grocery_market_gw import common


async def test_proxies_grocery_cart_update_200(
        taxi_grocery_market_gw, grocery_cart, personal,
):
    """ Proxies request to grocery-cart /update
    proxies response from grocery-cart """

    cart_id = '01234567-89ab-cdef-000a-000000000001'
    order_id = '0123456789-grocery'
    idempotency_token = 'some-idempotency-token'
    grocery_cart.add_cart(cart_id, order_id=order_id)

    request_json = {
        'cart_id': cart_id,
        'position': {'location': [55, 37]},
        'offer_id': 'some-offer-id',
        'cart_version': 1,
        'items': [
            {
                'item_id': 'some-item-id',
                'price': '123.456',
                'quantity': '10',
                'currency': 'RUB',
                'cashback': '7.89',
            },
        ],
    }
    cart_request_json = copy.deepcopy(request_json)
    for item in cart_request_json['items']:
        item['id'] = item['item_id']
        item.pop('item_id')

    personal.check_request(
        personal_phone_id=common.DEFAULT_PERSONAL_PHONE_ID,
        phone=common.DEFAULT_HEADERS['Phone-Number'],
    )
    grocery_cart.check_request(
        cart_request_json,
        headers={
            'X-Idempotency-Token': idempotency_token,
            **common.DAFAULT_AUTH_CONTEXT,
        },
        handler=mock_grocery_cart.Handler.update,
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/update',
        json=request_json,
        headers={
            'X-Idempotency-Token': idempotency_token,
            **common.DEFAULT_HEADERS,
        },
    )

    assert grocery_cart.mock_update_times_called() == 1
    assert response.status == 200
    assert response.json()['cart_id'] == cart_id


async def test_grocery_cart_update_negative_quantity(
        taxi_grocery_market_gw, grocery_cart, personal,
):
    """ quantity should be >= 0 in request
    to grocery-cart """

    cart_id = '01234567-89ab-cdef-000a-000000000001'
    order_id = '0123456789-grocery'
    idempotency_token = 'some-idempotency-token'
    grocery_cart.add_cart(cart_id, order_id=order_id)

    request_json = {
        'cart_id': cart_id,
        'position': {'location': [55, 37]},
        'offer_id': 'some-offer-id',
        'cart_version': 1,
        'items': [
            {
                'item_id': 'some-item-id',
                'price': '123.456',
                'quantity': '-10',
                'currency': 'RUB',
                'cashback': '7.89',
            },
        ],
    }
    cart_request_json = copy.deepcopy(request_json)
    for item in cart_request_json['items']:
        item['id'] = item['item_id']
        item['quantity'] = str(max(0, int(item['quantity'])))
        item.pop('item_id')

    personal.check_request(
        personal_phone_id=common.DEFAULT_PERSONAL_PHONE_ID,
        phone=common.DEFAULT_HEADERS['Phone-Number'],
    )
    grocery_cart.check_request(
        cart_request_json,
        headers={
            'X-Idempotency-Token': idempotency_token,
            **common.DAFAULT_AUTH_CONTEXT,
        },
        handler=mock_grocery_cart.Handler.update,
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/update',
        json=request_json,
        headers={
            'X-Idempotency-Token': idempotency_token,
            **common.DEFAULT_HEADERS,
        },
    )

    assert grocery_cart.mock_update_times_called() == 1
    assert response.status == 200
    assert response.json()['cart_id'] == cart_id


@pytest.mark.parametrize(
    'error_status, error_code',
    [(400, 'BAD_REQUEST'), (404, 'CART_NOT_FOUND'), (409, 'CONFLICT')],
)
async def test_proxies_grocery_cart_update_client_error(
        taxi_grocery_market_gw, mockserver, error_status, error_code,
):
    """ Proxies request to grocery-cart /update
    proxies 4xx-error from grocery-cart """

    error_message = 'some cart error'

    @mockserver.json_handler('/grocery-cart/lavka/v1/cart/v1/update')
    def _mock_grocery_cart_update_error(request):
        code = 'CART_NOT_FOUND' if error_status == 404 else 'NO_CODE'
        return mockserver.make_response(
            json={'code': code, 'message': error_message}, status=error_status,
        )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/update',
        json={'position': {'location': [55, 37]}, 'items': []},
        headers={'X-Idempotency-Token': 'some-idempotency-token'},
    )
    assert _mock_grocery_cart_update_error.times_called == 1
    assert response.status == error_status
    response_json = response.json()
    assert response_json['code'] == error_code
    assert response_json['message'] == error_message


async def test_proxies_grocery_cart_update_500(
        taxi_grocery_market_gw, mockserver,
):
    """ Proxies request to grocery-cart /update
    throws on grocery-cart error """

    @mockserver.json_handler('/grocery-cart/lavka/v1/cart/v1/update')
    def _mock_grocery_cart_update_error(request):
        return mockserver.make_response(status=500)

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/update',
        json={'position': {'location': [55, 37]}, 'items': []},
        headers={'X-Idempotency-Token': 'some-idempotency-token'},
    )

    assert _mock_grocery_cart_update_error.has_calls is True
    assert response.status == 500
