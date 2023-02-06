async def test_basic(taxi_userver_sample):
    response = await taxi_userver_sample.get('/autogen/testpoint/callback')
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello, world'}


async def test_callback(taxi_userver_sample, testpoint):
    @testpoint('callback_sample')
    def callback_sample(data):
        return {'subject': 'foo'}

    response = await taxi_userver_sample.get('/autogen/testpoint/callback')
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello, foo'}
    assert callback_sample.times_called == 1
