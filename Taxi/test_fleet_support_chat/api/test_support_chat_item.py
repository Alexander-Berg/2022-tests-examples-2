import aiohttp.web


async def test_success(
        web_app_client,
        headers,
        mock_parks,
        mockserver,
        mock_support_chat,
        load_json,
):
    stub = load_json('success.json')

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    async def _users_list(request):
        if request.json == stub['dac_common_request']:
            return aiohttp.web.json_response(stub['dac_common_response'])
        assert request.json == stub['dac_request']
        return aiohttp.web.json_response(stub['dac_response'])

    @mock_support_chat('/v1/chat/search')
    async def _search(request):
        assert request.json == stub['support_chat_request']
        return aiohttp.web.json_response(stub['support_chat_response'])

    response = await web_app_client.post(
        '/support-chat-api/v1/item', headers=headers, json={'id': 'id'},
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['service_response']
