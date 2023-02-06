# pylint: disable=too-many-lines
import datetime
import decimal
import json

import pytest

CREATED = 'created'
PAYED = 'payed'
CONFIRMED = 'confirmed'
READY_TO_DELIVERY = 'ready_to_delivery'
TAKEN = 'taken'
FINISHED = 'finished'
CANCELLED = 'cancelled'
PROMISE_CHANGED = 'promise_changed'
SENT = 'sent'

LOGBROKER_CONSUMER_SETTINGS = {
    'order_client_events_consumer': {
        'enabled': True,
        'chunk_size': 2,
        'queue_timeout_ms': 50,
        'config_poll_period_ms': 1000,
    },
}


def _get_payload(order_nr, order_event):
    payload = {'order_nr': order_nr, 'order_event': order_event}

    if order_event == CREATED:
        payload['created_at'] = '2019-10-31T11:20:00+00:00'
        payload['order_type'] = 'retail'
        payload['delivery_type'] = 'native'
        payload['shipping_type'] = 'delivery'
        payload['eater_id'] = '12345'
        payload['eater_personal_phone_id'] = '123123'
        payload['eater_passport_uid'] = 'yandex-uid'
        payload['taxi_user_id'] = 'taxi-user-id'
        payload['promised_at'] = '2020-09-04T16:26:43+00:00'
        payload['application'] = 'web'
        payload['place_id'] = '123123'
        payload['device_id'] = 'some_device_id'
        payload['delivery_coordinates'] = {'lat': 34.56, 'lon': 12.34}
        payload['payment_method'] = 'payment-method'
    elif order_event == PAYED:
        payload['payed_at'] = '2020-09-04T15:26:48+00:00'
    elif order_event == CONFIRMED:
        payload['payed_at'] = '2020-09-04T15:26:51+00:00'
    elif order_event == READY_TO_DELIVERY:
        payload['ready_to_delivery_at'] = '2020-09-04T18:59:52+03:00'
    elif order_event == TAKEN:
        payload['taken_at'] = '2020-09-04T15:56:51+00:00'
    elif order_event == FINISHED:
        payload['finished_at'] = '2020-09-04T15:59:51+00:00'
    elif order_event == CANCELLED:
        payload['cancelled_at'] = '2020-09-04T16:59:51+00:00'
        payload['cancellation_reason'] = 'not_ready'
        payload['cancelled_by'] = 'operator'
    elif order_event == PROMISE_CHANGED:
        payload['promised_at'] = '2020-09-04T17:59:51+00:00'
    elif order_event == SENT:
        payload['sent_at'] = '2020-09-04T15:36:51+00:00'
    else:
        raise Exception('unknown order_event {}'.format(order_event))

    return payload


def _merge_events(order_nr, events):
    payload = {}
    for order_event in events:
        payload.update(_get_payload(order_nr, order_event))
    return payload


async def _push_lb_order(taxi_eats_ordershistory, lb_order):
    message = str(json.dumps(lb_order))
    response = await taxi_eats_ordershistory.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-client-events-consumer',
                'data': message,
                'topic': '/eda/processing/testing/order-client-events',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200


async def _push_and_run_lb(taxi_eats_ordershistory, event):
    # send order confirmed by procaas
    await _push_lb_order(taxi_eats_ordershistory, event)

    # wait for lb messages to be read
    await taxi_eats_ordershistory.run_task(
        'order-client-events-consumer-lb_consumer',
    )


async def db_insert_order(pgsql, order_nr, order_status):
    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        f"""
            INSERT INTO eats_ordershistory.orders
              (order_id, order_source, eats_user_id, taxi_user_id, yandex_uid,
              place_id, status, delivery_location, total_amount, is_asap,
              created_at)
            VALUES
              ('{order_nr}', 'eda', '123123', '123123', '123123', 123,
              '{order_status}', '(1,1)', '0.0', True, NOW());""",
    )


