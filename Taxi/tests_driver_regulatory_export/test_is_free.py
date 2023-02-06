import pytest


@pytest.mark.config(
    DRIVER_REGULATORY_ON_ORDER_STATUSES={'__default__': ['transporting']},
    DRIVER_REGULATORY_DETECT_FREE_BY_STATUS=True,
)
@pytest.mark.parametrize(
    'is_free, statuses, should_be_free',
    [
        pytest.param(
            False, ['waiting'], True, id='driver is waiting, not on order',
        ),
        pytest.param(
            True,
            ['complete', 'transporting'],
            True,
            id='driver is free from candidates, so he is free unconditionally',
        ),
        pytest.param(
            False,
            ['driving', 'transporting'],
            False,
            id='driver is transporting, so he should be busy',
        ),
        pytest.param(True, [], True, id='driver is totally free'),
        pytest.param(
            False,
            [],
            True,
            id='driver has no orders, so he is free for deptrans',
        ),
    ],
)
async def test_is_free(
        taxi_driver_regulatory_export,
        mockserver,
        load_json,
        is_free,
        statuses,
        should_be_free,
):
    @mockserver.json_handler('/candidates/deptrans')
    def _mock_candidates(request):
        answer = load_json('answer.json')['drivers'][0]
        answer['free'] = is_free
        answer['status'] = {}
        answer['status']['orders'] = [{'status': x} for x in statuses]
        return mockserver.make_response(status=200, json={'drivers': [answer]})

    response = await taxi_driver_regulatory_export.post('/v1/deptrans/cars')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['free'] == should_be_free
