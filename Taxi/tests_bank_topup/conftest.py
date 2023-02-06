import copy
import typing as tp

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_audit_logger.mock_bank_audit import bank_audit  # noqa: F401
from bank_topup_plugins import *  # noqa: F403 F401

from tests_bank_topup import common

try:
    import library.python.resource  # noqa: F401

    _IS_ARCADIA = True
except ImportError:
    _IS_ARCADIA = False

if _IS_ARCADIA:
    import logging
    import dataclasses

    @pytest.fixture(autouse=True)
    async def service_logs(taxi_bank_topup):
        levels = {
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'CRITICAL': logging.CRITICAL,
        }

        # Each log record is captured as a dictionary,
        # so we need to turn it back into a string
        def serialize_tskv(row):
            # these two will only lead to data duplication
            skip = {'timestamp', 'level'}

            # reorder keys so that 'text' is always in front
            keys = list(row.keys())
            keys.remove('text')
            keys.insert(0, 'text')

            return '\t'.join([f'{k}={row[k]}' for k in keys if k not in skip])

        async with taxi_bank_topup.capture_logs() as capture:
            # This hack tricks the client into thinking that
            # caches still need to be invalidated on the first call
            # so as not to break tests that depend on this behaviour
            # pylint: disable=protected-access
            taxi_bank_topup._client._state_manager._state = (
                dataclasses.replace(
                    # pylint: disable=protected-access
                    taxi_bank_topup._client._state_manager._state,
                    caches_invalidated=False,
                )
            )

            @capture.subscribe()
            # pylint: disable=unused-variable
            def log(**row):
                logging.log(
                    levels.get(row['level'], logging.DEBUG),
                    serialize_tskv(row),
                )

            yield capture


@pytest.fixture
def trust_mock(mockserver):
    class Context:
        def __init__(self):
            self.basket_info_handler = None
            self.unhold_handler = None
            self.clear_handler = None

            self.basket = copy.deepcopy(common.TRUST_BASKET_INFO)

        def set_payment_status(self, status):
            self.basket['payment_status'] = status

        def set_card_number(self, card_number):
            self.basket['user_account'] = card_number

        def set_rrn(self, rrn):
            self.basket['rrn'] = rrn

    context = Context()

    @mockserver.json_handler(
        r'/bank-trust-payments/trust-payments/v2/payments/'
        r'(?P<purchase_token>\w+)',
        regex=True,
    )
    def _basket_info_handler(request, purchase_token):
        assert request.method == 'GET'
        assert request.headers['X-Uid']
        if purchase_token != context.basket['purchase_token']:
            return mockserver.make_response(
                status=404, json={'status': 'error'},
            )
        return mockserver.make_response(status=200, json=context.basket)

    @mockserver.json_handler(
        '/bank-trust-payments/trust-payments/v2/payment-methods',
    )
    def _lpm_handler(request):
        response = {
            'status': 'success',
            'bound_payment_methods': [
                {
                    'account': 'w/10d35034-d481-5b2e-aaf6-c8531af9486f',
                    'currency': 'RUB',
                    'balance': '100941.01',
                    'id': (
                        'yandex_account-w/10d35034-d481-5b2e-aaf6-c8531af9486f'
                    ),
                },
                {
                    'region_id': 225,
                    'last_service_paid_ts': 1630400152.643436,
                    'payment_method': 'card',
                    'payment_system': 'MasterCard',
                    'id': 'card-xa2a55b59db7f376e2b610229',
                    'card_bank': 'RBS BANK (ROMANIA), S.A.',
                },
            ],
        }

        return mockserver.make_response(status=200, json=response)

    @mockserver.json_handler(
        r'/bank-trust-payments/trust-payments/v2/'
        r'payments/(?P<purchase_token>\w+)/unhold',
        regex=True,
    )
    def _unhold_handler(request, purchase_token):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        r'/bank-trust-payments/trust-payments/v2/'
        r'payments/(?P<purchase_token>\w+)/clear',
        regex=True,
    )
    def _clear_handler(request, purchase_token):
        return mockserver.make_response(status=200)

    context.basket_info_handler = _basket_info_handler
    context.unhold_handler = _unhold_handler
    context.clear_handler = _clear_handler

    return context


