import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_transfers_plugins import *  # noqa: F403 F401
from testsuite.utils import http

from tests_bank_transfers import common

try:
    import library.python.resource  # noqa: F401
    _IS_ARCADIA = True
except ImportError:
    _IS_ARCADIA = False

if _IS_ARCADIA:
    import logging
    import dataclasses

    @pytest.fixture(autouse=True)
    async def service_logs(taxi_bank_transfers):
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

        async with taxi_bank_transfers.capture_logs() as capture:
            # This hack tricks the client into thinking that
            # caches still need to be invalidated on the first call
            # so as not to break tests that depend on this behaviour
            # pylint: disable=protected-access
            taxi_bank_transfers._client._state_manager._state = (
                dataclasses.replace(
                    # pylint: disable=protected-access
                    taxi_bank_transfers._client._state_manager._state,
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


ALL_BANKS = [
    {
        'bank_id': '100000000190',
        'names': [
            {'locale': 'ru', 'name': 'РОСКОСМОСБАНК'},
            {'locale': 'en', 'name': 'ROSCOSMOSBANK'},
        ],
    },
    {
        'bank_id': '100000000191',
        'names': [
            {'locale': 'ru', 'name': 'Банк Казани'},
            {'locale': 'en', 'name': 'BANK OF KAZAN'},
        ],
    },
    {
        'bank_id': '100000000065',
        'names': [
            {'locale': 'ru', 'name': 'Точка'},
            {'locale': 'en', 'name': 'Tochka'},
        ],
    },
    {
        'bank_id': '110000000207',
        'names': [
            {'locale': 'ru', 'name': 'Дойче банк'},
            {'locale': 'en', 'name': 'Deutsche Bank'},
        ],
    },
    {
        'bank_id': '100000000015',
        'names': [
            {'locale': 'ru', 'name': 'Банк ФК Открытие'},
            {'locale': 'en', 'name': 'Openbank'},
        ],
    },
    {
        'bank_id': '100000000014',
        'names': [
            {'locale': 'ru', 'name': 'Банк Русский Стандарт'},
            {'locale': 'en', 'name': 'Rus Standart Bank'},
        ],
    },
    {
        'bank_id': '100000000012',
        'names': [
            {'locale': 'ru', 'name': 'Росбанк'},
            {'locale': 'en', 'name': 'Rosbank'},
        ],
    },
    {
        'bank_id': '100000000016',
        'names': [
            {'locale': 'ru', 'name': 'Почта Банк'},
            {'locale': 'en', 'name': 'Pochta Bank'},
        ],
    },
    {
        'bank_id': '100000000004',
        'names': [
            {'locale': 'ru', 'name': 'Тинькофф Банк'},
            {'locale': 'en', 'name': 'Tinkoff Bank'},
        ],
    },
    {
        'bank_id': '100000000001',
        'names': [
            {'locale': 'ru', 'name': 'Газпромбанк'},
            {'locale': 'en', 'name': 'Gazprombank'},
        ],
    },
    {
        'bank_id': '100000000008',
        'names': [
            {'locale': 'ru', 'name': 'Альфа-Банк'},
            {'locale': 'en', 'name': 'Alfa-Bank'},
        ],
    },
    {
        'bank_id': '100000000007',
        'names': [
            {'locale': 'ru', 'name': 'Райффайзенбанк'},
            {'locale': 'en', 'name': 'Raiffeisenbank'},
        ],
    },
    {
        'bank_id': '100000000005',
        'names': [
            {'locale': 'ru', 'name': 'ВТБ Банк'},
            {'locale': 'en', 'name': 'VTB Bank'},
        ],
    },
    {
        'bank_id': '100000000009',
        'names': [
            {'locale': 'ru', 'name': 'QIWI Кошелек'},
            {'locale': 'en', 'name': 'QIWI Wallet'},
        ],
    },
    {
        'bank_id': '100000000011',
        'names': [
            {'locale': 'ru', 'name': 'РНКБ БАНК'},
            {'locale': 'en', 'name': 'RNKB Bank'},
        ],
    },
    {
        'bank_id': '100000000111',
        'names': [
            {'locale': 'ru', 'name': 'Сбербанк'},
            {'locale': 'en', 'name': 'Sberbank'},
        ],
    },
    {
        'bank_id': '100000000150',
        'names': [
            {'locale': 'ru', 'name': 'Яндекс Банк'},
            {'locale': 'en', 'name': 'Yandex Bank'},
        ],
    },
]


BANKS_WITH_M2M = [
    {
        'bank_id': '100000000190',
        'names': [
            {'locale': 'ru', 'name': 'РОСКОСМОСБАНК'},
            {'locale': 'en', 'name': 'ROSCOSMOSBANK'},
        ],
    },
]


@pytest.fixture(autouse=True)
def bank_core_statement_mock(mockserver):
    class Context:
        def __init__(self):
            self.balance = common.AGREEMENT_BALANCE
            self.month_limit = common.MAX_MONTHLY_TURNOVER
            self.transaction_limit = common.MAX_TXN_SUM
            self.no_code_limit = common.DEBIT_LIMITS[2]
            self.debit_limits = common.DEBIT_LIMITS

        def set_balance(self, balance):
            self.balance = balance

        def set_month_limit(self, limit):
            self.debit_limits = [
                limit if x == self.month_limit else x
                for x in self.debit_limits
            ]
            self.month_limit = limit

        def set_transaction_limit(self, limit):
            self.debit_limits = [
                limit if x == self.transaction_limit else x
                for x in self.debit_limits
            ]
            self.transaction_limit = limit

        def set_limit_without_code(self, limit):
            self.debit_limits = [
                limit if x == self.no_code_limit else x
                for x in self.debit_limits
            ]
            self.no_code_limit = limit

    context = Context()
    money_template = {'amount': '15000', 'currency': common.DEFAULT_CURRENCY}
    limit_template = {
        'period_start': '2018-01-28T00:00:00.000+03:00',
        'period': 'MONTH',
        'threshold': money_template.copy(),
        'remaining': money_template.copy(),
    }
    agreement_balance_template = {
        'agreement_id': common.TEST_AGREEMENT_ID,
        'balance': money_template.copy(),
        'credit_limit': [],
        'debit_limit': [],
    }

    @mockserver.json_handler('/bank-core-statement/v1/agreements/balance/get')
    def _mock_get_agreements_balance(request: http.Request):
        if (
                'agreement_id' in request.query
                and request.query['agreement_id'] != common.TEST_AGREEMENT_ID
        ):
            return mockserver.make_response(
                status=404, json={'code': '404', 'message': 'Not found'},
            )
        agreement_balance = agreement_balance_template.copy()
        agreement_balance['balance']['amount'] = str(context.balance)
        money = money_template.copy()
        limit = limit_template.copy()
        for limit_amount in common.CREDIT_LIMITS:
            money['amount'] = str(common.THRESHOLD_LIMIT)
            limit['threshold'] = money.copy()
            money['amount'] = str(limit_amount)
            limit['remaining'] = money.copy()
            agreement_balance['credit_limit'].append(limit.copy())
        for limit_amount in context.debit_limits:
            money['amount'] = str(common.THRESHOLD_LIMIT)
            limit['threshold'] = money.copy()
            money['amount'] = str(limit_amount)
            limit['remaining'] = money.copy()
            if limit_amount == context.transaction_limit:
                limit['code'] = 'MAX_TXN_SUM'
            elif limit_amount == context.month_limit:
                limit['code'] = 'MAX_MONTHLY_TURNOVER'
            else:
                limit.pop('code', None)
            agreement_balance['debit_limit'].append(limit.copy())
        return {'agreements': [agreement_balance]}

    return context


@pytest.fixture(autouse=True)
def bank_core_faster_payments_mock(mockserver):
    class Context:
        def __init__(self):
            self.http_status_code = 200
            self.bank_check_status = 'SUCCESS'
            self.me2me_pull_response_status = 'PROCESSING'
            self.is_yandex_in_history = False
            self.continue_handler = None
            self.perform_handler = None
            self.me2me_pull_perform_handler = None
            self.get_default_bank_handler = None
            self.error_code = 'error'

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_bank_check_status(self, status):
            self.bank_check_status = status

        def set_me2me_pull_response_status(self, status):
            self.me2me_pull_response_status = status

        def add_yandex_to_bank_hist(self):
            self.is_yandex_in_history = True

        def set_error_code(self, code):
            self.error_code = code

    context = Context()

    tinkoff = {
        'bank_id': '100000000004',
        'names': [
            {'locale': 'ru', 'name': 'Тинькофф Банк'},
            {'locale': 'en', 'name': 'Tinkoff Bank'},
        ],
    }
    rosbank = {
        'bank_id': '100000000012',
        'names': [
            {'locale': 'en', 'name': 'Rosbank'},
            {'locale': 'ru', 'name': 'Росбанк'},
        ],
    }
    yandex_bank = {
        'bank_id': '100000000150',
        'names': [
            {'locale': 'ru', 'name': 'Яндекс Банк'},
            {'locale': 'en', 'name': 'Yandex Bank'},
        ],
    }
    sberbank = {
        'bank_id': '100000000111',
        'names': [
            {'locale': 'ru', 'name': 'Сбербанк'},
            {'locale': 'en', 'name': 'Sberbank'},
        ],
    }

    def get_cashed_bank(bank=tinkoff, receiver_name=common.RECEIVER_NAME_1):
        return {'bank': bank, 'recipientName': receiver_name}

    @mockserver.json_handler('/bank-core-faster-payments/v1/connect/info/get')
    def _mock_get_connect_info(request: http.Request):
        if request.headers['X-Yandex-BUID'] in [
                common.TEST_BANK_UID,
                common.TEST_YANDEX_BANK_FPS_ON_BUID,
        ]:
            return {'is_connected': True}
        if request.headers['X-Yandex-BUID'] in [
                common.TEST_ABSENT_IN_FPS_CORE_AND_USERINFO_BASES_BUID,
                common.TEST_ABSENT_IN_USERINFO_BUID,
        ]:
            return mockserver.make_response(
                status=404, json={'code': '404', 'message': 'no buid in bd'},
            )
        return {'is_connected': False}

    @mockserver.json_handler('/bank-core-faster-payments/v1/connect')
    def _mock_connect(request: http.Request):
        assert request.json['phone_number']
        if (
                request.headers['X-Yandex-BUID']
                == common.TEST_ABSENT_IN_FPS_CORE_AND_USERINFO_BASES_BUID
        ):
            return mockserver.make_response(
                status=404, json={'code': '404', 'message': 'no buid in bd'},
            )
        return mockserver.make_response(
            status=200, json={'code': '200', 'message': 'Ok'},
        )

    @mockserver.json_handler('/bank-core-faster-payments/v1/disconnect')
    def _mock_disconnect(request: http.Request):
        if (
                request.headers['X-Yandex-BUID']
                == common.TEST_ABSENT_IN_FPS_CORE_AND_USERINFO_BASES_BUID
        ):
            return mockserver.make_response(
                status=404, json={'code': '404', 'message': 'no buid in bd'},
            )
        return mockserver.make_response(
            status=200, json={'code': '200', 'message': 'Ok'},
        )

    @mockserver.json_handler(
        '/bank-core-faster-payments/v1/user/banks-history/get',
    )
    def _mock_get_banks_history(request: http.Request):
        banks_history = []
        phone = request.json['phone_number']
        if phone not in [common.RECEIVER_PHONE_00, common.RECEIVER_PHONE_01]:
            banks_history.append(
                get_cashed_bank(receiver_name=common.get_receiver_name(phone)),
            )

            if phone == common.RECEIVER_PHONE_2:
                banks_history.append(
                    get_cashed_bank(
                        receiver_name=common.get_receiver_name(phone),
                        bank=rosbank,
                    ),
                )

            if context.is_yandex_in_history:
                banks_history.append(
                    get_cashed_bank(
                        receiver_name=common.get_receiver_name(phone),
                        bank=yandex_bank,
                    ),
                )

        return {'userBanksHistory': banks_history}

    @mockserver.json_handler(
        '/bank-core-faster-payments/v1/user/bank-default/get',
    )
    def _mock_get_default_bank(request: http.Request):
        phone = request.json['phone_number']
        if phone not in (
                common.RECEIVER_PHONE_00,
                common.RECEIVER_PHONE_1,
                common.RECEIVER_PHONE_2,
                common.RECEIVER_PHONE_YANDEX,
                common.RECEIVER_PHONE_SBER,
        ):
            return {}
        if phone == common.RECEIVER_PHONE_SBER:
            return {'default-bank': sberbank}
        return (
            {'default-bank': yandex_bank}
            if phone == common.RECEIVER_PHONE_YANDEX
            else {'default-bank': rosbank}
        )

    @mockserver.json_handler('/bank-core-faster-payments/v1/banks/get')
    def _mock_get_banks(request: http.Request):
        if (
                'transfer_type' in request.query
                and request.query['transfer_type'] == 'M2M_PULL'
        ):
            return {'banks': BANKS_WITH_M2M}

        return {'banks': ALL_BANKS}

    @mockserver.json_handler(
        '/bank-core-faster-payments/v1/me2me-pull/request/perform',
    )
    def _mock_me2me_pull_perform_request(request: http.Request):
        if context.http_status_code != 200:
            return mockserver.make_response(
                status=context.http_status_code,
                json={
                    'code': str(context.http_status_code),
                    'message': 'Error',
                },
            )

        if context.me2me_pull_response_status == 'FAILED':
            return {
                'status': 'FAILED',
                'request_id': 'aa1234',
                'errors': [{'code': '500', 'message': 'Internal error'}],
            }
        if context.me2me_pull_response_status == 'SUCCESS':
            return {'status': 'SUCCESS', 'request_id': 'aa1236'}

        return {'status': 'PENDING', 'request_id': 'aa1235'}

    @mockserver.json_handler(
        '/bank-core-faster-payments/v1/transfer/request/perform',
    )
    def _mock_perform_transfer_request(request: http.Request):
        if (
                request.json['phone_number'] != common.RECEIVER_PHONE_1
                or request.json['agreement_id'] != common.TEST_AGREEMENT_ID
                or request.json['bank_id'] != common.TINKOFF
                or float(request.json['amount']['amount'])
                > common.AGREEMENT_BALANCE
        ):
            return {
                'status': 'FAILED',
                'request_id': 'aa1234',
                'errors': [
                    {'code': context.error_code, 'message': 'Internal error'},
                ],
            }
        return {'status': 'PENDING', 'request_id': 'aa1235'}

    @mockserver.json_handler(
        '/bank-core-faster-payments/v1/transfer/request/continue',
    )
    def _mock_continue_transfer_request(request: http.Request):
        if request.json['request_id'] != common.CHECK_REQUEST_ID:
            return {
                'status': 'FAILED',
                'request_id': 'aa1234',
                'errors': [{'code': '500', 'message': 'Internal error'}],
            }
        return {'status': 'PENDING', 'request_id': 'aa1236'}

    @mockserver.json_handler(
        '/bank-core-faster-payments/v1/transfer/request/check',
    )
    def _mock_check_transfer_request(request: http.Request):
        request_id = request.json['request_id']
        result = {'request_id': request_id}
        if request_id == 'aa1235':
            result['status'] = 'PENDING'
        elif request_id == 'aa1236':
            result['status'] = 'SUCCESS'
        else:
            result['status'] = 'FAILED'
            result['errors'] = [{'code': '500', 'message': 'Internal error'}]
        return result

    @mockserver.json_handler('/bank-core-faster-payments/v2/transfer/check')
    def _mock_check_transfer_v2(request: http.Request):
        if context.http_status_code != 200:
            return mockserver.make_response(
                status=context.http_status_code,
                json={'code': context.error_code, 'message': 'error'},
            )
        if context.bank_check_status == 'PENDING':
            return {'status': 'PENDING'}
        if (
                request.json['phone_number'] != common.RECEIVER_PHONE_1
                or request.json['bank_id'] == common.ROSDORBANK
        ):
            return {'status': 'SUCCESS', 'response': {'isEnable': False}}
        response: dict = {
            'status': 'SUCCESS',
            'response': {
                'isEnable': True,
                'recipientName': common.RECEIVER_NAME_1,
            },
        }
        if (
                'amount' in request.json
                and request.json['bank_id'] != common.YANDEX_BANK
        ):
            response['response']['request_id'] = common.CHECK_REQUEST_ID
        return response

    @mockserver.json_handler('/bank-core-faster-payments/v1/transfer/check')
    def _mock_check_transfer_v1(request: http.Request):
        if request.json['phone_number'] != common.RECEIVER_PHONE_1:
            return {'isEnable': False}
        response = {'isEnable': True, 'recipientName': common.RECEIVER_NAME_1}
        if (
                'amount' in request.json
                and request.json['bank_id'] != common.YANDEX_BANK
        ):
            response['request_id'] = common.CHECK_REQUEST_ID
        return response

    context.continue_handler = _mock_continue_transfer_request
    context.perform_handler = _mock_perform_transfer_request
    context.me2me_pull_perform_handler = _mock_me2me_pull_perform_request
    context.get_default_bank_handler = _mock_get_default_bank

    return context


@pytest.fixture(autouse=True)
def bank_userinfo_mock(mockserver):
    class Context:
        def __init__(self):
            self.get_userinfo_handler = None
            self.get_phone_number_handler = None
            self.get_antifraud_info_handler = None

            self.phone_number = common.RECEIVER_PHONE_00
            self.http_status_code = 200
            self.http_response = {
                'auth_status': 'IDENTIFIED',
                'phone': common.RECEIVER_PHONE_1,
            }

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_phone_number(self, number):
            self.phone_number = number

    context = Context()

    @mockserver.json_handler('/bank-userinfo/v1/userinfo/v1/get_user_info')
    def _mock_get_userinfo(request: http.Request):
        if (
                request.headers['X-Yandex-BUID']
                == common.TEST_ABSENT_IN_FPS_CORE_AND_USERINFO_BASES_BUID
        ):
            return mockserver.make_response(
                status=404, json={'code': '404', 'message': 'no buid in bd'},
            )
        if (
                request.headers['X-Yandex-BUID']
                == common.TEST_YANDEX_BANK_FPS_ON_BUID
        ):
            context.http_response['phone'] = common.RECEIVER_PHONE_YANDEX
        return mockserver.make_response(status=200, json=context.http_response)

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_antifraud_info',
    )
    def _mock_get_antifraud_info(request: http.Request):
        return mockserver.make_response(
            status=200,
            json={
                'antifraud_info': {
                    'client_ip': 'client_ip',
                    'device_id': 'device_id',
                },
            },
        )

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_phone_number',
    )
    def _mock_get_phone_number(request: http.Request):
        return mockserver.make_response(
            status=200, json={'phone': context.phone_number},
        )

    context.get_userinfo_handler = _mock_get_userinfo
    context.get_phone_number_handler = _mock_get_phone_number
    context.get_antifraud_info_handler = _mock_get_antifraud_info
    return context


@pytest.fixture(autouse=True)
def bank_authorization(mockserver, mocked_time):
    class Context:
        def __init__(self):
            self.create_track_handler = None
            self.http_status_code = 200
            self.response_create_track = {'track_id': 'default_track_id'}

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_response_create_track(self, new_response):
            self.response_create_track = new_response

    context = Context()

    @mockserver.json_handler(
        '/bank-authorization/authorization-internal/v1/create_track',
    )
    def _create_track_handler(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=context.http_status_code,
            json=context.response_create_track,
        )

    context.create_track_handler = _create_track_handler

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

        def set_response(self, resolution='ALLOW', actions=[]):
            self.response = {
                'resolution': resolution,
                'action': actions,
                'af_decision_id': 'af_decision_id',
            }

    context = Context()

    @mockserver.json_handler('/bank-risk/risk/calculation/confirm_transfer')
    def _risk_calculation_handler(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    context.risk_calculation_handler = _risk_calculation_handler

    return context


@pytest.fixture(autouse=True)
def bank_core_client_mock(mockserver):
    class Context:
        def __init__(self):
            self.response = {
                'auth_level': 'KYC',
                'phone_number': common.RECEIVER_PHONE_1,
            }
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
