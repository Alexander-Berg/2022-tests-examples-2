import pytest

from taxi.scripts import db as scripts_db


@pytest.mark.parametrize(
    'filter_param,expected_status,expected_response',
    [
        pytest.param(
            {'organizations': 'test-org'},
            400,
            {
                'status': 'error',
                'message': 'Unknown organizations test-org',
                'code': 'INVALID_ORGANIZATION',
            },
            id='filter_by_unknown_org',
        ),
        pytest.param(
            {'organizations': 'taximeter'},
            200,
            {'items': [{'id': 'test-filter-by-org'}]},
            id='filter_by_1_org',
        ),
        pytest.param(
            {'organizations': 'taximeter,taxi'},
            200,
            {
                'items': sorted(
                    [
                        {'id': 'test-filter-by-org'},
                        {'id': 'test-get-script'},
                        {'id': 'test-filter-exec-type-psql'},
                        {'id': 'test-filter-by-comment-1'},
                        {'id': 'test-filter-by-comment-2'},
                        {'id': 'test-filter-by-ticket'},
                        {'id': 'test-filter-by-script-1'},
                        {'id': 'test-filter-by-script-2'},
                        {'id': 'test-filter-by-arguments'},
                        {'id': 'test-filter-by-started-from'},
                        {'id': 'test-filter-by-run-status-approved-manual'},
                    ],
                    key=str,
                ),
            },
            id='filter_by_2_orgs',
        ),
        pytest.param(
            {},
            200,
            {
                'items': sorted(
                    [
                        {'id': 'test-filter-by-comment-1'},
                        {'id': 'test-filter-by-comment-2'},
                        {'id': 'test-filter-by-org'},
                        {'id': 'test-filter-by-run-status-approved-manual'},
                        {'id': 'test-filter-by-ticket'},
                        {'id': 'test-filter-exec-type-psql'},
                        {'id': 'test-get-script'},
                        {'id': 'test-filter-by-script-1'},
                        {'id': 'test-filter-by-script-2'},
                        {'id': 'test-filter-by-arguments'},
                        {'id': 'test-filter-by-started-from'},
                    ],
                    key=str,
                ),
            },
            id='no_filters',
        ),
        pytest.param(
            {'ticket': 'TAXIBACKEND-TEST'},
            200,
            {'items': [{'id': 'test-filter-by-org'}]},
            id='filter_by_ticket',
        ),
        pytest.param(
            {'ticket': 'ticket'},
            200,
            {'items': [{'id': 'test-filter-by-ticket'}]},
            id='filter_by_ticket_pattern',
        ),
        pytest.param(
            {'execute_type': 'psql'},
            200,
            {'items': [{'id': 'test-filter-exec-type-psql'}]},
            id='filter_by_psql_execute_type',
        ),
        pytest.param(
            {'created_by': 'someone'},
            200,
            {'items': []},
            id='filter_by_someone',
        ),
        pytest.param(
            {'created_by': ':me'},
            200,
            {
                'items': [
                    {'id': 'test-filter-by-org'},
                    {'id': 'test-filter-exec-type-psql'},
                ],
            },
            id='filter_by_me',
        ),
        pytest.param(
            {'comment': 'com'},
            200,
            {
                'items': sorted(
                    [
                        {'id': 'test-filter-by-comment-1'},
                        {'id': 'test-filter-by-comment-2'},
                    ],
                    key=str,
                ),
            },
            id='filter_by_comment',
        ),
        pytest.param(
            {'comment': 'com '},
            200,
            {'items': sorted([{'id': 'test-filter-by-comment-2'}], key=str)},
            id='filter_by_comment_with_spaces',
        ),
        pytest.param(
            {'name': 'taxi.'},
            200,
            {
                'items': sorted(
                    [
                        {'id': 'test-filter-by-script-1'},
                        {'id': 'test-filter-by-script-2'},
                    ],
                    key=str,
                ),
            },
            id='filter_by_script_name',
        ),
        pytest.param(
            {'name': 'pgmigrate.py'},
            200,
            {'items': []},
            id='filter_by_script_name_no_found',
        ),
        pytest.param(
            {'arguments': 'repository'},
            200,
            {'items': [{'id': 'test-filter-by-arguments'}]},
            id='filter_by_script_arguments',
        ),
        pytest.param(
            {'started_from': '2020-05-06T12:00:00.0Z'},
            200,
            {'items': [{'id': 'test-filter-by-started-from'}]},
            id='filter_by_start_time',
        ),
        pytest.param(
            {'status': scripts_db.ScriptStatus.APPROVED},
            200,
            {'items': [{'id': 'test-filter-by-run-status-approved-manual'}]},
            id='filter_by_approved_status_manual',
        ),
    ],
)
@pytest.mark.usefixtures('setup_many_scripts')
async def test_filter_scripts(
        patch,
        scripts_client,
        filter_param,
        expected_status,
        expected_response,
):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def _get_drafts_mock(data, log_extra):
        approvals_data = [
            {
                'change_doc_id': 'scripts_test-filter-by-org',
                'created_by': 'd1mbas',
                'id': 1,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
            {
                'change_doc_id': 'scripts_not-exists',
                'created_by': 'd1mbas',
                'id': 2,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
            {
                'change_doc_id': 'scripts_test-get-script',
                'created_by': 'test-login',
                'id': 3,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
            {
                'change_doc_id': 'scripts_test-filter-exec-type-psql',
                'created_by': 'd1mbas',
                'id': 3,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
            {
                'change_doc_id': 'scripts_test-filter-by-comment-1',
                'created_by': 'd1mbas',
                'id': 4,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
            {
                'change_doc_id': 'scripts_test-filter-by-comment-2',
                'created_by': 'd1mbas',
                'id': 5,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
            {
                'change_doc_id': 'scripts_test-filter-by-ticket',
                'created_by': 'd1mbas',
                'id': 6,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
            {
                'change_doc_id': 'scripts_test-filter-by-script-1',
                'created_by': 'd1mbas',
                'id': 7,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
            {
                'change_doc_id': 'scripts_test-filter-by-script-2',
                'created_by': 'd1mbas',
                'id': 8,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
            {
                'change_doc_id': 'scripts_test-filter-by-arguments',
                'created_by': 'd1mbas',
                'id': 8,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
            {
                'change_doc_id': 'scripts_test-filter-by-started-from',
                'created_by': 'd1mbas',
                'id': 8,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': scripts_db.ScriptStatus.APPLYING,
            },
            {
                'change_doc_id': (
                    'scripts_test-filter-by-run-status-approved-manual'
                ),
                'created_by': 'karachevda',
                'id': 3,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': True,
                'status': scripts_db.ScriptStatus.APPROVED,
            },
        ]
        change_doc_ids = data.get('change_doc_ids')
        if not change_doc_ids:
            return approvals_data
        return [
            x for x in approvals_data if x['change_doc_id'] in change_doc_ids
        ]

    response = await scripts_client.get(
        '/scripts/', params=filter_param, headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == expected_status
    data = await response.json()
    if 'items' in data:
        data['items'] = sorted(
            [{'id': x['id']} for x in data['items']], key=str,
        )
    assert data == expected_response
