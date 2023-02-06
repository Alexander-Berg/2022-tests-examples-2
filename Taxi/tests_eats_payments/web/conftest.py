import datetime as dt
import typing
import uuid

import pytest

from tests_eats_payments import consts
from tests_eats_payments import helpers
from tests_eats_payments import models


@pytest.fixture(name='mock_transactions_invoice_create')
def _mock_transactions_invoice_create(mockserver, load_json):
    def _inner(
            payment_type: str = 'card',
            payment_method_id: str = '123',
            billing_service: str = 'food_payment',
            service: str = consts.DEFAULT_SERVICE,
            billing_id: typing.Optional[str] = None,
            payer_login: typing.Optional[str] = None,
            personal_phone_id: typing.Optional[str] = None,
            pass_params: typing.Optional[dict] = None,
            payment_timeout: typing.Optional[int] = None,
            invoice_create_response=None,
            complement_payment: typing.Optional[models.Complement] = None,
            app_metrica_device_id: str = None,
            trust_afs_params: dict = None,
            trust_developer_payload: str = None,
            without_trust_orders: bool = None,
    ):
        if payment_type == 'corp':
            billing_id = ''

        # pylint: disable=invalid-name
        @mockserver.json_handler('/transactions-eda/v2/invoice/create')
        def transactions_create_invoice_handler(request):
            if invoice_create_response is not None:
                return mockserver.make_response(**invoice_create_response)

            payment_method = {
                'method': payment_method_id,
                'type': payment_type,
            }

            if billing_id is not None:
                payment_method['billing_id'] = billing_id

            if payment_type == 'badge':
                assert payer_login is not None
                payment_method['payer_login'] = payer_login

            payments = [payment_method]
            if complement_payment is not None:
                payments.append(complement_payment.get_transaction_payment())

            expected_request_body = {
                'id': 'test_order',
                'invoice_due': '2020-08-12T07:30:00+00:00',
                'antifraud_payload': {
                    'app_metrica_device_id': app_metrica_device_id,
                    'login_id': 'test_login_id',
                },
                'billing_service': billing_service,
                'payments': payments,
                'currency': 'RUB',
                'yandex_uid': '100500',
                'pass_params': pass_params or {},
                'user_ip': '127.0.0.1',
                'login_id': 'test_login_id',
                'service': service,
            }
            if without_trust_orders is not None:
                expected_request_body[
                    'without_trust_orders'
                ] = without_trust_orders
            if personal_phone_id is not None:
                expected_request_body['personal_phone_id'] = personal_phone_id
            if trust_afs_params is not None:
                expected_request_body['trust_afs_params'] = trust_afs_params
            if trust_developer_payload is not None:
                expected_request_body[
                    'trust_developer_payload'
                ] = trust_developer_payload
            if payment_timeout is not None:
                expected_request_body['payment_timeout'] = payment_timeout

            print(request.json)
            print(expected_request_body)
            assert request.json == expected_request_body
            return {}

        return transactions_create_invoice_handler

    return _inner


@pytest.fixture
def mock_transactions(mockserver):
    @mockserver.json_handler('/transactions-eda/v2/invoice/create')
    def _mock_create(request):
        return {}

    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def _mock_update(request):
        return {}

    class Context:
        def create_times_called(self):
            return _mock_create.times_called

        def update_times_called(self):
            return _mock_update.times_called

    context = Context()
    return context


@pytest.fixture
def mock_cargo_payments_create(mockserver):
    def _inner(
            expected_status=200,
            expected_payment_id=None,
            expected_request=None,
            error=None,
    ):
        if expected_payment_id is None:
            expected_payment_id = str(uuid.uuid4())

        @mockserver.json_handler('/cargo-payments/v1/payment/create')
        def _mock_create(request):
            if expected_request is not None:
                assert request.json == expected_request
            if error is not None:
                raise error
            if expected_status == 200:
                return {'payment_id': expected_payment_id, 'revision': 123}
            return mockserver.make_response(
                status=expected_status,
                json={'code': str(expected_status), 'message': 'some error'},
            )

        return _mock_create

    return _inner


@pytest.fixture
def mock_cargo_payments_update(mockserver):
    def _inner(expected_status=200, expected_request=None, error=None):
        @mockserver.json_handler('/cargo-payments/v1/payment/update')
        def _mock_update(request):
            if expected_request is not None:
                assert request.json == expected_request
            if error is not None:
                raise error
            if expected_status == 200:
                return mockserver.make_response(status=200)
            return mockserver.make_response(
                status=expected_status,
                json={'code': str(expected_status), 'message': 'some error'},
            )

        return _mock_update

    return _inner


