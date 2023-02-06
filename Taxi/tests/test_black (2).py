import pathlib
from typing import Any
from typing import Iterable
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Set

import pytest

from taxi_linters import taxi_black
from taxi_linters import utils


class Params(NamedTuple):
    targets: Set[str]
    expected_expanded: Set[str]
    file_tree: Mapping[str, Any]
    cwd: Optional[str] = None  # None - in file_tree root
    smart: bool = False


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                targets={'good.py'},
                expected_expanded={'good.py'},
                file_tree={'.git': {'.keep': ''}, 'good.py': '', 'bad.py': ''},
            ),
            id='simple_case',
        ),
        pytest.param(
            Params(
                targets={
                    'services/example/good.py',
                    'services/example2/good2.py',
                    'build/bad.py',
                    'build/bad2.py',
                },
                expected_expanded={
                    'services/example/good.py',
                    'services/example2/good2.py',
                    'build/bad.py',
                    'build/bad2.py',
                },
                file_tree={
                    '.git': {'.keep': ''},
                    'services': {
                        'example': {'good.py': ''},
                        'example2': {'good2.py': ''},
                    },
                    'build': {'bad.py': '', 'bad2.py': ''},
                },
            ),
            id='files_in_exceptions_dont_filter_on_wrapper_layer',
        ),
        pytest.param(
            Params(
                targets={
                    'services/example/good.py',
                    'services/example2/good2.py',
                    'build/bad.py',
                    'build/bad2.py',
                },
                expected_expanded={
                    'services/example/good.py',
                    'services/example2/good2.py',
                },
                smart=True,
                file_tree={
                    '.git': {'.keep': ''},
                    'services': {
                        'example': {'good.py': ''},
                        'example2': {'good2.py': ''},
                    },
                    'build': {'bad.py': '', 'bad2.py': ''},
                },
            ),
            id='files_in_exceptions_filter_on_wrapper_layer_smart',
        ),
    ],
)
def test_files_searching(params: Params, make_dir_tree, tmp_path, monkeypatch):
    curdir = tmp_path
    if params.cwd is not None:
        curdir = tmp_path / params.cwd
    make_dir_tree(params.file_tree, tmp_path)
    monkeypatch.chdir(curdir)

    targets: Set[pathlib.Path] = {
        pathlib.Path(target) for target in params.targets
    }
    expanded: Iterable[pathlib.Path]
    # pylint: disable=protected-access
    if params.smart:

        def mock_get_changed_files(*args, **kwargs):
            return params.targets

        monkeypatch.setattr(utils, 'get_changed_files', mock_get_changed_files)
        expanded = taxi_black._collect_smart_targets(targets)
    else:
        expanded = taxi_black._collect_targets_by_version(targets)[
            taxi_black.CURRENT_VERSION
        ]
    assert sorted(expanded) == sorted(
        [pathlib.Path(target) for target in params.expected_expanded],
    )
