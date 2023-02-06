import pytest


EXISTING_CGROUPS = {'lxc_service'}
EXISTING_NGROUPS = {'nanny-service'}


@pytest.mark.config(USE_APPROVALS=True)
@pytest.mark.parametrize(
    'script_url, saved_script, owner_service_name',
    [
        (
            (
                'https://github.yandex-team.ru/taxi/tools-py3/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'lxc_service/do-stuff.py'
            ),
            {
                'local_relative_path': 'lxc_service/do-stuff.py',
                'project': 'lxc_service',
                'execute_type': 'python',
            },
            'nanny-service',
        ),
    ],
)
async def test_create_for_alias_n_get_from_owner(
        patch,
        scripts_client,
        mock_executor_schemas,
        script_url,
        saved_script,
        owner_service_name,
):
    mock_executor_schemas(
        **{
            'nanny-service': {
                'service_settings': {'aliases': ['lxc_service']},
            },
        },
    )
    _drafts = [
        {
            'id': 1,
            'status': 'applying',
            'change_doc_id': 'scripts_waits-for-execute',
            'created_by': 'testsuite',
            'approvals': [],
            'run_manually': False,
        },
    ]

    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def _check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def _create_draft_mock(*args, **kwargs):
        pass

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def _get_draft_mock(*args, **kwargs):
        return _drafts[0]

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def _get_drafts_mock(*args, **kwargs):
        return _drafts

    @patch('scripts.lib.clients.conductor.Client.check_cgroup_exists')
    async def _check_cgroup_exists(group, log_extra=None):
        return group in EXISTING_CGROUPS

    @patch('scripts.lib.clients.clownductor.Client.check_ngroup_exists')
    async def _check_ngroup_exists(group, log_extra=None):
        return group in EXISTING_NGROUPS

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': script_url,
            'ticket': 'TAXIBACKEND-1',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '123',
        },
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 200, await response.text()
    result = await response.json()
    _drafts[0]['change_doc_id'] = f'scripts_{result["id"]}'

    response = await scripts_client.get(
        f'/{result["id"]}/', headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 200, await response.text()
    script = await response.json()
    _compare(script, saved_script)
    response = await scripts_client.post(
        '/scripts/next-script/', json={'service_name': owner_service_name},
    )
    assert response.status == 200, await response.text()
    script = await response.json()
    _compare(script, saved_script)


def _compare(dict_1: dict, dict_2: dict):
    def _extract(data: dict) -> dict:
        return {key: val for key, val in data.items() if key in common_keys}

    common_keys = dict_1.keys() & dict_2.keys()
    assert _extract(dict_1) == _extract(dict_2)
