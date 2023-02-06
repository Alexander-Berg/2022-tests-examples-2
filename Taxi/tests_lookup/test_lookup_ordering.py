import json

from tests_lookup import lookup_params


INTENT = 'direct-assignment'


def create_request():
    return {
        'intent': INTENT,
        'request': {
            'search': {
                'order': {
                    'id': '100',
                    'allowed_classes': ['econom'],
                    'request': {'source': {'geopoint': [1, 2]}},
                },
                'experiments': [
                    '1___1_test',
                    '1__test_22_02_2018',
                    '1__test_2',
                ],
                'user_experiments': ['taxiroute2', 'forced_surge'],
            },
            'candidates': [
                {
                    'id': 'c1',
                    'route_info': {
                        'time': 100,
                        'distance': 200,
                        'approximate': True,
                    },
                },
                {
                    'id': 'c2',
                    'route_info': {
                        'time': 200,
                        'distance': 200,
                        'approximate': False,
                    },
                },
                {
                    'id': 'c3',
                    'route_info': {
                        'time': 50,
                        'distance': 200,
                        'approximate': False,
                    },
                },
                {
                    'id': 'c4',
                    'route_info': {
                        'time': 250,
                        'distance': 300,
                        'approximate': True,
                    },
                },
                {
                    'id': 'c5',
                    'route_info': {
                        'time': 300,
                        'distance': 350,
                        'approximate': True,
                    },
                },
            ],
        },
    }


async def test_approximate(
        acquire_candidate, testpoint, mockserver, load_json,
):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates')
    def _driver_scoring(request):
        return mockserver.make_response(
            '{"error": {"text": "something-happened"}}', status=400,
        )

    @testpoint('ordering-response')
    def _ordering_response(data):
        assert data == load_json('approximate_response.json')

    @testpoint('ordering-request')
    def _ordering_request(data):
        return load_json('approximate_request.json')

    await acquire_candidate(lookup_params.create_params())
    assert _driver_scoring.has_calls


async def test_reposition_check(
        acquire_candidate, testpoint, mockserver, load_json,
):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates')
    def _driver_scoring(request):
        return mockserver.make_response(
            '{"error": {"text": "something-happened"}}', status=400,
        )

    @testpoint('ordering-response')
    def _ordering_response(data):
        assert data == load_json('reposition_response.json')

    @testpoint('ordering-request')
    def _ordering_request(data):
        return load_json('reposition_request.json')

    await acquire_candidate(lookup_params.create_params())
    assert _driver_scoring.has_calls


async def test_scoring_200(acquire_candidate, testpoint, mockserver):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates')
    def _driver_scoring(request):
        body = json.loads(request.get_data())['request']
        assert 'candidates' in body
        assert 'search' in body
        nonlocal metadata
        return {
            'candidates': [
                {'id': 'c3', 'score': 50, 'penalty': 0, 'metadata': metadata},
                {'id': 'c2', 'score': 200, 'penalty': 0},
                {'id': 'c1', 'score': 100, 'penalty': 1000},
            ],
        }

    @testpoint('ordering-response')
    def _ordering_response(data):
        assert data['source'] == 'scoring'
        candidates = data['candidates']
        assert len(candidates) == 3
        assert (
            candidates[0].get('id'),
            candidates[0].get('score'),
            candidates[0].get('penalty'),
            candidates[0].get('metadata'),
        ) == ('c3', 50, 0, metadata)
        assert (
            candidates[1].get('id'),
            candidates[1].get('score'),
            candidates[1].get('penalty'),
            candidates[1].get('metadata'),
        ) == ('c2', 200, 0, None)
        assert (
            candidates[2].get('id'),
            candidates[2].get('score'),
            candidates[2].get('penalty'),
            candidates[2].get('metadata'),
        ) == ('c1', 100, 1000, None)

    @testpoint('ordering-request')
    def _ordering_request(data):
        return create_request()

    metadata = {'reposition': {'mode': 'home'}}

    await acquire_candidate(lookup_params.create_params())
    assert _driver_scoring.has_calls


