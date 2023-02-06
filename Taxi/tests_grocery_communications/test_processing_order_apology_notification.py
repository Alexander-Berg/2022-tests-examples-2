import pytest

from tests_grocery_communications import configs
from tests_grocery_communications import consts
from tests_grocery_communications import models


def _get_title_and_text(localizations, key, locale):
    title_localizations = next(
        e for e in localizations if e['_id'] == key + '_title'
    )['values']
    text_localizations = next(
        e for e in localizations if e['_id'] == key + '_text'
    )['values']
    title_localization = next(
        e
        for e in title_localizations
        if e['conditions']['locale']['language'] == locale
    )
    text_localization = next(
        e
        for e in text_localizations
        if e['conditions']['locale']['language'] == locale
    )
    return title_localization['value'], text_localization['value']


def _check_event(
        processing, order_id, apology_reason_type, reason, idempotency_token,
):
    events_compensations = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    for event in events_compensations:
        if (
                event.payload.get('order_id', None) == order_id
                and event.payload.get('apology_reason_type', None)
                == apology_reason_type
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
    'apology_reason_type', ['long_courier_assignment', 'long_delivery'],
)
@pytest.mark.parametrize('locale', ['ru', 'en'])
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_basic(
        taxi_grocery_communications,
        grocery_orders,
        ucommunications,
        load_json,
        apology_reason_type,
        locale,
):
    localizations = load_json('localizations/grocery_communications.json')
    expected_title, expected_text = _get_title_and_text(
        localizations, 'apology.' + apology_reason_type + '.push', locale,
    )

    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale=locale,
        app_info=f'app_name={consts.APP_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )
    ucommunications.check_request(
        title=expected_title,
        text=expected_text,
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
        push_intent='grocery.apology',
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/apology-notification',
        json={
            'order_id': consts.ORDER_ID,
            'apology_reason_type': apology_reason_type,
        },
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'is_ucomm_500, delivered, expected_response_code',
    [(False, True, 200), (True, False, 500)],
)
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_notification_logging(
        taxi_grocery_communications,
        grocery_orders,
        pgsql,
        ucommunications,
        load_json,
        is_ucomm_500,
        delivered,
        expected_response_code,
):
    apology_reason_type = 'long_courier_assignment'
    locale = 'en'
    localizations = load_json('localizations/grocery_communications.json')
    expected_title, expected_text = _get_title_and_text(
        localizations, 'apology.' + apology_reason_type + '.push', locale,
    )

    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale=locale,
        app_info=f'app_name={consts.APP_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )
    ucommunications.check_request(
        title=expected_title,
        text=expected_text,
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
        push_intent='grocery.apology',
    )

    notification = models.Notification(pgsql=pgsql, order_id=consts.ORDER_ID)

    if is_ucomm_500:
        ucommunications.set_error_code(500)

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/apology-notification',
        json={
            'order_id': consts.ORDER_ID,
            'apology_reason_type': apology_reason_type,
        },
    )
    assert response.status_code == expected_response_code

    notification.update()

    assert notification.order_id == consts.ORDER_ID
    assert notification.x_yandex_login is None
    assert notification.notification_type == 'push'
    assert notification.notification_title == expected_title
    assert notification.notification_text == expected_text
    assert notification.intent == 'apology'
    assert notification.source == 'admin'
    assert notification.taxi_user_id == consts.TAXI_USER_ID
    assert notification.delivered is delivered


@pytest.mark.parametrize('error_code, times_called', [(409, 1), (502, 3)])
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_retry_count(
        taxi_grocery_communications,
        grocery_orders,
        ucommunications,
        processing,
        error_code,
        times_called,
):
    apology_reason_type = 'long_courier_assignment'
    locale = 'en'

    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale=locale,
        app_info=f'app_name={consts.APP_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )

    ucommunications.set_error_code(error_code)

    retry_count = 10

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/apology-notification',
        json={
            'order_id': consts.ORDER_ID,
            'apology_reason_type': apology_reason_type,
            'event_policy': {'retry_count': retry_count, 'retry_interval': 30},
        },
    )
    assert response.status_code == 200

    suffix = f'retry-policy-{retry_count + 1}'
    processing_payload = _check_event(
        processing,
        consts.ORDER_ID,
        apology_reason_type,
        'apology_notification',
        f'apology-{consts.ORDER_ID}{apology_reason_type}{suffix}',
    )

    assert ucommunications.times_user_sms_send_called() == 0
    assert ucommunications.times_notification_push_called() == times_called
    assert processing_payload['event_policy']['retry_count'] == retry_count + 1


@pytest.mark.parametrize(
    'payload, expected_text, expected_title',
    [
        (
            {'value': '10'},
            'Привет, опаздаем кароч, но потом дадим промик на 10%',
            'Задержка',
        ),
    ],
)
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_with_payload(
        taxi_grocery_communications,
        grocery_orders,
        ucommunications,
        payload,
        expected_text,
        expected_title,
):
    locale = 'ru'
    apology_reason_type = 'late_order_promocode'

    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale=locale,
        app_info=f'app_name={consts.APP_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )
    ucommunications.check_request(
        title=expected_title,
        text=expected_text,
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
        push_intent='grocery.apology',
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/apology-notification',
        json={
            'order_id': consts.ORDER_ID,
            'apology_reason_type': apology_reason_type,
            'payload': payload,
        },
    )
    assert response.status_code == 200
