import pytest


@pytest.fixture
def mock_vault_session(mockserver):
    @mockserver.json_handler('/vault-api/', prefix=True)
    def _request(request):
        return mockserver.make_response(
            json={
                'status': 'ok',
                'version': {
                    'value': [
                        {'key': 'project', 'value': 'test_project'},
                        {'key': 'provider_name', 'value': 'test_provider'},
                        {'key': 'user', 'value': 'user'},
                        {'key': 'host', 'value': 'host'},
                        {'key': 'port', 'value': 'port'},
                        {'key': 'db_name', 'value': 'db_name'},
                    ],
                },
            },
        )

    return _request


@pytest.mark.parametrize(
    ['data', 'expected_status', 'expected_data'],
    [
        (
            {
                'service_name': 'test_service_1',
                'type': 'secdist',
                'data': '{ {{ TEST_1 }} }',
            },
            200,
            {'is_valid': True},
        ),
        (
            {'service_name': 'test_service_1', 'type': 'secdist', 'data': ''},
            400,
            {
                'is_valid': False,
                'details': (
                    'template is not valid cause of follow error: '
                    'template is empty'
                ),
            },
        ),
        (
            {
                'service_name': 'test_service_1',
                'type': 'secdist',
                'data': ' {{ TEST_2 }} }',
            },
            400,
            {
                'is_valid': False,
                'details': (
                    'template is not valid cause of follow error: '
                    'template is not a valid JSON (Extra data: '
                    'line 1 column 17 (char 16))'
                ),
            },
        ),
        (
            {
                'service_name': 'test_service_1',
                'type': 'secdist',
                'data': '{ {{ TEST_3 }} }',
            },
            400,
            {
                'is_valid': False,
                'details': (
                    'template is not valid cause of follow error: '
                    'some variables ({\'TEST_3\'}) have no value to render'
                ),
            },
        ),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_templates.sql'])
@pytest.mark.usefixtures('mock_vault_session')
async def test_templates_check(
        web_app_client, data, expected_status, expected_data,
):
    response = await web_app_client.post(
        '/v1/templates/check/',
        headers={'X-YaTaxi-Api-Key': 'strongbox_api_token'},
        json=data,
    )
    assert response.status == expected_status
    if expected_data is not None:
        result = await response.json()
        assert result['is_valid'] == expected_data['is_valid']
        if 'details' in expected_data:
            assert (
                result['details'].strip() == expected_data['details'].strip()
            )


@pytest.mark.features_on('arcadia_pr_creation')
@pytest.mark.usefixtures('mock_vault_session')
@pytest.mark.pgsql('strongbox', files=['test_templates.sql'])
@pytest.mark.parametrize(
    'existed_job_vars', [None, {}, {'pull_request_url': 'arcadia_url'}],
)
async def test_templates_arcadia_upsert(
        web_app_client, mockserver, existed_job_vars,
):
    @mockserver.json_handler(
        '/task-processor/v1/jobs/retrieve_by_change_doc_id/',
    )
    async def _retrieve_by_change_doc_id(request):
        change_doc_id = 'ArcadiaChangeTemplate-test_service_3'
        assert request.json['change_doc_id'] == change_doc_id
        if existed_job_vars is not None:
            return {
                'jobs': [
                    {
                        'id': 122,
                        'status': 'in_progress',
                        'recipe_id': 1,
                        'name': 'ArcadiaChangeTemplate',
                        'created_at': 1,
                        'job_vars': existed_job_vars,
                        'change_doc_id': change_doc_id,
                    },
                ],
            }
        return mockserver.make_response(json={}, status=404)

    @mockserver.json_handler('/task-processor/v1/jobs/start/')
    async def _start(_request):
        return {'job_id': 123}

    response = await web_app_client.post(
        '/v1/templates/upsert/',
        headers={'X-YaTaxi-Api-Key': 'strongbox_api_token'},
        json={
            'service_name': 'test_service_3',
            'type': 'secdist',
            'ticket': 'TAXIPLATFORM-1116',
            'data': '{ {{ TEST_1 }} }',
        },
    )
    if existed_job_vars is None:
        assert response.status == 200
        assert await response.json() == {
            'job_link': (
                'https://tariff-editor.taxi.yandex-team.ru/task-processor'
                '/providers/4/jobs/edit/123?provider_id=4'
            ),
        }
    else:
        assert response.status == 400
        msg = (
            'Job is already created: '
            'https://tariff-editor.taxi.yandex-team.ru/task-processor'
            '/providers/4/jobs/edit/122?provider_id=4'
        )
        if existed_job_vars.get('pull_request_url'):
            msg = 'Pull request already exists: arcadia_url'
        assert await response.json() == {
            'code': 'UNABLE_TO_CREATE_PULL_REQUEST',
            'message': msg,
        }


@pytest.mark.parametrize(
    ['service_name', 'expected_data'],
    [
        ('test_service_1', '{"test_service_1_key": "value"}'),
        ('test_service_2', '{"key" : "value"}\n'),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_templates.sql'])
async def test_templates_get(web_app_client, service_name, expected_data):

    response = await web_app_client.get(
        '/v1/templates/',
        headers={'X-YaTaxi-Api-Key': 'strongbox_api_token'},
        params={'service_name': service_name},
    )
    assert response.status == 200
    data = await response.json()
    assert data['data'] == expected_data
