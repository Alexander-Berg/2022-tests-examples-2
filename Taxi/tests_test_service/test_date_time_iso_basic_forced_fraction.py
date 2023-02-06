import pytest


@pytest.mark.parametrize(
    ['dttm_in', 'dttm_out'],
    [
        ('2021-04-04T15:32:22.54236+1000', '2021-04-04T05:32:22.54236+0000'),
        ('2021-04-04T15:32:22.0+1000', '2021-04-04T05:32:22.0+0000'),
        ('2021-04-04T15:32:22.00000+1000', '2021-04-04T05:32:22.0+0000'),
        ('2021-04-04T15:32:22.01420+1000', '2021-04-04T05:32:22.0142+0000'),
        ('2021-04-04T15:32:22.+1000', '2021-04-04T05:32:22.0+0000'),
    ],
)
async def test_success(taxi_test_service, mockserver, dttm_in, dttm_out):
    @mockserver.json_handler(
        '/test-service/datetime/date-time-iso-basic-forced-fraction',
    )
    async def _handle(request):
        return {'value': request.query['value']}

    response = await taxi_test_service.get(
        '/datetime/date-time-iso-basic-forced-fraction',
        params={'value': dttm_in},
    )

    assert _handle.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'value': dttm_out}


@pytest.mark.parametrize('dttm_in', ['2021-04-04T15:32:22+1000'])
async def test_fail(taxi_test_service, dttm_in):
    response = await taxi_test_service.get(
        '/datetime/date-time-iso-basic-forced-fraction',
        params={'value': dttm_in},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': f'invalid datetime value of \'value\' in query: {dttm_in}',
    }
