import aiohttp.web


async def test_success(
        web_app_client, mock_auth, mock_dispatcher_access_control,
):
    park_id_ = mock_auth.park.id

    @mock_dispatcher_access_control('/v1/parks/users/yandex/grants/list')
    async def _get_grants(request):
        return aiohttp.web.json_response(
            {'grants': [{'id': 'driver_read_common'}]},
        )

    response = await web_app_client.post(
        '/fleet_common/services/grants',
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-Login': 'abacaba',
            'X-Yandex-UID': '123',
            'X-Park-Id': park_id_,
            'X-Real-IP': '127.0.0.1',
        },
    )

    assert response.status == 200
