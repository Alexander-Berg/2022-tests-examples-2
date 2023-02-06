import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_audit_logger.mock_bank_audit import bank_audit  # noqa: F401
from bank_cashback_processing_plugins import *  # noqa: F403 F401


@pytest.fixture
def trust_mock(mockserver):
    class Context:
        def __init__(self):
            self.basket = {
                'purchase_token': 'purchase_token',
                'amount': '100',
                'currency': 'RUB',
                'payment_status': 'not_started',
                'payment_timeout': '1200.00',
                'start_ts': '1630656576.841',
                'final_status_ts': '1630656600.841',
                'paymethod_id': 'card-xc153df956eadfc0868925ed6',
                'payment_method': 'card',
                'orders': [
                    {
                        'order_id': '165469887',
                        'order_ts': '1630656576.841',
                        'orig_amount': '100.00',
                        'paid_amount': '100.00',
                    },
                ],
            }

            self.refund_status = None
            self.trust_refund_id = None
            self.basket_info_handler = None
            self.basket_create_handler = None
            self.basket_start_handler = None
            self.payment_methods_handler = None
            self.account_handler = None
            self.create_refund_handler = None
            self.refund_status_handler = None
            self.start_refund_handler = None

            self.has_bonus_account = False

        def set_payment_status(self, status):
            self.basket['payment_status'] = status

        def set_has_account(self, has_bonus_account):
            self.has_bonus_account = has_bonus_account

        def set_refund_status(self, status):
            self.refund_status = status

        def set_refund_id(self, refund_id):
            self.trust_refund_id = refund_id

    context = Context()

    @mockserver.json_handler(
        r'/bank-trust-payments/trust-payments/v2/topup/'
        r'(?P<purchase_token>\w+)',
        regex=True,
    )
    def _basket_info_handler(request, purchase_token):
        assert request.method == 'GET'
        if purchase_token != context.basket['purchase_token']:
            return mockserver.make_response(
                status=404, json={'status': 'error'},
            )
        return mockserver.make_response(status=200, json=context.basket)

    @mockserver.json_handler(
        r'/bank-trust-payments/trust-payments/v2/topup/'
        r'(?P<purchase_token>\w+)/start',
        regex=True,
    )
    def _basket_start_handler(request, purchase_token):
        assert request.method == 'POST'
        if purchase_token != context.basket['purchase_token']:
            return mockserver.make_response(
                status=404, json={'status': 'error'},
            )
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/topup')
    def _basket_create_handler(request):
        context.basket['purchase_token'] = 'purchase_token'
        context.basket['amount'] = request.json['amount']
        context.basket['currency'] = request.json['currency']

        assert request.method == 'POST'
        return mockserver.make_response(
            status=201, json={'purchase_token': 'purchase_token'},
        )

    @mockserver.json_handler(
        '/bank-trust-payments/trust-payments/v2/payment-methods',
    )
    def _payment_methods_handler(request):
        assert request.method == 'GET'
        assert request.headers.get('X-Uid')

        return mockserver.make_response(
            status=200,
            json={
                'bound_payment_methods': [
                    {
                        'currency': 'USD',
                        'payment_method': 'yandex_account',
                        'id': 'usd_id',
                    },
                    {
                        'currency': 'RUB',
                        'payment_method': 'yandex_account',
                        'id': 'rub_id',
                    },
                ],
            },
        )

    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/account')
    def _account_handler(request):
        assert request.method == 'POST'
        assert request.headers.get('X-Uid')
        assert request.json.get('currency')

        status = 200 if context.has_bonus_account else 201

        return mockserver.make_response(
            status=status,
            json={
                'status': 'success',
                'currency': 'RUB',
                'id': 'w/4808feca-1b86-537a-86e1-f934875c1223',
                'payment_method_id': (
                    'yandex_account-w/4808feca-1b86-537a-86e1-f934875c1223'
                ),
            },
        )

    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/refunds')
    def _create_refund_handler(request):
        assert request.method == 'POST'
        assert 'pass_params' not in request.json
        if request.json['purchase_token'] != context.basket['purchase_token']:
            return mockserver.make_response(
                status=404, json={'status': 'error'},
            )
        return mockserver.make_response(
            status=200,
            json={
                'trust_refund_id': context.trust_refund_id,
                'status': 'success',
            },
        )

    @mockserver.json_handler(
        r'/bank-trust-payments/trust-payments/v2/refunds/(?P<refund_id>\w+)',
        regex=True,
    )
    def _refund_status_handler(request, refund_id):
        assert request.method == 'GET'
        return mockserver.make_response(
            status=200, json={'status': context.refund_status},
        )

    @mockserver.json_handler(
        r'/bank-trust-payments/trust-payments/v2/refunds/'
        r'(?P<refund_id>\w+)/start',
        regex=True,
    )
    def _start_refund_handler(request, refund_id):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=200, json={'status': context.refund_status},
        )

    context.basket_info_handler = _basket_info_handler
    context.basket_start_handler = _basket_start_handler
    context.basket_create_handler = _basket_create_handler
    context.payment_methods_handler = _payment_methods_handler
    context.account_handler = _account_handler
    context.create_refund_handler = _create_refund_handler
    context.refund_status_handler = _refund_status_handler
    context.start_refund_handler = _start_refund_handler

    return context


@pytest.fixture
def _calculator_mock(mockserver):
    @mockserver.json_handler(
        '/bank-cashback-calculator/cashback-calculator-internal/v1/calculate',
    )
    def _mock_internal_calculator(request):
        return mockserver.make_response(
            status=200,
            json={
                'rules': [
                    {
                        'rule_id': 'id_1',
                        'ticket': 'ticket',
                        'issuer': 'issuer',
                        'campaign_name': 'campaign_name',
                        'cashback': {'amount': '1.11', 'currency': 'RUB'},
                    },
                    {
                        'rule_id': 'id_2',
                        'ticket': 'ticket',
                        'issuer': 'issuer',
                        'campaign_name': 'campaign_name',
                        'cashback': {'amount': '11.1', 'currency': 'RUB'},
                    },
                ],
            },
        )

    _calculator_mock.calc_handle = _mock_internal_calculator
    return _calculator_mock


@pytest.fixture
def _userinfo_mock(mockserver):
    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _mock_buid_info(request):
        return {
            'buid_info': {
                'buid': 'bank_uid',
                'yandex_uid': 'yandex_uid',
                'phone_id': 'phone_id',
            },
        }

    _userinfo_mock.buid_info_handle = _mock_buid_info
    return _userinfo_mock


@pytest.fixture
def _blackbox_mock(mockserver):
    @mockserver.json_handler('/blackbox/blackbox')
    def _mock_userinfo(request):
        assert request.query == {
            'attributes': '1015',
            'uid': 'yandex_uid',
            'userip': 'fake_ip',
            'format': 'json',
            'method': 'userinfo',
        }
        return {'users': [{'id': 'yandex_uid', 'attributes': {'1015': '1'}}]}

    _blackbox_mock.userinfo_handle = _mock_userinfo
    return _blackbox_mock


@pytest.fixture
def _stq_mock(mockserver):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        return {}

    _stq_mock.schedule_handle = _mock_stq_schedule
    _stq_mock.reschedule_handle = _mock_stq_reschedule
    return _stq_mock
