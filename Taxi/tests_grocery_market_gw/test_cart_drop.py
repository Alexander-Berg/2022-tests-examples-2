# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks import grocery_cart as mock_grocery_cart

from tests_grocery_market_gw import common


async def test_proxies_grocery_cart_drop_200(
        taxi_grocery_market_gw, grocery_cart, personal,
):
    """ Proxies request to grocery-cart /drop
    proxies response from grocery-cart """

    cart_id = '01234567-89ab-cdef-000a-000000000001'
    grocery_cart.add_cart(cart_id)

    request_json = {'cart_id': cart_id}

    personal.check_request(
        personal_phone_id=common.DEFAULT_PERSONAL_PHONE_ID,
        phone=common.DEFAULT_HEADERS['Phone-Number'],
    )
    grocery_cart.check_request(
        request_json,
        headers=common.DAFAULT_AUTH_CONTEXT,
        handler=mock_grocery_cart.Handler.drop,
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/drop',
        json=request_json,
        headers=common.DEFAULT_HEADERS,
    )

    assert grocery_cart.mock_lavka_drop_times_called() == 1
    assert response.status == 200
    assert response.json() == {}


async def test_proxies_grocery_cart_drop_404(
        taxi_grocery_market_gw, grocery_cart, personal,
):
    """ Proxies request to grocery-cart /drop
    proxies 404-error from grocery-cart """

    cart_id = '01234567-89ab-cdef-000a-000000000001'
    request_json = {'cart_id': cart_id}

    personal.check_request(
        personal_phone_id=common.DEFAULT_PERSONAL_PHONE_ID,
        phone=common.DEFAULT_HEADERS['Phone-Number'],
    )
    grocery_cart.check_request(
        request_json,
        headers=common.DAFAULT_AUTH_CONTEXT,
        handler=mock_grocery_cart.Handler.drop,
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/drop',
        json=request_json,
        headers=common.DEFAULT_HEADERS,
    )
    assert grocery_cart.mock_lavka_drop_times_called() == 1
    assert response.status == 404
    assert response.json() == {
        'code': 'CART_NOT_FOUND',
        'message': 'Cart not found',
    }


async def test_proxies_grocery_cart_drop_500(
        taxi_grocery_market_gw, mockserver,
):
    """ Proxies request to grocery-cart /drop
    throws on grocery-cart error """

    @mockserver.json_handler('/grocery-cart/lavka/v1/cart/v1/drop')
    def _mock_grocery_cart_drop_error(request):
        return mockserver.make_response(status=500)

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/drop',
        json={'cart_id': '01234567-89ab-cdef-000a-000000000001'},
    )

    assert _mock_grocery_cart_drop_error.has_calls is True
    assert response.status == 500
