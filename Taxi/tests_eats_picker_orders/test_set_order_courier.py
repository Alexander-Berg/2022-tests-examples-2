import datetime

import pytest

from . import utils


def check_apply_state_requests(mock_apply_state, eats_id):
    assert mock_apply_state.times_called == 1
    mock_apply_state_request = mock_apply_state.next_call()['request'].json
    assert mock_apply_state_request['eats_id'] == eats_id
    assert mock_apply_state_request['status'] == 'assigned'


@pytest.mark.parametrize('method', ['put', 'post'])
async def test_set_picker_of_not_existed_order_404(
        stq, taxi_eats_picker_orders, method,
):
    response = await taxi_eats_picker_orders.request(
        method,
        '/api/v1/order/courier?eats_id=123',
        json={
            'id': '123',
            'requisites': [{'type': 'TinkoffBank', 'value': '02894719'}],
            'picker_phone_id': '123',
            'picker_name': 'Picker Pickerovich',
        },
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload == {
        'errors': [{'code': 404, 'description': 'Заказ не найден'}],
    }
    assert stq.eats_picker_orders_autostart_picking.times_called == 0


@pytest.mark.parametrize('method', ['put', 'post'])
@pytest.mark.parametrize('status', ['cancelled', 'complete'])
async def test_set_picker_of_done_order_409(
        stq, taxi_eats_picker_orders, create_order, status, method,
):
    create_order(eats_id='123-456', state=status)
    response = await taxi_eats_picker_orders.request(
        method,
        '/api/v1/order/courier?eats_id=123-456',
        json={
            'id': '123',
            'requisites': [{'type': 'TinkoffBank', 'value': '02894719'}],
            'picker_phone_id': '123',
            'picker_name': 'Picker Pickerovich',
        },
    )
    assert response.status_code == 409
    payload = response.json()
    assert payload == {
        'errors': [
            {
                'code': 409,
                'description': (
                    'Can\'t change picker of order in status \'%s\'' % status
                ),
            },
        ],
    }
    assert stq.eats_picker_orders_autostart_picking.times_called == 0


@pytest.mark.now('2021-10-18T20:00:00+0000')
@pytest.mark.parametrize('method', ['put', 'post'])
@pytest.mark.parametrize('order_claim_id', ['CLAIM_ID_10', None])
@pytest.mark.parametrize('request_claim_id', ['CLAIM_ID_20', None])
@pytest.mark.parametrize(
    'has_config, config_enabled',
    [(False, False), (True, True), (True, False)],
)
@utils.send_order_events_config()
async def test_set_picker_success_204(
        stq,
        taxi_eats_picker_orders,
        now,
        mockserver,
        experiments3,
        create_order,
        get_order,
        get_last_order_status,
        method,
        order_claim_id,
        request_claim_id,
        has_config,
        config_enabled,
        mock_processing,
        mock_apply_state,
):
    if has_config:
        experiments3.add_experiment3_from_marker(
            utils.autostart_picking_config(enabled=config_enabled, delay=42),
            None,
        )
    customer_id = 'vpupkin'

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _mock_eats_order_stats(json_request):
        assert [i['value'] for i in json_request.json['identities']] == [
            customer_id,
        ]

        filters = {
            x['name']: x['values'] for x in json_request.json['filters']
        }
        assert filters['business_type'] == ['retail']

        return {
            'data': [
                {
                    'identity': {'type': 'eater_id', 'value': customer_id},
                    'counters': [
                        {
                            'properties': [],
                            'value': 7,
                            'first_order_at': '2021-08-19T13:04:05+0000',
                            'last_order_at': '2021-09-19T13:04:05+0000',
                        },
                    ],
                },
            ],
        }

    picker_id = '123'
    eats_id = '123-456'
    order_id = create_order(
        eats_id=eats_id,
        state='new',
        picker_id=None,
        payment_limit=1000,
        last_version=44,
        claim_id=order_claim_id,
        customer_id=customer_id,
    )

    timer_id = 12345

    @mockserver.json_handler('/eats-picker-timers/api/v1/timer/start')
    def mock_eats_picker_timers_start(request):
        assert request.method == 'POST'
        assert request.json['eats_id'] == eats_id
        assert request.json['timer_type'] == 'timer_order_autostart'
        assert request.json['duration'] == 42
        return mockserver.make_response(
            status=200, json={'timer_id': timer_id},
        )

    response = await taxi_eats_picker_orders.request(
        method,
        '/api/v1/order/courier?eats_id=123-456',
        json={
            'id': picker_id,
            'requisites': [{'type': 'TinkoffBank', 'value': '31337'}],
            'picker_phone_id': '123',
            'picker_name': 'Picker Pickerovich',
            'claim_id': request_claim_id,
        },
    )
    assert response.status_code == 204

    check_apply_state_requests(mock_apply_state, eats_id)
    assert mock_processing.times_called == 1

    order = get_order(order_id)
    assert order['picker_id'] == picker_id
    assert order['state'] == 'assigned'
    assert order['picker_card_type'] == 'TinkoffBank'
    assert order['picker_card_value'] == '31337'
    assert order['claim_id'] == (request_claim_id or order_claim_id)

    order_status = get_last_order_status(order_id)
    assert order_status['state'] == 'assigned'
    assert order_status['author_id'] == picker_id
    assert order_status['last_version'] == 44

    assert _mock_eats_order_stats.times_called == 1
    assert get_order(order_id)['customer_orders_count'] == 7

    if config_enabled:
        assert stq.eats_picker_orders_autostart_picking.times_called == 1
        stq_call = stq.eats_picker_orders_autostart_picking.next_call()
        assert stq_call['eta'] == now + datetime.timedelta(seconds=42)
        assert stq_call['id'] == eats_id
        assert stq_call['kwargs']['eats_id'] == eats_id
        assert stq_call['kwargs']['picker_id'] == picker_id
        assert stq_call['kwargs']['retries'] == 3
        assert stq_call['kwargs']['timer_id'] == timer_id
        assert mock_eats_picker_timers_start.times_called == 1
    else:
        assert stq.eats_picker_orders_autostart_picking.times_called == 0
        assert mock_eats_picker_timers_start.times_called == 0


@pytest.mark.parametrize('method', ['put', 'post'])
@pytest.mark.now('2020-10-20T17:50:00+0000')
@utils.send_order_events_config()
async def test_reset_picker_success_204(
        taxi_eats_picker_orders,
        create_order,
        get_order,
        mockserver,
        method,
        mock_processing,
        mock_apply_state,
):
    eats_id = '123-456'
    order_id = create_order(
        eats_id=eats_id,
        state='picked_up',
        picker_id='old-one',
        payment_limit=1000,
        last_version=44,
        picker_card_type='TinkoffBank',
        picker_card_value='111',
        picker_phone_id='1',
        picker_phone=('+7-999-888-77-66', '2020-10-21T17:45:00+0000'),
    )

    limit_requests = [
        {
            'card_value': '111',
            'card_type': 'TinkoffBank',
            'amount': 0,
            'order_id': eats_id,
        },
        {
            'card_value': '222',
            'card_type': 'TinkoffBank',
            'amount': 1000,
            'order_id': eats_id,
        },
    ]

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        print(request.method, request.query)
        if request.method == 'POST':
            expected = limit_requests.pop(0)
            assert request.query.get('card_value') == expected['card_value']
            assert request.query.get('card_type') == expected['card_type']
            assert request.json['amount'] == expected['amount']
            assert request.json['order_id'] == expected['order_id']
            return mockserver.make_response(
                json={'order_id': expected['order_id']}, status=200,
            )

        assert request.query.get('card_value') == '111'
        assert request.query.get('card_type') == 'TinkoffBank'
        return mockserver.make_response(json={'amount': 1000.0}, status=200)

    response = await taxi_eats_picker_orders.request(
        method,
        '/api/v1/order/courier',
        params={'eats_id': eats_id},
        json={
            'id': 'new-one',
            'requisites': [{'type': 'TinkoffBank', 'value': '222'}],
            'picker_phone_id': '123',
            'picker_name': 'Picker Pickerovich',
        },
    )
    assert response.status_code == 204

    check_apply_state_requests(mock_apply_state, eats_id)
    assert mock_processing.times_called == 1

    order = get_order(order_id)
    assert order['picker_id'] == 'new-one'
    assert order['state'] == 'assigned'
    assert order['picker_card_type'] == 'TinkoffBank'
    assert order['picker_card_value'] == '222'
    assert order['picker_phone'] is None

    assert _mock_eats_picker_payment.times_called == 2


@pytest.mark.parametrize('method', ['put', 'post'])
async def test_change_picker_without_requisites_400(
        taxi_eats_picker_orders, create_order, method,
):
    create_order(
        eats_id='123-456', picker_card_type=None, picker_card_value=None,
    )

    response = await taxi_eats_picker_orders.request(
        method,
        '/api/v1/order/courier?eats_id=123-456',
        json={
            'id': 'new-one',
            'requisites': [],
            'picker_phone_id': '13',
            'picker_name': 'Picker Pickerovich',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'


@pytest.mark.parametrize(
    'method, expected_status', [['put', 409], ['post', 423]],
)
async def test_error_on_setting_same_picker_on_multiple_active_orders(
        taxi_eats_picker_orders, create_order, method, expected_status,
):
    create_order(eats_id='order-1', picker_id='1', state='assigned')
    create_order(eats_id='order-2', picker_id='2', state='assigned')

    response = await taxi_eats_picker_orders.request(
        method,
        '/api/v1/order/courier?eats_id=order-2',
        json={
            'id': '1',
            'requisites': [{'type': 'TinkoffBank', 'value': '222'}],
            'picker_phone_id': '123',
            'picker_name': 'Picker Pickerovich',
        },
    )
    assert response.status_code == expected_status
    payload = response.json()
    assert payload == {
        'errors': [
            {
                'code': expected_status,
                'description': (
                    'Can\'t set picker because he already has an active order'
                ),
            },
        ],
    }


@pytest.mark.parametrize('method', ['put', 'post'])
@utils.send_order_events_config()
async def test_set_picker_with_finished_orders_204(
        taxi_eats_picker_orders,
        create_order,
        get_order,
        method,
        mock_processing,
        mock_apply_state,
):
    create_order(eats_id='order-1', picker_id='1', state='complete')
    create_order(eats_id='order-2', picker_id='1', state='cancelled')
    order_id = create_order(eats_id='order-3', picker_id=None, state='new')

    response = await taxi_eats_picker_orders.request(
        method,
        '/api/v1/order/courier?eats_id=order-3',
        json={
            'id': '1',
            'requisites': [{'type': 'TinkoffBank', 'value': '222'}],
            'picker_phone_id': '123',
            'picker_name': 'Picker Pickerovich',
        },
    )
    assert response.status_code == 204

    check_apply_state_requests(mock_apply_state, 'order-3')
    assert mock_processing.times_called == 1

    order = get_order(order_id)
    assert order['picker_id'] == '1'
    assert order['state'] == 'assigned'
    assert order['picker_card_type'] == 'TinkoffBank'
    assert order['picker_card_value'] == '222'


@pytest.mark.parametrize('method', ['put', 'post'])
@utils.send_order_events_config()
async def test_reset_picker_success_202(
        taxi_eats_picker_orders,
        create_order,
        method,
        mock_processing,
        mock_apply_state,
):
    eats_id = '123-456'
    create_order(
        eats_id=eats_id,
        state='new',
        picker_id=None,
        payment_limit=1000,
        last_version=44,
    )

    response = await taxi_eats_picker_orders.request(
        method,
        '/api/v1/order/courier',
        params={'eats_id': eats_id},
        json={
            'id': '123',
            'requisites': [{'type': 'TinkoffBank', 'value': '31337'}],
        },
    )
    assert response.status_code == 204

    check_apply_state_requests(mock_apply_state, eats_id)
    assert mock_processing.times_called == 1

    response = await taxi_eats_picker_orders.put(
        '/api/v1/order/courier',
        params={'eats_id': eats_id},
        json={
            'id': '123',
            'requisites': [{'type': 'TinkoffBank', 'value': '31337'}],
        },
    )
    assert response.status_code == 202

    assert mock_apply_state.times_called == 0
    assert mock_processing.times_called == 1


@pytest.mark.parametrize(
    'method, expected_status', [['put', 500], ['post', 423]],
)
@pytest.mark.now('2020-10-20T17:50:00+0000')
async def test_payment_error(
        taxi_eats_picker_orders,
        create_order,
        mockserver,
        method,
        expected_status,
):
    create_order(
        eats_id='123-456',
        state='picked_up',
        picker_id='old-one',
        payment_limit=1000,
        last_version=44,
        picker_card_type='TinkoffBank',
        picker_card_value='111',
        picker_phone_id='1',
        picker_phone=('+7-999-888-77-66', '2020-10-21T17:45:00+0000'),
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(_):
        return mockserver.make_response(status=500)

    response = await taxi_eats_picker_orders.request(
        method,
        '/api/v1/order/courier?eats_id=123-456',
        json={
            'id': 'new-one',
            'requisites': [{'type': 'TinkoffBank', 'value': '222'}],
            'picker_phone_id': '123',
            'picker_name': 'Picker Pickerovich',
        },
    )
    assert response.status_code == expected_status
    payload = response.json()
    assert payload == {
        'errors': [
            {'code': expected_status, 'description': 'Payment internal error'},
        ],
    }
