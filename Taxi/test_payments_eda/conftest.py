# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
# pylint: disable=invalid-name
import dataclasses
import datetime
import enum
import typing
from unittest import mock
import uuid

import pytest

from taxi.clients import tvm
from taxi.util import dates as date_utils

from payments_eda import consts as service_consts
import payments_eda.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from payments_eda.utils import payment_types
from test_payments_eda import consts
from test_payments_eda import preorder
from test_payments_eda import transactions_eda

DEFAULT_GROCERY_CART_ITEMS_V2 = [
    {
        'info': {
            'item_id': 'item_id',
            'shelf_type': 'store',
            'title': '',
            'refunded_quantity': '0',
        },
        'sub_items': [
            {
                'item_id': 'bfd7526fa5d74eae9e5c034d40235be0-grocery',
                'price': '10.50',
                'full_price': '50',
                'quantity': '1',
                'paid_with_cashback': '39.50',
            },
        ],
    },
]

DEFAULT_ITEM_TITLE = 'item-title-1122'
DEFAULT_CART_ID = 'x5aaa7b83fbacea65239f13f3'

pytest_plugins = ['payments_eda.generated.service.pytest_plugins']


class TransactionsType(enum.Enum):
    eda = 'eda'
    lavka_isr = 'lavka-isr'


@pytest.fixture
def eda_doc_mockserver(mockserver):
    def wrap(data=None, base_url=None):
        base_url = 'eda_superapp' if base_url is None else base_url

        @mockserver.json_handler(f'/{base_url}/internal-api/v1/orders')
        def handler(request):
            assert request.method == 'GET'
            assert 'X-Ya-Service-Ticket' in request.headers
            return data

        return handler

    return wrap


@pytest.fixture
def grocery_orders_mockserver(mockserver):
    def wrap(data=None):
        @mockserver.json_handler('/grocery-orders/internal/v1/get-info')
        def handler(request):
            return data

        return handler

    return wrap


@pytest.fixture
def corp_int_api_mock(mockserver):
    def wrap(response):
        @mockserver.json_handler(
            '/taxi-corp-integration/v1/payment-methods/eats',
        )
        def handler(request):
            headers = {'X-YaRequestId': uuid.uuid4().hex}
            return mockserver.make_response(
                status=200, headers=headers, json=response,
            )

        return handler

    return wrap


@pytest.fixture
def available_accounts_mockserver(mockserver, load_json):
    def wrap(response=None):
        @mockserver.json_handler('/personal_wallet/v1/available-accounts')
        def handler(request):
            nonlocal response
            if response is None:
                response = load_json('personal_wallet_available_accounts.json')
            return mockserver.make_response(status=200, json=response)

        return handler

    return wrap


@pytest.fixture
def personal_store_mockserver(mockserver):
    def wrap(value):
        @mockserver.json_handler('/personal/v1/tins/store')
        def handler(request):
            assert request.json == {'value': value, 'validate': True}

            return {'id': consts.PERSONAL_TIN_ID, 'value': value}

        return handler

    return wrap


@pytest.fixture(autouse=True)
def enable_tvm(monkeypatch):
    async def patched_get_ticket(*args, **kwargs):
        return 'ticket'

    def patched_check_rules(self, dst):
        if self.service_name == 'payments_eda' and dst in (
                'eda_core',
                'personal_wallet',
        ):
            return True
        return False

    monkeypatch.setattr(tvm.TVMClient, 'get_ticket', patched_get_ticket)
    monkeypatch.setattr(tvm.TVMClient, 'check_rules', patched_check_rules)


