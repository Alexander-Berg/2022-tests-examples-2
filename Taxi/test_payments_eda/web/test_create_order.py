# pylint: disable=too-many-lines

import dataclasses
import datetime
import decimal
import typing

from aiohttp import web
import pytest

from taxi.clients import experiments3
from taxi.util import dates as date_utils
from taxi.util import unused

from payments_eda import consts as service_consts
from payments_eda.utils import experiments
from test_payments_eda import common
from test_payments_eda import consts
from test_payments_eda import preorder

VALID_CARD_ID = 'card-x5a4adedaf78dba6f9c56fee4'
VALID_WALLET_ID = 'wallet_id/1234567890'

DEFAULT_AMOUNT = '123.43'
PERSONAL_EMAIL_ID = 'personal-email-id'
PERSONAL_PHONE_ID = 'personal-phone-id'

TRANSACTIONS_EDA_GROCERY_SERVICE = 'grocery-order-cycle'


@dataclasses.dataclass()
class OrderMockParams:
    is_grocery: bool = False
    external_ref: str = '123'
    amount: str = DEFAULT_AMOUNT
    business: typing.Optional[str] = None
    max_bonus_points: typing.Optional[str] = None


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


NEW_BASE_URL = 'new_base_url'

GET_BASE_EDA_URL_FROM_EXPERIMENT = pytest.mark.client_experiments3(
    consumer=service_consts.EXP3_CONSUMER_WEB,
    experiment_name=experiments.EXP3_PAYMENTS_EDA_URLS,
    args=[
        {
            'name': 'yandex_uid',
            'type': 'string',
            'value': consts.DEFAULT_YANDEX_UID,
        },
        {'name': 'phone_id', 'type': 'string', 'value': 'phone_id'},
        {'name': 'service', 'type': 'string', 'value': 'eats'},
    ],
    value={'patched_base_url': f'$mockserver/{NEW_BASE_URL}'},
)


GROCERY_TRUST_SERVICE_ENABLED_DISABLED = pytest.mark.parametrize(
    'grocery_receipts_service_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                PAYMENTS_EDA_GROCERY_TRUST_SERVICE_ENABLED=True,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                PAYMENTS_EDA_GROCERY_TRUST_SERVICE_ENABLED=False,
            ),
        ),
    ],
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


def _get_item_from_invoice_update(request):
    items_by_payment_type = request.json['items_by_payment_type']
    assert len(items_by_payment_type) == 1

    items = items_by_payment_type[0]['items']
    assert len(items) == 1
    return items[0]


def _get_eda_response(
        amount, max_bonus_points=None, eats_meta_info=None, business=None,
):
    add_max_bonus_points = (
        {}
        if max_bonus_points is None
        else {'max_bonus_points': max_bonus_points}
    )
    add_eats_meta_info = (
        {} if eats_meta_info is None else {'meta_info': eats_meta_info}
    )
    add_business = {} if business is None else {'business': business}
    eda_response = {
        'items': [
            {
                'amount': amount,
                'currency': 'RUB',
                'item_id': '123',
                **add_eats_meta_info,
            },
        ],
        'country_code': 'RU',
        'region_id': 1,
        'service_product_id': 'food_product_id',
        'uuid': consts.DEFAULT_YANDEX_UID,
        'location': consts.LOCATION,
        'currency': 'RUB',
        **add_max_bonus_points,
        **add_business,
    }
    return eda_response