@pytest.fixture
def mock_cargo_payments_refund(mockserver):
    def _inner(expected_status=200, expected_request=None, error=None):
        @mockserver.json_handler('/cargo-payments/v1/payment/refund')
        def _mock_update(request):
            if expected_request is not None:
                assert request.json == expected_request
            if error is not None:
                raise error
            if expected_status == 200:
                return mockserver.make_response(status=200)
            return mockserver.make_response(
                status=expected_status,
                json={'code': str(expected_status), 'message': 'some error'},
            )

        return _mock_update

    return _inner


@pytest.fixture(name='mock_user_state_save_last_payment')
def _mock_user_state_save_last_payment(mockserver, load_json):
    def _inner(
            payment_type: str = 'card',
            payment_method_id: str = '123',
            validate_request=False,
            save_last_payment_response=None,
            error=None,
            service=consts.DEFAULT_SERVICE,
    ):
        # pylint: disable=invalid-name
        @mockserver.json_handler(
            '/user-state/internal/v1/last-payment-methods',
        )
        def user_state_save_last_payment_handler(request):
            if save_last_payment_response is not None:
                return mockserver.make_response(**save_last_payment_response)

            if error is not None:
                raise error

            if validate_request:
                expected_request_body = {
                    'flows': [
                        {
                            'flow_type': 'order',
                            'payment_method': {
                                'id': payment_method_id,
                                'type': payment_type,
                            },
                        },
                    ],
                }
                assert request.json == expected_request_body
                assert request.query['service'] == service

            return {}

        return user_state_save_last_payment_handler

    return _inner


@pytest.fixture(name='mock_blackbox')
def _mock_blackbox(mockserver):
    @mockserver.json_handler('/blackbox')
    def blackbox_handler(request):
        assert dict(request.args) == {
            'uid': '100500',
            'userip': '127.0.0.1',
            'method': 'userinfo',
            'format': 'json',
            'dbfields': 'subscription.suid.669',
            'aliases': 'all',
        }
        return {
            'users': [
                {
                    'aliases': {'13': 'foo'},
                    'dbfields': {'subscription.suid.669': '1'},
                    'uid': {'hosted': False, 'lite': False, 'value': '100500'},
                },
            ],
        }

    return blackbox_handler


# pylint: disable=invalid-name
@pytest.fixture(name='check_no_payment_callback')
def check_no_payment_callback_fixture(stq):
    def _inner(
            task_id: str = 'some_task_id', eta: dt.datetime = None, **kwargs,
    ):
        helpers.check_callback_mock(
            callback_mock=stq.eats_payments_check_no_payment,
            task_id=task_id,
            queue='eats_payments_check_no_payment',
            eta=eta,
            **kwargs,
        )

    return _inner


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'tvm2_eda_core: mark test to use eda_core TVM2 ticket',
    )
    config.addinivalue_line(
        'markers',
        'tvm2_eats_corp_orders: mark test to use eats_corp_orders TVM2 ticket',
    )


@pytest.fixture(name='build_headers_for_create_order')
def build_headers_for_create_order_fixture(request, taxi_config):
    def _inner(headers: typing.Optional[dict] = None):
        headers = headers or consts.BASE_HEADERS
        for m in request.node.iter_markers():
            if m.name == 'tvm2_eda_core':
                taxi_config.set_values(
                    {
                        'TVM_ENABLED': True,
                        'TVM_RULES': [
                            {'src': 'eda_core', 'dst': 'eats-payments'},
                        ],
                    },
                )
                headers['X-Ya-Service-Ticket'] = consts.MOCK_EDA_CORE_TICKET
                headers['X-Ya-User-Ticket'] = consts.MOCK_EDA_CORE_TICKET
                return headers
            elif m.name == 'tvm2_eats_corp_orders':
                taxi_config.set_values(
                    {
                        'TVM_ENABLED': True,
                        'TVM_RULES': [
                            {
                                'src': 'eats-corp-orders',
                                'dst': 'eats-payments',
                            },
                        ],
                    },
                )
                # taxi_config.set_values(configs.TVM_CONFIGS)
                headers[
                    'X-Ya-Service-Ticket'
                ] = consts.MOCK_EATS_CORP_ORDERS_TICKET
                headers[
                    'X-Ya-User-Ticket'
                ] = consts.MOCK_EATS_CORP_ORDERS_TICKET
                return headers
        return headers

    return _inner


