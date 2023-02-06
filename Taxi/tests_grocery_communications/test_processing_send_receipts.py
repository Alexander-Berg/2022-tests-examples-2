import datetime

import pytest

from tests_grocery_communications import configs
from tests_grocery_communications import consts
from tests_grocery_communications import processing_noncrit

PERSONAL_PHONE_ID = 'personal_phone_id'
APP_INFO = 'app_name=lavka_iphone'
SENDER_APP = 'lavka'


def _get_receipts(last_receipt_type):
    return [
        {'receipt_type': 'tips_receipt', 'receipt_url': 'url'},
        {'receipt_type': last_receipt_type, 'receipt_url': 'some_url'},
    ]


def _send_receipt_request(receipt_type, **kwargs):
    return {
        'receipts': _get_receipts(receipt_type),
        'reason': 'send_receipts_notification',
        **kwargs,
    }


def _prepare(
        ucommunications,
        experiments3,
        request,
        notification_type,
        expected_title,
        expected_text,
        expected_sender=None,
):
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

    ucommunications.check_request(
        title=expected_title,
        text=expected_text,
        user_id=request['taxi_user_id'],
        push_intent='grocery.receipts',
        sms_intent=configs.RECEIPT_NOTIFICATION_INTENT,
        sender=expected_sender,
    )


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


@pytest.mark.parametrize(
    'notification_type',
    [
        'receipt_via_sms',
        'receipt_notification_only_push',
        'receipt_url_deeplink_push',
        'receipt_orderhistory_deeplink_push',
    ],
)
@pytest.mark.parametrize(
    'receipt_type', ['payment_receipt', 'refund_receipt', 'tips_receipt'],
)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_basic(
        taxi_grocery_communications,
        ucommunications,
        experiments3,
        load_json,
        notification_type,
        receipt_type,
):
    localizations = load_json('localizations/grocery_communications.json')
    expected_title, expected_text = _get_title_and_text(
        localizations, notification_type + '_' + receipt_type, 'ru',
    )
    request = _send_receipt_request(
        order_id='test_order_id',
        personal_phone_id=PERSONAL_PHONE_ID,
        locale='ru',
        taxi_user_id='super_user',
        receipts=_get_receipts(receipt_type),
        receipt_type=receipt_type,
        times_called=0,
        app_info=APP_INFO,
    )
    _prepare(
        ucommunications=ucommunications,
        experiments3=experiments3,
        request=request,
        notification_type=notification_type,
        expected_title=expected_title,
        expected_text=expected_text,
        expected_sender=SENDER_APP,
    )
    response = await taxi_grocery_communications.post(
        '/processing/v1/send-receipts', json=request,
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'notification_type',
    [
        'receipt_via_sms',
        'receipt_notification_only_push',
        'receipt_url_deeplink_push',
        'receipt_orderhistory_deeplink_push',
    ],
)
@pytest.mark.parametrize(
    'receipt_type', ['payment_receipt', 'refund_receipt', 'tips_receipt'],
)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_try_again_later(
        taxi_grocery_communications,
        ucommunications,
        experiments3,
        load_json,
        processing,
        notification_type,
        receipt_type,
):
    retry_count = 10
    order_id = 'test_order_id'
    localizations = load_json('localizations/grocery_communications.json')
    expected_title, expected_text = _get_title_and_text(
        localizations, notification_type + '_' + receipt_type, 'ru',
    )
    request = _send_receipt_request(
        order_id=order_id,
        personal_phone_id=PERSONAL_PHONE_ID,
        locale='ru',
        taxi_user_id='super_user',
        receipts=_get_receipts(receipt_type),
        receipt_type=receipt_type,
        times_called=0,
        app_info=APP_INFO,
    )
    request['event_policy'] = {
        'retry_count': retry_count,
        'retry_interval': 30,
    }
    _prepare(
        ucommunications=ucommunications,
        experiments3=experiments3,
        request=request,
        notification_type=notification_type,
        expected_title=expected_title,
        expected_text=expected_text,
    )
    ucommunications.set_error_code(409)
    response = await taxi_grocery_communications.post(
        '/processing/v1/send-receipts', json=request,
    )
    assert response.status_code == 200

    processing_payload = processing_noncrit.check_noncrit_event(
        processing,
        order_id,
        reason='send_receipts_notification',
        idempotency_token=f'send-receipts-notification-{order_id}'
        f'retry-policy-{retry_count + 1}',
    )
    assert processing_payload['event_policy']['retry_count'] == retry_count + 1


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@pytest.mark.now(consts.NOW)
async def test_error_after(
        taxi_grocery_communications,
        ucommunications,
        experiments3,
        load_json,
        processing,
):
    notification_type = 'receipt_notification_only_push'
    receipt_type = 'payment_receipt'
    order_id = 'test_order_id'
    localizations = load_json('localizations/grocery_communications.json')
    expected_title, expected_text = _get_title_and_text(
        localizations, notification_type + '_' + receipt_type, 'ru',
    )

    delta = datetime.timedelta(minutes=1)
    error_after = consts.NOW_DT - delta

    request = _send_receipt_request(
        order_id=order_id,
        personal_phone_id=PERSONAL_PHONE_ID,
        locale='ru',
        taxi_user_id='super_user',
        receipts=_get_receipts(receipt_type),
        receipt_type=receipt_type,
        times_called=0,
        app_info=APP_INFO,
    )
    request['event_policy'] = {
        'retry_count': 10,
        'retry_interval': 30,
        'error_after': error_after.isoformat(),
    }
    _prepare(
        ucommunications=ucommunications,
        experiments3=experiments3,
        request=request,
        notification_type=notification_type,
        expected_title=expected_title,
        expected_text=expected_text,
    )
    ucommunications.set_error_code(409)
    response = await taxi_grocery_communications.post(
        '/processing/v1/send-receipts', json=request,
    )
    assert response.status_code == 500

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert not events


