import pytest

from . import utils


EATS_ID = '123'
PICKER_ID = '1122'


@pytest.mark.parametrize(
    'order_status, expected_status',
    [
        ('picking', 200),
        ('confirmed', 202),
        ('picked_up', 202),
        ('waiting_confirmation', 204),
        ('new', 409),
    ],
)
@utils.send_order_events_config()
async def test_request_cart_confirmation_responses(
        taxi_eats_picker_orders,
        stq,
        create_order,
        order_status,
        expected_status,
        mock_processing,
):
    create_order(eats_id=EATS_ID, picker_id=PICKER_ID, state=order_status)
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/cart/request-confirmation',
        headers=utils.da_headers(PICKER_ID),
        json={'eats_id': EATS_ID},
    )
    assert response.status_code == expected_status
    assert stq.wait_for_cart_confirmation.times_called == 0

    assert mock_processing.times_called == (1 if expected_status == 200 else 0)


@utils.send_order_events_config()
async def test_request_cart_confirmation_add(
        taxi_eats_picker_orders,
        stq,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        get_last_order_status,
        mock_processing,
):
    order_id = create_order(
        eats_id=EATS_ID, picker_id=PICKER_ID, state='picking', last_version=1,
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
        quantity=1,
        sold_by_weight=False,
    )
    item_id_2 = create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id='eats-item-2',
        quantity=2,
        sold_by_weight=False,
    )
    create_picked_item(
        order_item_id=item_id_1, picker_id=PICKER_ID, count=1, cart_version=1,
    )
    create_picked_item(
        order_item_id=item_id_2, picker_id=PICKER_ID, count=2, cart_version=1,
    )
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/cart/request-confirmation',
        headers=utils.da_headers(PICKER_ID),
        json={'eats_id': EATS_ID},
    )
    assert response.status_code == 200
    assert stq.wait_for_cart_confirmation.times_called == 1

    assert mock_processing.times_called == 1

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == 'waiting_confirmation'
    assert last_order_status['author_id'] == PICKER_ID


@utils.send_order_events_config()
async def test_request_cart_confirmation_remove(
        taxi_eats_picker_orders,
        stq,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        get_last_order_status,
        mock_processing,
):
    order_id = create_order(
        eats_id=EATS_ID, picker_id=PICKER_ID, state='picking', last_version=1,
    )
    create_order_item(
        order_id=order_id,
        version=0,
        eats_item_id='eats-item-1',
        quantity=1,
        sold_by_weight=False,
    )
    create_order_item(
        order_id=order_id,
        version=0,
        eats_item_id='eats-item-2',
        quantity=2,
        sold_by_weight=False,
    )
    item_id_1 = create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id='eats-item-1',
        quantity=1,
        sold_by_weight=False,
    )
    create_picked_item(
        order_item_id=item_id_1, picker_id=PICKER_ID, count=1, cart_version=1,
    )
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/cart/request-confirmation',
        headers=utils.da_headers(PICKER_ID),
        json={'eats_id': EATS_ID},
    )
    assert response.status_code == 200
    assert stq.wait_for_cart_confirmation.times_called == 0
    assert get_last_order_status(order_id)['state'] == 'picked_up'

    assert mock_processing.times_called == 1


@utils.send_order_events_config()
async def test_request_cart_confirmation_update(
        taxi_eats_picker_orders,
        stq,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        get_last_order_status,
        mock_processing,
):
    order_id = create_order(
        eats_id=EATS_ID, picker_id=PICKER_ID, state='picking', last_version=1,
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
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/cart/request-confirmation',
        headers=utils.da_headers(PICKER_ID),
        json={'eats_id': EATS_ID},
    )
    assert response.status_code == 200
    assert stq.wait_for_cart_confirmation.times_called == 1
    assert get_last_order_status(order_id)['state'] == 'waiting_confirmation'

    assert mock_processing.times_called == 1


