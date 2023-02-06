async def test_https_cert_ok(taxi_userver_sample, mockserver_ssl):
    @mockserver_ssl.json_handler('/https-test/ok')
    def handle(request):
        return {'message': 'OK'}

    response = await taxi_userver_sample.get('/autogen/https/test')
    assert response.status_code == 200
    assert response.json() == {'message': 'OK'}
    assert handle.times_called == 1
