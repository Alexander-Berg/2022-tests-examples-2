import aiohttp.web


async def test_success(web_app_client, headers, mock_feeds, load_json):
    stub = load_json('success.json')

    @mock_feeds('/v1/log_status')
    async def _v1_fetch(request):
        assert request.json == stub['feeds_log_status']['request']
        return aiohttp.web.json_response(stub['feeds_log_status']['response'])

    response = await web_app_client.post(
        '/api/v1/feeds/read', headers=headers, json=stub['service']['request'],
    )

    assert response.status == 200