@pytest.mark.now('2021-01-22T12:00:00+0000')
@pytest.mark.config(
    EATS_PICKER_ORDERS_CART_CONFIRMATION_SETTINGS={
        'retries': 10,
        'timeout': 1,
    },
)
@pytest.mark.parametrize(
    'order_status, exec_tries, status_updated_at, '
    'expected_status, rescheduled, events_sent',
    [
        pytest.param(
            'waiting_confirmation',
            0,
            '2021-01-22T11:59:00+0000',
            'picking',
            0,
            1,
            id='cart not confirmed',
        ),
        pytest.param(
            'waiting_confirmation',
            10,
            '2021-01-22T11:59:00+0000',
            'waiting_confirmation',
            0,
            0,
            id='retries number exceeded',
        ),
        pytest.param(
            'picking',
            0,
            '2021-01-22T11:59:00+0000',
            'picking',
            0,
            0,
            id='wrong status',
        ),
        pytest.param(
            'waiting_confirmation',
            0,
            '2021-01-22T12:00:00+0000',
            'waiting_confirmation',
            1,
            0,
            id='waiting confirmation',
        ),
    ],
)
@utils.send_order_events_config()
async def test_request_cart_confirmation_stq(
        mockserver,
        stq_runner,
        create_order,
        get_last_order_status,
        order_status,
        exec_tries,
        status_updated_at,
        expected_status,
        rescheduled,
        mock_processing,
        events_sent,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    order_id = create_order(
        eats_id=EATS_ID,
        picker_id=PICKER_ID,
        state=order_status,
        last_version=0,
        created_at=status_updated_at,
    )
    await stq_runner.wait_for_cart_confirmation.call(
        task_id='sample_task',
        kwargs={'eats_id': EATS_ID, 'picker_id': PICKER_ID},
        exec_tries=exec_tries,
    )
    assert mock_stq_reschedule.times_called == rescheduled
    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == expected_status

    assert mock_processing.times_called == events_sent


@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type',
    [
        ['picker_id', 'picker'],
        ['picker_id', None],
        ['system', 'system'],
        ['system', None],
        ['customer_id', 'customer'],
    ],
)
async def test_request_cart_confirmation_cart_items_mismatch_410(
        taxi_eats_picker_orders,
        stq,
        create_order,
        init_measure_units,
        create_order_item,
        create_picked_item,
        create_order_status,
        is_deleted_by,
        deleted_by_type,
):
    eats_id = 'eats_id'
    picker_id = 'picker_id'
    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, state='picking',
    )
    create_order_status(
        order_id, last_version=0, state='picking', comment='new comment',
    )
    create_order_item(order_id=order_id, eats_item_id='item_0', version=0)
    order_item_id_1_v0 = create_order_item(
        order_id=order_id, eats_item_id='item_1', version=0,
    )
    order_item_id_2_v0 = create_order_item(
        order_id=order_id, eats_item_id='item_2', version=0,
    )
    order_item_id_0_v1 = create_order_item(
        order_id=order_id, eats_item_id='item_0', version=1,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='item_1',
        version=1,
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
    )
    order_item_id_3_v1 = create_order_item(
        order_id=order_id,
        eats_item_id='item_3',
        version=1,
        is_deleted_by='another_picker',
    )
    create_picked_item(
        order_item_id=order_item_id_0_v1,
        picker_id=picker_id,
        cart_version=1,
        count=1,
    )
    create_picked_item(
        order_item_id=order_item_id_1_v0,
        picker_id=picker_id,
        cart_version=1,
        count=1,
    )
    create_picked_item(
        order_item_id=order_item_id_2_v0,
        picker_id=picker_id,
        cart_version=1,
        count=1,
    )
    create_picked_item(
        order_item_id=order_item_id_3_v1,
        picker_id=picker_id,
        cart_version=1,
        count=1,
    )

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/cart/request-confirmation',
        headers=utils.da_headers(picker_id),
        json={'eats_id': eats_id},
    )

    assert response.status == 410
    response = response.json()
    assert response['code'] == 'CART_ITEMS_MISMATCH'
    assert response['details']['items_mismatch'] == ['item_1', 'item_2']

    assert stq.wait_for_cart_confirmation.times_called == 0


async def test_request_cart_confirmation_400(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/cart/request-confirmation',
        headers=utils.da_headers('1'),
        json={'eeats_id': '123'},
    )

    assert response.status == 400


async def test_request_cart_confirmation_401(taxi_eats_picker_orders):
    bad_header = {
        'X-Request-Application-Version': '9.99 (9999)',
        'X-YaEda-CourierId': '123',
    }
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/cart/request-confirmation',
        headers=bad_header,
        json={'eats_id': '123'},
    )

    assert response.status == 401
