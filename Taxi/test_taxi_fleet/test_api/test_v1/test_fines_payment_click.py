import aiohttp.web


async def test_success(web_app_client, headers, mock_fleet_fines):
    @mock_fleet_fines('/v1/deferred-update')
    async def _deferred_update(request):
        assert request.query['uin'] == 'test'
        return aiohttp.web.json_response()

    response = await web_app_client.post(
        '/api/v1/fines/payment-click?uin=test', headers=headers, json={},
    )

    assert response.status == 200
