# Testpoint `sample` is called from within the service `userver-sample`,
# when it is run in testsuite.
async def test_testpoint(taxi_userver_sample, testpoint):
    @testpoint('sample')
    def _sample(data):  # `data` - is the data from the service
        assert data == {'id': 'id', 'value': 123}

    response = await taxi_userver_sample.post('testpoint')
    assert response.status_code == 200
    assert _sample.times_called == 1  # make sure that _sample was called
