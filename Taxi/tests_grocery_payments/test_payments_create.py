# pylint: disable=too-many-lines

import copy
import datetime

import pytest

from . import consts
from . import headers
from . import models
from . import pytest_marks
from .plugins import configs
from .plugins import mock_passport

PaymentType = models.PaymentType
PassportUser = mock_passport.User

COUNTRY = models.Country.Russia

FIRST_ITEM_PRICE = '10'
SECOND_ITEM_QUANTITY = '1'

ITEMS = [
    models.Item(item_id='item-id-1', price=FIRST_ITEM_PRICE, quantity='2'),
    models.Item(
        item_id='item-id-2',
        price='20',
        quantity=SECOND_ITEM_QUANTITY,
        receipt_info=models.ReceiptInfo(
            title='delivery-title',
            vat='20',
            personal_tin_id='personal-tin-id-x123',
        ),
    ),
    models.Item(
        item_id='item-id-3',
        price='123',
        quantity='1',
        item_type=models.ItemType.delivery,
    ),
    models.Item(
        item_id='helping_hand',
        price='10',
        quantity='1',
        item_type=models.ItemType.helping_hand,
    ),
    models.Item(
        item_id='service_fee',
        price='29',
        quantity='1',
        item_type=models.ItemType.service_fee,
    ),
]


PAYMENT_METHOD = models.PaymentMethod(
    payment_type=PaymentType.card, payment_id=consts.CARD_ID,
)

CASHBACK_PAYMENT_METHOD = models.PaymentMethod(
    payment_type=PaymentType.personal_wallet,
    payment_id=consts.PERSONAL_WALLET_ID,
)


@pytest.fixture(name='grocery_payments_create')
def _grocery_payments_create(taxi_grocery_payments, user_state, transactions):
    async def _inner(
            country=COUNTRY,
            items=None,
            payment_method=None,
            items_by_payment_types=None,
            **kwargs,
    ):
        if items_by_payment_types is None:
            payment_method = payment_method or PAYMENT_METHOD
            items_by_payment_types = [
                {
                    'items': models.to_request_items(items or ITEMS),
                    'payment_method': payment_method.to_request(),
                },
            ]

        return await taxi_grocery_payments.post(
            '/payments/v1/create',
            json={
                'order_id': consts.ORDER_ID,
                'country_iso3': country.country_iso3,
                'currency': country.currency,
                'items_by_payment_types': items_by_payment_types,
                'user_info': headers.DEFAULT_USER_INFO,
                **kwargs,
            },
        )

    return _inner


@pytest.mark.parametrize(
    'payment_type',
    [
        PaymentType.card,
        PaymentType.applepay,
        PaymentType.googlepay,
        PaymentType.cibus,
    ],
)
async def test_basic(grocery_payments_create, transactions, payment_type):
    trust_settings = configs.trust_settings_payload(COUNTRY)

    billing_service = trust_settings['billing_service']
    product_id = trust_settings['product_id']
    operation_id = 'abcabcabc111'

    payment_method = models.PaymentMethod(
        payment_type=payment_type, payment_id=consts.CARD_ID,
    )

    transactions.create.check(
        billing_service=billing_service,
        currency=COUNTRY.currency,
        id=consts.ORDER_ID,
        pass_params=consts.PASS_PARAMS,
        payments=[payment_method.to_transactions()],
        personal_phone_id=headers.PERSONAL_PHONE_ID,
        service=consts.SERVICE,
        user_ip=headers.DEFAULT_IP,
        yandex_uid=headers.YANDEX_UID,
        disable_automatic_composite_refund=True,
    )

    transactions.update.check(
        operation_type='create',
        operation_id=operation_id,
        id=consts.ORDER_ID,
        items_by_payment_type=[
            {
                'items': models.to_operation_items(
                    ITEMS, product_id=product_id,
                ),
                'payment_type': payment_method.payment_type.value,
            },
        ],
        originator=consts.TRANSACTIONS_ORIGINATOR,
        user_ip=headers.DEFAULT_IP,
        yandex_uid=headers.YANDEX_UID,
        disable_automatic_composite_refund=True,
        version=1,
    )

    response = await grocery_payments_create(
        items=ITEMS,
        payment_method=payment_method,
        operation_id=operation_id,
        user_info=headers.DEFAULT_USER_INFO,
    )
    assert response.status_code == 200

    assert transactions.create.times_called == 1
    assert transactions.update.times_called == 1

    assert response.json() == {
        'invoice_id': consts.ORDER_ID,
        'operation_id': operation_id,
    }


