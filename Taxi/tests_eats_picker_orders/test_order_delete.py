import pytest

from . import utils


@pytest.mark.parametrize('status', ['cancelled', 'complete'])
async def test_cancel_order_of_wrong_status(
        taxi_eats_picker_orders, create_order, status,
):
    create_order(state=status, eats_id='123')
    response = await taxi_eats_picker_orders.delete(
        '/api/v1/order?eats_id=123', json={},
    )
    assert response.status_code == 409
    payload = response.json()
    assert payload == {
        'errors': [
            {
                'code': 409,
                'description': (
                    'Current order status doesn\'t allow cancellation'
                ),
            },
        ],
    }


@pytest.mark.parametrize('picker_id', ['221', None])
@pytest.mark.parametrize('status', ['assigned', 'paid', 'packing', 'handing'])
@utils.send_order_events_config()
async def test_cancel_order_success(
        taxi_eats_picker_orders,
        create_order,
        get_cursor,
        mockserver,
        picker_id,
        status,
        mock_processing,
):
    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        if request.method == 'GET':
            assert request.method == 'GET'
            assert request.query['card_type'] == 'TinkoffBank'
            assert request.query['card_value'] == '31003'
            return mockserver.make_response(
                json={'amount': 1000.0}, status=200,
            )

        assert request.query.get('card_value') == '31003'
        assert request.query.get('card_type') == 'TinkoffBank'
        assert request.json['amount'] == 0
        assert request.json['order_id'] == '823'
        return mockserver.make_response(json={'order_id': '823'}, status=200)

    order_id = create_order(
        state=status,
        eats_id='823',
        last_version=42,
        picker_id=picker_id,
        picker_card_type='TinkoffBank',
        picker_card_value='31003',
    )
    response = await taxi_eats_picker_orders.delete(
        '/api/v1/order?eats_id=823', json={'comment': 'Foo bar'},
    )
    assert response.status_code == 204

    assert mock_processing.times_called == 1

    cursor = get_cursor()
    cursor.execute(
        'SELECT state FROM eats_picker_orders.orders WHERE id = %s',
        (order_id,),
    )
    order_state = cursor.fetchone()[0]
    assert order_state == 'cancelled'

    cursor.execute(
        'SELECT * FROM eats_picker_orders.order_statuses'
        ' WHERE order_id = %s  ORDER BY created_at DESC LIMIT 1',
        (order_id,),
    )
    order_status = cursor.fetchone()
    assert order_status['state'] == 'cancelled'
    assert order_status['last_version'] == 42
    assert order_status['comment'] == 'Foo bar'

    assert bool(_mock_eats_picker_payment.times_called) == bool(picker_id)


@utils.send_order_events_config()
async def test_allow_cancelling_order_if_limit_changed(
        taxi_eats_picker_orders, create_order, mockserver, mock_processing,
):
    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        if request.method == 'GET':
            assert request.method == 'GET'
            assert request.query['card_type'] == 'TinkoffBank'
            assert request.query['card_value'] == '31003'
            return mockserver.make_response(
                json={'amount': 1000.0}, status=200,
            )

        assert request.query.get('card_value') == '31003'
        assert request.query.get('card_type') == 'TinkoffBank'
        assert request.json['amount'] == 0
        assert request.json['order_id'] == '823'
        return mockserver.make_response(json={'order_id': '823'}, status=200)

    create_order(
        state='picking',
        eats_id='823',
        last_version=42,
        picker_id='221',
        picker_card_type='TinkoffBank',
        picker_card_value='31003',
        payment_limit=4_000,
    )

    response = await taxi_eats_picker_orders.delete(
        '/api/v1/order?eats_id=823', json={'comment': 'Foo bar'},
    )
    assert response.status_code == 204

    assert mock_processing.times_called == 1
