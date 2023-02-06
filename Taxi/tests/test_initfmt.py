import pathlib
from typing import Any
from typing import List
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Set

import pytest

from taxi_linters import taxi_initfmt
from taxi_linters import utils


RICH_TREE = {
    '.git': {'.keep': ''},
    'submodules': {
        'submodule1': {
            '.git': {'.keep': ''},
            'testsuite_dir': {
                '__init__.py': '',
                'file.py': '',
                'dir': {'__main__.py': ''},
            },
            'subsubmodule': {
                'codegen': {
                    '.git': {'.keep': ''},
                    's_th.py': '',
                    '__init__.py': '',
                    'dir': {'__main__.py': ''},
                },
            },
        },
    },
    'services': {
        'service1': {
            'dir_wo_py': {'dir': {'file.yaml': ''}, 'control': ''},
            'dir_wo_init': {
                'dir': {'file.py': ''},
                'dir_wo_py': {'file.yaml': ''},
                'file.py': '',
            },
            'dir_with_init': {
                '__init__.py': '',
                'dir_with_init': {'__init__.py': '', 'file.py': ''},
                'dir_wo_init': {'file.py': ''},
                'dir_wo_py': {'file.yaml': ''},
                'dir_with_subdir1': {'dir': {'file.py': ''}},
                'dir_with_subdir2': {'file.py': '', 'dir': {'file.yaml': ''}},
                'dir_with_subdir3': {'file.py': '', 'dir': {'file.py': ''}},
                'dir_init_a': {'__init__.py': 'a'},
                'dir_with_pyi': {
                    '__init__.pyi': '',
                    'dir': {'__file__.py': ''},
                },
            },
        },
        'service_under_ignore': {
            'dir': {'__init__.py': '', 'dir': {'file.py': ''}},
        },
    },
    'services.yaml': (
        'linters:\n'
        '  initfmt:\n'
        '    disable-paths-wildcards:\n'
        '    - services/service_under_ignore/*\n'
    ),
}


class Params(NamedTuple):
    targets: List[str]
    added: Set[str]
    file_tree: Mapping[str, Any]
    unchanged_init: Optional[str] = None


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                targets=['.'],
                added={'dir/'},
                file_tree={
                    '.git': {'.keep': ''},
                    '__init__.py': '',
                    'dir': {'file.py': ''},
                },
            ),
            id='simple_case',
        ),
        pytest.param(
            Params(
                targets=['.'],
                added=set(),
                file_tree={
                    '.git': {'.keep': ''},
                    '__init__.py': '',
                    'submodule': {
                        '.git': {'.keep': ''},
                        '__init__.py': '',
                        'dir': {'file.py': ''},
                    },
                    'dir': {'__main__.py': ''},
                    'dir2': {'__init__.py': ''},
                    'services.yaml': (
                        'linters:\n'
                        '  initfmt:\n'
                        '    disable-paths-wildcards:\n'
                        '    - dir/*\n'
                    ),
                },
            ),
            id='no_added_files',
        ),
        pytest.param(
            Params(
                targets=['.'],
                added={
                    'services/service1/dir_with_init/dir_wo_init/',
                    'services/service1/dir_with_init/dir_with_subdir1/',
                    'services/service1/dir_with_init/dir_with_subdir1/dir/',
                    'services/service1/dir_with_init/dir_with_subdir2/',
                    'services/service1/dir_with_init/dir_with_subdir3/',
                    'services/service1/dir_with_init/dir_with_subdir3/dir/',
                    'services/service1/dir_with_init/dir_with_pyi/',
                    'services/service1/dir_with_init/dir_with_pyi/dir/',
                },
                file_tree=RICH_TREE,
                unchanged_init='services/service1/dir_with_init/dir_init_a',
            ),
            id='hard_case',
        ),
        pytest.param(
            Params(
                targets=[
                    'services/service1/dir_with_init/'
                    'dir_with_subdir3/dir/file.py',
                    'services/service1/dir_with_init/dir_wo_init/',
                ],
                added={
                    'services/service1/dir_with_init/dir_with_subdir3/',
                    'services/service1/dir_with_init/dir_with_subdir3/dir/',
                    'services/service1/dir_with_init/dir_wo_init/',
                },
                file_tree=RICH_TREE,
                unchanged_init='services/service1/dir_with_init/dir_init_a',
            ),
            id='several_targets',
        ),
    ],
)
def test_initfmt(params: Params, make_dir_tree, tmp_path, monkeypatch):
    curdir = tmp_path
    make_dir_tree(params.file_tree, tmp_path)
    monkeypatch.chdir(curdir)

    # pylint: disable=protected-access
    args = taxi_initfmt._parse_argv(params.targets)
    files_by_groups = utils.collect_file_groups_single_fmt(
        taxi_initfmt.NAME, taxi_initfmt.SUFFIXES, args,
    )
    files = utils.files_from_all_groups(files_by_groups)

    all_added: Set[pathlib.Path] = set()
    for _file in files:
        all_added.update(
            taxi_initfmt._format_init(_file.relative_to(curdir).parents)[0],
        )

    if params.unchanged_init:
        filepath = pathlib.Path(params.unchanged_init, '__init__.py')
        assert filepath.read_text() == 'a'

    assert {
        pathlib.Path(_file, '__init__.py') for _file in params.added
    } == all_added
