"""
    Mocks /driver-trackstory/position API
"""

import pytest

from simulator.core import modules
from simulator.core.utils import current_time


@pytest.fixture(name='mock_simulator_driver_trackstory')
def _mock_simulator_driver_trackstory(mockserver):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock(request):
        result = []

        now = current_time.CurrentTime.get()

        for driver_id in request.json['driver_ids']:
            candidate = modules.CandidatesModel.get(driver_id)
            candidate.sync_position(timestamp=now)

            result.append(
                {
                    'position': {
                        'lat': candidate.info.position[1],
                        'lon': candidate.info.position[0],
                        'timestamp': int(now.timestamp()),
                    },
                    'type': 'adjusted',
                    'driver_id': candidate.id,
                },
            )

        return {'results': result}

    return _mock
