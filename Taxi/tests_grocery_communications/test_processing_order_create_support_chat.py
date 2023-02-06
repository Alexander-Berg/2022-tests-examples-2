import pytest

from tests_grocery_communications import configs
from tests_grocery_communications import consts
from tests_grocery_communications import models
from tests_grocery_communications import processing_noncrit

MACRO_ID = 123


@pytest.mark.parametrize(
    'code, payload, expected_msg',
    [
        (
            'order_edited',
            {
                'products': [{'short_name': 'Нордский мёд', 'count': '2'}],
                'operation_type': 'add',
            },
            'В корзине кое-что поменялось.\nБыли добавлены '
            'новые товары:\n- Нордский мёд (2 шт.)',
        ),
        (
            'order_edited',
            {
                'products': [
                    {'short_name': 'Мёд "Чёрный вереск"', 'count': '1'},
                ],
                'operation_type': 'remove',
            },
            'В корзине кое-что поменялось.\nБыли удалены следующие '
            'товары:\n- Мёд "Чёрный вереск" (1 шт.)',
        ),
    ],
)
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_with_payload(
        taxi_grocery_communications,
        grocery_orders,
        chatterbox_uservices,
        code,
        payload,
        expected_msg,
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

    chatterbox_uservices.check_request(
        request_id=consts.ORDER_ID + '-0',
        user_id=consts.TAXI_USER_ID,
        yandex_uid=consts.YANDEX_UID,
        platform='yandex',
        message=expected_msg,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/create-support-chat',
        json={'order_id': consts.ORDER_ID, 'code': code, 'payload': payload},
    )
    assert response.status_code == 200
    assert chatterbox_uservices.times_create_chat_lavka_called() == 1


@pytest.mark.parametrize(
    'app_name', [consts.APP_IPHONE, consts.MARKET_IPHONE, consts.DELI_IPHONE],
)
async def test_macro_id(
        pgsql,
        taxi_grocery_communications,
        grocery_orders,
        chatterbox_uservices,
        app_name,
):
    grocery_orders.add_order(
        order_id=consts.ORDER_ID,
        locale='ru',
        app_info=f'app_name={app_name}',
        user_info={
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'eats_user_id': consts.EATS_USER_ID,
        },
        yandex_uid=consts.YANDEX_UID,
    )

    notification = models.Notification(pgsql=pgsql, order_id=consts.ORDER_ID)
    platform = 'yango' if app_name == consts.DELI_IPHONE else 'yandex'
    chatterbox_uservices.check_request(
        request_id=consts.ORDER_ID + '-0',
        user_id=consts.TAXI_USER_ID,
        yandex_uid=consts.YANDEX_UID,
        platform=platform,
        macro_id=MACRO_ID,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/create-support-chat',
        json={
            'order_id': consts.ORDER_ID,
            'macro_id': MACRO_ID,
            'code': 'feedback',
        },
    )

    assert response.status_code == 200
    assert response.json() == {}
    if app_name == consts.MARKET_IPHONE:
        assert chatterbox_uservices.times_create_chat_market_called() == 1
    else:
        assert chatterbox_uservices.times_create_chat_lavka_called() == 1

    notification.update()
    assert notification.order_id == consts.ORDER_ID
    assert notification.x_yandex_login is None
    assert notification.notification_type == 'init_chat'
    assert notification.notification_title is None
    assert notification.notification_text == str(MACRO_ID)
    assert notification.source == 'feedback'
    assert notification.personal_phone_id == consts.PERSONAL_PHONE_ID
    assert notification.taxi_user_id == consts.TAXI_USER_ID
    assert notification.intent == ''


async def test_chat_already_opened(
        taxi_grocery_communications, grocery_orders, chatterbox_uservices,
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

    platform = 'yandex'
    chatterbox_uservices.check_request(
        request_id=consts.ORDER_ID + '-0',
        user_id=consts.TAXI_USER_ID,
        yandex_uid=consts.YANDEX_UID,
        platform=platform,
        macro_id=MACRO_ID,
        already_opened=True,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/create-support-chat',
        json={
            'order_id': consts.ORDER_ID,
            'macro_id': MACRO_ID,
            'code': 'feedback',
        },
    )

    assert response.status_code == 400
    assert chatterbox_uservices.times_create_chat_lavka_called() == 1


async def test_retry_count_increment(
        taxi_grocery_communications,
        grocery_orders,
        chatterbox_uservices,
        processing,
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

    retry_count = 10
    request = {
        'order_id': consts.ORDER_ID,
        'code': 'feedback',
        'macro_id': MACRO_ID,
        'event_policy': {'retry_count': retry_count, 'retry_interval': 30},
    }

    chatterbox_uservices.set_init_with_tvm_response_code(500)

    response = await taxi_grocery_communications.post(
        '/processing/v1/order/create-support-chat', json=request,
    )
    assert response.status_code == 200

    processing_payload = processing_noncrit.check_noncrit_event(
        processing,
        consts.ORDER_ID,
        reason='create_support_chat',
        idempotency_token=f'create-support-chat-{consts.ORDER_ID}'
        f'feedbackretry-policy-{retry_count + 1}',
    )
    assert processing_payload['event_policy']['retry_count'] == retry_count + 1
