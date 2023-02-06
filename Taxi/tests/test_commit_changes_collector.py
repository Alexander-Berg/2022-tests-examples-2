import functools
import os
import pathlib
from typing import Callable
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Sequence

import freezegun
import git
import pytest

import commit_changes_collector
from taxi_buildagent.tools import vcs
from tests.plugins import arc
from tests.utils import repository
from tests.utils.examples import arcadia
from tests.utils.examples import backend_py3
from tests.utils.examples import uservices


def _create_git_ignore(repo: vcs.Repo) -> None:
    path = pathlib.Path(repo.path) / repo.VCS_IGNORE
    path.write_text('generated-*', encoding='utf-8')
    repo.add_paths_to_index([repo.VCS_IGNORE])
    repo.commit('add .gitignore')


def _create_two_files(repo: vcs.Repo) -> None:
    (pathlib.Path(repo.path) / 'file1').write_text('data1', encoding='utf-8')
    repo.add_paths_to_index(['file1'])
    repo.commit('add file1')
    (pathlib.Path(repo.path) / 'file2').write_text('data2', encoding='utf-8')
    repo.add_paths_to_index(['file2'])
    repo.commit('add file2')


class Params(NamedTuple):
    init_repo: Callable[[str], git.Repo]
    prev_commit_generated: Dict[str, str]
    last_commit_generated: Dict[str, str]
    report_changed_generated: List[str]
    report_changed_paths: str
    report_current_branch: str
    create_git_ignore: bool = False
    startup_proc: Optional[Callable[[vcs.Repo], None]] = None
    commits: Sequence[repository.Commit] = ()
    arc_calls: List[str] = []
    build_dir: str = ''
    os_uservices: str = ''
    make_target: str = 'gen'


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                init_repo=uservices.init,
                prev_commit_generated={'not-changed': '1', 'changed': '1'},
                last_commit_generated={'not-changed': '1', 'changed': '2'},
                report_changed_generated=[
                    'changed',
                    'services/driver-authorizer/local-files-dependencies.txt',
                    'services/pilorama/local-files-dependencies.txt',
                ],
                report_changed_paths=(
                    'services/driver-authorizer/local-files-dependencies.txt\n'
                    'services/pilorama/local-files-dependencies.txt'
                ),
                report_current_branch='develop',
            ),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                prev_commit_generated={'not-changed': '1', 'changed': '1'},
                last_commit_generated={'not-changed': '1', 'changed': '2'},
                report_changed_generated=[
                    'changed',
                    'services/some/src/source.cpp',
                ],
                report_changed_paths='services/some/src/source.cpp',
                report_current_branch='develop',
                commits=[
                    repository.Commit(
                        'create file',
                        ['services/some/src/source.cpp'],
                        files_content='important content',
                    ),
                    repository.Commit(
                        'update file',
                        ['services/some/src/source.cpp'],
                        files_content='new content',
                    ),
                ],
            ),
            id='uservices create and update file',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                prev_commit_generated={'not-changed': '1', 'changed': '1'},
                last_commit_generated={'not-changed': '1', 'changed': '2'},
                report_changed_generated=[
                    'changed',
                    'libraries/another-library/local-files-dependencies.txt',
                ],
                report_changed_paths=(
                    'libraries/another-library/local-files-dependencies.txt'
                ),
                report_current_branch='develop',
            ),
            id='backend_py3',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                prev_commit_generated={'not-changed': '1', 'changed': '1'},
                last_commit_generated={'not-changed': '1', 'changed': '2'},
                report_changed_generated=['changed', 'file2'],
                report_changed_paths='file2',
                report_current_branch='develop',
                startup_proc=_create_two_files,
                create_git_ignore=True,
            ),
            id='backend_py3 .gitignore',
        ),
        pytest.param(
            Params(
                init_repo=functools.partial(
                    arcadia.init_uservices,
                    main_service='test-service',
                    changelog_content='some_content',
                ),
                prev_commit_generated={'not-changed': '1', 'changed': '1'},
                last_commit_generated={'not-changed': '1', 'changed': '2'},
                report_changed_generated=[
                    'services/driver-authorizer/local-files-dependencies.txt',
                    'services/test-service/local-files-dependencies.txt',
                ],
                report_changed_paths=(
                    'services/driver-authorizer/local-files-dependencies.txt\n'
                    'services/test-service/local-files-dependencies.txt'
                ),
                report_current_branch=(
                    'users/robot-taxi-teamcity/uservices/test-service'
                ),
                make_target='build-bionic',
                os_uservices='bionic',
                arc_calls=[
                    'arc info --json',
                    'arc rev-parse HEAD',
                    'arc log --json -n1 $taxidir',
                    'arc diff aaaaa^ aaaaa $taxidir --name-only',
                    'arc log -n2 --oneline HEAD .',
                    'arc fetch users/robot-taxi-teamcity/'
                    'statistics/bionic/taxi',
                    'arc merge-base trunk users/robot-taxi-teamcity/'
                    'statistics/bionic/taxi',
                    'arc info --json',
                    'arc checkout -b statistics-prev 45329c',
                    'arc add --all',
                    'arc commit --message add generated files --force',
                    'arc info --json',
                    'arc clean -d -x -q',
                    'arc checkout -b statistics-cur HEAD',
                    'arc add --all',
                    'arc commit --message add generated files --force',
                    'arc diff statistics-cur statistics-prev $taxidir '
                    '--name-only',
                    'arc push statistics-cur:users/robot-taxi-teamcity/'
                    'statistics/bionic/taxi --force',
                ],
            ),
            id='uservices_arcadia',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                prev_commit_generated={'not-changed': '1', 'changed': '1'},
                last_commit_generated={
                    'not-changed': '1',
                    'changed': '2',
                    'CMakeCache.txt': '123',
                },
                report_changed_generated=['build-dir/changed', 'file2'],
                report_changed_paths='file2',
                report_current_branch='develop',
                startup_proc=_create_two_files,
                create_git_ignore=True,
                build_dir='build-dir',
            ),
            id='add_build_dir_and_skip_ignore',
        ),
    ],
)
@freezegun.freeze_time('2018-04-23 14:22:56', tz_offset=3)
def test_commit_changes_collector(tmpdir, commands_mock, params) -> None:
    init_repo = params.init_repo(tmpdir)
    os.chdir(tmpdir)
    if hasattr(init_repo, 'git'):
        init_repo.git.branch('statistics', 'HEAD')
        init_repo.git.push('origin', 'statistics')
        repo_path = pathlib.Path(tmpdir / 'repo')
    else:
        repo_path = pathlib.Path(tmpdir / 'taxi')
    repo = vcs.open_repo(repo_path)
    report_dir = tmpdir.mkdir('report')

    if params.create_git_ignore:
        _create_git_ignore(repo)

    if params.startup_proc:
        params.startup_proc(repo)

    if params.commits:
        repository.apply_commits(init_repo, params.commits)
        init_repo.git.submodule('update', '--init', '--recursive')

    build_dir = repo_path
    if params.build_dir:
        build_dir = tmpdir.mkdir(params.build_dir)

    generated_files_sequence = [
        params.prev_commit_generated,
        params.last_commit_generated,
    ]

    @commands_mock('make')
    def _make(args, **kwargs):
        assert args[1] == params.make_target
        files_to_gen = generated_files_sequence.pop(0)
        for filename, content in files_to_gen.items():
            (build_dir / filename).write_text(content, encoding='utf8')
        return ''

    @commands_mock('arc')
    def arc_mock(args, **kwargs):
        command = args[1]
        if command == 'info':
            return '{"branch": "users/robot-taxi-teamcity/uservices/%s"}' % (
                'test-service',
            )
        if command == 'status':
            return '?? generated-last-1\n A generated-last-2'
        if command == 'log':
            if args[3] == '--oneline':
                return 'aaaaa ddd\n45329c ffefe'
            return (
                '[{"author":"noname","commit":"aaaaa","message":'
                '"junk pr commit","parents":["23456b"],"date":'
                '"2021-03-18T20:23:22+03:00"}]'
            )
        if command == 'diff':
            return (
                'taxi/services/driver-authorizer/local-files-dependencies.txt'
                '\ntaxi/services/test-service/local-files-dependencies.txt'
            )
        return 0

    def assert_file_as_expected(basename, expected):
        with open(report_dir / basename) as inp:
            actual = inp.read()
        assert expected == actual, basename

    argv = []
    if params.make_target:
        argv.extend(['--make-target', params.make_target])
    if params.build_dir:
        argv.extend(['--build-dir', params.build_dir])
    if params.os_uservices:
        argv.extend(['--os', params.os_uservices])
    commit_changes_collector.main(argv + [str(repo_path), str(report_dir)])

    assert_file_as_expected(
        'changed_generated.txt', '\n'.join(params.report_changed_generated),
    )
    assert_file_as_expected('changed_paths.txt', params.report_changed_paths)
    assert_file_as_expected('current_branch.txt', params.report_current_branch)
    expected_arc_calls = [
        arc.replace_paths(command, {'taxidir': repo_path})
        for command in params.arc_calls
    ]
    assert expected_arc_calls == [
        ' '.join(call['args']) for call in arc_mock.calls
    ]
