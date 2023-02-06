# pylint: disable=too-many-lines
import pytest
import pytz

from . import utils

EATS_ID = '42'
PICKER_ID = '1122'


def without_trailing_zeros(iso_dt):
    left, right = iso_dt.split('+')
    return '+'.join([left.rstrip('0'), right])


@pytest.mark.parametrize(
    'api_handler',
    [
        pytest.param(
            '/4.0/eats-picker/api/v1/order/status', id='client handler',
        ),
        pytest.param('/api/v1/order/status', id='admin handler'),
    ],
)
async def test_get_every_status(
        taxi_eats_picker_orders,
        create_order,
        order_statuses_list,
        api_handler,
):
    not_mapped_statuses = []
    bad_mapped_statuses = []
    for status in order_statuses_list:
        eats_id = f'eats-id-{status}'
        picker_id = f'picker-id-{status}'
        create_order(eats_id=eats_id, picker_id=picker_id, state=status)
        response = await taxi_eats_picker_orders.get(
            api_handler,
            params={'eats_id': eats_id},
            headers=utils.da_headers(picker_id),
        )
        if response.status != 200:
            not_mapped_statuses.append(status)
        elif response.json()['status'] != status:
            bad_mapped_statuses.append(status)
    assert (
        not not_mapped_statuses
    ), f'Statuses {not_mapped_statuses} is not mapped'
    assert (
        not bad_mapped_statuses
    ), f'Incorrect mapping for statuses {bad_mapped_statuses}'


@pytest.mark.parametrize(
    'api_handler',
    [
        pytest.param(
            '/4.0/eats-picker/api/v1/order/status', id='client handler',
        ),
        pytest.param('/api/v1/order/status', id='admin handler'),
    ],
)
async def test_get_status_without_history(
        taxi_eats_picker_orders, create_order, api_handler,
):
    create_order(eats_id=EATS_ID, picker_id=PICKER_ID, state='assigned')
    response = await taxi_eats_picker_orders.get(
        api_handler,
        params={'eats_id': EATS_ID},
        headers=utils.da_headers(PICKER_ID),
    )
    assert response.status == 200
    payload = response.json()

    assert payload['status'] == 'assigned'
    assert payload['comment'] == ''
    assert 'reason_code' not in payload


@pytest.mark.parametrize(
    'api_handler',
    [
        pytest.param(
            '/4.0/eats-picker/api/v1/order/status', id='client handler',
        ),
        pytest.param('/api/v1/order/status', id='admin handler'),
    ],
)
@utils.send_order_events_config()
async def test_get_status_with_history(
        taxi_eats_picker_orders,
        create_order,
        get_last_order_status,
        mockserver,
        api_handler,
        mock_processing,
):
    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(_):
        return mockserver.make_response(json={'order_id': EATS_ID}, status=200)

    order_id = create_order(eats_id=EATS_ID, picker_id=PICKER_ID)
    await taxi_eats_picker_orders.delete(
        '/api/v1/order?eats_id=42', json={'comment': 'Because I can'},
    )
    response = await taxi_eats_picker_orders.get(
        api_handler,
        params={'eats_id': EATS_ID},
        headers=utils.da_headers(PICKER_ID),
    )
    assert response.status == 200
    payload = response.json()

    assert mock_processing.times_called == 1

    order_status = get_last_order_status(order_id)
    assert payload['updated_at'] == without_trailing_zeros(
        order_status['created_at'].astimezone(pytz.UTC).isoformat(),
    )
    assert payload['status'] == 'cancelled'
    assert payload['comment'] == 'Because I can'


