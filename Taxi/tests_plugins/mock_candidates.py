import json

import pytest


class CandidatesContext:
    def __init__(self):
        self.profiles = {'times_called': 0}


@pytest.fixture(autouse=True)
def mock_candidates(mockserver):
    candidates_context = CandidatesContext()

    @mockserver.json_handler('/candidates/profiles')
    def mock_profiles(request):
        body = json.loads(request.get_data())
        drivers = body['driver_ids']
        result = []
        for driver in drivers:
            data = {}
            data['dbid'] = driver['dbid']
            data['uuid'] = driver['uuid']
            data['classes'] = ['econom', 'business']
            data['position'] = [33.0, 55.0]
            result.append(data)
        candidates_context.profiles['times_called'] += 1
        return {'drivers': result}

    return candidates_context
