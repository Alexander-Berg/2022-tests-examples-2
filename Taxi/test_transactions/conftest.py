# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
import uuid

from aiohttp import web
import pytest

import transactions.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['transactions.generated.service.pytest_plugins']


@pytest.fixture(name='mock_experiments3')
def my_mock_experiments3(mockserver):
    class Context:
        def __init__(self):
            self.crutches = None
            self.handler = None
            self.expected_uid = '123'

        def set_crutches(self, crutches):
            self.crutches = crutches

        @property
        def times_called(self):
            return self.handler.times_called

    context = Context()

    def _make_values(crutches):
        return [
            {
                'name': '@lol4t0 crutches',
                'value': {'crutches': list(crutches)},
            },
        ]

    @mockserver.json_handler('/experiments3/v1/experiments')
    def _handler(request):
        if context.crutches is not None:
            assert request.json == {
                'consumer': 'crutches',
                'args': [
                    {
                        'name': 'yandex_uid',
                        'type': 'string',
                        'value': context.expected_uid,
                    },
                ],
            }
            return {'items': _make_values(context.crutches)}
        return {'items': []}

    context.handler = _handler
    return context


@pytest.fixture
def personal_tins_bulk_retrieve(mockserver):
    def _do_mock():
        @mockserver.json_handler('/personal/v1/tins/bulk_retrieve')
        def _handler(request):
            ids = sorted(item['id'] for item in request.json['items'])
            resp_body = {
                'items': [
                    {'id': tin_id, 'value': str(i)}
                    for i, tin_id in enumerate(ids)
                ],
            }
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def uantifraud_allow(mock_uantifraud):
    @mock_uantifraud('/v1/payment/check')
    async def handler(request):
        return web.json_response({'status': 'allow'})

    return handler


@pytest.fixture
def uantifraud_block(mock_uantifraud):
    @mock_uantifraud('/v1/payment/check')
    async def handler(request):
        return web.json_response({'status': 'block'})

    return handler


@pytest.fixture
def uantifraud_500(mock_uantifraud):
    @mock_uantifraud('/v1/payment/check')
    async def handler(request):
        return web.Response(status=500)

    return handler


@pytest.fixture
def mock_uuid4(patch):
    @patch('uuid.uuid4')
    def uuid4():
        return uuid.UUID('11111111111111111111111111111111')

    return uuid4


@pytest.fixture
def personal_phones_retrieve(mockserver):
    def _do_mock():
        @mockserver.json_handler('/personal/v1/phones/retrieve')
        def _handler(request):
            resp_body = {
                'value': '+79999999999',
                'id': '6fda7ec82df145ec95de983070a3640c',
            }
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def personal_emails_retrieve(mockserver):
    def _do_mock():
        @mockserver.json_handler('/personal/v1/emails/retrieve')
        def _handler(request):
            resp_body = {
                'value': 'x@example.com',
                'id': '6fda7ec82df145ec95de983070a3640c',
            }
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def personal_phones_store(mockserver):
    def _do_mock(http_status=200):
        @mockserver.json_handler('/personal/v1/phones/store')
        def _handler(request):
            phone = request.json['value']
            resp_body = {
                'value': phone,
                'id': 'ef65e0f5b3274f7a9b8eb6bc7152b88f',
            }
            return mockserver.make_response(status=http_status, json=resp_body)

    return _do_mock


@pytest.fixture
def personal_emails_store(mockserver):
    def _do_mock(http_status=200):
        @mockserver.json_handler('/personal/v1/emails/store')
        def _handler(request):
            email = request.json['value']
            resp_body = {
                'value': email,
                'id': '4c3a6de6758742d0963496a9ac95663c',
            }
            return mockserver.make_response(status=http_status, json=resp_body)

    return _do_mock