async def test_create_invalid_card_400(grocery_payments_create):
    response = await grocery_payments_create(
        payment_method=models.PaymentMethod(
            payment_type=PaymentType.card, payment_id='eda-card',
        ),
        operation_id='some_operation_id',
        user_info=headers.DEFAULT_USER_INFO,
    )
    assert response.status_code == 400


@pytest_marks.COUNTRIES
async def test_country(grocery_payments_create, transactions, country):
    transactions.create.check(currency=country.currency)

    response = await grocery_payments_create(country=country)
    assert response.status_code == 200

    assert transactions.create.times_called == 1
    assert transactions.update.times_called == 1


@pytest_marks.INVOICE_ORIGINATORS
async def test_originator(grocery_payments_create, transactions, originator):
    invoice_id = originator.prefix + consts.ORDER_ID

    transactions.create.check(id=invoice_id)
    transactions.update.check(id=invoice_id)

    response = await grocery_payments_create(
        order_id=consts.ORDER_ID, originator=originator.request_name,
    )
    assert response.status_code == 200

    assert transactions.create.times_called == 1
    assert transactions.update.times_called == 1

    assert response.json()['invoice_id'] == invoice_id


@pytest.mark.parametrize(
    'transactions_originator',
    ['grocery_payments', 'grocery_payments_fallback_proxy'],
)
async def test_transactions_originator(
        grocery_payments_create,
        transactions,
        grocery_payments_configs,
        transactions_originator,
):
    grocery_payments_configs.set_originator(transactions_originator)
    transactions.update.check(originator=transactions_originator)

    response = await grocery_payments_create()
    assert response.status_code == 200

    assert transactions.update.times_called == 1


async def test_auth_context(grocery_payments_create, transactions, user_state):
    transactions.create.check(
        pass_params=consts.PASS_PARAMS,
        personal_phone_id=headers.PERSONAL_PHONE_ID,
        user_ip=headers.DEFAULT_IP,
        yandex_uid=headers.YANDEX_UID,
    )

    transactions.update.check(
        user_ip=headers.DEFAULT_IP, yandex_uid=headers.YANDEX_UID,
    )

    response = await grocery_payments_create()
    assert response.status_code == 200

    assert transactions.create.times_called == 1
    assert transactions.update.times_called == 1


async def test_create_billing_settings_version(
        grocery_payments_create, transactions,
):
    trust_settings = configs.trust_settings_versioned(COUNTRY)
    billing_service = trust_settings['billing_service']

    transactions.create.check(billing_service=billing_service)

    response = await grocery_payments_create(
        billing_settings_version=configs.BILLING_SETTINGS_VERSION,
    )
    assert response.status_code == 200


@pytest.mark.parametrize('enabled', [True, False])
async def test_without_trust_orders(
        grocery_payments_create,
        transactions,
        grocery_payments_configs,
        enabled,
):
    grocery_payments_configs.without_trust_orders(enabled)

    transactions.create.check(without_trust_orders=enabled)

    response = await grocery_payments_create()
    assert response.status_code == 200


async def test_create_badge(grocery_payments_create, transactions, passport):
    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']

    payment_method = models.PaymentMethod(
        payment_type=PaymentType.badge, payment_id=consts.PAYMENT_ID,
    )

    transactions.create.check(payments=[payment_method.to_transactions()])

    transactions.update.check(
        items_by_payment_type=[
            {
                'items': models.to_operation_items(
                    ITEMS, product_id=product_id,
                ),
                'payment_type': payment_method.payment_type.value,
            },
        ],
    )

    passport.user = PassportUser(headers.YANDEX_UID, consts.STAFF_LOGIN, True)
    passport.blackbox.check(uid=headers.YANDEX_UID, userip=headers.DEFAULT_IP)

    response = await grocery_payments_create(payment_method=payment_method)
    assert response.status_code == 200

    assert transactions.create.times_called == 1
    assert transactions.update.times_called == 1
    assert passport.blackbox.times_called == 1


