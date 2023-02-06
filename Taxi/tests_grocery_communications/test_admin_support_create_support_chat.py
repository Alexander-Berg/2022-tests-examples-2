import pytest

from tests_grocery_communications import configs
from tests_grocery_communications import consts
from tests_grocery_communications import models


ORDER_ID = '123'
MESSAGE = '123'
USER_ID = 'taxi_user_id'
PERSONAL_PHONE_ID = 'personal_phone_id'
YANDEX_UID = 'yandex_uid'


def _prepare(
        grocery_orders,
        chatterbox_uservices,
        app_name,
        user_info,
        app_ver1='',
        app_ver2='',
        app_ver3='',
        notification_number=0,
        already_opened=False,
):
    app_info = (
        f'app_name={app_name},'
        f'app_ver1={app_ver1},app_ver2={app_ver2},app_ver3={app_ver3}'
    )
    grocery_orders.add_order(
        order_id=ORDER_ID,
        locale='ru',
        yandex_uid=YANDEX_UID,
        user_info=user_info,
        app_info=app_info,
    )
    if app_name in (
            consts.DELI_IPHONE,
            consts.DELI_ANDROID,
            consts.YANGO_IPHONE,
            consts.YANGO_ANDROID,
    ):
        platform = 'yango'
    else:
        platform = 'yandex'
    chatterbox_uservices.check_request(
        request_id=f'{ORDER_ID}-{notification_number}',
        user_id=USER_ID,
        yandex_uid=YANDEX_UID,
        platform=platform,
        message=MESSAGE,
        already_opened=already_opened,
    )


@pytest.mark.parametrize(
    'app_name', [consts.APP_IPHONE, consts.MARKET_IPHONE, consts.DELI_IPHONE],
)
async def test_basic(
        pgsql,
        taxi_grocery_communications,
        grocery_orders,
        chatterbox_uservices,
        app_name,
):
    request = {'order_id': ORDER_ID, 'message': MESSAGE}
    x_yandex_login = 'x_yandex_login'
    user_info = {
        'taxi_user_id': USER_ID,
        'personal_phone_id': PERSONAL_PHONE_ID,
    }

    notification = models.Notification(pgsql=pgsql, order_id=ORDER_ID)

    _prepare(
        grocery_orders=grocery_orders,
        chatterbox_uservices=chatterbox_uservices,
        app_name=app_name,
        user_info=user_info,
    )

    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/create-support-chat',
        headers={'X-Yandex-Login': x_yandex_login},
        json=request,
    )

    assert response.status_code == 200
    assert response.json() == {'ticket_id': 'ticket_id', 'ticket_status': 'OK'}
    if app_name == consts.MARKET_IPHONE:
        assert chatterbox_uservices.times_create_chat_market_called() == 1
    else:
        assert chatterbox_uservices.times_create_chat_lavka_called() == 1

    notification.update()
    assert notification.order_id == ORDER_ID
    assert notification.x_yandex_login == x_yandex_login
    assert notification.notification_type == 'init_chat'
    assert notification.notification_title is None
    assert notification.notification_text == MESSAGE
    assert notification.source == 'admin'
    assert notification.personal_phone_id == PERSONAL_PHONE_ID
    assert notification.taxi_user_id == user_info['taxi_user_id']
    assert notification.intent == ''


async def test_chat_already_opened(
        taxi_grocery_communications, grocery_orders, chatterbox_uservices,
):
    request = {'order_id': ORDER_ID, 'message': MESSAGE}
    x_yandex_login = 'x_yandex_login'
    user_info = {
        'taxi_user_id': USER_ID,
        'personal_phone_id': PERSONAL_PHONE_ID,
    }

    _prepare(
        grocery_orders=grocery_orders,
        chatterbox_uservices=chatterbox_uservices,
        app_name=consts.APP_IPHONE,
        user_info=user_info,
        already_opened=True,
    )

    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/create-support-chat',
        headers={'X-Yandex-Login': x_yandex_login},
        json=request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'ticket_id': 'ticket_id',
        'ticket_status': 'Chat already opened',
    }
    assert chatterbox_uservices.times_create_chat_lavka_called() == 1