@pytest.fixture
def bank_core_statement_mock(mockserver):
    def make_response_balance(wallet_id=None, agreement_id=None):
        assert (wallet_id is None) != (agreement_id is None)
        credit_limit_template = {
            'period_start': '2020-08-01T00:00:00+00:00',
            'period': 'MONTH',
            'threshold': {'amount': '20.00', 'currency': 'RUB'},
            'remaining': {'amount': '0.00', 'currency': 'RUB'},
        }

        money_template = {'amount': '20.00', 'currency': 'RUB'}

        balance_template: tp.Dict[str, tp.Any] = {
            'balance': money_template,
            'debit_limit': [],
            'credit_limit': [],
            'public_agreement_id': 'test_agreement_id',
        }

        root_key = None
        balance_id_key = None
        balance_id = None
        if wallet_id:
            balance_id_key = 'id'
            root_key = 'wallets'
            balance_id = wallet_id
        if agreement_id:
            balance_id_key = 'agreement_id'
            root_key = 'agreements'
            balance_id = agreement_id
        balance_template.update({balance_id_key: balance_id})

        if balance_id == 'many_limits':
            credit_limits = []
            for i in [54, 157.03, 10.23, 157, 9999.00, 10.1]:
                money_template['amount'] = str(i)
                credit_limit_template['remaining'] = money_template
                credit_limits.append(credit_limit_template)
            balance_template['credit_limit'] = credit_limits
            return {root_key: [balance_template]}
        if balance_id == 'bad_id':
            return {root_key: []}
        if balance_id == 'money_less_max_limit':
            remaining = money_template.copy()
            remaining['amount'] = str(5)
            credit_limit_template['remaining'] = remaining
            balance_template['credit_limit'].append(credit_limit_template)
            balance_template['balance']['amount'] = str(15)
            return {root_key: [balance_template]}
        if balance_id == 'no_limits':
            return {root_key: [balance_template]}
        if balance_id == 'different_id':
            balance_template[balance_id_key] = 'new_id'
            return {root_key: [balance_template]}
        if balance_id == 'max_limit_less_balance':
            balance_template['credit_limit'].append(credit_limit_template)
            balance_template['balance']['amount'] = str(20)
            return {root_key: [balance_template]}
        if balance_id == 'remaining_less_threshold':
            credit_limit_template['remaining'] = money_template.copy()
            threshold = money_template.copy()
            threshold['amount'] = str(25.00)
            credit_limit_template['threshold'] = threshold
            balance_template['credit_limit'].append(credit_limit_template)
            balance_template['balance']['amount'] = str(5)
            return {root_key: [balance_template]}
        if balance_id == 'check_status':
            return mockserver.make_response(
                status=context.http_status_code,
                json={'code': 'error_code', 'message': 'error_message'},
            )
        return {root_key: []}

    class Context:
        def __init__(self):
            self.response = {'status': 'SUCCESS'}
            self.http_status_code = 200
            self.wallets_balance_handler = None
            self.agreements_balance_handler = None
            self.balance_get_response = None
            self.bad_response_status = None

        def set_response(self, response):
            self.response = response

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_balance_get_response(self, resp):
            self.balance_get_response = resp

        def balance_handler_has_calls(self):
            return (
                self.wallets_balance_handler.has_calls
                != self.agreements_balance_handler.has_calls
            )

    context = Context()

    @mockserver.json_handler(
        '/bank-core-statement/v1/wallets/balance/get', prefix=True,
    )
    def _mock_get_wallets_balance(request):
        if context.bad_response_status is not None:
            return mockserver.make_response(
                status=context.bad_response_status,
                json={'code': '', 'message': ''},
            )
        if context.balance_get_response is None:
            return make_response_balance(wallet_id=request.query['wallet_id'])
        return context.balance_get_response

    @mockserver.json_handler(
        '/bank-core-statement/v1/agreements/balance/get', prefix=True,
    )
    def _mock_get_agreements_balance(request):
        if context.bad_response_status is not None:
            return mockserver.make_response(
                status=context.bad_response_status,
                json={'code': '', 'message': ''},
            )
        if context.balance_get_response is None:
            return make_response_balance(
                agreement_id=request.query['agreement_id'],
            )
        return context.balance_get_response

    context.wallets_balance_handler = _mock_get_wallets_balance
    context.agreements_balance_handler = _mock_get_agreements_balance

    return context


