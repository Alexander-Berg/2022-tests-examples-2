import pytest

from grocery_salaries.utils.pandas_helpers import to_str


@pytest.mark.parametrize(
    'input_string, result_string', [(b'Tursunboy \xd5gli', 'Tursunboy Õgli')],
)
def test_bytes_to_utf_str(input_string: str, result_string: str):
    test_string = to_str(input_string)

    assert test_string == result_string
