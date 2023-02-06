import dataclasses
from typing import List
from typing import Sequence

import pytest

import arc_checkout
import download_deb_from_sandbox
from taxi_buildagent.tools.vcs import arc_repo
from tests.utils import pytest_wraps
from tests.utils.examples import arcadia


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    environment: str = 'production'
    service_yaml: str = 'service.yaml'
    sidecar_yaml: str = 'sidecar.yaml'
    recipe: str = 'recipe.ext'
    tc_set_parameters_calls: Sequence = ()
    tc_report_problems_calls: Sequence = ()
    get_resource_calls: Sequence = ()
    ya_calls_args: Sequence[List[str]] = (
        ['ya', 'download', 'sbr:123', '--untar'],
    )


@pytest.mark.arc
@pytest_wraps.parametrize(
    [
        Params(pytest_id='production_case'),
        Params(
            pytest_id='prestable_case',
            service_yaml='service_prestable.yaml',
            get_resource_calls=[
                {
                    'args': (
                        'get',
                        'https://sandbox.yandex-team.ru/api/v1.0/resource',
                    ),
                    'kwargs': {
                        'params': {
                            'attrs': (
                                '{"service_name": "exp3-matcher", '
                                '"resource_name": "deb", "environment": '
                                '"production"}'
                            ),
                            'limit': '1',
                        },
                    },
                },
            ],
        ),
        Params(
            pytest_id='testing_case',
            environment='testing',
            get_resource_calls=[
                {
                    'args': (
                        'get',
                        'https://sandbox.yandex-team.ru/api/v1.0/resource',
                    ),
                    'kwargs': {
                        'params': {
                            'attrs': (
                                '{"service_name": "exp3-matcher", '
                                '"resource_name": "deb", "environment": '
                                '"testing"}'
                            ),
                            'limit': '1',
                        },
                    },
                },
            ],
        ),
    ],
)
def test_download_deb_from_sandbox(
        params: Params,
        commands_mock,
        monkeypatch,
        patch_requests,
        tmp_path,
        load,
        startrek,
        teamcity_set_parameters,
        teamcity_report_problems,
        arcadia_builder,
):
    arcadia_path = tmp_path / 'arcadia'
    arcadia_path.mkdir()
    monkeypatch.chdir(arcadia_path)

    service_name = 'basic-project'
    project_path = arcadia_path / 'projects' / service_name

    startrek.ticket_status = 'testing'
    monkeypatch.setenv('ARCADIA_TOKEN', 'cool-token')

    @patch_requests(download_deb_from_sandbox.API_URL)
    def get_resource(*args, **kwargs):
        return patch_requests.response(
            status_code=200, json={'items': [{'id': '123'}]},
        )

    @commands_mock('ya')
    def ya_mock(args, **kwargs):
        return ''

    with arcadia_builder:
        arcadia.init_arcadia_basic_project(arcadia_builder)
        sidecar_path = '../../taxi/uservices/services/exp3-matcher'
        arcadia.update_arcadia_project(
            arcadia_builder,
            {
                'recipes/deb/recipe.ext': load(params.recipe),
                'service.yaml': load(params.service_yaml),
                'deb/.keep': 'keep deb dir',
                f'{sidecar_path}/service.yaml': load(params.sidecar_yaml),
                f'{sidecar_path}/recipes/deb/recipe.ext': load(params.recipe),
            },
            'add service and sidecar files',
        )

    arc_checkout.main([str(arcadia_path), '--branch', 'trunk'])
    assert teamcity_report_problems.calls == []

    repo = arc_repo.Repo(arcadia_path, from_root=True)

    master_branch = repo.stable_branch_prefix + 'projects/basic-project'
    repo.checkout_new_branch(master_branch, repo.active_branch)
    repo.arc.push('--force', '--set-upstream', master_branch)

    # FIXME(TAXITOOLS-3888): shouldn't be a special case for monoprojects
    monkeypatch.setenv('MASTER_BRANCH', master_branch)

    monkeypatch.chdir(project_path)
    repo.checkout(master_branch)
    download_deb_from_sandbox.main(['--environment', params.environment])

    assert [call['args'] for call in ya_mock.calls] == list(
        params.ya_calls_args,
    )
    assert teamcity_set_parameters.calls == list(
        params.tc_set_parameters_calls,
    )
    assert teamcity_report_problems.calls == list(
        params.tc_report_problems_calls,
    )
    assert get_resource.calls == list(params.get_resource_calls)
