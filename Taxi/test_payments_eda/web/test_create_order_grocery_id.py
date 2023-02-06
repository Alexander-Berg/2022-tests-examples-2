import dataclasses
import typing

import pytest

from payments_eda import consts as service_consts
from payments_eda.utils import experiments
from test_payments_eda import conftest
from test_payments_eda import consts
from test_payments_eda import preorder

VALID_CARD_ID = 'card-x5a4adedaf78dba6f9c56fee4'
GROCERY_ORDER_ID = 'bfd7526fa5d74eae9e5c034d40235be0-grocery'
TRANSACTIONS_EDA_GROCERY_SERVICE = 'grocery-order-cycle'
PERSONAL_PHONE_ID = 'phone-2809'
ITEM_TITLE = 'item-title-1122'


@dataclasses.dataclass()
class OrderMockParams:
    amount: str = consts.DEFAULT_AMOUNT
    business: typing.Optional[str] = None


@dataclasses.dataclass()
class Headers:
    pa_yandex_uid: str = consts.DEFAULT_YANDEX_UID
    pa_ya_taxi_user_id: str = consts.DEFAULT_USER_ID
    pa_bound_uids: str = ''
    pa_user_agent: typing.Optional[str] = None
    pa_request_application: typing.Optional[str] = None
    pa_ya_taxi_pass_flags: typing.Optional[str] = None


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.translations(
        client_messages={
            'payments_eda.orders.error.user_order_mismatch.message': {
                'ru': 'user order mismatch message',
            },
            'payments_eda.orders.error.user_order_mismatch.title': {
                'ru': 'user order mismatch title',
            },
            'payments_eda.orders.error.not_found.message': {
                'ru': 'not found message',
            },
            'payments_eda.orders.error.not_found.title': {
                'ru': 'not found title',
            },
            'payments_eda.orders.error.invalid_payment_method.message': {
                'ru': 'invalid payment method',
            },
            'payments_eda.orders.error.transaction_conflict.message': {
                'ru': 'transaction conflict',
            },
        },
    ),
]


enable_complement_payments = (  # pylint: disable=invalid-name
    pytest.mark.client_experiments3(
        consumer=service_consts.EXP3_CONSUMER_WEB,
        experiment_name=experiments.SUPERAPP_COMPLEMENT_PAYMENT,
        args=[
            {
                'name': 'yandex_uid',
                'type': 'string',
                'value': consts.DEFAULT_YANDEX_UID,
            },
            {'name': 'phone_id', 'type': 'string', 'value': 'phone_id'},
            {'name': 'service', 'type': 'string', 'value': 'eats'},
        ],
        value={'enabled': True},
    )
)


def _enable_wallet_for(service=None):
    args = [
        {
            'name': 'yandex_uid',
            'type': 'string',
            'value': consts.DEFAULT_YANDEX_UID,
        },
        {'name': 'phone_id', 'type': 'string', 'value': 'phone_id'},
    ]
    if service is not None:
        args.append({'name': 'service', 'type': 'string', 'value': service})
    return pytest.mark.client_experiments3(
        consumer=service_consts.EXP3_CONSUMER_WEB,
        experiment_name=experiments.PERSONAL_WALLET_ENABLED_EXP,
        args=args,
        value={'enabled': True},
    )


