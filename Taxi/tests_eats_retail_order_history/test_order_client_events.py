import datetime

import pytest

from . import utils

ALLOWED_ORDER_TYPES = [utils.OrderType.shop, utils.OrderType.retail]


@pytest.fixture(name='assert_order_updated')
def _assert_order_updated(assert_mocks):
    def do_assert_order_updated(is_updated):
        if is_updated:
            assert_mocks(
                orders_retrieve_called=1,
                order_revision_list_called=1,
                order_revision_details_called=2,
                place_assortment_details_called=2,
                retrieve_places_called=1,
                get_picker_order_called=1,
                cart_diff_called=1,
                eda_candidates_list_called=1,
                performer_location_called=0,
                vgw_api_forwardings_called=1,
                cargo_driver_voiceforwardings_called=0,
            )
        else:
            assert_mocks()

    return do_assert_order_updated


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@pytest.mark.parametrize('is_order_exist', [False, True])
@pytest.mark.parametrize(
    'yandex_uid, do_add_by_yandex_uid',
    [(utils.YANDEX_UID, True), (None, False)],
)
@pytest.mark.parametrize(
    'order_type, do_add_by_order_type',
    [
        (order_type, order_type in ALLOWED_ORDER_TYPES)
        for order_type in utils.OrderType
    ],
)
async def test_stq_order_client_events_created(
        stq_runner,
        create_order,
        environment,
        is_order_exist,
        get_order_by_order_nr,
        yandex_uid,
        do_add_by_yandex_uid,
        order_type,
        do_add_by_order_type,
        assert_order_updated,
):
    if is_order_exist:
        create_order()
    environment.set_default()
    event = utils.make_order_client_event(
        utils.ORDER_ID,
        utils.OrderClientEvent.created,
        eater_passport_uid=yandex_uid,
        order_type=order_type,
    )

    await stq_runner.eats_retail_order_history_order_client_events.call(
        task_id='unique', kwargs={'event': event},
    )
    order = get_order_by_order_nr(event['order_nr'])

    do_add = do_add_by_yandex_uid and do_add_by_order_type

    assert (order is not None) == (do_add or is_order_exist)

    if do_add:
        assert order['order_nr'] == event['order_nr']
        assert order['yandex_uid'] == event['eater_passport_uid']
        assert order['customer_id'] == event['eater_id']
        assert order['place_id'] == event['place_id']
        assert order['personal_phone_id'] == event['eater_personal_phone_id']
        assert order['application'] == event['application']

    assert_order_updated(do_add)


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@pytest.mark.parametrize('is_order_exist', [False, True])
@pytest.mark.parametrize(
    'order_type, do_call_by_order_type',
    [
        (order_type, order_type in ALLOWED_ORDER_TYPES)
        for order_type in utils.OrderType
    ],
)
@pytest.mark.parametrize(
    'status_for_customer, do_call_by_status_for_customer',
    [
        (utils.StatusForCustomer.in_delivery, True),
        (utils.StatusForCustomer.delivered, False),
    ],
)
@pytest.mark.parametrize(
    'last_notification_type, do_call_by_last_notification',
    [
        (None, True),
        ('first_retail_order_changes', True),
        ('order_in_delivery', False),
    ],
)
@utils.currencies_config3()
async def test_stq_order_client_events_taken(
        stq_runner,
        stq,
        now,
        create_order,
        create_customer_notification,
        environment,
        assert_order_updated,
        is_order_exist,
        order_type,
        do_call_by_order_type,
        status_for_customer,
        do_call_by_status_for_customer,
        last_notification_type,
        do_call_by_last_notification,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    if is_order_exist:
        create_order()
    environment.set_default()
    environment.change_order_status(
        utils.YANDEX_UID, utils.ORDER_ID, status_for_customer.name,
    )

    if last_notification_type is not None:
        create_customer_notification(
            notification_type_v2=last_notification_type,
            idempotency_token=f'{utils.ORDER_ID}_{last_notification_type}',
            status_for_customer='in_delivery',
        )

    event = utils.make_order_client_event(
        utils.ORDER_ID, utils.OrderClientEvent.taken, order_type=order_type,
    )

    await stq_runner.eats_retail_order_history_order_client_events.call(
        task_id='unique', kwargs={'event': event},
    )

    do_update = is_order_exist and do_call_by_order_type
    do_call = (
        is_order_exist
        and do_call_by_order_type
        and do_call_by_status_for_customer
        and do_call_by_last_notification
    )
    assert stq.eats_retail_order_history_notify_customer.times_called == int(
        do_call,
    )

    if do_call:
        task_info = stq.eats_retail_order_history_notify_customer.next_call()
        del task_info['kwargs']['log_extra']
        notification_type = 'order_in_delivery'
        assert task_info['kwargs'] == {
            'notification_type': notification_type,
            'idempotency_token': f'{utils.ORDER_ID}_{notification_type}',
            'time': now.isoformat(),
            'level': 'INFO',
            'order_nr': utils.ORDER_ID,
            'total_cost_for_customer': {'currency_sign': '₽', 'value': '987'},
        }

    assert_order_updated(do_update)


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@pytest.mark.parametrize('is_order_exist', [False, True])
@pytest.mark.parametrize(
    'order_event',
    [
        utils.OrderClientEvent.confirmed,
        utils.OrderClientEvent.payed,
        utils.OrderClientEvent.cancelled,
        utils.OrderClientEvent.finished,
    ],
)
@pytest.mark.parametrize(
    'order_type, do_update_by_order_type',
    [
        (order_type, order_type in ALLOWED_ORDER_TYPES)
        for order_type in utils.OrderType
    ],
)
@utils.currencies_config3()
async def test_stq_order_client_events_default(
        stq_runner,
        now,
        create_order,
        environment,
        assert_order_updated,
        is_order_exist,
        order_event,
        order_type,
        do_update_by_order_type,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    if is_order_exist:
        create_order()
    environment.set_default()
    environment.change_order_status(
        utils.YANDEX_UID, utils.ORDER_ID, 'delivered',
    )

    event = utils.make_order_client_event(
        utils.ORDER_ID, order_event, order_type=order_type,
    )

    await stq_runner.eats_retail_order_history_order_client_events.call(
        task_id='unique', kwargs={'event': event},
    )

    do_update = is_order_exist and do_update_by_order_type

    assert_order_updated(do_update)
