# pylint: disable=C0103
import os
import pathlib
import shutil
import subprocess
from typing import Callable
from typing import NamedTuple
from typing import Optional
from typing import Sequence

import git
import pytest

import run_build
from tests.plugins import arc as arc_mod
from tests.utils import repository
from tests.utils.examples import arcadia
from tests.utils.examples import backend
from tests.utils.examples import backend_cpp
from tests.utils.examples import backend_py3
from tests.utils.examples import uservices


class Params(NamedTuple):
    init_repo: Callable[[str], git.Repo]
    branch: str
    path: str = ''
    argv: Sequence[str] = ()
    fail_message: Optional[str] = None
    is_exited: bool = False


def call_kwargs(stdout=False, cwd=None, env=None):
    if env:
        copy = os.environ.copy()
        copy.update(env)
        env = copy
    kwargs = {'cwd': cwd, 'env': env}
    if stdout:
        kwargs['stdout'] = subprocess.PIPE
    return kwargs


@pytest.mark.parametrize(
    'params',
    [
        Params(init_repo=backend.init, branch='master'),
        Params(init_repo=backend.init, branch='develop'),
        Params(init_repo=backend_cpp.init, branch='master'),
        Params(init_repo=backend_cpp.init, branch='develop'),
        Params(
            init_repo=backend_cpp.init,
            branch='masters/antifraud',
            path='antifraud',
        ),
        Params(
            init_repo=backend_py3.init,
            branch='masters/taxi-adjust',
            path='services/taxi-adjust',
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/driver-authorizer',
            path='services/driver-authorizer',
        ),
        Params(
            init_repo=backend.init, branch='HEAD^', argv=['--build-current'],
        ),
        Params(
            init_repo=backend.init,
            branch='HEAD^',
            fail_message='Could not match branch `HEAD` in project to build',
            is_exited=True,
        ),
    ],
)
def test_build(
        tmpdir,
        chdir,
        commands_mock,
        monkeypatch,
        params,
        teamcity_report_problems,
):
    @commands_mock('debuild')
    def debuild(args, **kwargs):
        return 0

    monkeypatch.setenv('NPROCS', '5')
    repo = params.init_repo(tmpdir)
    repo.git.checkout(params.branch)
    chdir(repo.working_tree_dir)

    if params.is_exited:
        with pytest.raises(SystemExit):
            run_build.main(params.argv)
    else:
        run_build.main(params.argv)
    if params.fail_message is not None:
        fail_message = teamcity_report_problems.calls[0]['description']
        assert debuild.calls == []
        assert fail_message == params.fail_message
    else:
        assert debuild.calls == [
            {
                'args': [
                    'debuild',
                    '--no-tgz-check',
                    '--no-lintian',
                    '-sa',
                    '-b',
                ],
                'kwargs': call_kwargs(
                    cwd=pathlib.Path(repo.working_tree_dir, params.path),
                    env={'DEB_BUILD_OPTIONS': 'parallel=5 nocheck'},
                ),
            },
        ]


def test_build_first_project(tmpdir, chdir, teamcity_report_problems):
    repo = backend.init(tmpdir)
    chdir(repo.working_tree_dir)
    repo.git.checkout('-b', 'masters/new-project')
    repository.commit_debian_dir(
        repo, 'new-project', path='new-project', version='0.0.0',
    )
    with pytest.raises(SystemExit):
        run_build.main([])
    assert teamcity_report_problems.calls == [
        {'description': 'Not building 0.0.0 release', 'identity': None},
    ]


def test_build_empty_project(tmpdir, chdir, teamcity_report_problems):
    repo = backend_py3.init(tmpdir)
    chdir(repo.working_tree_dir)
    repo.git.checkout('-b', 'masters/new-project')
    with pytest.raises(SystemExit):
        run_build.main([])
    assert teamcity_report_problems.calls == [
        {'description': 'Changelog not found', 'identity': None},
    ]


def test_build_broken_project(
        tmpdir, chdir, teamcity_report_problems, commands_mock, monkeypatch,
):
    @commands_mock('debuild')
    def debuild(args, **kwargs):
        return 1

    monkeypatch.setenv('NPROCS', '5')
    repo = backend_cpp.init(tmpdir)
    repo.git.checkout('masters/antifraud')
    chdir(repo.working_tree_dir)
    with pytest.raises(SystemExit):
        run_build.main([])
    assert debuild.calls == [
        {
            'args': ['debuild', '--no-tgz-check', '--no-lintian', '-sa', '-b'],
            'kwargs': call_kwargs(
                cwd=pathlib.Path(repo.working_tree_dir, 'antifraud'),
                env={'DEB_BUILD_OPTIONS': 'parallel=5 nocheck'},
            ),
        },
    ]
    assert teamcity_report_problems.calls == [
        {
            'description': (
                'Build failed. See '
                'https://wiki.yandex-team.ru/taxi/backend/'
                'automatization/faq/#upalbildservisavteamcity '
                'for details'
            ),
            'identity': None,
        },
    ]


