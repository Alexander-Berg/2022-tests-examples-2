async def test_success(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/time-point-tz')
    async def _mock(request):
        return {
            'query_dttm': request.query['dttm'],
            'body_dttm': request.json['dttm'],
        }

    response = await taxi_userver_sample.post(
        '/autogen/time-point-tz',
        params={'dttm': '2017-04-04T15:32:22+10:00'},
        json={'dttm': '2018-04-04T15:32:22+10:00'},
    )
    assert _mock.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'query_dttm': '2017-04-04T05:32:22+00:00',
        'body_dttm': '2018-04-04T05:32:22+00:00',
    }
