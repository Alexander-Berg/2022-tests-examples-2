import pytest


@pytest.fixture
def pay_response(
        taxi_eats_corp_orders_web,
        qr_code,
        terminal_id,
        terminal_token,
        items,
        idempotency_key,
):
    async def func(params_override: dict = None):
        if params_override is None:
            params_override = {}
        data = {
            'authorization': f'{terminal_id}:{terminal_token}',
            'user_code': qr_code,
            'idempotency_key': idempotency_key,
            'items': items,
            'mcc': 1,
            'currency': 'RUB',
        }
        data.update(params_override)
        response = await taxi_eats_corp_orders_web.post(
            '/v1/payment/pay', json=data,
        )
        return response.status, await response.json()

    return func


@pytest.fixture
def internal_pay_response(
        taxi_eats_corp_orders_web,
        qr_code,
        terminal_id,
        terminal_token,
        items,
        order_id,
        place_id,
        proper_headers_code_get,
):
    async def func(params_override: dict = None):
        if params_override is None:
            params_override = {}
        data = {
            'order_id': order_id,
            'place_id': place_id,
            'items': items,
            'mcc': 1,
            'currency': 'RUB',
        }
        data.update(params_override)
        response = await taxi_eats_corp_orders_web.post(
            '/internal/v1/payment/pay',
            json=data,
            headers=proper_headers_code_get,
        )
        return response.status

    return func