@pytest.fixture
def personal_tins_bulk_store(mockserver):
    def _do_mock(http_status=200):
        @mockserver.json_handler('/personal/v1/tins/bulk_store')
        def _handler(request):
            tins = sorted(item['value'] for item in request.json['items'])
            resp_body = {
                'items': [
                    {'id': str(tin_id), 'value': tin}
                    for tin_id, tin in enumerate(tins)
                ],
            }
            return mockserver.make_response(status=http_status, json=resp_body)

    return _do_mock


@pytest.fixture
def fill_service_orders_success(mockserver):
    def _do_mock(
            expect: Optional[Dict[str, Any]] = None,
            return_input_order_id=False,
    ):
        @mockserver.json_handler('/trust-payments/v2/orders/', prefix=True)
        def _handler(request):
            def _post_handler(request):
                assert 'X-Uid' in request.headers
                if expect is not None:
                    req_body = request.json
                    for key, expected_value in expect.items():
                        if expected_value is None:
                            assert key not in req_body
                        else:
                            assert req_body[key] == expected_value
                resp_body = {
                    'status': 'success',
                    'status_code': 'created',
                    'order_id': 'some_service_order_id',
                }
                if return_input_order_id:
                    resp_body['order_id'] = request.json['order_id']
                return mockserver.make_response(status=200, json=resp_body)

            def _get_handler(request):
                assert 'X-Uid' in request.headers
                resp_body = {
                    'status': 'error',
                    'status_code': 'order_not_found',
                }
                return mockserver.make_response(status=404, json=resp_body)

            if request.method == 'GET':
                return _get_handler(request)
            assert request.method == 'POST'
            return _post_handler(request)

        return _handler

    return _do_mock


