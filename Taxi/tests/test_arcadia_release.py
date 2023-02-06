import dataclasses
import json
import pathlib
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Sequence

import pytest

import arc_checkout
import run_release
from taxi_buildagent.tools.vcs import arc_repo
from tests.utils import pytest_wraps
from tests.utils.examples import arcadia


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    init_repo: Callable = arcadia.init_arcadia_nested_services
    branch_locked: bool = False
    build_problems_calls: Sequence[Dict[str, Any]] = ()
    build_parameters_calls: Sequence[Dict[str, Any]] = (
        {'name': 'env.AFFECTED_USERS', 'value': 'tester'},
    )
    project_path: str = 'projects/nested-example'
    service_path: Optional[str] = 'nested/services/first-service'
    master_branch: str = 'projects/nested-example/first-service'
    master_at: str = 'r2'
    create_ticket_calls: Sequence[Dict[str, Any]] = (
        {
            'json': {
                'assignee': 'release-starter',
                'components': [100, 42],
                'description': (
                    'tester | feat first-service: add service.yaml'
                    '(((https://a.yandex-team.ru/arc/commit/3 3)))'
                ),
                'followers': ['tester'],
                'queue': 'TAXIREL',
                'summary': 'example-project first-service 0.0.2',
            },
        },
    )
    expected_tag: str = (
        'tags/users/robot-taxi-teamcity/'
        'projects/nested-example/first-service/0.0.2'
    )
    is_push_expected: bool = True


BRANCH_LOCKED_MESSAGE = 'Another release build is in progress'

PARAMS = [
    Params(pytest_id='basic_success'),
    Params(
        pytest_id='fail_with_branch_lock',
        branch_locked=True,
        create_ticket_calls=[],
        build_problems_calls=(
            {'description': BRANCH_LOCKED_MESSAGE, 'identity': 'branch_lock'},
        ),
        build_parameters_calls=(
            {'name': 'env.BUILD_PROBLEM', 'value': BRANCH_LOCKED_MESSAGE},
        ),
        is_push_expected=False,
    ),
]


@pytest.mark.arc
@pytest_wraps.parametrize(PARAMS)
def test_arc_release(
        params: Params,
        tmp_path,
        commands_mock,
        monkeypatch,
        arcadia_builder,
        startrek,
        teamcity_set_parameters,
        teamcity_report_problems,
):
    work_dir: pathlib.Path = tmp_path / 'arcadia'
    work_dir.mkdir()
    monkeypatch.chdir(work_dir)

    monkeypatch.setattr('taxi_buildagent.tickets.USER_NAME', 'release-starter')
    monkeypatch.setenv('RELEASE_TICKET_SUMMARY', 'example-project')
    monkeypatch.setenv('TELEGRAM_DISABLED', '1')
    monkeypatch.setenv('SLACK_DISABLED', '1')
    monkeypatch.setenv('ADD_FOLLOWERS', '1')

    @commands_mock('ya')
    def ya_mock(args, **kwargs):
        return 0

    with arcadia_builder:
        params.init_repo(arcadia_builder)

    arc_checkout.main([str(work_dir), '--branch', 'trunk'])
    assert teamcity_report_problems.calls == []

    repo = arc_repo.Repo(work_dir / params.project_path, from_root=True)
    master_branch = repo.stable_branch_prefix + params.master_branch
    repo.checkout_new_branch(master_branch, params.master_at)

    # FIXME(TAXITOOLS-3888): shouldn't be a special case for monoprojects
    if not params.service_path:
        monkeypatch.setenv('MASTER_BRANCH', master_branch)

    service_path = pathlib.Path(repo.path, params.service_path or '.')
    changelog_path = service_path / 'debian/changelog'
    changelog_path.parent.mkdir(exist_ok=True, parents=True)
    changelog_path.write_text(
        """sample-first-service (0.0.1) unstable; urgency=low

  * Ivan Ivanov | Initial release

 -- buildfarm <buildfarm@yandex-team.ru>  Fri, 1 Sep 2021 12:00:00 +0300
""",
    )
    repo.add_paths_to_index([str(changelog_path)])
    repo.commit('release 0.0.1')
    repo.arc.push('--force', '--set-upstream', master_branch)
    initial_commit = repo.get_commit_info('HEAD')

    if params.branch_locked:
        lockfile = repo.path / '.lock'
        lockfile.parent.mkdir(exist_ok=True, parents=True)
        lockfile.touch()
        repo.add_paths_to_index([str(lockfile)], force=True)
        repo.commit('locked!')
        repo.push_tag(f'lock/release/{params.master_branch}')
        repo.reset(initial_commit.hash, hard=True)

    monkeypatch.setenv('BUILD_ID', '42')

    run_release.main(['--path', params.project_path])

    # No uncommitted junk should be present
    assert json.loads(repo.arc.status('--json', output=True)) == {'status': {}}

    assert ya_mock.calls == []
    assert teamcity_report_problems.calls == list(params.build_problems_calls)
    assert teamcity_set_parameters.calls == list(params.build_parameters_calls)
    assert startrek.create_ticket.calls == list(params.create_ticket_calls)
    assert startrek.create_comment.calls == []

    current_commit = repo.get_commit_info('HEAD')
    if not params.build_problems_calls:
        assert current_commit.author_name == 'buildfarm'
    else:
        assert current_commit.hash == initial_commit.hash

    if params.is_push_expected:
        repo.fetch_remote(master_branch)
        branch_commit = repo.get_commit(repo.REMOTE_PREFIX + master_branch)
        assert branch_commit == current_commit.hash

        repo.fetch_remote(params.expected_tag)
        tag_commit = repo.get_commit(repo.REMOTE_PREFIX + params.expected_tag)
        assert tag_commit == current_commit.hash