def assert_db_orders(psql, expected_db_orders_count):
    cursor = psql.cursor()
    cursor.execute('SELECT * FROM eats_ordershistory.orders;')
    db_orders = cursor.fetchall()
    assert len(db_orders) == expected_db_orders_count


@pytest.mark.config(
    EATS_ORDERSHISTORY_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,db_order_status',
    [
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, PAYED]),
            ],
            PAYED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, CONFIRMED]),
            ],
            CONFIRMED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, TAKEN]),
            ],
            TAKEN,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, FINISHED]),
            ],
            FINISHED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, CANCELLED]),
            ],
            CANCELLED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, PROMISE_CHANGED]),
            ],
            CREATED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, CONFIRMED]),
                _merge_events('111111-100000', [CREATED, PAYED]),
            ],
            PAYED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, PAYED]),
                _merge_events('111111-100000', [CREATED, CONFIRMED]),
            ],
            CONFIRMED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, PAYED]),
                _merge_events('111111-100000', [CREATED, CONFIRMED]),
                _merge_events('111111-100000', [CREATED, TAKEN]),
                _merge_events('111111-100000', [CREATED, FINISHED]),
            ],
            FINISHED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, PAYED]),
            ],
            PAYED,
        ),
    ],
)
async def test_order_save_db(
        taxi_eats_ordershistory,
        pgsql,
        lb_orders,
        db_order_status,
        mock_external,
):
    order_nr = '111111-100000'

    for lb_order in lb_orders:
        await _push_and_run_lb(taxi_eats_ordershistory, lb_order)

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        f"""SELECT status::TEXT FROM eats_ordershistory.orders
        WHERE order_id='{order_nr}'""",
    )
    status = cursor.fetchone()[0]
    assert status == db_order_status


@pytest.mark.config(
    EATS_ORDERSHISTORY_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
async def test_sent_event(taxi_eats_ordershistory, pgsql):
    order_nr = '111111-100000'
    await db_insert_order(pgsql, order_nr, CREATED)
    await _push_and_run_lb(
        taxi_eats_ordershistory, _merge_events(order_nr, [CREATED, SENT]),
    )

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        f"""SELECT status FROM eats_ordershistory.orders
        WHERE order_id='{order_nr}'""",
    )
    db_status = cursor.fetchone()[0]
    assert db_status == 'sent'


@pytest.fixture(name='mock_external', autouse=True)
def _mock_external(mockserver, load_json, request):
    first_revision, last_revision = (
        request.param
        if hasattr(request, 'param')
        else (
            'revisions/revision_doc.json',
            'revisions/revision_doc_add_refund.json',
        )
    )

    @mockserver.json_handler(
        '/eats-core-orders/server/api/v1/order/get-address/' + '1234',
    )
    def _mock_address(request):
        return {
            'full_address': 'full_address_1',
            'entrance': 'entrance_1',
            'floor_number': 'floor_number_1',
            'office': 'office_1',
            'doorcode': 'doorcode_1',
            'comment': 'comment_1',
        }

    @mockserver.json_handler('/eats-order-revision/v1/revision/list')
    def _mock_revision_list(request):
        return {
            'order_id': request.query['order_id'],
            'revisions': [{'origin_revision_id': 'test_revision'}],
        }

    @mockserver.json_handler(
        '/eats-order-revision/v1/order-revision/customer-services/details',
    )
    def _mock_details(request):
        return load_json(first_revision)

    @mockserver.json_handler(
        '/eats-order-revision/v1/revision/latest/customer-services/details',
    )
    def _mock_latest_details(request):
        return load_json(last_revision)


@pytest.mark.config(
    EATS_ORDERSHISTORY_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,expected_db_orders_count',
    [
        (
            [
                _get_payload('1234', CREATED),
                _merge_events('1234', [CREATED, PAYED]),
            ],
            16,
        ),
        (
            [
                {'not_valid_message': 'not_valid_message'},
                _merge_events('1234', [CREATED, PAYED]),
            ],
            15,
        ),
    ],
)
async def test_order_save_db_different_orders(
        taxi_eats_ordershistory,
        pgsql,
        lb_orders,
        expected_db_orders_count,
        mock_external,
):
    for lb_order in lb_orders:
        await _push_and_run_lb(taxi_eats_ordershistory, lb_order)

    assert_db_orders(pgsql['eats_ordershistory'], expected_db_orders_count)


