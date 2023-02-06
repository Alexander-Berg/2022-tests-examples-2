import datetime

import pytest

from tests_grocery_communications import configs
from tests_grocery_communications import consts
from tests_grocery_communications import models
from tests_grocery_communications import processing_noncrit


MOBILE_CONFIG = pytest.mark.config(
    GROCERY_COMMUNICATIONS_MOBILE_CLIENTS=[
        consts.APP_IPHONE,
        consts.YANGO_IPHONE,
        consts.DELI_IPHONE,
        consts.YANGO_ANDROID,
        consts.DELI_ANDROID,
    ],
)

AFTER_NOW_DT = consts.NOW_DT + datetime.timedelta(minutes=10)
AFTER_NOW = AFTER_NOW_DT.isoformat()

SBP_LINK = 'https://some.ru'
DEPOT_ID = 123

ORDER_STATUS_INTENT = 'grocery.order_status'


def _add_default_order(
        grocery_orders,
        grocery_depots,
        app_name=consts.APP_IPHONE,
        locale='en',
):
    grocery_depots.add_depot(depot_test_id=DEPOT_ID)
    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        depot_id=str(DEPOT_ID),
        short_order_id=consts.SHORT_ORDER_ID,
        locale=locale,
        app_info=f'app_name={app_name}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
        yandex_uid=consts.YANDEX_UID,
    )