@pytest.fixture(name='check_create_order')
def check_create_order_fixture(
        taxi_eats_payments, build_headers_for_create_order,
):
    async def _inner(
            payment_type: str,
            items: typing.List[dict] = None,
            payment_method_id: str = consts.TEST_PAYMENT_ID,
            headers: typing.Optional[dict] = None,
            additional_request_part: typing.Optional[dict] = None,
            response_status: int = 200,
            service: str = consts.DEFAULT_SERVICE,
            ttl: int = None,
            business=None,
    ):
        additional_payload = {}
        if additional_request_part is not None:
            additional_payload = additional_request_part
        if items is None:
            items = [helpers.make_item(item_id='big_mac', amount='2.00')]

        payload = {
            'id': consts.TEST_ORDER_ID,
            'currency': 'RUB',
            'mcc': 100500,
            'revision': 'abcd',
            'payment_method': {'id': payment_method_id, 'type': payment_type},
            'items': items,
            'service': service,
            'originator': consts.DEFAULT_ORIGINATOR,
            **additional_payload,
        }

        if ttl is not None:
            payload['ttl'] = ttl

        headers = build_headers_for_create_order(headers)
        response = await taxi_eats_payments.post(
            'v1/orders/create', json=payload, headers=headers,
        )
        assert response.status == response_status

    return _inner


@pytest.fixture(name='check_create_order_v2')
def check_create_order_v2_fixture(
        taxi_eats_payments, build_headers_for_create_order,
):
    async def _inner(
            order_id: str,
            revision: str,
            payment_type: str,
            payment_method_id: str = consts.TEST_PAYMENT_ID,
            headers: typing.Optional[dict] = None,
            additional_request_part: typing.Optional[dict] = None,
            service: str = consts.DEFAULT_SERVICE,
            response_status: int = 200,
    ):
        additional_payload = {}
        if additional_request_part is not None:
            additional_payload = additional_request_part

        payload = {
            'id': order_id,
            'payment_method': {'id': payment_method_id, 'type': payment_type},
            'currency': 'RUB',
            'mcc': 100500,
            'service': service,
            'revision': revision,
            **additional_payload,
        }

        headers = build_headers_for_create_order(headers)
        response = await taxi_eats_payments.post(
            'v2/orders/create', json=payload, headers=headers,
        )
        assert response.status == response_status
        return response

    return _inner


@pytest.fixture(name='mock_personal')
def _mock_personal(mockserver):
    def _inner(
            data_type: str,
            personal_id: typing.Optional[str] = None,
            value: typing.Optional[str] = None,
            personal_response=None,
            error=None,
            **kwargs,
    ):
        # pylint: disable=invalid-name
        @mockserver.json_handler(f'/personal/v1/{data_type}/retrieve')
        def personal_retrieve_handler(request):
            if personal_response is not None:
                return mockserver.make_response(**personal_response)

            if error is not None:
                raise error

            if personal_id is not None:
                assert request.json == {
                    'id': personal_id,
                    'primary_replica': False,
                }
            return {'id': personal_id, 'value': value}

        return personal_retrieve_handler

    return _inner


@pytest.fixture(name='mock_personal_retrieve_tins')
def _mock_personal_retrieve_tins(mock_personal):
    async def _inner(
            personal_id: str = 'personal-tin-id', value: str = '1234567890',
    ):
        return mock_personal('tins', personal_id=personal_id, value=value)

    return _inner


@pytest.fixture(name='mock_retrieve_invoice_retrieve')
def _mock_retrieve_invoice_retrieve(mock_transactions_invoice_retrieve):
    def _inner(*args, **kwargs):
        # so that the data in test file does not interfere with test cases
        extra = {
            'sum_to_pay': [],
            'held': [],
            'cleared': [],
            'debt': [],
            **kwargs,
        }
        return mock_transactions_invoice_retrieve(*args, **extra)

    return _inner


@pytest.fixture(name='mock_cardstorage')
def _mock_cardstorage(mockserver):
    def _inner():
        # pylint: disable=invalid-name
        @mockserver.json_handler('/cardstorage/v1/card')
        def cardstorage_card_handler(request):
            return {
                'bin': '424242',
                'card_id': '',
                'billing_card_id': '',
                'permanent_card_id': '',
                'currency': 'RUB',
                'expiration_month': 12,
                'expiration_year': 2022,
                'number': '',
                'owner': '',
                'possible_moneyless': False,
                'region_id': '',
                'regions_checked': [],
                'system': '',
                'valid': True,
                'bound': True,
                'unverified': False,
                'busy': True,
                'busy_with': [],
                'from_db': True,
            }

        return cardstorage_card_handler

    return _inner
