import pytest

from . import utils


@pytest.mark.parametrize('status', ['cancelled', 'complete'])
async def test_cancel_order_of_wrong_status(
        taxi_eats_picker_orders, create_order, status,
):
    create_order(state=status, eats_id='123')
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/cancel?eats_id=123', json={},
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
        get_last_order_status,
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
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/cancel?eats_id=823', json={'comment': 'Foo bar'},
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

    order_status = get_last_order_status(order_id)
    assert order_status['state'] == 'cancelled'
    assert order_status['last_version'] == 42
    assert order_status['comment'] == 'Foo bar'
    assert order_status['author_id'] is None

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

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/cancel?eats_id=823', json={'comment': 'Foo bar'},
    )
    assert response.status_code == 204

    assert mock_processing.times_called == 1


@pytest.mark.parametrize('state', ['picking', 'assigned', 'picked_up'])
@utils.send_order_events_config()
async def test_change_spent_on_cancel(
        taxi_eats_picker_orders,
        create_order,
        get_order,
        update_order,
        create_order_status,
        mockserver,
        mock_apply_state,
        state,
        mock_processing,
):
    order_nr = '823'
    card_value = '31003'
    card_type = 'TinkoffBank'

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        if request.method == 'GET':
            assert request.query['card_type'] == card_type
            assert request.query['card_value'] == card_value
            body = {'amount': 1_000}
        else:
            body = {'order_id': order_nr}
        return mockserver.make_response(json=body, status=200)

    order_id = create_order(
        state=state,
        eats_id=order_nr,
        last_version=42,
        picker_card_type=card_type,
        picker_card_value=card_value,
        payment_limit=4_000,
        spent=None,
    )

    response = await taxi_eats_picker_orders.request(
        'PUT',
        f'/api/v1/order/courier?eats_id={order_nr}',
        json={
            'id': '123',
            'requisites': [{'type': card_type, 'value': card_value}],
        },
    )
    assert response.status_code == 204

    if state == 'picked_up':
        update_order(order_nr, state=state)
        create_order_status(order_id, state)
    response = await taxi_eats_picker_orders.post(
        f'/api/v1/order/cancel?eats_id={order_nr}',
        json={'comment': 'Foo bar'},
    )
    assert response.status_code == 204

    order = get_order(order_id)
    if state == 'picked_up':
        assert order['spent'] == 3_000
    else:
        assert order['spent'] is None

    assert mock_processing.times_called == 2


@pytest.mark.parametrize('state', ['new'])
@utils.send_order_events_config()
async def test_no_picker_on_cancel(
        taxi_eats_picker_orders,
        create_order,
        get_order,
        mockserver,
        state,
        mock_processing,
):
    order_nr = '823-4567'

    order_id = create_order(
        state=state,
        eats_id=order_nr,
        last_version=42,
        payment_limit=4_000,
        spent=None,
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return

    response = await taxi_eats_picker_orders.post(
        f'/api/v1/order/cancel?eats_id={order_nr}',
        json={'comment': 'Foo bar'},
    )
    assert response.status_code == 204

    assert _mock_eats_picker_payment.times_called == 0

    order = get_order(order_id)
    assert order['state'] == 'cancelled'

    assert mock_processing.times_called == 1