@MOBILE_CONFIG
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.GROCERY_COMMUNICATIONS_TRACKING_DEEPLINK_PREFIX
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
@pytest.mark.parametrize(
    'app_name,push_times_called,sms_times_called',
    [
        (consts.APP_IPHONE, 1, 0),
        (consts.APP_WEB, 0, 1),
        (consts.YANGO_IPHONE, 1, 0),
        (consts.DELI_IPHONE, 1, 0),
        (consts.YANGO_ANDROID, 1, 0),
        (consts.DELI_ANDROID, 1, 0),
    ],
)
@pytest.mark.parametrize(
    'code, title, text, locale, push_intent',
    [
        (
            'ready_for_pickup',
            None,
            'The order {} is ready for pickup',
            'en',
            ORDER_STATUS_INTENT,
        ),
        (
            'accepted',
            None,
            'The order {} is accepted',
            'en',
            ORDER_STATUS_INTENT,
        ),
        (
            'assembling',
            None,
            'The order {} is assembling',
            'en',
            ORDER_STATUS_INTENT,
        ),
        (
            'common_failure',
            None,
            'The order {} was failed, it was canceled',
            'en',
            'grocery.order_failure',
        ),
        (
            'compensation',
            None,
            'We gave you a compensation',
            'en',
            'grocery.compensation',
        ),
        (
            'money_failure',
            None,
            'Failed to pay for the order {}, it was canceled',
            'en',
            'grocery.order_failure',
        ),
        (
            'ready_for_dispatch',
            None,
            'The order {} was assembled and is ready for delivery',
            'en',
            ORDER_STATUS_INTENT,
        ),
        (
            'delivering',
            None,
            'The order {} is delivering',
            'en',
            ORDER_STATUS_INTENT,
        ),
        (
            'delivered',
            None,
            'Your order has been delivered',
            'en',
            ORDER_STATUS_INTENT,
        ),
        (
            'courier_not_rover',
            'Not a rover',
            'The order will not be brought by rover :c',
            'en',
            ORDER_STATUS_INTENT,
        ),
        (
            'courier_not_rover',
            'Не робот(',
            'Заказ доставит курьер, а не робот(',
            'ru',
            ORDER_STATUS_INTENT,
        ),
        (
            'ready_for_delivery_confirmation',
            None,
            'Bender is waiting outside to kick your ass',
            'en',
            ORDER_STATUS_INTENT,
        ),
        (
            'ready_for_delivery_confirmation',
            None,
            'Дрон прибыл к вашему местоположению',
            'ru',
            ORDER_STATUS_INTENT,
        ),
        ('delivered', None, 'Ваш заказ доставлен', 'ru', ORDER_STATUS_INTENT),
        (
            'client_not_responded',
            'Could not contact',
            'The courier had to leave. They waited 10 minutes, '
            'but could not reach you by phone. Order canceled',
            'en',
            ORDER_STATUS_INTENT,
        ),
        (
            'client_not_responded',
            'Не смогли связаться',
            'Курьеру пришлось уехать — он ждал 10 минут, '
            'но не смог вам дозвониться. Заказ отменили',
            'ru',
            ORDER_STATUS_INTENT,
        ),
    ],
)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_basic(
        taxi_grocery_communications,
        pgsql,
        grocery_orders,
        grocery_depots,
        ucommunications,
        code,
        title,
        text,
        locale,
        app_name,
        push_times_called,
        sms_times_called,
        push_intent,
):
    _add_default_order(
        grocery_orders, grocery_depots, app_name=app_name, locale=locale,
    )

    sms_intent = configs.ORDER_STATUS_NOTIFICATION_INTENT
    if 'money_failure' in code:
        sms_intent = configs.MONEY_CANCEL_NOTIFICATION_INTENT
    if 'common_failure' in code:
        sms_intent = configs.CANCEL_NOTIFICATION_INTENT
    if 'compensation' in code:
        sms_intent = configs.COMPENSATION_NOTIFICATION_INTENT
    if app_name == consts.APP_WEB:
        sms_intent = configs.SMS_ONLY_INTENT

    if app_name == consts.APP_IPHONE:
        deeplink = consts.LAVKA_TRACKING_DEEPLINK_PREFIX + consts.ORDER_ID
    elif app_name == consts.APP_WEB:
        deeplink = None
    else:
        deeplink = consts.YANGODELI_TRACKING_DEEPLINK_PREFIX + consts.ORDER_ID

    if title is None:
        if app_name in (consts.APP_IPHONE, consts.APP_WEB):
            if locale == 'en':
                title = 'Yandex.Grocery'
            else:
                title = 'Яндекс.Лавка'
        else:
            if locale == 'en':
                title = 'Yango.Deli'
            else:
                title = 'Янго.Доставка'

    ucommunications.check_request(
        title=title,
        text=text.format(consts.SHORT_ORDER_ID),
        push_intent=push_intent,
        sms_intent=sms_intent,
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
        deeplink=deeplink,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification',
        json={'code': code, 'payload': {}, 'order_id': consts.ORDER_ID},
    )

    assert response.status_code == 200

    # do nothing for optional in web
    if code in ('common_failure', 'money_failure', 'compensation'):
        assert ucommunications.times_notification_push_called() == 0
        assert (
            ucommunications.times_user_sms_send_called()
            == sms_times_called + push_times_called
        )
    else:
        if app_name == consts.APP_WEB:
            assert ucommunications.times_user_sms_send_called() == 0
            assert ucommunications.times_notification_push_called() == 0
        else:
            assert (
                ucommunications.times_notification_push_called()
                == push_times_called
            )
            assert (
                ucommunications.times_user_sms_send_called()
                == sms_times_called
            )


@MOBILE_CONFIG
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@pytest.mark.parametrize(
    'locale, text', [('ru', f'Ссылка {SBP_LINK}'), ('en', f'Link {SBP_LINK}')],
)
async def test_sbp_link(
        taxi_grocery_communications,
        grocery_orders,
        grocery_depots,
        ucommunications,
        locale,
        text,
):
    _add_default_order(grocery_orders, grocery_depots, locale=locale)

    sms_intent = configs.SMS_ONLY_INTENT

    ucommunications.check_request(
        title='Яндекс.Лавка',
        text=text,
        sms_intent=sms_intent,
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification',
        json={
            'code': 'sbp_link',
            'payload': {'sbp_link': SBP_LINK},
            'order_id': consts.ORDER_ID,
        },
    )

    assert response.status_code == 200

    assert ucommunications.times_notification_push_called() == 0
    assert ucommunications.times_user_sms_send_called() == 1


