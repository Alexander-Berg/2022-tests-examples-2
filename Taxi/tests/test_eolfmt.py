import pytest

from taxi_linters import taxi_eolfmt


@pytest.mark.parametrize(
    'before,after,file_name',
    [
        pytest.param(
            'Unicode символы',
            'Unicode символы\n',
            'main.py',
            id='unicode_symbols_wo_newline',
        ),
        pytest.param(
            'Unicode символы\n',
            'Unicode символы\n',
            'main.txt',
            id='unicode_symbols_w_newline',
        ),
        pytest.param(
            'Unicode символы\nВезде',
            'Unicode символы\nВезде\n',
            'main.h',
            id='unicode_several_strings_wo_newline',
        ),
        pytest.param(
            'empty_file = None',
            'empty_file = None\n',
            'main.py',
            id='python_file_wo_newline',
        ),
        pytest.param(
            'empty_file = None\n',
            'empty_file = None\n',
            'main.py',
            id='python_file_w_newline',
        ),
        pytest.param(
            '#include <stdio.h>',
            '#include <stdio.h>\n',
            'main.cpp',
            id='cpp_file_wo_newline',
        ),
        pytest.param('', '', '__init__.py', id='empty_file'),
        pytest.param(
            '#include <stdio.h>\n\n\n',
            '#include <stdio.h>\n\n\n',
            'main.cpp',
            id='several_newline',
        ),
        pytest.param('\n', '\n', 'python.ini', id='one_newline'),
    ],
)
def test_formatting(before, after, file_name, tmp_path):
    temp_file = tmp_path / file_name
    temp_file.write_text(before)
    # pylint: disable=protected-access
    taxi_eolfmt._format_eol(temp_file)

    assert temp_file.read_text() == after
