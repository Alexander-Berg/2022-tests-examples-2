import http
import json

from aiohttp import web
import pytest

from taxi import discovery

from test_operation_calculations import conftest


@pytest.mark.parametrize(
    'expected, sources',
    (
        pytest.param(
            {'source': 'geo', 'value': 10, 'variants': [20]},
            ['geo', 'mfg', 'nmfg'],
        ),
        pytest.param(
            {'source': 'mfg', 'value': 5, 'variants': [30]}, ['mfg', 'nmfg'],
        ),
        pytest.param(
            {'source': 'nmfg', 'value': 40, 'variants': []}, ['nmfg'],
        ),
        pytest.param({'value': 0, 'variants': [], 'source': ''}, []),
    ),
)
@pytest.mark.geo_nodes(conftest.GEO_NODES)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
async def test_v1_geosubventions_multidraft_params_post(
        web_app_client,
        expected,
        sources,
        open_file,
        mock_taxi_tariffs,
        mock_geoareas,
        mock_billing_subventions_x,
        response_mock,
        patch_aiohttp_session,
):
    with open_file('test_data.json', mode='rb', encoding=None) as fp:
        test_data = json.load(fp)

    @mock_billing_subventions_x('/v2/rules/by_filters')
    def _bsx_select_handler(request):
        req = request.json
        only_geo = req.get('geoareas_constraint', {}).get('has_geoarea', False)
        r_types = req['rule_types']
        rules = test_data['bsx']

        def check_rule(rule):
            rule_type = rule['rule_type']
            is_geo = 'geoarea' in rule
            if rule_type not in r_types:
                return False
            if is_geo and 'geo' not in sources:
                return False
            if not is_geo and 'mfg' not in sources:
                return False
            if only_geo ^ is_geo:
                return False
            if is_geo and 'geo' not in sources:
                return False
            return True

        return web.json_response(
            {'rules': [rule for rule in rules if check_rule(rule)]},
        )

    @patch_aiohttp_session(
        discovery.find_service('billing_subventions').url + '/v1/rules/select',
        'POST',
    )
    def _patch_request(method, url, **kwargs):
        r_types = kwargs['json']['types']

        def check_rule(rule):
            rule_type = rule['type']
            if rule_type not in r_types:
                return False
            if 'nmfg' in sources and rule_type == 'daily_guarantee':
                return True
            if 'mfg' in sources and not rule.get('geoareas'):
                return True
            if 'geo' in sources and rule.get('geoareas'):
                return True
            return False

        rules = [rule for rule in test_data['old_billing'] if check_rule(rule)]
        return response_mock(json={'subventions': rules})

    response = await web_app_client.get(
        '/v1/geosubventions/min_activity/',
        params={'task_id': '7f9b08b19da21d53ed964474'},
    )
    status = response.status
    result = await response.json()

    assert status == http.HTTPStatus.OK
    assert {'activity': expected} == result
