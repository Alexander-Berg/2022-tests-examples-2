# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from dispatcher_access_control_plugins import *  # noqa: F403 F401 E501 I100
import pytest


@pytest.fixture
def mock_fleet_synchronizer(mockserver):
    @mockserver.json_handler(
        '/fleet-synchronizer/fleet-synchronizer/v1/sync/park/property',
    )
    def _mock_sync_handler(request):
        return {}

    return _mock_sync_handler
