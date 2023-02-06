import aiohttp.web


async def test_success(web_app_client, headers, mock_driver_fix, load_json):
    stub = load_json('success.json')

    @mock_driver_fix('/v1/view/status_summary')
    async def _status_summary(request):
        return aiohttp.web.json_response(stub['response'])

    response = await web_app_client.post(
        '/api/v1/drivers/driver-fix-status-summary',
        headers=headers,
        json={'driver_id': 'aab36cr7560d499f8acbe2c52a7j7n9p'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['response']
