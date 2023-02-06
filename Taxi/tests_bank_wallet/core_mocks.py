import copy

import pytest

from testsuite.utils import http


@pytest.fixture
def core_agreement_mock(mockserver):
    class Context:
        def __init__(self):
            self.agreements_list_handler = None
            self.agreements = []
            self.response_code = 200

        def set_agreements(self, agreements):
            self.agreements = agreements

        def set_response_code(self, code):
            self.response_code = code

    context = Context()

    @mockserver.json_handler('/bank-core-agreement/v1/agreement/list')
    def _agreements_list_handler(request):
        return mockserver.make_response(
            status=context.response_code,
            json={'agreements': context.agreements},
        )

    context.agreements_list_handler = _agreements_list_handler
    return context


@pytest.fixture
def core_card_mock(mockserver):
    class Context:
        def __init__(self):
            self.card_list_handler = None
            self.cards = []
            self.response_code = 200

        def set_cards(self, cards):
            self.cards = cards

        def set_response_code(self, code):
            self.response_code = code

    context = Context()

    @mockserver.json_handler('/bank-core-card/v1/card/info/list')
    def _card_list_mock(request):
        return mockserver.make_response(
            status=context.response_code, json={'cards': context.cards},
        )

    context.card_list_handler = _card_list_mock
    return context


@pytest.fixture
def bank_core_client_mock(mockserver):
    class Context:
        def __init__(self):
            self.get_user_status_handler = None
            self.user_status = None  # ANONYMOUS, IDENTIFIED, KYC, KYC_EDS
            self.needed_error_code = None

        def set_user_status(self, user_status='ANONYMOUS'):
            self.user_status = user_status

    context = Context()

    @mockserver.json_handler('/bank-core-client/v1/client/info/get')
    def _get_user_status_handler(request):
        if context.needed_error_code:
            return mockserver.make_response(
                status=context.needed_error_code,
                json={'code': '', 'message': ''},
            )
        if (context.user_status is None) or (
                context.user_status
                not in ['ANONYMOUS', 'IDENTIFIED', 'KYC', 'KYC_EDS']
        ):
            raise ValueError('No user_status assigned or invalid')
        return {
            'auth_level': context.user_status,
            'phone_number': '+70000000000',
        }

    context.get_user_status_handler = _get_user_status_handler

    return context


DATES = [f'2022-02-{str(day).zfill(2)}' for day in range(28, 0, -1)]
TIME_MARK = {
    'timestamp': '2022-03-23T19:06:03.557007Z',
    'creation_timestamp': '2022-03-23T19:06:03.557007+00:00',
    'cursor_key': 404,
    'cursor': '404',
    # cursor == base64(seconds_epoch:nanoseconds) in real faster-payments,
    # 'MDow' == 0:0 for the last transfer in history
    # cursor == str(cursor_key) for testing purposes
}

TOPUP_LOCALIZATION = {  # topup['payment']['payment_info']
    'ru': {'description': 'с карты Visa ···· 5368', 'name': 'Пополнение'},
    'en': {'description': 'from card Visa ···· 5368', 'name': 'Top up'},
}
PENDING_TOPUP = {
    'payment': {
        'payment_info': {
            'payment_id': '4cd35924-8d69-4653-93a6-e4aa99afc5ea',
            'creation_timestamp': '2021-11-18T15:03:59.147381+00:00',
            'money': {'amount': '999', 'currency': 'RUB'},
            'image': (
                'https://avatars.mdst.yandex.net/get-fintech/65575/income'
            ),
            'type': 'CREDIT',
        },
        'status': 'PROCESSING',
    },
    'cursor_key': 404,
}


class LimitedPendingContext:
    def __init__(self):
        self.http_status_code = 200
        self.amount = 10
        self.order = 'last'  # first, mixed
        # first - the newest (first in descending sorted list)
        # last - the oldest (last in descending sorted list)

    def set_amount(self, amount):
        assert 0 <= amount <= 14
        self.amount = amount

    def set_order(self, order):
        assert order in ('last', 'first', 'mixed')
        self.order = order

    def set_http_status_code(self, code):
        self.http_status_code = code


