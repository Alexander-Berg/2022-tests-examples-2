import datetime
import json

from aiohttp import web
import pytest

from taxi import discovery

from test_operation_calculations import conftest


@pytest.fixture(name='mock_thirdparty_servers')
def mock_thirdparty_servers_fixture(
        web_app_client,
        mock_taxi_tariffs,
        mock_geoareas,
        mock_billing_subventions_x,
        patch_aiohttp_session,
        response_mock,
        mock_taxi_approvals,
        mockserver,
        patch,
        open_file,
):
    with open_file('test_data_common.json') as fp:
        test_data_common = json.load(fp)

    @mock_geoareas('/geoareas/v1/tariff-areas')
    def _get_tariff_areas(request):
        return web.json_response(test_data_common['geoareas'])

    @mock_geoareas('/subvention-geoareas/admin/v1/geoareas')
    def _subvention_geoareas_select_handler(request):
        return web.json_response(test_data_common['subvention_geoareas'])

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        return web.json_response(test_data_common['tariff_settings'])

    @mock_taxi_tariffs('/v1/tariffs')
    def _get_tariffs(request):
        return web.json_response(test_data_common['tariffs'])

    @mock_taxi_tariffs('/v1/tariff_zones')
    def _tariff_zones_handler(request):
        return web.json_response(test_data_common['tariff_zones'])

    @mock_billing_subventions_x('/v2/rules/by_filters')
    def _bsx_select_handler(request):
        return web.json_response(test_data_common['current_rules'])

    @patch_aiohttp_session(
        discovery.find_service('chatterbox').url + '/v1/rules/select', 'POST',
    )
    def _patch_request(method, url, **kwargs):
        return response_mock(json={'subventions': []})

    @mockserver.json_handler('/taxi-exp-py3/v1/experiments/')
    def _handler_exp(request):
        exp_name = request.query.get('name')
        return test_data_common['current_experiments'][exp_name]

    @mockserver.json_handler('/taxi-exp-py3/v1/experiments/list/')
    def _handler_exp_list(request):
        offset = request.query.get('offset')
        return (
            test_data_common['current_experiments_list']
            if offset == '0'
            else {'experiments': []}
        )

    @mock_taxi_approvals('/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        return [
            {'id': 1, 'tickets': ['RUPRICING-1'], 'version': 1},
            {'id': 3, 'tickets': ['RUPRICING-2'], 'version': 1},
            {'id': 4, 'tickets': ['RUPRICING-3'], 'version': 1},
            {'id': 5, 'tickets': ['RUPRICING-5'], 'version': 1},
            {'id': 8, 'tickets': ['RUPRICING-5'], 'version': 1},
        ]

    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def _create_ticket(*args, **kwargs):
        queue = kwargs.get('queue', 'TEST')
        return {'key': f'{queue}-1'}

    @mock_taxi_approvals('/drafts/create/')
    def _draft_create(request):
        return web.json_response(
            {'id': 1, 'version': 1, 'status': 'need_approval'},
        )

    @mockserver.json_handler('/taxi_approvals/drafts/create/')
    def _handler(request):
        return {'id': 10, 'version': 1, 'status': 'need_approval'}

    @mock_taxi_approvals('/multidrafts/create/')
    def _multidraft_create(request):
        return web.json_response({'id': 2})


@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
@pytest.mark.geo_nodes(conftest.GEO_NODES)
async def test_v1_geosubventions_multidraft_tasks_close_candidates_post(
        web_app_client, open_file, mock_thirdparty_servers,
):
    with open_file('test_data_base.json') as fp:
        test_data = json.load(fp)

    response_close = await web_app_client.post(
        '/v1/geosubventions/multidraft/tasks/close_candidates/',
        json=test_data['close_candidates_body'],
        headers={'X-Yandex-Login': 'test_robot', 'Referer': 'http://some.url'},
    )
    assert response_close.status == 200
    response_body = await response_close.json()
    md_request_body = test_data['multidraft_tasks_post_body']
    md_request_body['close_rules_ids'] = []
    md_request_body['close_experiments'] = []
    for rule in response_body['conflicting_rules']:
        if rule['should_close']:
            md_request_body['close_rules_ids'].extend(rule['rule_ids'])
            md_request_body['close_experiments'].append(
                rule['experiment_name'],
            )

    assert md_request_body['close_rules_ids'] == (
        test_data['expected']['close_rules_ids']
    )
    assert md_request_body['close_experiments'] == (
        test_data['expected']['close_experiments']
    )

    md_request_body['state_hash'] = response_body['state_hash']

    response_task = await web_app_client.post(
        '/v2/geosubventions/multidraft/tasks/',
        json=md_request_body,
        headers={'X-Yandex-Login': 'test_robot', 'Referer': 'http://some.url'},
    )
    assert response_task.status == 200


@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
@pytest.mark.geo_nodes(conftest.GEO_NODES)
async def test_v1_geosubventions_current_rules_close_candidates_post(
        web_app_client, open_file, mock_thirdparty_servers, monkeypatch,
):
    monkeypatch.setattr(
        datetime.datetime,
        'utcnow',
        lambda: datetime.datetime(2020, 10, 16, 13, 32, 41, 123456),
    )
    monkeypatch.setattr(
        datetime.datetime,
        'now',
        lambda tz=None: datetime.datetime(2020, 10, 16, 13, 32, 41, 123456),
    )

    with open_file('test_data_current_rules.json') as fp:
        test_data = json.load(fp)

    response_close = await web_app_client.post(
        '/v1/geosubventions/current_rules/close_candidates/',
        json=test_data['close_candidates_body'],
        headers={'X-Yandex-Login': 'test_robot', 'Referer': 'http://some.url'},
    )
    assert response_close.status == 200
    response_body = await response_close.json()
    result = {'ids': [], 'experiments': []}
    md_request_body = test_data['multidraft_tasks_post_body']
    md_request_body['close_rules_ids'] = []
    md_request_body['close_experiments'] = []

    assert not response_body['conflicting_rules']

    for rule in response_body['non_confflicting_rules']:
        assert not rule['should_close']
        result['ids'].extend(rule['rule_ids'])
        md_request_body['close_rules_ids'].extend(rule['rule_ids'])
        if rule.get('experiment_name'):
            result['experiments'].append(rule['experiment_name'])
            md_request_body['close_experiments'].append(
                rule['experiment_name'],
            )

    assert result == test_data['expected']

    md_request_body['state_hash'] = response_body['state_hash']

    response_task = await web_app_client.post(
        '/v1/geosubventions/multidraft/close_rules/',
        json=md_request_body,
        headers={'X-Yandex-Login': 'test_robot', 'Referer': 'http://some.url'},
    )
    assert response_task.status == 200
