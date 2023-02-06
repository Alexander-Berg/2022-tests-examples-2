import aiohttp.web


async def test_success(web_app_client, headers, mockserver, load_json):
    stub = load_json('success.json')

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    async def _list_users(request):
        assert request.json == stub['dac_request']
        return aiohttp.web.json_response(stub['dac_response'])

    response = await web_app_client.post(
        '/api/v1/users/list', headers=headers, json={'limit': 2},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
