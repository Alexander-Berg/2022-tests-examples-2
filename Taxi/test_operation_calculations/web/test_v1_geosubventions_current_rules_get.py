import http
import json

from aiohttp import web
import pytest

from taxi import discovery

import operation_calculations.geosubventions.calculators.utils as utils
from test_operation_calculations import conftest


@pytest.mark.parametrize(
    'geo_node, node_type, no_tag_main_tag, expected_status,'
    ' expected_message, expected_key,  retrieve_apis',
    [
        pytest.param(
            'br_saratov',
            'geo_node',
            False,
            http.HTTPStatus.OK,
            None,
            'new',
            ['new'],
        ),
        pytest.param(
            'br_saratov',
            'geo_node',
            False,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'BadRequest',
                'message': 'Too many tariff zones for br_saratov: 2',
            },
            'new',
            ['new'],
            marks=pytest.mark.config(
                ATLAS_GEOSUBVENTIONS={'max_current_zones': 0},
            ),
        ),
        pytest.param(
            'br_saratov',
            'geo_node',
            False,
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'BadRequest', 'message': 'Too many rules collected 3'},
            'new',
            ['new'],
            marks=pytest.mark.config(
                ATLAS_GEOSUBVENTIONS={'max_current_rules': 2},
            ),
        ),
        pytest.param(
            'br_saratov',
            'geo_node',
            False,
            http.HTTPStatus.CONFLICT,
            {'code': 'Conflict', 'message': 'Rules exist in both apis'},
            'old',
            ['new', 'old'],
        ),
        pytest.param(
            'br_saratov',
            'geo_node',
            False,
            http.HTTPStatus.OK,
            None,
            'old',
            ['old'],
        ),
        pytest.param(
            'br_saratov',
            'geo_node',
            True,
            http.HTTPStatus.OK,
            None,
            'new_main_tag',
            ['new'],
        ),
    ],
)
@pytest.mark.config(
    TARIFF_CLASSES_MAPPING={
        'uberkids': {'classes': ['child_tariff']},
        'uberx': {'classes': ['econom']},
        'vezeteconom': {'classes': ['econom']},
    },
)
@pytest.mark.geo_nodes(conftest.GEO_NODES)
async def test_v1_geosubventions_current_rules_get(
        web_app_client,
        geo_node,
        node_type,
        no_tag_main_tag,
        expected_key,
        expected_message,
        expected_status,
        retrieve_apis,
        mock_geoareas,
        mock_billing_subventions_x,
        mock_taxi_tariffs,
        mockserver,
        mock_taxi_agglomerations,
        response_mock,
        patch_aiohttp_session,
        open_file,
):
    with open_file('test_data.json', mode='rb', encoding=None) as fp:
        test_data = json.load(fp)

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        return web.json_response(test_data['tariff_settings'])

    @mock_billing_subventions_x('/v2/rules/by_filters')
    def _bsx_select_handler(request):

        tag_constr = request.json.get('tags_constraint', {})
        rules = test_data['bsx_rules'] if 'new' in retrieve_apis else []
        if tag_constr.get('has_tag') is False:
            rules = [rule for rule in rules if not rule.get('tag')]
        return web.json_response({'rules': rules})

    @mock_geoareas('/subvention-geoareas/admin/v1/geoareas')
    def _geoareas_select_handler(request):
        assert request.method == 'POST'
        return web.json_response(test_data['geoareas'])

    @patch_aiohttp_session(
        discovery.find_service('chatterbox').url + '/v1/rules/select', 'POST',
    )
    def _patch_request(method, url, **kwargs):
        rules = test_data['billing_old_api'] if 'old' in retrieve_apis else []
        return response_mock(json={'subventions': rules})

    params = {
        'geo_zone[name]': geo_node,
        'geo_zone[type]': node_type,
        'no_tag_main_tag': json.dumps(no_tag_main_tag),
    }
    params.update(test_data['request_params'])
    response = await web_app_client.get(
        '/v1/geosubventions/current_rules/',
        headers={'X-Yandex-Login': 'test_robot'},
        params=params,
    )

    assert response.status == expected_status

    expected_message = expected_message or test_data['expected'][expected_key]
    msg = await response.json()

    if response.status == http.HTTPStatus.OK:
        msg['draft_rules'] = utils.sort_draft_rules(msg['draft_rules'])
        msg['polygons'] = sorted(msg['polygons'], key=lambda p: p['id'])
        msg['tariff_zones'] = sorted(msg['tariff_zones'])
        msg['current_rules_tags'] = sorted(msg['current_rules_tags'])
    assert msg == expected_message