def check_db_order_status(pgsql, order_nr, status):
    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        'SELECT status ' 'FROM eats_ordershistory.orders WHERE order_id = %s;',
        (order_nr,),
    )
    statuses = list(cursor)
    assert len(statuses) == 1
    assert statuses[0] == (status,)


def get_order(
        status,
        total_amount,
        created_at,
        delivered_at=None,
        last_revision_id=None,
        flow_type='retail',
        cancel_reason=None,
        cancelled_at=None,
        ready_to_delivery_at=None,
        taken_at=None,
):
    return (
        '1234',  # order_id
        'eda',  # order_source
        12345,  # eats_user_id
        'taxi-user-id',  # taxi_user_id
        'yandex-uid',  # yandex_uid
        123123,  # place_id
        status,
        '(12.34,34.56)',  # delivery_location
        total_amount,
        True,  # is_asap
        cancel_reason,
        created_at,
        delivered_at,
        flow_type,
        'retail',  # order_type
        '1500',  # original_total_amount
        'RUB',  # currency
        'delivery',  # shipping_type
        'native',  # delivery_type
        last_revision_id,
        cancelled_at,
        ready_to_delivery_at,
        taken_at,
    )


QUERY_SELECT_CART = """SELECT order_id, name, quantity,
place_menu_item_id, origin_id, original_quantity, measure_unit,
parent_origin_id, cost_for_customer, refunded_amount, catalog_type,
standalone_parent_origin_id FROM eats_ordershistory.cart_items
WHERE order_id = %s;"""

QUERY_SELECT_ORDER = """SELECT order_id, order_source, eats_user_id,
taxi_user_id, yandex_uid, place_id, status, delivery_location, total_amount,
is_asap, cancel_reason, created_at, delivered_at, flow_type, order_type,
original_total_amount, currency, shipping_type, delivery_type,
last_revision_id, cancelled_at, ready_to_delivery_at, taken_at
FROM eats_ordershistory.orders WHERE order_id = %s;"""

QUERY_SELECT_ADDRESS = """SELECT order_id, full_address, entrance,
                       floor_number, office, doorcode, comment
                       FROM eats_ordershistory.addresses
                       WHERE order_id = %s;"""

CART = {
    (
        '1234',  # order_id
        'test_cp_name_1',  # name
        2,  # quantity
        1,  # place_menu_item_id
        'test_cp_origin_id',  # origin_id
        2,  # original_quantity
        None,  # measure_unit
        None,  # parent_origin_id
        decimal.Decimal('1500.00'),  # cost_for_customer
        None,  # refunded_amount
        'eats_nomenclature',  # catalog_type
        None,  # standalone_parent_origin_id
    ),
    (
        '1234',  # order_id
        'with_parent',  # name
        2,  # quantity
        None,  # place_menu_item_id
        None,  # origin_id
        2,  # original_quantity
        None,  # measure_unit
        'test_cp_origin_id',  # parent_origin_id
        decimal.Decimal('0.00'),  # cost_for_customer
        None,  # refunded_amount
        'eats_nomenclature',  # catalog_type
        None,  # standalone_parent_origin_id
    ),
    (
        '1234',  # order_id
        'standalone',  # name
        1,  # quantity
        None,  # place_menu_item_id
        None,  # origin_id
        1,  # original_quantity
        None,  # measure_unit
        None,  # parent_origin_id
        decimal.Decimal('0.00'),  # cost_for_customer
        None,  # refunded_amount
        'eats_nomenclature',  # catalog_type
        'test_cp_origin_id',  # standalone_parent_origin_id
    ),
}