# pylint: disable=protected-access
# pylint: disable=R0913,R0914
@_enable_wallet_for('eats')
@pytest.mark.config(PAYMENTS_EDA_SAVE_LAST_PAYMENT_METHOD_ENABLED=True)
@pytest.mark.config(PERSONAL_WALLET_FIRM_BY_SERVICE={'eats': {'RUB': '32'}})
@pytest.mark.config(PAYMENTS_EDA_CORP_ENABLED=True)
@pytest.mark.config(PAYMENTS_EDA_COLLECT_PRODUCT_METRICS=True)
@pytest.mark.config(PAYMENTS_EDA_GROCERY_RECEIPTS_ENABLED=True)
@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.parametrize(
    'payment_method, payment_method_id, available_payment_types, status',
    [
        ('card', VALID_CARD_ID, ['applepay', 'card'], 200),
        ('card', 'card-unknown', ['applepay', 'card'], 409),
        ('card', VALID_CARD_ID, [], 409),
        ('applepay', 'applepay-123', ['applepay', 'card'], 200),
        ('applepay', 'applepay-123', [], 409),
        ('googlepay', 'googlepay-123', ['googlepay'], 200),
        ('googlepay', 'googlepay-123', ['card'], 409),
        ('unknown', 'unknown-123', ['card'], 400),
        ('corp', 'corp:yataxi_rus_dmkurilov:RUB', ['corp'], 409),
        ('corp', 'corp:someteam:RUB', ['corp'], 409),
        ('corp', 'unknown', ['corp'], 409),
        ('corp', 'badge:hello:RUB', ['badge'], 409),
        ('corp', 'badge:hello:RUB', ['card'], 409),
        ('personal_wallet', consts.VALID_WALLET_ID, ['personal_wallet'], 409),
    ],
)
@preorder.GROCERY_TRUST_SERVICE_ENABLED_DISABLED
@preorder.GROCERY_TRUST_SETTINGS
@pytest.mark.parametrize(
    'billing_settings_version', [None, 'settings-version'],
)
async def test_create_order(
        web_app,
        web_app_client,
        mock_cardstorage,
        mock_get_order,
        mock_get_payment_types_info,
        personal_store_mockserver,
        mockserver,
        mock_cardstorage_payment_methods,
        patch,
        load_json,
        payment_method,
        payment_method_id,
        available_payment_types,
        status,
        build_pa_headers,
        mock_uuid,
        available_accounts_mockserver,
        mock_blackbox,
        mock_user_state,
        mock_invoice_create,
        mock_invoice_update,
        grocery_billing_service,
        grocery_product_id,
        grocery_trust_settings_enabled,
        billing_settings_version,
):
    headers = Headers()
    mock_get_payment_types_info(
        request_service='eats',
        request_yandex_uid=headers.pa_yandex_uid,
        request_user_agent=headers.pa_user_agent,
        available_payment_types=available_payment_types,
        merchant_ids=[],
    )

    available_accounts_mockserver()

    item_id = '123'
    service = 'eats'
    get_order = mock_get_order(
        is_grocery=True,
        item_id=item_id,
        amount=consts.DEFAULT_AMOUNT,
        billing_settings_version=billing_settings_version,
    )

    personal_store_mockserver(value=preorder.GROCERY_DEFAULT_TIN)

    mock_user_state.set_payment(
        payment_method=payment_method, payment_method_id=payment_method_id,
    )

    billing_service = grocery_billing_service
    product_id = grocery_product_id
    if billing_settings_version is not None and grocery_trust_settings_enabled:
        billing_service += '_versioned'
        product_id += '_versioned'

    invoice_create_mock = mock_invoice_create(
        order_id=GROCERY_ORDER_ID,
        transaction_service=TRANSACTIONS_EDA_GROCERY_SERVICE,
        payment_method=payment_method,
        payment_method_id=payment_method_id,
        yandex_uid=headers.pa_yandex_uid,
        taxi_user_id=headers.pa_ya_taxi_user_id,
        personal_phone_id=PERSONAL_PHONE_ID,
        billing_service=billing_service,
    )

    mock_uuid(consts.DEFAULT_UUID)

    invoice_update_mock = mock_invoice_update(
        payment_method=payment_method,
        payment_method_id=payment_method_id,
        items=[
            conftest.TransactionItem(
                product_id=product_id,
                fiscal_receipt_info=conftest.FiscalReceiptInfo(
                    title=ITEM_TITLE,
                    vat='nds_20',
                    personal_tin_id=consts.PERSONAL_TIN_ID,
                ),
            ),
        ],
    )

    request_url = (
        f'/4.0/payments/v1/orders?external_ref={GROCERY_ORDER_ID}'
        f'&service={service}'
    )

    response = await web_app_client.post(
        request_url,
        json={
            'payment_method': payment_method,
            'payment_method_id': payment_method_id,
        },
        headers=build_pa_headers(
            consts.USER_IP,
            'ru-RU',
            yandex_uid=headers.pa_yandex_uid,
            bound_uids=headers.pa_bound_uids,
            user_agent=headers.pa_user_agent,
            request_application=headers.pa_request_application,
            ya_taxi_pass_flags=headers.pa_ya_taxi_pass_flags,
            personal_phone_id=PERSONAL_PHONE_ID,
            personal_email_id='email-personal-999',
        ),
    )
    if status != 200:
        assert response.status == status
        return

    data = await response.json()

    assert response.status == 200
    assert data == {
        'order_id': GROCERY_ORDER_ID,
        'total': consts.DEFAULT_AMOUNT,
        'currency': 'RUB',
        'expires_at': '2018-07-21T17:00:00+03:00',
    }

    cardstorage_times_called = int('card' in available_payment_types)
    assert (
        mock_cardstorage_payment_methods.times_called
        == cardstorage_times_called
    )
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert get_order.times_called == 1
    # Collect metrics on success
    if status != 200:
        return

    for agg in web_app['context'].stats._aggregations.keys():
        if ('sensor', 'create_order_prefinish') in agg:
            assert dict(agg) == {
                'invoice_service': TRANSACTIONS_EDA_GROCERY_SERVICE,
                'sensor': 'create_order_prefinish',
                'currency': 'RUB',
                'country_code': 'RU',
                'region_id': '123',
            }
            break
    else:
        pytest.fail('Failed to collect prefinish metrics')


