import base64

from aiohttp import web
import pytest

DIFF_PARAMETERS = [
    {
        'subsystem_name': 'abc',
        'parameters': ['service_name', 'description', 'maintainers'],
    },
    {
        'subsystem_name': 'nanny',
        'parameters': [
            'cpu',
            'ram',
            'instances',
            'datacenters_count',
            'root_size',
            'persistent_volumes',
            'work_dir',
            'root_storage_class',
            'root_bandwidth_guarantee_mb_per_sec',
        ],
    },
    {
        'subsystem_name': 'service_info',
        'parameters': ['duty', 'duty_group_id'],
    },
]


DIFF_SERVICES = {
    'services': ['service_exist', 'service_2', 'test_yaml_generate'],
}


@pytest.mark.features_on('diff_validation')
@pytest.mark.parametrize(
    'cube_name',
    [
        'StartSyncRemoteParams',
        'UpdateServiceYamlParams',
        'SaveRemoteSubsystemConfig',
        'StartChangeAbcSubsystem',
        'WaitChangeSubsystem',
        'SaveRemoteAbcConfig',
        'CheckDiffForDeploy',
        'CreateDiffDraft',
        'WaitForDiffDraftApply',
        'ApplyDiffDraftCommentGenerate',
        'EndDiffCommentGenerate',
        'FindCurrentDiff',
        'CurrentDiffCommentGenerate',
        'StartChangeNannySubsystem',
        'GetPrestableForDiff',
        'GenerateCommentWaitDiffResolve',
        'PrepareServiceYaml',
        'StartResolveDiff',
        'ClownductorChangeProjectForService',
    ],
)
@pytest.mark.config(
    CLOWNDUCTOR_DIFF_PARAMETERS=DIFF_PARAMETERS,
    CLOWNDUCTOR_DIFF_CONFIGURATION=DIFF_SERVICES,
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql', 'add_test_jobs.sql'])
@pytest.mark.translations(
    clownductor={
        'tickets.parameters_errors_comment': {
            'en': (
                'The following errors were found in the parameters: '
                '{parameters_errors}. '
                'The diff will be skipped.'
            ),
            'ru': (
                'В параметрах были обнаружены следующие ошибки: '
                '{parameters_errors}. '
                'Дифф будет пропущен.'
            ),
        },
    },
)
async def test_params_handlers(
        web_app_client,
        web_context,
        cube_name,
        load_json,
        abc_mockserver,
        login_mockserver,
        staff_mockserver,
        mock_task_processor,
        mock_github,
        mockserver,
        patch,
        relative_load_plaintext,
        get_remote_params,
):
    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    # pylint: disable=W0612
    def taxi_approvals_drafts_list(request):
        return []

    @mockserver.json_handler('/taxi_approvals/drafts/create/')
    # pylint: disable=W0612
    def taxi_approvals_drafts_create(request):
        return {'id': 1}

    @mockserver.json_handler('/taxi_approvals/drafts/1/')
    # pylint: disable=W0612
    def taxi_approvals_drafts(request):
        return {
            'id': 1,
            'status': 'succeeded',
            'data': {'branch_id': 1},
            'tickets': ['TICKET-1', 'RUPRICING-4'],
        }

    @mock_task_processor('/v1/jobs/start/')
    # pylint: disable=W0612
    async def handler(request):  # pylint: disable=unused-argument
        return web.json_response({'job_id': 1})

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    # pylint: disable=unused-variable
    async def create_comment(*args, **kwargs):
        assert True

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    # pylint: disable=unused-variable
    async def get_myself(*args, **kwargs):
        return {'login': 'robot-taxi-clown'}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    # pylint: disable=unused-variable
    async def get_comments(*args, **kwargs):
        return []

    @mockserver.json_handler('/client-abc/v4/duty/schedules-cursor/')
    async def _schedule_cursor_mock(request):
        results = []
        if request.query['service__slug'] == 'existing-service':
            results.append(
                {
                    'id': 5152,
                    'name': 'Дежурство по сервисам',
                    'service': {'id': 37133, 'slug': 'existing-service'},
                    'duration': '7 00:00:00',
                    'start_date': '2022-04-04',
                    'slug': 'existing-schedule',
                },
            )
        return {'next': None, 'previous': None, 'results': results}

    abc_mockserver()
    login_mockserver()
    staff_mockserver()

    json_datas = load_json(f'request_data/{cube_name}.json')
    for json_data in json_datas:
        github_responses = load_json('github_responses.json')
        if json_data.get('mock_github'):
            key = json_data['mock_github']['key']
            file_content = json_data['mock_github']['yaml_content']
            yaml_data = relative_load_plaintext(file_content, 'rb')
            github_responses[key]['content']['content'] = base64.b64encode(
                yaml_data,
            )
        mock_github(github_responses)

        if json_data.get('expected_yaml'):
            expected_yaml = relative_load_plaintext(json_data['expected_yaml'])
            json_data['content_expected']['payload'][
                'content_service_yaml'
            ] = expected_yaml

        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected'], json_data.get(
            'expected_yaml', '',
        )


@pytest.mark.parametrize(
    'cube_name', [pytest.param('SaveRemoteNannyConfig', id='regular flow')],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_save_remote_nanny_config(
        web_app_client,
        cube_name,
        load_json,
        abc_mockserver,
        login_mockserver,
        staff_mockserver,
        mock_task_processor,
        get_remote_params,
):
    abc_mockserver()
    login_mockserver()
    staff_mockserver()

    json_datas = load_json(f'request_data/{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/SaveRemoteNannyConfig/',
            json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']

        remote_params = await get_remote_params(1, 1, 'nanny')
        remote_unstable = remote_params.unstable

        expected_params = json_data['expected_params']
        expected_dc = expected_params['dc']
        if expected_dc is None:
            assert remote_unstable.datacenters_regions.value == expected_dc
        else:
            assert set(remote_unstable.datacenters_regions.value) == set(
                expected_dc,
            )
            expected_dc_count = expected_params['dc_count']
            assert remote_unstable.datacenters_count.value == expected_dc_count
        assert (
            remote_unstable.network_bandwidth_guarantee_mb_per_sec.value
            == expected_params['network_guarantee']
        )
