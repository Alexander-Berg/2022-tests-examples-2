import aiohttp.web


async def test_success(
        web_app_client, mock_parks, headers, mock_uapi_keys, load_json,
):
    stub = load_json('success.json')

    @mock_uapi_keys('/v2/keys')
    async def _key_get(request):
        assert request.method == 'GET'
        assert request.query == stub['apikeys_request']
        return aiohttp.web.json_response(stub['apikeys_response'])

    response = await web_app_client.post(
        '/api/v1/apikeys/key?id=494', headers=headers, json={},
    )

    assert response.status == 200
    assert await response.json() == stub['service_response']
    assert _key_get.has_calls
