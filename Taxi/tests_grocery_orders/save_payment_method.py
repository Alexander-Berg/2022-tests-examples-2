import pytest

from . import headers
from . import models

CART_HANDLER = '/grocery-cart/internal/v1/cart/save-payment-method-id'

DEFAULT_HEADERS = {'headers': {'X-Yandex-UID': headers.YANDEX_UID}}


@pytest.fixture(name='mock_save_payment_method')
def _mock_save_payment_method(mockserver):
    def _wrapper(error_code=None, **kwargs):
        @mockserver.json_handler(CART_HANDLER)
        def _mock(request):
            if error_code is not None:
                return mockserver.make_response('{}', error_code)

            for key in kwargs:
                assert request.json[key] == kwargs[key], key

            return {}

        return _mock

    return _wrapper


async def test_basic(taxi_grocery_orders, pgsql, mock_save_payment_method):
    order = models.Order(pgsql=pgsql)

    payment_type = 'card'
    payment_id = 'card-x123'

    save_payment_method_mock = mock_save_payment_method(
        cart_id=order.cart_id,
        payment_type=payment_type,
        payment_id=payment_id,
    )

    response = await taxi_grocery_orders.post(
        '/internal/v1/save-payment-method',
        json={
            'order_id': order.order_id,
            'payment_type': payment_type,
            'payment_id': payment_id,
        },
        **DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    assert save_payment_method_mock.times_called == 1


@pytest.mark.parametrize('error_code', [404, 409])
async def test_errors(
        taxi_grocery_orders, pgsql, mock_save_payment_method, error_code,
):
    order = models.Order(pgsql=pgsql)

    payment_type = 'card'
    payment_id = 'card-x123'

    save_payment_method_mock = mock_save_payment_method(error_code=error_code)

    response = await taxi_grocery_orders.post(
        '/internal/v1/save-payment-method',
        json={
            'order_id': order.order_id,
            'payment_type': payment_type,
            'payment_id': payment_id,
        },
        **DEFAULT_HEADERS,
    )
    assert response.status_code == 404

    assert save_payment_method_mock.times_called == 1


async def test_another_user(
        taxi_grocery_orders, pgsql, mock_save_payment_method,
):
    order = models.Order(pgsql=pgsql, yandex_uid=headers.YANDEX_UID + 'xxx')

    save_payment_method_mock = mock_save_payment_method()

    response = await taxi_grocery_orders.post(
        '/internal/v1/save-payment-method',
        json={
            'order_id': order.order_id,
            'payment_type': 'card',
            'payment_id': 'card-x123',
        },
        **DEFAULT_HEADERS,
    )
    assert response.status_code == 401

    assert save_payment_method_mock.times_called == 0
