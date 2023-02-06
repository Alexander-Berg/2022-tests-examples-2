import copy
import decimal
from urllib import parse

import pytest

from . import utils


DEFAULT_EATS_ID = 'test_eats_id'
EATS_ID_PAID = 'test_eats_id_paid'
EATS_ID_WITH_RECEIPT = 'test_eats_id_with_receipt'
DEFAULT_PICKER_ID = 'test_picker_id'
PICKER_ID_PAID = 'test_picker_id_paid'
PICKER_ID_WITH_RECEIPT = 'test_picker_id_with_receipt'
DEFAULT_RECEIPT = {
    't': '20200618T105208',
    's': '1098.02',
    'fn': '4891689280440300',
    'i': '19097',
    'fp': '313667667',
    'n': '1',
}


@pytest.mark.pgsql('picker_orders')
@pytest.mark.parametrize(
    'order_state, expected_status',
    [
        ('picked_up', 200),
        ('receipt_rejected', 200),
        ('paid', 202),
        ('receipt_processing', 204),
        ('new', 409),
    ],
)
@pytest.mark.now('2020-06-18T10:00:00')
@utils.send_order_events_config()
async def test_order_receipt_v2_order_states(
        taxi_eats_picker_orders,
        stq,
        create_order,
        order_state,
        expected_status,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(eats_id=eats_id, picker_id=picker_id, state=order_state)
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/receipt',
        params={'eats_id': eats_id},
        json=DEFAULT_RECEIPT,
        headers=utils.da_headers(picker_id),
    )
    assert response.status_code == expected_status
    assert stq.receipt_upload.times_called == (
        1 if expected_status == 200 else 0
    )
    assert mock_processing.times_called == (1 if expected_status == 200 else 0)


