# pylint: disable=redefined-outer-name
import collections
import itertools
import json

import jinja2
import pytest

from clownductor.internal.tasks import processor
from clownductor.internal.utils import postgres


@pytest.fixture(name='grafana_api_search_existed_dashboard')
def _grafana_api_search_existed_dashboard():
    return [
        'nanny_test_service_stable',
        'nanny_test_service_2_stable',
        'nanny_test_service_3_stable',
    ]


BORDER_COMMENT = jinja2.Template(
    '**Stable:**\n'
    'Waiting for approves for release with internal id '
    '((/services/1/edit/{{service_id}}/jobs?jobId=4&isClownJob=true '
    'release:4)).\n\n'
    '{{ "Deploy image: {image}\n\n".format(image=image) if image}}'
    '**Managers should approve** by setting status '
    '"ready for release" to this ticket.\n'
    '**After this, developers should write:**\n%%\nOK for release:4\n%%\n'
    'in the comments to this ticket.\n\n'
    'See the instruction for the deploy ((https://wiki.yandex-team.ru/'
    'taxi/backend/basichowto/deploy/ here)).\n',
)

TRANSLATIONS = {
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
}


@pytest.fixture
def check_lock(web_context):
    async def do_it(job_id, exists=True):
        job_ids = await web_context.service_manager.jobs.get_remote_ids_or_own(
            [job_id],
        )
        assert len(job_ids) == 1
        job_id = job_ids[0]['job_id']
        locks = await web_context.locks.find(job_id=job_id)
        if exists:
            assert locks, f'lock did not created for job {job_id}'
        else:
            assert (
                not locks
            ), f'lock exists but not expected for job {job_id}: {locks}'

    return do_it


