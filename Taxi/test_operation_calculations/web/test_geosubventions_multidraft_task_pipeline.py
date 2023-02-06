# pylint: disable=C0302

import copy
import http
import json
import uuid

from aiohttp import web
import pytest

from taxi.stq import async_worker_ng

from operation_calculations.geosubventions.multidraft import (
    multidraft_internal as md_internal,
)
import operation_calculations.geosubventions.storage as storage_lib
from operation_calculations.stq import geosubventions_multidraft
from test_operation_calculations import conftest


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def trim_draft(draft):
    draft.pop('request_id')
    tag = draft['data'].get('rule_spec', {}).get('rule', {}).get('tag')
    if tag:
        pref = tag.split('_')[0]
        if is_valid_uuid(pref):
            tag = '_'.join(tag.split('_')[1:])
            draft['data']['rule_spec']['rule']['tag'] = tag
    if 'old_rule_ids' in draft['data']:
        draft['data']['old_rule_ids'] = sorted(draft['data']['old_rule_ids'])
    draft['change_doc_id'] = ':'.join(draft['change_doc_id'].split(':')[:-1])
    return draft


def trim_exp_draft(draft):
    draft.pop('request_id')
    draft.pop('change_doc_id')
    for pos, clause in enumerate(draft['data']['clauses']):
        alias = clause['alias']
        if clause.get('value', {}).get('geo_exp_tag'):
            tag = clause['value']['geo_exp_tag']
            draft['data']['clauses'][pos]['value']['geo_exp_tag'] = tag[
                tag.find('_') + 1 :
            ]
        draft['data']['clauses'][pos]['alias'] = alias[alias.find('_') + 1 :]
        if 'salt' in clause['predicate']['init']:
            draft['data']['clauses'][pos]['predicate']['init'][
                'salt'
            ] = '657d0d24-1a8c-4599-9629-c7391fcbfa10'
    default = draft.get('data', {}).get('default_value', {})
    if default and default.get('geo_exp_tag', ''):
        draft['data']['default_value']['geo_exp_tag'] = draft['data'][
            'default_value'
        ]['geo_exp_tag'][33:]
    name = draft['data']['name']
    draft['data']['name'] = name[: name.rfind('_')]
    descr = draft['data']['description']
    draft['data']['description'] = descr[: descr.rfind(' ')]
    return draft


DEFAULT_DRAFT_POLYGONS = {
    'prefix': '',
    'polygons': [
        {
            'polyId': 'mscmo_pol0',
            'name': 'mscmo_pol0',
            'draft_name': 'mscmo_pol0',
        },
        {
            'polyId': 'mscmo_pol2',
            'name': 'mscmo_pol2',
            'draft_name': 'mscmo_pol2',
        },
        {
            'polyId': 'mscmo_pol3',
            'name': 'mscmo_pol3',
            'draft_name': 'mscmo_pol3',
        },
        {
            'polyId': 'mscmo_pol5',
            'name': 'mscmo_pol5',
            'draft_name': 'mscmo_pol5',
        },
        {
            'polyId': 'mscmo_pol6',
            'name': 'mscmo_pol6',
            'draft_name': 'mscmo_pol6',
        },
    ],
}
DEFAULT_ATLAS_GEOSUBVENTIONS_CONFIG = {
    'ticket_queue': 'TEST',
    'ticket_queue_international': 'TEST_INT',
    'ticket_queue_logistics': 'TEST_LOG',
    'logistics_preset': 'logistics',
}