@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.parametrize('payment_method', ['card', 'applepay'])
@preorder.GROCERY_TRUST_SETTINGS_ISRAEL
async def test_create_order_from_israel(
        web_app,
        web_app_client,
        mock_cardstorage,
        mock_get_order,
        mock_get_payment_types_info,
        personal_store_mockserver,
        mockserver,
        mock_cardstorage_payment_methods,
        patch,
        build_pa_headers,
        mock_uuid,
        available_accounts_mockserver,
        mock_blackbox,
        mock_user_state,
        mock_invoice_create,
        mock_invoice_update,
        payment_method,
):
    headers = Headers()
    mock_get_payment_types_info(
        request_service='grocery',
        request_yandex_uid=headers.pa_yandex_uid,
        request_user_agent=headers.pa_user_agent,
        available_payment_types=['card', 'applepay'],
        merchant_ids=[],
    )

    available_accounts_mockserver()

    item_id = '123'
    service = 'grocery'
    get_order = mock_get_order(
        is_grocery=True,
        item_id=item_id,
        amount=consts.DEFAULT_AMOUNT,
        country_iso2='IL',
    )

    payment_method_id = VALID_CARD_ID

    personal_store_mockserver(value=preorder.GROCERY_DEFAULT_TIN)

    mock_user_state.set_payment(
        payment_method=payment_method, payment_method_id=payment_method_id,
    )

    invoice_create_mock = mock_invoice_create(
        order_id=GROCERY_ORDER_ID,
        transaction_service=TRANSACTIONS_EDA_GROCERY_SERVICE,
        payment_method=payment_method,
        payment_method_id=payment_method_id,
        yandex_uid=headers.pa_yandex_uid,
        taxi_user_id=headers.pa_ya_taxi_user_id,
        personal_phone_id=PERSONAL_PHONE_ID,
        billing_service=preorder.ISRAEL_BILLING_SERVICE,
        transactions_type=conftest.TransactionsType.lavka_isr,
    )

    mock_uuid(consts.DEFAULT_UUID)

    invoice_update_mock = mock_invoice_update(
        payment_method=payment_method,
        payment_method_id=payment_method_id,
        items=[
            conftest.TransactionItem(product_id=preorder.ISRAEL_PRODUCT_ID),
        ],
        transactions_type=conftest.TransactionsType.lavka_isr,
    )

    request_url = (
        f'/4.0/payments/v1/orders?external_ref={GROCERY_ORDER_ID}'
        f'&service={service}'
    )

    response = await web_app_client.post(
        request_url,
        json={
            'payment_method': payment_method,
            'payment_method_id': payment_method_id,
        },
        headers=build_pa_headers(
            consts.USER_IP,
            'ru-RU',
            yandex_uid=headers.pa_yandex_uid,
            bound_uids=headers.pa_bound_uids,
            user_agent=headers.pa_user_agent,
            request_application=headers.pa_request_application,
            ya_taxi_pass_flags=headers.pa_ya_taxi_pass_flags,
            personal_phone_id=PERSONAL_PHONE_ID,
            personal_email_id='email-personal-999',
        ),
    )
    assert response.status == 200
    assert await response.json() == {
        'order_id': GROCERY_ORDER_ID,
        'total': consts.DEFAULT_AMOUNT,
        'currency': 'RUB',
        'expires_at': '2018-07-21T17:00:00+03:00',
    }

    assert invoice_update_mock.times_called == 1
    assert invoice_create_mock.times_called == 1
    assert get_order.times_called == 1