# pylint: disable=R0913,R0914
async def _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        payment_method='card',
        payment_method_id=VALID_CARD_ID,
        eats_meta_info=None,
        complements=None,
        service='eats',
        available_payment_types=None,
        person_is_kpb=False,
        ext_login_exp_enabled=False,
        status=200,
        order_params=OrderMockParams(),
        headers=Headers(),
        available_accounts_response=None,
        expected_split=None,
        expected_cardstorage_times_called=None,
        grocery_orders_mockserver=None,
        transactions_eda_service=None,
        billing_service=None,
        product_id=None,
        eda_doc_base_url=None,
):
    if transactions_eda_service is None:
        transactions_eda_service = service

    if available_payment_types is None:
        available_payment_types = ['card']

    mock_get_payment_types_info(
        request_service=service,
        request_yandex_uid=headers.pa_yandex_uid,
        request_user_agent=headers.pa_user_agent,
        available_payment_types=available_payment_types,
        merchant_ids=[],
    )

    if available_accounts_response is None:
        available_accounts_response = load_json(
            'personal_wallet_available_accounts.json',
        )
    personal_wallet_mock = available_accounts_mockserver(
        available_accounts_response,
    )

    if order_params.is_grocery:
        get_order_mock = grocery_orders_mockserver(
            preorder.grocery_orders_response_body(),
        )
        mock_grocery_cart.set_items(
            order_params.external_ref, order_params.amount,
        )
        mock_grocery_cart.set_payment_method(payment_method_id)
    else:
        eda_response = _get_eda_response(
            order_params.amount,
            order_params.max_bonus_points,
            eats_meta_info,
            order_params.business,
        )
        get_order_mock = eda_doc_mockserver(eda_response, eda_doc_base_url)

    unused.dummy(personal_wallet_mock)

    user_ip = '1.1.1.1'
    cardstorage_payment_methods = load_json('cardstorage_payment_methods.json')

    @mock_cardstorage('/v1/payment_methods')
    async def mock_payment_method(request, **kwargs):
        return cardstorage_payment_methods

    data = {
        'payment_method': payment_method,
        'payment_method_id': payment_method_id,
    }

    if complements is not None:
        data['complements'] = complements

    external_ref = order_params.external_ref

    transactions_payment_method = payment_method
    if payment_method == 'corp' and payment_method_id.startswith('badge:'):
        transactions_payment_method = 'badge'

    payer_login = 'ihelos'
    external_login = 'ihelos_external'
    wallet_account = {
        'id': (
            'wallet/yataxi'
            if VALID_WALLET_ID.startswith('wallet_id/')
            else VALID_WALLET_ID
        ),
    }

    @mockserver.json_handler('/user-state/internal/v1/last-payment-methods')
    def user_state_handler(request):
        expected = {
            'flows': [
                {
                    'flow_type': service_consts.FLOW_TYPE_ORDER,
                    'payment_method': {
                        'type': payment_method,
                        'id': payment_method_id,
                    },
                },
            ],
        }

        assert request.json == expected
        return {}

    unused.dummy(user_state_handler)

    @mockserver.json_handler('/blackbox/blackbox')
    def blackbox_handler(*args, **kwargs):
        return {
            'users': [
                {
                    'login': external_login,
                    'aliases': {} if person_is_kpb else {'13': payer_login},
                    'dbfields': (
                        {
                            'subscription.suid.668': (
                                '1' if person_is_kpb else ''
                            ),
                        }
                        if ext_login_exp_enabled
                        else {'subscription.suid.669': ''}
                    ),
                },
            ],
        }

    unused.dummy(blackbox_handler)

    @mockserver.json_handler('/badgepay/pg/eda/payerInfo')
    def badgepay_handler(request, *args, **kwargs):
        if ext_login_exp_enabled and person_is_kpb:
            assert 'externalLogin' in request.query
        else:
            assert 'login' in request.query
        return {'login': payer_login, 'location': 'All'}

    unused.dummy(badgepay_handler)

    def get_payment(payment_method, payment_method_id):
        payment = {'method': payment_method_id, 'type': payment_method}

        if payment_method == 'badge':
            payment['payer_login'] = payer_login
        elif payment_method == 'personal_wallet':
            payment['account'] = wallet_account
            payment['service'] = '32'
        else:
            payment['billing_id'] = ''
        return payment

    def validate_invoice_create(request):
        pass_params = {}
        nonlocal billing_service
        if billing_service is None:
            billing_service = 'food_payment'
        if payment_method == 'corp' and payment_method_id.startswith('badge:'):
            billing_service = 'food_payment_badge'
        elif payment_method == 'corp':
            pass_params = {
                'user_info': {
                    'accept_language': 'ru-RU',
                    'is_portal': False,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                },
            }
            billing_service = 'food_payment_corp'
        elif payment_method == 'personal_wallet':
            billing_service = 'food_payment_wallet'

        payments = [
            get_payment(transactions_payment_method, payment_method_id),
        ]
        if complements is not None:
            payments += [
                get_payment(c['payment_method'], c['payment_method_id'])
                for c in complements
            ]

        expected_personal_email_id = None
        expected_personal_phone_id = None
        if order_params.business == service_consts.BUSINESS_PHARMACY:
            billing_service = service_consts.BILLING_SERVICE_PHARMACY
        if order_params.business == service_consts.BUSINESS_ZAPRAVKI_ROS_NEFT:
            billing_service = service_consts.BILLING_SERVICE_FUEL
            pass_params['terminal_route_data'] = {'description': 'food'}
            expected_personal_email_id = PERSONAL_EMAIL_ID
        if order_params.is_grocery:
            expected_personal_phone_id = PERSONAL_PHONE_ID

        invoice_due = date_utils.localize(
            datetime.datetime.strptime(
                '2018-07-20T14:10:00', '%Y-%m-%dT%H:%M:%S',
            ),
        ).isoformat()

        expected_data = {
            'billing_service': billing_service,
            'currency': 'RUB',
            'id': external_ref,
            'invoice_due': invoice_due,
            'pass_params': pass_params,
            'user_ip': user_ip,
            'yandex_uid': headers.pa_yandex_uid,
            'external_user_info': {
                'user_id': headers.pa_ya_taxi_user_id,
                'origin': 'taxi',
            },
            'service': transactions_eda_service,
            'payments': payments,
        }
        if expected_personal_email_id is not None:
            expected_data['personal_email_id'] = expected_personal_email_id
        if expected_personal_phone_id is not None:
            expected_data['personal_phone_id'] = expected_personal_phone_id

        assert request.json == expected_data

    @mockserver.json_handler('/transactions-eda/v2/invoice/create')
    def v2_invoices_create_handler(request):
        validate_invoice_create(request)
        return {}

    def validate_invoice_update(request):
        payments = [
            get_payment(transactions_payment_method, payment_method_id),
        ]
        if complements is not None:
            payments += [
                get_payment(c['payment_method'], c['payment_method_id'])
                for c in complements
            ]

        def _get_amount(item):
            if 'amount' in item['items'][0]:
                return item['items'][0]['amount']

            price = decimal.Decimal(item['items'][0]['price'])
            quantity = decimal.Decimal(item['items'][0]['quantity'])

            return str(price * quantity)

        given_split = {
            item['payment_type']: _get_amount(item)
            for item in request.json['items_by_payment_type']
        }

        if expected_split is not None:
            assert given_split == expected_split
        assert request.json['operation_id'] == 'create:foobar'
        assert request.json['payments'] == payments

        if order_params.business == service_consts.BUSINESS_ZAPRAVKI_ROS_NEFT:
            assert request.json['payment_timeout'] == 180

            item = _get_item_from_invoice_update(request)
            assert item == {
                'amount': '123.43',
                'commission_category': 600,
                'fiscal_receipt_info': {
                    'personal_tin_id': '100500',
                    'title': 'Сопутствующие продовольственные товары',
                    'vat': 'nds_20',
                },
                'item_id': 'food',
                'product_id': 'food_product_id',
            }

        if order_params.is_grocery:
            item = _get_item_from_invoice_update(request)
            assert item['product_id'] == product_id
            assert item['price'] == DEFAULT_AMOUNT
            assert item['quantity'] == '1'

    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def v2_invoices_update_handler(request):
        validate_invoice_update(request)
        return {}

    mock_uuid('foobar')

    request_url = (
        f'/4.0/payments/v1/orders?external_ref={external_ref}'
        f'&service={service}'
    )
    resp = await web_app_client.post(
        request_url,
        json=data,
        headers=build_pa_headers(
            user_ip,
            'ru-RU',
            yandex_uid=headers.pa_yandex_uid,
            bound_uids=headers.pa_bound_uids,
            user_agent=headers.pa_user_agent,
            request_application=headers.pa_request_application,
            ya_taxi_pass_flags=headers.pa_ya_taxi_pass_flags,
            personal_phone_id=PERSONAL_PHONE_ID,
            personal_email_id=PERSONAL_EMAIL_ID,
        ),
    )
    if status != 200:
        assert resp.status == status
        return

    data = await resp.json()
    if _pharmacy_corp_order(
            order_params.business, payment_method, payment_method_id,
    ):
        assert resp.status == 409
        assert data == {
            'code': 'invalid_payment_method',
            'message': 'invalid payment method',
        }
        create_times_called = 0
        update_times_called = 0
    else:
        assert resp.status == 200
        assert data == {
            'order_id': external_ref,
            'total': order_params.amount,
            'currency': 'RUB',
            'expires_at': '2018-07-21T17:00:00+03:00',
        }
        create_times_called = 1
        update_times_called = 1

    if expected_cardstorage_times_called is None:
        expected_cardstorage_times_called = int(
            'card' in available_payment_types,
        )
    assert (
        mock_payment_method.times_called == expected_cardstorage_times_called
    )
    assert v2_invoices_create_handler.times_called == create_times_called
    assert v2_invoices_update_handler.times_called == update_times_called
    assert get_order_mock.times_called == 1


