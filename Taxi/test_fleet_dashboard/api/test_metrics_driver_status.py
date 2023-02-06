ENDPOINT = '/dashboard/v1/metrics/driver-statuses'

PARK_ID = '7ad36bc7560449998acbe2c57a75c293'


async def test_ok(web_app_client, headers, mockserver):
    @mockserver.json_handler('/driver-status/v2/statuses/park')
    def _mock_driver_status(request):
        assert request.json == {'park': PARK_ID}
        return {'free': 2, 'busy': 4, 'onorder': 8}

    response = await web_app_client.post(ENDPOINT, headers=headers)
    assert response.status == 200
    assert await response.json() == {'free': 2}