@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_create_order_grocery_payments_flow(
        web_app,
        web_app_client,
        build_pa_headers,
        mock_get_order,
        personal_store_mockserver,
        _mock_save_grocery_payment_method,
):

    item_id = '123'
    service = 'grocery'
    get_order_mock = mock_get_order(
        is_grocery=True,
        item_id=item_id,
        amount=consts.DEFAULT_AMOUNT,
        grocery_billing_flow='grocery_payments',
    )

    personal_store_mockserver(value=preorder.GROCERY_DEFAULT_TIN)

    payment_method = 'card'
    payment_method_id = VALID_CARD_ID

    request_url = (
        f'/4.0/payments/v1/orders?external_ref={GROCERY_ORDER_ID}'
        f'&service={service}'
    )

    headers = Headers()
    save_grocery_payment_method = _mock_save_grocery_payment_method(
        yandex_uid=headers.pa_yandex_uid,
        payment_type=payment_method,
        payment_id=payment_method_id,
        order_id=GROCERY_ORDER_ID,
    )

    response = await web_app_client.post(
        request_url,
        json={
            'payment_method': payment_method,
            'payment_method_id': payment_method_id,
        },
        headers=build_pa_headers(
            consts.USER_IP,
            'ru-RU',
            yandex_uid=headers.pa_yandex_uid,
            bound_uids=headers.pa_bound_uids,
            user_agent=headers.pa_user_agent,
            request_application=headers.pa_request_application,
            ya_taxi_pass_flags=headers.pa_ya_taxi_pass_flags,
            personal_phone_id=PERSONAL_PHONE_ID,
            personal_email_id='email-personal-999',
        ),
    )
    assert response.status == 200
    assert await response.json() == {
        'order_id': GROCERY_ORDER_ID,
        'total': consts.DEFAULT_AMOUNT,
        'currency': 'RUB',
        'expires_at': '2018-07-21T17:00:00+03:00',
    }

    assert save_grocery_payment_method.times_called == 1
    assert get_order_mock.times_called == 1


@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.parametrize('error_code', [401, 404])
async def test_create_order_grocery_payments_flow_errors(
        web_app,
        web_app_client,
        build_pa_headers,
        mock_get_order,
        personal_store_mockserver,
        _mock_save_grocery_payment_method,
        error_code,
):

    item_id = '123'
    service = 'grocery'
    get_order_mock = mock_get_order(
        is_grocery=True,
        item_id=item_id,
        amount=consts.DEFAULT_AMOUNT,
        grocery_billing_flow='grocery_payments',
    )

    personal_store_mockserver(value=preorder.GROCERY_DEFAULT_TIN)

    payment_method = 'card'
    payment_method_id = VALID_CARD_ID

    request_url = (
        f'/4.0/payments/v1/orders?external_ref={GROCERY_ORDER_ID}'
        f'&service={service}'
    )

    headers = Headers()
    save_grocery_payment_method = _mock_save_grocery_payment_method(
        error_code=error_code,
    )

    response = await web_app_client.post(
        request_url,
        json={
            'payment_method': payment_method,
            'payment_method_id': payment_method_id,
        },
        headers=build_pa_headers(
            consts.USER_IP,
            'ru-RU',
            yandex_uid=headers.pa_yandex_uid,
            bound_uids=headers.pa_bound_uids,
            user_agent=headers.pa_user_agent,
            request_application=headers.pa_request_application,
            ya_taxi_pass_flags=headers.pa_ya_taxi_pass_flags,
            personal_phone_id=PERSONAL_PHONE_ID,
            personal_email_id='email-personal-999',
        ),
    )
    assert response.status == 400

    response_json = await response.json()
    assert response_json['code'] == 'CANNOT_SAVE_PAYMENT_METHOD'

    assert save_grocery_payment_method.times_called == 1
    assert get_order_mock.times_called == 1


@pytest.fixture
def _mock_save_grocery_payment_method(mockserver):
    def _checker(error_code=None, yandex_uid=None, **kwargs):
        @mockserver.json_handler(
            '/grocery-orders/internal/v1/save-payment-method',
        )
        def _mock(request):
            if error_code is not None:
                return mockserver.make_response('{}', error_code)

            if yandex_uid is not None:
                assert request.headers['X-Yandex-UID'] == yandex_uid

            for key in kwargs:
                assert request.json[key] == kwargs[key], key

            return {}

        return _mock

    return _checker