@pytest.mark.config(
    EATS_PICKER_ORDERS_RECEIPT_UPLOAD_SETTINGS={'timeout': 1, 'retries': 3},
)
@pytest.mark.parametrize(
    'eats_id, picker_id, picker_payment_amount, edadeal_status, '
    'picker_payment_status, expected_status, reschedule_counter, '
    'order_final_status',
    [
        pytest.param(
            DEFAULT_EATS_ID,
            DEFAULT_PICKER_ID,
            2,
            202,
            200,
            200,
            0,
            'complete',
            id='simple test',
        ),
        pytest.param(
            DEFAULT_EATS_ID,
            DEFAULT_PICKER_ID,
            2,
            202,
            200,
            200,
            3,
            'receipt_rejected',
            id='retries number exceeded',
        ),
        pytest.param(
            EATS_ID_PAID,
            PICKER_ID_PAID,
            2,
            202,
            200,
            202,
            0,
            'paid',
            id='status incorrect',
        ),
        pytest.param(
            DEFAULT_EATS_ID,
            '666',
            2,
            202,
            200,
            404,
            0,
            'picked_up',
            id='picker incorrect',
        ),
        pytest.param(
            DEFAULT_EATS_ID,
            DEFAULT_PICKER_ID,
            200,
            202,
            200,
            200,
            0,
            'receipt_processing',
            id='receipt limit incorrect',
        ),
        pytest.param(
            DEFAULT_EATS_ID,
            DEFAULT_PICKER_ID,
            2,
            400,
            200,
            200,
            0,
            'receipt_processing',
            id='edadeal 400 error',
        ),
        pytest.param(
            DEFAULT_EATS_ID,
            DEFAULT_PICKER_ID,
            2,
            409,
            200,
            200,
            0,
            'complete',
            id='edadeal 409 error',
        ),
        pytest.param(
            DEFAULT_EATS_ID,
            DEFAULT_PICKER_ID,
            2,
            422,
            200,
            200,
            0,
            'receipt_processing',
            id='edadeal 422 error',
        ),
        pytest.param(
            DEFAULT_EATS_ID,
            DEFAULT_PICKER_ID,
            2,
            202,
            500,
            200,
            0,
            'receipt_processing',
            id='picker_payment 500 error',
        ),
    ],
)
@pytest.mark.now('2020-06-18T10:00:00')
@utils.send_order_events_config()
async def test_order_receipt_v2_full(
        taxi_eats_picker_orders,
        mockserver,
        stq,
        stq_runner,
        get_order_by_eats_id,
        get_last_order_status,
        eats_id,
        picker_id,
        picker_payment_amount,
        edadeal_status,
        picker_payment_status,
        expected_status,
        reschedule_counter,
        order_final_status,
        mock_processing,
):
    @mockserver.json_handler('/edadeal-checkprovider/v1/checks')
    def _mock_edadeal(request):
        assert (
            dict(parse.parse_qsl(request.get_data().decode()))
            == DEFAULT_RECEIPT
        )
        assert request.headers['X-Correlation-Id'] == eats_id
        return mockserver.make_response(status=edadeal_status)

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        if request.method == 'GET':
            assert request.query.get('card_type') == 'TinkoffBank'
            assert request.query.get('card_value') == 'test_cid_1'
            return mockserver.make_response(
                json={'amount': picker_payment_amount},
                status=picker_payment_status,
            )

        assert request.query.get('card_type') == 'TinkoffBank'
        assert request.query.get('card_value') == 'test_cid_1'
        assert request.json['amount'] == 0
        assert request.json['order_id'] == eats_id
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    core_picker_orders_statuses = []

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        assert request.json['eats_id'] == eats_id
        status = request.json['status']
        assert status in ('complete', 'paid')
        assert request.json['timestamp'] == '2020-06-18T10:00:00+00:00'
        expected_reasons = {
            'paid': 'receipt-uploaded',
            'complete': 'picking_only:receipt-uploaded',
        }
        assert request.json['reason'] == expected_reasons[status]
        core_picker_orders_statuses.append(status)

        return mockserver.make_response(json={}, status=200)

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/receipt',
        params={'eats_id': eats_id},
        json=DEFAULT_RECEIPT,
        headers=utils.da_headers(picker_id),
    )

    assert response.status_code == expected_status
    if expected_status != 200:
        assert stq.receipt_upload.times_called == 0
        order_doc = get_order_by_eats_id(eats_id)
        assert order_doc['state'] == order_final_status
        return

    assert mock_processing.times_called == 1

    assert stq.receipt_upload.times_called == 1
    next_call = stq.receipt_upload.next_call()
    task_id = next_call['id']
    kwargs = next_call['kwargs']
    assert kwargs['eats_id'] == eats_id
    assert kwargs['picker_id'] == picker_id
    assert kwargs['receipt'] == DEFAULT_RECEIPT
    await stq_runner.receipt_upload.call(
        task_id=task_id, kwargs=kwargs, reschedule_counter=reschedule_counter,
    )
    order_doc = get_order_by_eats_id(eats_id)
    order_status = get_last_order_status(order_doc['id'])
    assert order_doc['state'] == order_final_status
    assert order_status['state'] == order_final_status
    if expected_status not in {'complete', 'packing', 'handing'}:
        return

    assert order_doc['spent'] == decimal.Decimal('1098.02')
    assert order_status['last_version'] == 0
    assert stq.send_order_paid_billing_event.times_called == 1
    assert _mock_eats_core_picker_orders.times_called == (
        int(expected_status == 'complete') * 2
    )
    if expected_status == 'complete':
        assert core_picker_orders_statuses == ['paid', 'complete']
    kwargs = stq.send_order_paid_billing_event.next_call()['kwargs']
    assert kwargs['order_id'] == 1
    assert kwargs['eats_id'] == eats_id
    assert kwargs['picker_id'] == picker_id
    assert kwargs['paid_at'] == '2020-06-18T13:00:00'
    assert kwargs['amount'] == 1098.02
    assert kwargs['currency'] == 'RUB'


