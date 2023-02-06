import os
import pathlib
from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Set
from typing import Union

import pytest

from taxi_linters import taxi_format

SUFFIXES = {
    'yaml': '.yaml',
    'json': '.json',
    'eol': '.cpp',
    'black': '.py',
    'clang': '.cpp',
}
FILES = {
    'yaml': dict(unformatted='a:a\n', formatted='a: a\n', error='a: a:\n'),
    'json': dict(unformatted='{ }\n', formatted='{}\n', error='{}{}\n'),
    'eol': dict(unformatted='a', formatted='a\n', error=''),
    'black': dict(unformatted='a \n', formatted='a\n', error=' a\n'),
    'clang': dict(unformatted='}}\n', formatted='}\n}\n'),
}


def content(*statuses: str, prefix: str = '', git: bool = False):
    structure: Dict[str, Union[str, dict]] = dict()
    for status in statuses:
        for fmt, sfx in SUFFIXES.items():
            prefix = prefix + '_' if prefix else prefix
            if status in FILES[fmt]:
                structure[prefix + status + sfx] = FILES[fmt][status]
    if git:
        structure['.git'] = {'.keep': ''}
    return structure


def ignore_list(**formatters):
    config = 'linters:\n'
    for fmt, ignores in formatters.items():
        config += f'    {fmt}:\n'
        config += f'        disable-paths-wildcards:\n'
        for ignore in ignores:
            config += f'          - {ignore}\n'
    return config


def files(*not_presented: str, suf_dir: str = '', status: str = 'unformatted'):
    return {
        pathlib.Path(suf_dir, status + sfx)
        for fmt, sfx in SUFFIXES.items()
        if fmt not in not_presented
    }


SIMPLE_TREE = {
    **content('unformatted', 'formatted', git=True),
    'bad': content('unformatted', 'formatted'),
    'good': content('formatted'),
    '.gitignore': '/bad',
    'subdir': {'bad': content('unformatted', 'formatted')},
    'submodule': content('unformatted', git=True),
}


