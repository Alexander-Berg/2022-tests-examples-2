import pytest


@pytest.fixture(name='order_core', autouse=True)
def _order_core(mockserver):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def _mock(_):
        return {}

    return {}