@pytest.fixture
def mock_get_service_order(mockserver):
    def _do_mock(
            order_id,
            status,
            status_code,
            expect_headers: Optional[Dict[str, Any]] = None,
    ):
        @mockserver.json_handler(f'/trust-payments/v2/orders/{order_id}')
        def _handler(request):
            assert request.method == 'GET'
            assert 'X-Uid' in request.headers
            if expect_headers is not None:
                headers = request.headers
                for name, expected_value in expect_headers.items():
                    if expected_value is None:
                        assert name not in headers
                    else:
                        assert headers[name] == expected_value
            resp_body = {
                'status': status,
                'status_code': status_code,
                'order_id': order_id,
            }
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def cardstorage_card(mockserver):
    def _do_mock(valid: bool = True):
        @mockserver.json_handler('/cardstorage/v1/card')
        def _handler(request):
            resp_body = {
                'card_id': '<card_id>',
                'billing_card_id': '<billing_card_id>',
                'permanent_card_id': '<permanent_card_id>',
                'currency': 'RUB',
                'expiration_month': 1,
                'expiration_year': 2020,
                'number': '<number>',
                'owner': '<owner>',
                'possible_moneyless': False,
                'region_id': '<region_id>',
                'regions_checked': [],
                'system': '<system>',
                'valid': valid,
                'bound': True,
                'unverified': False,
                'busy': False,
                'busy_with': [],
                'from_db': True,
            }
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def cardstorage_update_card(mockserver):
    def _do_mock(requests: list = None):
        @mockserver.json_handler('/cardstorage/v1/update_card')
        def _handler(request):
            if requests is not None:
                requests.append(request.json)
            resp_body = {}
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def mock_trust_check_basket(mockserver):
    def _do_mock(
            purchase_token,
            payment_status,
            status: str = None,
            status_code: str = None,
            status_desc: str = None,
            user_phone: Optional[str] = None,
            user_email: Optional[str] = None,
            orders: Optional[List[dict]] = None,
            receipt: Optional[str] = None,
            clearing_receipt: Optional[str] = None,
            terminal_id: Optional[int] = 12345,
            uid: Optional[str] = None,
            clear_ts: Optional[str] = None,
            expect_headers: Optional[Dict[str, Any]] = None,
            resp_body: Optional[Dict[str, Any]] = None,
    ):
        @mockserver.json_handler(
            f'/trust-payments/v2/payment_status/{purchase_token}/',
        )
        def _handler(request):
            assert 'X-Uid' in request.headers
            if expect_headers is not None:
                headers = request.headers
                for name, expected_value in expect_headers.items():
                    if expected_value is None:
                        assert name not in headers
                    else:
                        assert headers[name] == expected_value
            nonlocal resp_body
            if resp_body is not None:
                return mockserver.make_response(status=200, json=resp_body)
            resp_body = {
                'status': 'success',
                'purchase_token': purchase_token,
                'payment_status': payment_status,
            }
            if status:
                resp_body['status'] = status
            if status_code:
                resp_body['status_code'] = status_code
            if status_desc:
                resp_body['status_desc'] = status_desc
            if user_phone:
                resp_body['user_phone'] = user_phone
            if user_email:
                resp_body['user_email'] = user_email
            if orders is not None:
                resp_body['orders'] = []
            if receipt is not None:
                resp_body['fiscal_receipt_url'] = receipt
            if clearing_receipt is not None:
                resp_body['fiscal_receipt_clearing_url'] = clearing_receipt
            if terminal_id is not None:
                resp_body['terminal'] = {'id': terminal_id}
            if uid is not None:
                resp_body['uid'] = uid
            if clear_ts is not None:
                resp_body['clear_ts'] = clear_ts
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def mock_trust_check_basket_full(mockserver):
    def _do_mock(
            purchase_token,
            payment_status,
            status: str = None,
            status_code: str = None,
            status_desc: str = None,
            user_phone: Optional[str] = None,
            user_email: Optional[str] = None,
            orders: Optional[List[dict]] = None,
            receipt: Optional[str] = None,
            clearing_receipt: Optional[str] = None,
            terminal_id: Optional[int] = 12345,
            uid: Optional[str] = None,
            clear_ts: Optional[str] = None,
            expect_headers: Optional[Dict[str, Any]] = None,
            resp_body: Optional[Dict[str, Any]] = None,
    ):
        @mockserver.json_handler(
            f'/trust-payments/v2/payments/{purchase_token}/',
        )
        def _handler(request):
            assert 'X-Uid' in request.headers
            if expect_headers is not None:
                headers = request.headers
                for name, expected_value in expect_headers.items():
                    if expected_value is None:
                        assert name not in headers
                    else:
                        assert headers[name] == expected_value
            nonlocal resp_body
            if resp_body is not None:
                return mockserver.make_response(status=200, json=resp_body)
            resp_body = {
                'status': 'success',
                'purchase_token': purchase_token,
                'payment_status': payment_status,
            }
            if status:
                resp_body['status'] = status
            if status_code:
                resp_body['status_code'] = status_code
            if status_desc:
                resp_body['status_desc'] = status_desc
            if user_phone:
                resp_body['user_phone'] = user_phone
            if user_email:
                resp_body['user_email'] = user_email
            if orders is not None:
                resp_body['orders'] = orders
            if receipt is not None:
                resp_body['fiscal_receipt_url'] = receipt
            if clearing_receipt is not None:
                resp_body['fiscal_receipt_clearing_url'] = clearing_receipt
            if terminal_id is not None:
                resp_body['terminal'] = {'id': terminal_id}
            if uid is not None:
                resp_body['uid'] = uid
            if clear_ts is not None:
                resp_body['clear_ts'] = clear_ts
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def mock_trust_check_refund(mockserver):
    def _do_mock(
            trust_refund_id,
            receipt: Optional[str] = None,
            expect_headers: Optional[Dict[str, Any]] = None,
            status: str = 'success',
    ):
        @mockserver.json_handler(
            f'/trust-payments/v2/refunds/{trust_refund_id}/',
        )
        def _handler(request):
            assert 'X-Uid' in request.headers
            if expect_headers is not None:
                headers = request.headers
                for name, expected_value in expect_headers.items():
                    if expected_value is None:
                        assert name not in headers
                    else:
                        assert headers[name] == expected_value
            resp_body = {
                'status': status,
                'status_desc': 'refund sent to payment system',
            }
            if receipt is not None:
                resp_body['fiscal_receipt_url'] = receipt
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def mock_trust_resize(mockserver):
    def _do_mock(
            purchase_token: str,
            service_order_id: str,
            expected_body: Optional[Dict[str, Any]] = None,
    ):
        url = (
            f'/trust-payments/v2/payments/'
            f'{purchase_token}/orders/{service_order_id}/resize'
        )

        @mockserver.json_handler(url)
        def _handler(request):
            assert 'X-Uid' in request.headers
            if expected_body is not None:
                body = request.json
                for key, expected_value in expected_body.items():
                    if expected_value is None:
                        assert key not in body
                    else:
                        assert body[key] == expected_value
            resp_body = {
                'status': 'success',
                'status_code': 'payment_is_updated',
            }
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def mock_trust_create_topup(mockserver):
    def _do_mock(
            purchase_token: str,
            pass_params: Optional[dict],
            expected_service_token: Optional[str] = None,
            expected_product_id: Optional[str] = None,
            expected_fiscal_nds: Optional[str] = None,
            expected_fiscal_title: Optional[str] = None,
    ):
        @mockserver.json_handler(f'/trust-payments/v2/topup/')
        def _handler(request):
            req_body = request.json
            if pass_params is None:
                assert 'pass_params' not in req_body
            else:
                assert req_body['pass_params'] == pass_params
            if expected_product_id is not None:
                assert req_body['product_id'] == expected_product_id
            if expected_fiscal_nds is not None:
                assert req_body['fiscal_nds'] == expected_fiscal_nds
            if expected_fiscal_title is not None:
                assert req_body['fiscal_title'] == expected_fiscal_title
            _check_service_token(request, expected_service_token)
            resp_body = {
                'status': 'success',
                'status_code': 'payment_created',
                'purchase_token': purchase_token,
            }
            return mockserver.make_response(status=201, json=resp_body)

    return _do_mock


