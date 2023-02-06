import itertools
import os
import pathlib
from typing import AbstractSet
from typing import Any
from typing import List
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Set

import pytest

from taxi_linters import python_linters
from taxi_linters import python_linters_config
from taxi_linters import taxi_yamlfmt


def dump(data: dict) -> Optional[str]:
    return taxi_yamlfmt.dump({'linters': data})


class Params(NamedTuple):
    targets: Set[str]
    expected_expanded: Set[str]
    file_tree: Mapping[str, Any]
    cwd: Optional[str] = None  # None - in file_tree root


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                targets={
                    'services/example/good.py',
                    'services/example2/bad.py',
                    'build/bad.py',
                    'build/bad2.py',
                },
                expected_expanded={'services/example/good.py'},
                file_tree={
                    '.git': {'.keep': ''},
                    'services': {
                        'example': {'__init__.py': '', 'good.py': ''},
                        'example2': {
                            '__init__.py': '',
                            'bad.py': '',
                            'service.yaml': dump(
                                {'disable-paths-wildcards': ['bad.py']},
                            ),
                        },
                        '__init__.py': '',
                    },
                    'services.yaml': dump(
                        {'disable-paths-wildcards': ['build/*']},
                    ),
                    'build': {'__init__.py': '', 'bad.py': '', 'bad2.py': ''},
                },
            ),
            id='file_in_exceptions_but_in_targets_explicitly_'
            'still_bad_and_this_is_smart_param_case_too',
        ),
        pytest.param(
            Params(
                targets={'.'},
                expected_expanded={
                    'services/example/good.py',
                    'services/__init__.py',
                },
                file_tree={
                    'services': {
                        'example': {'good.py': ''},
                        'example2': {
                            'bad.py': '',
                            'service.yaml': dump(
                                {'disable-paths-wildcards': ['bad.py']},
                            ),
                        },
                        '__init__.py': '',
                    },
                    'services.yaml': dump(
                        {'disable-paths-wildcards': ['build/*']},
                    ),
                    'build': {'__init__.py': '', 'bad.py': '', 'bad2.py': ''},
                },
            ),
            id='not_git_repo',
        ),
    ],
)
def test_files_searching(params: Params, make_dir_tree, tmp_path, monkeypatch):
    curdir = tmp_path
    if params.cwd is not None:
        curdir = tmp_path / params.cwd
    make_dir_tree(params.file_tree, tmp_path)
    monkeypatch.chdir(curdir)

    expanded = itertools.chain.from_iterable(
        file_group.files
        for file_group in python_linters_config.get_filegroups_for_linters(
            {pathlib.Path(target).resolve() for target in params.targets},
        )
    )
    assert sorted(expanded) == sorted(
        os.path.abspath(expected) for expected in params.expected_expanded
    )