@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.config(PAYMENTS_EDA_COLLECT_PRODUCT_METRICS=True)
@pytest.mark.parametrize(
    'service',
    [
        service_consts.SERVICE_EATS,
        service_consts.SERVICE_GROCERY,
        service_consts.SERVICE_PHARMACY,
        service_consts.SERVICE_SHOP,
    ],
)
async def test_create_order_with_custom_service(
        web_app,
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        mock_get_payment_types_info,
        get_single_stat_by_label_values,
        mockserver,
        patch,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        available_accounts_mockserver,
        service,
):
    await _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        service=service,
    )

    stat = get_single_stat_by_label_values(
        web_app['context'], {'sensor': 'create_order_prefinish'},
    )

    assert stat == common.make_stat(
        {
            'invoice_service': service,
            'sensor': 'create_order_prefinish',
            'currency': 'RUB',
            'country_code': 'RU',
            'region_id': '1',
        },
    )


# pylint: disable=R0913,R0914
@_enable_wallet_for('eats')
@pytest.mark.config(PAYMENTS_EDA_SAVE_LAST_PAYMENT_METHOD_ENABLED=True)
@pytest.mark.config(PERSONAL_WALLET_FIRM_BY_SERVICE={'eats': {'RUB': '32'}})
@pytest.mark.config(PAYMENTS_EDA_CORP_ENABLED=True)
@pytest.mark.config(PAYMENTS_EDA_COLLECT_PRODUCT_METRICS=True)
@pytest.mark.config(PAYMENTS_EDA_FUEL_FISCAL_PERSONAL_TIN_ID='100500')
@pytest.mark.config(PAYMENTS_EDA_GROCERY_RECEIPTS_ENABLED=True)
@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.parametrize(
    'payment_method, payment_method_id, '
    'available_payment_types, person_is_kpb, ext_login_exp_enabled, status',
    [
        ('card', VALID_CARD_ID, ['applepay', 'card'], False, False, 200),
        ('card', 'card-unknown', ['applepay', 'card'], False, False, 409),
        ('card', VALID_CARD_ID, [], False, False, 409),
        ('applepay', 'applepay-123', ['applepay', 'card'], False, False, 200),
        ('applepay', 'applepay-123', [], False, False, 409),
        ('googlepay', 'googlepay-123', ['googlepay'], False, False, 200),
        ('googlepay', 'googlepay-123', ['card'], False, False, 409),
        ('unknown', 'unknown-123', ['card'], False, False, 400),
        ('corp', 'corp:yataxi_rus_dmkurilov:RUB', ['corp'], False, False, 200),
        ('corp', 'corp:someteam:RUB', ['corp'], False, False, 409),
        ('corp', 'unknown', ['corp'], False, False, 409),
        ('corp', 'badge:hello:RUB', ['badge'], False, False, 200),
        ('corp', 'badge:hello:RUB', ['badge'], True, True, 200),
        ('corp', 'badge:hello:RUB', ['card'], False, False, 409),
        (
            'personal_wallet',
            VALID_WALLET_ID,
            ['personal_wallet'],
            True,
            False,
            200,
        ),
    ],
)
@pytest.mark.parametrize('business', [None, 'pharmacy', 'zapravki_ros_neft'])
async def test_create_order(
        web_app,
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        mock_get_payment_types_info,
        mockserver,
        patch,
        load_json,
        payment_method,
        payment_method_id,
        available_payment_types,
        person_is_kpb,
        ext_login_exp_enabled,
        status,
        business,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        available_accounts_mockserver,
        get_single_stat_by_label_values,
):
    await _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        payment_method=payment_method,
        payment_method_id=payment_method_id,
        available_payment_types=available_payment_types,
        person_is_kpb=person_is_kpb,
        ext_login_exp_enabled=ext_login_exp_enabled,
        status=status,
        order_params=OrderMockParams(business=business),
        service='eats',
    )
    # Collect metrics on success
    if status != 200 or _pharmacy_corp_order(
            business, payment_method, payment_method_id,
    ):
        return

    stat = get_single_stat_by_label_values(
        web_app['context'], {'sensor': 'create_order_prefinish'},
    )

    assert stat == common.make_stat(
        {
            'invoice_service': 'eats',
            'sensor': 'create_order_prefinish',
            'currency': 'RUB',
            'country_code': 'RU',
            'region_id': '1',
        },
    )


