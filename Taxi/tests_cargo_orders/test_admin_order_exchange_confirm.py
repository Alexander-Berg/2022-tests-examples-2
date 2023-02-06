import pytest

DEFAULT_HEADERS = {'Accept-Language': 'en'}


@pytest.fixture(name='orders_confirm_point')
def _orders_confirm_point(taxi_cargo_orders):
    async def _wrapper(order_id: str, headers=None):
        if headers is None:
            headers = DEFAULT_HEADERS
        response = await taxi_cargo_orders.post(
            '/admin/v1/order/exchange/confirm',
            params={'cargo_order_id': order_id},
            json={
                'comment': 'some comment',
                'ticket': 'TICKET-100',
                'last_known_status': 'ready_for_pickup_confirmation',
                'new_status': 'pickuped',
                'point_id': 1,
                'idempotency_token': 'some_token',
            },
            headers=headers,
        )
        return response

    return _wrapper


async def test_happy_path(
        orders_confirm_point, mock_dispatch_exchange_confirm, default_order_id,
):
    mock_dispatch_exchange_confirm.expected_request = {
        'last_known_status': 'pickup_confirmation',
        'point_id': 1,
        'support': {'comment': 'some comment', 'ticket': 'TICKET-100'},
        'performer_info': {
            'park_id': 'park_id1',
            'driver_id': 'driver_id1',
            'tariff_class': 'cargo',
            'transport_type': 'electric_bicycle',
        },
        'async_timer_calculation_supported': False,
    }

    response = await orders_confirm_point(default_order_id)
    assert response.status_code == 200

    assert mock_dispatch_exchange_confirm.handler.times_called == 1