@pytest.mark.parametrize(
    'app_name',
    [
        consts.MARKET_ANDROID,
        consts.MARKET_ANDROID_NATIVE,
        consts.MARKET_ANDROID_V2,
        consts.MARKET_IPHONE,
        consts.MARKET_IPHONE_NATIVE,
        consts.MARKET_IPHONE_V2,
    ],
)
@pytest.mark.parametrize(
    'code, text',
    [
        ('ready_for_pickup', 'The order {} is ready for pickup'),
        ('accepted', 'The order {} is accepted'),
        ('assembling', 'The order {} is assembling'),
        (
            'ready_for_dispatch',
            'The order {} was assembled and is ready for delivery',
        ),
        ('delivering', 'The order {} is delivering'),
        ('delivered', 'Your order has been delivered'),
    ],
)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_market_notifications(
        grocery_market_gw,
        taxi_grocery_communications,
        grocery_orders,
        grocery_depots,
        ucommunications,
        app_name,
        code,
        text,
):
    _add_default_order(grocery_orders, grocery_depots, app_name=app_name)

    grocery_market_gw.set_v1_notify(
        expected_json={
            'yandex_uid': consts.YANDEX_UID,
            'translated_push_title': '',
            'translated_push_message': text.format(consts.SHORT_ORDER_ID),
            'idempotency_token': code + '-' + consts.ORDER_ID,
        },
        response_code=200,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification',
        json={'code': code, 'payload': {}, 'order_id': consts.ORDER_ID},
    )

    assert response.status_code == 200

    assert grocery_market_gw.times_gw_v1_notify_called() == 1
    assert ucommunications.times_notification_push_called() == 0
    assert ucommunications.times_user_sms_send_called() == 0


@pytest.mark.parametrize(
    'ucommunications_code,orders_response,notification_code, times_called',
    [
        (400, 400, 'delivered', 1),
        (404, 404, 'delivered', 1),
        (409, 500, 'delivered', 1),
        (429, 500, 'delivered', 1),
        (502, 500, 'delivered', 3),
    ],
)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_default_error_from_ucommunication(
        taxi_grocery_communications,
        pgsql,
        grocery_orders,
        grocery_depots,
        ucommunications,
        ucommunications_code,
        orders_response,
        notification_code,
        times_called,
):
    _add_default_order(grocery_orders, grocery_depots)

    ucommunications.set_error_code(ucommunications_code)
    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification',
        json={
            'order_id': consts.ORDER_ID,
            'code': notification_code,
            'payload': {},
        },
    )

    if ucommunications_code == 429:
        assert response.status_code == 500
    elif ucommunications_code == 404:
        assert response.status_code == 400
    else:
        assert response.status_code == orders_response

    assert ucommunications.times_notification_push_called() == times_called


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('add_deadline', [True, False])
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_deadline(
        taxi_grocery_communications,
        pgsql,
        grocery_orders,
        grocery_depots,
        ucommunications,
        add_deadline,
):
    _add_default_order(grocery_orders, grocery_depots)

    ucommunications.set_error_code(500)
    request = {
        'order_id': consts.ORDER_ID,
        'code': 'assembling',
        'payload': {},
    }

    if add_deadline:
        request['deadline'] = (
            consts.NOW_DT - datetime.timedelta(minutes=1)
        ).isoformat()
    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification', json=request,
    )
    if add_deadline:
        assert response.status_code == 200
    else:
        assert response.status_code == 500


@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'now_delta_minutes, should_try', [(-10, False), (10, True)],
)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_stop_retry_after(
        taxi_grocery_communications,
        grocery_orders,
        grocery_depots,
        ucommunications,
        processing,
        now_delta_minutes,
        should_try,
):
    _add_default_order(grocery_orders, grocery_depots)

    ucommunications.set_error_code(409)

    notification_payload = {'receipt_url': 'receipt_url'}

    delta = datetime.timedelta(minutes=now_delta_minutes)
    request_stop_retry_after = consts.NOW_DT + delta

    request = {
        'order_id': consts.ORDER_ID,
        'code': 'assembling',
        'payload': notification_payload,
        'event_policy': {
            'retry_count': 10,
            'stop_retry_after': request_stop_retry_after.isoformat(),
            'retry_interval': 30,
        },
    }

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification', json=request,
    )
    assert response.status_code == 200

    processing_payload = processing_noncrit.check_noncrit_event(
        processing, consts.ORDER_ID, reason='order_notification',
    )

    if should_try:
        assert ucommunications.times_sms_push_called() == 1
        assert processing_payload is not None
        assert processing_payload['payload'] == notification_payload
    else:
        assert ucommunications.times_sms_push_called() == 0
        assert processing_payload is None