@pytest.fixture
def build_pa_headers():
    def _wrapper(
            user_ip,
            locale,
            yandex_uid=consts.DEFAULT_YANDEX_UID,
            yandex_login_id=None,
            bound_uids='',
            user_agent=None,
            request_application=None,
            ya_taxi_pass_flags=None,
            ya_taxi_user_id=consts.DEFAULT_USER_ID,
            personal_phone_id=None,
            personal_email_id=None,
    ):
        headers = {
            'X-Ya-User-Ticket': 'ticket-123',
            'X-Yandex-UID': yandex_uid,
            'X-YaTaxi-PhoneId': 'phone_id',
            'X-YaTaxi-UserId': ya_taxi_user_id,
            'X-Yandex-Login': '345',
            'X-YaTaxi-Pass-Flags': 'phonish',
            'X-YaTaxi-User': 'personal_phone_id=phone777',
            'X-YaTaxi-Bound-Uids': bound_uids,
            'X-Request-Language': 'ru_RU',
            'X-Request-Application': 'app=iphone',
            'X-Remote-Ip': user_ip,
        }
        if locale is not None:
            headers['Accept-Language'] = locale
        if user_agent is not None:
            headers['User-Agent'] = user_agent
        if request_application is not None:
            headers['X-Request-Application'] = request_application
        if ya_taxi_pass_flags is not None:
            headers['X-YaTaxi-Pass-Flags'] = ya_taxi_pass_flags
        if yandex_login_id is not None:
            headers['X-Login-Id'] = yandex_login_id

        personal_data = {}
        if personal_phone_id is not None:
            personal_data['personal_phone_id'] = personal_phone_id
        if personal_email_id is not None:
            personal_data['personal_email_id'] = personal_email_id
        if personal_data:
            headers['X-YaTaxi-User'] = ','.join(
                f'{k}={v}' for k, v in personal_data.items()
            )
        return headers

    return _wrapper


@pytest.fixture
def empty_transactions_update_mock(mockserver):
    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def _v2_invoice_update_mock(request):
        return {}

    return _v2_invoice_update_mock


@pytest.fixture
def empty_transactions_create_mock(mockserver):
    @mockserver.json_handler('/transactions-eda/v2/invoice/create')
    def _v2_invoice_create_mock(request):
        return {}

    return _v2_invoice_create_mock


@pytest.fixture()
def mock_uuid(patch):
    def _wrapper(value):
        @patch('uuid.uuid4')
        def new_uuid():
            return mock.Mock(hex=value)

        return new_uuid

    return _wrapper


@pytest.fixture
def mock_get_payment_types_info(patch):
    def _mock(
            request_user_agent=None,
            request_yandex_uid=None,
            request_service=None,
            available_payment_types=None,
            merchant_ids=None,
    ):
        @patch('payments_eda.utils.payment_types.get_payment_types_info')
        async def _mock_get_payment_types_info(
                service: str,
                lat: float,
                lon: float,
                user_agent: str,
                *args,
                **kwargs,
        ):
            nonlocal request_service
            if request_service is None:
                request_service = 'eats'
            assert service == request_service

            assert lon == consts.LOCATION[0]
            assert lat == consts.LOCATION[1]

            nonlocal request_yandex_uid
            if request_yandex_uid is None:
                request_yandex_uid = consts.DEFAULT_YANDEX_UID

            # Using such a check due to the impossibility of
            # importing api_4_0_middleware
            if 'auth_ctx' in kwargs:
                assert kwargs['auth_ctx'].yandex_uid == request_yandex_uid
                assert kwargs['auth_ctx'].yandex_taxi_phoneid == 'phone_id'

            if request_user_agent is not None:
                assert user_agent == request_user_agent

            nonlocal available_payment_types
            if available_payment_types is None:
                available_payment_types = ['card']

            nonlocal merchant_ids
            if merchant_ids is None:
                merchant_ids = ['merchant.ru.yandex.ytaxi.trust']

            return payment_types.PaymentTypeInfo(
                available_payment_types=available_payment_types,
                merchant_ids=merchant_ids,
            )

    return _mock


@pytest.fixture
def mock_get_order(
        grocery_orders_mockserver, mock_grocery_cart, eda_doc_mockserver,
):
    def _mock(
            is_grocery,
            item_id,
            currency='RUB',
            amount='10.50',
            country_iso2='RU',
            business=None,
            card_id=preorder.NO_CARD_ID,
            make_random=False,
            base_url=None,
            grocery_billing_flow='payments_eda',
            billing_settings_version=None,
    ):
        return preorder.mock_get_order_helper(
            grocery_orders_mockserver,
            mock_grocery_cart,
            eda_doc_mockserver,
            is_grocery,
            item_id,
            currency,
            amount,
            card_id=card_id,
            make_random=make_random,
            items=None,
            business=business,
            country_iso2=country_iso2,
            base_url=base_url,
            grocery_billing_flow=grocery_billing_flow,
            billing_settings_version=billing_settings_version,
        )

    return _mock


