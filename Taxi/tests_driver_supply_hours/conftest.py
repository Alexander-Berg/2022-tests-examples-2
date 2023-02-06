# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from driver_supply_hours_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(name='_parks_mock')
def parks_mock(mockserver):
    class ParkContext:
        def __init__(self):
            self.statistics_working_time = None
            self.parks_response = None

        def set_parks_response(self, parks_response):
            self.parks_response = parks_response

    context = ParkContext()

    @mockserver.json_handler('/parks/driver-profiles/statistics/working-time')
    def _statistics_working_time(request):
        return context.parks_response

    context.statistics_working_time = _statistics_working_time
    return context
