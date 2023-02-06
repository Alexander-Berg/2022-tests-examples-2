import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_performer_support_plugins import *  # noqa: F403 F401


@pytest.fixture(name='get_work_mode_in_same_day')
async def _get_work_mode(mockserver):
    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _mock_handler(request):
        return {
            'mode': {
                'name': 'eats_couriers_pedestrian',
                'started_at': '2021-06-30T13:13:56+03:00',
                'features': [{'name': 'eats_couriers_pedestrian'}],
            },
        }
