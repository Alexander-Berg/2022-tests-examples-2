# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from driver_orders_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture
def doaa_mock(mockserver):
    class Context:
        def __init__(self):
            self.json = {'status': 'complete'}
            self.status_code = 200
            self.request_body = {
                'park_id': 'park_id1',
                'origin': 'yandex_dispatch',
                'driver_profile_id': 'driver_id1',
                'setcar_id': 'order_id1',
                'should_notify': True,
            }

        def set_json(self, json):
            self.json = json

        def set_status_code(self, code):
            self.status_code = code

        def set_request_body(self, body):
            self.request_body = body

        def times_called(self):
            return (
                _doaa_mock_complete.times_called
                + _doaa_mock_cancelled.times_called
            )

    context = Context()

    def _mock_internal(request):
        assert request.headers.get('X-Yandex-Login')
        assert request.json == context.request_body
        return mockserver.make_response(
            status=context.status_code, json=context.json,
        )

    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order/status/complete',
    )
    def _doaa_mock_complete(request):
        return _mock_internal(request)

    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order/status/cancelled',
    )
    def _doaa_mock_cancelled(request):
        return _mock_internal(request)

    return context
