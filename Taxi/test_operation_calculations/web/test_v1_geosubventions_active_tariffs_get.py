import http
import json

from aiohttp import web
import pytest


@pytest.fixture(name='test_data')
def test_data_fixture(open_file):
    with open_file('test_data.json') as handler:
        return json.load(handler)


@pytest.fixture(name='mock_thirdparty_servers')
def mock_thirdparty_servers_fixture(test_data, mock_taxi_tariffs):
    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        return web.json_response(test_data['tariff_settings'])


async def test_v1_geosubventions_active_tariffs_get(
        web_app_client, mock_thirdparty_servers, test_data,
):
    response = await web_app_client.get(
        '/v1/geosubventions/active_tariffs/',
        params={'tariff_zones': 'moscow'},
    )
    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    assert result == test_data['expected_response']
