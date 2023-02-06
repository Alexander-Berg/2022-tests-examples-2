import aiohttp.web


async def test_success(
        web_app_client, headers, mock_cashbox_integration, load_json,
):
    stub = load_json('success.json')

    @mock_cashbox_integration('/v1/parks/cashboxes/current')
    async def _cashbox_current(request):
        assert request.json == stub['cashbox_request']
        return aiohttp.web.json_response(stub['cashbox_response'])

    response = await web_app_client.post(
        '/api/v1/cashbox-integration/current',
        headers=headers,
        json={'cashbox_id': '86f260fc38c443e1a1c55de2d1a383cf'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