@pytest.fixture
def mock_grocery_process_receipts(mockserver):
    def _mock(order_id=None, payments=None, refunds=None, return_400=False):
        @mockserver.json_handler(
            '/grocery-orders/internal/v1/process-receipts',
        )
        def _handler(request):
            if return_400:
                return mockserver.make_response('{}', 400)

            if order_id is not None:
                assert request.json == {
                    'order_id': order_id,
                    'payments': payments,
                    'refunds': refunds,
                }
            return {}

        return _handler

    return _mock


@pytest.fixture
def mock_cardstorage_payment_methods(load_json, mock_cardstorage):
    @mock_cardstorage('/v1/payment_methods')
    def handler(request):
        return load_json('cardstorage_payment_methods.json')

    return handler


@pytest.fixture
def mock_blackbox(mockserver):
    data = {}

    @mockserver.json_handler('/blackbox/blackbox')
    def _handler(request):
        return {'users': [{'aliases': {'13': context.get_payer_login()}}]}

    class Context:
        def set_payer_login(self, login):
            data['payer_login'] = login

        def get_payer_login(self):
            return data.get('payer_login', 'payer_login')

    context = Context()
    return context


@pytest.fixture
def mock_user_state(mockserver):
    data = {}

    @mockserver.json_handler('/user-state/internal/v1/last-payment-methods')
    def _handler(request):
        expected = {
            'flows': [
                {
                    'flow_type': service_consts.FLOW_TYPE_ORDER,
                    'payment_method': {
                        'type': data['payment_method'],
                        'id': data['payment_method_id'],
                    },
                },
            ],
        }

        assert request.json == expected
        return {}

    class Context:
        def set_payment(self, *, payment_method, payment_method_id):
            data['payment_method'] = payment_method
            data['payment_method_id'] = payment_method_id

    context = Context()
    return context


@pytest.fixture
def mock_invoice_create(mockserver, mock_blackbox):
    def _wrapper(
            order_id: str,
            transaction_service: str,
            payment_method: str,
            payment_method_id: str,
            yandex_uid: str,
            taxi_user_id: str,
            transactions_type: TransactionsType = TransactionsType.eda,
            personal_email_id: typing.Optional[str] = None,
            personal_phone_id: typing.Optional[str] = None,
            billing_service: typing.Optional[str] = None,
    ):
        host = 'transactions-eda'
        if transactions_type == TransactionsType.lavka_isr:
            host = 'transactions-lavka-isr'

        @mockserver.json_handler(f'/{host}/v2/invoice/create')
        def _mock(request):
            pass_params = {}
            nonlocal billing_service
            if billing_service is None:
                billing_service = 'food_payment'
            if payment_method == 'corp' and payment_method_id.startswith(
                    'badge:',
            ):
                billing_service = 'food_payment_badge'
            elif payment_method == 'corp':
                pass_params = {
                    'user_info': {
                        'accept_language': 'ru-RU',
                        'is_portal': False,
                        'personal_phone_id': 'phone777',
                    },
                }
                billing_service = 'food_payment_corp'
            elif payment_method == 'personal_wallet':
                billing_service = 'food_payment_wallet'

            wallet_account = {
                'id': (
                    'wallet/yataxi'
                    if consts.VALID_WALLET_ID.startswith('wallet_id/')
                    else consts.VALID_WALLET_ID
                ),
            }

            transactions_payment_method = payment_method
            if payment_method == 'corp' and payment_method_id.startswith(
                    'badge:',
            ):
                transactions_payment_method = 'badge'

            payments = [
                transactions_eda.get_payment(
                    mock_blackbox,
                    wallet_account,
                    transactions_payment_method,
                    payment_method_id,
                ),
            ]

            invoice_due = date_utils.localize(
                datetime.datetime.strptime(
                    '2018-07-20T14:10:00', '%Y-%m-%dT%H:%M:%S',
                ),
            ).isoformat()

            personal = {}
            if personal_phone_id is not None:
                personal['personal_phone_id'] = personal_phone_id
            if personal_email_id is not None:
                personal['personal_email_id'] = personal_email_id

            expected_data = {
                'billing_service': billing_service,
                'currency': 'RUB',
                'id': order_id,
                'invoice_due': invoice_due,
                'pass_params': pass_params,
                'user_ip': consts.USER_IP,
                'yandex_uid': yandex_uid,
                'external_user_info': {
                    'user_id': taxi_user_id,
                    'origin': 'taxi',
                },
                'service': transaction_service,
                'payments': payments,
                **personal,
            }

            assert request.json == expected_data
            return {}

        return _mock

    return _wrapper