@pytest.mark.parametrize(
    'api_handler',
    [
        pytest.param(
            '/4.0/eats-picker/api/v1/order/status', id='client handler',
        ),
        pytest.param('/api/v1/order/status', id='admin handler'),
    ],
)
async def test_get_status_of_not_existed_order(
        taxi_eats_picker_orders, create_order, api_handler,
):
    create_order(eats_id='', picker_id='', last_version=1, state='picking')
    response = await taxi_eats_picker_orders.get(
        api_handler,
        params={'eats_id': EATS_ID},
        headers=utils.da_headers(PICKER_ID),
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'api_handler',
    [
        pytest.param(
            '/4.0/eats-picker/api/v1/order/status', id='client handler',
        ),
        pytest.param('/api/v1/order/status', id='admin handler'),
    ],
)
@pytest.mark.parametrize(
    'comment, reason_code',
    [
        (None, None),
        ('Because I can', None),
        (None, 'UNKNOWN_CANCEL_REASON'),
        ('Because I can', 'UNKNOWN_CANCEL_REASON'),
    ],
)
async def test_get_order_status_if_multiple(
        taxi_eats_picker_orders,
        create_order,
        create_order_status,
        api_handler,
        comment,
        reason_code,
):
    order_id = create_order(
        eats_id=EATS_ID, picker_id=PICKER_ID, last_version=1, state='picking',
    )
    create_order_status(
        order_id, last_version=1, state='new', comment='new comment',
    )
    create_order_status(
        order_id, last_version=1, state='assigned', comment='assigned comment',
    )
    create_order_status(
        order_id, last_version=1, state='picking', comment='picking comment 1',
    )
    create_order_status(
        order_id,
        last_version=1,
        state='picking',
        comment=comment,
        reason_code=reason_code,
    )

    response = await taxi_eats_picker_orders.get(
        api_handler,
        params={'eats_id': EATS_ID},
        headers=utils.da_headers(PICKER_ID),
    )
    assert response.status == 200
    payload = response.json()

    assert payload['status'] == 'picking'
    assert payload['comment'] == (comment or '')
    if reason_code:
        assert payload['reason_code'] == reason_code
    else:
        assert 'reason_code' not in payload


@utils.polling_delay_config()
async def test_get_status_polling_delay_200(
        taxi_eats_picker_orders, create_order,
):
    create_order(eats_id=EATS_ID, picker_id=PICKER_ID, state='assigned')
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order/status',
        params={'eats_id': EATS_ID},
        headers=utils.da_headers(PICKER_ID),
    )

    assert response.status == 200
    assert response.headers['X-Polling-Delay'] == '5'
    assert (
        response.headers['X-Polling-Config']
        == 'picking=45s,auto_handle=3s,manual_handle=20s'
    )


@utils.polling_delay_config()
async def test_get_status_polling_delay_400(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.get(
        f'/4.0/eats-picker/api/v1/order/status',
    )

    assert response.status == 400
    assert 'X-Polling-Delay' not in response.headers
    assert 'X-Polling-Config' not in response.headers


@utils.polling_delay_config()
@pytest.mark.parametrize(
    'eats_id, picker_id',
    [[EATS_ID, 'other_picker'], ['other_order', PICKER_ID]],
)
async def test_get_status_polling_delay_404(
        taxi_eats_picker_orders, create_order, eats_id, picker_id,
):
    create_order(eats_id=EATS_ID, picker_id=PICKER_ID, state='assigned')
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order/status',
        params={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )

    assert response.status == 404
    assert response.headers['X-Polling-Delay'] == '5'
    assert (
        response.headers['X-Polling-Config']
        == 'picking=45s,auto_handle=3s,manual_handle=20s'
    )


@pytest.mark.parametrize(
    'source_state,dest_state,comment,reason_code,expected_code',
    [
        ('new', 'waiting_dispatch', None, None, 200),
        ('dispatching', 'waiting_dispatch', None, None, 200),
        ('dispatch_failed', 'waiting_dispatch', None, None, 200),
        ('assigned', 'waiting_dispatch', None, None, 200),
        ('picking', 'waiting_dispatch', None, None, 200),
        ('waiting_dispatch', 'dispatching', None, None, 200),
        ('dispatch_failed', 'dispatching', None, None, 200),
        ('dispatching', 'dispatch_failed', None, None, 200),
        ('dispatching', 'dispatch_failed', 'comment', None, 200),
        ('dispatching', 'dispatch_failed', None, 'UNKNOWN_CANCEL_REASON', 200),
        ('dispatching', 'dispatch_failed', '', 'UNKNOWN_CANCEL_REASON', 200),
        (
            'dispatching',
            'dispatch_failed',
            'comment',
            'PLACE_HAS_NO_PICKER',
            200,
        ),
        # Allow changing status to itself
        ('waiting_dispatch', 'waiting_dispatch', None, None, 202),
        ('dispatching', 'dispatching', None, None, 202),
        ('dispatch_failed', 'dispatch_failed', None, None, 202),
    ],
)
@utils.send_order_events_config()
async def test_post_order_status_success(
        taxi_eats_picker_orders,
        create_order,
        create_order_status,
        get_last_order_status,
        get_order,
        source_state,
        dest_state,
        comment,
        reason_code,
        expected_code,
        mock_processing,
):
    order_id = create_order(eats_id='42', last_version=1, state=source_state)
    create_order_status(
        order_id, last_version=1, state=source_state, comment='new comment',
    )

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/status?eats_id=42',
        json={
            'status': dest_state,
            'comment': comment,
            'reason_code': reason_code,
        },
    )
    assert response.status == expected_code

    assert mock_processing.times_called == (1 if expected_code == 200 else 0)

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == dest_state
    if response.status == 200:
        assert last_order_status['author_id'] is None
        assert last_order_status['comment'] == comment
        assert last_order_status['reason_code'] == reason_code

    assert get_order(order_id)['state'] == dest_state