async def test_create_corp(grocery_payments_create, transactions, user_state):
    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']

    payment_method = models.PaymentMethod(
        payment_type=PaymentType.corp, payment_id=consts.PAYMENT_ID,
    )

    transactions.create.check(
        pass_params={
            'user_info': {
                'is_portal': False,
                'accept_language': headers.DEFAULT_LOCALE,
                'personal_phone_id': headers.PERSONAL_PHONE_ID,
            },
        },
        payments=[payment_method.to_transactions()],
    )

    transactions.update.check(
        items_by_payment_type=[
            {
                'items': models.to_operation_items(
                    ITEMS, product_id=product_id,
                ),
                'payment_type': payment_method.payment_type.value,
            },
        ],
    )

    response = await grocery_payments_create(payment_method=payment_method)
    assert response.status_code == 200

    assert transactions.create.times_called == 1
    assert transactions.update.times_called == 1


@pytest.mark.parametrize(
    'payment_id, expected_status_code',
    [('sbp_link', 200), ('sbp_qr', 200), ('??', 400)],
)
async def test_create_sbp(
        grocery_payments_create,
        transactions,
        user_state,
        payment_id,
        expected_status_code,
):
    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']

    payment_method = models.PaymentMethod(
        payment_type=PaymentType.sbp, payment_id=payment_id,
    )

    transactions.create.check(payments=[payment_method.to_transactions()])

    transactions.update.check(
        items_by_payment_type=[
            {
                'items': models.to_operation_items(
                    ITEMS, product_id=product_id,
                ),
                'payment_type': payment_method.payment_type.value,
            },
        ],
    )

    response = await grocery_payments_create(payment_method=payment_method)
    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    'country, extra',
    [
        (
            models.Country.Russia,
            dict(
                cashback_service=consts.RUSSIA_CASHBACK_SERVICE,
                ticket=consts.RUSSIA_CASHBACK_TICKET,
            ),
        ),
        (
            models.Country.Israel,
            dict(
                cashback_service=consts.ISRAEL_CASHBACK_SERVICE,
                ticket=consts.ISRAEL_CASHBACK_TICKET,
            ),
        ),
    ],
)
async def test_create_with_cashback(
        grocery_payments_create, transactions, country, extra,
):
    trust_settings = configs.trust_settings_payload(country)
    product_id = trust_settings['product_id']

    payments = [
        PAYMENT_METHOD.to_transactions(),
        CASHBACK_PAYMENT_METHOD.to_transactions(),
    ]

    transactions.create.check(payments=payments)

    transactions.update.check(
        operation_type='create',
        wallet_payload={
            'has_plus': 'true',
            'order_id': consts.ORDER_ID,
            'service_id': consts.CASHBACK_SERVICE_ID,
            'wallet_id': consts.PERSONAL_WALLET_ID,
            **extra,
        },
        items_by_payment_type=[
            {
                'items': models.to_operation_items(
                    ITEMS, product_id=product_id,
                ),
                'payment_type': PAYMENT_METHOD.payment_type.value,
            },
            {
                'items': models.to_operation_items(
                    ITEMS, product_id=product_id,
                ),
                'payment_type': CASHBACK_PAYMENT_METHOD.payment_type.value,
            },
        ],
    )

    response = await grocery_payments_create(
        country=country,
        items_by_payment_types=[
            {
                'items': models.to_request_items(ITEMS),
                'payment_method': PAYMENT_METHOD.to_request(),
            },
            {
                'items': models.to_request_items(ITEMS),
                'payment_method': CASHBACK_PAYMENT_METHOD.to_request(),
            },
        ],
    )
    assert response.status_code == 200

    assert transactions.create.times_called == 1
    assert transactions.update.times_called == 1


