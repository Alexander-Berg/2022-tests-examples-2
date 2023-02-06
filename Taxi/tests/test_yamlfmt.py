import collections
import pathlib
import shutil
import textwrap
from typing import Any
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Set

import pytest

from taxi_linters import taxi_yamlfmt
from taxi_linters import utils

TEST_DATA_DIR = pathlib.Path(__file__).parent / 'static' / 'yaml'
SEVERAL_DOC_NOT_FORMATTED = (
    TEST_DATA_DIR / 'several_docs' / 'not_formatted.yaml'
)
SEVERAL_DOC_FORMATTED = TEST_DATA_DIR / 'several_docs' / 'formatted.yaml'
SEVERAL_DOC_EDITED = TEST_DATA_DIR / 'several_docs' / 'edited.yaml'
PARAMS_TEST_DIR = list(
    zip(
        sorted((TEST_DATA_DIR / 'before').rglob('*')),
        sorted((TEST_DATA_DIR / 'after').rglob('*')),
        sorted((TEST_DATA_DIR / 'edited').rglob('*')),
    ),
)


def edit_data(data, formatted_data=None):
    if isinstance(data, dict):
        value = {
            'my_config': {'external': False},
            'my_other_config': {'external': True},
        }
        data['volumes'] = value
        if formatted_data:
            formatted_data['volumes'] = value
    elif isinstance(data, list):
        data.append(2)
        if formatted_data:
            formatted_data.append(2)


@pytest.mark.parametrize('file,_,edited_file', PARAMS_TEST_DIR)
def test_dump(file, _, edited_file, tmp_path):
    data = taxi_yamlfmt.load(file.read_text())
    edit_data(data)
    tmp_file = tmp_path / file.name
    taxi_yamlfmt.dump(data, tmp_file)
    assert len(list(tmp_path.iterdir())) == 1
    assert edited_file.read_text() == tmp_file.read_text()


@pytest.mark.parametrize(
    'not_formatted_file,sorted_keys_file',
    zip(
        sorted((TEST_DATA_DIR / 'before').rglob('*')),
        sorted((TEST_DATA_DIR / 'sorted').rglob('*')),
    ),
)
def test_dump_sorted(not_formatted_file, sorted_keys_file, tmp_path):
    data = taxi_yamlfmt.load(not_formatted_file.read_text())
    tmp_file = tmp_path / not_formatted_file.name
    taxi_yamlfmt.dump(data, tmp_file, sort_keys=True)
    assert len(list(tmp_path.iterdir())) == 1
    assert sorted_keys_file.read_text() == tmp_file.read_text()


