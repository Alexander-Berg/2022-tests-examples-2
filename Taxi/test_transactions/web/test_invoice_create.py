# pylint: disable=redefined-outer-name,invalid-name
import copy
import datetime

import pytest

from test_transactions import helpers

PASS_PARAMS = {
    'user_info': {
        'is_portal': False,
        'personal_phone_id': 'personal-phone-id-123',
        'accept_language': 'ru-RU',
    },
}

PAYMENT_CARD = {'type': 'card', 'method': 'card-1324', 'billing_id': '1324'}

PAYMENT_APPLEPAY = {
    'type': 'applepay',
    'method': 'apple_token-124_DEAD_F00D',
    'billing_id': 'F00D',
}

PAYMENT_GOOGLEPAY = {
    'type': 'googlepay',
    'method': 'google_token-124_DEAD_F00D',
    'billing_id': 'F00D',
}

PAYMENT_CORP = {
    'type': 'corp',
    'method': 'corp:some_ref:RUB',
    'billing_id': '',
}

PAYMENT_WALLET = {
    'type': 'personal_wallet',
    'method': 'wallet_id/12345',
    'service': 'eda',
    'account': {'id': 'abcdabcdabcdabcdabcd'},
}

PAYMENT_BADGE = {
    'type': 'badge',
    'method': 'badge/12345',
    'payer_login': 'torvalds_linus',
}

BILLING_SERVICE_TAXI = 'card'
BILLING_SERVICE_EATS = 'food_payment'
BILLING_SERVICE_EATS_CORP = 'food_payment_corp'