@pytest.mark.pgsql('clownductor', files=['test_deploy_job_data.sql'])
@pytest.mark.parametrize(
    'test_file_name',
    [
        'deploy_unstable_no_aliases.json',
        'deploy_unstable_aliases.json',
        'deploy_stable_no_aliases.json',
        'deploy_stable_aliases.json',
        pytest.param(
            'deploy_stable_aliases_reversed.json',
            marks=[
                pytest.mark.pgsql(
                    'clownductor',
                    files=[
                        'clear_all_related_services.sql',
                        'test_deploy_job_data_related_inversed.sql',
                    ],
                ),
            ],
        ),
        'deploy_stable_same_name.json',
        'deploy_unstable_sandbox_resources_no_aliases.json',
        'deploy_unstable_sandbox_resources_with_aliases.json',
        'deploy_stable_sandbox_resources_no_aliases.json',
        'deploy_stable_sandbox_resources_with_aliases.json',
        'deploy_stable_aliases_incorrect_order.json',
        'deploy_stable_logbroker_configuration.json',
        'depoy_unstable_logbroker_configuration.json',
    ],
)
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'new_get_approvers': True,
        'tc_deploy_changelog': True,
        'cancel_old_deploys': True,
        'named_target_deploy': True,
        'locks_for_deploy': True,
        'diff_validation': True,
        'update_hosts_cube_enabled': True,
        'enable_testing_deploy_message': True,
    },
    CLOWNDUCTOR_RELEASE_ST_COMMENT_SETTINGS={'verbose_enabled': True},
    CLOWNDUCTOR_DIFF_PARAMETERS=[
        {'subsystem_name': 'nanny', 'parameters': ['cpu']},
    ],
    CLOWNDUCTOR_DIFF_CONFIGURATION={
        'services': ['test_service', 'test_service_2', 'test_service_3'],
    },
    CLOWNDUCTOR_STARTREK_QUEUE_COMPONENTS={'TAXIREL': [42]},
    CLOWNDUCTOR_FEATURES_PER_SERVICE={
        '__default__': {'enable_logbroker_configuration': True},
    },
)
@pytest.mark.features_on('startrek_close_approval')
@pytest.mark.features_on(
    'startrek_clown_component', 'main_service_from_relation',
)
@pytest.mark.translations(clownductor=TRANSLATIONS)
async def test_teamcity_deploy_job(
        web_app_client,
        mockserver,
        login_mockserver,
        nanny_mockserver,
        conductor_mockserver,
        staff_mockserver,
        test_file_name,
        get_job,
        web_context,
        get_job_variables,
        get_task,
        load_json,
        patch,
        patch_github_single_file,
        add_grant,
):  # pylint: disable=R0913
    login_mockserver()
    conductor_mockserver()
    staff_mockserver()
    patch_github_single_file(
        'services/test_service/service.yaml', 'uservice.yaml',
    )
    await add_grant('mvpetrov', 'deploy_approve_programmer', project_id=1)
    await add_grant('bruno', 'deploy_approve_manager', project_id=1)

    test_info = load_json(test_file_name)
    created_drafts = {}

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text, *args, **kwargs):
        if 'There are already exists resolve diff jobs' in text:
            await _update_job(web_context, 1000, 'success')
            await _update_job(web_context, 1002, 'success')
        assert ticket

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def get_myself(*args, **kwargs):
        return {'login': 'robot-taxi-clown'}

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def _create_draft_mock(data, login, *args, **kwargs):
        draft = {'id': data['data']['branch_id'], **data}
        draft['tickets'] = ['TICKET-1', 'RUPRICING-4']
        created_drafts[draft['change_doc_id']] = draft
        await _add_resolve_diff_job(
            web_context, data['data']['branch_id'], 'success',
        )
        return draft

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def _get_drafts_mock(data, *args, **kwargs):
        change_doc_id = data['change_doc_ids'][0].replace('clownductor_', '')
        draft = created_drafts.get(change_doc_id)
        if draft:
            draft['status'] = 'succeeded'
            return [draft]
        return None

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def _get_draft_mock(draft_id, *args, **kwargs):
        change_doc_id = 'DIFF_RESOLVE_{}'.format(draft_id)
        draft = created_drafts.get(change_doc_id)
        if draft:
            draft['status'] = 'succeeded'
            return draft
        return None

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def get_ticket(ticket):
        return {'status': {'key': 'open'}}

    @patch('taxi.clients.startrack.StartrackAPIClient.execute_transition')
    async def _execute_transaction(
            ticket_key, transition, data, *args, **kwargs,
    ):
        assert transition == 'close'
        assert data == {'resolution': 'fixed'}
        return {}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def get_comments(*args, **kwargs):
        if 'short_id' in kwargs and kwargs['short_id'] is not None:
            return []
        service_id = 1
        image = test_info['request_data'].get('docker_image')
        if test_file_name == 'deploy_unstable_no_aliases_diff_collision.json':
            service_id = 9
        if test_file_name == 'deploy_stable_aliases_reversed.json':
            service_id = 3
        if test_file_name == 'deploy_stable_same_name.json':
            service_id = 4
        if test_info['request_data'].get('aliases'):
            inited_vars = test_info['expected_jobs'][0]['inited_variables']
            all_names = itertools.chain(
                [inited_vars['name']],
                [item['nanny_name'] for item in inited_vars['aliases']],
            )
            parts = [
                'This is release for several services:',
                *[f'* **{name}**' for name in all_names],
                '',
                'Approve messages will trigger deploy for all services above.',
                '',
                BORDER_COMMENT.render(service_id=service_id, image=image),
            ]
            comment = '\n'.join(parts)
        else:
            comment = BORDER_COMMENT.render(service_id=service_id, image=image)
        return [
            {
                'self': 'url_to_comment',
                'id': 1,
                'createdBy': {'id': 'robot-taxi-clown'},
                'createdAt': '2100-06-28T15:27:25.358+0000',
                'updatedAt': '2100-06-28T15:27:25.358+0000',
                'text': comment,
            },
            {
                'self': 'url_to_comment',
                'id': 2,
                'createdBy': {'id': 'mvpetrov'},
                'createdAt': '2100-06-28T15:27:25.359+0000',
                'updatedAt': '2100-06-28T15:27:25.359+0000',
                'text': 'OK for diff_resolve:4',
            },
            {
                'self': 'url_to_comment',
                'id': 3,
                'createdBy': {'id': 'mvpetrov'},
                'createdAt': '2100-06-28T15:27:25.361+0000',
                'updatedAt': '2100-06-28T15:27:25.361+0000',
                'text': 'PRESTABLE OK for release:4',
            },
            {
                'self': 'url_to_comment',
                'id': 4,
                'createdBy': {'id': 'mvpetrov'},
                'createdAt': '2100-06-28T15:27:27.361+0000',
                'updatedAt': '2100-06-28T15:27:27.361+0000',
                'text': 'OK for release:4',
            },
            {
                'self': 'url_to_comment',
                'id': 5,
                'createdBy': {'id': 'mvpetrov'},
                'createdAt': '2100-06-28T15:27:27.361+0000',
                'updatedAt': '2100-06-28T15:27:27.361+0000',
                'text': 'CLOSE TICKET for release:4',
            },
        ]

    @patch('taxi.clients.startrack.StartrackAPIClient.get_field_history')
    async def get_field_history(*args, **kwargs):
        return [
            {
                'fields': [{'to': {'key': 'readyForRelease'}}],
                'updatedBy': {'id': 'bruno'},
                'updatedAt': '2100-06-28T15:27:26.361+0000',
            },
        ]

    @mockserver.json_handler('/logs-from-yt/v1/logbroker/configure')
    def _mock_configure(request):
        return {
            'operations': [
                {'id': '777', 'installation': 'logbroker.yandex.net'},
            ],
        }

    @mockserver.json_handler('/logs-from-yt/v1/logbroker/configure/status')
    def _mock_configure_status(request):
        return {
            'operations': [
                {
                    'id': '777',
                    'logbroker_installation': 'logbroker.yandex.net',
                    'ready': True,
                    'success': True,
                },
            ],
        }

    @mockserver.json_handler('/client-abc/v4/duty/schedules-cursor/')
    async def _schedule_cursor_mock(request):
        return {'next': None, 'previous': None, 'results': []}

    result = await web_app_client.post(
        '/api/teamcity_deploy',
        json=test_info['request_data'],
        headers={'X-YaTaxi-Api-Key': 'valid_teamcity_token'},
    )
    content = await result.json()
    assert result.status == 200, content
    assert content['job_id'] == test_info['expected_jobs'][0]['id']

    await _assert_job(
        get_job,
        get_task,
        get_job_variables,
        web_context,
        test_info['expected_jobs'],
    )
    for mock_func in [
            get_myself,
            create_comment,
            get_ticket,
            get_comments,
            get_field_history,
            _execute_transaction,
    ]:
        if test_info['request_data']['env'] == 'production':
            assert mock_func.calls, mock_func.__name__
        else:
            assert not mock_func.calls, mock_func.__name__


