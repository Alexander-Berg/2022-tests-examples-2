# pylint: disable=too-many-lines
import dataclasses
from typing import Any
from typing import Dict
from typing import Optional
from typing import Sequence

import freezegun
import pytest

import arc_checkout
import run_arcadia_custom
from taxi_buildagent import debian_package
from taxi_buildagent.clients import arcadia as arcadia_client
from taxi_buildagent.tools.vcs import arc_repo
from tests.utils import pytest_wraps
from tests.utils.examples import arcadia

BASE_CHANGELOG: str = 'base_changelog.txt'
BUILD_NUMBER = '123'


@dataclasses.dataclass
class ArcadiaCommit:
    name: str
    data: Sequence[str]
    project_path: str = 'projects/basic-project'


@dataclasses.dataclass
class ArcadiaPR:
    branch: str
    commits: Sequence[ArcadiaCommit]


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    arcadia_prs: str
    exp_arcadia_calls: Sequence[Dict[str, Any]] = (
        {
            'kwargs': {
                'headers': {'Authorization': 'OAuth some-token'},
                'params': {
                    'fields': (
                        'review_requests(id,author,summary,'
                        'vcs(from_branch,to_branch),'
                        'checks(system,type,status,updated_at,alias),labels,'
                        'description)'
                    ),
                    'query': (
                        'label(taxi/deploy:testing);open();path('
                        '/projects/basic-project|'
                        '/projects/other-proj/ml|'
                        '/projects/other-proj/schemas)'
                    ),
                    'limit': 10000,
                },
            },
            'method': 'get',
            'url': arcadia_client.API_URL + 'v1/review-requests',
        },
    )
    tc_report_build_number: Sequence[Dict[str, Any]] = (
        {'build_number': '0.0.0testing123'},
    )
    prs_content: Sequence[ArcadiaPR] = ()
    tc_set_parameters: Sequence[Dict[str, Any]] = ()
    tc_report_problems: Sequence[Dict[str, Any]] = ()
    exp_package_name: str = 'yandex-taxi-my-service'
    exp_version: str = '0.0.0testing123'
    exp_release_ticket: Optional[str] = 'https://st.yandex-team.ru/TAXIREL-222'
    exp_changes: Sequence[str] = ()


