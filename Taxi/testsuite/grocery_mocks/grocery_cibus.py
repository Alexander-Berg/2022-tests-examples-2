# pylint: disable=import-only-modules
import pytest

from .utils.handle_context import HandleContext


DEFAULT_PAYMENT_ORDER_ID = 'default-order-id'
DEFAULT_PAYMENT = {
    'status': 'init',
    'token': '620e8eef1db8d43ff3bf6355_qNdt4vl9XHGhQEn2afDo',
    'redirect_url': 'https://qav1.mysodexo.co.il/Auth.aspx',
    'finish_url': 'some-url.ru/finish',
    'application_id': 'D7120EAA-75D6-48F6-A95A-977E0ACC72F7',
    'created': '2020-03-03T10:04:37Z',
}

DEFAULT_PAYMENT_FAIL = {
    'status': 'fail',
    'token': '',
    'redirect_url': '',
    'application_id': 'D7120EAA-75D6-48F6-A95A-977E0ACC72F7',
}

DEFAULT_PAYMENT_ERROR = {'code': 'error code', 'message': 'some error message'}


@pytest.fixture(name='grocery_cibus')
def mock_grocery_cibus(mockserver):
    class Context:
        def __init__(self):
            self.cibus_status = HandleContext()

    context = Context()

    def _make_error_response(handler: HandleContext):
        error_code = handler.status_code
        body = handler.response_with(
            {'code': str(error_code), 'message': f'{error_code} error'},
        )
        return mockserver.make_response(json=body, status=error_code)

    @mockserver.json_handler('/grocery-cibus/internal/cibus/v1/status')
    def _mock_grocery_cibus_status(request):
        handler = context.cibus_status
        handler(request)

        if not handler.is_ok:
            return _make_error_response(handler)

        return handler.response_with(DEFAULT_PAYMENT)

    return context
