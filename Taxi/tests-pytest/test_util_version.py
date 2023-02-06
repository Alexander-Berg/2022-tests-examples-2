import pytest

from taxi.util import version


@pytest.mark.parametrize(
    'a,b,excepted_min_result,excepted_max_result', [
        (None, '7.0 (22)', None, '7.0 (22)'),
        ('8.5 (11)', '8.4 (15)', '8.4 (15)', '8.5 (11)'),
        ('1.2', '1.3 (15)', '1.2', '1.3 (15)'),
        ('10.12', '9.4', '9.4', '10.12'),
        (None, None, None, None),
])
def test_version_check(a, b, excepted_min_result, excepted_max_result):
    min_result = version.min_version(a, b)
    assert excepted_min_result == min_result
    max_result = version.max_version(a, b)
    assert excepted_max_result == max_result
