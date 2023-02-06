import pytest

from . import experiments

HEADERS = {'X-Yandex-Login': 'superSupport', 'Accept-Language': 'ru'}

CANCEL_MATRIX_PICKUP = {
    'groups': [
        {
            'name': 'pickup',
            'description': 'pickup',
            'reasons': [
                {
                    'name': 'out_of_stock',
                    'description': 'Отсутсвует товар',
                    'compensations': [
                        {
                            'type': 'promocode',
                            'promocode_type': 'percent',
                            'promocode_value': 10,
                        },
                        {
                            'promocode_value': 300,
                            'type': 'promocode',
                            'promocode_type': 'fixed',
                        },
                    ],
                },
            ],
        },
    ],
}

CANCEL_MATRIX_PICKUP_EN = {
    'groups': [
        {
            'name': 'pickup',
            'description': 'pickup',
            'reasons': [
                {
                    'name': 'out_of_stock',
                    'description': 'Item missing',
                    'compensations': [
                        {
                            'type': 'promocode',
                            'promocode_type': 'percent',
                            'promocode_value': 10,
                        },
                        {
                            'promocode_value': 300,
                            'type': 'promocode',
                            'promocode_type': 'fixed',
                        },
                    ],
                },
            ],
        },
    ],
}

CANCEL_MATRIX_COURIER = {
    'groups': [
        {
            'name': 'courier',
            'description': 'courier_name',
            'reasons': [
                {
                    'name': 'out_of_stock',
                    'description': 'Отсутсвует товар',
                    'compensations': [
                        {
                            'promocode_value': 10,
                            'type': 'promocode',
                            'promocode_type': 'percent',
                        },
                        {
                            'promocode_value': 300,
                            'type': 'promocode',
                            'promocode_type': 'fixed',
                        },
                    ],
                },
                {
                    'name': 'cant_wait',
                    'description': 'Не хочет ждать',
                    'compensations': [{'type': 'refund'}],
                },
            ],
        },
    ],
}


@pytest.mark.parametrize('locale', ['ru', 'en'])
@experiments.CANCELMATRIX_EXPERIMENT
async def test_basic(
        taxi_grocery_support,
        pgsql,
        experiments3,
        grocery_orders,
        grocery_cart,
        locale,
):
    grocery_orders.add_order(order_id='abba', delivery_type='pickup')
    grocery_cart.set_delivery_type('pickup')

    headers = {'X-Yandex-Login': 'superSupport', 'Accept-Language': locale}
    request_json = {'order_id': 'abba'}
    response = await taxi_grocery_support.post(
        '/admin/v1/api/cancel/reasons', json=request_json, headers=headers,
    )

    assert response.status_code == 200
    if locale == 'en':
        assert response.json() == CANCEL_MATRIX_PICKUP_EN
    else:
        assert response.json() == CANCEL_MATRIX_PICKUP


@experiments.CANCELMATRIX_COURIER
async def test_courier(
        pgsql,
        taxi_grocery_support,
        experiments3,
        grocery_orders,
        grocery_cart,
):
    grocery_orders.add_order(order_id='abba')
    grocery_cart.set_delivery_type('courier')

    request = {'order_id': 'abba'}
    response = await taxi_grocery_support.post(
        '/admin/v1/api/cancel/reasons', json=request, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == CANCEL_MATRIX_COURIER


@pytest.mark.parametrize(
    'header, status_code',
    [
        ({'X-Yandex-Login': 'superSupport', 'Accept-Language': 'ru'}, 404),
        ({'X-Yandex-Login': 'superSupport'}, 400),
        ({'Accept-Language': 'ru'}, 404),
    ],
)
async def test_bad_request(
        pgsql,
        taxi_grocery_support,
        experiments3,
        grocery_orders,
        header,
        status_code,
):
    grocery_orders.add_order(order_id='right_order_id')
    request = {'order_id': 'wrong_order_id'}

    response = await taxi_grocery_support.post(
        '/admin/v1/api/cancel/reasons', json=request, headers=header,
    )

    assert response.status_code == status_code
