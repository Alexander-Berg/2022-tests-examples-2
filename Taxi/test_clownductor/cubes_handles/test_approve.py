# pylint: disable=unused-variable
import pytest


def _clowny_roles_usage_switcher(feature: str):
    return pytest.mark.parametrize(
        '',
        [
            pytest.param(
                id=f'use clowny-roles for feature {feature}',
                marks=[pytest.mark.roles_features_on(feature)],
            ),
            pytest.param(
                id=f'do not use clowny-roles for feature {feature}',
                marks=[pytest.mark.roles_features_off(feature)],
            ),
        ],
    )


APPROVE_CHECK_SWITCHER = _clowny_roles_usage_switcher('approve_check')


@APPROVE_CHECK_SWITCHER
@pytest.mark.parametrize(
    'cube_name',
    [
        'ApproveCubeLiteGenerateApproveId',
        'GenerateTestingDeployMessage',
        'ApproveCubeLiteGeneratePreApproveId',
        'ApproveCubeLiteEnsureComment',
        'ApproveCubeOptionalLiteEnsureComment',
        'ApproveCubeLiteWaitForManagersApprove',
        'ApproveCubeLiteWaitForDevelopersApprove',
        'ApproveCubeLiteWaitForSingleApprove',
        'WaitForDiffCommentApprove',
        'ApproveGenerateInstruction',
    ],
)
@pytest.mark.pgsql('clownductor', files=['test_approve.sql'])
@pytest.mark.config(
    CLOWNDUCTOR_RELEASE_ST_COMMENT_SETTINGS={'verbose_enabled': True},
    CLOWNDUCTOR_FEATURES={
        'render_instruction': True,
        'enable_testing_deploy_message': True,
    },
)
@pytest.mark.features_on('startrek_close_approval')
async def test_post_approve_cubes_handles(
        web_app_client,
        cube_name,
        load_json,
        cookie_monster_mockserver,
        patch,
        st_get_myself,
        st_create_comment,
        add_grant,
        clowny_roles_grants,
):
    cookie_monster_mockserver()
    await add_grant(
        'some-developer1', 'deploy_approve_programmer', project_id=1,
    )
    await add_grant('some-manager1', 'deploy_approve_manager', project_id=1)
    clowny_roles_grants.add_dev_approver(
        'some-developer1', {'id': 'test_project', 'type': 'project'},
    )
    clowny_roles_grants.add_manager_approver(
        'some-manager1', {'id': 'test_project', 'type': 'project'},
    )

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def get_comments(*args, **kwargs):
        comments_map = {
            'ApproveCubeLiteWaitForManagersApprove': [
                {
                    'login': 'robot-taxi-clown',
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': 'some comment here',
                },
            ],
            'ApproveCubeLiteWaitForDevelopersApprove': [
                {
                    'login': 'some-developer1',
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': 'OK for release:456',
                },
                {
                    'login': 'robot-taxi-clown',
                    'time': '2000-06-28T15:25:25.361+0000',
                    'text': 'OK for release:456',
                },
            ],
        }
        comments = comments_map.get(cube_name, [])
        if 'short_id' in kwargs and kwargs['short_id'] is not None:
            return []
        return [
            {
                'id': id(entry),
                'text': entry['text'],
                'createdBy': {'id': entry['login']},
                'createdAt': entry['time'],
            }
            for entry in comments
        ]

    @patch('taxi.clients.startrack.StartrackAPIClient.get_field_history')
    async def get_field_history(*args, **kwargs):
        history = [
            {
                'login': 'some-manager1',
                'time': '2001-06-28T15:27:25.361+0000',
                'to': 'readyForRelease',
            },
        ]
        return [
            {
                'fields': [{'to': {'key': entry['to']}}],
                'updatedBy': {'id': entry['login']},
                'updatedAt': entry['time'],
            }
            for entry in history
        ]

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def get_ticket(ticket):
        return {'status': {'key': 'open'}, 'assignee': {'id': 'deoevgen'}}

    @patch(
        'clownductor.generated.service.conductor_api.'
        'plugin.ConductorClient.get_approvers',
    )
    async def _get_approvers(*args, **kwargs):
        return [str(arg) for arg in args if arg is not None]

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200, str(
            (data_request, await response.text()),
        )
        content = await response.json()
        assert content == json_data['content_expected']


