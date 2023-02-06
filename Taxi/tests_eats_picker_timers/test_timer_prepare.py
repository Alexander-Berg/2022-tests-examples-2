import pytest

from . import utils

TIMESTAMPTZ_NOW = '2021-01-19T15:00:27.010000+03:00'


@pytest.mark.now(TIMESTAMPTZ_NOW)
@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/prepare', '/api/v1/timer/prepare'],
)
@utils.orders_autostart_picking_config(delay=45)
async def test_timer_prepare_timer_order_autostart(
        taxi_eats_picker_timers, handle, mockserver, order_get_json,
):
    eats_id = 'eats-id'
    picker_id = '1'
    body = {
        'eats_id': eats_id,
        'timer_type': 'timer_order_autostart',
        'duration': 100,
    }

    @mockserver.json_handler('/eats-picker-orders/api/v1/order')
    def _get_order(request):
        return mockserver.make_response(
            status=200, json=order_get_json(eats_id, 'picking', picker_id),
        )

    response = await taxi_eats_picker_timers.post(
        handle, headers=utils.da_headers(), json=body,
    )
    assert response.status == 200

    assert response.json()['eta_seconds'] == 45