@pytest.mark.parametrize(
    'version_after_create_409, enable_to_resolve_by_version',
    [(1, True), (2, True), (3, False)],
)
@pytest.mark.parametrize(
    'currency_in_retrieve, enable_to_resolve_by_currency',
    [(None, True), ('unknown-currency', False)],
)
async def test_conflicts_during_create(
        grocery_payments_create,
        transactions,
        version_after_create_409,
        enable_to_resolve_by_version,
        currency_in_retrieve,
        enable_to_resolve_by_currency,
):
    if currency_in_retrieve is None:
        currency_in_retrieve = COUNTRY.currency

    transactions.create.status_code = 409

    transactions.retrieve.mock_response(
        currency=currency_in_retrieve,
        operation_info={
            'originator': 'processing',
            'priority': 1,
            'version': version_after_create_409,
        },
    )

    response = await grocery_payments_create()

    assert transactions.create.times_called == 1

    enable_to_resolve = (
        enable_to_resolve_by_version and enable_to_resolve_by_currency
    )

    if enable_to_resolve:
        assert transactions.update.times_called == 1
        assert transactions.retrieve.times_called == 1
        assert response.status_code == 200
    else:
        assert response.status_code == 409
        assert transactions.retrieve.times_called == 1


@pytest.mark.parametrize(
    'first_item_price, enable_to_resolve_by_price',
    [(FIRST_ITEM_PRICE, True), (FIRST_ITEM_PRICE + '1', False)],
)
@pytest.mark.parametrize(
    'second_item_quantity, enable_to_resolve_by_quantity',
    [(SECOND_ITEM_QUANTITY, True), (SECOND_ITEM_QUANTITY + '1', False)],
)
@pytest.mark.parametrize(
    'operation_payment_method, enable_to_resolve_by_payment',
    [(PAYMENT_METHOD.payment_type.value, True), ('corp', False)],
)
async def test_conflicts_during_update(
        grocery_payments_create,
        transactions,
        first_item_price,
        enable_to_resolve_by_price,
        second_item_quantity,
        enable_to_resolve_by_quantity,
        operation_payment_method,
        enable_to_resolve_by_payment,
):
    transactions.update.status_code = 409

    items = copy.deepcopy(ITEMS)
    items[0].price = first_item_price
    items[1].quantity = second_item_quantity

    last_operation_revision = 'last-operation-id'
    request_operation_id = 'request-operation-id'

    assert last_operation_revision != request_operation_id

    operation = copy.deepcopy(consts.DEFAULT_OPERATION)
    operation['sum_to_pay'] = [
        {
            'items': models.to_operation_items(items),
            'payment_type': operation_payment_method,
        },
    ]
    operation['id'] = f'create:{last_operation_revision}'

    transactions.retrieve.mock_response(
        operations=[consts.DEFAULT_OPERATION, operation],
    )

    response = await grocery_payments_create(operation_id=request_operation_id)

    assert transactions.create.times_called == 1
    assert transactions.update.times_called == 1

    enable_to_resolve = (
        enable_to_resolve_by_price
        and enable_to_resolve_by_quantity
        and enable_to_resolve_by_payment
    )

    if enable_to_resolve:
        assert transactions.retrieve.times_called == 1
        assert response.status_code == 200
        assert response.json() == {
            'invoice_id': consts.ORDER_ID,
            'operation_id': last_operation_revision,
        }
    else:
        assert transactions.retrieve.times_called == 1
        assert response.status_code == 409


@pytest.mark.parametrize(
    'title_request, title_transactions',
    [
        pytest.param('a' * 120, 'a' * 120, id='small_title'),
        pytest.param(
            'a' * 150, 'a' * 125 + '...', id='truncation_long_en_title',
        ),
        pytest.param(
            'абвг' * 100, 'абвг' * 31 + 'а' + '...', id='truncation_utf8',
        ),
    ],
)
async def test_items_title_truncate_utf8(
        grocery_payments_create,
        transactions,
        title_request,
        title_transactions,
):
    items = copy.deepcopy(ITEMS)
    items[0].receipt_info = models.ReceiptInfo(
        title=title_request, vat='20', personal_tin_id='personal-tin-id-x123',
    )

    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']

    items[0].receipt_info = models.ReceiptInfo(
        title=title_transactions,
        vat='20',
        personal_tin_id='personal-tin-id-x123',
    )

    transactions_items = models.to_operation_items(items, product_id)

    transactions.update.check(
        items_by_payment_type=[
            {'items': transactions_items, 'payment_type': 'card'},
        ],
    )

    response = await grocery_payments_create(items=items)
    assert response.status_code == 200

    assert transactions.create.times_called == 1
    assert transactions.update.times_called == 1


