# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks import grocery_cart as mock_grocery_cart

from tests_grocery_market_gw import common


async def test_proxies_grocery_cart_restore_200(
        taxi_grocery_market_gw, grocery_cart, personal,
):
    """ Proxies request to grocery-cart /restore
    proxies response from grocery-cart """

    cart_id = '01234567-89ab-cdef-000a-000000000001'
    order_id = '0123456789-grocery'
    grocery_cart.add_cart(cart_id, order_id=order_id)

    request_json = {
        'order_id': order_id,
        'position': {'location': [55, 37]},
        'offer_id': 'some-offer-id',
    }

    personal.check_request(
        personal_phone_id=common.DEFAULT_PERSONAL_PHONE_ID,
        phone=common.DEFAULT_HEADERS['Phone-Number'],
    )
    grocery_cart.check_request(
        request_json,
        headers=common.DAFAULT_AUTH_CONTEXT,
        handler=mock_grocery_cart.Handler.restore,
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/restore',
        json=request_json,
        headers=common.DEFAULT_HEADERS,
    )

    assert grocery_cart.mock_restore_times_called() == 1
    assert response.status == 200
    assert response.json()['cart_id'] == cart_id


async def test_proxies_grocery_cart_restore_404(
        taxi_grocery_market_gw, grocery_cart, personal,
):
    """ Proxies request to grocery-cart /restore
    proxies 404-error from grocery-cart """

    request_json = {
        'position': {'location': [55, 37]},
        'order_id': '0123456789-grocery',
    }

    personal.check_request(
        personal_phone_id=common.DEFAULT_PERSONAL_PHONE_ID,
        phone=common.DEFAULT_HEADERS['Phone-Number'],
    )
    grocery_cart.check_request(
        request_json,
        headers=common.DAFAULT_AUTH_CONTEXT,
        handler=mock_grocery_cart.Handler.restore,
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/restore',
        json=request_json,
        headers=common.DEFAULT_HEADERS,
    )
    assert grocery_cart.mock_restore_times_called() == 1
    assert response.status == 404
    assert response.json() == {
        'code': 'CART_NOT_FOUND',
        'message': 'Cart not found',
    }


async def test_proxies_grocery_cart_restore_500(
        taxi_grocery_market_gw, mockserver,
):
    """ Proxies request to grocery-cart /restore
    throws on grocery-cart error """

    @mockserver.json_handler('/grocery-cart/lavka/v1/cart/v1/restore')
    def _mock_grocery_cart_restore_error(request):
        return mockserver.make_response(status=500)

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/restore',
        json={
            'position': {'location': [55, 37]},
            'order_id': '0123456789-grocery',
        },
    )

    assert _mock_grocery_cart_restore_error.has_calls is True
    assert response.status == 500
