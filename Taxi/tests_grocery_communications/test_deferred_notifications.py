from typing import Optional

import pytest

from tests_grocery_communications import configs
from tests_grocery_communications import consts
from tests_grocery_communications import models


def _assert_stq(stq_handler, task_id=None, **vargs):
    stq_call = stq_handler.next_call()
    if task_id is not None:
        assert stq_call['id'] == task_id
    kwargs = stq_call['kwargs']
    for key in vargs:
        assert kwargs[key] == vargs[key], key


@pytest.fixture
def _run_stq(mockserver, stq_runner):
    async def _inner(
            order_id,
            group_type,
            expect_fail: bool = False,
            exec_tries: Optional[int] = None,
    ):
        await stq_runner.grocery_communications_deferred_notification.call(
            task_id=order_id,
            kwargs={'order_id': order_id, 'group_type': group_type},
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


@pytest.mark.parametrize(
    'apology_reason_type, is_deferred',
    [('long_courier_assignment', False), ('long_delivery', True)],
)
@configs.DEFERRED_NOTIFICATIONS_SETTINGS
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_apology_notification_is_deferred(
        pgsql,
        stq,
        taxi_grocery_communications,
        grocery_orders,
        ucommunications,
        apology_reason_type,
        is_deferred,
):
    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale='en',
        app_info=f'app_name={consts.APP_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/apology-notification',
        json={
            'order_id': consts.ORDER_ID,
            'apology_reason_type': apology_reason_type,
        },
    )
    assert response.status_code == 200

    if is_deferred:
        assert ucommunications.times_notification_push_called() == 0
        deferred_notification = models.DeferredNotification(
            pgsql=pgsql,
            order_id=consts.ORDER_ID,
            group_type='assigned_courier',
            notification_type='courier_is_late',
        )
        deferred_notification.compare_with_db()
        _assert_stq(
            stq.grocery_communications_deferred_notification,
            task_id=deferred_notification.group_type
            + '-'
            + deferred_notification.order_id,
            order_id=deferred_notification.order_id,
            group_type=deferred_notification.group_type,
        )
    else:
        assert ucommunications.times_notification_push_called() == 1


@pytest.mark.parametrize(
    'order_notification_code, is_deferred',
    [('delivered', False), ('delivering', True)],
)
@configs.DEFERRED_NOTIFICATIONS_SETTINGS
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_delivering_notification_is_deferred(
        taxi_grocery_communications,
        grocery_orders,
        pgsql,
        stq,
        ucommunications,
        order_notification_code,
        is_deferred,
):
    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale='en',
        app_info=f'app_name={consts.APP_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification',
        json={
            'code': order_notification_code,
            'payload': {},
            'order_id': consts.ORDER_ID,
        },
    )
    assert response.status_code == 200

    if is_deferred:
        assert ucommunications.times_notification_push_called() == 0
        deferred_notification = models.DeferredNotification(
            pgsql=pgsql,
            order_id=consts.ORDER_ID,
            group_type='assigned_courier',
            notification_type='courier_picked_up_order',
        )
        deferred_notification.compare_with_db()
        _assert_stq(
            stq.grocery_communications_deferred_notification,
            task_id=deferred_notification.group_type
            + '-'
            + deferred_notification.order_id,
            order_id=deferred_notification.order_id,
            group_type=deferred_notification.group_type,
        )
    elif order_notification_code in consts.STATUS_CHANGE_CODES:
        assert ucommunications.times_notification_push_called() == 0
        deferred_notification = models.DeferredNotification(
            pgsql=pgsql,
            order_id=consts.ORDER_ID,
            group_type='status_change',
            notification_type=order_notification_code,
        )
        deferred_notification.compare_with_db()
        _assert_stq(
            stq.grocery_communications_deferred_notification,
            task_id=deferred_notification.group_type
            + '-'
            + deferred_notification.order_id,
            order_id=deferred_notification.order_id,
            group_type=deferred_notification.group_type,
        )
    else:
        assert ucommunications.times_notification_push_called() == 1


