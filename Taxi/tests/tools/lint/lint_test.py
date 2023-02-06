import pytest

from tools.lint.lint import get_mypy_command


@pytest.mark.parametrize(
    'report_dir,expected', [
        (None, 'mypy'),
        ('', 'mypy'),
        ('report_dir', 'mypy --junit-xml report_dir/mypy.xml'),
    ]
)
def test_mypy_command(report_dir, expected):
    actual = get_mypy_command(report_dir)
    assert actual == expected
