# pylint: disable=wildcard-import, unused-wildcard-import, import-error, C0411

from driver_tutorials_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture
def unique_drivers(mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _mock(request):
        assert request.json == {'profile_id_in_set': ['park_1_driver_1']}
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'park_1_driver_1',
                    'data': {'unique_driver_id': 'driver_unique_1'},
                },
            ],
        }


@pytest.fixture(name='mock_driver_trackstory')
def _driver_trackstory(mockserver):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock(request):
        return {
            # moscow
            'position': {'lon': 37.590533, 'lat': 55.733863, 'timestamp': 3},
            'type': 'raw',
        }
