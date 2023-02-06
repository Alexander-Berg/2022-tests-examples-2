# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_proactive_support_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
def _mock_eats_core_order_support(mockserver):
    @mockserver.json_handler(
        '/eats-core-order-support/internal-api/v1/order-support/meta',
    )
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'operator': {
                    'login': 'dummy_operator_login',
                    'assigned_at': '2020-04-28T12:00:00+03:00',
                },
                'cancellation': {'is_notified_by_operator': False},
            },
        )

    return mock