@pytest.fixture
def bank_topup_mock(mockserver):
    class Context(LimitedPendingContext):
        def __init__(self):
            super().__init__()
            self.get_pending_payments_handler = None

    context = Context()

    def get_topup(locale, date):
        topup = copy.deepcopy(PENDING_TOPUP)
        topup['payment']['payment_info'].update(TOPUP_LOCALIZATION[locale])
        timestamp = date + TIME_MARK['creation_timestamp'][len(date) :]
        topup['payment']['payment_info']['creation_timestamp'] = timestamp
        topup['cursor_key'] = int(date[-2:])
        return topup

    @mockserver.json_handler(
        '/bank-topup/topup-internal/v1/get_pending_payments',
    )
    def _get_pending_payments_handler(request: http.Request):
        if context.http_status_code != 200:
            return mockserver.make_response(
                status=context.http_status_code,
                json={'code': 'error_code', 'message': 'error_message'},
            )
        assert request.method == 'POST'
        assert request.json['buid'] == '1'
        locale = request.json['locale']
        assert locale in ('ru', 'en')
        payments = []
        if context.amount > 0:
            if context.order == 'first':
                dates = DATES[:14]
            elif context.order == 'last':
                dates = DATES[14:]
            elif context.order == 'mixed':
                dates = DATES[::2]
            else:
                raise RuntimeError('Wrong topups order')
            for date in dates[: context.amount]:
                payments.append(get_topup(locale, date))
        context.set_amount(10)
        context.set_order('last')
        limit = request.json['limit']
        assert limit > 0
        if 'cursor_key' in request.json:
            cursor_key = request.json['cursor_key']
            payments = [
                payment
                for payment in payments
                if payment['cursor_key'] < cursor_key
            ]
        return mockserver.make_response(
            status=200, json={'payments': payments[:limit]},
        )

    context.get_pending_payments_handler = _get_pending_payments_handler
    return context


PENDING_TRANSFER = {
    'c2c-details': {
        'bank-id': '100000000004',
        'phone': '+79123456789',
        'name': 'Иван Иванович И.',
    },
    'cursor': 'MDow',
    'debit_agreement_id': 'public_ag_EJCJcPWBQMGzlp9',
    'errors': [],
    'modified_date': '2022-03-23T19:06:03.557007Z',
    'money': {'amount': '111', 'currency': 'RUB'},
    'request_id': 'c8fe469a-3c83-4f7e-ad12-1417539a8b6a',
    'timestamp': '2022-03-23T19:06:03.557007Z',
    'transaction_id': 'c8fe469a-3c83-4f7e-ad12-1417539a8b6a',
}


@pytest.fixture
def bank_core_faster_payments_mock(mockserver):
    class Context(LimitedPendingContext):
        def __init__(self):
            super().__init__()
            self.list_pending_transfer = None

    context = Context()

    def get_transfer(date):
        transfer = copy.deepcopy(PENDING_TRANSFER)
        timestamp = date + TIME_MARK['timestamp'][len(date) :]
        transfer['timestamp'] = timestamp
        transfer['cursor'] = date[-2:]
        return transfer

    @mockserver.json_handler(
        '/bank-core-faster-payments/v1/transfer/pending/list',
    )
    def _list_pending_transfer(request: http.Request):
        if context.http_status_code != 200:
            return mockserver.make_response(
                status=100,
                json={'code': 'error_code', 'message': 'error_message'},
            )
        assert request.method == 'POST'
        assert request.headers['X-Yandex-BUID'] == '1'
        transfers = []
        if context.amount > 0:
            if context.order == 'first':
                dates = DATES[:14]
            elif context.order == 'last':
                dates = DATES[14:]
            elif context.order == 'mixed':
                dates = DATES[1::2]
            else:
                raise RuntimeError('Wrong transfers order')
            for date in dates[: context.amount]:
                transfers.append(get_transfer(date))
        context.set_amount(10)
        context.set_order('last')
        limit = request.json['limit']
        assert limit > 0
        if 'cursor' in request.json:
            cursor = request.json['cursor']
            transfers = [
                transfer
                for transfer in transfers
                if int(transfer['cursor']) < int(cursor)
            ]
        return mockserver.make_response(
            status=200, json={'transfers': transfers[:limit]},
        )

    context.list_pending_transfer = _list_pending_transfer
    return context
