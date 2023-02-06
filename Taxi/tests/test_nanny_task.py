from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Set

import pytest
from taxi_linters import taxi_jsonfmt as json
from taxi_linters import taxi_yamlfmt as yaml

import nanny_task
from tests.utils import repository
from tests.utils.examples import uservices


class Params(NamedTuple):
    resources: List[str]
    commits: List[repository.Commit] = []
    main_service: Optional[str] = None
    error: Optional[str] = None
    services_to_update: Set[str] = set()
    resources_to_update: List[Dict[str, Any]] = [
        dict(
            resource_type='RES',
            resource_id='123',
            task_type='TYPE',
            task_id='123456789',
            local_path='path',
        ),
    ]
    environments: List[str] = ['production', 'testing']
    branch_name: Optional[str] = None


def commit_resource(service, content):
    files = [f'generated/services/{service}/sandbox/resources.json']
    files_content = json.dumps(content)
    return repository.Commit(service, files, files_content=files_content)


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                resources=['RES'],
                commits=[
                    repository.Commit(
                        'docker', files=['services/pilorama/Dockerfile'],
                    ),
                    commit_resource(
                        'driver-authorizer',
                        [{'type': 'RES', 'local-path': 'path'}],
                    ),
                    commit_resource(
                        'pilorama',
                        [
                            {'type': 'RES', 'local-path': 'path'},
                            {'type': 'RES1', 'local-path': 'path1'},
                        ],
                    ),
                ],
                services_to_update={'pilorama', 'driver-authorizer'},
            ),
            id='simple_case',
        ),
        pytest.param(
            Params(
                resources=['RES'],
                commits=[
                    commit_resource(
                        'driver-authorizer',
                        [{'type': 'RES', 'local-path': 'path'}],
                    ),
                ],
                services_to_update={'driver-authorizer'},
                branch_name='tank',
            ),
            id='send_branch_to_nanny',
        ),
        pytest.param(
            Params(
                resources=['RES'],
                commits=[
                    repository.Commit(
                        'docker', files=['services/pilorama/Dockerfile'],
                    ),
                    commit_resource(
                        'driver-authorizer',
                        [
                            {'type': 'RES', 'local-path': 'path'},
                            {'type': 'RES1', 'local-path': 'path1'},
                        ],
                    ),
                    commit_resource(
                        'driver-authorizer2',
                        [{'type': 'RES', 'local-path': 'path'}],
                    ),
                    commit_resource(
                        'pilorama', [{'type': 'RES1', 'local-path': 'path1'}],
                    ),
                ],
                services_to_update={'driver-authorizer'},
            ),
            id='choose_only_rtc_services_with_specified_resource',
        ),
        pytest.param(
            Params(
                resources=['RES'],
                commits=[
                    commit_resource(
                        'driver-authorizer',
                        [{'type': 'RES', 'local-path': 'path'}],
                    ),
                ],
                services_to_update={'driver-authorizer'},
                environments=['testing', 'prestable'],
            ),
            id='several_environments',
        ),
        pytest.param(
            Params(
                resources=['RES', 'RES1', 'RES2'],
                commits=[
                    repository.Commit(
                        'docker', files=['services/pilorama/Dockerfile'],
                    ),
                    commit_resource(
                        'driver-authorizer',
                        [
                            {'type': 'RES', 'local-path': 'path'},
                            {'type': 'RES1', 'local-path': 'path1'},
                        ],
                    ),
                    commit_resource(
                        'driver-authorizer2',
                        [{'type': 'RES2', 'local-path': 'path2'}],
                    ),
                    commit_resource(
                        'pilorama', [{'type': 'RES', 'local-path': 'path'}],
                    ),
                ],
                services_to_update={'driver-authorizer', 'pilorama'},
                resources_to_update=[
                    dict(
                        resource_type='RES',
                        resource_id='123',
                        task_type='TYPE',
                        task_id='123456789',
                        local_path='path',
                    ),
                    dict(
                        resource_type='RES1',
                        resource_id='223',
                        task_type='TYPE',
                        task_id='123456789',
                        local_path='path1',
                    ),
                    dict(
                        resource_type='RES2',
                        resource_id='323',
                        task_type='TYPE',
                        task_id='123456789',
                        local_path='path2',
                    ),
                ],
            ),
            id='choose_several_resources',
        ),
        pytest.param(
            Params(
                resources=['RES'],
                commits=[
                    repository.Commit(
                        'docker',
                        files=[
                            'services/pilorama/Dockerfile',
                            'services/pilorama/Dockerfile.alias_pilorama',
                            'services/driver-authorizer2/Dockerfile.alias2',
                            'services/driver-authorizer3/Dockerfile.alias3',
                        ],
                    ),
                    commit_resource(
                        'driver-authorizer',
                        [{'type': 'RES', 'local-path': 'path'}],
                    ),
                    commit_resource(
                        'driver-authorizer2',
                        [{'type': 'RES', 'local-path': 'path'}],
                    ),
                    commit_resource(
                        'driver-authorizer3',
                        [{'type': 'RES', 'local-path': 'path'}],
                    ),
                    commit_resource(
                        'pilorama',
                        [
                            {'type': 'RES', 'local-path': 'path'},
                            {'type': 'RES1', 'local-path': 'path1'},
                        ],
                    ),
                    repository.Commit(
                        'disable-authorizer2',
                        files=['services/driver-authorizer2/service.yaml'],
                        files_content=yaml.dump(
                            {'teamcity': {'clownductor-disabled': True}},
                        ),
                    ),
                    repository.Commit(
                        'alias_authorizer3',
                        files=['services/driver-authorizer3/service.yaml'],
                        files_content=yaml.dump(
                            {'clownductor': {'aliases': ['alias_yaml3']}},
                        ),
                    ),
                ],
                main_service='pilorama',
                services_to_update={'alias3', 'pilorama', 'driver-authorizer'},
            ),
            id='specify_main_service_and_get_aliases',
        ),
        pytest.param(
            Params(
                resources=['RES', 'RES1'],
                commits=[
                    commit_resource(
                        'driver-authorizer',
                        [
                            {'type': 'RES', 'local-path': 'path'},
                            {'type': 'RES1', 'local-path': 'path2'},
                        ],
                    ),
                    commit_resource(
                        'driver-authorizer2',
                        [{'type': 'RES1', 'local-path': 'path1'}],
                    ),
                ],
                error=(
                    'Different local-path for resource \'RES1\' found:\n'
                    'Services \'driver-authorizer2\' have \'path1\' '
                    'as local-path\nServices \'driver-authorizer\' have '
                    '\'path2\' as local-path\n'
                ),
            ),
            id='error_duplicated_local_path',
        ),
        pytest.param(
            Params(
                resources=['RES', 'RES1'],
                commits=[
                    repository.Commit(
                        'docker',
                        files=[
                            'services/pilorama/Dockerfile',
                            'services/driver-authorizer2/Dockerfile',
                        ],
                    ),
                    commit_resource(
                        'driver-authorizer2',
                        [
                            {'type': 'RES2', 'local-path': 'path2'},
                            {'type': 'RES3', 'local-path': 'path3'},
                        ],
                    ),
                    commit_resource(
                        'driver-authorizer3',
                        [
                            {'type': 'RES', 'local-path': 'path'},
                            {'type': 'RES1', 'local-path': 'path1'},
                        ],
                    ),
                ],
            ),
            id='choose_nothing',
        ),
    ],
)
def test_create_ticket(
        params,
        monkeypatch,
        sandbox,
        startrek,
        patch_requests,
        tmpdir,
        teamcity_report_problems,
):
    repo = uservices.init(tmpdir)
    repository.apply_commits(repo, params.commits)

    monkeypatch.setenv('CLOWNDUCTOR_TOKEN', 'token')
    monkeypatch.setenv('RELEASE_TICKET', 'ticket/REL-123')
    for res in params.resources_to_update:
        sandbox.append_resource(
            type_=res['resource_type'],
            id_=res['resource_id'],
            task_id=123456789,
        )
    for type_, id_ in ('RES', 124), ('RES1', 213):
        sandbox.append_resource(type_=type_, id_=id_, task_id=123456789)
    sandbox.patch_all()

    @patch_requests(nanny_task.CLOWNDUCTOR_URL)
    def _update_resources(*args, **kwargs):
        assert (
            sorted(
                kwargs['json']['sandbox_resources'],
                key=lambda k: k['resource_type'],
            )
            == params.resources_to_update
        )
        updated_services = {kwargs['json']['service_name']} | set(
            kwargs['json']['aliases'],
        )
        if params.main_service:
            assert kwargs['json']['service_name'] == params.main_service
        if params.branch_name:
            assert kwargs['json']['branch_name'] == params.branch_name
        assert params.services_to_update == updated_services
        return patch_requests.response(json={})

    args = ['-t', repo.working_dir, '-r', *params.resources]
    if params.main_service:
        args += ['-m', params.main_service]
    if params.environments:
        args += ['-e', *params.environments]
    if params.branch_name:
        args += ['-b', params.branch_name]
    nanny_task.main(args)

    if params.error:
        assert teamcity_report_problems.calls[0]['description'] == params.error
        return

    create_comment_calls = 0
    if params.services_to_update and 'production' in params.environments:
        create_comment_calls = len(params.environments)
    assert len(startrek.create_comment.calls) == create_comment_calls
    assert len(params.resources) == len(sandbox.resource.calls)
    assert len({res['task_id'] for res in params.resources_to_update}) == len(
        sandbox.task.calls,
    )
