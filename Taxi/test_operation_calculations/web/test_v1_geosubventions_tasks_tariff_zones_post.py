import json

from aiohttp import web
import pytest


@pytest.fixture(autouse=True)
def services(open_file, mock_taxi_tariffs, mock_geoareas):
    with open_file('services_responses.json') as data_json:
        services_responses = json.load(data_json)

    @mock_taxi_tariffs('/v1/tariffs')
    def _tariff_zones_handler(request):
        return web.json_response(services_responses['tariffs'])

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        return web.json_response(services_responses['tariff_settings'])

    @mock_geoareas('/geoareas/v1/tariff-areas')
    def _get_tariff_areas(request):
        return web.json_response(services_responses['geoareas'])


@pytest.fixture(name='test_data')
def test_data_fixture(open_file, test_data_json):
    with open_file(test_data_json) as data_json:
        return json.load(data_json)


@pytest.mark.parametrize(
    'test_data_json',
    ['test_data_ok.json', 'test_data_intersecting_polygons.json'],
    ids=lambda x: x.split('.')[0][10:],
)
async def test_geosubventons_tasks_tariff_zones(
        web_app_client, open_file, test_data,
):
    response = await web_app_client.post(
        '/v1/geosubventions/tasks/tariff_zones',
        json=test_data['request'],
        headers={'X-Yandex-Login': 'test_robot'},
    )

    assert response.status == test_data['status']
    content = await response.json()

    if response.status == 200:
        assert content == test_data['response']
    else:
        assert content['message'] == test_data['error_message']