@pytest.mark.now(consts.NOW)
async def test_create_autoclear(grocery_payments_create, transactions):
    transactions.create.check(id=consts.ORDER_ID)
    transactions.clear.check(id=consts.ORDER_ID, clear_eta=consts.NOW)

    response = await grocery_payments_create(autoclear=True)
    assert response.status_code == 200

    assert transactions.create.times_called == 1
    assert transactions.update.times_called == 1
    assert transactions.clear.times_called == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('payment_type', [PaymentType.card, PaymentType.sbp])
async def test_create_save_last_pm(
        grocery_payments_create, user_state, payment_type,
):
    payment_method = copy.deepcopy(PAYMENT_METHOD)

    if payment_type == PaymentType.sbp:
        payment_method.payment_meta = dict(sbp=dict(bank='bank'))

    user_state.service = 'grocery'
    user_state.last_payment_method.check(
        payment_method=PAYMENT_METHOD.to_request(),
        headers={
            'X-Yandex-UID': headers.YANDEX_UID,
            'X-YaTaxi-User': headers.USER_INFO,
        },
    )

    response = await grocery_payments_create(payment_method=PAYMENT_METHOD)
    assert response.status_code == 200

    assert user_state.last_payment_method.times_called == 1


@configs.CARDSTORAGE_AVS_DATA
async def test_avs_data_in_pass_params(grocery_payments_create, transactions):
    transactions.create.check(pass_params=configs.PASS_PARAMS)

    response = await grocery_payments_create()
    assert response.status_code == 200

    assert transactions.create.times_called == 1


@configs.CARDSTORAGE_AVS_DATA
@pytest.mark.parametrize('enabled', [True, False])
async def test_trust_afs_params(
        grocery_payments_create,
        grocery_payments_configs,
        transactions,
        enabled,
):
    grocery_payments_configs.set_force_3ds(enabled)

    trust_afs_params = {'force_3ds': enabled}
    transactions.create.check(trust_afs_params=trust_afs_params)

    response = await grocery_payments_create()
    assert response.status_code == 200

    assert transactions.create.times_called == 1


@configs.CARDSTORAGE_AVS_DATA
@pytest.mark.parametrize('verified', [True, False])
async def test_force_3ds_for_unverified(
        grocery_payments_create, transactions, verified,
):
    trust_afs_params = {'force_3ds': not verified}
    transactions.create.check(trust_afs_params=trust_afs_params)
    payment_method = models.PaymentMethod(
        payment_type=PaymentType.card,
        payment_id=consts.CARD_ID,
        payment_meta=dict(card=dict(verified=verified)),
    )

    response = await grocery_payments_create(payment_method=payment_method)
    assert response.status_code == 200

    assert transactions.create.times_called == 1


@configs.TERMINAL_PASS_PARAMS_ENABLED
async def test_processing_name_in_pass_params(
        grocery_payments_create,
        transactions,
        grocery_payments_configs,
        experiments3,
):
    name = 'some_name_123'

    grocery_payments_configs.disable_eda_route_data(enabled=True)
    grocery_payments_configs.processing_name(name)

    is_yandex_card = True
    payment_method = models.PaymentMethod(
        payment_type=PaymentType.card,
        payment_id=consts.CARD_ID,
        payment_meta=dict(card=dict(is_yandex_card=is_yandex_card)),
    )

    transactions.create.check(
        pass_params={'terminal_route_data': {'preferred_processing_cc': name}},
    )

    exp3_recorder = experiments3.record_match_tries(
        configs.PROCESSING_NAME_CONFIG,
    )

    region_id = 2809
    response = await grocery_payments_create(
        region_id=region_id, payment_method=payment_method,
    )
    assert response.status_code == 200

    assert transactions.create.times_called == 1

    exp3_matches = await exp3_recorder.get_match_tries(1)
    exp3_kwargs = exp3_matches[0].kwargs

    assert exp3_kwargs['personal_phone_id'] == headers.PERSONAL_PHONE_ID
    assert (
        exp3_kwargs['primary_payment_type']
        == PAYMENT_METHOD.payment_type.value
    )
    assert exp3_kwargs['country_iso3'] == COUNTRY.country_iso3
    assert exp3_kwargs['yandex_uid'] == headers.YANDEX_UID
    assert exp3_kwargs['region_id'] == region_id
    assert exp3_kwargs['is_yandex_card'] == is_yandex_card


