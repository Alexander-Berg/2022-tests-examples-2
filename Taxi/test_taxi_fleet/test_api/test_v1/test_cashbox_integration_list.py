import aiohttp.web


async def test_success(
        web_app_client, headers, mock_cashbox_integration, load_json,
):
    stub = load_json('success.json')

    @mock_cashbox_integration('/v1/parks/cashboxes/list')
    async def _cashbox_list(request):
        assert request.json == stub['cashbox_request']
        return aiohttp.web.json_response(stub['cashbox_response'])

    @mock_cashbox_integration('/v1/parks/cashboxes/current/retrieve')
    async def _cashbox_retrieve(request):
        assert request.json == stub['cashbox_retrieve_request']
        return aiohttp.web.json_response(stub['cashbox_retrieve_response'])

    response = await web_app_client.post(
        '/api/v1/cashbox-integration/list', headers=headers, json={},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
