import copy

import pytest

from tests_grocery_communications import configs
from tests_grocery_communications import models


ORDER_ID = '123'
NOTIFICATION_INTENT = 'admin_preset_message'
INTENT = 'grocery.admin_preset_message'
APP_INFO = 'app_name=lavka_iphone'
SENDER_APP = 'lavka'

DEFAULT_PUSH_MESSAGE = {
    'tanker_key': 'support_test_notification',
    'notification_args': [
        {'key': 'client_name', 'value': 'Name'},
        {'key': 'promocode', 'value': 'ABRAKADABRA'},
        {'key': 'discount', 'value': '17'},
    ],
}

DEFAULT_SMS_MESSAGE = {
    'tanker_key': 'test_tanker_key',
    'notification_args': [
        {'key': 'arg1', 'value': 'value1'},
        {'key': 'arg2', 'value': 'value2'},
    ],
}

DEFAULT_INIT_CHAT_MESSAGE = {
    'tanker_key': 'test_tanker_key',
    'notification_args': [
        {'key': 'arg1', 'value': 'value1'},
        {'key': 'arg2', 'value': 'value2'},
    ],
}

DEFAULT_PUSH_REQUEST = {'order_id': ORDER_ID, 'message': DEFAULT_PUSH_MESSAGE}
DEFAULT_SMS_REQUEST = {'order_id': ORDER_ID, 'message': DEFAULT_SMS_MESSAGE}
DEFAULT_INIT_CHAT_REQUEST = {
    'order_id': ORDER_ID,
    'message': DEFAULT_INIT_CHAT_MESSAGE,
}


def _assert_ucommunications_calls(ucommunications, notification_type):
    if notification_type == 'push':
        assert ucommunications.times_notification_push_called() == 1
        assert ucommunications.times_user_sms_send_called() == 0
    elif notification_type == 'sms':
        assert ucommunications.times_notification_push_called() == 0
        assert ucommunications.times_user_sms_send_called() == 1


@pytest.mark.parametrize(
    'request_param, notification_type, title,'
    'text, use_send_sms_keys, chat_opened',
    [
        (
            DEFAULT_PUSH_REQUEST,
            'push',
            'Приветствуем вас в Лавке, Name',
            'Вот ваш промокод новичка ABRAKADABRA на 17% скидки!',
            True,
            None,
        ),
        (
            DEFAULT_PUSH_REQUEST,
            'push',
            'Приветствуем вас в Лавке, Name',
            'Вот ваш промокод новичка ABRAKADABRA на 17% скидки!',
            False,
            None,
        ),
        (
            DEFAULT_SMS_REQUEST,
            'sms',
            None,
            'Тестовое сообщение с двумя подставленными '
            'значениями: value1 и value2',
            True,
            None,
        ),
        (
            DEFAULT_SMS_REQUEST,
            'sms',
            None,
            'Тестовое сообщение с двумя подставленными '
            'значениями: value1 и value2',
            False,
            None,
        ),
        (
            DEFAULT_INIT_CHAT_REQUEST,
            'init_chat',
            None,
            'Тестовое сообщение инициации чата с двумя '
            'значениями: value1 и value2',
            False,
            False,
        ),
        (
            DEFAULT_INIT_CHAT_REQUEST,
            'init_chat',
            None,
            'Тестовое сообщение инициации чата с двумя '
            'значениями: value1 и value2',
            False,
            True,
        ),
    ],
)
@configs.GROCERY_COMMUNICATIONS_ORDERS_SUPPORT_NOTIFICATIONS_EXPERIMENT
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_basic(
        pgsql,
        taxi_grocery_communications,
        grocery_orders,
        ucommunications,
        chatterbox_uservices,
        request_param,
        notification_type,
        title,
        text,
        use_send_sms_keys,
        chat_opened,
):
    user_id = 'taxi_user_id'
    request = copy.deepcopy(request_param)
    if not use_send_sms_keys:
        request['notification_type'] = notification_type
    user_info = {
        'taxi_user_id': user_id,
        'personal_phone_id': 'personal_phone_id',
    }
    grocery_orders.add_order(
        order_id=ORDER_ID,
        locale='ru',
        yandex_uid='yandex_uid',
        user_info=user_info,
        app_info=APP_INFO,
    )
    notification = models.Notification(pgsql=pgsql, order_id=ORDER_ID)

    idempotency_token = (
        f'preset-message-{ORDER_ID}-{request["message"]["tanker_key"]}'
    )
    if notification_type == 'init_chat':
        chatterbox_uservices.check_request(
            request_id=ORDER_ID + '-0',
            user_id=user_id,
            yandex_uid='yandex_uid',
            platform='yandex',
            message=text,
            already_opened=chat_opened,
        )
    elif notification_type == 'sms':
        ucommunications.check_request(
            idempotency_token=idempotency_token,
            title=title,
            text=text,
            sms_intent=configs.SMS_ONLY_INTENT,
            phone_id=user_info['personal_phone_id'],
            sender=SENDER_APP,
        )
    else:
        ucommunications.check_request(
            idempotency_token=idempotency_token,
            title=title,
            text=text,
            push_intent=INTENT,
            user_id=user_info[user_id],
        )
    x_yandex_login = 'x_yandex_login'
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send/preset-message',
        headers={'Accept-Language': 'en', 'X-Yandex-Login': x_yandex_login},
        json=request,
    )

    assert response.status_code == 200
    assert response.json() == {}
    if notification_type == 'init_chat':
        assert chatterbox_uservices.times_create_chat_lavka_called() == 1
    else:
        _assert_ucommunications_calls(ucommunications, notification_type)

    if chat_opened:
        return

    notification.update()
    assert notification.order_id == ORDER_ID
    assert notification.x_yandex_login == x_yandex_login
    assert notification.notification_type == notification_type
    assert notification.notification_title == title
    assert notification.notification_text == text
    assert notification.source == 'admin'
    if notification_type == 'push':
        assert notification.personal_phone_id is None
        assert notification.taxi_user_id == user_info['taxi_user_id']
        assert notification.intent == NOTIFICATION_INTENT
    elif notification_type == 'sms':
        assert notification.personal_phone_id == user_info['personal_phone_id']
        assert notification.taxi_user_id is None
        assert notification.intent == NOTIFICATION_INTENT