@pytest.mark.parametrize(
    'payment,pass_params,currency,billing_service',
    [
        (PAYMENT_CARD, {}, 'RUB', BILLING_SERVICE_EATS),
        (PAYMENT_CORP, PASS_PARAMS, 'RUB', BILLING_SERVICE_EATS_CORP),
    ],
)
async def test_invoice_create_basic(
        eda_web_app_client,
        web_app_client,
        db,
        payment,
        pass_params,
        currency,
        billing_service,
):
    if billing_service == BILLING_SERVICE_TAXI:
        client = web_app_client
        coll = db.orders
    else:
        client = eda_web_app_client
        coll = db.eda_invoices
    response = await client.post(
        '/invoice/create',
        json={
            'id': 'my-order',
            'invoice_due': '2019-05-01 03:00:00Z',
            'billing_service': billing_service,
            'payment': payment,
            'currency': currency,
            'yandex_uid': '123',
            'personal_phone_id': 'personal-phone-id',
            'personal_email_id': 'personal-email-id',
            'pass_params': pass_params,
            'user_ip': '127.0.0.1',
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}

    order = await coll.find_one('my-order')

    assert order['billing_tech'] == {
        'transactions': [],
        'compensations': [],
        'service_orders': {},
        'version': 1,
    }
    assert order['cashback_tech'] == {'transactions': [], 'version': 1}
    assert order['yandex_uid'] == '123'
    assert order['invoice_request'] == {
        'billing_service': billing_service,
        'currency': currency,
        'invoice_due': datetime.datetime(2019, 5, 1, 3, 0),
        'pass_params': pass_params,
        'payment': payment,
        'personal_phone_id': 'personal-phone-id',
        'personal_email_id': 'personal-email-id',
        'yandex_uid': '123',
        'operations': [],
        'cashback_operations': [],
        'cashback_version': 1,
        'products': {},
        'version': 1,
        'user_ip': '127.0.0.1',
    }
    assert order['payment_tech'] == {
        'last_known_ip': '127.0.0.1',
        'main_card_payment_id': payment['method'],
        'main_card_billing_id': payment['billing_id'],
        'type': payment['type'],
        'sum_to_pay': {},
    }


async def test_invoice_create_with_precise_due(eda_web_app_client, db):
    response = await eda_web_app_client.post(
        '/invoice/create',
        json={
            'id': 'my-order',
            'invoice_due': '2020-03-25T12:22:37.530062',
            'billing_service': BILLING_SERVICE_EATS,
            'payment': PAYMENT_CARD,
            'currency': 'RUB',
            'yandex_uid': '11111111',
            'pass_params': {},
            'user_ip': '127.0.0.1',
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}


@pytest.mark.parametrize(
    'billing_service', [BILLING_SERVICE_TAXI, BILLING_SERVICE_EATS],
)
async def test_invoice_create_repeat(
        eda_web_app_client, web_app_client, billing_service,
):
    if billing_service == BILLING_SERVICE_TAXI:
        client = web_app_client
    else:
        client = eda_web_app_client
    response = await client.post(
        '/invoice/create',
        json={
            'id': 'existing',
            # due is different from existing value
            'invoice_due': '2019-05-01T03:00:10.530062',
            'billing_service': billing_service,
            'payment': {
                'type': 'card',
                'method': '1324',
                'billing_id': 'card-1324',
            },
            'currency': 'RUR',
            'yandex_uid': '123',
            'personal_phone_id': 'personal-id',
            'pass_params': {},
            'user_ip': '127.0.0.1',
        },
    )

    assert response.status == 200
    content = await response.json()
    assert content == {}


async def test_invoice_create_repeat_conflict(web_app_client, db):
    response = await web_app_client.post(
        '/invoice/create',
        json={
            'id': 'existing',
            'invoice_due': '2019-05-01 03:00:00Z',
            'billing_service': 'card',
            'payment': {
                'type': 'card',
                'method': '1324',
                'billing_id': 'card-1324',
            },
            'currency': 'USD',  # changed
            'yandex_uid': '123',
            'personal_phone_id': 'personal-id',
            'pass_params': {},
            'user_ip': '127.0.0.1',
        },
    )

    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'conflict',
        'message': 'Invoice exists and does not match current request',
    }


async def test_invoice_create_wallet(eda_web_app_client, db):
    response = await eda_web_app_client.post(
        '/invoice/create',
        json={
            'id': 'my-order',
            'invoice_due': '2019-05-01 03:00:00Z',
            'billing_service': 'food_payment',
            'payment': PAYMENT_WALLET,
            'currency': 'RUB',
            'yandex_uid': '123',
            'personal_phone_id': 'personal-id',
            'pass_params': {},
            'user_ip': '127.0.0.1',
        },
    )
    assert response.status == 200
    order = await db.eda_invoices.find_one('my-order')

    assert order['invoice_request'] == {
        'billing_service': 'food_payment',
        'currency': 'RUB',
        'invoice_due': datetime.datetime(2019, 5, 1, 3, 0),
        'pass_params': {},
        'payment': {
            'type': 'personal_wallet',
            'method': 'wallet_id/12345',
            'wallet_service': 'eda',
            'wallet_account': {'id': 'abcdabcdabcdabcdabcd'},
        },
        'personal_phone_id': 'personal-id',
        'yandex_uid': '123',
        'operations': [],
        'cashback_operations': [],
        'cashback_version': 1,
        'products': {},
        'version': 1,
        'user_ip': '127.0.0.1',
    }
    assert order['payment_tech'] == {
        'last_known_ip': '127.0.0.1',
        'main_card_payment_id': 'wallet_id/12345',
        'main_card_billing_id': 'wallet_id/12345',
        'type': 'personal_wallet',
        'sum_to_pay': {},
        'wallet_account': {'id': 'abcdabcdabcdabcdabcd'},
        'wallet_service': 'eda',
    }


async def test_invoice_create_badge(eda_web_app_client, db):
    response = await eda_web_app_client.post(
        '/invoice/create',
        json={
            'id': 'my-order',
            'invoice_due': '2019-05-01 03:00:00Z',
            'billing_service': 'card',
            'payment': PAYMENT_BADGE,
            'currency': 'RUB',
            'yandex_uid': '123',
            'personal_phone_id': 'personal-id',
            'pass_params': {},
            'user_ip': '127.0.0.1',
        },
    )
    assert response.status == 200
    order = await db.eda_invoices.find_one('my-order')

    assert order['invoice_request'] == {
        'billing_service': 'card',
        'currency': 'RUB',
        'invoice_due': datetime.datetime(2019, 5, 1, 3, 0),
        'pass_params': {},
        'payment': {
            'type': 'badge',
            'method': 'badge/12345',
            'payer_login': 'torvalds_linus',
        },
        'personal_phone_id': 'personal-id',
        'yandex_uid': '123',
        'operations': [],
        'cashback_operations': [],
        'cashback_version': 1,
        'products': {},
        'version': 1,
        'user_ip': '127.0.0.1',
    }
    assert order['payment_tech'] == {
        'last_known_ip': '127.0.0.1',
        'main_card_payment_id': 'badge/12345',
        'main_card_billing_id': 'badge/12345',
        'type': 'badge',
        'sum_to_pay': {},
        'payer_login': 'torvalds_linus',
    }


@pytest.mark.parametrize('omit_billing_id', [False, True])
@pytest.mark.parametrize(
    'data_path',
    [
        'card_and_wallet.json',
        'corp_and_wallet.json',
        'applepay_and_wallet.json',
        'googlepay_and_wallet.json',
        'card_applepay_and_wallet.json',
        'card.json',
        'no_payments.json',
        'wallet.json',
        'card_uber.json',
        'agent.json',
        'yandex_card.json',
        'yandex_card_card_prefix.json',
        'cibus.json',
        'sbp.json',
    ],
)
@pytest.mark.parametrize('without_trust_orders', [True, False, None])
async def test_v2_invoice_create(
        patch,
        load_py_json,
        web_app_client,
        eda_web_app_client,
        lavka_isr_web_app_client,
        db,
        data_path,
        omit_billing_id,
        without_trust_orders,
):

    data = load_py_json(data_path)
    invoice_id = data.get('invoice_id', 'my-order')

    restore = helpers.patch_safe_restore_invoice(patch, None, [invoice_id])

    scope = data.get('scope', 'eda')
    if scope == 'eda':
        client = eda_web_app_client
        coll = db.eda_invoices
        payment_tech_field = 'payment_tech'
    elif scope == 'lavka_isr':
        client = lavka_isr_web_app_client
        coll = db.lavka_isr_invoices
        payment_tech_field = 'payment_tech'
    else:
        assert scope == 'taxi'
        client = web_app_client
        coll = db.orders
        payment_tech_field = 'invoice_payment_tech'
    if omit_billing_id:
        payments = [
            _without_billing_id(payment) for payment in data['payments']
        ]
    else:
        payments = data['payments']
    response = await client.post(
        '/v2/invoice/create',
        json={
            'id': invoice_id,
            'invoice_due': '2019-05-01 03:00:00Z',
            'billing_service': BILLING_SERVICE_EATS,
            'payments': payments,
            'currency': 'RUB',
            'yandex_uid': '123',
            'personal_phone_id': 'personal-id',
            'pass_params': {},
            'trust_afs_params': {'afs': 'params'},
            'trust_developer_payload': 'some developer payload',
            'antifraud_payload': {},
            'user_ip': '127.0.0.1',
            'automatic_clear_delay': 10800,
            'id_namespace': 'some_id_namespace',
            'without_trust_orders': without_trust_orders,
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}
    assert len(restore.calls) == 1

    order = await coll.find_one(invoice_id)
    assert order['billing_tech'] == {
        'transactions': [],
        'compensations': [],
        'service_orders': {},
        'version': 1,
    }
    assert order['cashback_tech'] == {'transactions': [], 'version': 1}
    assert order['yandex_uid'] == '123'

    check_invoice_request = {
        'billing_service': BILLING_SERVICE_EATS,
        'currency': 'RUB',
        'invoice_due': datetime.datetime(2019, 5, 1, 3, 0),
        'pass_params': {},
        'trust_afs_params': {'afs': 'params'},
        'trust_developer_payload': 'some developer payload',
        'antifraud_payload': {},
        'payments': data['expected_payment_tech']['payments'],
        'personal_phone_id': 'personal-id',
        'yandex_uid': '123',
        'operations': [],
        'cashback_operations': [],
        'cashback_version': 1,
        'products': {},
        'version': 1,
        'user_ip': '127.0.0.1',
        'automatic_clear_delay': 10800,
        'id_namespace': 'some_id_namespace',
    }

    if without_trust_orders is not None:
        check_invoice_request['without_trust_orders'] = without_trust_orders

    assert order['invoice_request'] == check_invoice_request
    assert order[payment_tech_field] == data['expected_payment_tech']


@pytest.mark.parametrize('billing_service', ['uber', 'uber_roaming'])
async def test_uber_invoice_create(web_app_client, billing_service):
    response = await web_app_client.post(
        '/v2/invoice/create',
        json={
            'id': 'order-without-migration',
            'invoice_due': '2019-05-01 03:00:00Z',
            'billing_service': billing_service,
            'payments': [
                {'billing_id': 'card-1324', 'method': '1324', 'type': 'card'},
            ],
            'currency': 'RUB',
            'yandex_uid': '123',
            'personal_phone_id': 'personal-id',
            'pass_params': {},
            'user_ip': '127.0.0.1',
            'automatic_clear_delay': 10800,
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}


@pytest.mark.parametrize(
    'data_path', ['migrate_fresh_order.json', 'migrate_migrated_order.json'],
)
async def test_migrate_taxi_order(load_py_json, web_app_client, db, data_path):
    data = load_py_json(data_path)
    response = await web_app_client.post(
        '/v2/invoice/create', json=data['request_body'],
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}
    coll = db.orders
    order = await coll.find_one(data['request_body']['id'])
    del order['updated']
    del order['created']
    assert order == data['expected_order']


@pytest.mark.parametrize(
    'data_path',
    [
        'duplicate_payments.json',
        'unknown_billing_service.json',
        'no_wallet_service.json',
        'bad_invoice_id.json',
        'coop_account.json',
    ],
)
async def test_invalid_v2_invoice_create(
        load_py_json, web_app_client, db, data_path,
):
    data = load_py_json(data_path)
    response = await web_app_client.post(
        '/v2/invoice/create', json=data['request'],
    )
    assert response.status == 400
    content = await response.json()
    assert content['message'] == data['expected_message']


@pytest.mark.parametrize('api_version', ['', '/v2'])
@pytest.mark.parametrize(
    'extra_field,extra_field_value',
    [
        ('service', 'eda'),
        ('service', None),
        ('external_user_info', {'user_id': 'abc', 'origin': 'taxi'}),
        ('user_id', None),
    ],
)
async def test_invoice_create_with_extra_fields(
        load_py_json,
        eda_web_app_client,
        db,
        api_version,
        extra_field,
        extra_field_value,
):
    await _check_create_with_extra_field(
        load_py_json,
        eda_web_app_client,
        db,
        extra_field=extra_field,
        extra_field_value=extra_field_value,
        api_version=api_version,
    )


@pytest.mark.parametrize(
    'extra_field, extra_field_value',
    [
        ('mcc', 1234),
        ('login_id', 'some_login_id'),
        ('metric_namespaces', ['isr']),
    ],
)
async def test_invoice_create_with_extra_field(
        load_py_json, eda_web_app_client, db, extra_field, extra_field_value,
):
    await _check_create_with_extra_field(
        load_py_json,
        eda_web_app_client,
        db,
        extra_field=extra_field,
        extra_field_value=extra_field_value,
        api_version='/v2',
    )


async def _check_create_with_extra_field(
        load_py_json,
        eda_web_app_client,
        db,
        extra_field,
        extra_field_value,
        api_version,
):
    pass_params = {}
    currency = 'RUB'
    billing_service = BILLING_SERVICE_EATS
    client = eda_web_app_client
    coll = db.eda_invoices

    data = {
        'id': 'my-order',
        'invoice_due': '2019-05-01 03:00:00Z',
        'billing_service': billing_service,
        'currency': currency,
        'yandex_uid': '123',
        'personal_phone_id': 'personal-id',
        'pass_params': pass_params,
        'user_ip': '127.0.0.1',
    }
    if extra_field_value:
        data[extra_field] = extra_field_value

    if api_version == '/v2':
        payments_data = load_py_json(
            'test_v2_invoice_create/card_and_wallet.json',
        )
        data['payments'] = payments_data['payments']
    else:
        data['payment'] = PAYMENT_CARD

    response = await client.post(api_version + '/invoice/create', json=data)
    assert response.status == 200
    content = await response.json()
    assert content == {}

    order = await coll.find_one('my-order')

    if extra_field_value:
        assert order['invoice_request'][extra_field] == extra_field_value
    else:
        assert extra_field not in order['invoice_request']


def _without_billing_id(payment):
    if 'billing_id' not in payment:
        return payment
    if payment['type'] in ('applepay', 'googlepay', 'card', 'sbp'):
        stripped = copy.deepcopy(payment)
        del stripped['billing_id']
        return stripped
    return payment
