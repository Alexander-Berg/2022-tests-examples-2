import aiohttp.web


URL = '/api/v1/regular-charges/check-limits'
HEADERS = {
    'Accept-Language': 'ru',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
    'X-Real-IP': '127.0.0.1',
}


async def test_success(
        web_app_client, headers, load_json, mock_fleet_rent_py3,
):
    service_stub = load_json('service_success.json')
    fleet_rent_stub = load_json('fleet_rent_success.json')

    @mock_fleet_rent_py3('/v1/park/rents/used-limits')
    async def _v1_park_rents_used_limits(request):
        assert request.method == 'GET'
        assert request.query == fleet_rent_stub['request']
        return aiohttp.web.json_response(fleet_rent_stub['response'])

    response = await web_app_client.post(
        URL, headers=HEADERS, json=service_stub['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