def _make_complements(**kwargs):
    return [
        {'payment_method': k, 'payment_method_id': v}
        for k, v in kwargs.items()
    ]


@pytest.mark.config(PAYMENTS_EDA_FUEL_FISCAL_PERSONAL_TIN_ID='100500')
@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.parametrize(
    'business',
    [
        None,
        'restaurant',
        'store',
        'pharmacy',
        'shop',
        'zapravki_ros_neft',
        'zapravki',
    ],
)
async def test_create_order_parametrize_business(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        available_accounts_mockserver,
        business,
):
    await _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        order_params=OrderMockParams(business=business),
        service='eats',
    )


@_enable_wallet_for('eats')
@enable_complement_payments
@pytest.mark.config(PERSONAL_WALLET_FIRM_BY_SERVICE={'eats': {'RUB': '32'}})
@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.parametrize(
    'available_payment_types',
    (['card'], ['personal_wallet'], ['card', 'personal_wallet']),
)
@pytest.mark.parametrize(
    'status,primary,complements',
    (
        (200, 'card', None),
        (200, 'card', _make_complements()),
        (200, 'card', _make_complements(personal_wallet=VALID_WALLET_ID)),
        (409, 'card', _make_complements(card=VALID_CARD_ID)),
    ),
)
@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
@preorder.GROCERY_TRUST_SERVICE_ENABLED_DISABLED
@preorder.GROCERY_TRUST_SETTINGS
async def test_create_composite_order(
        web_app,
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        grocery_orders_mockserver,
        mock_get_payment_types_info,
        personal_store_mockserver,
        mockserver,
        load_json,
        available_payment_types,
        status,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        available_accounts_mockserver,
        primary,
        complements,
        is_grocery,
        external_ref,
        grocery_billing_service,
        grocery_product_id,
        grocery_trust_settings_enabled,
):
    available_accounts_response = load_json(
        'available_accounts_with_complements.json',
    )

    types = {primary}
    for complement in complements or []:
        types.add(complement['payment_method'])
    if not types <= set(available_payment_types):
        status = 409

    transactions_eda_service = None
    billing_service = None
    product_id = None
    if is_grocery:
        transactions_eda_service = TRANSACTIONS_EDA_GROCERY_SERVICE
        billing_service = grocery_billing_service
        product_id = grocery_product_id
        personal_store_mockserver(value=preorder.GROCERY_DEFAULT_TIN)

    await _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        payment_method=primary,
        payment_method_id=VALID_CARD_ID,
        available_payment_types=available_payment_types,
        status=status,
        complements=complements,
        available_accounts_response=available_accounts_response,
        order_params=OrderMockParams(
            is_grocery=is_grocery, external_ref=external_ref,
        ),
        grocery_orders_mockserver=grocery_orders_mockserver,
        transactions_eda_service=transactions_eda_service,
        billing_service=billing_service,
        product_id=product_id,
    )


