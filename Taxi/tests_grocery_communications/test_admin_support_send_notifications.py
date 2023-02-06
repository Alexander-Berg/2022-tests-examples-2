import pytest

from tests_grocery_communications import configs

PERSONAL_PHONE_ID = '1273o182j3e9w'
CUSTOM_TEXT = 'Test sms text'


def _get_order_meta(order_id, phone_id=PERSONAL_PHONE_ID):
    return {
        'order_id': order_id,
        'personal_phone_id': phone_id,
        'order_state': 'delivering',
        'order_type': 'grocery',
    }


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_by_order_ids(
        taxi_grocery_communications, ucommunications, grocery_order_log,
):
    order_ids = ['test-id-1', 'test-id-2']

    ucommunications.check_request(
        text=CUSTOM_TEXT,
        phone_id=PERSONAL_PHONE_ID,
        sms_intent=configs.ADMIN_CUSTOM_MESSAGE_INTENT,
    )

    grocery_order_log.set_get_orders_meta_response(
        [_get_order_meta(order_ids[0]), _get_order_meta(order_ids[1])], [],
    )

    x_yandex_login = 'x_yandex_login'
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': x_yandex_login},
        json={'send_by': {'order_ids': order_ids}, 'custom_text': CUSTOM_TEXT},
    )
    assert response.status_code == 200
    assert ucommunications.times_user_sms_send_called() == 2
    assert response.json()['failed_ids'] == []


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_by_order_ids_half_success(
        taxi_grocery_communications, ucommunications, grocery_order_log,
):
    order_ids = ['test-id-1', 'test-id-2']

    ucommunications.check_request(
        text=CUSTOM_TEXT,
        phone_id=PERSONAL_PHONE_ID,
        sms_intent=configs.ADMIN_CUSTOM_MESSAGE_INTENT,
    )

    grocery_order_log.set_get_orders_meta_response(
        [_get_order_meta(order_ids[0])], [order_ids[1]],
    )

    x_yandex_login = 'x_yandex_login'
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': x_yandex_login},
        json={'send_by': {'order_ids': order_ids}, 'custom_text': CUSTOM_TEXT},
    )
    assert response.status_code == 200
    assert ucommunications.times_user_sms_send_called() == 1
    assert response.json()['failed_ids'] == [order_ids[1]]


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_by_order_ids_different_phones(
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
        '/admin/communications/v1/support/send-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': x_yandex_login},
        json={'send_by': {'order_ids': order_ids}, 'custom_text': CUSTOM_TEXT},
    )
    assert response.status_code == 200
    assert ucommunications.times_user_sms_send_called() == 3
    assert response.json()['failed_ids'] == []


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_by_personal_phone_ids(
        taxi_grocery_communications, ucommunications,
):
    personal_phone_ids = ['phone-1', 'phone-2', 'phone-3']

    x_yandex_login = 'x_yandex_login'
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': x_yandex_login},
        json={
            'send_by': {'personal_phone_ids': personal_phone_ids},
            'custom_text': CUSTOM_TEXT,
        },
    )
    assert response.status_code == 200
    assert ucommunications.times_user_sms_send_called() == 3
    assert response.json()['failed_ids'] == []


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_by_taxi_user_ids(taxi_grocery_communications, ucommunications):
    taxi_user_ids = ['taxi_user-1', 'taxi_user-2', 'taxi_user-3']

    x_yandex_login = 'x_yandex_login'
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': x_yandex_login},
        json={
            'send_by': {'taxi_user_ids': taxi_user_ids},
            'custom_text': CUSTOM_TEXT,
        },
    )
    assert response.status_code == 200
    assert ucommunications.times_user_sms_send_called() == 3
    assert response.json()['failed_ids'] == []


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_by_raw_phones(taxi_grocery_communications, ucommunications):
    phones = ['8800553535', '88888888888', '81337228101']

    x_yandex_login = 'x_yandex_login'
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': x_yandex_login},
        json={'send_by': {'raw_phones': phones}, 'custom_text': CUSTOM_TEXT},
    )
    assert response.status_code == 200
    assert ucommunications.times_user_sms_send_called() == 3
    assert response.json()['failed_ids'] == []


@pytest.mark.config(GROCERY_ALLOW_CUSTOM_MESSAGE=False)
async def test_405_disabled_with_config(taxi_grocery_communications):
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/send-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'faraday'},
        json={
            'send_by': {'order_ids': ['order_id']},
            'custom_text': 'Some text whatever',
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
        '/admin/communications/v1/support/send-notifications',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'faraday'},
        json={'send_by': {'order_ids': ['order_id']}, 'custom_text': bad_text},
    )
    assert response.status_code == 405
