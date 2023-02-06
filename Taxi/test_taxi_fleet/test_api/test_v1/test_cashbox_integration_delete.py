import aiohttp.web


async def test_success(
        web_app_client, headers, mock_cashbox_integration, load_json,
):
    stub = load_json('success.json')

    @mock_cashbox_integration('/v1/parks/cashboxes')
    async def _cashbox_delete(request):
        assert request.query == stub['cashbox_request']
        return aiohttp.web.json_response(stub['cashbox_response'])

    cashbox_id = '86f260fc38c443e1a1c55de2d1a383cf'
    response = await web_app_client.post(
        f'/api/v1/cashbox-integration/delete?id={cashbox_id}',
        headers=headers,
        json={},
    )

    assert response.status == 200