class ParamsPath(NamedTuple):
    targets: List[str]
    expected_disabled_plugins: List[Mapping[str, AbstractSet[str]]]
    file_tree: Mapping[str, Any]


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            ParamsPath(
                targets=['services/sub_dir/file3.py', 'file1.py'],
                expected_disabled_plugins=[
                    {'flake8': {'E401'}},
                    {'flake8': {'E401'}},
                ],
                file_tree={
                    '.git': {'.keep': ''},
                    'services.yaml': dump(
                        {'disable_plugins': {'flake8': {'E401'}}},
                    ),
                    'file1.py': '',
                    'services': {'sub_dir': {'file3.py': ''}},
                },
            ),
            id='disabled_plugins_from_root_are_visible_at_top',
        ),
        pytest.param(
            ParamsPath(
                targets=['services/sub_dir/file3.py', 'file1.py'],
                expected_disabled_plugins=[{'flake8': {'E401'}}, {}],
                file_tree={
                    '.git': {'.keep': ''},
                    'file1.py': '',
                    'services': {
                        'service.yaml': dump(
                            {'disable_plugins': {'flake8': ['E401']}},
                        ),
                        'sub_dir': {'file3.py': ''},
                    },
                },
            ),
            id='disabled_plugins_from_parent_are_visible_at_top',
        ),
        pytest.param(
            ParamsPath(
                targets=['services/sub_dir/file3.py', 'services/file2.py'],
                expected_disabled_plugins=[{'flake8': {'E401'}}, {}],
                file_tree={
                    '.git': {'.keep': ''},
                    'services': {
                        'file2.py': '',
                        'sub_dir': {
                            'linters.yaml': dump(
                                {'disable_plugins': {'flake8': ['E401']}},
                            ),
                            'file3.py': '',
                        },
                    },
                },
            ),
            id='disabled_plugins_from_top_are_visible_at_top',
        ),
        pytest.param(
            ParamsPath(
                targets=['services/sub_dir/sub_dir/file4.py', 'file1.py'],
                expected_disabled_plugins=[
                    {'flake8': {'I100', 'F401', 'E703', 'E401'}},
                    {'flake8': {'E401'}},
                ],
                file_tree={
                    '.git': {'.keep': ''},
                    'services.yaml': dump(
                        {'disable_plugins': {'flake8': ['E401']}},
                    ),
                    'file1.py': '',
                    'services': {
                        'service.yaml': dump(
                            {'disable_plugins': {'flake8': ['E703']}},
                        ),
                        'file2.py': '',
                        'sub_dir': {
                            'library.yaml': dump(
                                {'disable_plugins': {'flake8': ['F401']}},
                            ),
                            'file3.py': '',
                            'sub_dir': {
                                'linters.yaml': dump(
                                    {'disable_plugins': {'flake8': ['I100']}},
                                ),
                                'file4.py': '',
                            },
                        },
                    },
                },
            ),
            id='disabled_plugins_from_all_path_are_visible_at_top',
        ),
        pytest.param(
            ParamsPath(
                targets=[
                    'service1/sub_dir/file3.py',
                    'service2/sub_dir/file3.py',
                ],
                expected_disabled_plugins=[
                    {'flake8': {'I100', 'E703', 'E401'}},
                    {'flake8': {'W292', 'F401', 'E401'}},
                ],
                file_tree={
                    '.git': {'.keep': ''},
                    'services.yaml': dump(
                        {'disable_plugins': {'flake8': ['E401']}},
                    ),
                    'file1.py': '',
                    'service1': {
                        'service.yaml': dump(
                            {'disable_plugins': {'flake8': ['E703']}},
                        ),
                        'file2.py': '',
                        'sub_dir': {
                            'library.yaml': dump(
                                {'disable_plugins': {'flake8': ['I100']}},
                            ),
                            'file3.py': '',
                        },
                    },
                    'service2': {
                        'service.yaml': dump(
                            {'disable_plugins': {'flake8': ['F401']}},
                        ),
                        'file2.py': '',
                        'sub_dir': {
                            'library.yaml': dump(
                                {'disable_plugins': {'flake8': ['W292']}},
                            ),
                            'file3.py': '',
                        },
                    },
                },
            ),
            id='disabled_plugins_are_visible_only_from_self_branch',
        ),
        pytest.param(
            ParamsPath(
                targets=[
                    'services/sub_dir/sub_dir/file4.py',
                    'services/file2.py',
                ],
                expected_disabled_plugins=[
                    {'flake8': {'I100', 'F401', 'E703'}},
                    {'flake8': {'E703'}},
                ],
                file_tree={
                    '.git': {'.keep': ''},
                    'services.yaml': dump(
                        {'disable_plugins': {'flake8': ['E401']}},
                    ),
                    'file1.py': '',
                    'services': {
                        '.git': {'.keep': ''},
                        'service.yaml': dump(
                            {'disable_plugins': {'flake8': ['E703']}},
                        ),
                        'file2.py': '',
                        'sub_dir': {
                            'library.yaml': dump(
                                {'disable_plugins': {'flake8': ['F401']}},
                            ),
                            'file3.py': '',
                            'sub_dir': {
                                'linters.yaml': dump(
                                    {'disable_plugins': {'flake8': ['I100']}},
                                ),
                                'file4.py': '',
                            },
                        },
                    },
                },
            ),
            id='disabled_plugins_are_visible_till_git_root',
        ),
    ],
)
def test_readings_all_configs(
        params: ParamsPath, make_dir_tree, tmp_path, monkeypatch,
):
    curdir = tmp_path
    make_dir_tree(params.file_tree, tmp_path)
    monkeypatch.chdir(curdir)

    for expected, target in zip(
            params.expected_disabled_plugins, params.targets,
    ):
        result = python_linters_config.get_filegroups_for_linters(
            {pathlib.Path(target).resolve()},
        )
        assert expected == result[-1].merged_config.disable_plugins


class MypyParams(NamedTuple):
    env: Mapping[str, Any]
    file_tree: Mapping[str, Any]
    is_lint_error: bool
    final_result: python_linters.LintResult


# pylint: disable=no-value-for-parameter
CACHE_ERROR_RESULT = python_linters.LintResult(
    ret_code=1,
    command='',
    output="""
Traceback (most recent call last):
  File "/usr/lib/yandex/taxi-py3-2/bin/mypy", line 8, in <module>
    sys.exit(console_entry())
  File "/usr/lib/yandex/taxi-py3-2/lib/python3.7/
  site-packages/mypy/__main__.py", line 8, in console_entry
    main(None, sys.stdout, sys.stderr)
  File "mypy/main.py", line 89, in main
  File "mypy/build.py", line 180, in build
  File "mypy/build.py", line 249, in _build
  File "mypy/build.py", line 2649, in dispatch
  File "mypy/build.py", line 2949, in process_graph
  File "mypy/build.py", line 3027, in process_fresh_modules
  File "mypy/build.py", line 1954, in fix_cross_refs
  File "mypy/fixup.py", line 25, in fixup_module
  File "mypy/fixup.py", line 76, in visit_symbol_table
  File "mypy/fixup.py", line 299, in lookup_qualified_stnode
  File "mypy/lookup.py", line 47, in lookup_fully_qualified
AssertionError: Cannot find component 'mock_ridehistory' for
'taxi_shared_payments.generated.service.clients.pytest_plugin.mock_ridehistory'
""",
    linter=python_linters.MyPy,
)


