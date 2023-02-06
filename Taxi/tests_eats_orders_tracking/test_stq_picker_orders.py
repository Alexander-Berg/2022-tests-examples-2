import datetime

import pytest

ORDER_NR = '111111-222222'
PICKER_ID = '12345'


def make_config_stq_retry(
        max_exec_tries=10, max_reschedule_counter=10, reschedule_seconds=10,
):
    return {
        'stq_orders': {
            'max_exec_tries': 10,
            'max_reschedule_counter': 10,
            'reschedule_seconds': 10,
        },
        'stq_couriers': {
            'max_exec_tries': 10,
            'max_reschedule_counter': 10,
            'reschedule_seconds': 10,
        },
        'stq_orders_eta': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_picker_orders': {
            'max_exec_tries': max_exec_tries,
            'max_reschedule_counter': max_reschedule_counter,
            'reschedule_seconds': reschedule_seconds,
        },
        'stq_cargo_waybill_changes': {
            'max_exec_tries': max_exec_tries,
            'max_reschedule_counter': max_reschedule_counter,
            'reschedule_seconds': reschedule_seconds,
        },
        'stq_order_taken_push': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_order_to_another_eater_sms': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
    }


def get_stq_orders_kwargs(
        order_nr,
        place_id,
        order_status,
        event_type='STATUS_CHANGE',
        created_at='2020-10-28T18:26:43.51+00:00',
        picker_phone=None,
        picker_id='picker_id',
        phone_expires_at='2020-10-28T21:26:43.51+00:00',
):
    phone = None
    if picker_phone is not None:
        phone = {'phone': picker_phone, 'expires_at': phone_expires_at}
    kwargs = {
        'event_type': event_type,
        'order_status': order_status,
        'order_nr': order_nr,
        'place_id': place_id,
        'created_at': created_at,
        'customer_id': 'customer_id',
        'picker_id': picker_id,
        'customer_picker_phone_forwarding': phone,
    }

    return kwargs


def get_picker_order_info(order_nr, get_cursor):
    cursor = get_cursor()
    cursor.execute(
        'SELECT order_nr, payload FROM eats_orders_tracking.picker_orders '
        'WHERE order_nr = %s',
        [order_nr],
    )
    return cursor.fetchone()


def get_picker_picker_phone(picker_id, get_cursor):
    cursor = get_cursor()
    cursor.execute(
        'SELECT picker_id, personal_phone_id, extension, ttl '
        'FROM eats_orders_tracking.picker_phones '
        'WHERE picker_id = %s',
        [picker_id],
    )
    return cursor.fetchone()


def make_order_json_in_db(
        kwargs,
        new_at=None,
        assigned_at=None,
        picking_at=None,
        picked_up_at=None,
        paid_at=None,
):
    status_history = {}
    if new_at is not None:
        status_history['new_at'] = new_at
    if assigned_at is not None:
        status_history['assigned_at'] = assigned_at
    if picking_at is not None:
        status_history['picking_at'] = picking_at
    if picked_up_at is not None:
        status_history['picked_up_at'] = picked_up_at
    if paid_at is not None:
        status_history['paid_at'] = paid_at
    return {
        'picker_id': kwargs['picker_id'],
        'status': kwargs['order_status'],
        'status_history': status_history,
    }


def insert_bad_order(get_cursor, order_nr):
    bad_payload = '{}'
    cursor = get_cursor()
    cursor.execute(
        'INSERT INTO eats_orders_tracking.picker_orders '
        '(order_nr, payload) VALUES (%s, %s)',
        [order_nr, bad_payload],
    )


def make_phone_number(number, extension=None):
    if extension:
        return number + ',,' + extension
    return number


