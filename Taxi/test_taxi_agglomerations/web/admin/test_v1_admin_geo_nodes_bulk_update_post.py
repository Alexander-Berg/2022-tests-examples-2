import datetime
from typing import Optional

import pytest

_NOW = datetime.datetime(2016, 6, 30)

DRAFT_ID = 1
DRAFT_VERSION = 10
MULTI_DRAFT_ID = 100

PARAMETRIZE = (
    pytest.param(
        {'geo_node_names': ['br_root'], 'tags': {'type': 'APPEND'}},
        400,
        None,
        [],
        None,
        None,
        {
            'code': 'INVALID_RULE',
            'message': (
                '[\'error during updating "br_root": '
                'value cannot be None when '
                'type is APPEND\']'
            ),
        },
        id='append_without_value',
    ),
    pytest.param(
        {
            'geo_node_names': ['br_root'],
            'tags': {'type': 'SET', 'value': ['test_tag']},
            'regional_managers': {'type': 'SET', 'value': ['test_reg_man']},
            'operational_managers': {'type': 'SET', 'value': ['test_op_man']},
            'macro_managers': {'type': 'SET', 'value': ['test_mac_man']},
            'oebs_mvp_id': {'type': 'SET', 'value': 'test_oebs_mvp_id'},
            'region_id': {'type': 'SET'},
        },
        400,
        {
            'change_doc_ids': ['agglomerations_br_root'],
            'statuses': ['need_approval'],
        },
        [{'id': 123, 'version': 2}],
        None,
        None,
        {
            'code': 'DRAFT_FOR_GEO_NODE_ALREADY_EXIST',
            'message': 'Existing draft_ids=[123]',
        },
        id='draft_already_exist',
    ),
    pytest.param(
        {
            'geo_node_names': ['br_root'],
            'tags': {'type': 'SET', 'value': ['test_tag']},
            'regional_managers': {'type': 'SET', 'value': ['test_reg_man']},
            'operational_managers': {'type': 'SET', 'value': ['test_op_man']},
            'macro_managers': {'type': 'SET', 'value': ['test_mac_man']},
            'oebs_mvp_id': {'type': 'SET', 'value': 'test_oebs_mvp_id'},
            'region_id': {'type': 'SET', 'value': 'region_id'},
        },
        200,
        {
            'change_doc_ids': ['agglomerations_br_root'],
            'statuses': ['need_approval'],
        },
        [],
        {
            'mode': 'push',
            'service_name': 'agglomerations',
            'api_path': 'agglomerations_admin_create_update_geonode',
            'run_manually': False,
            'data': {
                'name': 'br_root',
                'tanker_key': 'name.br_root',
                'hierarchy_type': 'BR',
                'node_type': 'root',
                'name_ru': 'Базовая иерархия',
                'name_en': 'Basic Hierarchy',
                'children': ['br_russia', 'br_kazakhstan'],
                'tags': ['test_tag'],
                'region_id': 'region_id',
                'oebs_mvp_id': 'test_oebs_mvp_id',
                'regional_managers': ['test_reg_man'],
                'operational_managers': ['test_op_man'],
                'macro_managers': ['test_mac_man'],
            },
        },
        {
            'data': {
                'geo_node_names': ['br_root'],
                'tags': {'type': 'SET', 'value': ['test_tag']},
                'regional_managers': {
                    'type': 'SET',
                    'value': ['test_reg_man'],
                },
                'operational_managers': {
                    'type': 'SET',
                    'value': ['test_op_man'],
                },
                'macro_managers': {'type': 'SET', 'value': ['test_mac_man']},
                'region_id': {'type': 'SET', 'value': 'region_id'},
                'oebs_mvp_id': {'type': 'SET', 'value': 'test_oebs_mvp_id'},
            },
            'description': 'Балковое изменение геонод',
            'attach_drafts': [{'id': DRAFT_ID, 'version': DRAFT_VERSION}],
        },
        {'multidraft_id': str(MULTI_DRAFT_ID)},
        id='set',
    ),
)


@pytest.mark.parametrize(
    'body, '
    'expected_status, '
    'expected_drafts_list_request,'
    'existing_drafts,'
    'expected_create_draft_request,'
    'expected_create_multi_draft_request,'
    'expected_content',
    PARAMETRIZE,
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb()
async def test_v1_admin_geo_nodes_bulk_update_post(
        web_app_client,
        mockserver,
        body,
        expected_status,
        expected_drafts_list_request,
        existing_drafts,
        expected_content,
        expected_create_draft_request,
        expected_create_multi_draft_request,
):
    drafts_list_request: Optional[dict] = None
    create_draft_request: Optional[dict] = None
    create_multi_draft_request: Optional[dict] = None

    @mockserver.json_handler('/taxi-approvals/drafts/list/')
    def _approvals_drafts_list(request):
        nonlocal drafts_list_request
        drafts_list_request = request.json
        return existing_drafts

    @mockserver.json_handler('/taxi-approvals/drafts/create/')
    def _approvals_create_draft(request):
        request.json.pop('request_id')
        nonlocal create_draft_request
        create_draft_request = request.json
        return {'id': DRAFT_ID, 'version': DRAFT_VERSION}

    @mockserver.json_handler('/taxi-approvals/multidrafts/create/')
    def _approvals_create_multidraft(request):
        request.json.pop('request_id')
        nonlocal create_multi_draft_request
        create_multi_draft_request = request.json
        return {'id': MULTI_DRAFT_ID}

    response = await web_app_client.post(
        'v1/admin/geo-nodes/bulk-update',
        json=body,
        headers={'X-Yandex-Login': 'robot'},
    )
    assert response.status == expected_status
    assert await response.json() == expected_content
    assert create_draft_request == expected_create_draft_request
    assert create_multi_draft_request == expected_create_multi_draft_request
    assert drafts_list_request == expected_drafts_list_request
