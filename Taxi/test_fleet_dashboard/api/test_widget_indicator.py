import aiohttp.web


async def test_success(web_app_client, headers, mock_api7, load_json):
    stub = load_json('success.json')

    @mock_api7('/v1/parks/driver-profiles/status/aggregation')
    async def _status_aggregation(request):
        assert request.json == stub['api7']['request']
        return aiohttp.web.json_response(stub['api7']['response'])

    response = await web_app_client.post(
        '/dashboard-api/v1/widget/indicator', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
