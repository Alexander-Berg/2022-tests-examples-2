import base64
import json

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_audit_logger.mock_bank_audit import bank_audit  # noqa: F401
from bank_wallet_plugins import *  # noqa: F403 F401

from tests_bank_wallet import common
from tests_bank_wallet.core_mocks import *  # noqa: F403 F401

try:
    import library.python.resource  # noqa: F401
    _IS_ARCADIA = True
except ImportError:
    _IS_ARCADIA = False

if _IS_ARCADIA:
    import logging
    import dataclasses

    @pytest.fixture(autouse=True)
    async def service_logs(taxi_bank_wallet):
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

        async with taxi_bank_wallet.capture_logs() as capture:
            # This hack tricks the client into thinking that
            # caches still need to be invalidated on the first call
            # so as not to break tests that depend on this behaviour
            # pylint: disable=protected-access
            taxi_bank_wallet._client._state_manager._state = (
                dataclasses.replace(
                    # pylint: disable=protected-access
                    taxi_bank_wallet._client._state_manager._state,
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
def bank_trust_gateway_mock(mockserver):
    def make_response_plus_balance(uid: str):
        balances = {
            '1': {
                'balances': [
                    {
                        'amount': '124.9999',
                        'currency': 'RUB',
                        'wallet_id': '42',
                    },
                ],
            },
            '2': {
                'balances': [
                    {
                        'amount': '321',
                        'currency': 'NOT_RUB',
                        'wallet_id': '34',
                    },
                    {'amount': '123.01', 'currency': 'RUB', 'wallet_id': '39'},
                ],
            },
            '3': {
                'balances': [
                    {
                        'amount': '322',
                        'currency': 'NOT_RUB',
                        'wallet_id': '25',
                    },
                ],
            },
            '4': {
                'balances': [
                    {'amount': '321', 'currency': 'RUB', 'wallet_id': '13'},
                    {'amount': '321', 'currency': 'RUB', 'wallet_id': '23'},
                ],
            },
            '5': {
                'balances': [
                    {'amount': ' 2', 'currency': 'RUB', 'wallet_id': '13'},
                ],
            },
            '6': {
                'balances': [
                    {
                        'amount': '3.12345',
                        'currency': 'RUB',
                        'wallet_id': '13',
                    },
                ],
            },
        }
        return balances[uid]

    class Context:
        def __init__(self):
            self.image_name = None
            self.group_id = None
            self.wallets_balance_handler = None
            self.plus_balance_handler = None
            self.transaction_list_handler = None
            self.transaction_handler = None

        def set_image_name(self, image_name):
            self.image_name = image_name

        def set_group_id(self, group_id):
            self.group_id = group_id

    context = Context()

    @mockserver.json_handler('/bank-trust-gateway/legacy/wallet-balance')
    def _mock_get_plus_balance(request):
        return make_response_plus_balance(request.query.get('uid'))

    context.plus_balance_handler = _mock_get_plus_balance

    return context


@pytest.fixture
def bank_core_statement_mock(mockserver):
    def make_response_wallets_balance(
            buid: str,
            currency,
            amount='10000',
            threshold='40000',
            remaining='39600',
            period='MONTH',
    ):
        wallets = {
            '1': {
                'wallets': [
                    common.build_wallet(
                        'f0180a66-a339-497e-9572-130f440cc338',
                        common.build_balance(amount, currency),
                        [
                            common.build_limit(
                                threshold, currency, remaining, period,
                            ),
                        ],
                        [
                            common.build_limit(
                                threshold, currency, remaining, period,
                            ),
                        ],
                    ),
                ],
            },
            'bad_buid': {'wallets': []},
            'many_wallets': {
                'wallets': [
                    common.build_wallet(
                        'f0180a66-a339-497e-9572-130f440cc338',
                        common.build_balance('10000', currency),
                        [],
                        [],
                    ),
                    common.build_wallet(
                        'f0180000-a339-497e-9572-130f440cc338',
                        common.build_balance('0', currency),
                        [],
                        [],
                    ),
                ],
            },
        }
        return wallets.get(buid)

    def make_response_wallets_balance2(buid: str, currency, amount='10000'):
        wallets = {
            '1': {
                'balances': [
                    common.build_wallet_balance(
                        'f0180a66-a339-497e-9572-130f440cc338',
                        common.build_balance(amount, currency),
                        ['method1', 'method2'],
                    ),
                ],
            },
            'bad_buid': {'balances': []},
            'many_wallets': {
                'balances': [
                    common.build_wallet_balance(
                        'f0180a66-a339-497e-9572-130f440cc338',
                        common.build_balance('10000', currency),
                        ['method1', 'method2'],
                    ),
                    common.build_wallet_balance(
                        'f0180000-a339-497e-9572-130f440cc338',
                        common.build_balance('0', currency),
                        ['method1', 'method2'],
                    ),
                ],
            },
        }
        return wallets.get(buid)

    def make_transactions(transaction_id=None):
        transactions = [
            {
                'transaction_id': '15',  # incoming transfer
                'status': 'CLEAR',
                'type': 'C2C_BY_PHONE',
                'direction': 'CREDIT',
                'timestamp': '2018-01-28T12:08:46.372+00:00',
                'money': {'amount': '10000', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'plus_credit': {'amount': '0', 'currency': 'RUB'},
                'fees': [],
                'rrn': '205500001071',
                'auth_code': 'CY8PZ5',
                'originator_system_name': 'Payment Hub',
                'merchant': {
                    'merchant_name': '',
                    'merchant_country': '',
                    'merchant_category_code': '',
                },
                'description': 'Комментарий',
                'c2c-details': {
                    'phone': '+79123456789',
                    'bank-id': '100000000999',  # unknown code
                    'name': 'Иван Иванович А',
                    'operation-code': 'A2053112902642010000057BD2157589',
                },
            },
            {
                'transaction_id': '14',  # topup
                'status': 'CLEAR',
                'type': 'UNDEFINED',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:47.000+00:00',
                'merchant': {
                    'merchant_id': '2bea9c35-6032-4d76-b697-4a7d852a5051',
                    'merchant_name': 'YANDEX_DRIVE',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '400', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'cashback': {
                    'cashbackType': 'MONEY',
                    'currency': 'RUB',
                    'expectedAmount': '100.00',
                    'executedAmount': '20.00',
                },
                'plus_credit': {
                    'amount': '200',
                    'currency': 'RUB',
                    'fees': [],
                },
                'fees': [],
                'payment_system': 'AMERICAN_EXPRESS',
                'card_number': '*********************1234',
            },
            {
                'transaction_id': '13',  # topup
                'status': 'CLEAR',
                'type': 'UNDEFINED',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:47.000+00:00',
                'merchant': {
                    'merchant_id': '2bea9c35-6032-4d76-b697-4a7d852a5051',
                    'merchant_name': 'YANDEX_DRIVE',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '400', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'plus_credit': {
                    'amount': '150',
                    'currency': 'RUB',
                    'fees': [],
                },
                'cashback': {
                    'cashbackType': 'PLUS',
                    'currency': 'RUB',
                    'expectedAmount': '200',
                    'executedAmount': '150',
                },
                'fees': [],
                'payment_system': 'MIR',
                'card_number': '*********************1234',
            },
            {
                'transaction_id': '12',  # topup
                'status': 'CLEAR',
                'type': 'UNDEFINED',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:47.000+00:00',
                'merchant': {
                    'merchant_id': '2bea9c35-6032-4d76-b697-4a7d852a5051',
                    'merchant_name': 'YANDEX_DRIVE',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '400', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'plus_credit': {
                    'amount': '150',
                    'currency': 'RUB',
                    'fees': [],
                },
                'cashback': {
                    'cashbackType': 'PLUS',
                    'currency': 'RUB',
                    'expectedAmount': '200',
                    'executedAmount': '150',
                },
                'fees': [],
                'payment_system': 'MASTER_CARD',
                'card_number': '*********************1234',
            },
            {
                'transaction_id': '11',  # with none token
                'status': 'CLEAR',
                'type': 'PURCHASE',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:48+00:00',
                'merchant': {
                    'merchant_id': '74382543-1f6c-4ba1-9270-c9721ad414eb',
                    'merchant_name': 'YANDEX_EDA                           ',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '100', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'plus_credit': {'amount': '0.12', 'currency': 'RUB'},
                'cashback': {
                    'cashbackType': 'PLUS',
                    'currency': 'RUB',
                    'expectedAmount': '200',
                    'executedAmount': '0.12',
                },
                'fees': [],
                'token_provider': 'GOOGLE',
                'token_suffix': '1234',
            },
            {
                'transaction_id': '10',  # with token
                'status': 'CLEAR',
                'type': 'PURCHASE',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:48+00:00',
                'merchant': {
                    'merchant_id': '74382543-1f6c-4ba1-9270-c9721ad414eb',
                    'merchant_name': 'YANDEX_EDA                           ',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '100', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'plus_credit': {'amount': '0.12', 'currency': 'RUB'},
                'cashback': {
                    'cashbackType': 'PLUS',
                    'currency': 'RUB',
                    'expectedAmount': '200',
                    'executedAmount': '0.12',
                },
                'fees': [],
                'token_provider': 'APPLE',
                'token_suffix': '1234',
            },
            {
                'transaction_id': '9',  # plus credit almost zero amount
                'status': 'CLEAR',
                'type': 'PURCHASE',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:48+00:00',
                'merchant': {
                    'merchant_id': '74382543-1f6c-4ba1-9270-c9721ad414eb',
                    'merchant_name': 'YANDEX_EDA',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '100', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'plus_credit': {'amount': '0.12', 'currency': 'RUB'},
                'cashback': {
                    'cashbackType': 'PLUS',
                    'currency': 'RUB',
                    'expectedAmount': '200',
                    'executedAmount': '0.12',
                },
                'fees': [],
                'payment_system': 'VISA',
                'card_number': '*********************1234',
            },
            {
                'transaction_id': '8',  # plus credit invalid currency
                'status': 'CLEAR',
                'type': 'PURCHASE',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:48+00:00',
                'merchant': {
                    'merchant_id': '74382543-1f6c-4ba1-9270-c9721ad414eb',
                    'merchant_name': 'YANDEX_EDA',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '100', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'plus_credit': {'amount': '321', 'currency': 'USD'},
                'cashback': {
                    'cashbackType': 'PLUS',
                    'currency': 'USD',
                    'expectedAmount': '400',
                    'executedAmount': '321',
                },
                'fees': [],
            },
            {
                'transaction_id': '7',  # plus debit invalid currency
                'status': 'CLEAR',
                'type': 'PURCHASE',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:48+00:00',
                'merchant': {
                    'merchant_id': '74382543-1f6c-4ba1-9270-c9721ad414eb',
                    'merchant_name': 'YANDEX_EDA',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '100', 'currency': 'RUB'},
                'plus_debit': {'amount': '123', 'currency': 'EUR'},
                'plus_credit': {'amount': '0', 'currency': 'RUB'},
                'fees': [],
            },
            {
                'transaction_id': '6',  # plus debit in purchase
                'status': 'CLEAR',
                'type': 'PURCHASE',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:48+00:00',
                'merchant': {
                    'merchant_id': '74382543-1f6c-4ba1-9270-c9721ad414eb',
                    'merchant_name': 'YANDEX_EDA',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '100', 'currency': 'RUB'},
                'plus_debit': {'amount': '50.12', 'currency': 'RUB'},
                'plus_credit': {'amount': '0', 'currency': 'RUB'},
                'fees': [],
            },
            {
                'transaction_id': '5',  # plus empty in purchase
                'status': 'CLEAR',
                'type': 'PURCHASE',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:48+00:00',
                'merchant': {
                    'merchant_id': '74382543-1f6c-4ba1-9270-c9721ad414eb',
                    'merchant_name': 'YANDEX_EDA',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '100', 'currency': 'RUB'},
                'plus_debit': {'amount': '', 'currency': 'RUB'},
                'plus_credit': {'amount': '', 'currency': 'RUB'},
                'cashback': {
                    'cashbackType': 'PLUS',
                    'currency': 'RUB',
                    'expectedAmount': '',
                    'executedAmount': '',
                },
                'fees': [],
            },
            {
                'transaction_id': '4',  # plus 4 digits after point in purchase
                'status': 'CLEAR',
                'type': 'PURCHASE',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:48+00:00',
                'merchant': {
                    'merchant_id': '74382543-1f6c-4ba1-9270-c9721ad414eb',
                    'merchant_name': 'YANDEX_EDA',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '100', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'plus_credit': {'amount': '50.1234', 'currency': 'RUB'},
                'cashback': {
                    'cashbackType': 'PLUS',
                    'currency': 'RUB',
                    'expectedAmount': '200',
                    'executedAmount': '50.1234',
                },
                'fees': [],
            },
            {
                'transaction_id': '3',  # purchase
                'status': 'CLEAR',
                'type': 'PURCHASE',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:48+00:00',
                'merchant': {
                    'merchant_id': '74382543-1f6c-4ba1-9270-c9721ad414eb',
                    'merchant_name': 'YANDEX_EDA',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '100', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'plus_credit': {'amount': '50.55', 'currency': 'RUB'},
                'cashback': {
                    'cashbackType': 'PLUS',
                    'currency': 'RUB',
                    'expectedAmount': '100.00',
                    'executedAmount': '50.55',
                },
                'fees': [],
            },
            {
                'transaction_id': '2',  # topup
                'status': 'CLEAR',
                'type': 'C2C_BY_PHONE',
                'direction': 'DEBIT',
                'timestamp': '2018-02-01T12:08:47.000+00:00',
                'money': {'amount': '400', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'plus_credit': {
                    'amount': '150',
                    'currency': 'RUB',
                    'fees': [],
                },
                'cashback': {
                    'cashbackType': 'PLUS',
                    'currency': 'RUB',
                    'expectedAmount': '200',
                    'executedAmount': '150',
                },
                'fees': [],
                'rrn': '205500001071',
                'auth_code': 'CY8PZ5',
                'originator_system_name': 'Payment Hub',
                'merchant': {
                    'merchant_name': '',
                    'merchant_country': '',
                    'merchant_category_code': '',
                },
                'description': 'Комментарий',
                'c2c-details': {
                    'phone': '+79123456789',
                    'bank-id': '100000000004',
                    'name': 'Иван Иванович А',
                    'operation-code': 'A2053112902642010000057BD2157589',
                },
            },
            {
                'transaction_id': '1',  # incoming transfer
                'status': 'CLEAR',
                'type': 'C2C_BY_PHONE',
                'direction': 'CREDIT',
                'timestamp': '2018-01-28T12:08:46.372+00:00',
                'money': {'amount': '10000', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'plus_credit': {'amount': '0', 'currency': 'RUB'},
                'fees': [],
                'rrn': '205500001071',
                'auth_code': 'CY8PZ5',
                'originator_system_name': 'Payment Hub',
                'merchant': {
                    'merchant_name': '',
                    'merchant_country': '',
                    'merchant_category_code': '',
                },
                'description': 'Комментарий',
                'c2c-details': {
                    'phone': '+79123456789',
                    'bank-id': '100000000004',
                    'name': 'Иван Иванович А',
                    'operation-code': 'A2053112902642010000057BD2157589',
                },
            },
        ]
        if transaction_id:
            transactions = [
                x
                for x in transactions
                if x.get('transaction_id') == transaction_id
            ]
            return (
                transactions[0]
                if len(transactions) == 1
                else mockserver.make_response(
                    status=404,
                    json={
                        'message': 'Order with current id is not found',
                        'code': 'Not found',
                    },
                )
            )
        return transactions

    def make_response_transaction_list(cursor, page_size, transactions_count):
        transactions = make_transactions()
        if transactions_count is not None:
            transactions = transactions[:transactions_count]
        if not transactions:
            return {'status_groups': []}
        transaction_id = int(transactions[0].get('transaction_id')) + 1
        if cursor:
            cursor = json.loads(
                base64.b64decode(cursor.encode('ascii')).decode('ascii'),
            )
            transaction_id = int(cursor.get('cursor_key'))
            page_size = int(cursor.get('page_size'))

        response = {
            'status_groups': [
                x
                for x in transactions
                if int(x.get('transaction_id')) < transaction_id
            ][: int(page_size)],
        }
        if transaction_id - int(page_size) > 1:
            response['cursor'] = base64.b64encode(
                f'{{"cursor_key":"{transaction_id - int(page_size)}", '
                f'"page_size":{int(page_size)}}}'.encode('ascii'),
            ).decode('ascii')

        return response

    def get_wallets_id(wallet_ids_count):
        wallets = [
            {'id': 'f0180a66-a339-497e-9572-130f440cc338', 'currency': 'RUB'},
            {'id': '2', 'currency': 'RUB'},
            {'id': '3', 'currency': 'RUB'},
        ]
        return {'wallets': list(wallets[:wallet_ids_count])}

    class Context:
        def __init__(self):
            self.image_name = None
            self.group_id = None
            self.wallets_balance_handler = None
            self.wallets_balance2_handler = None
            self.transaction_list_handler = None
            self.trx_list_by_agreement_handler = None
            self.trx_list_by_card_handler = None
            self.agreements_balances_handler = None
            self.limit_get_list_handler = None
            self.transaction_handler = None
            self.wallet_id_get_handler = None
            self.need_timeout_exception = False
            self.needed_error_code = None
            self.wallet_ids_count = None
            self.balance_currency = 'RUB'
            self.transactions_count = None
            self.explicit_wallets_specification = None
            self.balance_amount = '10000'
            self.remaining_amount = '39600'
            self.threshold_amount = '40000'
            self.wallet_period = 'MONTH'
            self.agreements_balances = []
            self.agreement_limits = []

        def set_image_name(self, image_name):
            self.image_name = image_name

        def set_group_id(self, group_id):
            self.group_id = group_id

        def set_agreements_balances(self, balances):
            self.agreements_balances = balances

        def set_agreement_limits(self, limits):
            self.agreement_limits = limits

    context = Context()

    @mockserver.json_handler(
        '/bank-core-statement/v1/wallets/balance/get', prefix=True,
    )
    def _mock_get_wallets_balance(request):
        if context.need_timeout_exception:
            raise mockserver.TimeoutError()
        if context.explicit_wallets_specification:
            return {'wallets': context.explicit_wallets_specification}
        return make_response_wallets_balance(
            request.headers.get('X-Yandex-BUID'),
            context.balance_currency,
            context.balance_amount,
            context.threshold_amount,
            context.remaining_amount,
            context.wallet_period,
        )

    @mockserver.json_handler(
        '/bank-core-statement/v2/wallets/balance/get', prefix=True,
    )
    def _mock_get_wallets_balance2(request):
        if context.need_timeout_exception:
            raise mockserver.TimeoutError()
        if context.explicit_wallets_specification:
            return {'balances': context.explicit_wallets_specification}
        return make_response_wallets_balance2(
            request.headers.get('X-Yandex-BUID'),
            context.balance_currency,
            context.balance_amount,
        )

    @mockserver.json_handler(
        '/bank-core-statement/v1/agreements/balance/get', prefix=True,
    )
    def _mock_get_agreements_balances(request):
        return {'agreements': context.agreements_balances}

    @mockserver.json_handler('/bank-core-statement/v1/limit/get/list')
    def _mock_limit_get_list(request):
        return {'limits': context.agreement_limits}

    def _get_transaction_list(request, cursor, limit):
        if context.need_timeout_exception:
            raise mockserver.TimeoutError()
        if context.needed_error_code:
            return mockserver.make_response(
                status=context.needed_error_code,
                json={'code': '', 'message': ''},
            )
        return make_response_transaction_list(
            cursor, limit, context.transactions_count,
        )

    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/get',
        prefix=True,
    )
    def _mock_get_transaction_list(request):
        cursor, page_size = (
            request.query.get('cursor'),
            request.query.get('page_size'),
        )
        if cursor and page_size:
            return mockserver.make_response(status=500)
        return _get_transaction_list(request, cursor, page_size)

    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions'
        '/grouped-by-status/get-by-agreement-id',
        prefix=True,
    )
    def _mock_get_transaction_list_by_agreement(request):
        assert request.query.get('agreement_id')
        return _get_transaction_list(
            request, request.query.get('cursor'), request.query.get('limit'),
        )

    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions'
        '/grouped-by-status/get-by-card-id',
        prefix=True,
    )
    def _mock_get_transaction_list_by_card(request):
        assert request.query.get('public_card_id')
        return _get_transaction_list(
            request, request.query.get('cursor'), request.query.get('limit'),
        )

    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
        prefix=True,
    )
    def _mock_get_transaction(request):
        if context.need_timeout_exception:
            raise mockserver.TimeoutError()
        if context.needed_error_code:
            return mockserver.make_response(
                status=context.needed_error_code,
                json={'code': '', 'message': ''},
            )
        return make_transactions(request.query.get('transaction_id'))

    @mockserver.json_handler('/bank-core-statement/v1/wallets/id/get')
    def _mock_wallets_id_get(request):
        if context.need_timeout_exception:
            raise mockserver.TimeoutError()
        if context.needed_error_code:
            return mockserver.make_response(
                status=context.needed_error_code,
                json={'code': '', 'message': ''},
            )
        return get_wallets_id(context.wallet_ids_count)

    context.wallets_balance_handler = _mock_get_wallets_balance
    context.wallets_balance2_handler = _mock_get_wallets_balance2
    context.transaction_list_handler = _mock_get_transaction_list
    context.trx_list_by_agreement_handler = (
        _mock_get_transaction_list_by_agreement
    )
    context.trx_list_by_card_handler = _mock_get_transaction_list_by_card
    context.agreements_balances_handler = _mock_get_agreements_balances
    context.limit_get_list_handler = _mock_limit_get_list
    context.transaction_handler = _mock_get_transaction
    context.wallet_id_get_handler = _mock_wallets_id_get

    return context


@pytest.fixture
def bank_applications_mock(mockserver):
    class Context:
        def __init__(self):
            self.get_applications_handler = None
            self.needed_error_code = None
            self.applications = None

    context = Context()

    @mockserver.json_handler(
        '/bank-applications/applications-internal/v1/get_applications',
    )
    def _get_applications_handler(request):
        if context.needed_error_code:
            return mockserver.make_response(
                status=context.needed_error_code,
                json={'code': '', 'message': ''},
            )
        if context.applications is None:
            return {'applications': []}
        return context.applications

    context.get_applications_handler = _get_applications_handler

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


@pytest.fixture
def bank_core_card_mock(mockserver):
    class Context:
        def __init__(self):
            self.info_by_trust_card_id_handler = None
            self.card_mapping_info = None

        def set_card_mapping_info(self, card_mapping_info):
            self.card_mapping_info = card_mapping_info

    context = Context()

    @mockserver.json_handler(
        '/bank-core-card/v1/card/mapping/info/by-trust-card-id',
    )
    def _mock_info_by_trust_card_id_handler(request):
        return context.card_mapping_info

    context.info_by_trust_card_id_handler = _mock_info_by_trust_card_id_handler

    return context
