import dataclasses
from typing import Sequence

import pytest

import arc_checkout
import send_teamcity_build_info
from taxi_buildagent.tools.vcs import arc_repo
from tests.utils import pytest_wraps
from tests.utils.examples import arcadia


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    changelog: str = 'changelog'
    service_yaml: str = 'service.yaml'
    tc_set_parameters_calls: Sequence = (
        {
            'name': 'env.RELEASE_TICKET',
            'value': 'https://st.test.yandex-team.ru/TAXIREL-1',
        },
    )
    tc_report_problems_calls: Sequence = ()
    extra_args: Sequence[str] = ()


@pytest.mark.arc
@pytest_wraps.parametrize(
    [
        Params(pytest_id='simple_case'),
        Params(
            pytest_id='extra_package_data',
            extra_args=('--with-version', '--with-last-changelog'),
            tc_set_parameters_calls=[
                {
                    'name': 'env.RELEASE_TICKET',
                    'value': 'https://st.test.yandex-team.ru/TAXIREL-1',
                },
                {'name': 'env.VERSION', 'value': '0.0.1'},
                {
                    'name': 'env.LAST_CHANGELOG',
                    'value': '* sanyash | Initial release',
                },
            ],
        ),
        Params(
            pytest_id='deb_case',
            service_yaml='service_deb.yaml',
            tc_set_parameters_calls=[
                {
                    'name': 'env.RELEASE_TICKET',
                    'value': 'https://st.test.yandex-team.ru/TAXIREL-1',
                },
                {'name': 'TIER_0', 'value': '1'},
                {'name': 'TIER_0_BUILD_DEBIAN', 'value': '1'},
            ],
        ),
        Params(
            pytest_id='substitutions_case',
            service_yaml='service_with_substitutions.yaml',
            tc_set_parameters_calls=[
                {
                    'name': 'env.RELEASE_TICKET',
                    'value': 'https://st.test.yandex-team.ru/TAXIREL-1',
                },
                {'name': 'TIER_0', 'value': '1'},
                {'name': 'TIER_0_BUILD_MACOS', 'value': '1'},
                {'name': 'TIER_0_BUILD_DEBIAN', 'value': '1'},
            ],
        ),
    ],
)
def test_send_teamcity_build_info(
        params: Params,
        monkeypatch,
        tmp_path,
        load,
        teamcity_set_parameters,
        teamcity_report_problems,
        arcadia_builder,
):
    arcadia_path = tmp_path / 'arcadia'
    arcadia_path.mkdir()
    monkeypatch.chdir(arcadia_path)

    service_name = 'basic-project'
    project_path = arcadia_path / 'projects' / service_name

    monkeypatch.setenv('ARCADIA_TOKEN', 'cool-token')

    with arcadia_builder:
        arcadia.init_arcadia_basic_project(arcadia_builder)
        arcadia.update_arcadia_project(
            arcadia_builder,
            {
                'service.yaml': load(params.service_yaml),
                'debian/changelog': load(params.changelog),
            },
            'add service.yaml and debian/changelog',
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
    send_teamcity_build_info.main(params.extra_args)

    assert teamcity_set_parameters.calls == list(
        params.tc_set_parameters_calls,
    )
    assert teamcity_report_problems.calls == list(
        params.tc_report_problems_calls,
    )
