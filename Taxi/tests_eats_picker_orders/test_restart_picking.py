import datetime

import pytest

from . import utils


@pytest.mark.parametrize(
    'handle, picker_id, customer_id',
    [
        ['/4.0/eats-picker/api/v1/order/restart-picking', '1234', '1122'],
        ['/api/v1/order/restart-picking', None, '1122'],
    ],
)
@pytest.mark.parametrize('comment', [None, 'comment'])
@pytest.mark.parametrize(
    'zero_limit',
    [
        False,
        pytest.param(
            False, marks=[utils.zero_limit_on_picking_start_experiment(False)],
        ),
        pytest.param(
            True,
            marks=[utils.zero_limit_on_picking_start_experiment(enabled=True)],
        ),
    ],
)
@utils.send_order_events_config()
async def test_restart_picking_200(
        taxi_eats_picker_orders,
        mockserver,
        create_order,
        get_order,
        get_last_order_status,
        handle,
        picker_id,
        customer_id,
        comment,
        zero_limit,
        mock_processing,
):
    eats_id = '123'
    order_created_at = datetime.datetime.fromisoformat(
        '2021-02-10 09:00:00+03:00',
    )
    order_id = create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='waiting_confirmation',
        created_at=order_created_at,
        payment_value=500,
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        assert request.json.get('amount') == (0 if zero_limit else 4000)
        assert request.json.get('order_id') == eats_id
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id},
        json={'customer_id': customer_id, 'comment': comment},
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    assert get_order(order_id)['state'] == 'picking'
    status = get_last_order_status(order_id)
    assert status['state'] == 'picking'
    assert status['comment'] == comment
    assert status['author_id'] == (picker_id or customer_id)


@pytest.mark.parametrize(
    'handle',
    [
        '/4.0/eats-picker/api/v1/order/restart-picking',
        '/api/v1/order/restart-picking',
    ],
)
async def test_restart_picking_bad_request_400(
        taxi_eats_picker_orders, handle,
):
    response = await taxi_eats_picker_orders.post(
        handle, params={'eats_id': '123'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'handle, request_body',
    [
        ['/4.0/eats-picker/api/v1/order/restart-picking', {}],
        ['/api/v1/order/restart-picking', {'customer_id': '1122'}],
    ],
)
async def test_restart_picking_order_not_found_404(
        taxi_eats_picker_orders, handle, request_body,
):
    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.da_headers('1122'),
        params={'eats_id': '123'},
        json=request_body,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'handle, request_body',
    [
        ['/4.0/eats-picker/api/v1/order/restart-picking', {}],
        ['/api/v1/order/restart-picking', {'customer_id': '1122'}],
    ],
)
@pytest.mark.parametrize('status', ['new', 'picking', 'confirmed'])
async def test_restart_picking_wrong_status_409(
        taxi_eats_picker_orders, create_order, handle, request_body, status,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(eats_id=eats_id, picker_id=picker_id, state=status)
    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id},
        json=request_body,
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'wrong_order_state'


async def test_restart_picking_401(taxi_eats_picker_orders):
    bad_header = {
        'X-Request-Application-Version': '9.99 (9999)',
        'X-YaEda-CourierId': '123',
    }
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/restart-picking',
        headers=bad_header,
        params={'eats_id': '123'},
        json={},
    )
    assert response.status_code == 401
