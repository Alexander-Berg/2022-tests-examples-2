import aiohttp.web
import pytest

URL = '/reports-api/v1/drivers/segments/list'


@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_success(
        web_app_client,
        headers,
        mock_parks,
        mock_api7,
        mock_driver_work_rules,
        load_json,
):
    service_stub = load_json('service.json')
    api7_drivers_stub = load_json('api7_drivers.json')
    driver_work_rules_stub = load_json('driver_work_rules.json')

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == api7_drivers_stub['request']
        return aiohttp.web.json_response(api7_drivers_stub['response'])

    @mock_driver_work_rules('/v1/work-rules/list')
    async def _v1_work_rules_list(request):
        assert request.json == driver_work_rules_stub['request']
        return aiohttp.web.json_response(driver_work_rules_stub['response'])

    response = await web_app_client.post(
        URL, headers=headers, json=service_stub['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
