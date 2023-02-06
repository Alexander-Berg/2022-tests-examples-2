import json

import pytest
# root conftest for service combo-matcher
pytest_plugins = ['combo_matcher_plugins.pytest_plugins']


@pytest.fixture(autouse=True)
def driver_scoring(mockserver):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _score_candidates_bulk(bulk_request):
        request_json = json.loads(bulk_request.get_data())

        responses = []
        for request in request_json['requests']:
            response = []
            candidates = sorted(request['candidates'], key=lambda x: x['id'])
            for i, candidate in enumerate(candidates):
                response.append(
                    {'id': candidate['id'], 'score': i * 1000, 'penalty': 0},
                )
            responses.append({'candidates': response})

        bulk_response = {'responses': responses}
        return mockserver.make_response(json=bulk_response, status=200)