@freezegun.freeze_time(
    '2020-09-01 20:59:59', tz_offset=3, ignore=['grpc._channel'],
)
@pytest.mark.arc
@pytest_wraps.parametrize(
    [
        Params(
            pytest_id='no_prs',
            arcadia_prs='arcadia_no_prs.json',
            exp_changes=['(same as master)', 'CURRENT DEVELOP:'],
        ),
        Params(
            pytest_id='main_case',
            arcadia_prs='arcadia_prs1.json',
            exp_changes=[
                '(same as master)',
                '* buildfarm | feat ololo: ololo',
                '* buildfarm | feat ololo: ololo',
                '* buildfarm | feat ololo: ololo',
                '* buildfarm | fix',
                '* buildfarm | fixxxx',
                '* buildfarm | zzzz',
                'CURRENT DEVELOP:',
                'PR alberist@ "feat ololo: ololo (#5678)":',
                'PR dteterin@ "feat README: edit (#1234)":',
            ],
            prs_content=[
                ArcadiaPR(
                    branch='users/dteterin/edit-README-only',
                    commits=[
                        ArcadiaCommit(
                            name='feat ololo: ololo\n\nIssue: TIKET-123',
                            data=[
                                'services/my-service/service.yaml',
                                'services/my-service/src/main.cpp',
                            ],
                        ),
                        ArcadiaCommit(
                            name='fix',
                            data=['services/driver-authorizer/service.yaml'],
                        ),
                        ArcadiaCommit(name='fixxxx', data=['servicez.yaml']),
                    ],
                ),
                ArcadiaPR(
                    branch='users/alberist/ololo',
                    commits=[
                        ArcadiaCommit(
                            name='feat ololo: ololo',
                            data=['services/my-service/debian/changelog'],
                        ),
                        ArcadiaCommit(name='zzzz', data=['services1.yaml']),
                    ],
                ),
            ],
            tc_set_parameters=[
                {'name': 'env.AFFECTED_USERS', 'value': 'alberist dteterin'},
                {
                    'name': 'env.CUSTOM_MERGED_PULL_REQUESTS_REPORT',
                    'value': (
                        '[{"number": 1234, "url": '
                        '"https://a.yandex-team.ru/review/1234", '
                        '"staff_user": "dteterin", "title": '
                        '"feat README: edit", "labels": '
                        '["custom/label"], "from_branch": '
                        '"users/dteterin/edit-README-only"}, '
                        '{"number": 5678, "url": '
                        '"https://a.yandex-team.ru/review/5678", '
                        '"staff_user": "alberist", "title": '
                        '"feat ololo: ololo", "labels": '
                        '["custom/label"], "from_branch": '
                        '"users/alberist/ololo"}]'
                    ),
                },
            ],
        ),
        Params(
            pytest_id='additional_project_case',
            arcadia_prs='arcadia_prs1.json',
            exp_changes=[
                '(same as master)',
                'CURRENT DEVELOP:',
                'PR dteterin@ "feat README: edit (#1234)":',
            ],
            prs_content=[
                ArcadiaPR(
                    branch='users/dteterin/edit-README-only',
                    commits=[
                        ArcadiaCommit(
                            name='feat other-project: sone\n\nIssue: TIKET-1',
                            data=['../other-proj/schemas/some.txt'],
                        ),
                    ],
                ),
                ArcadiaPR(
                    branch='users/alberist/ololo',
                    commits=[
                        ArcadiaCommit(
                            name='feat ololo: ololo',
                            data=['../new-proj/services/my-service'],
                        ),
                    ],
                ),
            ],
            tc_set_parameters=[
                {'name': 'env.AFFECTED_USERS', 'value': 'dteterin'},
                {
                    'name': 'env.CUSTOM_MERGED_PULL_REQUESTS_REPORT',
                    'value': (
                        '[{"number": 1234, "url": '
                        '"https://a.yandex-team.ru/review/1234", '
                        '"staff_user": "dteterin", "title": '
                        '"feat README: edit", "labels": ["custom/label"], '
                        '"from_branch": "users/dteterin/edit-README-only"}]'
                    ),
                },
            ],
        ),
    ],
)
def test_run_arcadia_custom(
        params: Params,
        commands_mock,
        tmpdir,
        tmp_path,
        monkeypatch,
        load,
        teamcity_report_build_number,
        teamcity_set_parameters,
        teamcity_report_problems,
        patch_requests,
        load_json,
        arcadia_builder,
):
    @patch_requests(arcadia_client.API_URL + 'v1/review-requests')
    def arcadia_mock(method, url, **kwargs):
        return patch_requests.response(json=load_json(params.arcadia_prs))

    arcadia_path = tmp_path / 'arcadia'
    arcadia_path.mkdir()
    monkeypatch.chdir(arcadia_path)

    project_path = arcadia_path / 'projects' / 'basic-project'
    service_path = project_path / 'services' / 'my-service'
    changelog_path = service_path / 'debian' / 'changelog'

    monkeypatch.setenv('ARCADIA_TOKEN', 'some-token')

    with arcadia_builder:
        arcadia.init_arcadia_basic_project(arcadia_builder)

    arc_checkout.main([str(arcadia_path), '--branch', 'trunk'])

    assert teamcity_report_problems.calls == []

    repo = arc_repo.Repo(arcadia_path, from_root=True)

    master_branch = (
        repo.stable_branch_prefix + 'projects/basic-project/my-service'
    )
    repo.checkout_new_branch(master_branch, 'trunk')
    changelog_path.parent.mkdir(exist_ok=True, parents=True)
    changelog_path.write_text(load(BASE_CHANGELOG))
    repo.add_paths_to_index([str(changelog_path)])
    repo.commit('release 0.0.0')
    repo.arc.push('--force', '--set-upstream', master_branch)

    repo.fetch_remote(master_branch)

    for pr_content in params.prs_content:
        branch = pr_content.branch
        repo.checkout_new_branch(branch, 'trunk')
        for commit in pr_content.commits:
            for file_path in commit.data:
                full_file_path = project_path.joinpath(file_path)
                full_file_path.parent.mkdir(parents=True, exist_ok=True)
                full_file_path.write_text('')
                repo.add_paths_to_index(['.'])
                repo.commit(commit.name)
                repo.arc.push('--force', '--set-upstream', branch)

    repo.checkout(master_branch)

    argv = [
        '--build-number',
        BUILD_NUMBER,
        '--deploy-branch',
        'testing',
        '--path',
        str(project_path.relative_to(arcadia_path)),
    ]
    run_arcadia_custom.main(argv)

    assert teamcity_report_build_number.calls == list(
        params.tc_report_build_number,
    )
    assert teamcity_set_parameters.calls == list(params.tc_set_parameters)
    assert teamcity_report_problems.calls == list(params.tc_report_problems)
    assert arcadia_mock.calls == list(params.exp_arcadia_calls)
    with changelog_path.open(encoding='utf-8') as fin:
        changelog = debian_package.parse_changelog(fin)
    assert changelog.package_name == params.exp_package_name
    assert changelog.version == params.exp_version
    assert sorted(changelog.changes) == list(params.exp_changes)
