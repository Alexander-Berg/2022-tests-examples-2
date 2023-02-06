import aiohttp.web


async def test_success(
        web_app_client,
        mock_parks,
        mock_dac_users,
        headers,
        mock_feeds,
        load_json,
):
    stub = load_json('success.json')

    @mock_feeds('/v1/fetch_by_id')
    async def _v1_fetch(request):
        assert request.json == stub['feeds_fetch_by_id']['request']
        return aiohttp.web.json_response(stub['feeds_fetch_by_id']['response'])

    response = await web_app_client.post(
        '/api/v1/feeds/list/by-id',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