@pytest.fixture(autouse=True)
def services(
        mock_geoareas,
        mock_taxi_tariffs,
        mock_billing_subventions_x,
        mock_taxi_agglomerations,
        mock_taxi_approvals,
        mock_tags,
        mockserver,
        patch,
        monkeypatch,
        open_file,
):
    with open_file('services_responses.json') as data_json:
        services_responses = json.load(data_json)

    monkeypatch.setattr(
        md_internal, '_make_tag', lambda p, t: 'test_' + t if t else None,
    )

    @mock_geoareas('/subvention-geoareas/admin/v1/geoareas')
    def _subvention_geoareas_select_handler(request):
        return web.json_response(services_responses['subvention_geoareas'])

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        return web.json_response(services_responses['tariff_settings'])

    @mock_taxi_tariffs('/v1/tariffs')
    def _get_tariffs(request):
        return web.json_response(services_responses['tariffs'])

    @mock_taxi_tariffs('/v1/tariff_zones')
    def _get_tariff_zones(request):
        return web.json_response(services_responses['tariff_zones'])

    @mock_geoareas('/geoareas/v1/tariff-areas')
    def _get_tariff_areas(request):
        return web.json_response(services_responses['geoareas'])

    @mock_taxi_agglomerations('/v1/geo_nodes/find_parents_grouped_level')
    def _mock_parents(request):
        return web.json_response(services_responses['geo_nodes_parents'])

    @mockserver.json_handler('/taxi-exp-py3/v1/experiments/')
    def _handler_exp(request):
        exp_name = request.query.get('name')
        return services_responses['current_experiments'][exp_name]

    @mock_geoareas('/subvention-geoareas/internal/v1/create_geoarea')
    def _geoareas_set_handler(request):
        return web.json_response({'id': '1'})

    @mock_taxi_agglomerations('/v1/geo_nodes/get_info/')
    def _mock_node_info(request):
        return web.json_response(services_responses['geo_nodes_info'])

    @mock_billing_subventions_x('/v2/rules/by_filters')
    def _bsx_select(request):
        req = request.json
        tag_constr = req.get('tags_constraint', {})
        rules = services_responses['current_rules']['rules']
        zones = req.get('zones')
        tariffs = req.get('tariff_classes')

        def check_rule(rule):

            if zones and rule['zone'] not in zones:
                return False
            if tariffs and rule['tariff_class'] not in tariffs:
                return False
            if tag_constr.get('has_tag') is False and rule.get('tag'):
                return False
            if tag_constr.get('tags') and rule.get(
                    'tag',
            ) not in tag_constr.get('tags'):
                return False
            return True

        resp = [rule for rule in rules if check_rule(rule)]
        return web.json_response({'rules': resp})

    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def _create_ticket(*args, **kwargs):
        queue = kwargs.get('queue', 'TEST')
        return {'key': f'{queue}-1'}

    @mock_taxi_approvals('/multidrafts/create/')
    def _multidraft_create(request):
        return web.json_response({'id': 2})

    @mock_tags('/v1/topics/items')
    def _mock_topics_items(request):
        return web.json_response(services_responses['topics_items'])

    @mock_taxi_approvals('/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        return services_responses['drafts_list']


@pytest.fixture(name='test_data')
def test_data_fixture(open_file):
    with open_file('test_data.json', mode='rb', encoding=None) as fp:
        return json.load(fp)


@pytest.mark.parametrize(
    'extra_parms,expected_md_status,expected_status,'
    'expected_content,test_params',
    (
        pytest.param(
            {
                'task_id': '5f9b08b19da21d52ed964475',
                'draft_polygons': DEFAULT_DRAFT_POLYGONS,
                'close_all_current_rules': False,
            },
            http.HTTPStatus.OK,
            http.HTTPStatus.OK,
            {
                'ticket_url': 'https://st.test.yandex-team.ru/TEST-1',
                'draft_id': 2,
                'draft_url': (
                    'https://tariff-editor.taxi.tst.'
                    'yandex-team.ru/drafts/multidraft/2/?multi=true'
                ),
                'exp_draft_id': 2,
                'exp_draft_url': (
                    'https://tariff-editor.taxi.tst.yandex-team.ru'
                    '/drafts/multidraft/2/?multi=true'
                ),
            },
            {'expected_key': 'experiment_close', 'list_exp': True},
            marks=[
                pytest.mark.config(
                    ATLAS_GEOSUBVENTIONS_EXPERIMENTS_GENERAL={
                        'consumers': ['geo_experiment_consumer'],
                        'department': 'taxi',
                        'split_multidrafts': True,
                    },
                    EXP3_ADMIN_CONFIG={
                        'settings': {'common': {'departments': {'taxi': {}}}},
                    },
                ),
                pytest.mark.pgsql(
                    'operation_calculations',
                    files=['pg_geosubventions_multidrafts.sql'],
                ),
            ],
        ),
        pytest.param(
            {
                'task_id': '5f9b08b19da21d52ed964470',
                'draft_polygons': DEFAULT_DRAFT_POLYGONS,
            },
            http.HTTPStatus.OK,
            http.HTTPStatus.CONFLICT,
            {
                'description': {
                    'polygons': [
                        {
                            'draft_name': 'mscmo_pol0',
                            'errors': ['existing_conflict'],
                            'existing': True,
                            'name': 'mscmo_pol0',
                            'polyId': 'mscmo_pol0',
                        },
                        {
                            'draft_name': 'mscmo_pol2',
                            'existing': False,
                            'name': 'mscmo_pol2',
                            'polyId': 'mscmo_pol2',
                        },
                        {
                            'draft_name': 'mscmo_pol3',
                            'existing': False,
                            'name': 'mscmo_pol3',
                            'polyId': 'mscmo_pol3',
                        },
                        {
                            'draft_name': 'mscmo_pol5',
                            'existing': False,
                            'name': 'mscmo_pol5',
                            'polyId': 'mscmo_pol5',
                        },
                        {
                            'draft_name': 'mscmo_pol6',
                            'existing': False,
                            'name': 'mscmo_pol6',
                            'polyId': 'mscmo_pol6',
                        },
                    ],
                    'prefix': '',
                },
                'error_type': 'polygon_conflict',
            },
            {},
        ),
        pytest.param(
            {
                'task_id': '7f9b08b19da21d53ed964474',
                'draft_polygons': {
                    'prefix': 'test_',
                    'polygons': [
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol0',
                            'name': 'pol1',
                            'draft_name': 'pol1',
                        },
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol1',
                            'name': 'pol2',
                            'draft_name': 'pol2',
                        },
                    ],
                },
            },
            http.HTTPStatus.OK,
            http.HTTPStatus.OK,
            {
                'ticket_url': 'https://st.test.yandex-team.ru/TEST-1',
                'draft_id': 2,
                'draft_url': (
                    'https://tariff-editor.taxi.tst.yandex-team.ru'
                    '/drafts/multidraft/2/?multi=true'
                ),
            },
            {'expected_key': 'experiments_main'},
        ),
        pytest.param(
            {
                'task_id': '7f9b08b19da21d53ed964479',
                'draft_polygons': {
                    'prefix': 'test_',
                    'polygons': [
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol0',
                            'name': 'pol1',
                            'draft_name': 'pol1',
                        },
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol1',
                            'name': 'pol2',
                            'draft_name': 'pol2',
                        },
                    ],
                },
                'tag': 'bad_tag',
            },
            http.HTTPStatus.BAD_REQUEST,
            None,
            {
                'code': 'Forbidden::CriticalWarnings',
                'message': 'Task result contains critical warnings',
                'details': {
                    'general': [
                        {
                            'critical': True,
                            'message': (
                                'Tag bad_tag is not from subventions topic'
                            ),
                            'type': 'invalid_tag',
                        },
                    ],
                },
            },
            None,
        ),
        pytest.param(
            {
                'task_id': '7f9b08b19da21d53ed964474',
                'draft_polygons': {
                    'prefix': 'test_',
                    'polygons': [
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol0',
                            'name': 'pol1',
                            'draft_name': 'pol1',
                        },
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol1',
                            'name': 'pol2',
                            'draft_name': 'pol2',
                        },
                    ],
                },
            },
            http.HTTPStatus.OK,
            http.HTTPStatus.OK,
            {
                'ticket_url': 'https://st.test.yandex-team.ru/TEST-1',
                'draft_id': 2,
                'draft_url': (
                    'https://tariff-editor.taxi.tst.yandex-team.ru'
                    '/drafts/multidraft/2/?multi=true'
                ),
            },
            {'expected_key': 'bulk_api'},
        ),
        pytest.param(
            {
                'task_id': '7f9b08b19da21d53ed964474',
                'draft_polygons': {
                    'prefix': 'test_',
                    'polygons': [
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol0',
                            'name': 'pol1',
                            'draft_name': 'pol1',
                        },
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol1',
                            'name': 'pol2',
                            'draft_name': 'pol2',
                        },
                    ],
                },
            },
            http.HTTPStatus.OK,
            http.HTTPStatus.OK,
            {
                'ticket_url': 'https://st.test.yandex-team.ru/TEST-1',
                'draft_id': 2,
                'draft_url': (
                    'https://tariff-editor.taxi.tst.yandex-team.ru'
                    '/drafts/multidraft/2/?multi=true'
                ),
            },
            {'expected_key': 'experiments_main'},
        ),
        pytest.param(
            {
                'task_id': '7f9b08b19da21d53ed964474',
                'with_experiments': True,
                'draft_polygons': {
                    'prefix': 'test_',
                    'polygons': [
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol0',
                            'name': 'pol1',
                            'draft_name': 'pol1',
                        },
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol1',
                            'name': 'pol2',
                            'draft_name': 'pol2',
                        },
                    ],
                },
            },
            http.HTTPStatus.OK,
            http.HTTPStatus.OK,
            {
                'ticket_url': 'https://st.test.yandex-team.ru/TEST-1',
                'draft_id': 2,
                'draft_url': (
                    'https://tariff-editor.taxi.tst.yandex-team.ru'
                    '/drafts/multidraft/2/?multi=true'
                ),
                'exp_draft_id': 2,
                'exp_draft_url': (
                    'https://tariff-editor.taxi.tst.yandex-team.ru'
                    '/drafts/multidraft/2/?multi=true'
                ),
            },
            {'expected_key': 'experiments'},
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'settings': {'common': {'departments': {'taxi': {}}}},
                },
                ATLAS_GEOSUBVENTIONS_EXPERIMENTS_GENERAL={
                    'consumers': ['geo_experiment_consumer'],
                    'department': 'taxi',
                    'split_multidrafts': True,
                },
            ),
        ),  # stop
        pytest.param(
            {
                'task_id': '5f9b08b19da21d52ed964474',
                'draft_polygons': {
                    'prefix': 'alien_test_',
                    'polygons': [
                        {
                            'polyId': 'mscmo_pol0',
                            'name': 'mscmo_pol0',
                            'draft_name': 'mscmo_pol0',
                        },
                        {
                            'polyId': 'mscmo_pol2',
                            'name': 'mscmo_pol2',
                            'draft_name': 'mscmo_pol2',
                        },
                        {
                            'polyId': 'mscmo_pol3',
                            'name': 'mscmo_pol3',
                            'draft_name': 'mscmo_pol3',
                        },
                        {
                            'polyId': 'mscmo_pol5',
                            'name': 'mscmo_pol5',
                            'draft_name': 'mscmo_pol5',
                        },
                        {
                            'polyId': 'mscmo_pol6',
                            'name': 'mscmo_pol6',
                            'draft_name': 'mscmo_pol6',
                        },
                        {
                            'polyId': 'alien_mscmo_pol0',
                            'name': 'alien_mscmo_pol0',
                            'draft_name': 'alien_mscmo_pol0',
                        },
                    ],
                },
            },
            http.HTTPStatus.OK,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'BadRequest',
                'message': (
                    'Полигоны пересекаются с зонами, отсутствующими'
                    ' в расчете:\nalien_mscmo_pol0: reutov'
                ),
            },
            {},
        ),
        pytest.param(
            {
                'task_id': '5f9b08b19da21d52ed964475',
                'draft_polygons': DEFAULT_DRAFT_POLYGONS,
            },
            http.HTTPStatus.OK,
            http.HTTPStatus.OK,
            {
                'ticket_url': 'https://st.test.yandex-team.ru/TEST-1',
                'draft_id': 2,
                'draft_url': (
                    'https://tariff-editor.taxi.tst.'
                    'yandex-team.ru/drafts/multidraft/2/?multi=true'
                ),
            },
            {'expected_key': 'default'},
        ),
        pytest.param(
            {
                'task_id': '5f9b08b19da21d52ed964475',
                'draft_polygons': DEFAULT_DRAFT_POLYGONS,
                'tariffs': ['cargo'],
            },
            http.HTTPStatus.OK,
            http.HTTPStatus.OK,
            {
                'ticket_url': 'https://st.test.yandex-team.ru/TEST_LOG-1',
                'draft_id': 2,
                'draft_url': (
                    'https://tariff-editor.taxi.tst.'
                    'yandex-team.ru/drafts/multidraft/2/?multi=true'
                ),
            },
            {'expected_key': 'logistics'},
            marks=pytest.mark.config(
                ATLAS_GEOSUBVENTIONS=dict(
                    **DEFAULT_ATLAS_GEOSUBVENTIONS_CONFIG,
                    filter_tariffs_in_draft=False,
                ),
            ),
        ),
        pytest.param(
            {
                'task_id': '5f9b08b19da21d52ed964475',
                'draft_polygons': DEFAULT_DRAFT_POLYGONS,
            },
            http.HTTPStatus.OK,
            http.HTTPStatus.OK,
            {
                'ticket_url': 'https://st.test.yandex-team.ru/TEST-1',
                'draft_id': 2,
                'draft_url': (
                    'https://tariff-editor.taxi.tst.'
                    'yandex-team.ru/drafts/multidraft/2/?multi=true'
                ),
            },
            {'expected_key': 'no_tariffs_filter'},
            marks=pytest.mark.config(
                ATLAS_GEOSUBVENTIONS=dict(
                    **DEFAULT_ATLAS_GEOSUBVENTIONS_CONFIG,
                    filter_tariffs_in_draft=False,
                ),
            ),
        ),
        pytest.param(
            {
                'task_id': '5f9b08b19da21d52ed964476',
                'draft_polygons': DEFAULT_DRAFT_POLYGONS,
                'tag': 'test_tag',
            },
            http.HTTPStatus.OK,
            http.HTTPStatus.OK,
            {
                'ticket_url': 'https://st.test.yandex-team.ru/TEST-1',
                'draft_id': 2,
                'draft_url': (
                    'https://tariff-editor.taxi.tst.'
                    'yandex-team.ru/drafts/multidraft/2/?multi=true'
                ),
            },
            {'expected_key': 'main_tag'},
        ),
        pytest.param(
            {
                'task_id': '5f9b08b19da21d52ed964475',
                'draft_polygons': DEFAULT_DRAFT_POLYGONS,
            },
            http.HTTPStatus.OK,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'BadRequest',
                'message': (
                    'Total interval count limit of 1 rule intervals in'
                    ' moscow exceeded.\nGot: 6 total rules, where:6 new'
                    ' intervals\nTotal interval count limit of 1 rule '
                    'intervals in dolgoprudny exceeded.\nGot: 6 total '
                    'rules, where:6 new intervals\nTotal interval count'
                    ' limit of 1 rule '
                    'intervals in himki exceeded.\nGot: 6 total '
                    'rules, where:6 new intervals'
                ),
            },
            {},
            marks=pytest.mark.config(
                ATLAS_GEOSUBVENTION_RESTRICTIONS={
                    '__default__': {'max_total_intervals': 1},
                },
            ),
        ),
        pytest.param(
            {
                'task_id': 'unknowntask',
                'draft_polygons': {
                    'prefix': 'test_',
                    'polygons': [
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol0',
                            'name': 'pol1',
                            'draft_name': 'pol1',
                        },
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol1',
                            'name': 'pol2',
                            'draft_name': 'pol2',
                        },
                    ],
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            None,
            {
                'code': 'NotFound',
                'message': 'result for task unknowntask not found',
            },
            None,
        ),
        pytest.param(
            {
                'task_id': '6246a78d637ede004ba7ce35',
                'draft_polygons': {
                    'prefix': 'test_',
                    'polygons': [
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol0',
                            'name': 'pol1',
                            'draft_name': 'pol1',
                        },
                        {
                            'polyId': '5fb38a175e48dae578953b08_pol1',
                            'name': 'pol2',
                            'draft_name': 'pol2',
                        },
                    ],
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            None,
            {
                'code': 'Forbidden::CriticalWarnings',
                'message': 'Task result contains critical warnings',
                'details': {
                    'polygons': [
                        {
                            'critical': True,
                            'interval': {
                                'end_dayofweek': 1,
                                'end_time': '10:20',
                                'start_dayofweek': 1,
                                'start_time': '08:50',
                            },
                            'limit': 0.195,
                            'polyId': '6246a78d637ede004ba7ce35pol7',
                            'type': 'max_subgmv_critical',
                            'value': 0.196,
                        },
                    ],
                },
            },
            None,
            marks=pytest.mark.config(
                ATLAS_GEOSUBVENTION_RESTRICTIONS={
                    '__default__': {
                        'max_subgmv_critical': 19.5,
                        'max_subvention_area_ratio': 1,
                    },
                },
                ATLAS_GEOSUBVENTIONS_CRITICAL_WARNINGS=['max_subgmv_critical'],
            ),
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
@pytest.mark.now('2020-10-17 07:25:00')
@pytest.mark.geo_nodes(conftest.GEO_NODES)
@pytest.mark.config(
    OPERATION_CALCULATIONS_GEOSUBVENTIONS_TARIFF_PRESETS={
        'logistics': {'__default__': ['cargo']},
    },
    ATLAS_GEOSUBVENTIONS=DEFAULT_ATLAS_GEOSUBVENTIONS_CONFIG,
)
async def test_geosubventions_multidraft_task_pipeline(
        web_app_client,
        web_context,
        stq3_context,
        mock_billing_subventions_x,
        mockserver,
        mock_taxi_approvals,
        extra_parms,
        expected_md_status,
        expected_status,
        expected_content,
        test_data,
        test_params,
):
    params = copy.deepcopy(test_data['params'])
    params.update(**extra_parms)

    drafts = []
    bulk_created = []

    @mock_billing_subventions_x('/v2/rules/single_ride/bulk_create')
    def _bsx_bulk_create(request):
        bulk_created.append(request.json)
        return {'ruleset_ref': 'test_ref'}

    @mockserver.json_handler('/taxi_approvals/drafts/create/')
    def _handler(request):
        drafts.append(trim_exp_draft(request.json))
        return {'id': 10, 'version': 1, 'status': 'need_approval'}

    @mock_taxi_approvals('/drafts/create/')
    def _draft_create(request):
        drafts.append(trim_draft(request.json))
        return web.json_response(
            {'id': 1, 'version': 1, 'status': 'need_approval'},
        )

    @mockserver.json_handler('/taxi-exp-py3/v1/experiments/list/')
    def _exp_list_handler(request):
        offset = request.query.get('offset')
        return (
            test_data['current_experiments_list']
            if test_params.get('list_exp') and offset == '0'
            else {'experiments': []}
        )

    # Initiate task
    md_task_response = await web_app_client.post(
        '/v1/geosubventions/multidraft/tasks/',
        json=params,
        headers={'X-Yandex-Login': 'test_robot', 'Referer': 'http://some.url'},
    )
    assert md_task_response.status == expected_md_status
    if expected_md_status != http.HTTPStatus.OK:
        assert await md_task_response.json() == expected_content
        return
    md_task_id = (await md_task_response.json())['task_id']

    # Check task is not completed yet
    waiting_check = await web_app_client.get(
        f'/v1/geosubventions/multidraft/tasks/{md_task_id}/result/',
    )
    assert waiting_check.status == http.HTTPStatus.CONFLICT
    waiting_result = await waiting_check.json()
    assert waiting_result['error_type'] == 'task_not_completed_yet'

    # Run task
    await geosubventions_multidraft.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=md_task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    # Check result
    response = await web_app_client.get(
        f'/v1/geosubventions/multidraft/tasks/{md_task_id}/result/',
    )
    text = await response.json()
    assert text == expected_content
    assert response.status == expected_status
    if response.status == http.HTTPStatus.OK:
        expected_key = test_params['expected_key']
        drafts = sorted(
            drafts,
            key=lambda d: (
                d['api_path'],
                d['data'].get('rule_spec', {}).get('rule', {}).get('tag', ''),
                d['data'].get('rule_spec', {}).get('geoareas', []),
            ),
        )
        assert bulk_created + drafts == test_data['expected'][expected_key]
        if 'task_id' in params:
            storage = storage_lib.GeoSubventionsStorage(web_context)
            md_info = await storage.fetch(
                f"""
            select *
            from operation_calculations.geosubventions_multidrafts_info
             where multidraft_id = '{text['draft_id']}'
            """,
                fetch_single_row=True,
            )
            assert dict(md_info)
