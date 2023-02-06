import copy

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks import grocery_cart as mock_grocery_cart

from tests_grocery_market_gw import common


async def test_proxies_grocery_cart_retrieve_200(
        taxi_grocery_market_gw, grocery_cart, personal,
):
    """ Proxies request to grocery-cart /retrieve
    proxies response from grocery-cart """

    cart_id = '01234567-89ab-cdef-000a-000000000001'
    grocery_cart.add_cart(cart_id)

    request_json = {
        'cart_id': cart_id,
        'position': {'location': [55, 37]},
        'offer_id': 'some-offer-id',
        'silent': True,
        'bound_user_ids': ['123456', '7890abcd'],
    }
    cart_request_json = copy.deepcopy(request_json)
    cart_request_json['disable_migration'] = cart_request_json['silent']
    cart_request_json.pop('silent')
    cart_request_json.pop('bound_user_ids')

    personal.check_request(
        personal_phone_id=common.DEFAULT_PERSONAL_PHONE_ID,
        phone=common.DEFAULT_HEADERS['Phone-Number'],
    )
    grocery_cart.check_request(
        cart_request_json,
        headers={
            'X-YaTaxi-Bound-Sessions': 'taxi:123456,taxi:7890abcd',
            **common.DAFAULT_AUTH_CONTEXT,
        },
        handler=mock_grocery_cart.Handler.retrieve,
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/retrieve',
        json=request_json,
        headers=common.DEFAULT_HEADERS,
    )

    assert grocery_cart.mock_retrieve_times_called() == 1
    assert response.status == 200
    assert response.json()['cart_id'] == cart_id


async def test_proxies_grocery_cart_retrieve_404(
        taxi_grocery_market_gw, grocery_cart, personal,
):
    """ Proxies request to grocery-cart /retrieve
    proxies 404-error from grocery-cart """

    request_json = {'position': {'location': [55, 37]}}

    personal.check_request(
        personal_phone_id=common.DEFAULT_PERSONAL_PHONE_ID,
        phone=common.DEFAULT_HEADERS['Phone-Number'],
    )
    grocery_cart.check_request(
        request_json,
        headers=common.DAFAULT_AUTH_CONTEXT,
        handler=mock_grocery_cart.Handler.retrieve,
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/retrieve',
        json=request_json,
        headers=common.DEFAULT_HEADERS,
    )
    assert grocery_cart.mock_retrieve_times_called() == 1
    assert response.status == 404
    assert response.json() == {
        'code': 'CART_NOT_FOUND',
        'message': 'Cart not found',
    }


async def test_proxies_grocery_cart_retrieve_500(
        taxi_grocery_market_gw, mockserver,
):
    """ Proxies request to grocery-cart /retrieve
    throws on grocery-cart error """

    @mockserver.json_handler('/grocery-cart/lavka/v1/cart/v1/retrieve')
    def _mock_grocery_cart_retrieve_error(request):
        return mockserver.make_response(status=500)

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/retrieve',
        json={'position': {'location': [55, 37]}},
    )

    assert _mock_grocery_cart_retrieve_error.has_calls is True
    assert response.status == 500
