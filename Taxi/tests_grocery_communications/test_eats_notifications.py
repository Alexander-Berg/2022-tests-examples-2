import pytest

from tests_grocery_communications import configs
from tests_grocery_communications import consts

EATS_APP_INFO = 'app_name=eda_webview_iphone'
SENDER_APP = 'lavka'
INTENT = 'test_intent'

DEFAULT_PUSH_MESSAGE = {
    'tanker_key': 'support_test_notification',
    'notification_args': [
        {'key': 'client_name', 'value': 'Name'},
        {'key': 'promocode', 'value': 'ABRAKADABRA'},
        {'key': 'discount', 'value': '17'},
    ],
}

DEFAULT_PUSH_REQUEST = {
    'order_id': consts.ORDER_ID,
    'message': DEFAULT_PUSH_MESSAGE,
}

MOBILE_CONFIG = pytest.mark.config(
    GROCERY_COMMUNICATIONS_MOBILE_CLIENTS=[
        consts.EDA_ANDROID,
        consts.EDA_IPHONE,
    ],
)

CUSTOM_TEXT_KEY = 'notification_custom_text'


def _get_receipts(last_receipt_type):
    return [
        {'receipt_type': 'tips_receipt', 'receipt_url': 'url'},
        {'receipt_type': last_receipt_type, 'receipt_url': 'some_url'},
    ]


def _send_receipt_request(receipt_type, **kwargs):
    return {'receipts': _get_receipts(receipt_type), **kwargs}


@configs.GROCERY_COMMUNICATIONS_ORDERS_SUPPORT_NOTIFICATIONS_EXPERIMENT
async def test_support_preset_message(
        taxi_grocery_communications,
        grocery_orders,
        eats_eaters,
        eats_notifications,
):
    request = DEFAULT_PUSH_REQUEST
    user_info = {
        'taxi_user_id': consts.TAXI_USER_ID,
        'eats_user_id': consts.EATS_USER_ID,
        'personal_phone_id': consts.PERSONAL_PHONE_ID,
    }
    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale='ru',
        user_info=user_info,
        app_info=EATS_APP_INFO,
    )

    eats_eaters.check_request(eats_id=consts.EATS_USER_ID)
    eats_notifications.check_request(notification_key=CUSTOM_TEXT_KEY)

    x_yandex_login = 'x_yandex_login'
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send/preset-message',
        headers={'Accept-Language': 'en', 'X-Yandex-Login': x_yandex_login},
        json=request,
    )
    assert response.status_code == 200
    assert eats_eaters.times_find_by_id_called() == 1
    assert eats_notifications.times_notification_called() == 1


@MOBILE_CONFIG
async def test_processing_order_notification(
        taxi_grocery_communications,
        grocery_orders,
        eats_eaters,
        eats_notifications,
):
    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        short_order_id=consts.SHORT_ORDER_ID,
        locale='en',
        app_info=EATS_APP_INFO,
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )

    eats_eaters.check_request(eats_id=consts.EATS_USER_ID)
    eats_notifications.check_request(notification_key=CUSTOM_TEXT_KEY)

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/notification',
        json={
            'code': 'delivering',
            'payload': {},
            'order_id': consts.ORDER_ID,
        },
    )
    assert response.status_code == 200
    assert eats_eaters.times_find_by_id_called() == 1
    assert eats_notifications.times_notification_called() == 1


@MOBILE_CONFIG
async def test_processing_compensation_notification(
        taxi_grocery_communications,
        grocery_orders,
        eats_eaters,
        eats_notifications,
):
    eats_eaters.check_request(eats_id=consts.EATS_USER_ID)
    eats_notifications.check_request(notification_key=CUSTOM_TEXT_KEY)

    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale='ru',
        app_info=f'app_name={consts.EDA_IPHONE}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/compensation/notification',
        json={
            'compensation_id': 'test_id',
            'order_id': consts.ORDER_ID,
            'compensation_type': 'refund',
            'compensation_info': {'compensation_value': 1, 'currency': '$'},
        },
    )
    assert response.status_code == 200
    assert eats_eaters.times_find_by_id_called() == 1
    assert eats_notifications.times_notification_called() == 1


@MOBILE_CONFIG
async def test_processing_apology_notification(
        taxi_grocery_communications,
        grocery_orders,
        eats_eaters,
        eats_notifications,
):
    eats_eaters.check_request(eats_id=consts.EATS_USER_ID)
    eats_notifications.check_request(notification_key=CUSTOM_TEXT_KEY)

    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale='ru',
        app_info=f'app_name={consts.EDA_IPHONE}',
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
            'apology_reason_type': 'long_courier_assignment',
        },
    )
    assert response.status_code == 200
    assert eats_eaters.times_find_by_id_called() == 1
    assert eats_notifications.times_notification_called() == 1


@pytest.mark.parametrize(
    'receipt_type', ['payment_receipt', 'refund_receipt', 'tips_receipt'],
)
async def test_processing_send_receipts(
        taxi_grocery_communications,
        experiments3,
        receipt_type,
        eats_eaters,
        eats_notifications,
):
    notification_type = 'receipt_orderhistory_deeplink_push'

    request = _send_receipt_request(
        order_id='test_order_id',
        personal_phone_id=consts.PERSONAL_PHONE_ID,
        locale='ru',
        taxi_user_id='super_user',
        eats_user_id=consts.EATS_USER_ID,
        receipts=_get_receipts(receipt_type),
        receipt_type=receipt_type,
        times_called=0,
        app_info=EATS_APP_INFO,
    )

    eats_eaters.check_request(eats_id=consts.EATS_USER_ID)
    eats_notifications.check_request(notification_key=CUSTOM_TEXT_KEY)

    experiments3.add_config(
        name='grocery_communications_send_receipts_options',
        consumers=['grocery-communications'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'receipt_notification_type': notification_type,
                    'retry_interval': {'hours': 24},
                    'error_after': {'hours': 48},
                    'intent': 'custom_intent',
                },
            },
        ],
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/send-receipts', json=request,
    )
    assert response.status_code == 200
    assert eats_eaters.times_find_by_id_called() == 1
    assert eats_notifications.times_notification_called() == 1