@configs.TERMINAL_PASS_PARAMS_ENABLED
@pytest.mark.parametrize('disable_eda_route_data', [True, False])
async def test_terminal_route_params_in_pass_params(
        grocery_payments_create,
        transactions,
        grocery_payments_configs,
        disable_eda_route_data,
):
    grocery_payments_configs.disable_eda_route_data(
        enabled=disable_eda_route_data,
    )

    pass_params = consts.PASS_PARAMS
    if not disable_eda_route_data:
        pass_params = {
            'terminal_route_data': {
                'merchant': 'lavka',
                'business': 'retail',
                'force_3ds': False,
                '3ds_supported': False,
            },
        }

    transactions.create.check(pass_params=pass_params)

    response = await grocery_payments_create()
    assert response.status_code == 200

    assert transactions.create.times_called == 1


@configs.TERMINAL_PASS_PARAMS_ENABLED
@pytest.mark.config(GROCERY_PAYMENTS_OPERATION_TTL_SECONDS=300)
async def test_ttl_on_update(grocery_payments_create, transactions):
    transactions.update.check(ttl=300)

    response = await grocery_payments_create()
    assert response.status_code == 200

    assert transactions.update.times_called == 1


async def test_create_with_empty_items(grocery_payments_create, transactions):
    payments = []

    transactions.create.check(payments=payments)

    transactions.update.check(
        operation_type='create', items_by_payment_type=[],
    )

    response = await grocery_payments_create(items_by_payment_types=[])
    assert response.status_code == 200

    assert transactions.create.times_called == 1
    assert transactions.update.times_called == 1


@pytest.mark.now(consts.NOW)
async def test_operation_timeout(
        grocery_payments_create,
        grocery_payments_configs,
        transactions,
        check_operation_timeout_stq_event,
):
    operation_type = 'create'
    operation_id = '123'
    ttl_seconds = 123

    grocery_payments_configs.set_operation_timeout(ttl_seconds=ttl_seconds)

    transactions.update.check(
        operation_type=operation_type, operation_id=operation_id,
    )

    response = await grocery_payments_create(operation_id=operation_id)
    assert response.status_code == 200

    invoice_id = response.json()['invoice_id']
    operation_id_full = f'{operation_type}:{operation_id}'
    task_id = f'{invoice_id}_{operation_id_full}'
    eta = consts.NOW_DT + datetime.timedelta(seconds=ttl_seconds)

    check_operation_timeout_stq_event(
        stq_event_id=task_id,
        eta=eta,
        invoice_id=invoice_id,
        operation_id=operation_id_full,
        type='hold_operation',
    )


@pytest_marks.INVOICE_ORIGINATORS
async def test_debt_init(
        grocery_payments_create, transactions, grocery_user_debts, originator,
):
    response = await grocery_payments_create(
        originator=originator.request_name,
    )
    assert response.status_code == 200

    assert grocery_user_debts.init.times_called == 1


async def test_debt_clear(
        grocery_payments_create, transactions, grocery_user_debts,
):
    response = await grocery_payments_create(autoclear=True)
    assert response.status_code == 200

    assert grocery_user_debts.init.times_called == 1
    assert grocery_user_debts.clear.times_called == 1


async def test_idempotency(
        grocery_payments_create, grocery_payments_db, transactions,
):
    invoice_id = consts.ORDER_ID
    operation_id = 'operation_id'

    for _ in range(2):
        response = await grocery_payments_create(operation_id=operation_id)
        assert response.status_code == 200

        assert grocery_payments_db.has_invoice_operation(
            invoice_id, f'create:{operation_id}',
        )

    assert transactions.create.times_called == 1


@pytest.mark.parametrize('operation_id', ['', ':', 'op:', ':op', 'o:p'])
async def test_wrong_operation_id(grocery_payments_create, operation_id):
    response = await grocery_payments_create(operation_id=operation_id)
    assert response.status_code == 400
