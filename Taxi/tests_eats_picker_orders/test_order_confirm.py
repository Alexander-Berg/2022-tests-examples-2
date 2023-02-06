import pytest

from . import utils


EATS_ID = '123'
PICKER_ID = '1122'
CUSTOMER_ID = 'customer_id'


@pytest.mark.parametrize(
    'eats_id, customer_id, author_type, order_status, expected_order_status, '
    'expected_response',
    [
        (EATS_ID, CUSTOMER_ID, 'customer', 'confirmed', 'confirmed', 202),
        (EATS_ID, CUSTOMER_ID, None, 'confirmed', 'confirmed', 400),
        (EATS_ID, CUSTOMER_ID, 'customer', 'picked_up', 'picked_up', 202),
        (
            EATS_ID,
            CUSTOMER_ID,
            'customer',
            'waiting_confirmation',
            'picked_up',
            200,
        ),
        (EATS_ID, None, 'customer', 'waiting_confirmation', 'picked_up', 200),
        (
            'wrong_eats_id',
            CUSTOMER_ID,
            'customer',
            'waiting_confirmation',
            'waiting_confirmation',
            404,
        ),
        (EATS_ID, CUSTOMER_ID, 'customer', 'picking', 'picking', 409),
        (EATS_ID, CUSTOMER_ID, 'customer', 'new', 'new', 409),
    ],
)
@pytest.mark.parametrize('require_approval', [False, True])
@utils.send_order_events_config()
async def test_order_confirm(
        taxi_eats_picker_orders,
        mockserver,
        create_order,
        get_last_order_status,
        eats_id,
        customer_id,
        author_type,
        order_status,
        expected_order_status,
        expected_response,
        require_approval,
        mock_processing,
):
    order_id = create_order(
        eats_id=eats_id, state=order_status, require_approval=require_approval,
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    params = {}
    if author_type is not None:
        params['author_type'] = author_type
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/confirm',
        params=params,
        json={'eats_id': EATS_ID, 'customer_id': customer_id},
    )
    assert response.status_code == expected_response

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == expected_order_status
    if response.status == 200:
        assert last_order_status['author_id'] == customer_id

    assert _mock_eats_picker_payment.times_called == (expected_response == 200)

    assert mock_processing.times_called == (expected_response == 200)


@pytest.mark.now('2021-02-01T12:00:00+0000')
@pytest.mark.config(
    EATS_PICKER_ORDERS_CART_CONFIRMATION_SETTINGS={
        'retries': 10,
        'timeout': 1,
    },
)
@utils.send_order_events_config()
async def test_request_cart_confirmation_and_confirm(
        taxi_eats_picker_orders,
        mockserver,
        stq,
        stq_runner,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        get_last_order_status,
        mock_processing,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    order_id = create_order(
        eats_id=EATS_ID,
        picker_id=PICKER_ID,
        state='picking',
        last_version=1,
        created_at='2021-02-01T12:00:00+0000',
    )
    create_order_item(
        order_id=order_id,
        version=0,
        eats_item_id='eats-item-1',
        quantity=1,
        sold_by_weight=False,
    )
    item_id_1 = create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id='eats-item-1',
        quantity=2,
        sold_by_weight=False,
    )
    create_picked_item(
        order_item_id=item_id_1, picker_id=PICKER_ID, count=2, cart_version=1,
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(json={'order_id': EATS_ID}, status=200)

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/cart/request-confirmation',
        headers=utils.da_headers(PICKER_ID),
        json={'eats_id': EATS_ID},
    )
    assert response.status_code == 200
    assert stq.wait_for_cart_confirmation.times_called == 1
    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == 'waiting_confirmation'
    assert last_order_status['author_id'] == PICKER_ID

    assert mock_processing.times_called == 1

    next_call = stq.wait_for_cart_confirmation.next_call()
    task_id = next_call['id']
    kwargs = next_call['kwargs']
    await stq_runner.wait_for_cart_confirmation.call(
        task_id=task_id, kwargs=kwargs,
    )
    assert mock_stq_reschedule.times_called == 1
    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == 'waiting_confirmation'
    assert last_order_status['author_id'] == PICKER_ID
    mock_stq_reschedule.flush()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/confirm',
        params={'author_type': 'customer'},
        json={'eats_id': EATS_ID},
    )
    assert response.status_code == 200
    assert get_last_order_status(order_id)['state'] == 'picked_up'
    await stq_runner.wait_for_cart_confirmation.call(
        task_id=task_id, kwargs=kwargs,
    )
    assert mock_stq_reschedule.times_called == 0
    assert get_last_order_status(order_id)['state'] == 'picked_up'

    assert mock_processing.times_called == 2


@pytest.mark.parametrize(
    'last_version_author, last_version_author_type, expected_status',
    [
        ['someone', None, 200],
        [PICKER_ID, 'picker', 200],
        [PICKER_ID, 'system', 200],
        ['customer', 'customer', 200],
        [None, 'system', 200],
        ['another_picker', 'picker', 410],
        ['another_picker', 'system', 410],
    ],
)
@utils.send_order_events_config()
async def test_request_cart_confirmation_version_author(
        taxi_eats_picker_orders,
        mockserver,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        last_version_author,
        last_version_author_type,
        expected_status,
        mock_processing,
):
    eats_item_id_1 = 'eats_item_id_1'
    eats_item_id_2 = 'eats_item_id_2'
    order_id = create_order(
        eats_id=EATS_ID,
        picker_id=PICKER_ID,
        last_version=100,
        state='picking',
    )

    create_order_item(
        version=0, order_id=order_id, eats_item_id=eats_item_id_1, quantity=1,
    )
    item_id_1 = create_order_item(
        version=1,
        order_id=order_id,
        eats_item_id=eats_item_id_1,
        quantity=2,
        author=last_version_author,
        author_type=last_version_author_type,
    )
    item_id_2 = create_order_item(
        version=1,
        order_id=order_id,
        eats_item_id=eats_item_id_2,
        quantity=2,
        author=last_version_author,
        author_type=last_version_author_type,
    )

    create_picked_item(order_item_id=item_id_1, picker_id=PICKER_ID, count=1)
    create_picked_item(order_item_id=item_id_2, picker_id=PICKER_ID, count=2)

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(json={'order_id': EATS_ID}, status=200)

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/cart/request-confirmation',
        headers=utils.da_headers(PICKER_ID),
        params={'author_type': 'customer'},
        json={'eats_id': EATS_ID},
    )
    assert response.status_code == expected_status

    assert mock_processing.times_called == (1 if expected_status == 200 else 0)
