import pytest

from taxi.util import version


@pytest.mark.parametrize(
    'version_str, expected_result',
    (('7.55 (79)', (7, 55, 79)), ('7.55', (7, 55)), ('not a number', None)),
)
async def test_as_tuple(version_str, expected_result):
    assert version.as_tuple(version_str) == expected_result


@pytest.mark.parametrize(
    'version_str, min_version_str, expected_result',
    (
        ('', '7.100', False),
        ('7.99', '', False),
        ('7.99', '7.100', False),
        ('7.100', '7.99', True),
        ('7.55 (79)', '7.55 (80)', False),
        ('7.55 (80)', '7.55 (79)', True),
    ),
)
async def test_check_version(version_str, min_version_str, expected_result):
    assert (
        version.check_version(version_str, min_version_str) == expected_result
    )
