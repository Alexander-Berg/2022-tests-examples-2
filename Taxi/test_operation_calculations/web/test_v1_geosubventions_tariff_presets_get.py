import http
import json

from aiohttp import web
import pytest


@pytest.mark.config(
    OPERATION_CALCULATIONS_GEOSUBVENTIONS_TARIFF_PRESETS={
        'cargo': {'__default__': ['express', 'cargo'], 'moscow': ['cargo']},
        'charity': {
            '__default__': ['suv', 'premium_suv'],
            'moscow': ['suv'],
            'spb': ['suv'],
        },
    },
)
@pytest.mark.parametrize(
    'params, expected_status, expected_content',
    (
        pytest.param(
            {'tariff_zones': 'moscow'},
            http.HTTPStatus.OK,
            {'cargo': ['cargo'], 'charity': ['suv']},
        ),
        pytest.param(
            {'tariff_zones': 'spb'},
            http.HTTPStatus.OK,
            {'cargo': ['express'], 'charity': ['suv']},
        ),
        pytest.param(
            {'tariff_zones': 'spb,moscow'}, http.HTTPStatus.CONFLICT, {},
        ),
        pytest.param(
            {'tariff_zones': 'moscow,spb'}, http.HTTPStatus.CONFLICT, {},
        ),
    ),
)
async def test_v1_geosubventions_tariff_presets_post(
        web_app_client,
        mock_taxi_tariffs,
        open_file,
        params,
        expected_status,
        expected_content,
):
    with open_file('test_data.json', mode='rb', encoding=None) as fp:
        test_data = json.load(fp)

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        req_zones = request.args['zone_names'].split(',')
        zones = []
        for zone in test_data['zones']:
            if zone['zone'] in req_zones:
                zones.append(zone)
        return web.json_response({'zones': zones})

    response = await web_app_client.get(
        f'/v1/geosubventions/tariff_presets/', params=params,
    )
    assert response.status == expected_status
    if expected_status == 200:
        assert await response.json() == expected_content
