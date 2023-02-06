from typing import Any
from typing import Dict
from typing import Optional

import pytest


@pytest.fixture
def trust_clear_pending_success(mockserver):
    def _do_mock():
        @mockserver.json_handler(
            '/trust-payments/v2/payment_status/trust-basket-token/',
        )
        def _handler(request):
            resp_body = {
                'status': 'success',
                'purchase_token': 'trust-basket-token',
                'payment_status': 'cleared',
            }
            return mockserver.make_response(status=200, json=resp_body)

        @mockserver.json_handler(
            '/trust-payments/v2/payments/trust-basket-token/',
        )
        def _handler2(request):
            resp_body = {
                'status': 'success',
                'purchase_token': 'trust-basket-token',
                'payment_status': 'cleared',
            }
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def mock_trust_successful_clear(
        trust_clear_init_success, trust_clear_pending_success,
):
    # pylint: disable=redefined-outer-name
    def _do_mock():
        trust_clear_init_success()
        trust_clear_pending_success()

    return _do_mock


@pytest.fixture
def mock_trust_successful_refund(
        trust_create_refund_success, mock_trust_start_refund,
):
    # pylint: disable=redefined-outer-name
    def _do_mock():
        trust_create_refund_success()
        mock_trust_start_refund(status='success')

    return _do_mock


@pytest.fixture
def trust_clear_init_success(mockserver):
    def _do_mock(expect_headers: Optional[Dict[str, Any]] = None):
        @mockserver.json_handler(
            '/trust-payments/v2/payments/trust-basket-token/clear/',
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
                'purchase_token': 'trust-basket-token',
                'payment_status': 'authorized',
            }
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def trust_create_refund_success(mockserver):
    def _do_mock(
            expect_headers: Optional[Dict[str, Any]] = None,
            expect_body: Optional[Dict[str, Any]] = None,
            expected_service_token: Optional[str] = None,
    ):
        @mockserver.json_handler('/trust-payments/v2/refunds/')
        def _handler(request):
            _check_service_token(request, expected_service_token)
            if expect_headers is not None:
                headers = request.headers
                for name, expected_value in expect_headers.items():
                    if expected_value is None:
                        assert name not in headers
                    else:
                        assert headers[name] == expected_value
            if expect_body is not None:
                for name, expected_value in expect_body.items():
                    if expected_value is None:
                        assert name not in request.json
                    else:
                        assert request.json[name] == expected_value
            resp_body = {
                'status': 'success',
                'trust_refund_id': 'trust-refund-id',
            }
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def mock_check_refund(mockserver):
    def _do_mock(status, expect_headers: Optional[Dict[str, Any]] = None):
        @mockserver.json_handler('/trust-payments/v2/refunds/trust-refund-id/')
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
                'trust_refund_id': 'trust-refund-id',
            }
            return mockserver.make_response(status=200, json=resp_body)

    return _do_mock


@pytest.fixture
def mock_get_pass_params(patch):
    fn_path = (
        'transactions.internal.payment_gateways.trust.gateway.'
        'get_pass_params'
    )

    @patch(fn_path)
    async def get_pass_params(
            invoice,
            payment_type,
            trust_details,
            maybe_agglomerations_client,
            billing_payments_service_id,
            transaction_payload,
    ):
        return {'x': 1}

    return get_pass_params


@pytest.fixture
def stq_reschedule(patch):
    @patch(
        'transactions.generated.service.'
        'stq_client.plugin.QueueClient.reschedule',
    )
    async def reschedule(eta, task_id):
        pass

    return reschedule


@pytest.fixture
def mock_stq_agent_reschedule(mockserver):
    def do_mock(expected_queue: str):
        @mockserver.json_handler('/stq-agent/queues/api/reschedule')
        def _handler(request):
            assert request.json['queue_name'] == expected_queue
            return {}

    return do_mock


@pytest.fixture
def patch_random(patch):
    @patch('random.random')
    def _random():
        return 0


def _check_service_token(request, expected_service_token: Optional[str]):
    if expected_service_token is not None:
        assert request.headers['X-Service-Token'] == expected_service_token


@pytest.fixture
def mock_bp_admin_v1_issue_register(mockserver):
    def _do_mock():
        @mockserver.json_handler('/billing-payment-admin/v1/issue/register')
        def _handler(request):
            return mockserver.make_response(status=200, json={})

    return _do_mock