@pytest.mark.parametrize(
    'event_type',
    ['ITEM_ADD', 'ITEM_REPLACE', 'ITEM_SOFT_DELETE', 'ITEM_PICKED'],
)
@pytest.mark.config(EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry())
async def test_stq_picker_orders_unsupported_event_type(
        stq_runner, get_cursor, event_type,
):
    kwargs = get_stq_orders_kwargs(
        order_nr=ORDER_NR,
        place_id='40',
        order_status='new',
        event_type=event_type,
    )
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    assert not get_picker_order_info(kwargs['order_nr'], get_cursor)


@pytest.mark.now('2020-10-28T18:20:43.51+00:00')
@pytest.mark.config(EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry())
async def test_stq_picker_orders_new_order(stq_runner, get_cursor):
    kwargs = get_stq_orders_kwargs(
        order_nr=ORDER_NR, place_id='40', order_status='new', created_at=None,
    )
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    order_nr, order_payload = get_picker_order_info(
        kwargs['order_nr'], get_cursor,
    )
    assert order_nr == kwargs['order_nr']
    assert order_payload == make_order_json_in_db(
        kwargs, new_at='2020-10-28T18:20:43.51+00:00',
    )


@pytest.mark.config(EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry())
async def test_stq_picker_orders_order_status_changes(stq_runner, get_cursor):
    new_at = '2020-10-28T19:26:43.51+00:00'
    kwargs = get_stq_orders_kwargs(
        order_nr=ORDER_NR,
        place_id='40',
        order_status='new',
        created_at=new_at,
    )
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    _, order_payload = get_picker_order_info(kwargs['order_nr'], get_cursor)
    assert order_payload == make_order_json_in_db(kwargs, new_at=new_at)

    assigned_at = '2020-10-28T20:26:43.51+00:00'
    kwargs['order_status'] = 'assigned'
    kwargs['created_at'] = assigned_at
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )

    _, order_payload = get_picker_order_info(kwargs['order_nr'], get_cursor)
    assert order_payload == make_order_json_in_db(
        kwargs, new_at=new_at, assigned_at=assigned_at,
    )

    picking_at = '2020-10-28T21:26:43.51+00:00'
    kwargs['order_status'] = 'picking'
    kwargs['created_at'] = picking_at
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )

    _, order_payload = get_picker_order_info(kwargs['order_nr'], get_cursor)
    assert order_payload == make_order_json_in_db(
        kwargs, new_at=new_at, assigned_at=assigned_at, picking_at=picking_at,
    )

    picked_up_at = '2020-10-28T22:26:43.51+00:00'
    kwargs['order_status'] = 'picked_up'
    kwargs['created_at'] = picked_up_at
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )

    _, order_payload = get_picker_order_info(kwargs['order_nr'], get_cursor)
    assert order_payload == make_order_json_in_db(
        kwargs,
        new_at=new_at,
        assigned_at=assigned_at,
        picking_at=picking_at,
        picked_up_at=picked_up_at,
    )

    paid_at = '2020-10-28T23:26:43.51+00:00'
    kwargs['order_status'] = 'paid'
    kwargs['created_at'] = paid_at
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )

    _, order_payload = get_picker_order_info(kwargs['order_nr'], get_cursor)
    assert order_payload == make_order_json_in_db(
        kwargs,
        new_at=new_at,
        assigned_at=assigned_at,
        picking_at=picking_at,
        picked_up_at=picked_up_at,
        paid_at=paid_at,
    )


@pytest.mark.config(EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry())
async def test_stq_picker_orders_wrong_events_order(stq_runner, get_cursor):
    # Check if events were received in wrong order (assigned before new)
    assigned_at = '2020-10-28T20:26:43.51+00:00'
    kwargs = get_stq_orders_kwargs(
        order_nr=ORDER_NR,
        place_id='40',
        order_status='assigned',
        created_at=assigned_at,
    )
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )

    _, order_payload = get_picker_order_info(kwargs['order_nr'], get_cursor)
    assert order_payload == make_order_json_in_db(
        kwargs, assigned_at=assigned_at,
    )

    new_at = '2020-10-28T19:26:43.51+00:00'
    kwargs['order_status'] = 'new'
    kwargs['created_at'] = new_at
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    _, order_payload = get_picker_order_info(kwargs['order_nr'], get_cursor)
    assert order_payload == make_order_json_in_db(
        kwargs, new_at=new_at, assigned_at=assigned_at,
    )


