import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_card_pcidss_plugins import *  # noqa: F403 F401


@pytest.fixture
def core_card_mock(mockserver):
    class Context:
        def __init__(self):
            self.http_status_code = 200
            self.pin_set_handler = None
            self.details_get_handler = None
            self.pin_set_body = {
                'status': 'SUCCESS',
                'error': {'code': 'some_code', 'message': 'some_message'},
            }
            self.details_get_body = {
                'number': '1234123412341234',
                'cvv2': '123',
            }

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_pin_set_body(self, body):
            self.pin_set_body = body

        def set_get_details_body(self, body):
            self.details_get_body = body

    context = Context()

    @mockserver.json_handler('/bank-core-card/v1/card/pin/set')
    def _pin_set_handler(request):
        return mockserver.make_response(
            status=context.http_status_code, json=context.pin_set_body,
        )

    @mockserver.json_handler('/bank-core-card/v1/card/details/get')
    def _details_handler(request):
        return mockserver.make_response(
            status=context.http_status_code, json=context.details_get_body,
        )

    context.pin_set_handler = _pin_set_handler
    context.details_get_handler = _details_handler

    return context