@pytest.mark.parametrize(
    'test_data,expected_str',
    [
        (
            collections.defaultdict(
                collections.OrderedDict,
                {
                    4: collections.OrderedDict(
                        [
                            (2, 4),
                            (
                                1,
                                collections.OrderedDict(
                                    [
                                        ('tmp', '23'),
                                        ('abc', 2),
                                        (3, [23, 4]),
                                        (
                                            '123',
                                            collections.defaultdict(
                                                str, {6: '333'},
                                            ),
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                    '2': 'Hello\nWorld!',
                    1: 'No',
                    '1': 'Yes\n',
                    'n': 'y',
                    'on': True,
                },
            ),
            textwrap.dedent(
                """
                    4:
                        2: 4
                        1:
                            tmp: '23'
                            abc: 2
                            3:
                              - 23
                              - 4
                            '123':
                                6: '333'
                    '2': |-
                        Hello
                        World!
                    1: 'No'
                    '1': |
                        Yes
                    n: y
                    'on': true
                """.lstrip(
                    '\n',
                ),
            ),
        ),
    ],
)
def test_dump_obj(test_data, expected_str):
    data = taxi_yamlfmt.dump(test_data)

    assert expected_str == data


@pytest.mark.parametrize('file,formatted_file,_', PARAMS_TEST_DIR)
def test_dump_wo_path(file, formatted_file, _):
    data = taxi_yamlfmt.load(file)
    formatted_data = taxi_yamlfmt.dump(data)
    assert formatted_data == formatted_file.read_text()


def test_dump_all(tmp_path):
    edited_file = SEVERAL_DOC_EDITED
    data = list(taxi_yamlfmt.load_all(SEVERAL_DOC_NOT_FORMATTED.read_text()))
    for doc in data:
        edit_data(doc)
    tmp_file = tmp_path / edited_file.name
    taxi_yamlfmt.dump_all(data, tmp_file)
    assert len(list(tmp_path.iterdir())) == 1
    assert edited_file.read_text() == tmp_file.read_text()


def test_dump_all_wo_path():
    data = taxi_yamlfmt.load_all(SEVERAL_DOC_NOT_FORMATTED)
    after_format = taxi_yamlfmt.dump_all(data)
    assert after_format == SEVERAL_DOC_FORMATTED.read_text()


@pytest.mark.parametrize('file,formatted_file,_', PARAMS_TEST_DIR)
def test_load(file, formatted_file, _):
    data = taxi_yamlfmt.load(file)
    formatted_data = taxi_yamlfmt.load(formatted_file)
    assert data == formatted_data
    edit_data(data, formatted_data)
    assert data == formatted_data


@pytest.mark.parametrize('file,formatted_file,_', PARAMS_TEST_DIR)
def test_load_string(file, formatted_file, _):
    data = taxi_yamlfmt.load(file.read_text())
    formatted_data = taxi_yamlfmt.load(formatted_file.read_text())
    assert data == formatted_data
    edit_data(data, formatted_data)
    assert data == formatted_data


def test_yaml_load_all():
    data = list(taxi_yamlfmt.load_all(SEVERAL_DOC_NOT_FORMATTED))
    formatted_data = list(taxi_yamlfmt.load_all(SEVERAL_DOC_FORMATTED))
    assert data == formatted_data
    for doc_not_form, doc_form in zip(data, formatted_data):
        edit_data(doc_not_form, doc_form)
    assert data == formatted_data


def test_load_all_string():
    data = list(taxi_yamlfmt.load_all(SEVERAL_DOC_NOT_FORMATTED.read_text()))
    formatted_data = list(
        taxi_yamlfmt.load_all(SEVERAL_DOC_FORMATTED.read_text()),
    )
    assert data == formatted_data
    for doc_not_form, doc_form in zip(data, formatted_data):
        edit_data(doc_not_form, doc_form)
    assert data == formatted_data


@pytest.mark.parametrize('before,after,_', PARAMS_TEST_DIR)
def test_format_file(before, after, _, tmp_path):
    temp_copy = tmp_path / before.name
    shutil.copy(before, temp_copy)
    result = taxi_yamlfmt.format_file(temp_copy)

    # no extra files
    assert len(list(tmp_path.iterdir())) == 1

    assert after.read_text() == temp_copy.read_text()
    assert result


@pytest.mark.parametrize(
    'filename', sorted((TEST_DATA_DIR / 'after').rglob('*')),
)
def test_format_file_stable(filename, tmp_path):
    temp_copy = tmp_path / filename.name
    shutil.copy(filename, temp_copy)
    result = taxi_yamlfmt.format_file(temp_copy)

    # no extra files
    assert len(list(tmp_path.iterdir())) == 1

    assert filename.read_text() == temp_copy.read_text()
    assert not result


def test_format_file_several(tmp_path):
    before = SEVERAL_DOC_NOT_FORMATTED
    temp_copy = tmp_path / before.name
    shutil.copy(before, temp_copy)
    result = taxi_yamlfmt.format_file(temp_copy)

    # no extra files
    assert len(list(tmp_path.iterdir())) == 1

    assert SEVERAL_DOC_FORMATTED.read_text() == temp_copy.read_text()
    assert result


@pytest.mark.parametrize('file,formatted_file,_', PARAMS_TEST_DIR)
def test_format_str(file, formatted_file, _):
    data = file.read_text()
    assert formatted_file.read_text() == taxi_yamlfmt.format_str(data)


def test_format_str_several():
    data = SEVERAL_DOC_NOT_FORMATTED.read_text()
    assert SEVERAL_DOC_FORMATTED.read_text() == taxi_yamlfmt.format_str(data)


@pytest.mark.parametrize('before,after,_', PARAMS_TEST_DIR)
def test_format_yaml(before, after, _, tmp_path):
    temp_copy = tmp_path / before.name
    shutil.copy(before, temp_copy)
    # pylint: disable=protected-access
    taxi_yamlfmt._format_yaml(temp_copy)

    # no extra files
    assert len(list(tmp_path.iterdir())) == 1

    assert after.read_text() == temp_copy.read_text()


@pytest.mark.parametrize(
    'filename', sorted((TEST_DATA_DIR / 'after').rglob('*')),
)
def test_stable(filename, tmp_path):
    temp_copy = tmp_path / filename.name
    shutil.copy(filename, temp_copy)
    # pylint: disable=protected-access
    taxi_yamlfmt._format_yaml(temp_copy)

    # no extra files
    assert len(list(tmp_path.iterdir())) == 1

    assert filename.read_text() == temp_copy.read_text()


class Params(NamedTuple):
    targets: Set[str]
    expected_expanded: Set[str]
    file_tree: Mapping[str, Any]
    cwd: Optional[str] = None  # None - in file_tree root


RICH_TREE = {
    '.git': {'.keep': ''},
    'submodules': {
        'testsuite': {
            '.git': {'.keep': ''},
            'testsuite_dir': {
                'another_testsuite.yaml': '',
                'some_py_file.py': '',
            },
            'submodules': {
                'codegen': {
                    '.git': {'.keep': ''},
                    'codegen_in_testsuite.yml': '',
                },
            },
            'services.yaml': (
                'linters:\n'
                '  yamlfmt:\n'
                '    disable-paths-wildcards:\n'
                '    - services.yaml\n'
            ),
            'some_testsuite.yaml': '',
        },
        'ml': {
            '.git': {'.keep': ''},
            'ml_dir': {'another_ml.yaml': '', 'some_py_file.py': ''},
            'submodules': {
                'ml_deps': {'.git': {'.keep': ''}, 'ml_deps_in_ml.yml': ''},
            },
            'services.yaml': (
                'linters:\n'
                '  yamlfmt:\n'
                '    disable-paths-wildcards:\n'
                '    - services.yaml\n'
                '    - disabled_in_ml.yaml\n'
            ),
            'some_ml.yaml': '',
            'disabled_in_ml.yaml': '',
            'disabled_in_root.yaml': '',
        },
        'format_this_in_subdir.yml': '',
    },
    'simple_dirs': {
        'schemas': {'good_schema.yaml': ''},
        'trash_yamls': {'bad_yml.yaml': ''},
    },
    'services.yaml': (
        'linters:\n'
        '  yamlfmt:\n'
        '    disable-paths-wildcards:\n'
        '    - services.yaml\n'
        '    - disabled_in_root.yaml\n'
        '    - simple_dirs/trash_yamls/*\n'
    ),
    'disabled_in_ml.yaml': '',
    'disabled_in_root.yaml': '',
    'good.yaml': '',
}


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                targets={'good.yaml'},
                expected_expanded={'good.yaml'},
                file_tree={
                    '.git': {'.keep': ''},
                    'good.yaml': '',
                    'bad.yaml': '',
                },
            ),
            id='simple_case',
        ),
        pytest.param(
            Params(
                targets={'good.yaml'},
                expected_expanded={'good.yaml'},
                file_tree={'good.yaml': '', 'bad.yaml': ''},
            ),
            id='file_not_in_repo',
        ),
        pytest.param(
            Params(
                targets={'good.yaml', 'exception.yml'},
                expected_expanded={'good.yaml'},
                file_tree={
                    '.git': {'.keep': ''},
                    'services.yaml': (
                        'linters:\n'
                        '  yamlfmt:\n'
                        '    disable-paths-wildcards:\n'
                        '    - exception.yml\n'
                    ),
                    'good.yaml': '',
                    'exception.yml': '',
                    'bad.yaml': '',
                },
            ),
            id='file_in_exceptions_but_in_targets_explicitly_'
            'still_bad_and_this_is_smart_param_case_too',
        ),
        pytest.param(
            Params(
                targets={'.'},
                expected_expanded={'good.yaml'},
                file_tree={
                    '.git': {'.keep': ''},
                    'services.yaml': (
                        'linters:\n'
                        '  yamlfmt:\n'
                        '    disable-paths-wildcards:\n'
                        '    - bad.yml\n'
                        '    - super*\n'
                        '    - services.yaml\n'
                    ),
                    'good.yaml': '',
                    'bad.yml': '',
                    'super_bad.yaml': '',
                },
            ),
            id='files_in_exceptions',
        ),
        pytest.param(
            Params(
                cwd='trash_yamls',
                targets={'../schemas/good.yaml'},
                expected_expanded={'../schemas/good.yaml'},
                file_tree={
                    'schemas': {'good.yaml': ''},
                    'trash_yamls': {'bad.yaml': ''},
                },
            ),
            id='file_not_in_repo_and_curdir_is_somewhere',
        ),
        pytest.param(
            Params(
                targets={'.'},
                expected_expanded={'good.yaml', 'bad.yaml'},
                file_tree={
                    '.git': {'.keep': ''},
                    'good.yaml': '',
                    'bad.yaml': '',
                },
            ),
            id='simple_case_gather',
        ),
        pytest.param(
            Params(
                targets={'.'},
                cwd='subdir',
                expected_expanded={'in_dir.yaml'},
                file_tree={
                    '.git': {'.keep': ''},
                    'subdir': {'in_dir.yaml': ''},
                    'bad1.yaml': '',
                    'bad2.yaml': '',
                },
            ),
            id='simple_case_from_subdir',
        ),
        pytest.param(
            Params(
                targets={'extra_subdir'},
                cwd='subdir',
                expected_expanded={
                    'extra_subdir/in_extra_subdir.yml',
                    'extra_subdir/super_extra_subdir'
                    '/in_super_extra_subdir.yml',
                    'extra_subdir/other_super_extra_subdir'
                    '/in_other_super_extra_subdir.yaml',
                },
                file_tree={
                    '.git': {'.keep': ''},
                    'subdir': {
                        'extra_subdir': {
                            'super_extra_subdir': {
                                'in_super_extra_subdir.yml': '',
                            },
                            'other_super_extra_subdir': {
                                'in_other_super_extra_subdir.yaml': '',
                            },
                            'in_extra_subdir.yml': '',
                        },
                        'in_subdir.yaml': '',
                    },
                    'bad1.yaml': '',
                    'bad2.yaml': '',
                },
            ),
            id='subdir_tree',
        ),
        pytest.param(
            Params(
                targets={'good.yaml', 'submodules/format_this_in_subdir.yml'},
                expected_expanded={
                    'good.yaml',
                    'submodules/format_this_in_subdir.yml',
                },
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
                        'format_this_in_subdir.yml': '',
                    },
                    'good.yaml': '',
                },
            ),
            id='simple_case_with_submodules',
        ),
        pytest.param(
            Params(
                targets={
                    'good.yaml',
                    'submodules/testsuite/some_testsuite.yaml',
                    'submodules/testsuite/testsuite_dir'
                    '/another_testsuite.yaml',
                },
                expected_expanded={
                    'good.yaml',
                    'submodules/testsuite/some_testsuite.yaml',
                    'submodules/testsuite/testsuite_dir'
                    '/another_testsuite.yaml',
                },
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
                        'format_this_in_subdir.yml': '',
                    },
                    'good.yaml': '',
                },
            ),
            id='explicit_file_is_ok_in_submodules',
        ),
        pytest.param(
            Params(
                targets={'.'},
                expected_expanded={
                    'good.yaml',
                    'submodules/format_this_in_subdir.yml',
                },
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
                        'format_this_in_subdir.yml': '',
                    },
                    'good.yaml': '',
                },
            ),
            id='exclude_submodules',
        ),
        pytest.param(
            Params(
                targets={'.'},
                expected_expanded={
                    'good.yaml',
                    'submodules/format_this_in_subdir.yml',
                },
                file_tree={
                    '.git': {
                        '.keep': '',
                        'internal_file_in_git.yaml': '',
                        'internal': {'other_internal_file_in_git.yml': ''},
                    },
                    'submodules': {
                        'testsuite': {
                            '.git': {'.keep': ''},
                            'testsuite_dir': {
                                'another_testsuite.yaml': '',
                                'some_py_file.py': '',
                            },
                            'some_testsuite.yaml': '',
                        },
                        'format_this_in_subdir.yml': '',
                    },
                    'good.yaml': '',
                },
            ),
            id='exclude_git_internal_folder',
        ),
        pytest.param(
            Params(
                targets={'.'},
                expected_expanded={
                    'good.yaml',
                    'disabled_in_ml.yaml',
                    'simple_dirs/schemas/good_schema.yaml',
                    'submodules/format_this_in_subdir.yml',
                },
                file_tree=RICH_TREE,
            ),
            id='all_together',
        ),
        pytest.param(
            Params(
                cwd='.',
                targets={'code'},
                expected_expanded={
                    'code/good.yaml',
                    'code/disabled_in_ml.yaml',
                    'code/simple_dirs/schemas/good_schema.yaml',
                    'code/submodules/format_this_in_subdir.yml',
                },
                file_tree={'code': RICH_TREE, 'wrong.yaml': ''},
            ),
            id='all_together_outside',
        ),
        pytest.param(
            Params(
                targets={'submodules/ml'},
                expected_expanded={
                    'submodules/ml/ml_dir/another_ml.yaml',
                    'submodules/ml/some_ml.yaml',
                    'submodules/ml/disabled_in_root.yaml',
                },
                file_tree=RICH_TREE,
            ),
            id='all_together_middle_submodoule_correct_services_yaml',
        ),
    ],
)
def test_files_searching(params: Params, make_dir_tree, tmp_path, monkeypatch):
    curdir = tmp_path
    if params.cwd is not None:
        curdir = tmp_path / params.cwd
    make_dir_tree(params.file_tree, tmp_path)
    monkeypatch.chdir(curdir)

    # pylint: disable=protected-access
    args = taxi_yamlfmt._parse_argv([])
    args.targets = {pathlib.Path(target) for target in params.targets}
    files_by_repos = utils.collect_file_groups_single_fmt(
        taxi_yamlfmt.NAME, taxi_yamlfmt.SUFFIXES, args,
    )
    files = utils.files_from_all_groups(files_by_repos)
    assert files == {
        pathlib.Path(target).resolve() for target in params.expected_expanded
    }