def test_build_package_json(
        tmpdir,
        teamcity_report_problems,
        commands_mock,
        monkeypatch,
        load,
        get_file_path,
):
    monkeypatch.setenv('MASTER_BRANCH', 'users/robot-taxi-teamcity/graph')
    work_dir = arcadia.init_graph(tmpdir, load('graph-changelog.txt'))
    monkeypatch.chdir(work_dir)

    @commands_mock('ya')
    def ya(args, **kwargs):
        shutil.copy(
            get_file_path('libyandex-taxi-graph.0.0.3.tar.gz'), str(work_dir),
        )
        return 0

    @commands_mock('debuild')
    def debuild(args, **kwargs):
        return 1

    @commands_mock('arc')
    def arc(args, **kwargs):
        command = args[1]
        if command == 'info':
            return '{"branch":"users/robot-taxi-teamcity/graph"}'
        return ''

    run_build.main(['--packages-json', 'package.json'])

    assert debuild.calls == []
    assert teamcity_report_problems.calls == []
    assert ya.calls == [
        {
            'args': [
                'ya',
                'package',
                '--build=release',
                '--debian',
                '--change-log=debian/changelog',
                'package.json',
            ],
            'kwargs': {'cwd': pathlib.PosixPath('.'), 'env': None},
        },
    ]
    arc_calls = [
        {
            'args': ['arc', 'info', '--json'],
            'kwargs': {
                'cwd': '$workdir',
                'env': None,
                'stderr': -1,
                'stdout': -1,
            },
        },
    ]
    arc_mod.substitute_paths(arc_calls, {'workdir': work_dir})

    assert arc.calls == arc_calls
    assert sorted(os.listdir(work_dir)) == [
        'debian',
        'libyandex-taxi-graph.0.0.3.tar.gz',
        'package.json',
        'taxi-graph_1.0.0_all.changes',
        'taxi-graph_1.0.0_all.deb',
    ]


class YaPackageParams(NamedTuple):
    argv: Sequence[str] = ()
    expected_ya_options: Sequence[str] = ()


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(YaPackageParams(), id='no_flags'),
        pytest.param(
            YaPackageParams(
                argv=['--ya-package-options=--strip'],
                expected_ya_options=['--strip'],
            ),
            id='one_flag_without_quotes',
        ),
        pytest.param(
            YaPackageParams(
                argv=['--ya-package-options="--strip"'],
                expected_ya_options=['--strip'],
            ),
            id='one_flag_in_quotes',
        ),
        pytest.param(
            YaPackageParams(
                argv=[
                    '--ya-package-options='
                    '"--strip --sandbox --owner=RESOURCE_OWNER"',
                ],
                expected_ya_options=[
                    '--strip',
                    '--sandbox',
                    '--owner=RESOURCE_OWNER',
                ],
            ),
            id='several_flags_in_quotes',
        ),
        pytest.param(
            YaPackageParams(
                argv=[
                    '--ya-package-options',
                    '--strip --sandbox --owner=RESOURCE_OWNER',
                ],
                expected_ya_options=[
                    '--strip',
                    '--sandbox',
                    '--owner=RESOURCE_OWNER',
                ],
            ),
            id='several_flags_without_quotes',
        ),
    ],
)
def test_debuild_arcadia_project(
        tmpdir,
        load,
        get_file_path,
        commands_mock,
        monkeypatch,
        teamcity_report_problems,
        params,
):
    monkeypatch.setenv('MASTER_BRANCH', 'users/robot-taxi-teamcity/graph')
    monkeypatch.setenv('ARCADIA_PROJECT_REL_PATH', 'taxi/graph')
    monkeypatch.setenv('NPROCS', '5')
    root_dir = tmpdir
    work_dir = arcadia.init_graph(root_dir, load('graph-changelog.txt'))
    monkeypatch.chdir(root_dir)

    @commands_mock('debuild')
    def debuild(args, **kwargs):
        return 1

    @commands_mock('ya')
    def ya(args, **kwargs):
        shutil.copy(
            get_file_path('libyandex-taxi-graph.0.0.3.tar.gz'), str(work_dir),
        )
        return 0

    @commands_mock('arc')
    def arc(args, **kwargs):
        command = args[1]
        if command == 'info':
            return '{"branch":"users/robot-taxi-teamcity/graph"}'
        return ''

    run_build.main(params.argv)

    assert debuild.calls == []
    assert teamcity_report_problems.calls == []
    args = [
        'ya',
        'package',
        '--build=release',
        '--debian',
        '--change-log=debian/changelog',
        *params.expected_ya_options,
    ]

    args.append('package.json')
    ya_calls = [{'args': args, 'kwargs': {'cwd': '$workdir', 'env': None}}]
    arc_mod.substitute_paths(ya_calls, {'workdir': work_dir})
    assert ya.calls == ya_calls
    assert arc.calls == []
    assert sorted(os.listdir(work_dir)) == [
        'debian',
        'libyandex-taxi-graph.0.0.3.tar.gz',
        'package.json',
        'taxi-graph_1.0.0_all.changes',
        'taxi-graph_1.0.0_all.deb',
    ]
