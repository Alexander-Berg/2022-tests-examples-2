import uuid

import pytest

from . import common
from . import consts
from . import experiments
from . import models


COMPENSATION_EVENT_POLICY = {
    'error_after': models.ONE_MINUTE_FROM_NOW,
    'retry_interval': 10,
    'stop_retry_after': models.SIX_MINUTES_FROM_NOW,
    'retry_count': 1,
}


@pytest.mark.now(models.NOW)
@pytest.mark.config(GROCERY_SUPPORT_NOTIFICATIONS_ENABLED=True)
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
@pytest.mark.parametrize(
    'compensation_type, is_full, currency, numeric_value, '
    'rounded_value, expected_processing_payload',
    [
        (
            'promocode',
            False,
            None,
            '15',
            15,
            {
                'reason': 'compensation_promocode',
                'promocode_value': 15,
                'promocode_type': 'percent',
            },
        ),
        (
            'voucher',
            False,
            'RUB',
            '8.35',
            9,
            {
                'reason': 'compensation_promocode',
                'promocode_value': 9,
                'promocode_value_numeric': '8.35',
                'promocode_type': 'fixed',
            },
        ),
        (
            'refund',
            False,
            'RUB',
            '8.35',
            9,
            {
                'reason': 'compensation_partial_refund',
                'items': [{'item_id': 'id1:st-md', 'refund_quantity': '2'}],
            },
        ),
        ('refund', True, 'RUB', '15', 15, {'reason': 'compensation_refund'}),
        (
            'superPlus',
            False,
            None,
            '15',
            15,
            {
                'reason': 'compensation_cashback',
                'compensation_value': 15,
                'compensation_source': 'admin_compensation',
            },
        ),
        (
            'percentPlus',
            False,
            None,
            # Value = ceil( 15% (rate) * 8.35 (items_price) ) = 2
            '2',
            2,
            {
                'reason': 'compensation_cashback',
                'compensation_value': 2,
                'compensation_source': 'admin_compensation',
            },
        ),
    ],
)
async def test_submit_compensation_pack(
        taxi_grocery_support,
        grocery_orders,
        grocery_cart,
        eats_compensations_matrix,
        pgsql,
        now,
        mockserver,
        processing,
        compensation_type,
        is_full,
        currency,
        numeric_value,
        rounded_value,
        expected_processing_payload,
):
    pack_id = 123
    compensation_uid = str(uuid.uuid4())
    situation_uid_1 = str(uuid.uuid4())
    situation_uid_2 = str(uuid.uuid4())
    order_id = 'order_id'
    compensation_maas_id = 11
    situation_one_maas_id = 14
    situation_two_maas_id = 15
    source = 'admin_compensation'
    situation_code = 'test_code'

    customer = common.create_default_customer(pgsql, now)

    compensation_info = {
        'compensation_value': rounded_value,
        'numeric_value': numeric_value,
        'status': 'in_progress',
    }
    if currency:
        compensation_info['currency'] = currency

    compensation = common.create_compensation_v2(
        pgsql,
        compensation_uid,
        compensation_maas_id,
        customer,
        situations=[situation_uid_1, situation_uid_2],
        main_situation_id=situation_one_maas_id,
        compensation_info=compensation_info,
        source=source,
        compensation_type=compensation_type,
        is_full=is_full,
        main_situation_code=situation_code,
    )

    situation_one_in_db = common.create_situation_v2(
        pgsql, situation_one_maas_id, situation_code=situation_code,
    )
    situation_one_in_db.update_db()

    situation_two_in_db = common.create_situation_v2(
        pgsql, situation_two_maas_id,
    )
    situation_two_in_db.update_db()

    order = models.Order(pgsql, order_id=order_id)
    grocery_orders.add_order(
        order_id=situation_one_in_db.order_id,
        user_info={
            'personal_phone_id': customer.personal_phone_id,
            'yandex_uid': customer.yandex_uid,
            'phone_id': customer.phone_id,
        },
    )

    grocery_cart.set_client_price('14')
    grocery_cart.set_items_v2(consts.CART_ITEMS)

    eats_compensations_matrix.set_get_pack_by_id_response(
        common.get_eats_compensation_pack(pack_id, compensation),
    )

    request_json = {
        'order_id': order.order_id,
        'compensation_pack_id': pack_id,
        'main_situation_id': situation_one_maas_id,
    }
    headers = {'X-Yandex-Login': compensation.support_login}

    response = await taxi_grocery_support.post(
        '/v3/api/compensation/submit-compensation-pack',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200

    compensation.compare_with_db()

    compensation.update()
    situation_one_in_db.update()
    situation_two_in_db.update()

    assert set(compensation.get_situations()) == {
        situation_one_in_db.get_id(),
        situation_two_in_db.get_id(),
    }
    assert (
        situation_one_in_db.get_bound_compensation() == compensation.get_id()
    )
    assert (
        situation_two_in_db.get_bound_compensation() == compensation.get_id()
    )

    expected_processing_payload['order_id'] = order.order_id
    expected_processing_payload[
        'compensation_id'
    ] = compensation.compensation_id
    expected_processing_payload['need_send_notification'] = False
    expected_processing_payload['event_policy'] = COMPENSATION_EVENT_POLICY

    events = list(processing.events(scope='grocery', queue='compensations'))
    assert len(events) == 2
    event = events[0]

    assert event.payload['order_id'] == order.order_id
    assert event.payload['reason'] == 'created'
    assert 'event_policy' not in event.payload

    assert events[1].payload == expected_processing_payload


@pytest.mark.now(models.NOW)
async def test_submit_compensation_pack_400(taxi_grocery_support, pgsql):
    pack_id = 123
    order_id = 'order_id'

    order = models.Order(pgsql, order_id=order_id)

    request_json = {
        'order_id': order.order_id,
        'compensation_pack_id': pack_id,
        'main_situation_id': '123',
    }
    headers = {'X-Yandex-Login': 'test_login'}

    response = await taxi_grocery_support.post(
        '/v3/api/compensation/submit-compensation-pack',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 400


@pytest.mark.now(models.NOW)
async def test_submit_compensation_pack_404(
        taxi_grocery_support,
        grocery_orders,
        grocery_cart,
        eats_compensations_matrix,
        pgsql,
        now,
        mockserver,
):
    pack_id = 123
    compensation_uid = str(uuid.uuid4())
    situation_uid_1 = str(uuid.uuid4())
    order_id = 'order_id'
    compensation_maas_id = 11
    situation_one_maas_id = 14

    customer = common.create_default_customer(pgsql, now)

    compensation_info = {'compensation_value': 15, 'status': 'in_progress'}
    compensation = common.create_compensation_v2(
        pgsql,
        compensation_uid,
        compensation_maas_id,
        customer,
        [situation_uid_1],
        situation_one_maas_id,
        compensation_info,
    )

    situation_one_in_db = common.create_situation_v2(
        pgsql, situation_one_maas_id,
    )
    situation_one_in_db.update_db()

    order = models.Order(pgsql, order_id=order_id)
    grocery_orders.add_order(
        order_id=situation_one_in_db.order_id,
        user_info={
            'personal_phone_id': customer.personal_phone_id,
            'yandex_uid': customer.yandex_uid,
            'phone_id': customer.phone_id,
        },
    )

    eats_compensations_matrix.set_error_code(404)

    request_json = {
        'order_id': order.order_id,
        'compensation_pack_id': pack_id,
        'main_situation_id': situation_one_maas_id,
    }
    headers = {'X-Yandex-Login': compensation.support_login}

    response = await taxi_grocery_support.post(
        '/v3/api/compensation/submit-compensation-pack',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 404