CART_WITH_REFUND = {
    (
        '1234',  # order_id
        'test_cp_name_1',  # name
        1,  # quantity
        1,  # place_menu_item_id
        'test_cp_origin_id',  # origin_id
        2,  # original_quantity
        None,  # measure_unit
        None,  # parent_origin_id
        decimal.Decimal('500.00'),  # cost_for_customer
        decimal.Decimal('1000.00'),  # refunded_amount
        'eats_nomenclature',  # catalog_type
        None,  # standalone_parent_origin_id
    ),
    (
        '1234',  # order_id
        'with_parent',  # name
        2,  # quantity
        None,  # place_menu_item_id
        None,  # origin_id
        2,  # original_quantity
        None,  # measure_unit
        'test_cp_origin_id',  # parent_origin_id
        decimal.Decimal('0.00'),  # cost_for_customer
        decimal.Decimal('0.00'),  # refunded_amount
        'eats_nomenclature',  # catalog_type
        None,  # standalone_parent_origin_id
    ),
    (
        '1234',  # order_id
        'standalone',  # name
        1,  # quantity
        None,  # place_menu_item_id
        None,  # origin_id
        1,  # original_quantity
        None,  # measure_unit
        None,  # parent_origin_id
        decimal.Decimal('0.00'),  # cost_for_customer
        decimal.Decimal('0.00'),  # refunded_amount
        'eats_nomenclature',  # catalog_type
        'test_cp_origin_id',  # standalone_parent_origin_id
    ),
}

ADDRESS = (
    '1234',  # order_id
    'full_address_1',  # full_address
    'entrance_1',  # entrance
    'floor_number_1',  # floor_number
    'office_1',  # office
    'doorcode_1',  # doorcode
    'comment_1',  # comment
)

CART_WITHOUT_PRODUCT_ID = {
    (
        '1234',  # order_id
        'without_product_id',  # name
        2,  # quantity
        2,  # place_menu_item_id
        '2',  # origin_id
        None,  # original_quantity
        None,  # measure_unit
        None,  # parent_origin_id
        None,  # cost_for_customer
        None,  # refunded_amount
        'eats_nomenclature',  # catalog_type
        None,  # standalone_parent_origin_id
    ),
    (
        '1234',  # order_id
        'without_product_id_2',  # name
        1,  # quantity
        3,  # place_menu_item_id
        '3',  # origin_id
        None,  # original_quantity
        None,  # measure_unit
        None,  # parent_origin_id
        None,  # cost_for_customer
        None,  # refunded_amount
        'eats_nomenclature',  # catalog_type
        None,  # standalone_parent_origin_id
    ),
}


async def resend_stq_tasks(taxi_eats_ordershistory, stq):
    # pylint: disable=unused-variable
    for i in range(stq.eats_ordershistory_update_order_info.times_called):
        task = stq.eats_ordershistory_update_order_info.next_call()
        task.pop('eta')
        task['task_id'] = task.pop('id')
        task['queue_name'] = task.pop('queue')
        await taxi_eats_ordershistory.post('testsuite/stq', json=task)


def make_add_order_stq_task(task_id, kwargs):
    return {
        'queue_name': 'eats_ordershistory_add_order',
        'task_id': task_id,
        'args': [],
        'kwargs': kwargs,
    }


def make_stq_order(total_amount, cart):
    return {
        'eats_user_id': 12345,
        'taxi_user_id': 'taxi-user-id',
        'yandex_uid': 'yandex-uid',
        'order_source': 'eda',
        'place_id': 123123,
        'delivery_location': {
            'lon': 12.34,
            'lat': 34.56,
            'full_address': 'full_address_1',
            'entrance': 'entrance_1',
            'floor_number': 'floor_number_1',
            'office': 'office_1',
            'doorcode': 'doorcode_1',
            'comment': 'comment_1',
        },
        'total_amount': total_amount,
        'is_asap': True,
        'created_at': '2019-10-31T11:20:00+00:00',
        'cart': cart,
        'flow_type': 'retail',
    }


