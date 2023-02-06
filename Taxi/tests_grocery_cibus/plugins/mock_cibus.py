# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest

from .. import consts

GET_TOKEN_REQUEST_TYPE = 'get_oauth_tok'
CANCEL_PAYMENT_REQUEST_TYPE = 'cancel_application_pay'

DEFAULT_GET_TOKEN_RESPONSE = {
    'oauth_signin_url': consts.REDIRECT_URL,
    'msg': 'OK',
    'token': consts.DEFAULT_TOKEN,
    'code': 0,
}

DEFAULT_CANCEL_RESPONSE = {'msg': 'OK', 'code': 0}


@pytest.fixture(name='cibus')
def mock_cibus(mockserver):
    class Context:
        def __init__(self):
            self.get_token = HandleContext()
            self.cancel_payment = HandleContext()

    context = Context()

    @mockserver.json_handler('/cibus/main.py')
    def _mock(request):
        request_type = request.json.get('type', None)
        assert request_type is not None

        if request_type == GET_TOKEN_REQUEST_TYPE:
            handler = context.get_token
            handler(request)

            return handler.response_with(DEFAULT_GET_TOKEN_RESPONSE)

        if request_type == CANCEL_PAYMENT_REQUEST_TYPE:
            handler = context.cancel_payment
            handler(request)

            return handler.response_with(DEFAULT_CANCEL_RESPONSE)

        assert False, 'unknown request_type: ' + request_type
        return {}

    return context
