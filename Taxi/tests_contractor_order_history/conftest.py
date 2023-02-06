# pylint: disable=redefined-outer-name
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from contractor_order_history_plugins import *  # noqa: F403 F401


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]


@pytest.fixture(name='mock_contractor_order_history', autouse=True)
def contractor_order_history_mock(mockserver):
    class Context:
        def __init__(self):
            pass

        @staticmethod
        @mockserver.json_handler('/contractor-order-history/insert')
        def insert(request):
            return {}

        @staticmethod
        @mockserver.json_handler('/contractor-order-history/update')
        def update(request):
            return {}

    ctx = Context()
    return ctx