@APPROVE_CHECK_SWITCHER
@pytest.mark.pgsql('clownductor', files=['test_approve.sql'])
async def test_post_approve_cube_get_approvers_handle(
        web_app_client,
        load_json,
        cookie_monster_mockserver,
        patch,
        add_grant,
        clowny_roles_grants,
):
    cookie_monster_mockserver()
    await add_grant(
        'some-developer1', 'deploy_approve_programmer', project_id=1,
    )
    await add_grant('some-manager1', 'deploy_approve_manager', project_id=1)
    clowny_roles_grants.add_dev_approver(
        'some-developer1', {'id': 'test_project', 'type': 'project'},
    )
    clowny_roles_grants.add_manager_approver(
        'some-manager1', {'id': 'test_project', 'type': 'project'},
    )

    @patch(
        'clownductor.generated.service.conductor_api.'
        'plugin.ConductorClient.get_approvers',
    )
    async def _get_approvers(*args, **kwargs):
        return [str(arg) for arg in args if arg is not None]

    json_datas = load_json('ApproveCubeGetApprovers.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/ApproveCubeGetApprovers/',
            json=data_request,
        )
        assert response.status == 200, str(
            (data_request, await response.text()),
        )
        content = await response.json()
        assert content == json_data['content_expected']


@pytest.mark.parametrize(
    ['comment_text', 'login', 'bad'],
    [
        pytest.param('pray continue', 'nikslim', False, id='ok'),
        pytest.param('just some comment', 'nikslim', True, id='bad_comment'),
        pytest.param('pray continue', 'some-man', True, id='bad_user'),
    ],
)
@pytest.mark.translations(
    clownductor={
        'tickets.approval_with_abc_role_bad': {
            'ru': 'Логин: {login}; ABC: {abc_slug}; Роли: {role_names};',
        },
    },
)
async def test_approve_abc_role(
        call_cube_handle,
        st_get_myself,
        patch,
        abc_mockserver,
        st_create_comment,
        comment_text,
        login,
        bad,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def get_comments(*args, **kwargs):
        if 'short_id' in kwargs and kwargs['short_id'] is not None:
            return []
        return [
            {
                'id': 1,
                'text': comment_text,
                'createdBy': {'id': login},
                'createdAt': '2000-06-28T15:25:25.361+0000',
            },
        ]

    abc_mockserver()
    content = {'status': 'success'}
    if bad:
        content = {'sleep_duration': 10, 'status': 'in_progress'}
    await call_cube_handle(
        'ApproveWaitForApprovalWithAbcRole',
        {
            'content_expected': content,
            'data_request': {
                'input_data': {
                    'st_key': 'TAXIADMIN-000',
                    'abc_slug': 'some-service',
                    'key_phrase': 'pray continue',
                    'roles_ids_to_check': [1257, 5, 1, 2],
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    if login != 'nikslim' and comment_text == 'pray continue':
        calls = st_create_comment.calls
        expected_text = (
            'Логин: some-man; ABC: some-service; '
            'Роли: Руководитель сервиса, Менеджер проектов, '
            'Менеджер по маркетингу, Разработчик 3;'
        )
        assert calls[0]['text'] == expected_text
    else:
        assert not st_create_comment.calls


def _make_job_vars(assignee_is_robot: bool = False):
    return {
        'service_id': 1,
        'tickets_info': {
            'COOLTASK-1': {
                'key': 'COOLTASK-1',
                'status': {'id': '4', 'key': 'inProgress'},
                'createdBy': {'id': 'd1mbas', 'is_robot': False},
                'assignee': {'id': 'deoevgen', 'is_robot': assignee_is_robot},
                'followers': [
                    {'id': 'oxcd8o', 'is_robot': False},
                    {'id': 'eatroshkin', 'is_robot': False},
                    {'id': 'deoevgen', 'is_robot': True},
                ],
            },
        },
    }


@pytest.mark.pgsql('clownductor', files=['test_approve.sql'])
@pytest.mark.parametrize(
    'job_vars, expected_payload',
    [
        pytest.param(
            _make_job_vars(True),
            {
                'summonees': ['eatroshkin', 'oxcd8o'],
                'release_id': 'release:1',
                'release_key_phrase': 'OK for release:1',
                'border_comment': (
                    'The resource alteration on prestable is done.\n'
                    'Expecting release approval: internal id '
                    '((/services/1/edit/1/jobs?jobId=1&isClownJob=true '
                    'release:1)).\n\n**Developers should write:**\n'
                    '%%\nOK for release:1\n%%\nin '
                    'the comments to this ticket.\n'
                ),
                'end_border_comment': 'The resource alteration was finished',
                'skip': False,
            },
            id='assignee_is_robot',
            marks=pytest.mark.features_on('enable_approve_change_resources'),
        ),
        pytest.param(
            _make_job_vars(True),
            {
                'skip': True,
                'end_border_comment': 'The resource alteration was finished',
                'summonees': [],
                'release_id': '',
                'release_key_phrase': '',
                'border_comment': '',
            },
            id='assignee_is_robot_features_off',
            marks=pytest.mark.features_off('enable_approve_change_resources'),
        ),
        pytest.param(
            _make_job_vars(),
            {
                'summonees': ['deoevgen'],
                'release_id': 'release:1',
                'release_key_phrase': 'OK for release:1',
                'border_comment': (
                    'The resource alteration on prestable is done.\n'
                    'Expecting release approval: internal id '
                    '((/services/1/edit/1/jobs?jobId=1&isClownJob=true '
                    'release:1)).\n\n**Developers should write:**\n'
                    '%%\nOK for release:1\n%%\nin '
                    'the comments to this ticket.\n'
                ),
                'end_border_comment': 'The resource alteration was finished',
                'skip': False,
            },
            id='assignee_is_not_robot_features_on',
            marks=pytest.mark.features_on('enable_approve_change_resources'),
        ),
    ],
)
async def test_generate_comment_change_resources(
        job_vars, expected_payload, call_cube_handle,
):
    data = {
        'content_expected': {'payload': expected_payload, 'status': 'success'},
        'data_request': {
            'input_data': job_vars,
            'job_id': 1,
            'retries': 0,
            'status': 'in_progress',
            'task_id': 1,
        },
    }
    await call_cube_handle('ApproveCubeGenerateCommentChangeResources', data)


@pytest.mark.usefixtures('clowny_roles_grants')
@pytest.mark.pgsql('clownductor', files=['test_approve.sql'])
@pytest.mark.parametrize(
    'cube_name, data_yaml',
    [
        pytest.param(
            'ApproveCubeLiteWaitForDevelopersApprove',
            'ApproveCubeLiteWaitForDevelopersApprove-non-authorized.yaml',
            marks=[pytest.mark.roles_features_off('approve_check')],
        ),
        pytest.param(
            'ApproveCubeLiteWaitForDevelopersApprove',
            (
                'ApproveCubeLiteWaitForDevelopersApprove-'
                'non-authorized-new_roles.yaml'
            ),
            marks=[pytest.mark.roles_features_on('approve_check')],
        ),
    ],
)
async def test_cube_for_creating_st_comment(
        mockserver, load_yaml, call_cube_handle, cube_name, data_yaml,
):
    @mockserver.json_handler('/startrek/myself')
    def _get_myself(_):
        return {'login': 'robot-clown'}

    @mockserver.json_handler('/startrek/issues/TAXIADMIN-10000/comments')
    def _comments(request):
        if request.method == 'POST':
            return {}

        if request.query.get('id'):
            return []
        return [
            {
                'id': 1,
                'createdAt': '1',
                'createdBy': {'id': 'robot-clown'},
                'text': '',
            },
            {
                'id': 2,
                'createdAt': '2',
                'createdBy': {'id': 'some-dev'},
                'text': 'OK for release:456',
            },
        ]

    def _assert_calls(test_case):
        # 2 get comments calls
        _comments.next_call()
        _comments.next_call()
        # 1 create comment call
        call = _comments.next_call()
        assert call['request'].method == 'POST'
        assert call['request'].json['text'] == test_case['st']['text'].rstrip()
        assert not _comments.has_calls

    data = load_yaml(data_yaml)
    for case in data:
        await call_cube_handle(cube_name, case['cube_data'])
        _assert_calls(case)
