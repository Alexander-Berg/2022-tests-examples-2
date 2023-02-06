import pathlib
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Sequence

import pytest

import arc_checkout
from tests.plugins import arc


class Params(NamedTuple):
    checkout_path: str
    arc_calls: List[Dict[str, Any]]
    commit: Optional[str] = None
    branch: Optional[str] = None
    rebase_on_trunk: bool = False
    conflict_with_trunk: bool = False
    wrong_commit: bool = False
    tc_report_problems_calls: Sequence[Dict[str, Any]] = []


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                checkout_path='arcadia',
                arc_calls=[
                    {
                        'args': [
                            'arc',
                            'mount',
                            '--mount',
                            '$workdir/arcadia',
                            '--store',
                            '$homedir/arc/store',
                            '--object-store',
                            '$homedir/arc/object-store',
                            '--allow-other',
                        ],
                        'kwargs': {
                            'cwd': '$homedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                ],
            ),
            id='simple_case',
        ),
        pytest.param(
            Params(
                checkout_path='arcadia',
                branch='users/dteterin/cool-branch',
                arc_calls=[
                    {
                        'args': [
                            'arc',
                            'mount',
                            '--mount',
                            '$workdir/arcadia',
                            '--store',
                            '$homedir/arc/store',
                            '--object-store',
                            '$homedir/arc/object-store',
                            '--allow-other',
                        ],
                        'kwargs': {
                            'cwd': '$homedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'fetch', 'users/dteterin/cool-branch'],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir/arcadia',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/dteterin/cool-branch',
                        ],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                ],
            ),
            id='with_branch',
        ),
        pytest.param(
            Params(
                checkout_path='arcadia',
                branch='arcadia/users/dteterin/cool-branch',
                arc_calls=[
                    {
                        'args': [
                            'arc',
                            'mount',
                            '--mount',
                            '$workdir/arcadia',
                            '--store',
                            '$homedir/arc/store',
                            '--object-store',
                            '$homedir/arc/object-store',
                            '--allow-other',
                        ],
                        'kwargs': {
                            'cwd': '$homedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'fetch', 'users/dteterin/cool-branch'],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir/arcadia',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/dteterin/cool-branch',
                        ],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                ],
            ),
            id='with_remote_branch',
        ),
        pytest.param(
            Params(
                checkout_path='arcadia',
                commit='736be3',
                arc_calls=[
                    {
                        'args': [
                            'arc',
                            'mount',
                            '--mount',
                            '$workdir/arcadia',
                            '--store',
                            '$homedir/arc/store',
                            '--object-store',
                            '$homedir/arc/object-store',
                            '--allow-other',
                        ],
                        'kwargs': {
                            'cwd': '$homedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'reset',
                            '736be3',
                            '--hard',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                ],
            ),
            id='with_commit',
        ),
        pytest.param(
            Params(
                checkout_path='arcadia',
                branch='users/dteterin/cool-branch',
                commit='736be3',
                arc_calls=[
                    {
                        'args': [
                            'arc',
                            'mount',
                            '--mount',
                            '$workdir/arcadia',
                            '--store',
                            '$homedir/arc/store',
                            '--object-store',
                            '$homedir/arc/object-store',
                            '--allow-other',
                        ],
                        'kwargs': {
                            'cwd': '$homedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'fetch', 'users/dteterin/cool-branch'],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir/arcadia',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/dteterin/cool-branch',
                        ],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'reset',
                            '736be3',
                            '--hard',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                ],
            ),
            id='with_branch_and_commit',
        ),
        pytest.param(
            Params(
                checkout_path='arcadia',
                branch='trunk',
                arc_calls=[
                    {
                        'args': [
                            'arc',
                            'mount',
                            '--mount',
                            '$workdir/arcadia',
                            '--store',
                            '$homedir/arc/store',
                            '--object-store',
                            '$homedir/arc/object-store',
                            '--allow-other',
                        ],
                        'kwargs': {
                            'cwd': '$homedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                ],
            ),
            id='on_trunk',
        ),
        pytest.param(
            Params(
                checkout_path='arcadia',
                branch='users/dteterin/cool-branch',
                commit='736be3',
                rebase_on_trunk=True,
                arc_calls=[
                    {
                        'args': [
                            'arc',
                            'mount',
                            '--mount',
                            '$workdir/arcadia',
                            '--store',
                            '$homedir/arc/store',
                            '--object-store',
                            '$homedir/arc/object-store',
                            '--allow-other',
                        ],
                        'kwargs': {
                            'cwd': '$homedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'fetch', 'users/dteterin/cool-branch'],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir/arcadia',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/dteterin/cool-branch',
                        ],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'reset',
                            '736be3',
                            '--hard',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                    {
                        'args': ['arc', 'rebase', 'trunk', '--force'],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                ],
            ),
            id='rebase_on_trunk',
        ),
        pytest.param(
            Params(
                checkout_path='arcadia',
                branch='users/dteterin/cool-branch',
                commit='736be3',
                conflict_with_trunk=True,
                arc_calls=[
                    {
                        'args': [
                            'arc',
                            'mount',
                            '--mount',
                            '$workdir/arcadia',
                            '--store',
                            '$homedir/arc/store',
                            '--object-store',
                            '$homedir/arc/object-store',
                            '--allow-other',
                        ],
                        'kwargs': {
                            'cwd': '$homedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'fetch', 'users/dteterin/cool-branch'],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir/arcadia',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/dteterin/cool-branch',
                        ],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'reset',
                            '736be3',
                            '--hard',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                    {
                        'args': ['arc', 'rebase', 'trunk', '--force'],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                ],
                tc_report_problems_calls=[
                    {
                        'description': 'conflicts with trunk',
                        'identity': 'trunk-conflicts',
                    },
                ],
            ),
            id='conflict_with_trunk',
        ),
        pytest.param(
            Params(
                checkout_path='arcadia',
                branch='users/dteterin/cool-branch',
                commit='736be3',
                wrong_commit=True,
                arc_calls=[
                    {
                        'args': [
                            'arc',
                            'mount',
                            '--mount',
                            '$workdir/arcadia',
                            '--store',
                            '$homedir/arc/store',
                            '--object-store',
                            '$homedir/arc/object-store',
                            '--allow-other',
                        ],
                        'kwargs': {
                            'cwd': '$homedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'fetch', 'users/dteterin/cool-branch'],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir/arcadia',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/dteterin/cool-branch',
                        ],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'reset',
                            '736be3',
                            '--hard',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir/arcadia', 'env': None},
                    },
                ],
                tc_report_problems_calls=[
                    {
                        'description': 'can not reset to commit 736be3',
                        'identity': 'unknown-commit',
                    },
                ],
            ),
            id='wrong_commit',
        ),
    ],
)
def test_arc_checkout(
        params,
        commands_mock,
        patch,
        tmpdir,
        monkeypatch,
        home_dir,
        teamcity_report_problems,
):
    workdir = pathlib.PosixPath(tmpdir)
    user_home_dir = pathlib.PosixPath(home_dir)
    monkeypatch.chdir(workdir)
    arc.substitute_paths(
        params.arc_calls, {'workdir': workdir, 'homedir': user_home_dir},
    )

    @commands_mock('arc')
    def arc_mock(args, **kwargs):
        command = args[1]
        if command == 'mount':
            workdir.joinpath('.arc').mkdir(parents=True, exist_ok=True)
        if command == 'info':
            return '{"branch": "trunk"}'
        if command == 'rebase' and params.conflict_with_trunk:
            return 1
        if command == 'reset' and params.wrong_commit:
            return 1
        return 0

    @patch('taxi_buildagent.utils.clean_dir')
    def clean_dir_mock(path):
        pass

    argv = [params.checkout_path]
    if params.branch:
        argv.extend(('--branch', params.branch))
    if params.commit:
        argv.extend(('--commit', params.commit))
    if params.rebase_on_trunk or params.conflict_with_trunk:
        argv.append('--rebase-on-trunk')

    if params.conflict_with_trunk or params.wrong_commit:
        with pytest.raises(SystemExit):
            arc_checkout.main(argv)
    else:
        arc_checkout.main(argv)

    assert arc_mock.calls == params.arc_calls
    assert clean_dir_mock.calls == [
        {'path': workdir / params.checkout_path},
        {'path': user_home_dir / 'arc' / 'store'},
    ]
    assert teamcity_report_problems.calls == params.tc_report_problems_calls