REGULAR_ERROR_RESULT = python_linters.LintResult(
    ret_code=1,
    command='',
    output=(
        'magic_wand/models/models.py:361:12: '
        '[Pylint: W0612(unused-variable), MyPy.execute_process] '
        'Unused variable'
    ),
    linter=python_linters.MyPy,
)


OK_RESULT = python_linters.LintResult(
    ret_code=0, command='', output='', linter=python_linters.MyPy,
)


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            MypyParams(
                file_tree={
                    '.git': {'.keep': ''},
                    '.mypy_cache': {'bad_cache.json': 'BAD'},
                    'services': {
                        'magic_wand': {
                            'service.yaml': '{}',
                            'magic_wand': {
                                '__init__.py': '',
                                'some.py': '',
                                'models': {'__init__.py': '', 'models.py': ''},
                            },
                        },
                    },
                },
                env={},
                is_lint_error=False,
                final_result=CACHE_ERROR_RESULT,
            ),
            id='typical_cache_error_case',
        ),
        pytest.param(
            MypyParams(
                file_tree={
                    '.git': {'.keep': ''},
                    '.mypy_cache': {'bad_cache.json': 'BAD'},
                    'services': {
                        'magic_wand': {
                            'service.yaml': '{}',
                            'magic_wand': {
                                '__init__.py': '',
                                'some.py': '',
                                'models': {'__init__.py': '', 'models.py': ''},
                            },
                        },
                    },
                },
                env={},
                is_lint_error=True,
                final_result=CACHE_ERROR_RESULT,
            ),
            id='typical_cache_error_case_with_regular_error',
        ),
        pytest.param(
            MypyParams(
                file_tree={
                    '.git': {'.keep': ''},
                    'special_for_cache': {
                        '.mypy_cache': {'bad_cache.json': 'BAD'},
                    },
                    'services': {
                        'magic_wand': {
                            'service.yaml': '{}',
                            'magic_wand': {
                                '__init__.py': '',
                                'some.py': '',
                                'models': {'__init__.py': '', 'models.py': ''},
                            },
                        },
                    },
                },
                env={'MYPY_CACHE_DIR': 'special_for_cache/.mypy_cache'},
                is_lint_error=False,
                final_result=OK_RESULT,
            ),
            id='typical_cache_error_case_with_env_cache_path',
        ),
        pytest.param(
            MypyParams(
                file_tree={
                    '.git': {'.keep': ''},
                    'special_for_cache': {
                        '.mypy_cache': {'bad_cache.json': 'BAD'},
                    },
                    'services': {
                        'magic_wand': {
                            'service.yaml': '{}',
                            'magic_wand': {
                                '__init__.py': '',
                                'some.py': '',
                                'models': {'__init__.py': '', 'models.py': ''},
                            },
                        },
                    },
                },
                env={'MYPY_CACHE_DIR': 'special_for_cache/.mypy_cache'},
                is_lint_error=True,
                final_result=REGULAR_ERROR_RESULT,
            ),
            id='typical_cache_error_case_with_env_cache_path_and_lint_error',
        ),
        pytest.param(
            MypyParams(
                file_tree={
                    '.git': {'.keep': ''},
                    '.mypy_cache': {'good_cache.json': 'GOOD'},
                    'services': {
                        'magic_wand': {
                            'service.yaml': '{}',
                            'magic_wand': {
                                '__init__.py': '',
                                'some.py': '',
                                'models': {'__init__.py': '', 'models.py': ''},
                            },
                        },
                    },
                },
                env={},
                is_lint_error=False,
                final_result=OK_RESULT,
            ),
            id='no_cache_errors',
        ),
    ],
)
def test_mypy_cache_delete(
        params: MypyParams, make_dir_tree, tmp_path, monkeypatch,
):
    def _mock_execute_process(
            process_data: python_linters.ProcessData,
    ) -> python_linters.LintResult:
        cache_dir = pathlib.Path(
            process_data.env.get(
                python_linters.MyPy.cache_dir_var,
                pathlib.Path.cwd() / '.mypy_cache',
            ),
        )
        cache_dir.mkdir(exist_ok=True, parents=True)
        if not os.listdir(cache_dir):
            (cache_dir / 'good_cache.json').write_text('GOOD')
        if 'good_cache.json' in os.listdir(cache_dir):
            if params.is_lint_error:
                return REGULAR_ERROR_RESULT
            return OK_RESULT
        if (cache_dir / 'bad_cache.json').exists():
            return CACHE_ERROR_RESULT
        return OK_RESULT

    monkeypatch.setattr(
        python_linters.Linter, 'execute_process', _mock_execute_process,
    )

    curdir = tmp_path
    make_dir_tree(params.file_tree, tmp_path)
    monkeypatch.chdir(curdir)

    for name, value in params.env.items():
        monkeypatch.setenv(name, value)

    filegroups = python_linters_config.get_filegroups_for_linters(
        targets={curdir},
    )

    filegroup = python_linters.MyPy.group_file_groups(filegroups)[0][0]
    result = python_linters.MyPy.run(filegroup)
    assert result == params.final_result
