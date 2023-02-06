# pylint: disable=redefined-outer-name
import pytest

import achievements_py3.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['achievements_py3.generated.service.pytest_plugins']


@pytest.fixture
def client_events_mocker(mockserver, mock_client_events):
    def wrapper(expect_event, expect_udids):
        class ClientEventsContext:
            def __init__(self, expect_event: str, expect_udids: set):
                self.expect_event = expect_event
                self.expect_udids = expect_udids
                self.pro_bulk_push = None

        ctx = ClientEventsContext(expect_event, expect_udids)

        @mock_client_events('/pro/v1/bulk-push')
        def _handler(request):
            body = request.json
            assert body['service'] == 'yandex.pro'
            input_udids = body['channels']['unique_contractor_ids']
            assert set(input_udids) == ctx.expect_udids
            assert body['event'] == ctx.expect_event
            return {}

        ctx.pro_bulk_push = _handler
        return ctx

    return wrapper