async def test_scoring_fallback(
        acquire_candidate,
        taxi_lookup,
        testpoint,
        mockserver,
        load_json,
        statistics,
):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates')
    def _driver_scoring(request):
        assert False, 'should\'nt be called'
        return mockserver.make_response('{}', status=200)

    @testpoint('ordering-response')
    def _ordering_response(data):
        assert data == load_json('reposition_response.json')

    @testpoint('ordering-request')
    def _ordering_request(data):
        request = load_json('reposition_request.json')
        request['intent'] = INTENT
        return request

    statistics.fallbacks = ['driver-scoring.%s.fallback-empty' % INTENT]
    await taxi_lookup.tests_control(invalidate_caches=True)
    await acquire_candidate(lookup_params.create_params())
    assert not _driver_scoring.has_calls


async def test_scoring_capture(
        acquire_candidate, taxi_lookup, testpoint, mockserver, statistics,
):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates')
    def _driver_scoring(request):
        if scoring_result == 'ok':
            return {
                'candidates': [
                    {'id': 'c3', 'score': 50, 'penalty': 0},
                    {'id': 'c2', 'score': 200, 'penalty': 0},
                    {'id': 'c1', 'score': 100, 'penalty': 1000},
                ],
            }
        if scoring_result == 'bad-id':
            return {
                'candidates': [
                    {'id': 'c-xxx-3', 'score': 50, 'penalty': 0},
                    {'id': 'c-xxx-2', 'score': 200, 'penalty': 0},
                    {'id': 'c-xxx-1', 'score': 100, 'penalty': 1000},
                ],
            }
        if scoring_result == 'empty':
            return {}
        if scoring_result == '400':
            return mockserver.make_response('data', status=400)
        if scoring_result == 'failed':
            return mockserver.make_response('failure', status=500)
        if scoring_result == 'network':
            raise mockserver.NetworkError()
        if scoring_result == 'timeout':
            raise mockserver.TimeoutError()
        if scoring_result == 'invalid-response-1':
            return {'candidates': 'not-an-array'}
        if scoring_result == 'invalid-response-2':
            return {'candidates': [{'id': 'c999', 'score': 50, 'penalty': 0}]}
        if scoring_result == 'invalid-response-3':
            return {'candidates': [{'id': 999, 'score': 50, 'penalty': 0}]}
        if scoring_result == 'empty-response':
            return {'candidates': []}
        assert False, 'should not be here: %s' % scoring_result
        return {}  # pylint

    @testpoint('ordering-request')
    def _ordering_request(data):
        return create_request()

    @testpoint('ordering-response')
    def _ordering_response(data):
        return

    async with statistics.capture(taxi_lookup) as capture:
        for test_mode in [
                'ok',
                'failed',
                'network',
                'timeout',
                '400',
                'invalid-response-1',
                'invalid-response-2',
                'invalid-response-3',
                'empty-response',
        ]:
            scoring_result = test_mode
            await acquire_candidate(lookup_params.create_params())

    stats = capture.statistics
    keys = list(stats.keys())
    for key in keys:
        if not key.startswith('driver-scoring'):
            stats.pop(key)
    assert stats == {
        'driver-scoring.%s.invalid_request' % INTENT: 1,
        'driver-scoring.%s.invalid_response' % INTENT: 3,
        'driver-scoring.%s.timeout' % INTENT: 1,
        'driver-scoring.%s.error' % INTENT: 2,
        'driver-scoring.%s.ok' % INTENT: 2,
        'driver-scoring.%s.empty' % INTENT: 1,
        'driver-scoring.%s.scored' % INTENT: 1,
    }


async def test_empty_response(acquire_candidate, mockserver):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates')
    def _driver_scoring(request):
        return mockserver.make_response('{"candidates":[]}', status=200)

    candidate = await acquire_candidate(lookup_params.create_params())
    assert _driver_scoring.has_calls
    assert not candidate