@pytest.mark.parametrize(
    'app_info, notification_type',
    [
        ('app_brand=lavka,app_name=lavka_iphone,app_build=release', 'push'),
        ('app_brand=lavka,app_name=lavka_web,app_build=release,', 'sms'),
        ('app_name=mobileweb_yango_iphone', 'push'),
        ('app_name=lavka_web', 'sms'),
        ('app_brand=lavka,device_make=apple,app_name=lavka_web', 'sms'),
        ('app_name=web_market_lavka', 'sms'),
    ],
)
@configs.GROCERY_COMMUNICATIONS_ORDERS_SUPPORT_NOTIFICATIONS_EXPERIMENT
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_sms_regex_match(
        pgsql,
        taxi_grocery_communications,
        grocery_orders,
        ucommunications,
        app_info,
        notification_type,
):
    request = copy.deepcopy(DEFAULT_PUSH_REQUEST)
    user_info = {
        'taxi_user_id': 'taxi_user_id',
        'personal_phone_id': 'personal_phone_id',
    }
    grocery_orders.add_order(
        order_id=ORDER_ID, locale='ru', user_info=user_info, app_info=app_info,
    )

    x_yandex_login = 'x_yandex_login'
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send/preset-message',
        headers={'Accept-Language': 'en', 'X-Yandex-Login': x_yandex_login},
        json=request,
    )

    assert response.status_code == 200
    assert response.json() == {}
    _assert_ucommunications_calls(ucommunications, notification_type)


async def test_order_not_found(
        taxi_grocery_communications, grocery_orders, ucommunications,
):
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send-notification',
        headers={'Accept-Language': 'en'},
        json=copy.deepcopy(DEFAULT_PUSH_REQUEST),
    )
    assert response.status_code == 404
    assert ucommunications.times_sms_push_called() == 0


@pytest.mark.parametrize(
    'message, status_code',
    [
        (
            {
                'tanker_key': 'test_tanker_key',
                'notification_args': [
                    {'key': 'incorrect_argument_key', 'value': 'value'},
                    {'key': 'arg2', 'value': 'value2'},
                ],
            },
            400,
        ),
        (
            {'tanker_key': 'unavailable_tanker_key', 'notification_args': []},
            405,
        ),
    ],
)
@configs.GROCERY_COMMUNICATIONS_ORDERS_SUPPORT_NOTIFICATIONS_EXPERIMENT
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_invalid_notification_message(
        taxi_grocery_communications,
        grocery_orders,
        ucommunications,
        message,
        status_code,
):
    request = {'order_id': ORDER_ID, 'message': message}
    grocery_orders.add_order(order_id=ORDER_ID, locale='ru')
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send/preset-message',
        headers={'Accept-Language': 'en'},
        json=request,
    )
    assert response.status_code == status_code
    assert ucommunications.times_sms_push_called() == 0


@configs.GROCERY_COMMUNICATIONS_ORDERS_SUPPORT_NOTIFICATIONS_EXPERIMENT
async def test_no_user_info(
        taxi_grocery_communications, grocery_orders, ucommunications,
):
    request = copy.deepcopy(DEFAULT_PUSH_REQUEST)
    grocery_orders.add_order(
        order_id=ORDER_ID,
        locale='ru',
        user_info={},
        app_info='app_name=lavka_iphone',
    )

    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send/preset-message',
        headers={'Accept-Language': 'en'},
        json=request,
    )

    assert response.status_code == 400
    assert ucommunications.times_sms_push_called() == 0
