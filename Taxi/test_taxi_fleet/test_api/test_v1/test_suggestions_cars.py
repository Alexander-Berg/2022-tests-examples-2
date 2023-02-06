import aiohttp.web

URL = '/api/v1/suggestions/cars'

HEADERS = {
    'Accept-Language': 'ru',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
    'X-Real-IP': '127.0.0.1',
}


async def test_by_text_success(web_app_client, headers, mock_api7, load_json):
    service_stub = load_json('service_success.json')
    api7_stub = load_json('api7_success.json')

    @mock_api7('/v1/parks/cars/list')
    async def _list_cars(request):
        assert request.json == api7_stub['request']['v1']
        return aiohttp.web.json_response(api7_stub['response'])

    response = await web_app_client.post(
        URL, headers=HEADERS, json=service_stub['request']['v1'],
    )

    assert response.status == 200
    assert await response.json() == service_stub['response']


async def test_by_ids_success(web_app_client, headers, mock_api7, load_json):
    service_stub = load_json('service_success.json')
    api7_stub = load_json('api7_success.json')

    @mock_api7('/v1/parks/cars/list')
    async def _list_cars(request):
        assert request.json == api7_stub['request']['v2']
        return aiohttp.web.json_response(api7_stub['response'])

    response = await web_app_client.post(
        URL, headers=HEADERS, json=service_stub['request']['v2'],
    )

    assert response.status == 200
    assert await response.json() == service_stub['response']