@pytest.mark.config(
    EATS_PICKER_ORDERS_RECEIPT_UPLOAD_SETTINGS={'timeout': 1, 'retries': 2},
)
@pytest.mark.parametrize(
    'eats_id, picker_id, picker_payment_amount, edadeal_status, '
    'picker_payment_status, expected_status, '
    'order_final_status, receipt_time',
    [
        pytest.param(
            DEFAULT_EATS_ID,
            DEFAULT_PICKER_ID,
            2,
            400,
            200,
            200,
            'complete',
            '20100618T105208',
            id='simple test',
        ),
    ],
)
@pytest.mark.now('2020-06-18T10:00:00')
@utils.send_order_events_config()
async def test_order_receipt_v2_comment(
        taxi_eats_picker_orders,
        mockserver,
        stq,
        stq_runner,
        eats_id,
        picker_id,
        picker_payment_amount,
        edadeal_status,
        picker_payment_status,
        expected_status,
        order_final_status,
        receipt_time,
        mock_processing,
):
    @mockserver.json_handler('/edadeal-checkprovider/v1/checks')
    def _mock_edadeal(request):
        assert (
            dict(parse.parse_qsl(request.get_data().decode()))
            == DEFAULT_RECEIPT
        )
        assert request.headers['X-Correlation-Id'] == eats_id
        return mockserver.make_response(status=edadeal_status)

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        if request.method == 'GET':
            assert request.query.get('card_type') == 'TinkoffBank'
            assert request.query.get('card_value') == 'test_cid_1'
            return mockserver.make_response(
                json={'amount': picker_payment_amount},
                status=picker_payment_status,
            )

        assert request.query.get('card_type') == 'TinkoffBank'
        assert request.query.get('card_value') == 'test_cid_1'
        assert request.json['amount'] == 0
        assert request.json['order_id'] == eats_id
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        assert request.json['eats_id'] == eats_id
        status = request.json['status']
        assert status in ('complete', 'paid')
        assert request.json['timestamp'] == '2020-06-18T10:00:00+00:00'
        expected_reasons = {
            'paid': 'receipt-uploaded',
            'complete': 'picking_only:receipt-uploaded',
        }
        assert request.json['reason'] == expected_reasons[status]

        return mockserver.make_response(json={}, status=400)

    receipt = copy.deepcopy(DEFAULT_RECEIPT)
    if receipt_time is not None:
        receipt['t'] = receipt_time

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/receipt',
        params={'eats_id': eats_id},
        json=receipt,
        headers=utils.da_headers(picker_id),
    )

    assert response.status_code == expected_status

    assert mock_processing.times_called == (1 if expected_status == 200 else 0)

    assert stq.receipt_upload.times_called == 1

    next_call = stq.receipt_upload.next_call()
    task_id = next_call['id']
    kwargs = next_call['kwargs']
    await stq_runner.receipt_upload.call(task_id=task_id, kwargs=kwargs)

    next_call = stq.receipt_upload.next_call()
    task_id = next_call['id']
    kwargs = next_call['kwargs']
    await stq_runner.receipt_upload.call(task_id=task_id, kwargs=kwargs)

    next_call = stq.receipt_upload.next_call()
    task_id = next_call['id']
    kwargs = next_call['kwargs']
    await stq_runner.receipt_upload.call(task_id=task_id, kwargs=kwargs)

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order/status',
        params={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.json()['status'] == 'receipt_rejected'
    assert (
        response.json()['comment']
        == 'Receipt upload failed. Reason: Время для загрузки чека истекло'
    )


@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type',
    [
        ['test_picker_id', 'picker'],
        ['test_picker_id', None],
        ['system', 'system'],
        ['system', None],
        ['customer_id', 'customer'],
    ],
)
async def test_order_receipt_v2_cart_items_mismatch_410(
        taxi_eats_picker_orders,
        stq,
        get_order_by_eats_id,
        init_measure_units,
        create_order_item,
        create_picked_item,
        is_deleted_by,
        deleted_by_type,
):
    eats_id = 'test_eats_id'
    picker_id = 'test_picker_id'
    order = get_order_by_eats_id(eats_id)
    order_id = order['id']
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
        '/4.0/eats-picker/api/v2/order/receipt',
        params={'eats_id': eats_id},
        json=DEFAULT_RECEIPT,
        headers=utils.da_headers(picker_id),
    )

    assert response.status_code == 410
    response = response.json()
    assert response['code'] == 'CART_ITEMS_MISMATCH'
    assert response['details']['items_mismatch'] == ['item_1', 'item_2']

    assert stq.receipt_upload.times_called == 0


