# pylint: disable=E0401
from grocery_mocks.utils.handle_context import HandleContext
import pytest

from tests_grocery_payments_methods import consts


@pytest.fixture(name='card_antifraud')
def mock_card_antifraud(mockserver):
    class Context:
        def __init__(self):
            self.verifications = HandleContext()
            self.verifications_status = HandleContext()

    context = Context()

    @mockserver.json_handler('card-antifraud/4.0/payment/verifications')
    def _mock_payment_verifications(request):
        context.verifications.process(
            request_body=request.json, request_headers=request.headers,
        )

        if not context.verifications.is_ok:
            return mockserver.make_response(
                status=context.verifications.status_code,
            )

        return consts.VERIFICATION_RESPONSE

    @mockserver.json_handler('card-antifraud/4.0/payment/verifications/status')
    def _mock_payment_verifications_status(request):
        context.verifications_status.process(
            request_body=request.query, request_headers=request.headers,
        )

        if not context.verifications_status.is_ok:
            return mockserver.make_response(
                status=context.verifications_status.status_code,
            )

        return consts.VERIFICATION_STATUS_RESPONSE

    return context