@configs.DEFERRED_NOTIFICATIONS_SETTINGS
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
@configs.GROCERY_COMMUNICATIONS_TRACKING_DEEPLINK_PREFIX
async def test_stq_call(pgsql, _run_stq, grocery_orders, ucommunications):
    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale='en',
        app_info=f'app_name={consts.APP_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )

    deferred_notification_1 = models.DeferredNotification(
        pgsql=pgsql,
        order_id=consts.ORDER_ID,
        group_type='assigned_courier',
        notification_type='courier_picked_up_order',
        is_sent=False,
    )
    deferred_notification_2 = models.DeferredNotification(
        pgsql=pgsql,
        order_id=consts.ORDER_ID,
        group_type='assigned_courier',
        notification_type='courier_is_late',
        is_sent=False,
    )
    deferred_notification_1.update_db()
    deferred_notification_2.update_db()

    expected_title = 'The order is delayed'
    expected_text = (
        'Sorry, the delivery is delayed. '
        'The courier is in a hurry to get to you'
    )
    expected_deeplink = consts.LAVKA_TRACKING_DEEPLINK_PREFIX + consts.ORDER_ID

    ucommunications.check_request(
        title=expected_title,
        text=expected_text,
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
        push_intent='grocery.apology',
        deeplink=expected_deeplink,
    )

    await _run_stq(
        order_id=deferred_notification_1.order_id,
        group_type=deferred_notification_1.group_type,
    )
    assert ucommunications.times_notification_push_called() == 1

    deferred_notification_1.is_sent = True
    deferred_notification_2.is_sent = True
    deferred_notification_1.compare_with_db()
    deferred_notification_2.compare_with_db()


@configs.DEFERRED_NOTIFICATIONS_SETTINGS
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
@configs.GROCERY_COMMUNICATIONS_TRACKING_DEEPLINK_PREFIX
@pytest.mark.parametrize(
    'notification_type, expected_reason, expected_title, expected_body',
    [
        (
            'ready_for_pickup',
            'order_status',
            'Yandex.Grocery',
            'The order short-id is ready for pickup',
        ),
        (
            'accepted',
            'order_status',
            'Yandex.Grocery',
            'The order short-id is accepted',
        ),
        (
            'assembling',
            'order_status',
            'Yandex.Grocery',
            'The order short-id is assembling',
        ),
        (
            'ready_for_dispatch',
            'order_status',
            'Yandex.Grocery',
            'The order short-id was assembled and is ready for delivery',
        ),
        (
            'delivered',
            'order_status',
            'Yandex.Grocery',
            'Your order has been delivered',
        ),
    ],
)
async def test_stq_call_status_change(
        pgsql,
        _run_stq,
        grocery_orders,
        ucommunications,
        notification_type,
        expected_reason,
        expected_title,
        expected_body,
):
    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        short_order_id='short-id',
        locale='en',
        app_info=f'app_name={consts.APP_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )

    deferred_notification = models.DeferredNotification(
        pgsql=pgsql,
        order_id=consts.ORDER_ID,
        group_type='status_change',
        notification_type=notification_type,
        is_sent=False,
    )
    deferred_notification.update_db()
    expected_deeplink = consts.LAVKA_TRACKING_DEEPLINK_PREFIX + consts.ORDER_ID

    ucommunications.check_request(
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
        push_intent='grocery.' + expected_reason,
        deeplink=expected_deeplink,
        title=expected_title,
        text=expected_body,
    )

    await _run_stq(
        order_id=deferred_notification.order_id,
        group_type=deferred_notification.group_type,
    )
    assert ucommunications.times_notification_push_called() == 1

    deferred_notification.is_sent = True
    deferred_notification.compare_with_db()


@configs.DEFERRED_NOTIFICATIONS_SETTINGS
async def test_sent_notifications_are_not_pushed(
        pgsql, _run_stq, grocery_orders, ucommunications,
):
    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale='en',
        app_info=f'app_name={consts.APP_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )

    deferred_notification = models.DeferredNotification(
        pgsql=pgsql,
        order_id=consts.ORDER_ID,
        group_type='assigned_courier',
        notification_type='courier_picked_up_order',
        is_sent=True,
    )
    deferred_notification.update_db()

    await _run_stq(
        order_id=deferred_notification.order_id,
        group_type=deferred_notification.group_type,
    )
    assert ucommunications.times_notification_push_called() == 0