@pytest.fixture
def mock_trust_start_topup(mockserver):
    def _do_mock(
            purchase_token: str,
            expected_service_token: Optional[str] = None,
            expect_headers: Optional[Dict[str, Any]] = None,
    ):
        url = f'/trust-payments/v2/topup/{purchase_token}/start/'

        @mockserver.json_handler(url)
        def _handler(request):
            assert 'X-Uid' in request.headers
            if expect_headers is not None:
                headers = request.headers
                for name, expected_value in expect_headers.items():
                    if expected_value is None:
                        assert name not in headers
                    else:
                        assert headers[name] == expected_value
            _check_service_token(request, expected_service_token)
            resp_body = {
                'status': 'success',
                'payment_status': 'started',
                'orders': [{'order_id': f'{purchase_token}-service-order-id'}],
            }
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def mock_trust_check_topup(mockserver):
    def _do_mock(
            purchase_token: str,
            expected_service_token: Optional[str] = None,
            expect_headers: Optional[Dict[str, Any]] = None,
    ):
        @mockserver.json_handler(f'/trust-payments/v2/topup/{purchase_token}/')
        def _handler(request):
            assert 'X-Uid' in request.headers
            if expect_headers is not None:
                headers = request.headers
                for name, expected_value in expect_headers.items():
                    if expected_value is None:
                        assert name not in headers
                    else:
                        assert headers[name] == expected_value
            _check_service_token(request, expected_service_token)
            resp_body = {
                'status': 'success',
                'payment_status': 'cleared',
                'orders': [{'order_id': f'{purchase_token}-service-order-id'}],
            }
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def mock_trust_successful_basket(
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
):
    def _do_mock(purchase_token, expected_orders=None, expected_back_url=None):
        mock_trust_create_basket(
            purchase_token,
            expected_orders=expected_orders,
            expected_back_url=expected_back_url,
        )
        mock_trust_pay_basket(purchase_token, payment_status='started')
        mock_trust_check_basket(purchase_token, payment_status='authorized')
        mock_trust_check_basket_full(
            purchase_token, payment_status='authorized',
        )

    return _do_mock