@pytest.mark.parametrize(
    'amount,max_discount,complement_balance,expected_split',
    (
        ('100', '40', '100', {'card': '60', 'personal_wallet': '40'}),
        ('100', '150', '125', {'card': '0', 'personal_wallet': '100'}),
        ('100', '50', '30', {'card': '70', 'personal_wallet': '30'}),
        ('100', '150', '80', {'card': '20', 'personal_wallet': '80'}),
        ('100', '150', '170', {'card': '0', 'personal_wallet': '100'}),
    ),
)
@_enable_wallet_for('eats')
@enable_complement_payments
@pytest.mark.config(PERSONAL_WALLET_FIRM_BY_SERVICE={'eats': {'RUB': '32'}})
@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_split_on_complement_payment(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        available_accounts_mockserver,
        max_discount,
        complement_balance,
        expected_split,
        amount,
):
    available_accounts_response = load_json(
        'available_accounts_with_complements.json',
    )
    for account in available_accounts_response['available_accounts']:
        account['money_left_as_decimal'] = complement_balance

    complements = [
        {
            'payment_method': 'personal_wallet',
            'payment_method_id': VALID_WALLET_ID,
        },
    ]

    await _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        payment_method='card',
        payment_method_id=VALID_CARD_ID,
        complements=complements,
        available_payment_types=['card', 'personal_wallet'],
        available_accounts_response=available_accounts_response,
        expected_split=expected_split,
        order_params=OrderMockParams(
            amount=amount, max_bonus_points=max_discount,
        ),
    )


def _pharmacy_corp_order(
        business: str, payment_method: str, payment_method_id: str,
):
    return all(
        [
            business == service_consts.BUSINESS_PHARMACY
            and payment_method == 'corp'
            and not payment_method_id.startswith('badge'),
        ],
    )


# pylint: disable=protected-access
# pylint: disable=R0913,R0914
@pytest.mark.config(PAYMENTS_EDA_CORP_ENABLED=True)
@pytest.mark.config(PAYMENTS_EDA_COLLECT_PRODUCT_METRICS=True)
@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.parametrize(
    'pa_yandex_uid, pa_bound_uids, expected_status',
    [
        (consts.DEFAULT_YANDEX_UID, '', 200),
        (
            'unknown_uid',
            f'unknown_uid_1,{consts.DEFAULT_YANDEX_UID},unknown_uid_2',
            200,
        ),
        ('unknown_uid', '', 404),
        ('unknown_uid', 'unknown_uid_1,unknown_uid_2,unknown_uid_3', 404),
    ],
)
async def test_order_user_access(
        web_app,
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        pa_yandex_uid,
        pa_bound_uids,
        expected_status,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
):
    await _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        status=expected_status,
        headers=Headers(
            pa_yandex_uid=pa_yandex_uid, pa_bound_uids=pa_bound_uids,
        ),
    )


@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.parametrize(
    'pa_request_application, expected_client_application',
    [
        # empty header from PA
        ('', None),
        # cannot parse header from PA
        ('some unknown header', None),
        (
            'app_brand=yataxi,app_ver2=21,platform_ver1=12,app_ver1=5,'
            'app_name=iphone,app_build=release,platform_ver2=1,'
            'app_ver3=43204,platform_ver3=2',
            experiments3.ClientApplication(
                application='iphone', version='5.21.43204', brand='yataxi',
            ),
        ),
        (
            'app_brand=yataxi,app_build=release,app_name=android,'
            'platform_ver1=9,app_ver1=3,app_ver2=131,app_ver3=0',
            experiments3.ClientApplication(
                application='android', version='3.131.0', brand='yataxi',
            ),
        ),
    ],
)
@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
@preorder.GROCERY_TRUST_SERVICE_ENABLED_DISABLED
@preorder.GROCERY_TRUST_SETTINGS
async def test_experiments_params(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        grocery_orders_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        personal_store_mockserver,
        mockserver,
        patch,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        load_json,
        pa_request_application,
        expected_client_application,
        is_grocery,
        external_ref,
        grocery_billing_service,
        grocery_product_id,
        grocery_trust_settings_enabled,
):
    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _mock_get_values(*args, client_application=None, **kwargs):
        assert client_application == expected_client_application
        return []

    transactions_eda_service = None
    billing_service = None
    product_id = None
    if is_grocery:
        transactions_eda_service = TRANSACTIONS_EDA_GROCERY_SERVICE
        billing_service = grocery_billing_service
        product_id = grocery_product_id
        personal_store_mockserver(value=preorder.GROCERY_DEFAULT_TIN)

    await _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        headers=Headers(pa_request_application=pa_request_application),
        order_params=OrderMockParams(
            is_grocery=is_grocery, external_ref=external_ref,
        ),
        grocery_orders_mockserver=grocery_orders_mockserver,
        transactions_eda_service=transactions_eda_service,
        billing_service=billing_service,
        product_id=product_id,
    )

    # checking only ExperimentsChecker - get_payment_types_info mocked
    # in these tests, but is tested separately
    assert len(_mock_get_values.calls) == 1


