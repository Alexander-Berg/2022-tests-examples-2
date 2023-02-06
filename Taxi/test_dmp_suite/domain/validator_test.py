import pytest
from dmp_suite.domain.validators import min_len_validator


@pytest.mark.parametrize(
    'params, check_str, err_expect', (
        ({'min_len': 3}, '123', None),
        ({'min_len': 3}, '12', 'длина поля меньше минимально допустимого значения: 2 < 3'),
        ({'min_len': 3, 'err_txt': 'свой текст {current_len}'}, '12', 'свой текст 2'),
    )
)
def test_min_len_validator(params, check_str, err_expect):
    validator = min_len_validator(**params)
    validation_result = validator(check_str)
    assert err_expect == validation_result
