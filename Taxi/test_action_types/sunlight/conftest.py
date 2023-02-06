from aiohttp import web
import pytest


@pytest.fixture(name='mock_sunlight_api')
def _mock_sunlight_api(mockserver):
    order = {
        'number': '71080191840',
        'estimated_delivery': '2021-08-06',
        'state': 'Осуществляется доставка',
        'late': True,
        'courier': None,
        'tracking': {
            'company': 'DPD',
            'url': 'http://url/CODE',
            'number': '99999999999',
        },
        'type': 'delivery',
        'is_paid_order': False,
        'payment_method': 'Наличные',
        'pickup_address': 'г City, ул Street, д 1, кв. 100',
        'summ': 1521.0,
        'checkout_channel': 'sunlight_app',
        'estimated_store': None,
        'customer_name': 'CustomerName',
    }

    error_reason = {'error_type': 'wrong_status', 'error_message': 'smth'}

    @mockserver.json_handler('/sunlight/yandex-bot/v1/orders/by-number/')
    async def _get_order_by_number(_):
        return web.json_response(data={'order': order})

    @mockserver.json_handler('/sunlight/yandex-bot/v1/orders/by-phone/')
    async def _get_orders_by_phone(_):
        return web.json_response(data={'orders': [order]})

    @mockserver.json_handler('/sunlight/yandex-bot/v1/orders/cancel/')
    async def _order_cancel(request):
        if (
                request.json.get('phone') == '1234'
                and request.json.get('number') == '4321'
        ):
            return web.json_response(status=400, data=error_reason)
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/sunlight/yandex-bot/v1/orders/extend/')
    async def _order_extend(request):
        if (
                request.json.get('phone') == '1234'
                and request.json.get('number') == '4321'
        ):
            return web.json_response(status=400, data=error_reason)
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/sunlight/yandex-bot/v1/customer/subscriptions/edit/',
    )
    async def _cancel_subscription(_):
        return mockserver.make_response(status=200)

    return order
