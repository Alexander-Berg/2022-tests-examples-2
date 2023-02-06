import aiohttp


IMAGE = b'image'


async def test_file_upload(taxi_talaria_misc, mockserver, default_pa_headers):
    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_s3(request):
        assert request.method == 'PUT'
        assert request.path == '/mds-s3/order_id/photo_id'
        assert request.get_data() == IMAGE
        return mockserver.make_response('OK', 200)

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/api/yandex/trace/photo/upload',
        params={'object_id': 'order_id', 'photo_id': 'photo_id'},
        data=aiohttp.payload.BytesPayload(IMAGE),
        headers={'Content-Type': 'image/jpeg', **default_pa_headers('123')},
    )
    assert response.status_code == 200
    assert _mock_s3.times_called == 1