# pylint: disable=too-many-arguments,too-many-locals
async def _check_create_order_conflicts(
        web_app_client,
        mock_cardstorage,
        patch,
        mock_get_order,
        mock_get_payment_types_info,
        available_accounts_mockserver,
        mockserver,
        load_json,
        sum_to_pay,
        version,
        pm_id,
        response_code,
        build_pa_headers,
        empty_transactions_update_mock,
        is_grocery,
        external_ref,
):
    mock_get_payment_types_info(
        available_payment_types=['card', 'applepay'], merchant_ids=[],
    )

    eda_mock = mock_get_order(
        is_grocery=is_grocery, item_id=external_ref, amount=DEFAULT_AMOUNT,
    )

    cardstorage_payment_methods = load_json('cardstorage_payment_methods.json')

    @mock_cardstorage('/v1/payment_methods')
    async def mock_payment_method(request, **kwargs):
        return cardstorage_payment_methods

    original_card_id = 'card-x5a4adedaf78dba6f9c56fee4'

    @mockserver.json_handler('/transactions-eda/v2/invoice/create')
    def v2_invoices_create_handler(request):
        if v2_invoices_create_handler.times_called == 0:
            return {}

        assert request.json['user_ip'] != '1.1.1.1'
        return web.Response(
            status=409, body='{"code": "conflict", "message": "error"}',
        )

    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def mock_invoice_retrieve(request):
        return {
            'cleared': [],
            'currency': 'RUB',
            'debt': [],
            'held': [],
            'id': external_ref,
            'invoice_due': '2018-07-20T14:00:00.0000+0000',
            'operation_info': {
                'originator': 'processing',
                'priority': 1,
                'version': version,
            },
            'operations': [],
            'payment_types': ['card'],
            'status': 'init',
            'sum_to_pay': [
                {
                    'items': [{'amount': sum_to_pay, 'item_id': 'food'}],
                    'payment_type': 'card',
                },
            ],
            'transactions': [],
            'yandex_uid': consts.DEFAULT_YANDEX_UID,
            'created': '2018-07-20T14:00:00.0000+0000',
        }

    uri = f'/4.0/payments/v1/orders?service=eats&external_ref={external_ref}'
    for user_ip, card_id, expected_code in [
            ('1.1.1.1', original_card_id, 200),
            ('2.2.2.2', pm_id, response_code),
    ]:
        data = {'payment_method': 'card', 'payment_method_id': card_id}
        resp = await web_app_client.post(
            uri, json=data, headers=build_pa_headers(user_ip, 'ru-RU'),
        )
        assert resp.status == expected_code, await resp.read()
        if expected_code == 200:
            assert await resp.json() == {
                'order_id': external_ref,
                'total': DEFAULT_AMOUNT,
                'currency': 'RUB',
                'expires_at': '2018-07-21T17:00:00+03:00',
            }

    assert v2_invoices_create_handler.times_called == 2
    assert mock_invoice_retrieve.times_called == 1
    assert mock_payment_method.times_called == 2
    if response_code == 409:
        assert empty_transactions_update_mock.times_called == 1
    else:
        assert empty_transactions_update_mock.times_called == 2
    assert eda_mock.times_called == 2


