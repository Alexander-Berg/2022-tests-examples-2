import pytest

from . import utils


@pytest.mark.parametrize('status', ['paid', 'packing', 'handing'])
@utils.send_order_events_config()
async def test_complete_order_success_200(
        taxi_eats_picker_orders,
        create_order,
        mockserver,
        status,
        mock_processing,
):
    @mockserver.json_handler(f'/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_picker_payment(request):
        assert request.method == 'POST'
        assert request.json['eats_id'] == '123'
        assert request.json['status'] == 'complete'
        return mockserver.make_response(json={'issuccess': True}, status=200)

    create_order(state=status, eats_id='123')
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/complete',
        json={'eats_id': '123', 'reason': 'test reason'},
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1


async def test_complete_order_already_completed_202(
        taxi_eats_picker_orders, create_order,
):
    create_order(state='complete', eats_id='123')
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/complete',
        json={'eats_id': '123', 'reason': 'test reason'},
    )
    assert response.status_code == 202


@pytest.mark.parametrize('status', ['paid', 'packing', 'handing'])
@utils.send_order_events_config()
async def test_complete_order_complete_after_completion_202(
        taxi_eats_picker_orders,
        create_order,
        mockserver,
        status,
        mock_processing,
):
    @mockserver.json_handler(f'/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_picker_payment(request):
        assert request.method == 'POST'
        assert request.json['eats_id'] == '123'
        assert request.json['status'] == 'complete'
        return mockserver.make_response(json={'issuccess': True}, status=200)

    create_order(state=status, eats_id='123')
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/complete',
        json={'eats_id': '123', 'reason': 'test reason'},
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/complete',
        json={'eats_id': '123', 'reason': 'test reason'},
    )
    assert response.status_code == 202

    assert mock_processing.times_called == 1


async def test_complete_order_not_exist_404(
        taxi_eats_picker_orders, create_order,
):
    create_order(state='paid', eats_id='123')
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/complete',
        json={'eats_id': '111', 'reason': 'test reason'},
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload['code'] == 'order_not_found'
    assert payload['message'] == 'Заказ не найден'


@pytest.mark.parametrize('status', ['dispatching', 'picking', 'new'])
async def test_complete_order_has_wrong_state_409(
        taxi_eats_picker_orders, create_order, status,
):
    create_order(state=status, eats_id='123')
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/complete',
        json={'eats_id': '123', 'reason': 'test reason'},
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload['code'] == 'order_has_invalid_state'