@pytest.mark.config(
    EATS_ORDERSHISTORY_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'created_stq_task, finished_stq_task',
    [
        (
            make_add_order_stq_task(
                task_id='1234:in_progress',
                kwargs={
                    'order': make_stq_order(
                        total_amount='1000',
                        cart=[
                            {
                                'place_menu_item_id': 1,
                                'product_id': 'test_cp_origin_id',
                                'name': 'test_cp_name_1',
                                'quantity': 2,
                                'origin_id': None,
                                'catalog_type': 'eats_nomenclature',
                            },
                            {
                                'place_menu_item_id': 2,
                                'product_id': None,
                                'name': 'without_product_id',
                                'quantity': 1,
                            },
                            {
                                'place_menu_item_id': 2,
                                'product_id': None,
                                'name': 'without_product_id',
                                'quantity': 1,
                            },
                            {
                                'place_menu_item_id': 3,
                                'product_id': None,
                                'name': 'without_product_id_2',
                                'quantity': 1,
                            },
                        ],
                    ),
                },
            ),
            make_add_order_stq_task(
                task_id='1234:delivered',
                kwargs={
                    'order': make_stq_order(
                        total_amount='500',
                        cart=[
                            {
                                'place_menu_item_id': 1,
                                'product_id': 'test_cp_origin_id',
                                'name': 'test_cp_name_1',
                                'quantity': 1,
                                'origin_id': None,
                                'catalog_type': 'eats_nomenclature',
                            },
                        ],
                    ),
                },
            ),
        ),
    ],
)
async def test_stq_with_procaas(
        taxi_eats_ordershistory,
        created_stq_task,
        finished_stq_task,
        pgsql,
        mock_external,
        stq,
):
    # send order in_progress by stq
    response = await taxi_eats_ordershistory.post(
        'testsuite/stq', json=created_stq_task,
    )
    assert response.status_code == 200
    assert response.json() == {'failed': False}

    await resend_stq_tasks(taxi_eats_ordershistory, stq)

    # send order created by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _merge_events('1234', [CREATED]),
    )

    await resend_stq_tasks(taxi_eats_ordershistory, stq)

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(QUERY_SELECT_ORDER, ('1234',))

    orders = list(cursor)
    assert len(orders) == 1
    created_at = datetime.datetime.fromisoformat('2019-10-31T14:20:00+03:00')
    assert orders[0] == get_order('created', '1500', created_at)

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(QUERY_SELECT_CART, ('1234',))

    carts = set(cursor)
    expected_cart = CART | CART_WITHOUT_PRODUCT_ID
    assert len(carts) == len(expected_cart)
    assert carts == expected_cart

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(QUERY_SELECT_ADDRESS, ('1234',))
    assert list(cursor)[0] == ADDRESS

    # send order payed by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _merge_events('1234', [CREATED, PAYED]),
    )

    check_db_order_status(pgsql, '1234', PAYED)

    # send order confirmed by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _merge_events('1234', [CREATED, CONFIRMED]),
    )

    check_db_order_status(pgsql, '1234', CONFIRMED)

    # send order ready by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory,
        _merge_events('1234', [CREATED, READY_TO_DELIVERY]),
    )

    check_db_order_status(pgsql, '1234', CONFIRMED)

    # send order taken by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _merge_events('1234', [CREATED, TAKEN]),
    )

    check_db_order_status(pgsql, '1234', TAKEN)

    # send order delivered by stq
    response = await taxi_eats_ordershistory.post(
        'testsuite/stq', json=finished_stq_task,
    )
    assert response.status_code == 200
    assert response.json() == {'failed': False}

    await resend_stq_tasks(taxi_eats_ordershistory, stq)

    # send order finished by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _merge_events('1234', [CREATED, FINISHED]),
    )

    await resend_stq_tasks(taxi_eats_ordershistory, stq)

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(QUERY_SELECT_ORDER, ('1234',))
    orders = list(cursor)
    assert len(orders) == 1
    delivered_at = datetime.datetime.fromisoformat('2020-09-04T18:59:51+03:00')
    taken_at = datetime.datetime.fromisoformat('2020-09-04T15:56:51+00:00')
    assert orders[0] == get_order(
        'finished',
        '500',
        created_at,
        delivered_at,
        'latest_test_revision',
        taken_at=taken_at,
    )

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(QUERY_SELECT_CART, ('1234',))
    expected_cart = CART_WITH_REFUND | CART_WITHOUT_PRODUCT_ID
    assert set(cursor) == expected_cart