@pytest.mark.now('2020-06-18T10:00:00')
@pytest.mark.parametrize(
    'author, author_type, expected_status',
    [
        ['someone', None, 200],
        ['customer', 'customer', 200],
        [None, 'system', 200],
        ['test_picker_id', 'system', 200],
        ['test_picker_id', 'picker', 200],
        ['another_picker', 'system', 410],
        ['another_picker', 'picker', 410],
    ],
)
@utils.send_order_events_config()
async def test_order_receipt_version_author(
        taxi_eats_picker_orders,
        mockserver,
        get_order_by_eats_id,
        init_measure_units,
        create_order_item,
        create_picked_item,
        author,
        author_type,
        expected_status,
        mock_processing,
):
    eats_id = 'test_eats_id'
    picker_id = 'test_picker_id'
    order = get_order_by_eats_id(eats_id)
    order_id = order['id']
    create_order_item(
        order_id=order_id, eats_item_id='deleted_item', version=0,
    )
    order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='added_item',
        version=1,
        author=author,
        author_type=author_type,
    )
    create_picked_item(
        order_item_id=order_item_id,
        picker_id=picker_id,
        cart_version=1,
        count=1,
    )

    @mockserver.json_handler('/edadeal-checkprovider/v1/checks')
    def _mock_edadeal(request):
        return {}

    picker_payment_amount = 2

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return {'amount': picker_payment_amount}

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        return {'isSuccess': True}

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/receipt',
        params={'eats_id': eats_id},
        json=DEFAULT_RECEIPT,
        headers=utils.da_headers(picker_id),
    )

    assert response.status_code == expected_status

    assert mock_processing.times_called == (1 if expected_status == 200 else 0)


