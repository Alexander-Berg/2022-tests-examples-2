# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from alt_offer_discount_plugins import *  # noqa: F403 F401


@pytest.fixture(name='mock_order_search', autouse=True)
def _mock_order_search(mockserver, request, load_json):
    marker_results = request.node.get_closest_marker('mock_order_search')

    if not marker_results:
        return

    request_json = load_json(marker_results.args[0])
    response_json = load_json(marker_results.args[1])

    # pylint: disable=unused-variable
    @mockserver.json_handler('/candidates/order-search')
    def mock_order_search(request_candidates):
        assert request_candidates.json == request_json
        return response_json


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'mock_order_search: mock candidates/order-search',
    )


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]