@pytest.mark.parametrize(
    'test_file_name',
    [
        'deploy_unstable_no_aliases_diff_collision.json',
        'deploy_stable_no_aliases_rollback.json',
        'deploy_unstable_no_aliases.json',
        'deploy_unstable_aliases.json',
        'deploy_stable_no_aliases_close_status.json',
        'deploy_stable_aliases_close_status.json',
        pytest.param(
            'deploy_stable_aliases_reversed_close_status.json',
            marks=[
                pytest.mark.pgsql(
                    'clownductor',
                    files=[
                        'clear_all_related_services.sql',
                        'test_deploy_job_data_related_inversed.sql',
                    ],
                ),
            ],
        ),
        'deploy_stable_same_name_close_status.json',
        'deploy_unstable_sandbox_resources_no_aliases.json',
        'deploy_unstable_sandbox_resources_with_aliases.json',
        'deploy_stable_sandbox_resources_no_aliases_close_status.json',
        'deploy_stable_sandbox_resources_with_aliases_close_status.json',
    ],
)
@pytest.mark.pgsql('clownductor', files=['test_deploy_job_data.sql'])
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'new_get_approvers': True,
        'tc_deploy_changelog': True,
        'cancel_old_deploys': True,
        'named_target_deploy': True,
        'locks_for_deploy': True,
        'diff_validation': True,
        'update_hosts_cube_enabled': True,
        'enable_testing_deploy_message': True,
    },
    CLOWNDUCTOR_RELEASE_ST_COMMENT_SETTINGS={'verbose_enabled': True},
    CLOWNDUCTOR_DIFF_PARAMETERS=[
        {'subsystem_name': 'nanny', 'parameters': ['cpu']},
    ],
    CLOWNDUCTOR_DIFF_CONFIGURATION={
        'services': ['test_service', 'test_service_2', 'test_service_3'],
    },
    CLOWNDUCTOR_STARTREK_QUEUE_COMPONENTS={'TAXIREL': [42]},
    CLOWNDUCTOR_RELEASE_TICKET_PROPERTIES={'TAXIREL': 'deployed'},
)
@pytest.mark.features_off('startrek_close_approval')
@pytest.mark.features_on(
    'startrek_close_by_status', 'main_service_from_relation',
)
@pytest.mark.features_on('startrek_clown_component')
@pytest.mark.translations(clownductor=TRANSLATIONS)
async def test_teamcity_deploy_job_status_close(
        web_app_client,
        login_mockserver,
        nanny_mockserver,
        conductor_mockserver,
        staff_mockserver,
        test_file_name,
        get_job,
        web_context,
        get_job_variables,
        get_task,
        load_json,
        patch,
        patch_github_single_file,
        add_grant,
        mockserver,
):  # pylint: disable=R0913
    login_mockserver()
    conductor_mockserver()
    staff_mockserver()
    patch_github_single_file(
        'services/test_service/service.yaml', 'uservice.yaml',
    )
    await add_grant('mvpetrov', 'deploy_approve_programmer', project_id=1)
    await add_grant('bruno', 'deploy_approve_manager', project_id=1)

    test_info = load_json(test_file_name)
    created_drafts = {}

    ticket_test_cache = collections.defaultdict(
        lambda: {
            'ticket': {'status': {'key': 'open'}},
            'history': [
                {
                    'fields': [{'to': {'key': 'readyForRelease'}}],
                    'updatedBy': {'id': 'bruno'},
                    'updatedAt': '2100-06-28T15:27:26.361+0000',
                },
            ],
        },
    )

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text, *args, **kwargs):
        if 'There are already exists resolve diff jobs' in text:
            await _update_job(web_context, 1000, 'success')
            await _update_job(web_context, 1002, 'success')
        assert ticket

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def get_myself(*args, **kwargs):
        return {'login': 'robot-taxi-clown'}

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def _create_draft_mock(data, login, *args, **kwargs):
        draft = {'id': data['data']['branch_id'], **data}
        draft['tickets'] = ['TICKET-1', 'RUPRICING-4']
        created_drafts[draft['change_doc_id']] = draft
        await _add_resolve_diff_job(
            web_context, data['data']['branch_id'], 'success',
        )
        return draft

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def _get_drafts_mock(data, *args, **kwargs):
        change_doc_id = data['change_doc_ids'][0].replace('clownductor_', '')
        draft = created_drafts.get(change_doc_id)
        if draft:
            draft['status'] = 'succeeded'
            return [draft]
        return None

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def _get_draft_mock(draft_id, *args, **kwargs):
        change_doc_id = 'DIFF_RESOLVE_{}'.format(draft_id)
        draft = created_drafts.get(change_doc_id)
        if draft:
            draft['status'] = 'succeeded'
            return draft
        return None

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def get_ticket(ticket):
        nonlocal ticket_test_cache
        result = ticket_test_cache[ticket]['ticket']
        ticket_test_cache[ticket]['ticket'] = {'status': {'key': 'deployed'}}
        return result

    @patch('taxi.clients.startrack.StartrackAPIClient.execute_transition')
    async def _execute_transaction(
            ticket_key, transition, data, *args, **kwargs,
    ):
        assert transition == 'close'
        assert data == {'resolution': 'fixed'}
        return {}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def get_comments(*args, **kwargs):
        if 'short_id' in kwargs and kwargs['short_id'] is not None:
            return []
        service_id = 1
        image = test_info['request_data'].get('docker_image')
        if (
                test_file_name
                == 'deploy_stable_aliases_reversed_close_status.json'
        ):
            service_id = 3
        if test_file_name == 'deploy_unstable_no_aliases_diff_collision.json':
            service_id = 9
        if test_file_name == 'deploy_stable_same_name_close_status.json':
            service_id = 4
        if test_file_name == 'deploy_stable_no_aliases_rollback.json':
            service_id = 8
        if test_info['request_data'].get('aliases'):
            inited_vars = test_info['expected_jobs'][0]['inited_variables']
            all_names = itertools.chain(
                [inited_vars['name']],
                [item['nanny_name'] for item in inited_vars['aliases']],
            )
            parts = [
                'This is release for several services:',
                *[f'* **{name}**' for name in all_names],
                '',
                'Approve messages will trigger deploy for all services above.',
                '',
                BORDER_COMMENT.render(service_id=service_id, image=image),
            ]
            comment = '\n'.join(parts)
        else:
            comment = BORDER_COMMENT.render(service_id=service_id, image=image)
        return [
            {
                'self': 'url_to_comment',
                'id': 1,
                'createdBy': {'id': 'robot-taxi-clown'},
                'createdAt': '2100-06-28T15:27:25.358+0000',
                'updatedAt': '2100-06-28T15:27:25.358+0000',
                'text': comment,
            },
            {
                'self': 'url_to_comment',
                'id': 2,
                'createdBy': {'id': 'mvpetrov'},
                'createdAt': '2100-06-28T15:27:25.359+0000',
                'updatedAt': '2100-06-28T15:27:25.359+0000',
                'text': 'OK for diff_resolve:4',
            },
            {
                'self': 'url_to_comment',
                'id': 3,
                'createdBy': {'id': 'mvpetrov'},
                'createdAt': '2100-06-28T15:27:25.361+0000',
                'updatedAt': '2100-06-28T15:27:25.361+0000',
                'text': 'PRESTABLE OK for release:4',
            },
            {
                'self': 'url_to_comment',
                'id': 4,
                'createdBy': {'id': 'mvpetrov'},
                'createdAt': '2100-06-28T15:27:27.361+0000',
                'updatedAt': '2100-06-28T15:27:27.361+0000',
                'text': 'OK for release:4',
            },
            {
                'self': 'url_to_comment',
                'id': 5,
                'createdBy': {'id': 'mvpetrov'},
                'createdAt': '2100-06-28T15:27:27.361+0000',
                'updatedAt': '2100-06-28T15:27:27.361+0000',
                'text': 'CLOSE TICKET for release:4',
            },
        ]

    @patch('taxi.clients.startrack.StartrackAPIClient.get_field_history')
    async def get_field_history(ticket, *args, **kwargs):
        nonlocal ticket_test_cache
        result = ticket_test_cache[ticket]['history']
        ticket_test_cache[ticket]['history'] = [
            {
                'fields': [{'to': {'key': 'deployed'}}],
                'updatedBy': {'id': 'bruno'},
                'updatedAt': '2101-06-28T15:27:26.361+0000',
            },
        ]
        return result

    @mockserver.json_handler('/client-abc/v4/duty/schedules-cursor/')
    async def _schedule_cursor_mock(request):
        return {'next': None, 'previous': None, 'results': []}

    result = await web_app_client.post(
        '/api/teamcity_deploy',
        json=test_info['request_data'],
        headers={'X-YaTaxi-Api-Key': 'valid_teamcity_token'},
    )
    content = await result.json()
    assert result.status == 200, content
    assert content['job_id'] == test_info['expected_jobs'][0]['id']

    await _assert_job(
        get_job,
        get_task,
        get_job_variables,
        web_context,
        test_info['expected_jobs'],
    )
    for mock_func in [get_ticket, get_field_history]:
        if test_info['request_data']['env'] == 'production':
            assert mock_func.calls, mock_func.__name__
        else:
            assert not mock_func.calls, mock_func.__name__

    for mock_func in [get_myself, create_comment, get_comments]:
        if (
                test_info['request_data']['env'] == 'production'
                or test_info['request_data']['service_name']
                == 'test_service_9'
        ):
            assert mock_func.calls, mock_func.__name__
        else:
            assert not mock_func.calls, mock_func.__name__

    if test_info['request_data']['env'] == 'production' and not test_info[
            'expected_jobs'
    ][0].get('inited_variables', {}).get('is_rollback'):
        assert _execute_transaction.calls
    else:
        assert not _execute_transaction.calls


