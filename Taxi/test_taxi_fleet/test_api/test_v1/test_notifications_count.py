import aiohttp.web


async def test_success(
        web_app_client, headers, mock_fleet_notifications, load_json,
):
    stub = load_json('success.json')

    @mock_fleet_notifications('/v1/notifications/count')
    async def _notifications_count(request):
        assert request.query == stub['notifications_query']
        return aiohttp.web.json_response(stub['notifications_response'])

    response = await web_app_client.post(
        '/api/v1/notifications/count', headers=headers, json={},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
