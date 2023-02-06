import pytest

from tests_grocery_communications import configs

PERSONAL_PHONE_ID = '1273o182j3e9w'
CUSTOM_TEXT = 'Test sms text'
SENDER = 'lavka'


def _get_order_meta(order_id, phone_id=PERSONAL_PHONE_ID):
    return {
        'order_id': order_id,
        'personal_phone_id': phone_id,
        'order_state': 'delivering',
        'order_type': 'grocery',
    }


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_basic(
        taxi_grocery_communications, ucommunications, grocery_order_log,
):
    order_ids = ['test-id-1', 'test-id-2']

    ucommunications.check_request(
        text=CUSTOM_TEXT,
        phone_id=PERSONAL_PHONE_ID,
        sms_intent=configs.ADMIN_CUSTOM_MESSAGE_INTENT,
        sender=SENDER,
    )

    grocery_order_log.set_get_orders_meta_response(
        [_get_order_meta(order_ids[0]), _get_order_meta(order_ids[1])], [],
    )

    x_yandex_login = 'x_yandex_login'
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send-sms-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': x_yandex_login},
        json={
            'order_ids': order_ids,
            'sms_custom_text': CUSTOM_TEXT,
            'sender': SENDER,
        },
    )
    assert response.status_code == 200
    assert ucommunications.times_user_sms_send_called() == 2
    assert response.json()['failed_order_ids'] == []


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_half_success(
        taxi_grocery_communications, ucommunications, grocery_order_log,
):
    order_ids = ['test-id-1', 'test-id-2']

    ucommunications.check_request(
        text=CUSTOM_TEXT,
        phone_id=PERSONAL_PHONE_ID,
        sms_intent=configs.ADMIN_CUSTOM_MESSAGE_INTENT,
        sender=SENDER,
    )

    grocery_order_log.set_get_orders_meta_response(
        [_get_order_meta(order_ids[0])], [order_ids[1]],
    )

    x_yandex_login = 'x_yandex_login'
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send-sms-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': x_yandex_login},
        json={
            'order_ids': order_ids,
            'sms_custom_text': CUSTOM_TEXT,
            'sender': SENDER,
        },
    )
    assert response.status_code == 200
    assert ucommunications.times_user_sms_send_called() == 1
    assert response.json()['failed_order_ids'] == [order_ids[1]]


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_different_phones(
        taxi_grocery_communications, ucommunications, grocery_order_log,
):
    order_ids = ['test-id-1', 'test-id-2', 'test-id-3']
    personal_phone_ids = ['phone-1', 'phone-2', 'phone-3']

    grocery_order_log.set_get_orders_meta_response(
        [
            _get_order_meta(order_ids[0], personal_phone_ids[0]),
            _get_order_meta(order_ids[1], personal_phone_ids[1]),
            _get_order_meta(order_ids[2], personal_phone_ids[2]),
        ],
        [],
    )

    x_yandex_login = 'x_yandex_login'
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send-sms-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': x_yandex_login},
        json={
            'order_ids': order_ids,
            'sms_custom_text': CUSTOM_TEXT,
            'sender': SENDER,
        },
    )
    assert response.status_code == 200
    assert ucommunications.times_user_sms_send_called() == 3
    assert response.json()['failed_order_ids'] == []


@pytest.mark.config(GROCERY_ALLOW_CUSTOM_MESSAGE=False)
async def test_405_disabled_with_config(taxi_grocery_communications):
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send-sms-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'faraday'},
        json={
            'order_ids': ['order_id'],
            'sms_custom_text': 'any_message',
            'sender': SENDER,
        },
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
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send-sms-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'faraday'},
        json={
            'order_ids': ['order_id'],
            'sms_custom_text': bad_text,
            'sender': SENDER,
        },
    )
    assert response.status_code == 405
