import aiohttp.web

URL = '/api/v1/drivers/download-async'

HEADERS = {
    'Accept-Language': 'ru',
    'X-Yandex-Login': 'abacaba',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
    'X-Real-IP': '127.0.0.1',
    'X-YaTaxi-Fleet-Permissions': 'permission',
}

QUERY = {'operation_id': '6c5c10956c2bbe505bb8c42201efe5ef'}


async def test_success(
        web_app_client,
        mock_parks,
        headers,
        load_json,
        mock_fleet_reports_storage,
        stq,
):
    stub = load_json('success.json')

    @mock_fleet_reports_storage('/internal/user/v1/operations/create')
    async def _create(request):
        assert request.json == stub['fleet_reports_storage']['request']
        return aiohttp.web.json_response(data={})

    response = await web_app_client.post(
        URL, headers=HEADERS, params=QUERY, json=stub['request'],
    )

    assert stq.taxi_fleet_drivers_download_async.has_calls
    assert response.status == 200