@pytest.mark.parametrize(
    'api_handler',
    [
        pytest.param(
            '/4.0/eats-picker/api/v1/order/status', id='client handler',
        ),
        pytest.param('/api/v1/order/status', id='admin handler'),
    ],
)
@pytest.mark.parametrize(
    'comment, reason_code',
    [
        (None, None),
        ('', None),
        (None, 'UNKNOWN_CANCEL_REASON'),
        ('Unknown cancel reason', 'UNKNOWN_CANCEL_REASON'),
        ('Picker Dispatch: Place closes soon', 'PLACE_CLOSES_SOON'),
    ],
)
@utils.send_order_events_config()
async def test_post_and_get_order_status(
        taxi_eats_picker_orders,
        create_order,
        create_order_status,
        api_handler,
        comment,
        reason_code,
        mock_processing,
):
    order_id = create_order(
        eats_id=EATS_ID, picker_id=PICKER_ID, last_version=1, state='new',
    )
    create_order_status(
        order_id, last_version=1, state='new', comment='new comment',
    )

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/status',
        params={'eats_id': EATS_ID},
        json={
            'status': 'dispatch_failed',
            'comment': comment,
            'reason_code': reason_code,
        },
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    response = await taxi_eats_picker_orders.get(
        api_handler,
        params={'eats_id': EATS_ID},
        headers=utils.da_headers(PICKER_ID),
    )
    assert response.status == 200
    payload = response.json()

    assert payload['status'] == 'dispatch_failed'
    assert payload['comment'] == (comment or '')
    if reason_code:
        assert payload['reason_code'] == reason_code
    else:
        assert 'reason_code' not in payload


@pytest.mark.parametrize(
    'source_state,expected_code,dest_state,'
    'sql_eats_id,json_eats_id,sql_picker_id,header_picker_id',
    [
        ('picking', 204, 'picked_up', '42', '42', '1122', '1122'),
        ('picked_up', 202, 'picked_up', '42', '42', '1122', '1122'),
        ('assigned', 409, 'assigned', '42', '42', '1122', '1122'),
        ('packing', 409, 'packing', '42', '42', '1122', '1122'),
        ('picking', 404, 'picking', '24', '42', '1122', '1122'),
        ('picking', 404, 'picking', '42', '42', '1122', '2211'),
    ],
)
@utils.send_order_events_config()
async def test_finish_picking(
        taxi_eats_picker_orders,
        mockserver,
        create_order,
        create_order_status,
        get_last_order_status,
        get_order,
        source_state,
        expected_code,
        dest_state,
        sql_eats_id,
        json_eats_id,
        sql_picker_id,
        header_picker_id,
        mock_processing,
):
    order_id = create_order(
        eats_id=sql_eats_id,
        last_version=1,
        state=source_state,
        picker_id=sql_picker_id,
    )
    create_order_status(
        order_id, last_version=1, state=source_state, comment='new comment',
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def mock_eats_picker_payment(request):
        return mockserver.make_response(
            json={'order_id': sql_eats_id}, status=200,
        )

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/finish-picking',
        json={'eats_id': json_eats_id},
        headers=utils.da_headers(header_picker_id),
    )
    assert response.status == expected_code

    assert mock_processing.times_called == (1 if expected_code == 204 else 0)

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == dest_state
    if response.status == 204:
        assert last_order_status['author_id'] == header_picker_id

    order_db = get_order(order_id)
    assert order_db['state'] == dest_state
    assert mock_eats_picker_payment.times_called == int(expected_code == 204)


