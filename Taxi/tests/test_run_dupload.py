import os
from typing import Callable
from typing import NamedTuple
from typing import Sequence

import git
import pytest

import run_dupload
from tests.utils import repository
from tests.utils.examples import arcadia
from tests.utils.examples import backend
from tests.utils.examples import backend_cpp
from tests.utils.examples import backend_py3
from tests.utils.examples import uservices


REPONAME = 'yandex-taxi-repo'


class Params(NamedTuple):
    init_repo: Callable[[str], git.Repo]
    changes: str
    branch: str
    path: str
    commits: Sequence[repository.Commit] = ()
    dupload_to: str = REPONAME


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                init_repo=backend.init,
                changes='taxi-backend_3.0.224_amd64.changes',
                branch='master',
                path='',
            ),
            id='backend master',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                changes='taxi-backend_3.0.224_amd64.changes',
                branch='develop',
                path='',
            ),
            id='backend develop',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                changes='taxi-backend-cpp_2.1.1_amd64.changes',
                branch='master',
                path='',
            ),
            id='backend-cpp master',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                changes='taxi-backend-cpp_2.1.1_amd64.changes',
                branch='develop',
                path='',
            ),
            id='backend-cpp develop',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                changes='taxi-antifraud_3.0.0hotfix25_amd64.changes',
                branch='masters/antifraud',
                path='antifraud',
            ),
            id='backend-cpp antifraud',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                changes='taxi-adjust_0.1.1_amd64.changes',
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
            ),
            id='backend-py3 taxi-adjust',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                changes='taxi-adjust_0.1.1_amd64.changes',
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'fix',
                        ['services/taxi-adjust/service.yaml'],
                        files_content=(
                            'teamcity:\n  dupload-to: yandex-taxi-common'
                        ),
                    ),
                ],
                dupload_to='yandex-taxi-common',
            ),
            id='backend-py3 taxi-adjust dupload-to',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                changes='driver-authorizer_1.1.1_amd64.changes',
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
            ),
            id='uservices driver-authorizer',
        ),
    ],
)
def test_dupload(tmpdir, chdir, commands_mock, monkeypatch, params: Params):
    @commands_mock('dpkg-architecture')
    def dpkg_architecture(args, **kwargs):
        return 'amd64'

    @commands_mock('dupload')
    def dupload(args, **kwargs):
        return 0

    monkeypatch.setenv('REPONAME', REPONAME)
    repo = params.init_repo(tmpdir)
    repo.git.checkout(params.branch)
    repository.apply_commits(repo, params.commits)
    chdir(repo.working_tree_dir)

    run_dupload.main([])

    assert dpkg_architecture.calls == [
        {
            'args': ['dpkg-architecture', '-qDEB_BUILD_ARCH'],
            'kwargs': {
                'cwd': os.path.join(repo.working_tree_dir, params.path),
                'env': None,
                'stdout': -1,
                'stderr': -1,
            },
        },
    ]
    assert dupload.calls == [
        {
            'args': [
                'dupload',
                '--nomail',
                '--to',
                params.dupload_to,
                params.changes,
            ],
            'kwargs': {
                'cwd': os.path.join(repo.working_tree_dir, params.path, '..'),
                'env': None,
            },
        },
    ]


@pytest.mark.parametrize(
    'script_args', [[], ['--packages-json', 'package.json']],
)
def test_packages_json_dupload(
        tmpdir, chdir, commands_mock, monkeypatch, load, script_args,
):
    @commands_mock('dpkg-architecture')
    def dpkg_architecture(args, **kwargs):
        return 'amd64'

    @commands_mock('dupload')
    def dupload(args, **kwargs):
        return 0

    @commands_mock('arc')
    def arc(args, **kwargs):
        command = args[1]
        if command == 'info':
            return '{"branch":"users/robot-taxi-teamcity/graph"}'
        return ''

    monkeypatch.setenv('REPONAME', REPONAME)
    monkeypatch.setenv('MASTER_BRANCH', 'users/robot-taxi-teamcity/graph')
    work_dir = arcadia.init_graph(tmpdir, load('graph-changelog.txt'))
    monkeypatch.chdir(work_dir)
    cwd = str(work_dir) + '/'

    run_dupload.main(script_args)

    assert dpkg_architecture.calls == [
        {
            'args': ['dpkg-architecture', '-qDEB_BUILD_ARCH'],
            'kwargs': {'cwd': cwd, 'env': None, 'stdout': -1, 'stderr': -1},
        },
    ]
    assert dupload.calls == [
        {
            'args': [
                'dupload',
                '--nomail',
                '--to',
                REPONAME,
                'libyandex-taxi-graph_8630448_amd64.changes',
            ],
            'kwargs': {'cwd': cwd, 'env': None},
        },
    ]

    assert arc.calls == [
        {
            'args': ['arc', 'info', '--json'],
            'kwargs': {
                'cwd': work_dir,
                'env': None,
                'stderr': -1,
                'stdout': -1,
            },
        },
    ]
