import aiohttp.web

URL = '/api/v1/suggestions/drivers'

HEADERS = {
    'Accept-Language': 'ru',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
    'X-Real-IP': '127.0.0.1',
}


async def test_by_text_success(web_app_client, headers, mockserver, load_json):
    service_stub = load_json('service_success.json')
    parks_stub = load_json('parks_success.json')

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_driver_profiles_retrieve(request):
        assert request.json == parks_stub['request']['v1']
        return aiohttp.web.json_response(parks_stub['response'])

    response = await web_app_client.post(
        URL, headers=HEADERS, json=service_stub['request']['v1'],
    )

    assert response.status == 200
    assert await response.json() == service_stub['response']


async def test_by_ids_success(web_app_client, headers, mockserver, load_json):
    service_stub = load_json('service_success.json')
    parks_stub = load_json('parks_success.json')

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_driver_profiles_retrieve(request):
        assert request.json == parks_stub['request']['v2']
        return aiohttp.web.json_response(parks_stub['response'])

    response = await web_app_client.post(
        URL, headers=HEADERS, json=service_stub['request']['v2'],
    )

    assert response.status == 200
    assert await response.json() == service_stub['response']
