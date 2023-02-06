import pytest

from tests_grocery_communications import configs
from tests_grocery_communications import consts
from tests_grocery_communications import models

COMPENSATION_ID = 'test_compensation_id'
PUSH_INTENT = 'grocery.compensation'
NOTIFICATION_INTENT = 'compensation'


def _check_event(processing, compensation_id, reason, idempotency_token=None):
    events_compensations = list(
        processing.events(scope='grocery', queue='compensations'),
    )
    for event in events_compensations:
        if (
                event.payload.get('compensation_id', None) == compensation_id
                and event.payload.get('reason', None) == reason
        ):
            if idempotency_token is not None:
                assert (
                    event.idempotency_token == idempotency_token
                ), event.idempotency_token

            return event.payload

    assert (
        idempotency_token is None
    ), 'idempotency token is not null and no events found'

    return None


@pytest.mark.parametrize(
    'title,text,compensation_type,compensation_info,'
    'situation_code,cancel_reason_message',
    [
        (
            'Full Refund Title',
            'Test situation happened. We are giving you a'
            ' full refund for your last order.',
            'full_refund',
            {'compensation_value': 100, 'currency': 'RUB'},
            'test_code',
            None,
        ),
        (
            'You have received',
            'a 99.99 RUB refund for the delivery cost of your last order.',
            'delivery_refund',
            {
                'compensation_value': 100,
                'numeric_value': '99.99',
                'currency': 'RUB',
            },
            None,
            None,
        ),
        (
            'You have received',
            'a 99.99 RUB refund for the delivery cost of your last order.',
            'delivery_refund',
            {
                'compensation_value': 100,
                'numeric_value': '99.99',
                'currency': 'RUB',
            },
            'untranslated_code',
            None,
        ),
        (
            'You have received',
            'a 99.99 RUB refund for the delivery cost of your last order.',
            'delivery_refund',
            {
                'compensation_value': 100,
                'numeric_value': '99.99',
                'currency': 'RUB',
            },
            'unknown_code',
            None,
        ),
        (
            'Compensation',
            'Test situation happened. We are giving you a 50 % promocode '
            'QWERTY for your next orders.',
            'promocode',
            {
                'generated_promo': 'QWERTY',
                'compensation_value': 50,
                'currency': '%',
            },
            'test_code',
            None,
        ),
        (
            'Compensation',
            'This is a custom text. We are giving you a 50 % promocode '
            'QWERTY for your next orders.',
            'promocode',
            {
                'generated_promo': 'QWERTY',
                'compensation_value': 50,
                'currency': '%',
            },
            'custom_code',
            None,
        ),
        (
            'Unfortunately, we had to cancel your order',
            'An item was sold out. Your card will be refunded.'
            ' We are giving you a 50 % promocode QWERTY for your next'
            ' orders.',
            'promocode',
            {
                'generated_promo': 'QWERTY',
                'compensation_value': 50,
                'currency': '%',
            },
            'test_code',
            'out_of_stock',
        ),
    ],
)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_notifications_with_payload(
        taxi_grocery_communications,
        grocery_orders,
        ucommunications,
        title,
        text,
        compensation_type,
        compensation_info,
        situation_code,
        cancel_reason_message,
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
    ucommunications.check_request(
        title=title,
        text=text,
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
        push_intent=PUSH_INTENT,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/compensation/notification',
        json={
            'compensation_id': COMPENSATION_ID,
            'order_id': consts.ORDER_ID,
            'compensation_type': compensation_type,
            'situation_code': situation_code,
            'compensation_info': compensation_info,
            'cancel_reason_message': cancel_reason_message,
        },
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'application, only_push, only_chat,'
    'push_with_chat, are_notifications_available',
    [
        (consts.YANGO_IPHONE, False, False, True, 'no'),
        (consts.YANGO_IPHONE, False, False, True, 'unknown'),
        (consts.YANGO_IPHONE, True, False, False, 'yes'),
        (consts.YANGO_ANDROID, False, True, False, 'no'),
        (consts.YANGO_ANDROID, True, False, False, 'unknown'),
        (consts.YANGO_ANDROID, True, False, False, 'yes'),
        (consts.APP_IPHONE, True, False, False, 'no'),
        (consts.APP_IPHONE, True, False, False, 'unknown'),
        (consts.APP_IPHONE, True, False, False, 'yes'),
    ],
)
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_create_chat(
        pgsql,
        taxi_grocery_communications,
        grocery_orders,
        ucommunications,
        chatterbox_uservices,
        application,
        only_push,
        only_chat,
        push_with_chat,
        are_notifications_available,
):
    title = 'Full Refund Title'
    text = (
        'Test situation happened. We are giving you a'
        ' full refund for your last order.'
    )
    compensation_type = 'full_refund'
    compensation_info = {'compensation_value': 100, 'currency': 'RUB'}
    situation_code = 'test_code'

    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        yandex_uid=consts.YANDEX_UID,
        locale='en',
        app_info=f'app_name={application}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )
    notifications_availability = models.NotificationsAvailability(
        pgsql=pgsql,
        order_id=consts.ORDER_ID,
        taxi_user_id=consts.TAXI_USER_ID,
        are_notifications_available=are_notifications_available,
        features={},
    )
    notifications_availability.update_db()
    if only_push or push_with_chat:
        ucommunications.check_request(
            title=title,
            text=text,
            user_id=consts.TAXI_USER_ID,
            phone_id=consts.PERSONAL_PHONE_ID,
            push_intent=PUSH_INTENT,
        )
    if only_chat or push_with_chat:
        chatterbox_uservices.check_request(
            request_id=consts.ORDER_ID + '-0',
            user_id=consts.TAXI_USER_ID,
            yandex_uid=consts.YANDEX_UID,
            platform='yango',
            message=text,
        )

    response = await taxi_grocery_communications.post(
        '/processing/v1/compensation/notification',
        json={
            'compensation_id': COMPENSATION_ID,
            'order_id': consts.ORDER_ID,
            'compensation_type': compensation_type,
            'situation_code': situation_code,
            'compensation_info': compensation_info,
            'cancel_reason_message': None,
        },
    )
    assert response.status_code == 200

    assert ucommunications.times_notification_push_called() == int(
        only_push or push_with_chat,
    )
    assert chatterbox_uservices.times_create_chat_lavka_called() == int(
        only_chat or push_with_chat,
    )


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
@pytest.mark.parametrize(
    'expected_code, ucomm_error, delivered',
    [(200, False, True), (500, True, False)],
)
async def test_notification_logging(
        taxi_grocery_communications,
        grocery_orders,
        pgsql,
        ucommunications,
        expected_code,
        ucomm_error,
        delivered,
):
    push_text = 'We gave you a compensation'
    push_title = 'Compensation'

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

    notification = models.Notification(pgsql=pgsql, order_id=consts.ORDER_ID)

    ucommunications.check_request(
        text=push_text,
        push_intent=PUSH_INTENT,
        title=push_title,
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
    )

    if ucomm_error:
        ucommunications.set_error_code(500)

    response = await taxi_grocery_communications.post(
        '/processing/v1/compensation/notification',
        json={
            'compensation_id': COMPENSATION_ID,
            'order_id': consts.ORDER_ID,
            'compensation_type': 'refund',
            'compensation_info': {'compensation_value': 1, 'currency': '$'},
        },
    )
    assert response.status_code == expected_code

    notification.update()

    assert notification.order_id == consts.ORDER_ID
    assert notification.x_yandex_login is None
    assert notification.notification_text == push_text
    assert notification.delivered is delivered
    assert notification.source == 'compensation'
    assert notification.intent == NOTIFICATION_INTENT
    assert notification.notification_title == push_title
    assert notification.taxi_user_id == consts.TAXI_USER_ID


@pytest.mark.now(consts.NOW)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
@pytest.mark.parametrize('error_code, times_called', [(409, 1), (502, 3)])
async def test_retry_count_increment(
        taxi_grocery_communications,
        grocery_orders,
        ucommunications,
        processing,
        error_code,
        times_called,
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
    ucommunications.set_error_code(error_code)

    retry_count = 10
    request = {
        'compensation_id': COMPENSATION_ID,
        'order_id': consts.ORDER_ID,
        'compensation_type': 'refund',
        'compensation_info': {'compensation_value': 1, 'currency': '$'},
        'event_policy': {'retry_count': retry_count, 'retry_interval': 30},
    }

    response = await taxi_grocery_communications.post(
        '/processing/v1/compensation/notification', json=request,
    )
    assert response.status_code == 200

    processing_payload = _check_event(
        processing,
        COMPENSATION_ID,
        reason='compensation_notification',
        idempotency_token=f'compensation-notification-{COMPENSATION_ID}'
        f'retry-policy-{retry_count + 1}',
    )

    assert ucommunications.times_notification_push_called() == times_called
    assert processing_payload['event_policy']['retry_count'] == retry_count + 1