@pytest.mark.parametrize(
    'last_version_author, last_version_author_type, expected_status',
    [
        ['someone', None, 204],
        ['picker_id', 'picker', 204],
        ['picker_id', 'system', 204],
        ['customer', 'customer', 204],
        [None, 'system', 204],
        ['another_picker', 'picker', 410],
        ['another_picker', 'system', 410],
    ],
)
@utils.send_order_events_config()
async def test_finish_picking_version_author(
        taxi_eats_picker_orders,
        mockserver,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        last_version_author,
        last_version_author_type,
        expected_status,
        mock_processing,
):
    eats_id = 'eats_id'
    picker_id = 'picker_id'
    order_id = create_order(
        eats_id=eats_id, last_version=1, state='picking', picker_id=picker_id,
    )

    eats_item_id_1 = 'eats_item_id_1'
    eats_item_id_2 = 'eats_item_id_2'

    create_order_item(
        version=0, order_id=order_id, eats_item_id=eats_item_id_1, quantity=1,
    )
    item_id_1 = create_order_item(
        version=1,
        order_id=order_id,
        eats_item_id=eats_item_id_1,
        quantity=1,
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

    create_picked_item(order_item_id=item_id_1, picker_id=picker_id, count=1)
    create_picked_item(order_item_id=item_id_2, picker_id=picker_id, count=2)

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/finish-picking',
        json={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == expected_status

    assert mock_processing.times_called == (1 if expected_status == 204 else 0)


@pytest.mark.experiments3(filename='exp3_sequential_payment.json')
@utils.send_order_events_config()
@pytest.mark.parametrize(
    'picker_id, place_id, brand_id, order_state_old, expected_status',
    [
        ('111', 222, '333', None, 204),
        ('111', 222, '333', 'picking', 204),
        ('111', 222, '333', 'picked_up', 409),
        ('111', 222, '333', 'receipt_processing', 409),
        ('111', 222, '333', 'receipt_rejected', 409),
        ('111', 222, '333', 'paid', 204),
        ('111', 222, None, 'picked_up', 204),
        ('444', 555, 666, None, 204),
        ('444', 555, 666, 'picked_up', 204),
    ],
)
async def test_finish_picking_sequential_payment(
        taxi_eats_picker_orders,
        mockserver,
        create_order,
        mock_processing,
        picker_id,
        place_id,
        brand_id,
        order_state_old,
        expected_status,
):
    if order_state_old:
        create_order(
            eats_id='eats_id_old',
            state=order_state_old,
            picker_id='picker_id_old',
            place_id=place_id,
            brand_id=brand_id,
        )

    eats_id = 'eats_id_0'
    create_order(
        eats_id=eats_id,
        state='picking',
        picker_id=picker_id,
        place_id=place_id,
        brand_id=brand_id,
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/finish-picking',
        json={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == expected_status

    assert mock_processing.times_called == (1 if expected_status == 204 else 0)


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
async def test_finish_picking_cart_items_mismatch_410(
        taxi_eats_picker_orders,
        create_order,
        init_measure_units,
        create_order_item,
        create_picked_item,
        create_order_status,
        get_last_order_status,
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
        '/4.0/eats-picker/api/v1/order/finish-picking',
        json={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 410
    response = response.json()
    assert response['code'] == 'CART_ITEMS_MISMATCH'
    assert response['details']['items_mismatch'] == ['item_1', 'item_2']

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == 'picking'


@utils.picked_item_positions_config(True)
async def test_finish_picking_cart_positions_mismatch_410(
        taxi_eats_picker_orders,
        create_order,
        init_measure_units,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
        create_order_status,
        get_last_order_status,
):
    eats_id = 'eats_id'
    picker_id = 'picker_id'
    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, state='picking',
    )
    create_order_status(
        order_id, last_version=0, state='picking', comment='new comment',
    )
    picked_item_ids = []
    for i in range(4):
        order_item_id = create_order_item(
            order_id=order_id, eats_item_id=f'item_{i}', version=0,
        )
        picked_item_id = create_picked_item(
            order_item_id=order_item_id,
            picker_id=picker_id,
            cart_version=1,
            count=10,
        )
        picked_item_ids.append(picked_item_id)
    for i in range(len(picked_item_ids), len(picked_item_ids) * 2):
        order_item_id = create_order_item(
            order_id=order_id,
            eats_item_id=f'item_{i}',
            version=0,
            sold_by_weight=True,
        )
        picked_item_id = create_picked_item(
            order_item_id=order_item_id,
            picker_id=picker_id,
            cart_version=1,
            weight=100,
        )
        picked_item_ids.append(picked_item_id)

    create_picked_item_position(picked_item_ids[0], count=10)
    create_picked_item_position(picked_item_ids[1], count=4)
    create_picked_item_position(picked_item_ids[1], count=6)
    create_picked_item_position(picked_item_ids[2], count=4)
    create_picked_item_position(picked_item_ids[2], count=7)
    create_picked_item_position(picked_item_ids[4], weight=100)
    create_picked_item_position(picked_item_ids[5], weight=40)
    create_picked_item_position(picked_item_ids[5], weight=60)
    create_picked_item_position(picked_item_ids[6], weight=40)
    create_picked_item_position(picked_item_ids[6], weight=70)

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/finish-picking',
        json={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 410
    response = response.json()
    assert response['code'] == 'CART_POSITIONS_MISMATCH'
    assert response['details']['items_positions_mismatch'] == [
        'item_2',
        'item_3',
        'item_6',
        'item_7',
    ]

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == 'picking'


@pytest.mark.experiments3(filename='exp3_payment_coefficient.json')
@pytest.mark.parametrize('brand_id, payment_limit', ((111, 4500), (333, 3300)))
@pytest.mark.parametrize('require_approval', [False, True])
@utils.send_order_events_config()
async def test_finish_picking_require_approval_204(
        taxi_eats_picker_orders,
        brand_id,
        payment_limit,
        require_approval,
        mockserver,
        create_order,
        create_order_status,
        get_last_order_status,
        get_order,
        mock_processing,
):
    eats_id = '42'
    picker_id = '1122'
    source_state = 'picking'
    dest_state = 'picked_up'
    order_id = create_order(
        eats_id=eats_id,
        last_version=1,
        state=source_state,
        picker_id=picker_id,
        require_approval=require_approval,
        payment_value=3000,
        brand_id=brand_id,
        place_id=222,
    )
    create_order_status(
        order_id, last_version=1, state=source_state, comment='new comment',
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def mock_eats_picker_payment(request):
        assert request.query.get('card_type') == 'TinkoffBank'
        assert request.query.get('card_value') == 'cid_1'
        assert request.json.get('amount') == payment_limit
        assert request.json.get('order_id') == eats_id
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/finish-picking',
        json={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 204
    assert mock_processing.times_called == 1

    assert get_last_order_status(order_id)['state'] == dest_state
    order_db = get_order(order_id)
    assert order_db['state'] == dest_state
    assert order_db['payment_limit'] == payment_limit
    assert mock_eats_picker_payment.times_called == 1


@pytest.mark.parametrize(
    'flow_type,source_state,expected_code,dest_state,'
    'sql_eats_id,json_eats_id,sql_picker_id,header_picker_id',
    [
        (
            'picking_packing',
            'paid',
            204,
            'packing',
            '42',
            '42',
            '1122',
            '1122',
        ),
        ('picking_handing', 'paid', 409, 'paid', '42', '42', '1122', '1122'),
        ('picking_only', 'paid', 409, 'paid', '42', '42', '1122', '1122'),
        (
            'picking_packing',
            'picked_up',
            409,
            'picked_up',
            '42',
            '42',
            '1122',
            '1122',
        ),
        ('picking_packing', 'paid', 404, 'paid', '24', '42', '1122', '1122'),
        ('picking_packing', 'paid', 404, 'paid', '42', '42', '1122', '2211'),
        (
            'picking_packing',
            'packing',
            202,
            'packing',
            '42',
            '42',
            '1122',
            '1122',
        ),
        (
            'picking_handing',
            'packing',
            202,
            'packing',
            '42',
            '42',
            '1122',
            '1122',
        ),  # strage, but do nothing
    ],
)
@utils.send_order_events_config()
async def test_start_packing(
        taxi_eats_picker_orders,
        create_order,
        create_order_status,
        get_last_order_status,
        get_order,
        flow_type,
        source_state,
        expected_code,
        dest_state,
        sql_eats_id,
        json_eats_id,
        sql_picker_id,
        header_picker_id,
        mock_processing,
):
    order_id = create_order(
        eats_id=sql_eats_id,
        last_version=1,
        state=source_state,
        picker_id=sql_picker_id,
        flow_type=flow_type,
    )
    create_order_status(
        order_id, last_version=1, state=source_state, comment='new comment',
    )

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start-packing',
        json={'eats_id': json_eats_id},
        headers=utils.da_headers(header_picker_id),
    )
    assert response.status == expected_code

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == dest_state
    if response.status == 204:
        assert last_order_status['author_id'] == header_picker_id
        assert mock_processing.times_called == 1

    assert get_order(order_id)['state'] == dest_state


@pytest.mark.parametrize(
    'flow_type,source_state,expected_code,dest_state,'
    'sql_eats_id,json_eats_id,sql_picker_id,header_picker_id,'
    'pack_description,expected_pack_description',
    [
        (
            'picking_packing',
            'packing',
            204,
            'complete',
            '42',
            '42',
            '1122',
            '1122',
            'розовая коробка',
            'розовая коробка',
        ),
        (
            'picking_handing',
            'packing',
            409,
            'packing',
            '42',
            '42',
            '1122',
            '1122',
            'розовая коробка',
            None,
        ),
        (
            'picking_only',
            'packing',
            409,
            'packing',
            '42',
            '42',
            '1122',
            '1122',
            'розовая коробка',
            None,
        ),
        (
            'picking_packing',
            'picked_up',
            409,
            'picked_up',
            '42',
            '42',
            '1122',
            '1122',
            'розовая коробка',
            None,
        ),
        (
            'picking_packing',
            'paid',
            404,
            'paid',
            '24',
            '42',
            '1122',
            '1122',
            'розовая коробка',
            None,
        ),
        (
            'picking_packing',
            'paid',
            404,
            'paid',
            '42',
            '42',
            '1122',
            '2211',
            'розовая коробка',
            None,
        ),
        (
            'picking_packing',
            'complete',
            202,
            'complete',
            '42',
            '42',
            '1122',
            '1122',
            'розовая коробка',
            None,
        ),
        (
            'picking_handing',
            'complete',
            202,
            'complete',
            '42',
            '42',
            '1122',
            '1122',
            'розовая коробка',
            None,
        ),  # strage, but do nothing
    ],
)
@pytest.mark.now('2020-06-18T10:00:00')
@utils.send_order_events_config()
async def test_finish_packing(
        taxi_eats_picker_orders,
        mockserver,
        create_order,
        create_order_status,
        get_last_order_status,
        get_order,
        flow_type,
        source_state,
        expected_code,
        dest_state,
        sql_eats_id,
        json_eats_id,
        sql_picker_id,
        header_picker_id,
        pack_description,
        expected_pack_description,
        mock_processing,
):
    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        assert request.json == {
            'eats_id': sql_eats_id,
            'status': 'complete',
            'timestamp': '2020-06-18T10:00:00+00:00',
            'reason': 'finish-packing',
        }

        return mockserver.make_response(json={'isSuccess': True}, status=200)

    order_id = create_order(
        eats_id=sql_eats_id,
        last_version=1,
        state=source_state,
        picker_id=sql_picker_id,
        flow_type=flow_type,
    )
    create_order_status(
        order_id, last_version=1, state=source_state, comment='new comment',
    )

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/finish-packing',
        json={'eats_id': json_eats_id, 'pack_description': pack_description},
        headers=utils.da_headers(header_picker_id),
    )
    assert response.status == expected_code
    expect_order_completion = (
        source_state != 'complete' and dest_state == 'complete'
    )
    assert (
        _mock_eats_core_picker_orders.times_called == expect_order_completion
    )

    assert mock_processing.times_called == expect_order_completion

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == dest_state
    if response.status == 204:
        assert last_order_status['author_id'] == header_picker_id

    order_db = get_order(order_id)
    assert order_db['state'] == dest_state
    assert order_db['pack_description'] == expected_pack_description


@pytest.mark.parametrize(
    'flow_type,source_state,expected_code,dest_state,'
    'sql_eats_id,json_eats_id,sql_picker_id,header_picker_id',
    [
        (
            'picking_handing',
            'paid',
            204,
            'handing',
            '42',
            '42',
            '1122',
            '1122',
        ),
        ('picking_packing', 'paid', 409, 'paid', '42', '42', '1122', '1122'),
        ('picking_only', 'paid', 409, 'paid', '42', '42', '1122', '1122'),
        (
            'picking_handing',
            'picked_up',
            409,
            'picked_up',
            '42',
            '42',
            '1122',
            '1122',
        ),
        ('picking_handing', 'paid', 404, 'paid', '24', '42', '1122', '1122'),
        ('picking_handing', 'paid', 404, 'paid', '42', '42', '1122', '2211'),
        (
            'picking_handing',
            'handing',
            202,
            'handing',
            '42',
            '42',
            '1122',
            '1122',
        ),
        (
            'picking_packing',
            'handing',
            202,
            'handing',
            '42',
            '42',
            '1122',
            '1122',
        ),  # strage, but do nothing
    ],
)
@pytest.mark.now('2021-01-25T18:00:00')
@utils.send_order_events_config()
async def test_start_handing(
        taxi_eats_picker_orders,
        mockserver,
        create_order,
        create_order_status,
        get_last_order_status,
        get_order,
        flow_type,
        source_state,
        expected_code,
        dest_state,
        sql_eats_id,
        json_eats_id,
        sql_picker_id,
        header_picker_id,
        mock_processing,
):
    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        assert request.json == {
            'eats_id': sql_eats_id,
            'status': 'handing',
            'timestamp': '2021-01-25T18:00:00+00:00',
            'reason': 'start-handing',
        }

        return mockserver.make_response(json={'isSuccess': True}, status=200)

    order_id = create_order(
        eats_id=sql_eats_id,
        last_version=1,
        state=source_state,
        picker_id=sql_picker_id,
        flow_type=flow_type,
    )
    create_order_status(
        order_id, last_version=1, state=source_state, comment='new comment',
    )

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start-handing',
        json={'eats_id': json_eats_id},
        headers=utils.da_headers(header_picker_id),
    )
    assert response.status == expected_code

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == dest_state
    if response.status == 204:
        assert last_order_status['author_id'] == header_picker_id

    assert get_order(order_id)['state'] == dest_state

    expect_order_start_handing = (
        source_state != 'handing' and dest_state == 'handing'
    )
    assert _mock_eats_core_picker_orders.times_called == int(
        expect_order_start_handing,
    )
    assert mock_processing.times_called == expect_order_start_handing


@pytest.mark.parametrize(
    'flow_type,source_state,expected_code,dest_state,'
    'sql_eats_id,json_eats_id,sql_picker_id,header_picker_id',
    [
        (
            'picking_handing',
            'handing',
            204,
            'complete',
            '42',
            '42',
            '1122',
            '1122',
        ),
        (
            'picking_packing',
            'handing',
            409,
            'handing',
            '42',
            '42',
            '1122',
            '1122',
        ),
        (
            'picking_only',
            'handing',
            409,
            'handing',
            '42',
            '42',
            '1122',
            '1122',
        ),
        ('picking_handing', 'paid', 409, 'paid', '42', '42', '1122', '1122'),
        (
            'picking_handing',
            'handing',
            404,
            'handing',
            '24',
            '42',
            '1122',
            '1122',
        ),
        (
            'picking_handing',
            'handing',
            404,
            'handing',
            '42',
            '42',
            '1122',
            '2211',
        ),
        (
            'picking_handing',
            'complete',
            202,
            'complete',
            '42',
            '42',
            '1122',
            '1122',
        ),
        (
            'picking_packing',
            'complete',
            202,
            'complete',
            '42',
            '42',
            '1122',
            '1122',
        ),  # strage, but do nothing
    ],
)
@pytest.mark.now('2020-06-18T10:00:00')
@utils.send_order_events_config()
async def test_finish_handing(
        taxi_eats_picker_orders,
        mockserver,
        create_order,
        create_order_status,
        get_last_order_status,
        get_order,
        flow_type,
        source_state,
        expected_code,
        dest_state,
        sql_eats_id,
        json_eats_id,
        sql_picker_id,
        header_picker_id,
        mock_processing,
):
    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        assert request.json == {
            'eats_id': sql_eats_id,
            'status': 'complete',
            'timestamp': '2020-06-18T10:00:00+00:00',
            'reason': 'finish-handing',
        }

        return mockserver.make_response(json={'isSuccess': True}, status=200)

    order_id = create_order(
        eats_id=sql_eats_id,
        last_version=1,
        state=source_state,
        picker_id=sql_picker_id,
        flow_type=flow_type,
    )
    create_order_status(
        order_id, last_version=1, state=source_state, comment='new comment',
    )

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/finish-handing',
        json={'eats_id': json_eats_id},
        headers=utils.da_headers(header_picker_id),
    )
    assert response.status == expected_code
    expect_order_completion = (
        source_state != 'complete' and dest_state == 'complete'
    )
    assert (
        _mock_eats_core_picker_orders.times_called == expect_order_completion
    )

    assert mock_processing.times_called == expect_order_completion

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == dest_state
    if response.status == 204:
        assert last_order_status['author_id'] == header_picker_id
    assert get_order(order_id)['state'] == dest_state


@pytest.mark.parametrize(
    'source_state,dest_state',
    [
        ('paid', 'waiting_dispatch'),
        ('picked_up', 'waiting_dispatch'),
        ('packing', 'waiting_dispatch'),
        ('handing', 'waiting_dispatch'),
        ('complete', 'waiting_dispatch'),
        ('cancelled', 'waiting_dispatch'),
        # For 'dispatching' status not all forbidden transitions
        # are presented in the test
        ('cancelled', 'dispatching'),
        ('paid', 'dispatching'),
        ('assigned', 'dispatching'),
        ('picking', 'dispatching'),
        # For 'dispatch_failed' status not all forbidden transitions
        # are presented in the test
        ('waiting_dispatch', 'dispatch_failed'),
        ('picked_up', 'dispatch_failed'),
        ('cancelled', 'dispatch_failed'),
    ],
)
async def test_post_order_status_forbidden_transitions(
        taxi_eats_picker_orders,
        create_order,
        create_order_status,
        get_last_order_status,
        get_order,
        source_state,
        dest_state,
):
    order_id = create_order(eats_id='42', last_version=1, state=source_state)
    create_order_status(
        order_id, last_version=1, state=source_state, comment='new comment',
    )

    response = await taxi_eats_picker_orders.post(
        f'/api/v1/order/status?eats_id=42', json={'status': dest_state},
    )
    assert response.status == 409

    assert get_last_order_status(order_id)['state'] == source_state
    assert get_order(order_id)['state'] == source_state


@pytest.mark.parametrize(
    'previous_state,current_state,expected_state,expected_code,'
    'sql_eats_id,query_eats_id',
    [
        ('picking', 'dispatching', 'picking', 204, '42', '42'),
        ('picking', 'waiting_dispatch', 'waiting_dispatch', 202, '42', '42'),
        ('picking', 'dispatching', 'dispatching', 404, '43', '42'),
        ('dispatching', 'dispatching', 'dispatching', 409, '42', '42'),
    ],
)
@utils.send_order_events_config()
async def test_delete_cancel_dispatch(
        taxi_eats_picker_orders,
        create_order,
        create_order_status,
        get_last_order_status,
        get_order,
        previous_state,
        current_state,
        expected_state,
        expected_code,
        sql_eats_id,
        query_eats_id,
        mock_processing,
):
    order_id = create_order(
        eats_id=sql_eats_id, last_version=1, state=current_state,
    )
    create_order_status(
        order_id, last_version=1, state=previous_state, comment='prev comment',
    )
    create_order_status(
        order_id,
        last_version=1,
        state=current_state,
        comment='current comment',
    )
    response = await taxi_eats_picker_orders.post(
        '/api/v1/cancel-dispatch', json={'eats_id': query_eats_id},
    )
    assert response.status == expected_code

    assert mock_processing.times_called == (1 if expected_code == 204 else 0)

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == expected_state
    if expected_code == 204:
        assert last_order_status['author_id'] is None

    assert get_order(order_id)['state'] == expected_state


@pytest.mark.parametrize(
    'api_handler',
    [
        pytest.param(
            '/4.0/eats-picker/api/v1/order/status', id='client handler',
        ),
        pytest.param('/api/v1/order/status', id='admin handler'),
    ],
)
async def test_get_request_with_mistakes_400(
        taxi_eats_picker_orders, create_order, api_handler,
):
    create_order(eats_id=EATS_ID, picker_id=PICKER_ID, state='assigned')
    response = await taxi_eats_picker_orders.get(
        api_handler,
        params={'eaes_id': EATS_ID},
        headers=utils.da_headers(PICKER_ID),
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'api_handler',
    [
        pytest.param(
            '/4.0/eats-picker/api/v1/order/status', id='client handler',
        ),
        pytest.param('/api/v1/order/status', id='admin handler'),
    ],
)
async def test_get_wrong_eats_id_404(
        taxi_eats_picker_orders, create_order, api_handler,
):
    create_order(eats_id=EATS_ID, picker_id=PICKER_ID, state='assigned')
    wrong_id = '12345'
    response = await taxi_eats_picker_orders.get(
        api_handler,
        params={'eats_id': wrong_id},
        headers=utils.da_headers(PICKER_ID),
    )
    assert response.status == 404


async def test_get_bad_header_401(taxi_eats_picker_orders):
    bad_header = {
        'X-Request-Application-Version': '9.99 (9999)',
        'X-YaEda-CourierId': '123',
    }
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order/status',
        params={'eats_id': EATS_ID},
        headers=bad_header,
    )
    assert response.status == 401