@pytest.fixture
def bank_core_accounting_mock(mockserver):
    class Context:
        def __init__(self):
            self.response = {'status': 'COMPLETED'}
            self.http_status_code = 200
            self.wallet_topup_save_handler = None
            self.balance_watchdog_save_handler = None
            self.balance_watchdog_save_exp_req = None

        def set_response(self, response):
            self.response = response

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_expected_watchdog_request(
                self,
                session_uid=common.DEFAULT_YABANK_SESSION_UUID,
                bank_uid=common.DEFAULT_YANDEX_BUID,
                idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
                agreement_id=common.DEFAULT_PUBLIC_AGREEMENT_ID,
                enable=True,
                threshold_currency=common.DEFAULT_CURRENCY,
                threshold_amount=common.DEFAULT_AMOUNT,
        ):
            self.balance_watchdog_save_exp_req = {
                'headers': {
                    'X-YaBank-SessionUUID': session_uid,
                    'X-Yandex-BUID': bank_uid,
                    'X-Idempotency-Token': idempotency_token,
                },
                'body': {
                    'agreement_id': agreement_id,
                    'enable': enable,
                    'threshold': {
                        'currency': threshold_currency,
                        'amount': threshold_amount,
                    },
                },
            }

    context = Context()

    @mockserver.json_handler(
        '/bank-core-accounting/v1/wallets/topup/save', prefix=False,
    )
    def _wallet_topup_save_handler(request):
        for header in ['X-YaBank-SessionUUID', 'X-Remote-IP', 'X-Yandex-BUID']:
            assert header in request.headers

        assert request.headers['X-Remote-IP'] != ''

        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    @mockserver.json_handler(
        '/bank-core-accounting/v1/balance/watchdog/save', prefix=False,
    )
    def _balance_watchdog_save_handler(request):
        for header in [
                'X-YaBank-SessionUUID',
                'X-Yandex-BUID',
                'X-Idempotency-Token',
        ]:
            assert (
                request.headers[header]
                == context.balance_watchdog_save_exp_req['headers'][header]
            )

        assert request.json == context.balance_watchdog_save_exp_req['body']

        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    context.wallet_topup_save_handler = _wallet_topup_save_handler
    context.balance_watchdog_save_handler = _balance_watchdog_save_handler

    return context


@pytest.fixture
def bank_core_agreement_mock(mockserver):
    class Context:
        def __init__(self):
            self.accessors_response = {
                'accessors': [
                    {
                        'accessor_id': common.TEST_WALLET_ID,
                        'buid': common.DEFAULT_YANDEX_BUID,
                        'agreement_id': common.DEFAULT_AGREEMENT_ID,
                        'accessor_type': 'WALLET',
                        'currency': 'RUB',
                        'public_agreement_id': (
                            common.DEFAULT_PUBLIC_AGREEMENT_ID
                        ),
                    },
                ],
            }
            self.agreement_response = {
                'agreement_id': 'private_123456',
                'buid': common.DEFAULT_YANDEX_BUID,
                'public_agreement_id': common.DEFAULT_PUBLIC_AGREEMENT_ID,
                'product': 'WALLET',
                'currency': 'RUB',
            }
            self.http_status_code = 200
            self.get_accessor_handler = None
            self.get_agreement_handler = None

        def set_accessors_response(self, response):
            self.accessors_response = response

        def set_agreement_response(self, response):
            self.agreement_response = response

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/bank-core-agreement/v1/accessor/list', prefix=False,
    )
    def _get_accessor_handler(request):
        assert request.headers.get('X-Yandex-BUID')

        return mockserver.make_response(
            status=context.http_status_code, json=context.accessors_response,
        )

    @mockserver.json_handler(
        '/bank-core-agreement/v1/agreement/get-by-public-id', prefix=False,
    )
    def _get_agreement_handler(request):
        assert 'X-Yandex-BUID' in request.headers
        assert 'public_agreement_id' in request.query

        return mockserver.make_response(
            status=context.http_status_code, json=context.agreement_response,
        )

    context.get_accessor_handler = _get_accessor_handler
    context.get_agreement_handler = _get_agreement_handler

    return context