@dataclasses.dataclass
class FiscalReceiptInfo:
    title: str
    vat: str
    personal_tin_id: str


@dataclasses.dataclass
class TransactionItem:
    item_id: str = '123'
    price: str = consts.DEFAULT_AMOUNT
    quantity: str = '1'
    product_id: str = 'eda_61664402_ride'
    fiscal_receipt_info: typing.Optional[FiscalReceiptInfo] = None


@pytest.fixture
def mock_invoice_update(mock_blackbox, mockserver):
    def wrap(
            payment_method,
            payment_method_id,
            items: typing.List[TransactionItem],
            transactions_type: TransactionsType = TransactionsType.eda,
    ):
        host = 'transactions-eda'
        if transactions_type == TransactionsType.lavka_isr:
            host = 'transactions-lavka-isr'

        @mockserver.json_handler(f'/{host}/v2/invoice/update')
        def handler(request):
            wallet_account = {
                'id': (
                    'wallet/yataxi'
                    if consts.VALID_WALLET_ID.startswith('wallet_id/')
                    else consts.VALID_WALLET_ID
                ),
            }

            transactions_payment_method = payment_method
            if payment_method == 'corp' and payment_method_id.startswith(
                    'badge:',
            ):
                transactions_payment_method = 'badge'

            payments = [
                transactions_eda.get_payment(
                    mock_blackbox,
                    wallet_account,
                    transactions_payment_method,
                    payment_method_id,
                ),
            ]

            assert len(request.json['items_by_payment_type']) == 1
            request_items = request.json['items_by_payment_type'][0]['items']
            data_items = []
            for item in items:
                to_add = dataclasses.asdict(item)
                if to_add['fiscal_receipt_info'] is None:
                    to_add.pop('fiscal_receipt_info')
                data_items.append(to_add)

            assert request_items == data_items
            assert (
                request.json['operation_id'] == f'create:{consts.DEFAULT_UUID}'
            )
            assert request.json['payments'] == payments

            return {}

        return handler

    return wrap


@pytest.fixture
def mock_grocery_cart(mockserver):
    @mockserver.json_handler('/grocery-cart/internal/v1/cart/retrieve/raw')
    def _mock_retrieve_raw(request):
        return context.cart_response

    class Context:
        def __init__(self):
            self.cart_response = {
                'cart_id': 'a49609bd-741d-410e-9f04-476f46ad43c7',
                'cart_version': 1,
                'user_type': 'yandex_taxi',
                'user_id': 'user-id',
                'checked_out': True,
                'exists_order_id': False,
                'delivery_type': 'eats_dispatch',
                'total_discount_template': '0 $SIGN$$CURRENCY$',
                'total_item_discounts_template': '0 $SIGN$$CURRENCY$',
                'total_promocode_discount_template': '0 $SIGN$$CURRENCY$',
                'items_full_price_template': '0 $SIGN$$CURRENCY$',
                'items_price_template': '0 $SIGN$$CURRENCY$',
                'full_total_template': '0 $SIGN$$CURRENCY$',
                'client_price_template': '0 $SIGN$$CURRENCY$',
                'client_price': '0',
                'total_discount': '0',
                'items': [],
            }

        def drop_items_v2(self):
            if 'items_v2' in self.cart_response:
                del self.cart_response['items_v2']

        def set_items(self, item_id, amount, currency='RUB'):
            self.cart_response['items'] = [
                {
                    'currency': currency,
                    'id': item_id,
                    'vat': '20.00',
                    'title': DEFAULT_ITEM_TITLE,
                    'price': amount,
                    'price_template': f'{str(amount)} $SIGN$$CURRENCY$',
                    'quantity': '1',
                    'refunded_quantity': '0',
                    'product_key': {'id': 'abc', 'shelf_type': 'store'},
                },
            ]

        def set_payment_method(self, pm_id):
            self.cart_response['payment_method_id'] = pm_id
            self.cart_response['payment_method_type'] = 'card'
            self.cart_response['payment_method_discount'] = False

    context = Context()
    return context