@pytest.mark.config(PAYMENTS_EDA_LIST_PAYMENTMETHODS_FROM_CARDSTORAGE=True)
@pytest.mark.parametrize(
    'sum_to_pay,version,pm_id,response_code',
    [
        ('0', 1, 'card-x5a4adedaf78dba6f9c56fee4', 200),
        ('0', 2, 'card-x5a4adedaf78dba6f9c56fee4', 409),
        ('123.4300', 2, 'card-x5a4adedaf78dba6f9c56fee4', 200),
        ('123.4300', 20, 'card-x5a4adedaf78dba6f9c56fee4', 200),
        ('123.4300', 2, 'card-x5aaa7b83fbacea65239f13f3', 200),  # pm id change
        ('123.429999999999', 2, 'card-x5a4adedaf78dba6f9c56fee4', 409),
    ],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
# pylint: disable=too-many-locals
async def test_create_order_conflicts(
        web_app_client,
        mock_cardstorage,
        patch,
        mock_get_order,
        mock_get_payment_types_info,
        available_accounts_mockserver,
        personal_store_mockserver,
        mockserver,
        load_json,
        sum_to_pay,
        version,
        pm_id,
        response_code,
        build_pa_headers,
        empty_transactions_update_mock,
        is_grocery,
        external_ref,
):
    personal_store_mockserver(value=preorder.GROCERY_DEFAULT_TIN)

    await _check_create_order_conflicts(
        web_app_client,
        mock_cardstorage,
        patch,
        mock_get_order,
        mock_get_payment_types_info,
        available_accounts_mockserver,
        mockserver,
        load_json,
        sum_to_pay,
        version,
        pm_id,
        response_code,
        build_pa_headers,
        empty_transactions_update_mock,
        is_grocery,
        external_ref,
    )


@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.config(PAYMENTS_EDA_ATTEMPT_TO_PATCH_EDA_BASE_URL=True)
async def test_no_base_eda_url_without_experiment(
        web_app,
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        mock_get_payment_types_info,
        get_single_stat_by_label_values,
        mockserver,
        patch,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        available_accounts_mockserver,
):
    await _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
    )


@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.config(PAYMENTS_EDA_ATTEMPT_TO_PATCH_EDA_BASE_URL=True)
@GET_BASE_EDA_URL_FROM_EXPERIMENT
async def test_get_base_eda_url_from_experiment(
        web_app,
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        mock_get_payment_types_info,
        get_single_stat_by_label_values,
        mockserver,
        patch,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        available_accounts_mockserver,
):
    order_params = OrderMockParams()
    eda_response = _get_eda_response(order_params.amount)
    mock_eda_doc = eda_doc_mockserver(eda_response)

    await _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        headers=Headers(pa_yandex_uid=consts.DEFAULT_YANDEX_UID),
        eda_doc_base_url=NEW_BASE_URL,
    )

    assert mock_eda_doc.times_called == 0


@pytest.mark.now('2018-07-20T14:00:00Z')
@common.add_experiment(experiment_name=experiments.USE_CARD_ANTIFRAUD)
@pytest.mark.parametrize(
    'ca_status, ca_response, pass_flags, expected_status',
    [
        # user blocked by antifraud
        (
            200,
            {'all_payments_available': False, 'available_cards': []},
            'portal',
            409,
        ),
        # card-antifraud not available
        (429, None, 'portal', 200),
        (500, None, 'portal', 200),
        # device verified
        (
            200,
            {'all_payments_available': True, 'available_cards': []},
            'portal',
            200,
        ),
        # only card verified
        (
            200,
            {
                'all_payments_available': False,
                'available_cards': [{'card_id': VALID_CARD_ID}],
            },
            'portal',
            200,
        ),
        # not portal
        (200, None, 'phonish', 200),
    ],
    ids=[
        'blocked',
        'card-antifraud_not_available_429',
        'card-antifraud_not_available_500',
        'device_verified',
        'card_verified',
        'user_not_portal',
    ],
)
@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
@preorder.GROCERY_TRUST_SERVICE_ENABLED_DISABLED
@preorder.GROCERY_TRUST_SETTINGS
async def test_card_antifraud(
        web_app,
        web_app_client,
        mock_cardstorage,
        mock_card_antifraud,
        eda_doc_mockserver,
        grocery_orders_mockserver,
        mock_get_payment_types_info,
        personal_store_mockserver,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        available_accounts_mockserver,
        ca_status,
        ca_response,
        pass_flags,
        expected_status,
        is_grocery,
        external_ref,
        grocery_billing_service,
        grocery_product_id,
        grocery_trust_settings_enabled,
):
    payment_method = 'card'
    available_payment_types = ['card']
    user_agent = 'ua for card-antifraud'

    @mock_card_antifraud('/v1/payment/availability')
    def _card_antifraud_mock(request, **kwargs):
        assert request.headers['Accept-Language'] == 'ru-RU'
        assert request.headers['User-Agent'] == user_agent
        if ca_status == 200:
            return ca_response
        return mockserver.make_response('', ca_status)

    transactions_eda_service = None
    billing_service = None
    product_id = None
    if is_grocery:
        transactions_eda_service = TRANSACTIONS_EDA_GROCERY_SERVICE
        billing_service = grocery_billing_service
        product_id = grocery_product_id
        personal_store_mockserver(value=preorder.GROCERY_DEFAULT_TIN)

    await _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        payment_method=payment_method,
        payment_method_id=VALID_CARD_ID,
        available_payment_types=available_payment_types,
        status=expected_status,
        headers=Headers(
            pa_ya_taxi_pass_flags=pass_flags, pa_user_agent=user_agent,
        ),
        order_params=OrderMockParams(
            is_grocery=is_grocery, external_ref=external_ref,
        ),
        grocery_orders_mockserver=grocery_orders_mockserver,
        transactions_eda_service=transactions_eda_service,
        billing_service=billing_service,
        product_id=product_id,
    )


