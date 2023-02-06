import aiohttp.web

URL = '/api/v1/drivers/download'

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
        web_app_client, headers, load_json, mock_api7, mock_driver_work_rules,
):
    service_stub = load_json('service_success.json')
    api7_drivers_stub = load_json('api7_drivers_success.json')
    driver_work_rules_stub = load_json('driver_work_rules_success.json')

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == api7_drivers_stub['request']
        return aiohttp.web.json_response(api7_drivers_stub['response'])

    @mock_driver_work_rules('/v1/work-rules/list')
    async def _v1_work_rules_list(request):
        assert request.json == driver_work_rules_stub['request']
        return aiohttp.web.json_response(driver_work_rules_stub['response'])

    response = await web_app_client.post(
        URL, headers=HEADERS, json=service_stub['request'],
    )

    assert response.status == 200
