import dataclasses
import pathlib
from typing import List
from typing import Sequence

import pytest

import arc_checkout
from taxi_buildagent.tools.vcs import arc_repo
from tests.utils import pytest_wraps
from tests.utils.examples import arcadia
import upload_sandbox_resources


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    environment: str = 'production'
    service_yaml: str = 'service.yaml'
    recipe: str = 'recipe.ext'
    exp_recipe: str = 'exp_recipe.ext'
    branch_exists: bool = False
    ya_calls_args: Sequence[List[str]] = (
        [
            'ya',
            'upload',
            'sandbox-resources/deb',
            '--owner',
            'sanyash',
            '--ttl',
            'inf',
            '--type',
            'OTHER_RESOURCE',
            '--json-output',
            '--tar',
            '--root',
            'sandbox-resources/deb',
            '--attr',
            'version=0.0.1',
            '--attr',
            'service_name=basic-project',
            '--attr',
            'resource_name=deb',
            '--attr',
            'environment=production',
        ],
        [
            'ya',
            'pr',
            'create',
            '--no-interactive',
            '--wait',
            '--json',
            '--push',
            '--publish',
            '--merge',
        ],
        [
            'ya',
            'pr',
            'edit',
            '--id',
            '12345',
            '--summary',
            'feat basic-project: up recipes to 666',
            '--description',
            'Relates: TAXIREL-1',
        ],
    )
    tc_set_parameters_calls: Sequence = ()
    tc_report_problems_calls: Sequence = ()
    teamcity_messages: Sequence[dict] = (
        {
            'buildStatus': (
                'text=\'Sandbox resources:|n'
                'https://sandbox.yandex-team.ru/resource/678\''
            ),
        },
    )
    st_create_comment_calls: Sequence[dict] = (
        {
            'json': {
                'text': (
                    'Созданные в процессе релиза сендбокс-ресурсы:\n'
                    'https://sandbox.yandex-team.ru/resource/678\n'
                    'Пулл-реквест на обновление id сендбокс-ресурсов: '
                    'https://a.yandex-team.ru/review/12345/details.'
                ),
            },
        },
    )


@pytest.mark.arc
@pytest_wraps.parametrize(
    [
        Params(pytest_id='production_case'),
        Params(
            pytest_id='production_case_branch_exists',
            branch_exists=True,
            ya_calls_args=[
                [
                    'ya',
                    'upload',
                    'sandbox-resources/deb',
                    '--owner',
                    'sanyash',
                    '--ttl',
                    'inf',
                    '--type',
                    'OTHER_RESOURCE',
                    '--json-output',
                    '--tar',
                    '--root',
                    'sandbox-resources/deb',
                    '--attr',
                    'version=0.0.1',
                    '--attr',
                    'service_name=basic-project',
                    '--attr',
                    'resource_name=deb',
                    '--attr',
                    'environment=production',
                ],
            ],
            st_create_comment_calls=[],
        ),
        Params(
            pytest_id='testing_case',
            environment='testing',
            ya_calls_args=[
                [
                    'ya',
                    'upload',
                    'sandbox-resources/deb',
                    '--owner',
                    'sanyash',
                    '--ttl',
                    'inf',
                    '--type',
                    'OTHER_RESOURCE',
                    '--json-output',
                    '--tar',
                    '--root',
                    'sandbox-resources/deb',
                    '--attr',
                    'version=0.0.1',
                    '--attr',
                    'service_name=basic-project',
                    '--attr',
                    'resource_name=deb',
                    '--attr',
                    'environment=testing',
                ],
            ],
            st_create_comment_calls=[],
        ),
    ],
)
def test_upload_sandbox_resources(
        params: Params,
        commands_mock,
        monkeypatch,
        tmp_path,
        load,
        startrek,
        teamcity_set_parameters,
        teamcity_report_problems,
        teamcity_messages,
        arcadia_builder,
):
    arcadia_path = tmp_path / 'arcadia'
    arcadia_path.mkdir()
    monkeypatch.chdir(arcadia_path)

    service_name = 'basic-project'
    project_path = arcadia_path / 'projects' / service_name
    service_path = project_path  # mono
    changelog_path = service_path / 'debian' / 'changelog'
    recipe_path = service_path / 'recipes' / 'deb' / 'recipe.ext'

    startrek.ticket_status = 'testing'
    build_number = '666'
    monkeypatch.setenv('ARCADIA_TOKEN', 'cool-token')
    monkeypatch.setenv('BUILD_NUMBER', build_number)
    monkeypatch.setenv('RELEASE_TICKET', 'https://st.yandex-team.ru/TAXIREL-1')

    auto_branch = f'auto/up-{service_name}-recipes-{build_number}'

    @commands_mock('ya')
    def ya_mock(args, **kwargs):
        command = args[1]
        if command == 'pr':
            pr_command = args[2]
            if pr_command == 'create':
                return '{"id":12345}'
        elif command == 'upload':
            return '{"resource_id":678}'
        return ''

    with arcadia_builder:
        arcadia.init_arcadia_basic_project(arcadia_builder)
        arcadia.update_arcadia_project(
            arcadia_builder,
            {
                'recipes/deb/recipe.ext': load(params.recipe),
                'service.yaml': load(params.service_yaml),
                'path/to/file': 'file content',
            },
            'add recipe and service.yaml',
        )

    arc_checkout.main([str(arcadia_path), '--branch', 'trunk'])
    assert teamcity_report_problems.calls == []

    repo = arc_repo.Repo(arcadia_path, from_root=True)

    master_branch = repo.stable_branch_prefix + 'projects/basic-project'
    repo.checkout_new_branch(master_branch, repo.active_branch)
    changelog_path.parent.mkdir(exist_ok=True, parents=True)
    changelog_path.write_text(load('changelog'))
    repo.add_paths_to_index([str(changelog_path)])
    repo.commit('release 0.0.1')
    repo.arc.push('--force', '--set-upstream', master_branch)

    if params.branch_exists:
        existing_branch = repo.stable_branch_prefix + auto_branch
        repo.checkout_new_branch(existing_branch, repo.active_branch)
        repo.arc.push('--force', '--set-upstream', existing_branch)

    # FIXME(TAXITOOLS-3888): shouldn't be a special case for monoprojects
    monkeypatch.setenv('MASTER_BRANCH', master_branch)

    monkeypatch.chdir(project_path)
    repo.checkout(master_branch)
    upload_sandbox_resources.main(
        [
            '--service-name',
            service_name,
            '--environment',
            params.environment,
            '--sandbox-resources-dir',
            'sandbox-resources',
            '--build-dir',
            'build-dir',
        ],
    )

    assert [call['args'] for call in ya_mock.calls] == list(
        params.ya_calls_args,
    )
    assert teamcity_set_parameters.calls == list(
        params.tc_set_parameters_calls,
    )
    assert teamcity_report_problems.calls == list(
        params.tc_report_problems_calls,
    )
    assert params.teamcity_messages[0] == {
        call['message_name']: call['value'] for call in teamcity_messages.calls
    }
    assert startrek.create_comment.calls == list(
        params.st_create_comment_calls,
    )
    assert (
        pathlib.Path('sandbox-resources', 'deb', 'file').read_text()
        == 'file content'
    )

    if params.environment == 'production':
        repo.checkout(auto_branch)
        assert recipe_path.read_text() == load(params.exp_recipe)