@pytest.fixture
def mock_trust_successful_compensation(
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
):
    # pylint: disable=invalid-name
    def _do_mock(purchase_token):
        mock_trust_create_basket(purchase_token)
        mock_trust_pay_basket(purchase_token, payment_status='cleared')
        mock_trust_check_basket(
            purchase_token=purchase_token, payment_status='cleared',
        )
        mock_trust_check_basket_full(
            purchase_token=purchase_token, payment_status='cleared',
        )

    return _do_mock


@pytest.fixture
def mock_trust_create_basket(mockserver):
    def _do_mock(
            purchase_token: str,
            status: str = 'success',
            status_code: Optional[str] = None,
            expected_service_token: Optional[str] = None,
            expected_orders: Optional[List[dict]] = None,
            expected_back_url: Optional[str] = None,
    ):
        @mockserver.json_handler('/trust-payments/v2/payments/')
        def _handler(request):
            _check_service_token(request, expected_service_token)
            if expected_orders is not None:
                assert request.json['orders'] == expected_orders
            assert request.json.get('back_url') == expected_back_url
            resp_body = {'status': status, 'purchase_token': purchase_token}
            if request.json.get('show_trust_payment_id'):
                resp_body['trust_payment_id'] = 'trust-payment-id'
            if status_code is not None:
                resp_body['status_code'] = status_code
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def mock_trust_pay_basket(mockserver):
    def _do_mock(
            purchase_token,
            payment_status,
            status: Optional[str] = None,
            status_code: Optional[str] = None,
            clear_ts: Optional[str] = None,
            expect_headers: Optional[Dict[str, Any]] = None,
    ):
        @mockserver.json_handler(
            f'/trust-payments/v2/payments/{purchase_token}/start/',
        )
        def _handler(request):
            assert 'X-Uid' in request.headers
            if expect_headers is not None:
                headers = request.headers
                for name, expected_value in expect_headers.items():
                    if expected_value is None:
                        assert name not in headers
                    else:
                        assert headers[name] == expected_value
            resp_body = {
                'status': 'success',
                'purchase_token': purchase_token,
                'payment_status': payment_status,
            }
            if status_code is not None:
                resp_body['status_code'] = status_code
            if status is not None:
                resp_body['status'] = status
            if clear_ts is not None:
                resp_body['clear_ts'] = clear_ts
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def mock_trust_start_refund(mockserver):
    def _do_mock(
            status,
            expected_service_token: Optional[str] = None,
            expect_headers: Optional[Dict[str, Any]] = None,
            trust_refund_id: str = 'trust-refund-id',
    ):
        @mockserver.json_handler(
            f'/trust-payments/v2/refunds/{trust_refund_id}/start/',
        )
        def _handler(request):
            assert 'X-Uid' in request.headers
            if expect_headers is not None:
                headers = request.headers
                for name, expected_value in expect_headers.items():
                    if expected_value is None:
                        assert name not in headers
                    else:
                        assert headers[name] == expected_value
            _check_service_token(request, expected_service_token)
            resp_body = {'status': status, 'trust_refund_id': trust_refund_id}
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def mock_trust_unhold(mockserver):
    def _do_mock(purchase_token: str, status_code: str):
        url = f'/trust-payments/v2/payments/{purchase_token}/unhold'

        @mockserver.json_handler(url)
        def _handler(request):
            assert 'X-Uid' in request.headers
            resp_body = {'status': 'success', 'status_code': status_code}
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


def _check_service_token(request, expected_service_token: Optional[str]):
    if expected_service_token is not None:
        assert request.headers['X-Service-Token'] == expected_service_token


logger = logging.getLogger('transactions')
logger.setLevel(logging.DEBUG)