@pytest.mark.config(
    EATS_ORDERSHISTORY_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
async def test_order_from_procaas_and_then_from_stq(
        taxi_eats_ordershistory, pgsql, mock_external, stq,
):
    # send order created by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _get_payload('1234', CREATED),
    )

    await resend_stq_tasks(taxi_eats_ordershistory, stq)

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(QUERY_SELECT_ORDER, ('1234',))

    orders = list(cursor)
    assert len(orders) == 1
    created_at = datetime.datetime.fromisoformat('2019-10-31T14:20:00+03:00')
    assert orders[0] == get_order(
        'created', '1500', created_at, flow_type='native',
    )

    # send order in_progress by stq
    request_body = make_add_order_stq_task(
        task_id='1234:in_progress',
        kwargs={
            'order': make_stq_order(
                total_amount='1000',
                cart=[
                    {
                        'place_menu_item_id': 1,
                        'product_id': 'test_cp_origin_id',
                        'name': 'test_cp_name_1',
                        'quantity': 2,
                        'origin_id': 'test_cp_origin_id',
                        'catalog_type': 'eats_nomenclature',
                    },
                ],
            ),
        },
    )

    response = await taxi_eats_ordershistory.post(
        'testsuite/stq', json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == {'failed': False}

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(QUERY_SELECT_ORDER, ('1234',))

    orders = list(cursor)
    assert len(orders) == 1
    created_at = datetime.datetime.fromisoformat('2019-10-31T14:20:00+03:00')
    assert orders[0] == get_order('created', '1500', created_at)

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(QUERY_SELECT_CART, ('1234',))

    carts = set(cursor)
    assert len(carts) == len(CART)
    assert carts == CART

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(QUERY_SELECT_ADDRESS, ('1234',))
    assert list(cursor)[0] == ADDRESS

    # send order payed by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _merge_events('1234', [CREATED, PAYED]),
    )

    check_db_order_status(pgsql, '1234', PAYED)

    # send order confirmed by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _merge_events('1234', [CREATED, CONFIRMED]),
    )

    check_db_order_status(pgsql, '1234', CONFIRMED)

    # send order ready by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory,
        _merge_events('1234', [CREATED, READY_TO_DELIVERY]),
    )

    check_db_order_status(pgsql, '1234', CONFIRMED)

    # send order taken by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _merge_events('1234', [CREATED, TAKEN]),
    )

    check_db_order_status(pgsql, '1234', TAKEN)

    # send order finished by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _merge_events('1234', [CREATED, CANCELLED]),
    )

    await resend_stq_tasks(taxi_eats_ordershistory, stq)

    # send order delivered by stq
    request_body['kwargs']['order']['task_id'] = '1234:cancelled'
    response = await taxi_eats_ordershistory.post(
        'testsuite/stq', json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == {'failed': False}

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(QUERY_SELECT_ORDER, ('1234',))
    orders = list(cursor)
    assert len(orders) == 1
    cancelled_at = datetime.datetime.fromisoformat('2020-09-04T16:59:51+00:00')
    taken_at = datetime.datetime.fromisoformat('2020-09-04T15:56:51+00:00')
    assert orders[0] == get_order(
        'cancelled',
        '1500',
        created_at,
        cancel_reason='not_ready',
        cancelled_at=cancelled_at,
        taken_at=taken_at,
    )

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(QUERY_SELECT_CART, ('1234',))

    assert set(cursor) == CART


@pytest.mark.config(
    EATS_ORDERSHISTORY_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize('init_status', [CANCELLED, FINISHED])
async def test_update_old_order(taxi_eats_ordershistory, pgsql, init_status):
    order_nr = '111111-100000'

    await db_insert_order(pgsql, order_nr, init_status)

    # send order created by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _get_payload(order_nr, CREATED),
    )

    await _push_and_run_lb(
        taxi_eats_ordershistory, _merge_events(order_nr, [CREATED, SENT]),
    )

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        f"""SELECT status FROM eats_ordershistory.orders
        WHERE order_id='{order_nr}'""",
    )
    db_status = cursor.fetchone()[0]
    assert db_status == init_status