@pytest.mark.config(EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry())
async def test_stq_picker_orders_order_status_lost(stq_runner, get_cursor):
    # Check that if some events weren't received
    new_at = '2020-10-28T19:26:43.51+00:00'
    kwargs = get_stq_orders_kwargs(
        order_nr=ORDER_NR,
        place_id='40',
        order_status='new',
        created_at=new_at,
    )
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    _, order_payload = get_picker_order_info(kwargs['order_nr'], get_cursor)
    assert order_payload == make_order_json_in_db(kwargs, new_at=new_at)

    paid_at = '2020-10-28T20:26:43.51+00:00'
    kwargs = get_stq_orders_kwargs(
        order_nr=ORDER_NR,
        place_id='40',
        order_status='paid',
        created_at=paid_at,
    )
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )

    _, order_payload = get_picker_order_info(kwargs['order_nr'], get_cursor)
    assert order_payload == make_order_json_in_db(
        kwargs, new_at=new_at, paid_at=paid_at,
    )


@pytest.mark.config(
    EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry(
        max_exec_tries=10, max_reschedule_counter=10, reschedule_seconds=0,
    ),
)
async def test_stq_picker_orders_retry_on_error(stq, stq_runner, get_cursor):
    # reschedule_seconds=0 so task so task finishes with an error and retries
    insert_bad_order(get_cursor, ORDER_NR)
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task',
        kwargs=get_stq_orders_kwargs(
            order_nr=ORDER_NR, place_id='40', order_status='new',
        ),
        expect_fail=True,
    )

    assert stq.eats_orders_tracking_picker_orders.has_calls is False


@pytest.mark.config(
    EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry(
        max_exec_tries=10, max_reschedule_counter=10, reschedule_seconds=0,
    ),
)
async def test_stq_picker_orders_stop_retries(stq, stq_runner, get_cursor):
    # exec_tries reached max value, stq will not be called
    insert_bad_order(get_cursor, ORDER_NR)
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task',
        kwargs=get_stq_orders_kwargs(
            order_nr=ORDER_NR, place_id='40', order_status='new',
        ),
        exec_tries=10,
        expect_fail=False,
    )

    assert stq.eats_orders_tracking_picker_orders.has_calls is False


@pytest.mark.config(
    EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry(
        max_exec_tries=10, max_reschedule_counter=10, reschedule_seconds=10,
    ),
)
async def test_stq_picker_orders_reschedule_on_error(
        stq, stq_runner, get_cursor,
):
    # Task failed and will be rescheduled
    insert_bad_order(get_cursor, ORDER_NR)
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task',
        kwargs=get_stq_orders_kwargs(
            order_nr=ORDER_NR, place_id='40', order_status='new',
        ),
        expect_fail=False,
    )

    assert stq.eats_orders_tracking_picker_orders.has_calls is True


@pytest.mark.config(
    EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry(
        max_exec_tries=10, max_reschedule_counter=10, reschedule_seconds=10,
    ),
)
async def test_stq_picker_orders_stop_reschedules(stq, stq_runner, get_cursor):
    # reschedule_counter reached max already and will not be called
    insert_bad_order(get_cursor, ORDER_NR)
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task',
        kwargs=get_stq_orders_kwargs(
            order_nr=ORDER_NR, place_id='40', order_status='new',
        ),
        reschedule_counter=10,
        expect_fail=False,
    )

    assert stq.eats_orders_tracking_picker_orders.has_calls is False


