import aiohttp.web
import pytest

URL = '/reports-api/v1/drivers/segments/update-driver'


@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_success(web_app_client, headers, mockserver, load_json):
    service_stub = load_json('service.json')
    parks_drivers_stub = load_json('parks_drivers.json')

    @mockserver.json_handler('/parks/internal/driver-profiles/profile')
    async def _v1_parks_driver_profiles_profile(request):
        assert request.json == parks_drivers_stub['request']
        return aiohttp.web.json_response(parks_drivers_stub['response'])

    response = await web_app_client.post(
        URL, headers=headers, json=service_stub['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