async def test_sms_without_intent(taxi_grocery_communications, experiments3):
    notification_type = 'receipt_via_sms'
    receipt_type = 'payment_receipt'
    request = _send_receipt_request(
        order_id='test_order_id',
        personal_phone_id=PERSONAL_PHONE_ID,
        locale='ru',
        taxi_user_id='super_user',
        receipts=_get_receipts(receipt_type),
        receipt_type=receipt_type,
        times_called=0,
        app_info=APP_INFO,
    )
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
                },
            },
        ],
    )
    response = await taxi_grocery_communications.post(
        '/processing/v1/send-receipts', json=request,
    )
    assert response.status_code == 400


async def test_ignore_list(
        taxi_grocery_communications, ucommunications, experiments3,
):
    receipt_type = 'tips_receipt'
    experiments3.add_config(
        name='grocery_communications_send_receipts_options',
        consumers=['grocery-communications'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'receipt_notification_type': (
                        'receipt_notification_only_push'
                    ),
                    'ignore_notification_list': [receipt_type],
                    'retry_interval': {'hours': 24},
                    'error_after': {'hours': 48},
                },
            },
        ],
    )

    request = _send_receipt_request(
        order_id='test_order_id',
        personal_phone_id=PERSONAL_PHONE_ID,
        locale='ru',
        taxi_user_id='super_user',
        receipts=_get_receipts(receipt_type),
        receipt_type=receipt_type,
        times_called=0,
        app_info=APP_INFO,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/send-receipts', json=request,
    )
    assert response.status_code == 200
    assert ucommunications.times_sms_push_called() == 0


@configs.GROCERY_RECEIPT_VIA_MAIL
@pytest.mark.config(GROCERY_COMMUNICATIONS_EMAIL_SENDER_CAMPAIGN_SLUG='slug')
async def test_receipt_via_email(
        taxi_grocery_communications, ucommunications, personal, sender,
):
    personal.check_request(email='testsuite@mail.ru', email_id='testsuite_id')
    sender.check_request(
        email='testsuite@mail.ru', args={'receipt_url': 'some_url'},
    )
    request = _send_receipt_request(
        order_id='test_order_id',
        personal_phone_id=PERSONAL_PHONE_ID,
        personal_email_id='testsuite_id',
        locale='ru',
        taxi_user_id='super_user',
        receipts=_get_receipts('payment_receipt'),
        receipt_type='payment_receipt',
        times_called=0,
        app_info=APP_INFO,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/send-receipts', json=request,
    )
    assert response.status_code == 200
    assert ucommunications.times_sms_push_called() == 0


@configs.GROCERY_RECEIPT_VIA_MAIL
@pytest.mark.config(GROCERY_COMMUNICATIONS_EMAIL_SENDER_CAMPAIGN_SLUG='slug')
async def test_retry_count_increment(
        taxi_grocery_communications, processing, sender,
):
    order_id = 'test_order_id'
    retry_count = 10

    request = _send_receipt_request(
        order_id=order_id,
        personal_phone_id=PERSONAL_PHONE_ID,
        personal_email_id='testsuite_id',
        locale='ru',
        taxi_user_id='super_user',
        receipts=_get_receipts('payment_receipt'),
        receipt_type='payment_receipt',
        times_called=0,
        app_info=APP_INFO,
    )
    request['event_policy'] = {
        'retry_count': retry_count,
        'retry_interval': 30,
    }

    sender.set_error_code(500)

    response = await taxi_grocery_communications.post(
        '/processing/v1/send-receipts', json=request,
    )
    assert response.status_code == 200

    processing_payload = processing_noncrit.check_noncrit_event(
        processing,
        order_id,
        reason='send_receipts_notification',
        idempotency_token=f'send-receipts-notification-{order_id}'
        f'retry-policy-{retry_count + 1}',
    )
    assert processing_payload['event_policy']['retry_count'] == retry_count + 1


@configs.GROCERY_RECEIPT_VIA_MAIL
@pytest.mark.config(GROCERY_COMMUNICATIONS_EMAIL_SENDER_CAMPAIGN_SLUG='slug')
async def test_receipt_via_passport_email(
        taxi_grocery_communications, ucommunications, passport, sender,
):
    sender.check_request(
        email='my_email@gmail.com', args={'receipt_url': 'some_url'},
    )

    request = _send_receipt_request(
        order_id='test_order_id',
        personal_phone_id=PERSONAL_PHONE_ID,
        locale='ru',
        taxi_user_id='super_user',
        receipts=_get_receipts('payment_receipt'),
        receipt_type='payment_receipt',
        times_called=0,
        app_info=APP_INFO,
        yandex_uid='test_uid',
        user_ip='127.0.0.1',
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/send-receipts', json=request,
    )
    assert response.status_code == 200
    assert passport.times_mock_blackbox_called() == 1
    assert ucommunications.times_sms_push_called() == 0