@pytest.mark.now('2018-07-20T14:00:00Z')
@common.add_experiment(experiment_name=experiments.USE_CARD_ANTIFRAUD)
@common.add_experiment(experiment_name=experiments.USE_CARD_FILTER_EXP)
@pytest.mark.parametrize(
    'card_filter_status, use_card_filter', [(500, False), (200, True)],
)
@preorder.PARAMETRIZE_EDA_AND_GROCERY_ORDER
@preorder.GROCERY_TRUST_SERVICE_ENABLED_DISABLED
@preorder.GROCERY_TRUST_SETTINGS
async def test_card_filter(
        web_app,
        web_app_client,
        mock_card_antifraud,
        mock_get_payment_types_info,
        mock_cardstorage,
        personal_store_mockserver,
        mock_card_filter,
        grocery_orders_mockserver,
        eda_doc_mockserver,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        available_accounts_mockserver,
        card_filter_status,
        use_card_filter,
        is_grocery,
        external_ref,
        grocery_billing_service,
        grocery_product_id,
        grocery_trust_settings_enabled,
):
    payment_method = 'card'
    available_payment_types = ['card']

    card_filter_payment_methods = load_json('card_filter_filtered_cards.json')

    @mock_card_filter('/v1/filteredcards')
    async def card_filter_mock(request, **kwargs):
        if card_filter_status != 200:
            return mockserver.make_response(
                status=card_filter_status, json={'message': 'error'},
            )
        return card_filter_payment_methods

    @mock_card_antifraud('/v1/payment/availability')
    async def card_antifraud_mock(request, **kwargs):
        # We don't need card-antifraud check if card-filter was used.
        # Return empty list of cards in that case to make sure that
        # test fails if we check card-antifraud by mistake.
        available_cards = (
            [] if use_card_filter else [{'card_id': VALID_CARD_ID}]
        )
        return {
            'all_payments_available': False,
            'available_cards': available_cards,
        }

    transactions_eda_service = None
    billing_service = None
    product_id = None
    if is_grocery:
        transactions_eda_service = TRANSACTIONS_EDA_GROCERY_SERVICE
        billing_service = grocery_billing_service
        product_id = grocery_product_id
        personal_store_mockserver(value=preorder.GROCERY_DEFAULT_TIN)

    await _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        payment_method=payment_method,
        payment_method_id=VALID_CARD_ID,
        available_payment_types=available_payment_types,
        expected_cardstorage_times_called=int(not use_card_filter),
        headers=Headers(pa_ya_taxi_pass_flags='portal'),
        order_params=OrderMockParams(
            is_grocery=is_grocery, external_ref=external_ref,
        ),
        grocery_orders_mockserver=grocery_orders_mockserver,
        transactions_eda_service=transactions_eda_service,
        billing_service=billing_service,
        product_id=product_id,
    )

    assert card_filter_mock.times_called == 1
    assert card_antifraud_mock.times_called == 1


@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.parametrize(
    'payment_method, payment_method_id, '
    'available_payment_types, eats_meta_info, status',
    [
        ('card', VALID_CARD_ID, ['applepay', 'card'], {}, 200),
        (
            'card',
            VALID_CARD_ID,
            ['applepay', 'card'],
            {'payment_method': {'type': 'card', 'id': VALID_CARD_ID}},
            200,
        ),
        (
            'card',
            VALID_CARD_ID,
            ['applepay', 'card'],
            {'payment_method': {'type': 'card', 'id': 'unknown_id'}},
            409,
        ),
        (
            'card',
            VALID_CARD_ID,
            ['applepay', 'card'],
            {'payment_method': {'type': 'applepay'}},
            409,
        ),
        (
            'applepay',
            'applepay-123',
            ['applepay', 'card'],
            {'payment_method': {'type': 'card', 'id': 'unknown_id'}},
            409,
        ),
        (
            'applepay',
            'applepay-123',
            ['applepay', 'card'],
            {'payment_method': {'type': 'applepay'}},
            200,
        ),
    ],
)
@pytest.mark.parametrize('business', [None, 'pharmacy'])
async def test_eats_meta_info(
        web_app,
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        payment_method,
        payment_method_id,
        available_payment_types,
        eats_meta_info,
        status,
        business,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        available_accounts_mockserver,
):
    await _check_create_order(
        web_app_client,
        mock_cardstorage,
        eda_doc_mockserver,
        available_accounts_mockserver,
        mock_get_payment_types_info,
        mockserver,
        load_json,
        build_pa_headers,
        mock_uuid,
        mock_grocery_cart,
        payment_method=payment_method,
        payment_method_id=payment_method_id,
        available_payment_types=available_payment_types,
        eats_meta_info=eats_meta_info,
        status=status,
        order_params=OrderMockParams(business=business),
        service='eats',
    )


@pytest.fixture(autouse=True)
def _corp_int_api_list_payment_methods(load_json, corp_int_api_mock):
    corp_lpm = load_json('corp_int_api_list_payment_methods.json')
    return corp_int_api_mock(corp_lpm)
