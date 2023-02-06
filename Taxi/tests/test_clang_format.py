import pathlib
from typing import NamedTuple
from typing import Set

import pytest

from taxi_linters import taxi_clang_format


UNFORMATTED = (
    'int main() {foo(param1, [](char c) { return c == \';\'; }, param2);}'
)

SIMPLE_TREE = {
    'repo_wo_services_yaml': {'.git': '', 'file.cpp': UNFORMATTED},
    'repo_version_7': {
        '.git': '',
        'services.yaml': 'linters: {clang-format: {version: 7}}',
        'file.cpp': UNFORMATTED,
    },
    'repo_version_9': {
        '.git': '',
        'services.yaml': 'linters: {clang-format: {version: 9}}',
        'file.cpp': UNFORMATTED,
    },
}
COMPLICATED_TREE = {
    'repo_mingle': {
        '.git': '',
        'sbm': {'.git': '', 'file.cpp': UNFORMATTED},
        'service.yaml': (
            'linters: {clang-format: {disable-paths-wildcards: '
            '[mingle_dir_1/mingle_dir_2/dir_un_2/*, '
            'mingle_dir_1/mingle_dir_2/dir_un_3/*]}}'
        ),
        'dir_9_1': {
            'service.yaml': 'linters: {clang-format: {version: 9}}',
            'file.cpp': UNFORMATTED,
        },
        'mingle_dir_1': {
            'mingle_dir_2': {
                'service.yaml': (
                    'linters: {clang-format: {version: 9, '
                    'disable-paths-wildcards: '
                    '[dir_un_1/*, dir_un_3/file.cpp]}}'
                ),
                'dir_un_1': {'file.cpp': UNFORMATTED},
                'dir_un_2': {'file.cpp': UNFORMATTED},
                'dir_un_3': {'file.cpp': UNFORMATTED},
                'file.cpp': UNFORMATTED,
                'dir_7_1': {
                    'library.yaml': 'linters: {clang-format: {version: 7}}',
                    'file.cpp': UNFORMATTED,
                    'dir_7_2': {'file.cpp': UNFORMATTED},
                },
            },
            'dir_7_3': {'file.cpp': UNFORMATTED},
            'file.cpp': UNFORMATTED,
        },
        'file.cpp': UNFORMATTED,
    },
}


def test_format_str():
    input_str = '#abc\n\n'
    output_str = '#abc\n'
    assert taxi_clang_format.format_str(input_str) == output_str


def test_format_str_style():
    input_str = 'int main(int &a) {}'
    output_str = 'int main(int& a) {}'
    assert taxi_clang_format.format_str(input_str) == output_str


def test_format_str_version():
    after_clang_format_7 = (
        'int main() {\n'
        '  foo(param1, [](char c) { return c == \';\'; }, param2);\n}'
    )
    after_clang_format_9 = (
        'int main() {\n'
        '  foo(\n'
        '      param1, [](char c) { return c == \';\'; }, param2);\n}'
    )

    assert taxi_clang_format.format_str(UNFORMATTED) == after_clang_format_7
    assert (
        taxi_clang_format.format_str(after_clang_format_7, version=9)
        == after_clang_format_9
    )


class Params(NamedTuple):
    tree: dict
    formatted7: Set[str] = set()
    formatted9: Set[str] = set()
    unformatted: Set[str] = set()


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                tree=SIMPLE_TREE,
                formatted7={'repo_wo_services_yaml', 'repo_version_7'},
                formatted9={'repo_version_9'},
            ),
            id='simple_format_out_of_repo',
        ),
        pytest.param(
            Params(
                tree=COMPLICATED_TREE,
                formatted7={
                    'repo_mingle',
                    'repo_mingle/mingle_dir_1',
                    'repo_mingle/mingle_dir_1/dir_7_3',
                    'repo_mingle/mingle_dir_1/mingle_dir_2/dir_7_1',
                    'repo_mingle/mingle_dir_1/mingle_dir_2/dir_7_1/dir_7_2',
                },
                formatted9={
                    'repo_mingle/dir_9_1',
                    'repo_mingle/mingle_dir_1/mingle_dir_2',
                },
                unformatted={
                    'repo_mingle/sbm',
                    'repo_mingle/mingle_dir_1/mingle_dir_2/dir_un_1',
                    'repo_mingle/mingle_dir_1/mingle_dir_2/dir_un_2',
                    'repo_mingle/mingle_dir_1/mingle_dir_2/dir_un_3',
                },
            ),
            id='simple_format_out_of_repo',
        ),
    ],
)
def test_format_repos(params, make_dir_tree, tmp_path, monkeypatch):
    def check_content(paths: Set[str], compare_to: str) -> None:
        for path in paths:
            text = pathlib.Path(tmp_path, path, 'file.cpp').read_text()
            assert compare_to == text

    after_clang_format_7 = (
        'int main() {\n'
        '  foo(param1, [](char c) { return c == \';\'; }, param2);\n}'
    )
    after_clang_format_9 = (
        'int main() {\n'
        '  foo(\n'
        '      param1, [](char c) { return c == \';\'; }, param2);\n}'
    )

    make_dir_tree(params.tree, tmp_path)
    monkeypatch.chdir(tmp_path)

    # pylint: disable=protected-access
    taxi_clang_format._main(['-v', *params.tree])

    check_content(params.formatted7, after_clang_format_7)
    check_content(params.formatted9, after_clang_format_9)
    check_content(params.unformatted, UNFORMATTED)
