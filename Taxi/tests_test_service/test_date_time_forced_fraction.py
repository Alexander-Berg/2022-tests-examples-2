import pytest


@pytest.mark.parametrize(
    ['dttm_in', 'dttm_out'],
    [
        ('2021-04-04T15:32:22.54236+10:00', '2021-04-04T05:32:22.54236+00:00'),
        ('2021-04-04T15:32:22.0+10:00', '2021-04-04T05:32:22.0+00:00'),
        ('2021-04-04T15:32:22.00000+10:00', '2021-04-04T05:32:22.0+00:00'),
        ('2021-04-04T15:32:22.01420+10:00', '2021-04-04T05:32:22.0142+00:00'),
        ('2021-04-04T15:32:22.+10:00', '2021-04-04T05:32:22.0+00:00'),
    ],
)
async def test_success(taxi_test_service, mockserver, dttm_in, dttm_out):
    @mockserver.json_handler(
        '/test-service/datetime/date-time-forced-fraction',
    )
    async def _handle(request):
        return {'value': request.query['value']}

    response = await taxi_test_service.get(
        '/datetime/date-time-forced-fraction', params={'value': dttm_in},
    )

    assert _handle.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'value': dttm_out}


@pytest.mark.parametrize('dttm_in', ['2021-04-04T15:32:22+10:00'])
async def test_fail(taxi_test_service, dttm_in):
    response = await taxi_test_service.get(
        '/datetime/date-time-forced-fraction', params={'value': dttm_in},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': f'invalid datetime value of \'value\' in query: {dttm_in}',
    }
