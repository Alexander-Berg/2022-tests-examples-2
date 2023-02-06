import aiohttp.web


async def test_success(
        web_app_client, headers, mock_fleet_notifications, load_json,
):
    stub = load_json('success.json')

    @mock_fleet_notifications('/v1/notifications/status')
    async def _notifications_status(request):
        assert request.query == stub['notifications_query']
        assert request.json == stub['notifications_request']
        return aiohttp.web.json_response(stub['notifications_response'])

    response = await web_app_client.post(
        '/api/v1/notifications/status',
        headers=headers,
        json={'ids': ['1', '2'], 'status': 'viewed'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
