import http
import json

from aiohttp import web
import pytest

from test_operation_calculations import conftest


@pytest.mark.parametrize(
    'geo_node, node_type, expected',
    [
        pytest.param(
            'br_saratov',
            'geo_node',
            ['', '911fcf7838584cb5a2b4141ac78b535f_geotool_main'],
        ),
        pytest.param('engels', 'tariff_zone', ['']),
    ],
)
@pytest.mark.geo_nodes(conftest.GEO_NODES)
async def test_v1_geosubventions_bsx_tags_get(
        web_app_client,
        geo_node,
        node_type,
        expected,
        open_file,
        mock_taxi_tariffs,
        mock_geoareas,
        mock_billing_subventions_x,
        mock_taxi_agglomerations,
):
    with open_file('test_data.json', mode='rb', encoding=None) as fp:
        test_data = json.load(fp)

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        return web.json_response(test_data['tariff_settings'])

    @mock_billing_subventions_x('/v2/rules/by_filters')
    def _bsx_select_handler(request):
        tag_constr = request.json.get('tags_constraint', {})
        zones_constr = request.json.get('zones', [])
        rules = test_data['bsx_rules']

        if tag_constr.get('has_tag') is False:
            rules = [rule for rule in rules if not rule.get('tag')]
        rules = [rule for rule in rules if rule['zone'] in zones_constr]
        return web.json_response({'rules': rules})

    @mock_geoareas('/subvention-geoareas/admin/v1/geoareas')
    def _geoareas_select_handler(request):
        return web.json_response(test_data['geoareas'])

    params = {
        'geo_zone[name]': geo_node,
        'geo_zone[type]': node_type,
        'datetime': '2020-10-17T12:00',
        'tariff': 'econom',
    }

    response = await web_app_client.get(
        '/v1/geosubventions/bsx_tags/', params=params,
    )
    status = response.status
    result = await response.json()

    assert status == http.HTTPStatus.OK
    result['tags'] = sorted(result['tags'])
    assert result == {'tags': expected}
