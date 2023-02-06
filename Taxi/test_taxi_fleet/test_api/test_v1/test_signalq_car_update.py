import aiohttp.web
import pytest

URL = '/fleet/signalq/v1/cars/update'

HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
    'X-Real-IP': '127.0.0.1',
}

FLEET_API_CAR_CATEGORIES = {
    'internal_categories': ['econom', 'comfort', 'business', 'eda'],
    'external_categories': [],
}


@pytest.mark.config(FLEET_API_CAR_CATEGORIES=FLEET_API_CAR_CATEGORIES)
async def test_success(web_app_client, headers, mockserver, load_json):
    api7_cars_list_stub = load_json('parks_cars_list_success.json')
    service_stub = load_json('service_success.json')

    @mockserver.json_handler('/parks/cars')
    async def _car_update(request):
        assert request.json == api7_cars_list_stub['request']
        assert request.query['id'] == service_stub['request']['query']['carId']
        return aiohttp.web.json_response(api7_cars_list_stub['response'])

    response = await web_app_client.post(
        URL,
        headers=HEADERS,
        params=service_stub['request']['query'],
        json=service_stub['request']['body'],
    )

    assert response.status == 200, (
        await response.json() == service_stub['response']
    )