# pylint: disable=protected-access
@pytest.mark.usefixtures('mock_internal_tp')
@pytest.mark.features_on('cancel_old_deploys')
@pytest.mark.features_on('locks_for_deploy')
@pytest.mark.features_on('startrek_close_approval')
@pytest.mark.features_off('startrek_close_by_status')
@pytest.mark.dontfreeze
@pytest.mark.parametrize(
    'test_file_name',
    [
        'deploy_unstable_no_aliases.json',
        'deploy_unstable_aliases.json',
        'deploy_stable_no_aliases.json',
        'deploy_stable_aliases.json',
        pytest.param(
            'deploy_stable_aliases_reversed.json',
            marks=[
                pytest.mark.pgsql(
                    'clownductor',
                    files=[
                        'clear_all_related_services.sql',
                        'test_deploy_job_data_related_inversed.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            'deploy_unstable_sandbox_as_alias_and_code_as_main.json',
            marks=[
                pytest.mark.pgsql(
                    'clownductor', files=['clear_all_related_services.sql'],
                ),
            ],
        ),
        'deploy_unstable_code_as_main_and_sandbox_as_alias.json',
    ],
)
@pytest.mark.pgsql(
    'clownductor', files=['test_deploy_job_data.sql', 'clear_all_jobs.sql'],
)
async def test_deploy_jobs_locking(
        run_job_with_meta,
        get_job_from_internal,
        monkeypatch,
        load_json,
        patch,
        conductor_mockserver,
        nanny_mockserver,
        web_app_client,
        patch_method,
        check_lock,
        patch_github_single_file,
        test_file_name,
):
    patch_github_single_file(
        'services/test_service/service.yaml', 'uservice.yaml',
    )
    # common mocks

    def _wait_for(*args, **kwargs):
        return 1

    monkeypatch.setattr(
        'clownductor.internal.tasks.cubes.cubes_meta.'
        'MetaCubeWaitForJobsCommon._wait_for',
        _wait_for,
    )
    monkeypatch.setattr(
        'clownductor.internal.tasks.cubes.cubes_internal_locks.'
        'InternalGetLock._wait_for',
        _wait_for,
    )
    monkeypatch.setattr(
        'clownductor.internal.tasks.cubes.cubes_internal_locks.'
        'InternalBatchGetLock._wait_for',
        _wait_for,
    )

    test_info = load_json(test_file_name)

    # mocks for stable
    conductor_mockserver()

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def _get_myself(*args, **kwargs):
        return {'login': 'robot-taxi-clown'}

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _create_comment(*args, **kwargs):
        pass

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(*args, **kwargs):
        return {}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_field_history')
    async def _get_field_history(*args, **kwargs):
        return [
            {
                'fields': [{'to': {'key': 'readyForRelease'}}],
                'updatedBy': {'id': 'bruno'},
                'updatedAt': '2100-06-28T15:27:26.361+0000',
            },
        ]

    @patch_method(
        'clownductor.internal.tasks.cubes.cubes_approve.'
        'ApproveCubeLiteWaitForDevelopersApprove._update',
    )
    async def _wait_for_developer_ok_update(self, input_data):
        self._data['payload'] = {'approved': input_data['release_id']}
        self.succeed()

    @patch_method(
        'clownductor.internal.tasks.cubes.cubes_approve.'
        'ApproveCubeLiteWaitForSingleApprove._update',
    )
    async def _wait_for_single_ok_update(self, _input_data):
        self._data['payload'] = {'approved': _input_data['release_id']}
        self.succeed()

    @patch_method(
        'clownductor.internal.tasks.cubes.cubes_approve.'
        'ApproveCubeLiteWaitForManagersApprove._update',
    )
    async def _wait_for_manager_ok_update(self, input_data):
        self._data['payload'] = {'approved': input_data['release_id']}
        self.succeed()

    @patch_method(
        'clownductor.internal.tasks.cubes.cubes_approve.'
        'ApproveCubeLiteEnsureComment._update',
    )
    async def _ensure_comment_update(self, input_data):
        self.succeed()

    @patch_method(
        'clownductor.internal.tasks.cubes.cubes_approve.'
        'ApproveCubeOptionalLiteEnsureComment._update',
    )
    async def _ensure_comment_lite_update(self, input_data):
        self.succeed()

    @patch_method(
        'clownductor.internal.tasks.cubes.cubes_approve.'
        'ApproveCubeWaitForClosureApproval._update',
    )
    async def _wait_for_ticket_close_ok_update(self, input_data):
        self._data['payload'] = {'skip': False}
        self.succeed()

    @patch_method(
        'clownductor.internal.tasks.cubes.cubes_startrek.'
        'StartrekCubeCloseTicket._update',
    )
    async def _close_ticket(self, input_data):
        self.succeed()

    # call deploy twice
    response = await web_app_client.post(
        '/api/teamcity_deploy',
        json=test_info['first_request_data'],
        headers={
            'X-YaTaxi-Api-Key': 'valid_teamcity_token',
            'X-YaRequestId': '1',
        },
    )
    assert response.status == 200, await response.text()

    first_job_id = (await response.json())['job_id']

    response = await web_app_client.post(
        '/api/teamcity_deploy',
        json=test_info['second_request_data'],
        headers={
            'X-YaTaxi-Api-Key': 'valid_teamcity_token',
            'X-YaRequestId': '2',
        },
    )
    assert response.status == 200, await response.text()
    second_job_id = (await response.json())['job_id']

    await check_lock(first_job_id, exists=True)

    first_job = await get_job_from_internal(first_job_id)
    second_job = await get_job_from_internal(second_job_id)

    async def _check_second_job(task):
        if task.cube.name == 'InternalBatchReleaseLock':
            return
        second_job_task, _ = await second_job.step()
        if task.cube.name == 'InternalCubeCheckAndNotifyDeployments':
            second_job_task, _ = await second_job.step()
        assert not second_job_task.status.is_success

    await run_job_with_meta(
        first_job,
        task_done_callback=_check_second_job,
        continue_on_sleep=False,
    )

    assert first_job.status.value == 'success'
    await check_lock(first_job_id, exists=False)

    await run_job_with_meta(second_job, continue_on_sleep=False)
    await check_lock(second_job_id, exists=False)


@pytest.mark.features_on('cancel_old_deploys', 'locks_for_deploy')
@pytest.mark.dontfreeze
@pytest.mark.parametrize(
    'test_file_name, new_job_id', [('deploy_twice_while_locked.json', 3)],
)
@pytest.mark.pgsql('clownductor', files=['test_deploy_sandbox_block.sql'])
async def test_deploy_old_jobs_canceling(
        get_job,
        load_json,
        patch,
        conductor_mockserver,
        nanny_mockserver,
        web_app_client,
        patch_github_single_file,
        test_file_name,
        new_job_id,
):
    patch_github_single_file(
        'services/test_service/service.yaml', 'uservice.yaml',
    )
    test_info = load_json(test_file_name)
    conductor_mockserver()

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _create_comment(*args, **kwargs):
        pass

    response = await web_app_client.post(
        '/api/teamcity_deploy',
        json=test_info['request_data'],
        headers={
            'X-YaTaxi-Api-Key': 'valid_teamcity_token',
            'X-YaRequestId': '1',
        },
    )
    assert response.status == 200

    job_id = (await response.json())['job_id']
    assert job_id == new_job_id

    job = (await get_job(job_id))[0]
    assert (
        test_info['request_data']['docker_image']
        == job['job_variables']['image']
    )

    job_sandbox = (await get_job(1))[0]
    assert job_sandbox['job']['status'] == 'in_progress'

    job_code = (await get_job(2))[0]
    assert job_code['job']['status'] == 'canceled'


# pylint: disable=protected-access
async def _assert_job(
        get_job, get_task, get_job_variables, web_context, expected_jobs,
):
    for job_info in expected_jobs:
        job_id = job_info['id']
        deploy_job = (await get_job(job_id))[0]
        assert deploy_job['job']['name'] == job_info['name']
        expected_tasks = job_info['stages']
        assert [x['name'] for x in deploy_job['tasks']] == [
            x['name'] for x in expected_tasks
        ], f'unexpected tasks sequence for job {job_id}'
        variables = await get_job_variables(job_id)
        variables = json.loads(variables['variables'])
        for field in job_info.get('ignore_variables', []):
            assert variables[field]
            del variables[field]
        assert (
            variables == job_info['inited_variables']
        ), f'inited variables are different for job {job_id}'
        for i, task in enumerate(deploy_job['tasks']):
            expected_task = expected_tasks[i]
            assert task['name'] == expected_task['name']
            async with postgres.primary_connect(web_context) as conn:
                db_conn = processor.DbConnection(
                    conn, web_context.postgres_queries,
                )
                await processor._try_update_task(
                    web_context, db_conn, task['id'],
                )
                updated_task = await get_task(job_id, task['id'])
                assert (
                    updated_task['status'] == 'success'
                ), f'{i}. {task["name"]} {task.get("error_message")}'
                variables = await get_job_variables(job_id)
                variables = json.loads(variables['variables'])
                appended_variables = {
                    key: variables[key]
                    for key in json.loads(task['output_mapping'])
                }
                for ignore_field in expected_task.get('ignore_variables', []):
                    appended_variables.pop(ignore_field)
                assert (
                    appended_variables == expected_task['appended_variables']
                ), f'{i}. {task["name"]}'
            if 'meta' in expected_task:
                meta = expected_task['meta']
                await _assert_job(
                    get_job, get_task, get_job_variables, web_context, meta,
                )

        async with postgres.primary_connect(web_context) as conn:
            db_conn = processor.DbConnection(
                conn, web_context.postgres_queries,
            )
            await processor._try_update_job(web_context, db_conn, job_id)
            job = (await get_job(job_id))[0]
            assert job['job']['status'] == 'success'


async def _update_job(web_context, job_id, status):
    async with postgres.primary_connect(web_context) as conn:
        await conn.fetch(
            """
            update task_manager.jobs
            set status = $2, idempotency_token = null
            where id = $1;
        """,
            job_id,
            status,
        )


async def _add_resolve_diff_job(web_context, branch_id, status):
    service_id = 2
    if branch_id == 6:
        service_id = 3
    async with postgres.primary_connect(web_context) as conn:
        await conn.fetch(
            """
            insert into task_manager.jobs (
                service_id,
                branch_id,
                name,
                initiator,
                status
            )
            values (
                $1, $2, 'ResolveServiceDiff', 'karachevda', $3
            )
            """,
            service_id,
            branch_id,
            status,
        )
