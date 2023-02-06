import pathlib
from typing import Any
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Set

import pytest

from taxi_linters import check_symlinks


class Params(NamedTuple):
    targets: Set[str]
    expected_output: str
    return_code: int
    file_tree: Mapping[str, Any]
    need_format_paths_in_output: bool = False
    cwd: Optional[str] = None  # None - in file_tree root


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                targets={'.'},
                expected_output='Symlinks not found',
                return_code=0,
                file_tree={
                    '.git': {'.keep': ''},
                    'good.yaml': '',
                    'bad.yaml': '',
                },
            ),
            id='simple_case_ok',
        ),
        pytest.param(
            Params(
                targets={'.'},
                expected_output='good.symlink',
                return_code=1,
                file_tree={
                    '.git': {'.keep': ''},
                    'bad.yaml': '',
                    'good.symlink': 'bad.yaml',
                },
            ),
            id='have_symlink',
        ),
        pytest.param(
            Params(
                targets={'.'},
                expected_output='submodules/lol_link_wat.symlink',
                return_code=1,
                file_tree={
                    '.git': {'.keep': ''},
                    'submodules': {
                        'testsuite': {
                            '.git': {'.keep': ''},
                            'testsuite_dir': {
                                'another_testsuite.yaml': '',
                                'some_py_file.py': '',
                            },
                            'some_testsuite.yaml': '',
                        },
                        'lol_link_wat.symlink': 'testsuite',
                    },
                    'good.yaml': '',
                },
            ),
            id='link_on_submodule',
        ),
        pytest.param(
            Params(
                targets={'.'},
                expected_output='Found 2 symlink(s):\n'
                '- {root_path}/submodules/lol_link_wat.symlink\n'
                '- {root_path}/submodules/lol_link_wat2.symlink\n',
                need_format_paths_in_output=True,
                return_code=1,
                file_tree={
                    '.git': {'.keep': ''},
                    'submodules': {
                        'testsuite': {
                            '.git': {'.keep': ''},
                            'testsuite_dir': {
                                'another_testsuite.yaml': '',
                                'some_py_file.py': '',
                            },
                            'some_testsuite.yaml': '',
                        },
                        'lol_link_wat.symlink': 'testsuite',
                        'lol_link_wat2.symlink': '../bad.yaml',
                    },
                    'good.yaml': '',
                    'bad.yaml': '',
                },
            ),
            id='links_in_submodule_format',
        ),
        pytest.param(
            Params(
                targets={'.'},
                expected_output='Symlinks not found',
                return_code=0,
                file_tree={
                    '.git': {'.keep': ''},
                    'submodules': {
                        'testsuite': {
                            '.git': {'.keep': ''},
                            'testsuite_dir': {
                                'another_testsuite.yaml': '',
                                'lol_link_wat.symlink': (
                                    'another_testsuite.yaml'
                                ),
                            },
                            'some_testsuite.yaml': '',
                            'some_testsuite.yaml.symlink': (
                                'some_testsuite.yaml'
                            ),
                        },
                    },
                    'good.yaml': '',
                },
            ),
            id='link_in_submodule_meh',
        ),
    ],
)
def test_symlinks(
        params: Params, make_dir_tree, tmp_path, monkeypatch, capsys,
):
    curdir = tmp_path
    if params.cwd is not None:
        curdir = tmp_path / params.cwd
    make_dir_tree(params.file_tree, tmp_path)
    monkeypatch.chdir(curdir)

    path_targets = {pathlib.Path(target) for target in params.targets}

    # pylint: disable=protected-access
    ret_code = check_symlinks._collect_symlinks(path_targets)
    assert ret_code == params.return_code

    captured = capsys.readouterr()
    expected_output = params.expected_output
    if params.need_format_paths_in_output:
        expected_output = params.expected_output.format(root_path=curdir)
    assert expected_output in captured.out
    assert captured.err == ''