@pytest.mark.parametrize(
    'order_notification_code, is_deferred',
    [
        ('ready_for_pickup', True),
        ('accepted', True),
        ('assembling', True),
        ('common_failure', False),
        ('money_failure', False),
        ('ready_for_dispatch', True),
        ('delivered', True),
    ],
)
@configs.DEFERRED_NOTIFICATIONS_SETTINGS
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_status_change_notification_is_deferred(
        taxi_grocery_communications,
        grocery_orders,
        pgsql,
        stq,
        ucommunications,
        order_notification_code,
        is_deferred,
):
    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale='en',
        app_info=f'app_name={consts.APP_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )

    test_payload = {'a': 1}
    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification',
        json={
            'code': order_notification_code,
            'payload': test_payload,
            'order_id': consts.ORDER_ID,
        },
    )
    assert response.status_code == 200

    if is_deferred and order_notification_code in consts.STATUS_CHANGE_CODES:
        assert ucommunications.times_notification_push_called() == 0
        deferred_notification = models.DeferredNotification(
            pgsql=pgsql,
            order_id=consts.ORDER_ID,
            group_type='status_change',
            notification_type=order_notification_code,
            payload=test_payload,
        )
        deferred_notification.compare_with_db()
        _assert_stq(
            stq.grocery_communications_deferred_notification,
            task_id=deferred_notification.group_type
            + '-'
            + deferred_notification.order_id,
            order_id=deferred_notification.order_id,
            group_type=deferred_notification.group_type,
        )
    else:
        assert ucommunications.times_user_sms_send_called() == 1


@configs.DEFERRED_NOTIFICATIONS_SETTINGS
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_deferred_order_edited(
        grocery_orders, chatterbox_uservices, pgsql, _run_stq,
):
    locale = 'ru'
    group_type = 'order_edited'
    removed_items_payload = {
        'products': [{'short_name': 'Эль', 'count': '1'}],
        'operation_type': 'remove',
    }
    added_items_payload = {
        'products': [
            {'short_name': 'Ром', 'count': '2'},
            {'short_name': 'Джин', 'count': '1'},
        ],
        'operation_type': 'add',
    }
    expected_msg = (
        'В корзине кое-что поменялось.'
        '\nБыли добавлены новые товары:'
        '\n- Джин (1 шт.)\n- Ром (2 шт.)'
        '\nБыли удалены следующие товары:'
        '\n- Эль (1 шт.)'
    )

    deferred_notification_1 = models.DeferredNotification(
        pgsql=pgsql,
        order_id=consts.ORDER_ID,
        group_type=group_type,
        notification_type='remove_123',
        payload=removed_items_payload,
    )
    deferred_notification_2 = models.DeferredNotification(
        pgsql=pgsql,
        order_id=consts.ORDER_ID,
        group_type=group_type,
        notification_type='add_123',
        payload=added_items_payload,
    )
    deferred_notification_1.update_db()
    deferred_notification_2.update_db()

    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale=locale,
        app_info=f'app_name={consts.APP_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
        yandex_uid=consts.YANDEX_UID,
    )

    chatterbox_uservices.check_request(
        request_id=consts.ORDER_ID + '-0',
        user_id=consts.TAXI_USER_ID,
        yandex_uid=consts.YANDEX_UID,
        platform='yandex',
        message=expected_msg,
    )

    await _run_stq(order_id=consts.ORDER_ID, group_type=group_type)
    assert chatterbox_uservices.times_create_chat_lavka_called() == 1


@configs.DEFERRED_NOTIFICATIONS_SETTINGS
async def test_order_edited_notification_is_deferred(
        taxi_grocery_communications, grocery_orders, pgsql, stq,
):
    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale='ru',
        app_info=f'app_name={consts.APP_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
        yandex_uid=consts.YANDEX_UID,
    )

    code = 'order_edited'
    payload = {
        'products': [{'short_name': 'Эль', 'count': '1'}],
        'operation_type': 'add',
    }
    response = await taxi_grocery_communications.post(
        '/processing/v1/order/create-support-chat',
        json={'order_id': consts.ORDER_ID, 'code': code, 'payload': payload},
    )
    assert response.status_code == 200

    deferred_notification = models.DeferredNotification(
        pgsql=pgsql,
        order_id=consts.ORDER_ID,
        group_type='order_edited',
        notification_type='add_Эль',
        payload=payload,
    )
    deferred_notification.compare_with_db()
    _assert_stq(
        stq.grocery_communications_deferred_notification,
        task_id=deferred_notification.group_type
        + '-'
        + deferred_notification.order_id,
        order_id=deferred_notification.order_id,
        group_type=deferred_notification.group_type,
    )
