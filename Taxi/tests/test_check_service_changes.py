import json
import os
from typing import List
from typing import NamedTuple
from typing import Sequence

import pytest

import check_service_changes
from tests.utils import repository
from tests.utils.examples import arcadia
from tests.utils.examples import backend_py3


class Params(NamedTuple):
    commits: Sequence[repository.Commit]
    master: str = 'masters/taxi-adjust'
    problems: List = []


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(Params(commits=[]), id='no-changes'),
        pytest.param(
            Params(
                commits=[
                    repository.Commit(
                        'commit',
                        [
                            'services/taximeter/file',
                            'services/new_service/debian/changelog',
                            'services/new_service/service.yaml',
                            'Makefile.imports',
                        ],
                    ),
                ],
            ),
            id='changes-in-other-folders',
        ),
        pytest.param(
            Params(
                commits=[
                    repository.Commit(
                        'commit',
                        ['services/taxi-adjust/file', 'Makefile.imports'],
                    ),
                ],
            ),
            id='changes-in-service-to-release',
        ),
        pytest.param(
            Params(
                commits=[
                    repository.Commit(
                        'commit',
                        ['services/taxi-adjust/file', 'Makefile.imports'],
                    ),
                ],
                problems=[
                    {
                        'description': (
                            'Service taxi-adjust has unreleased changes'
                        ),
                        'identity': None,
                    },
                ],
                master='masters/taximeter',
            ),
            id='changes-in-taxi-adjust',
        ),
    ],
)
def test_check_service_changes(
        tmpdir, chdir, monkeypatch, teamcity_report_problems, params: Params,
):
    repo = backend_py3.init(tmpdir)
    monkeypatch.setenv('REQUIRE_UNCHANGED_SERVICE', 'taxi-adjust')
    chdir(repo.working_tree_dir)
    repo.git.checkout('-b', 'origin/develop')
    repository.apply_commits(repo, params.commits)
    repo.git.checkout(params.master)

    check_service_changes.main()

    assert teamcity_report_problems.calls == params.problems


class ArcParams(NamedTuple):
    diff: str = ''
    fail: bool = False


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(ArcParams(), id='basic_success'),
        pytest.param(
            ArcParams(
                diff='taxi/services/driver-authorizer/foobar', fail=True,
            ),
            id='basic_failure',
        ),
    ],
)
def test_arc_check_service_changes(
        tmpdir,
        chdir,
        monkeypatch,
        commands_mock,
        teamcity_report_problems,
        params,
):
    monkeypatch.setenv('REQUIRE_UNCHANGED_SERVICE', 'driver-authorizer')

    workdir = arcadia.init_uservices(
        tmpdir,
        main_service='my-new-service',
        changelog_content='nobody cares',
    )
    monkeypatch.setenv(
        'MASTER_BRANCH', 'users/robot-taxi-teamcity/uservices/telematics',
    )

    @commands_mock('arc')
    def _arc(args, **kwargs):
        command = args[1]
        if command == 'info':
            return json.dumps(
                {
                    'branch': (
                        'users/robot-taxi-teamcity/uservices/my-new-service'
                    ),
                },
            )
        if command == 'merge-base':
            return 'master_base'
        if command == 'diff':
            assert args == [
                'arc',
                'diff',
                'master_base',
                'trunk',
                os.path.join(workdir, 'services/driver-authorizer'),
                '--name-only',
            ]
            return params.diff
        raise NotImplementedError(command)

    chdir(workdir)
    check_service_changes.main()

    if params.fail:
        assert teamcity_report_problems.calls == [
            {
                'description': (
                    'Service driver-authorizer has unreleased changes'
                ),
                'identity': None,
            },
        ]
    else:
        assert teamcity_report_problems.calls == []