@pytest.fixture
def bank_applications_mock(mockserver):
    def get_application_status(application_id):
        if application_id == common.APPLICATION_ID_NOEXIST:
            return mockserver.make_response(
                status=context.http_status_code,
                json={'code': 'error_code', 'message': 'error_message'},
            )
        if application_id == common.APPLICATION_ID_CREATED:
            return {'status': 'CREATED', 'type': context.type}
        if application_id == common.APPLICATION_ID_PROCESSING:
            return {'status': 'PROCESSING', 'type': context.type}
        if application_id == common.APPLICATION_ID_FAILED:
            return {'status': 'FAILED', 'type': context.type}
        if application_id == common.APPLICATION_ID_SUCCESS:
            return {'status': 'SUCCESS', 'type': context.type}
        return {'status': 'CREATED', 'type': context.type}

    class Context:
        def __init__(self):
            self.response = {'status': 'SUCCESS', 'type': 'DIGITAL_CARD_ISSUE'}
            self.http_status_code = 200
            self.application_status_handler = None
            self.type = 'DIGITAL_CARD_ISSUE'

        def set_response(self, response):
            self.response = response

        def set_application_type(self, app_type):
            self.type = app_type

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/bank-applications/v1/applications/v1/get_application_status',
        prefix=True,
    )
    def _mock_get_application_status(request):
        if 'X-Yandex-BUID' not in request.headers:
            return mockserver.make_response(
                status=500, json={'code': '', 'message': ''},
            )
        return get_application_status(request.json.get('application_id'))

    context.application_status_handler = _mock_get_application_status
    return context


@pytest.fixture(autouse=True)
def bank_core_client_mock(mockserver):
    class Context:
        def __init__(self):
            self.response = {'auth_level': 'KYC', 'phone_number': '1'}
            self.http_status_code = 200
            self.client_auth_level_handler = None
            self.bad_response_code = None

        def set_response(self, response):
            self.response = response

        def set_auth_level(self, auth_level):
            self.response['auth_level'] = auth_level

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/bank-core-client/v1/client/info/get', prefix=True,
    )
    def _mock_get_client_auth_level(request):
        if context.bad_response_code:
            return mockserver.make_response(
                status=context.bad_response_code,
                json={'code': str(context.bad_response_code), 'message': '-'},
            )
        buid = request.headers['X-Yandex-BUID']
        if buid == 'bad_buid':
            context.http_status_code = 404
            context.response = {
                'code': 'error_code',
                'message': 'error_message',
            }
        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    context.client_auth_level_handler = _mock_get_client_auth_level

    return context


@pytest.fixture(autouse=True)
def bank_risk(mockserver):
    class Context:
        def __init__(self):
            self.risk_calculation_handler = None
            self.http_status_code = 200
            self.response = {
                'resolution': 'ALLOW',
                'action': [],
                'af_decision_id': 'af_decision_id',
            }

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_response(self, resolution, actions):
            self.response = {
                'resolution': resolution,
                'action': actions,
                'af_decision_id': 'af_decision_id',
            }

    context = Context()

    @mockserver.json_handler('/bank-risk/risk/calculation/direct_credit_topup')
    def _risk_calculation_handler(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    context.risk_calculation_handler = _risk_calculation_handler

    return context


@pytest.fixture(autouse=True)
def bank_userinfo(mockserver):
    class Context:
        def __init__(self):
            self.get_antifraud_info_handler = None
            self.http_status_code = 200
            self.response = {
                'antifraud_info': {'device_id': 'device_id'},
                'created_at': '2021-10-31T00:01:00.0+00:00',
                'updated_at': '2021-10-31T00:02:00.0+00:00',
            }

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_response(self, antifraud_info):
            self.response = {
                'antifraud_info': antifraud_info,
                'created_at': '2021-10-31T00:01:00.0+00:00',
                'updated_at': '2021-10-31T00:02:00.0+00:00',
            }

    context = Context()

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_antifraud_info',
    )
    def _get_antifraud_info_handler(request):
        assert (
            request.json.get('session_uuid')
            == '9c4e663d-ff6e-4d12-9ebd-48c53c907791'
        )

        return mockserver.make_response(
            status=200,
            json={
                'antifraud_info': {'device_id': 'device_id'},
                'created_at': '2021-10-31T00:01:00.0+00:00',
                'updated_at': '2021-10-31T00:02:00.0+00:00',
            },
        )

    context.get_antifraud_info_handler = _get_antifraud_info_handler

    return context


@pytest.fixture
def access_control_mock(mockserver):
    class Context:
        def __init__(self):
            self.apply_policies_handler = None
            self.http_status_code = 200
            self.handler_path = None

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/bank-access-control/access-control-internal/v1/apply-policies',
    )
    def _apply_policies_handler(request):
        assert request.method == 'POST'
        context.handler_path = request.json['resource_attributes'][
            'handler_path'
        ]
        decision = (
            'PERMIT'
            if request.json['subject_attributes']['jwt'] == 'allow'
            else 'DENY'
        )
        return mockserver.make_response(
            status=context.http_status_code, json={'decision': decision},
        )

    context.apply_policies_handler = _apply_policies_handler
    return context