@pytest.mark.parametrize('extension', [None, '12345', ''])
@pytest.mark.config(EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry())
async def test_stq_picker_orders_phone_with_ext(
        stq_runner, get_cursor, extension, mock_eats_personal_store,
):
    phone = '+71234567891'
    expires_at = datetime.datetime(
        2020, 10, 29, 0, 26, 43, 510000, datetime.timezone.utc,
    )
    assert not get_picker_picker_phone(PICKER_ID, get_cursor)
    kwargs = get_stq_orders_kwargs(
        order_nr=ORDER_NR,
        place_id='40',
        order_status='assigned',
        event_type='PICKER_PHONE_FORWARDING_READY',
        picker_phone=make_phone_number(phone, extension),
        picker_id=PICKER_ID,
        phone_expires_at=expires_at.isoformat(),
    )
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    assert mock_eats_personal_store.times_called == 1
    db_picker_id, db_phone, db_extension, ttl = get_picker_picker_phone(
        PICKER_ID, get_cursor,
    )
    assert db_picker_id == PICKER_ID
    assert db_phone == 'id_' + phone
    assert ttl == expires_at
    if extension in [None, '']:
        assert not db_extension
    else:
        assert db_extension == extension


@pytest.mark.config(EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry())
async def test_stq_picker_orders_new_phone(
        stq_runner, get_cursor, mock_eats_personal_store,
):
    phone1 = '+71234567891'
    extension1 = '123'
    phone2 = '+71234567892'
    kwargs = get_stq_orders_kwargs(
        order_nr=ORDER_NR,
        place_id='40',
        order_status='assigned',
        event_type='PICKER_PHONE_FORWARDING_READY',
        picker_phone=make_phone_number(phone1, extension1),
        picker_id=PICKER_ID,
    )
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    db_picker_id, db_phone, db_extension, _ = get_picker_picker_phone(
        PICKER_ID, get_cursor,
    )
    assert db_picker_id == PICKER_ID
    assert db_phone == 'id_' + phone1
    assert db_extension == extension1

    kwargs = get_stq_orders_kwargs(
        order_nr=ORDER_NR,
        place_id='40',
        order_status='assigned',
        event_type='PICKER_PHONE_FORWARDING_READY',
        picker_phone=make_phone_number(phone2),
        picker_id=PICKER_ID,
    )
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    assert mock_eats_personal_store.times_called == 2
    db_picker_id, db_phone, db_extension, _ = get_picker_picker_phone(
        PICKER_ID, get_cursor,
    )
    assert db_picker_id == PICKER_ID
    assert db_phone == 'id_' + phone2
    assert not db_extension


@pytest.mark.config(EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry())
async def test_stq_picker_orders_personal_error(
        stq_runner, get_cursor, mockserver,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _handler_eats_personal_store(request):
        return mockserver.make_response(status=400)

    phone = '+71234567891'
    kwargs = get_stq_orders_kwargs(
        order_nr=ORDER_NR,
        place_id='40',
        order_status='assigned',
        event_type='PICKER_PHONE_FORWARDING_READY',
        picker_phone=make_phone_number(phone),
        picker_id=PICKER_ID,
    )
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=False,
    )
    db_data = get_picker_picker_phone(PICKER_ID, get_cursor)
    assert not db_data


@pytest.mark.config(
    EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry(
        reschedule_seconds=0,
    ),
)
async def test_stq_picker_orders_personal_timeout(
        stq_runner, get_cursor, mockserver, stq,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _handler_eats_personal_store(request):
        raise mockserver.NetworkError()

    phone = '+71234567891'
    kwargs = get_stq_orders_kwargs(
        order_nr=ORDER_NR,
        place_id='40',
        order_status='assigned',
        event_type='PICKER_PHONE_FORWARDING_READY',
        picker_phone=make_phone_number(phone),
        picker_id=PICKER_ID,
    )
    await stq_runner.eats_orders_tracking_picker_orders.call(
        task_id='sample_task', kwargs=kwargs, expect_fail=True,
    )
    db_data = get_picker_picker_phone(PICKER_ID, get_cursor)
    assert not db_data
    assert stq.eats_orders_tracking_picker_orders.has_calls is False