@pytest.mark.now(consts.NOW)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
@pytest.mark.parametrize('error_code, times_called', [(409, 1), (502, 3)])
async def test_retry_count_increment(
        taxi_grocery_communications,
        grocery_orders,
        grocery_depots,
        ucommunications,
        processing,
        error_code,
        times_called,
):
    _add_default_order(grocery_orders, grocery_depots)

    ucommunications.set_error_code(error_code)

    notification_payload = {'receipt_url': 'receipt_url'}
    notification_id = 'notification_id-123'

    retry_count = 10
    request = {
        'order_id': consts.ORDER_ID,
        'code': 'assembling',
        'payload': notification_payload,
        'notification_id': notification_id,
        'event_policy': {'retry_count': retry_count, 'retry_interval': 30},
    }

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification', json=request,
    )
    assert response.status_code == 200

    processing_payload = processing_noncrit.check_noncrit_event(
        processing,
        consts.ORDER_ID,
        reason='order_notification',
        idempotency_token=f'{notification_id}retry-policy-{retry_count + 1}',
    )

    assert ucommunications.times_notification_push_called() == times_called
    assert processing_payload['event_policy']['retry_count'] == retry_count + 1


def _get_last_processing_events(processing, order, count=1):
    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    order_events = events[-count:]

    for event in order_events:
        assert event.item_id == order.order_id

    return order_events


