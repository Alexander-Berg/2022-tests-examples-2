"""
    Mocks /candidates/order-satisfy API
"""

import pytest

from simulator.core import modules


@pytest.fixture(name='mock_simulator_order_satisfy')
def _mock_simulator_order_satisfy(mockserver):
    @mockserver.json_handler('/candidates/order-satisfy')
    def _mock(request):
        result = []

        for driver_id in request.json['driver_ids']:
            candidate = modules.CandidatesModel.get(driver_id)

            result.append(
                {
                    'classes': candidate.info.classes,
                    'dbid': candidate.info.park_id,
                    'uuid': candidate.info.driver_profile_id,
                    'id': candidate.id,
                    'position': candidate.info.position,
                    'status': {'orders': [], 'status': 'online'},
                    'transport': {'type': candidate.info.transport_type},
                    'is_satisfied': True,
                    'reasons': [],
                },
            )

        return {'candidates': result}

    return _mock