@pytest.mark.config(
    EATS_ORDERSHISTORY_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'expected_eta',
    [
        pytest.param(
            '2035-09-17T10:31:30+00:00',
            marks=[
                pytest.mark.config(
                    EATS_ORDERSHISTORY_REVISIONS_LIST_REQUEST_DELAY={
                        'delay_ms': 30000,
                    },
                ),
                pytest.mark.now('2035-09-17T10:31:00+00:00'),
            ],
        ),
        pytest.param(
            '2035-09-17T10:31:00+00:00',
            marks=[
                pytest.mark.config(
                    EATS_ORDERSHISTORY_REVISIONS_LIST_REQUEST_DELAY={
                        'delay_ms': 0,
                    },
                ),
                pytest.mark.now('2035-09-17T10:31:00+00:00'),
            ],
        ),
    ],
)
async def test_change_stq_eta(taxi_eats_ordershistory, stq, expected_eta):
    # send order created by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _get_payload('111111-100000', CREATED),
    )

    assert stq.eats_ordershistory_update_order_info.times_called == 2

    stq.eats_ordershistory_update_order_info.next_call()
    # first task to update address
    stq_task = stq.eats_ordershistory_update_order_info.next_call()
    expected_eta_dt = datetime.datetime.fromisoformat(expected_eta).replace(
        tzinfo=None,
    )
    diff_eta = expected_eta_dt - stq_task['eta'].replace(tzinfo=None)
    assert diff_eta.total_seconds() < 1


@pytest.mark.config(
    EATS_ORDERSHISTORY_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'mock_external',
    [
        pytest.param(
            (
                'revisions/first_revision_doc.json',
                'revisions/last_revision_with_refunds_doc.json',
            ),
        ),
    ],
    indirect=True,
)
async def test_revisions_with_refunds(
        taxi_eats_ordershistory, mock_external, stq, pgsql,
):
    # send order created by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _get_payload('1234', CREATED),
    )

    await resend_stq_tasks(taxi_eats_ordershistory, stq)

    # send order finished by procaas
    await _push_and_run_lb(
        taxi_eats_ordershistory, _merge_events('1234', [CREATED, FINISHED]),
    )

    await resend_stq_tasks(taxi_eats_ordershistory, stq)

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(QUERY_SELECT_CART, ('1234',))

    assert set(cursor) == {
        (
            '1234',  # order_id
            'test_cp_name_1',  # name
            0,  # quantity
            None,  # place_menu_item_id
            'test_cp_origin_id',  # origin_id
            2,  # original_quantity
            None,  # measure_unit
            None,  # parent_origin_id
            decimal.Decimal('0.00'),  # cost_for_customer
            decimal.Decimal('1500.00'),  # refunded_amount
            'eats_nomenclature',  # catalog_type
            None,  # standalone_parent_origin_id
        ),
        (
            '1234',  # order_id
            'test_cp_name_2',  # name
            1,  # quantity
            None,  # place_menu_item_id
            'test_cp_origin_id_1',  # origin_id
            0,  # original_quantity
            None,  # measure_unit
            None,  # parent_origin_id
            decimal.Decimal('300.00'),  # cost_for_customer
            decimal.Decimal('-300.00'),  # refunded_amount
            'eats_nomenclature',  # catalog_type
            None,  # standalone_parent_origin_id
        ),
    }