@configs.GROCERY_MESSENGER_SUPPORT
@pytest.mark.parametrize(
    'app_name,app_version,is_messenger',
    [
        (consts.DELI_IPHONE, '1.8.5', True),
        (consts.DELI_ANDROID, '1.8.5', False),
        (consts.DELI_IPHONE, '1.8.0', False),
        (consts.DELI_ANDROID, '1.8.0', False),
    ],
)
async def test_messenger(
        taxi_grocery_communications,
        grocery_orders,
        chatterbox_uservices,
        app_name,
        app_version,
        is_messenger,
):
    request = {'order_id': ORDER_ID, 'message': MESSAGE}
    x_yandex_login = 'x_yandex_login'
    user_info = {
        'taxi_user_id': USER_ID,
        'personal_phone_id': PERSONAL_PHONE_ID,
    }

    app_ver = app_version.split('.')
    _prepare(
        grocery_orders=grocery_orders,
        chatterbox_uservices=chatterbox_uservices,
        app_name=app_name,
        user_info=user_info,
        app_ver1=app_ver[0],
        app_ver2=app_ver[1],
        app_ver3=app_ver[2],
    )

    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/create-support-chat',
        headers={'X-Yandex-Login': x_yandex_login},
        json=request,
    )

    assert response.status_code == 200
    assert response.json() == {'ticket_id': 'ticket_id', 'ticket_status': 'OK'}
    if is_messenger:
        assert chatterbox_uservices.times_create_messenger_called() == 1
    else:
        assert chatterbox_uservices.times_create_chat_lavka_called() == 1


async def test_notification_number(
        pgsql,
        taxi_grocery_communications,
        grocery_orders,
        chatterbox_uservices,
):
    request = {'order_id': ORDER_ID, 'message': MESSAGE}
    x_yandex_login = 'x_yandex_login'
    tanker_key = 'tanker-key'
    notification_type = 'sms'
    notification_text = 'text'
    intent = 'intent'
    source = 'admin'
    user_info = {
        'taxi_user_id': USER_ID,
        'personal_phone_id': PERSONAL_PHONE_ID,
    }

    notification = models.Notification(
        pgsql,
        order_id=ORDER_ID,
        x_yandex_login=x_yandex_login,
        tanker_key=tanker_key,
        notification_type=notification_type,
        notification_text=notification_text,
        intent=intent,
        source=source,
        personal_phone_id=PERSONAL_PHONE_ID,
        taxi_user_id=USER_ID,
        delivered=True,
    )
    notification.insert()

    _prepare(
        grocery_orders=grocery_orders,
        chatterbox_uservices=chatterbox_uservices,
        app_name=consts.APP_IPHONE,
        user_info=user_info,
        notification_number=1,
    )

    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/create-support-chat',
        headers={'X-Yandex-Login': x_yandex_login},
        json=request,
    )

    assert response.status_code == 200
    assert response.json() == {'ticket_id': 'ticket_id', 'ticket_status': 'OK'}
    assert chatterbox_uservices.times_create_chat_lavka_called() == 1


@pytest.mark.config(GROCERY_ALLOW_CUSTOM_MESSAGE=False)
async def test_405_disabled_with_config(taxi_grocery_communications):
    request = {'order_id': ORDER_ID, 'message': 'any_message'}
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/create-support-chat',
        headers={'X-Yandex-Login': 'faraday'},
        json=request,
    )
    assert response.status_code == 405


@pytest.mark.config(
    CHATTERBOX_STOP_WORDS_LIST=['Ауф', 'Lol', 'Acceptée', 'חיל'],
)
@pytest.mark.parametrize(
    'bad_text',
    [
        'Не только лишь каждый может в завтрашний день, АУФ',
        'Some bad text, LOL',
        'Commande acceptée!',
        'כשנתחיל להכין אותה',
    ],
)
async def test_405_restricted_words(taxi_grocery_communications, bad_text):
    request = {'order_id': ORDER_ID, 'message': bad_text}
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/create-support-chat',
        headers={'X-Yandex-Login': 'faraday'},
        json=request,
    )
    assert response.status_code == 405