@pytest.mark.parametrize(
    'code,text,locale,country_iso3',
    [
        (
            'ready_for_dispatch',
            'The order {} was assembled and is ready for delivery',
            'en',
            'ISR',
        ),
        ('delivered', 'Your order has been delivered', 'en', 'RUS'),
    ],
)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_push_intents(
        taxi_grocery_communications,
        pgsql,
        grocery_orders,
        grocery_depots,
        ucommunications,
        code,
        text,
        locale,
        country_iso3,
):
    _add_default_order(grocery_orders, grocery_depots)

    ucommunications.check_request(
        title='Yandex.Grocery',
        text=text.format(consts.SHORT_ORDER_ID),
        push_intent=ORDER_STATUS_INTENT,
        sms_intent='order_cycle_common',
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
    )

    request = {'order_id': consts.ORDER_ID, 'code': code, 'payload': {}}

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification', json=request,
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'app_name, expected_phone_id, expected_user_id',
    [
        (consts.APP_IPHONE, None, consts.TAXI_USER_ID),
        (consts.EDA_IPHONE, consts.PERSONAL_PHONE_ID, None),
    ],
)
@pytest.mark.parametrize(
    'code,title,text,payload',
    [
        (
            'common_failure',
            'Yandex.Grocery',
            'Unfortunately, we had to cancel your '
            'order because of issues with delivery.',
            {'type': 'dispatch_failure', 'reason_message': ''},
        ),
        (
            'common_failure',
            'Performer not found',
            'Unfortunately, no performer.',
            {
                'type': 'dispatch_failure',
                'reason_message': 'performer_not_found',
            },
        ),
        (
            'common_failure',
            'Yandex.Grocery',
            'Unfortunately, we had to cancel your order because we can.',
            {'type': 'admin_request', 'reason_message': 'test_admin_reason'},
        ),
        (
            'common_failure',
            'Yandex.Grocery',
            'Unfortunately, we had to cancel your order because '
            'there was a reserve failure.',
            {'type': 'failure', 'reason_message': 'reserve_failed'},
        ),
        (
            'compensation',
            'Yandex.Grocery',
            'You have received a full refund for your last order.',
            {'type': 'refund', 'refund_info': {'type': 'full'}},
        ),
        (
            'compensation',
            'Yandex.Grocery',
            'As a compensation, we give you a promocode '
            'for your next order: QWERTY',
            {
                'type': 'promocode',
                'promocode_info': {
                    'type': 'percent',
                    'promocode': 'QWERTY',
                    'valid': True,
                },
            },
        ),
        (
            'compensation',
            'Yandex.Grocery',
            'As a compensation, we give you a promocode for 10 RUB '
            'for your next order: QWERTY',
            {
                'type': 'promocode',
                'promocode_info': {
                    'type': 'fixed',
                    'promocode': 'QWERTY',
                    'value': '10',
                    'valid': True,
                },
            },
        ),
        (
            'money_failure',
            'Common payment error notification Title',
            'Common payment error notification SubTitle',
            {
                'push_error_title': 'push_payment_error.title.common',
                'push_error_text': 'push_payment_error.subtitle.common',
                'sms_error_text': 'sms_payment_error.common',
            },
        ),
        (
            'money_failure',
            'No money on card notification Title',
            'No money on card notification SubTitle',
            {
                'push_error_title': (
                    'push_payment_error.title.not_enough_funds'
                ),
                'push_error_text': (
                    'push_payment_error.subtitle.not_enough_funds'
                ),
                'sms_error_text': 'sms_payment_error.not_enough_funds',
            },
        ),
        (
            'money_failure',
            'Yandex.Grocery',
            'Failed to pay for the order 32131-321-3412341, it was canceled',
            {},
        ),
    ],
)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_notifications_with_payload(
        taxi_grocery_communications,
        grocery_orders,
        grocery_depots,
        ucommunications,
        code,
        title,
        text,
        payload,
        app_name,
        expected_phone_id,
        expected_user_id,
):
    if code == 'compensation':
        push_intent = 'grocery.compensation'
        sms_intent = configs.COMPENSATION_NOTIFICATION_INTENT
    elif code == 'money_failure':
        push_intent = 'grocery.money_failure'
        sms_intent = configs.MONEY_CANCEL_NOTIFICATION_INTENT
    else:
        push_intent = 'grocery.order_failure'
        sms_intent = configs.CANCEL_NOTIFICATION_INTENT

    notification = {'title': title, 'text': text.format(consts.SHORT_ORDER_ID)}
    if app_name == consts.EDA_IPHONE:
        sms_intent = configs.SMS_ONLY_INTENT
        notification = None

    ucommunications.check_request(
        user_id=expected_phone_id,
        phone_id=expected_user_id,
        push_intent=push_intent,
        sms_intent=sms_intent,
        notification=notification,
    )

    _add_default_order(grocery_orders, grocery_depots, app_name)

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification',
        json={'code': code, 'payload': payload, 'order_id': consts.ORDER_ID},
    )
    assert response.status_code == 200