@utils.upload_not_picked_items_config()
@pytest.mark.now('2020-06-18T10:00:00')
@utils.send_order_events_config()
async def test_order_receipt_upload_not_picked_items(
        taxi_eats_picker_orders,
        stq,
        stq_runner,
        mockserver,
        get_order_by_eats_id,
        init_measure_units,
        create_order_item,
        create_picked_item,
        mock_processing,
):
    @mockserver.json_handler('/edadeal-checkprovider/v1/checks')
    def _mock_edadeal(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        if request.method == 'GET':
            return mockserver.make_response(json={'amount': 2}, status=200)
        return mockserver.make_response(
            json={'order_id': DEFAULT_EATS_ID}, status=200,
        )

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        return mockserver.make_response(json={'isSuccess': True}, status=200)

    order = get_order_by_eats_id(DEFAULT_EATS_ID)
    o0_v0 = create_order_item(
        order['id'],
        '0',
        0,
        sold_by_weight=True,
        measure_value=100,
        quantity=3,
    )
    o1_v0 = create_order_item(order['id'], '1', 0)
    o2_v0 = create_order_item(order['id'], '2', 0, quantity=2)
    o3_v0 = create_order_item(
        order['id'],
        '3',
        0,
        sold_by_weight=True,
        measure_value=1000,
        measure_quantum=500,
        quantity=0.5,
    )
    create_order_item(order['id'], '4', 0, quantity=10)
    create_order_item(order['id'], '5', 0, quantity=10)
    o0_v1 = create_order_item(
        order['id'],
        '0',
        1,
        sold_by_weight=True,
        measure_value=100,
        quantity=3,
    )
    o1_v1 = create_order_item(order['id'], '1', 1)
    o4_v1 = create_order_item(order['id'], '4', 1, quantity=20)
    o5_v1 = create_order_item(order['id'], '5', 1, quantity=20)
    create_order_item(order['id'], '6', 1, replacements=[('3', o3_v0)])
    create_picked_item(o0_v0, DEFAULT_PICKER_ID, 0, weight=100)
    create_picked_item(o1_v0, DEFAULT_PICKER_ID, 0, count=1)
    create_picked_item(o2_v0, DEFAULT_PICKER_ID, 0, count=2)
    create_picked_item(o0_v1, DEFAULT_PICKER_ID, 1, weight=100)
    create_picked_item(o1_v1, DEFAULT_PICKER_ID, 1, count=1)
    create_picked_item(o4_v1, DEFAULT_PICKER_ID, 1, count=4)
    create_picked_item(o5_v1, DEFAULT_PICKER_ID, 1, count=14)

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/receipt',
        params={'eats_id': DEFAULT_EATS_ID},
        json=DEFAULT_RECEIPT,
        headers=utils.da_headers(DEFAULT_PICKER_ID),
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    next_call = stq.receipt_upload.next_call()
    task_id = next_call['id']
    kwargs = next_call['kwargs']
    await stq_runner.receipt_upload.call(task_id=task_id, kwargs=kwargs)

    assert stq.eats_picker_not_picked_items.times_called == 1
    kwargs = stq.eats_picker_not_picked_items.next_call()['kwargs']
    assert kwargs['place_id'] == str(order['place_id'])

    def key(item):
        return item['eats_item_id']

    assert sorted(kwargs['not_picked_items'], key=key) == sorted(
        [
            {'eats_item_id': '2', 'quantity': 2.0, 'quantity_picked': 0.0},
            {'eats_item_id': '3', 'quantity': 0.5, 'quantity_picked': 0.0},
            {'eats_item_id': '4', 'quantity': 10.0, 'quantity_picked': 4.0},
        ],
        key=key,
    )
    assert 'brand_id' not in kwargs


@utils.upload_not_picked_items_config()
@pytest.mark.now('2020-06-18T10:00:00')
@utils.send_order_events_config()
async def test_order_receipt_upload_not_picked_items_no_changes(
        taxi_eats_picker_orders,
        stq,
        stq_runner,
        mockserver,
        get_order_by_eats_id,
        init_measure_units,
        create_order_item,
        create_picked_item,
        mock_processing,
):
    @mockserver.json_handler('/edadeal-checkprovider/v1/checks')
    def _mock_edadeal(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        if request.method == 'GET':
            return mockserver.make_response(json={'amount': 2}, status=200)
        return mockserver.make_response(
            json={'order_id': DEFAULT_EATS_ID}, status=200,
        )

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        return mockserver.make_response(json={'isSuccess': True}, status=200)

    order = get_order_by_eats_id(DEFAULT_EATS_ID)
    o0_v0 = create_order_item(
        order['id'],
        '0',
        0,
        sold_by_weight=True,
        measure_value=100,
        quantity=3,
    )
    o1_v0 = create_order_item(order['id'], '1', 0, quantity=2)
    o2_v0 = create_order_item(order['id'], '2', 0)
    create_picked_item(o0_v0, DEFAULT_PICKER_ID, 0, weight=300)
    create_picked_item(o1_v0, DEFAULT_PICKER_ID, 0, count=2)
    create_picked_item(o2_v0, DEFAULT_PICKER_ID, 0, count=1)

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/receipt',
        params={'eats_id': DEFAULT_EATS_ID},
        json=DEFAULT_RECEIPT,
        headers=utils.da_headers(DEFAULT_PICKER_ID),
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    next_call = stq.receipt_upload.next_call()
    task_id = next_call['id']
    kwargs = next_call['kwargs']
    await stq_runner.receipt_upload.call(task_id=task_id, kwargs=kwargs)

    assert stq.eats_picker_not_picked_items.times_called == 0