class Params(NamedTuple):
    file_tree: Mapping[str, Any]
    changed_files: Set[pathlib.Path]
    checking_dirs: List[str] = ['.']
    launch_dir: pathlib.Path = pathlib.Path('.')
    files_in_diff: Set[pathlib.Path] = set()
    args: List[str] = []
    errors: Optional[Set[str]] = None
    output_file: Optional[pathlib.Path] = None


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                file_tree={
                    **content('unformatted', 'formatted'),
                    'tmp': content('unformatted', 'formatted'),
                },
                changed_files=files() | files(suf_dir='tmp'),
            ),
            id='simple_format_all_files',
        ),
        pytest.param(
            Params(
                file_tree={
                    **SIMPLE_TREE,
                    'services.yaml': ignore_list(yamlfmt=['bad/*']),
                },
                changed_files=files('json', 'eol', 'black', 'clang')
                | files('json', 'eol', 'black', 'clang', suf_dir='subdir/bad'),
                args=['-F', 'yamlfmt'],
            ),
            id='one_formatter',
        ),
        pytest.param(
            Params(
                file_tree={
                    'file.not_existed': 'no_newline1',
                    'dir': {
                        'file.txt': 'no_newline2',
                        'file.not_existed': 'no_newline3',
                    },
                },
                checking_dirs=['file.not_existed', 'dir'],
                changed_files={
                    pathlib.Path('file.not_existed'),
                    pathlib.Path('dir/file.txt'),
                },
                args=['-F', 'eolfmt'],
            ),
            id='one_formatter_format_file_with_other_suffix',
        ),
        pytest.param(
            Params(
                file_tree=SIMPLE_TREE,
                changed_files=files('json', 'eol', 'clang')
                | files('json', 'eol', 'black', 'clang', suf_dir='bad')
                | files('json', 'eol', 'clang', suf_dir='subdir/bad'),
                args=['-F', 'yamlfmt', 'black'],
            ),
            id='yamlfmt_and_black_formatters',
        ),
        pytest.param(
            Params(
                file_tree={
                    **content('formatted', git=True),
                    'submodule': content('unformatted', git=True),
                    'bad': content('unformatted', 'formatted'),
                    '.gitignore': 'bad',
                    '.git': content('unformatted'),
                    'services.yaml': ignore_list(
                        **{
                            'yamlfmt': ['bad/*'],
                            'jsonfmt': ['bad/*'],
                            'eolfmt': ['bad/*'],
                            'clang-format': ['bad/*'],
                        },
                    ),
                },
                changed_files=set(),
            ),
            id='no_files_to_format',
        ),
        pytest.param(
            Params(
                file_tree={**SIMPLE_TREE, 'subdir': {}},
                checking_dirs=['.', 'submodule'],
                changed_files=files()
                | files('black', suf_dir='bad')
                | files(suf_dir='submodule'),
            ),
            id='some_targets',
        ),
        pytest.param(
            Params(
                file_tree=content('unformatted', 'error'),
                changed_files=files(),
                errors=files(status='error'),
            ),
            id='some_errors',
        ),
        pytest.param(
            Params(
                file_tree={
                    **SIMPLE_TREE,
                    'scripts': {'__init__.py': ''},
                    'userver': {
                        'scripts': {'docs': {'download.py': ''}},
                        'services.yaml': 'linters: {}\n',
                    },
                },
                changed_files=set(),
                checking_dirs=['userver'],
            ),
            id='initfmt_target_error',
        ),
        pytest.param(
            Params(
                file_tree={
                    **content('unformatted', 'formatted', git=True),
                    'subdir': content('unformatted', 'formatted'),
                },
                changed_files=files(suf_dir='subdir'),
                launch_dir=pathlib.Path('subdir'),
                files_in_diff=files(),
                args=['--smart'],
            ),
            id='smart_in_subdir',
        ),
        pytest.param(
            Params(
                file_tree={
                    **content('unformatted', 'formatted', git=True),
                    '__init__.py': '',
                    'tmp': content('unformatted', 'formatted'),
                },
                changed_files=files() | {pathlib.Path('tmp/__init__.py')},
                files_in_diff=files(),
                args=['--smart', '--teamcity'],
            ),
            id='smart_in_teamcity',
        ),
        pytest.param(
            Params(
                file_tree={**content('formatted'), 'services.yaml': ''},
                changed_files=set(),
            ),
            id='empty_service.yaml',
        ),
    ],
)
def test_formatting(params: Params, make_dir_tree, tmp_path, monkeypatch):
    workdir = tmp_path / 'working_dir'
    cmpdir = tmp_path / 'cmp_dir'
    make_dir_tree(params.file_tree, workdir)
    make_dir_tree(params.file_tree, cmpdir)
    monkeypatch.chdir(workdir / params.launch_dir)
    monkeypatch.setenv('TAXI_SMART_ROOT', '')

    for file_in_diff in params.files_in_diff:
        with (workdir / params.launch_dir / file_in_diff).open(
                'a',
        ) as file_for_change:
            file_for_change.write(' ')
        with (cmpdir / params.launch_dir / file_in_diff).open(
                'a',
        ) as file_for_change:

            file_for_change.write(' ')

    # pylint: disable=protected-access
    result = taxi_format._main([*params.args, '--', *params.checking_dirs])

    for changed_file in params.changed_files:
        assert changed_file.relative_to(
            params.launch_dir,
        ).exists(), f'File {changed_file} from changed_files not exist'

    for top, _, nondirs in os.walk(workdir):
        if '/.git' in top:
            continue

        cmp_root = top.replace('working_dir', 'cmp_dir')
        for file in nondirs:
            check_file = pathlib.Path(top, file)
            cmp_file = pathlib.Path(cmp_root, file)

            if check_file.relative_to(workdir) not in params.changed_files:
                assert cmp_file.read_text() == check_file.read_text()
            elif cmp_file.exists():
                assert cmp_file.read_text() != check_file.read_text()

    if params.errors:
        assert result
    else:
        assert not result
