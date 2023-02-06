from mock import patch, mock_open
import pytest

from tools.setup_utils import set_project_version, get_project_version, \
    debian_version

multy_line_input = """
__version__ = "unknown"
some_string = "__version__"
"""

multy_line_output = """
__version__ = \'2.0\'
some_string = "__version__"
"""


@pytest.mark.parametrize('input_content, output_content', [
    ('__version__ = \'\'', '__version__ = \'2.0\''),
    ('__version__ = \'unknown\'', '__version__ = \'2.0\''),
    ('__version__ = \'1.0\'', '__version__ = \'2.0\''),
    ('__version__ = ""', '__version__ = \'2.0\''),
    ('__version__ = "unknown"', '__version__ = \'2.0\''),
    ('__version__ = "1.0"', '__version__ = \'2.0\''),
    (multy_line_input, multy_line_output),
])
def test_set_project_version(input_content, output_content):
    with patch('tools.setup_utils.open', mock_open(read_data=input_content)) \
            as open_mock:
        set_project_version('dummy', '2.0')
        open_mock().write.assert_called_once_with(output_content)


@pytest.mark.parametrize('input_content, expected', [
    ('__version__ = \'2.0\'', '2.0'),
    ('# coding: utf-8\n\n__version__ = \'2.0\'', '2.0'),
])
def test_get_project_version(input_content, expected):
    with patch('tools.setup_utils.open', mock_open(read_data=input_content)) \
            as open_mock:
        assert expected == get_project_version('dummy')


@pytest.mark.parametrize('input_content, expected', [
    ('yandex-taxi-dmp-taxi-etl (1.312) unstable; urgency=low', '1.312'),
    ('yandex-taxi-dmp-taxi-etl (1.312hotfix1) unstable; urgency=low',
     '1.312hotfix1'),
])
def test_debian_version(input_content, expected):
    with patch('tools.setup_utils.open', mock_open(read_data=input_content)) \
            as open_mock:
        assert expected == debian_version('dummy')
