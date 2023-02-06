import aiohttp.web


async def test_success(
        web_app_client,
        headers,
        mockserver,
        mock_support_chat,
        load_json,
        patch,
):
    stub = load_json('success.json')

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    async def _users_list(request):
        assert request.json == stub['dac_request']
        return aiohttp.web.json_response(stub['dac_response'])

    @mock_support_chat('/v1/chat/chat_id/read')
    async def _read(request):
        assert request.json == stub['support_chat_read_request']
        return aiohttp.web.json_response(stub['support_chat_read_response'])

    @mock_support_chat('/v1/chat/chat_id/history')
    async def _history(request):
        assert request.json == stub['support_chat_request']
        return aiohttp.web.json_response(stub['support_chat_response'])

    response = await web_app_client.post(
        '/support-chat-api/v1/history',
        headers=headers,
        json={'chat_id': 'chat_id'},
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['service_response']
