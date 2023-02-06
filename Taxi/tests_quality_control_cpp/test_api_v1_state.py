import pytest


@pytest.mark.parametrize(
    'params, expected_code, expected_response',
    [
        (
            dict(id='1', type='driver'),
            200,
            dict(id='1', type='driver', exams=[]),
        ),
        (
            dict(id='1', type='driver'),
            200,
            dict(
                id='1',
                type='driver',
                exams=[
                    dict(
                        code='rqc',
                        enabled=False,
                        modified='2022-02-02T21:00:00+00:00',
                    ),
                ],
            ),
        ),
        (
            dict(id='1', type='ololo'),
            400,
            dict(
                code='INCORRECT_ENTITY_TYPE', message='Incorrect entity type',
            ),
        ),
        (
            dict(id='1', type='driver'),
            404,
            dict(code='ENTITY_NOT_FOUND', message='Entity not found in Qc'),
        ),
    ],
)
async def test_state_simple(
        taxi_quality_control_cpp,
        mockserver,
        params,
        expected_code,
        expected_response,
):
    @mockserver.handler('/quality-control/api/v1/state')
    def _api_v1_state(request):
        if expected_code == 200:
            return mockserver.make_response(status=200, json=expected_response)
        return mockserver.make_response('Some qc error', expected_code)

    response = await taxi_quality_control_cpp.get(
        'api/v1/state', params=params,
    )
    assert response.status_code == expected_code
    assert (
        response.headers['Content-Type'] == 'application/json; charset=utf-8'
    )
    if expected_response:
        assert response.json() == expected_response


@pytest.mark.now('2022-02-02T12:00:00+00:00')
async def test_state(taxi_quality_control_cpp, mockserver, load_json):
    params = dict(id='5d485be9e0eda8c4aafc4e92', type='driver')
    current_state = load_json('api_v1_state.json')

    @mockserver.handler('/quality-control/api/v1/state')
    def _api_v1_state(request):
        return mockserver.make_response(status=200, json=current_state)

    @mockserver.handler('/quality-control/api/v1/state/list')
    def _api_v1_state_list(request):
        cursor = request.query.get('cursor')
        if cursor:
            return mockserver.make_response(
                status=200, json=dict(items=[], cursor=cursor),
            )
        return mockserver.make_response(
            status=200, json=load_json('api_v1_state_list.json'),
        )

    response = await taxi_quality_control_cpp.get(
        'api/v1/state', params=params,
    )
    assert response.status_code == 200
    assert response.json() == current_state

    prev_state = current_state
    current_state = load_json('api_v1_state_updated.json')
    assert prev_state != current_state

    response = await taxi_quality_control_cpp.get(
        'api/v1/state', params=params,
    )
    assert response.status_code == 200
    assert response.json() == prev_state

    await taxi_quality_control_cpp.run_periodic_task(
        'driver-states-invalidator',
    )

    response = await taxi_quality_control_cpp.get(
        'api/v1/state', params=params,
    )
    assert response.status_code == 200
    assert response.json() == current_state