@configs.GROCERY_ORDER_NOTIFICATION_OPTIONS
async def test_ignore_list(
        taxi_grocery_communications,
        grocery_orders,
        grocery_depots,
        ucommunications,
):
    _add_default_order(grocery_orders, grocery_depots)

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification',
        json={'code': 'delivered', 'payload': {}, 'order_id': consts.ORDER_ID},
    )

    assert response.status_code == 200
    assert ucommunications.times_sms_push_called() == 0


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@pytest.mark.parametrize(
    'code, text, source, expected_code, ucomm_error, delivered',
    [
        (
            'common_failure',
            'The order {} was failed, it was canceled',
            'admin',
            200,
            False,
            True,
        ),
        (
            'money_failure',
            'Failed to pay for the order {}, it was canceled',
            'admin',
            200,
            False,
            True,
        ),
        (
            'compensation',
            'We gave you a compensation',
            'compensation',
            200,
            False,
            True,
        ),
        (
            'common_failure',
            'The order {} was failed, it was canceled',
            'admin',
            500,
            True,
            False,
        ),
        (
            'money_failure',
            'Failed to pay for the order {}, it was canceled',
            'admin',
            500,
            True,
            False,
        ),
    ],
)
async def test_notification_logging(
        taxi_grocery_communications,
        pgsql,
        grocery_orders,
        grocery_depots,
        ucommunications,
        code,
        text,
        source,
        expected_code,
        ucomm_error,
        delivered,
):
    _add_default_order(grocery_orders, grocery_depots)

    if code == 'compensation':
        push_intent = 'grocery.compensation'
        sms_intent = configs.COMPENSATION_NOTIFICATION_INTENT
        notification_intent = 'compensation'
    elif code == 'money_failure':
        push_intent = 'grocery.money_failure'
        sms_intent = configs.MONEY_CANCEL_NOTIFICATION_INTENT
        notification_intent = 'order_money_failure'
    else:
        push_intent = 'grocery.order_failure'
        sms_intent = configs.CANCEL_NOTIFICATION_INTENT
        notification_intent = 'order_failure'
    push_title = 'Yandex.Grocery'

    if ucomm_error:
        ucommunications.set_error_code(500)

    notification = models.Notification(pgsql=pgsql, order_id=consts.ORDER_ID)

    ucommunications.check_request(
        text=text.format(consts.SHORT_ORDER_ID),
        push_intent=push_intent,
        title=push_title,
        sms_intent=sms_intent,
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification',
        json={'code': code, 'payload': {}, 'order_id': consts.ORDER_ID},
    )

    assert response.status_code == expected_code

    notification.update()

    assert notification.order_id == consts.ORDER_ID
    assert notification.x_yandex_login is None
    assert notification.notification_text == text.format(consts.SHORT_ORDER_ID)
    assert notification.delivered is delivered
    assert notification.source == source
    if notification.notification_type == 'sms':
        assert notification.intent == notification_intent
        assert notification.personal_phone_id == consts.PERSONAL_PHONE_ID
        assert notification.notification_title is None
        assert notification.taxi_user_id is None
    elif notification.notification_type == 'push':
        assert notification.intent == notification_intent
        assert notification.personal_phone_id is None
        assert notification.notification_title == push_title
        assert notification.taxi_user_id == consts.TAXI_USER_ID
    else:
        assert notification.notification_type is not None


@MOBILE_CONFIG
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.GROCERY_ORDER_NOTIFICATION_OPTIONS
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
@pytest.mark.parametrize(
    'text,delivery_type',
    [
        ('The order {} is delivering', 'courier'),
        ('The order {} is being delivered by rover', 'rover'),
    ],
)
async def test_rover_push(
        taxi_grocery_communications,
        grocery_orders,
        grocery_depots,
        ucommunications,
        text,
        delivery_type,
):
    _add_default_order(grocery_orders, grocery_depots)

    ucommunications.check_request(
        title='Yandex.Grocery',
        text=text.format(consts.SHORT_ORDER_ID),
        push_intent=ORDER_STATUS_INTENT,
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification',
        json={
            'code': 'delivering',
            'payload': {'delivery_type': delivery_type},
            'order_id': consts.ORDER_ID,
        },
    )
    assert response.status_code == 200
    assert ucommunications.times_notification_push_called() == 1


@MOBILE_CONFIG
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.GROCERY_ORDER_NOTIFICATION_OPTIONS
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_debt_hold(
        taxi_grocery_communications,
        grocery_orders,
        grocery_depots,
        ucommunications,
):
    _add_default_order(grocery_orders, grocery_depots)

    amount = '10.01'

    ucommunications.check_request(
        title=(
            f'debt_hold_push_title -'
            f' short_order_id: {consts.SHORT_ORDER_ID}'
            f' debt_amount: {amount} ₽'
        ),
        text=(
            f'debt_hold_push_text - short_order_id: {consts.SHORT_ORDER_ID}'
            f' debt_amount: {amount} ₽'
        ),
        push_intent='grocery.debt_hold_message',
        user_id=consts.TAXI_USER_ID,
        phone_id=consts.PERSONAL_PHONE_ID,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification',
        json={
            'code': 'debt_hold',
            'payload': {'amount': amount, 'currency': 'RUB'},
            'order_id': consts.ORDER_ID,
        },
    )
    assert response.status_code == 200
    assert ucommunications.times_notification_push_called() == 1
