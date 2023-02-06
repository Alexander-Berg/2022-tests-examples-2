import aiohttp.web


async def test_success(
        web_app_client, mock_parks, headers, mock_uapi_keys, load_json,
):
    stub = load_json('success.json')

    @mock_uapi_keys('/v2/keys/list')
    async def _keys_list(request):
        assert request.method == 'POST'
        assert request.json == stub['apikeys_request']
        return aiohttp.web.json_response(stub['apikeys_response'])

    response = await web_app_client.post(
        '/api/v1/apikeys/list', headers=headers, json={},
    )

    assert response.status == 200
    assert await response.json() == stub['service_response']
    assert _keys_list.has_calls
