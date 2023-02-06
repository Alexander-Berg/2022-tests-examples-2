import datetime

import pytest

from . import utils


PAYLOAD_STATUS_CHANGE = {
    'event_type': 'STATUS_CHANGE',
    'order_status': 'assigned',
    'order_nr': utils.ORDER_ID,
    'place_id': utils.PLACE_ID,
    'customer_id': None,
    'picker_id': utils.PICKER_ID,
    'customer_picker_phone_forwarding': None,
}

PAYLOAD_PICKER_PHONE_FORWARDING_READY = {
    'event_type': 'PICKER_PHONE_FORWARDING_READY',
    'order_status': 'assigned',
    'order_nr': utils.ORDER_ID,
    'place_id': utils.PLACE_ID,
    'customer_id': utils.CUSTOMER_ID,
    'picker_id': utils.PICKER_ID,
    'customer_picker_phone_forwarding': {
        'phone': '+7-whatever',
        'expires_at': '2020-10-20T20:50:00+00:00',
    },
}


async def test_retail_order_history_picker_order_events_status_change(
        environment, stq_runner, create_order, get_order_by_order_nr,
):
    payload = PAYLOAD_STATUS_CHANGE

    create_order(
        order_nr=utils.ORDER_ID,
        status_for_customer='confirmed',
        delivery_address='ул. Пушкина, д. Колотушкина',
        delivery_point={'latitude': 59.93507, 'longitude': 30.33811},
    )

    initial_order = get_order_by_order_nr(utils.ORDER_ID)
    assert not initial_order['picker_id']

    environment.set_default()
    environment.add_picker_order(
        picker_id=payload['picker_id'], picking_status=payload['order_status'],
    )
    await stq_runner.eats_retail_order_history_picker_order_events.call(
        task_id=utils.ORDER_ID, kwargs=payload,
    )

    updated_order = get_order_by_order_nr(utils.ORDER_ID)
    assert updated_order['picker_id'] == payload['picker_id']


@pytest.mark.now('2021-08-01T12:00:00.123456+00:00')
async def test_retail_order_history_picker_order_events_phone_forwarding(
        environment, now, stq_runner, create_order, get_order_by_order_nr,
):
    now = now.replace(tzinfo=datetime.timezone.utc)

    payload = PAYLOAD_PICKER_PHONE_FORWARDING_READY

    create_order(
        order_nr=utils.ORDER_ID,
        status_for_customer='confirmed',
        delivery_address='ул. Пушкина, д. Колотушкина',
        delivery_point={'latitude': 59.93507, 'longitude': 30.33811},
    )

    initial_order = get_order_by_order_nr(utils.ORDER_ID)
    assert not initial_order['picker_phone']

    environment.set_default()
    environment.add_picker_order(
        picker_id=payload['picker_id'], picking_status=payload['order_status'],
    )
    await stq_runner.eats_retail_order_history_picker_order_events.call(
        task_id=utils.ORDER_ID, kwargs=payload,
    )

    updated_order = get_order_by_order_nr(utils.ORDER_ID)
    assert (
        updated_order['picker_phone'][0]
        == payload['customer_picker_phone_forwarding']['phone']
    )
    assert updated_order['picker_phone'][1] == datetime.datetime.fromisoformat(
        payload['customer_picker_phone_forwarding']['expires_at'],
    )

    updated_order['picker_phone'] = None
    initial_order['updated_at'] = None
    updated_order['updated_at'] = None
    assert initial_order == updated_order
