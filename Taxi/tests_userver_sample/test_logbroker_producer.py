async def test_message(taxi_userver_sample, testpoint):
    @testpoint('logbroker_publish')
    def commit(data):
        assert data.pop('source_id', None) is not None
        assert data == {'data': '1 2', 'name': 'positions'}

    response = await taxi_userver_sample.post(
        'logbroker/post', params={'lon': 1, 'lat': 2, 'seq_no': 3},
    )
    assert response.status_code == 200

    await commit.wait_call()
