import json

import pytest

from taxi_approvals.internal import headers as headers_module


def check_db(pgsql, expected_fields, expected_values):
    cursor = pgsql['approvals'].cursor()
    cursor.execute(
        'select service_name, api_path, path from approvals_schema.fields;',
    )
    fields = list(row for row in cursor)
    fields.sort()
    expected_fields.sort()
    assert fields == expected_fields
    cursor.execute(
        'select draft_id, value, value_type '
        'from approvals_schema.field_values;',
    )
    field_values = list(row for row in cursor)
    field_values.sort()
    expected_values.sort()
    assert field_values == expected_values


@pytest.mark.parametrize('is_platform', [False, True])
@pytest.mark.parametrize(
    'request_data, expected_ids, expected_fields, expected_values',
    [
        pytest.param(
            {
                'service_name': 'test_service',
                'api_path': 'test_api',
                'change_doc_id': 'change_doc_id_1',
                'request_id': 'request_id_1',
                'run_manually': False,
                'mode': 'push',
                'data': {
                    'project_id': 1,
                    'name': 'some_service',
                    'branches': [{'branch_id': 1}],
                },
            },
            [2],
            [
                ('test_service', 'test_api', 'name'),
                ('test_service', 'test_api', 'project_id'),
                ('test_service', 'test_api', 'branches.0.branch_id'),
            ],
            [
                (1, 'other_service_name', 'string'),
                (2, '1', 'integer'),
                (2, 'some_service', 'string'),
                (2, '1', 'integer'),
            ],
        ),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_create_draft(
        taxi_approvals_client,
        check_route_mock,
        create_reports_mock,
        pgsql,
        request_data,
        is_platform,
        expected_ids,
        expected_fields,
        expected_values,
):
    check_route_mock(
        change_doc_id=request_data['change_doc_id'],
        lock_ids=request_data.get('lock_ids_from_check'),
        route_method='POST',
        route_headers=request_data.get('route_headers'),
        route_params=request_data.get('route_params'),
        tickets=request_data.get('ticket_data_from_check'),
        summon_users=request_data.get('summon_users_from_check'),
        mode=request_data.get('check_mode'),
        data=request_data['data'],
        description='description from service answer',
    )
    headers = {headers_module.X_YANDEX_LOGIN: 'test_login'}
    params = {}
    if is_platform:
        headers[headers_module.X_MULTISERVICES_PLATFORM] = 'true'
        params = {'tplatform_namespace': 'taxi'}

    create_response = await taxi_approvals_client.post(
        '/drafts/create/', json=request_data, headers=headers, params=params,
    )
    assert create_response.status == 200
    check_db(pgsql, expected_fields, expected_values)


@pytest.mark.parametrize('is_platform', [False, True])
@pytest.mark.parametrize(
    'request_data, draft_id',
    [
        pytest.param(
            {
                'service_name': 'test_service',
                'mode': 'push',
                'api_path': 'test_api',
                'change_doc_id': 'change_doc_id_2',
                'request_id': 'request_id_2',
                'run_manually': False,
                'data': {
                    'project_id': 1,
                    'name': 'some_service',
                    'branches': [{'branch_id': 1}],
                },
            },
            1,
        ),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_edit_drafts(
        taxi_approvals_client,
        check_route_mock,
        is_platform,
        request_data,
        draft_id,
        pgsql,
):
    check_route_mock(
        change_doc_id=request_data.get('change_doc_id'),
        lock_ids=request_data.get('lock_ids_from_check'),
        route_method='POST',
        route_headers=request_data.get('route_headers'),
        route_params=request_data.get('route_params'),
    )
    headers = {headers_module.X_YANDEX_LOGIN: 'test_login'}
    if is_platform:
        headers[headers_module.X_MULTISERVICES_PLATFORM] = 'true'

    response = await taxi_approvals_client.post(
        f'/drafts/{draft_id}/edit/',
        data=json.dumps(request_data),
        headers={'X-Yandex-Login': 'test_user'},
        params={'tplatform_namespace': 'taxi'},
    )
    assert response.status == 200
    expected_fields = [
        ('test_service', 'test_api', 'name'),
        ('test_service', 'test_api', 'project_id'),
        ('test_service', 'test_api', 'branches.0.branch_id'),
    ]
    expected_values = [
        (1, '1', 'integer'),
        (1, 'some_service', 'string'),
        (1, '1', 'integer'),
    ]
    check_db(pgsql, expected_fields, expected_values)


@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_delete_draft(taxi_approvals_client, pgsql):
    draft_id = 1
    response = await taxi_approvals_client.delete(
        f'/drafts/{draft_id}/',
        headers={'X-Yandex-Login': 'test_user'},
        params={'tplatform_namespace': 'taxi'},
    )
    assert response.status == 200
    expected_fields = [
        ('test_service', 'test_api', 'branches.0.branch_id'),
        ('test_service', 'test_api', 'name'),
        ('test_service', 'test_api', 'project_id'),
    ]
    expected_values = []
    check_db(pgsql, expected_fields, expected_values)


@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_delete_draft_v2(taxi_approvals_client, pgsql):
    draft_id = 1
    response = await taxi_approvals_client.delete(
        f'/v2/drafts/',
        params={'id': draft_id, 'tplatform_namespace': 'taxi'},
        headers={'X-Yandex-Login': 'test_user'},
    )
    assert response.status == 200
    expected_fields = [
        ('test_service', 'test_api', 'branches.0.branch_id'),
        ('test_service', 'test_api', 'name'),
        ('test_service', 'test_api', 'project_id'),
    ]
    expected_values = []
    check_db(pgsql, expected_fields, expected_values)


@pytest.mark.translations(
    tariff_editor={
        'drafts.field.test_service.test_api.branches.0.branch_id': {
            'en': 'Branch id',
            'ru': 'Branch id в массиве',
        },
        'drafts.field.test_service.test_api.project_id': {
            'en': '',
            'ru': 'Айдишник проекта',
        },
    },
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
@pytest.mark.parametrize('locale', ['en-EN', 'ru-RU', None])
async def test_filter_fields(taxi_approvals_client, locale):
    headers = {}
    if locale:
        headers['Accept-Language'] = locale
    response = await taxi_approvals_client.post(
        '/v2/drafts/filters/fields/',
        headers=headers,
        json={'services_names': ['test_service'], 'api_paths': ['test_api']},
    )
    branch_title = 'Branch id в массиве'
    project_title = 'Айдишник проекта'
    if locale == 'en-EN':
        branch_title = 'Branch id'
        project_title = 'drafts.field.test_service.test_api.project_id'
    assert response.status == 200
    content = await response.json()
    assert content == {
        'fields': [
            {
                'api_path': 'test_api',
                'path': 'branches.0.branch_id',
                'service_name': 'test_service',
                'title': branch_title,
            },
            {
                'api_path': 'test_api',
                'path': 'name',
                'service_name': 'test_service',
                'title': 'drafts.field.test_service.test_api.name',
            },
            {
                'api_path': 'test_api',
                'path': 'project_id',
                'service_name': 'test_service',
                'title': project_title,
            },
        ],
    }
