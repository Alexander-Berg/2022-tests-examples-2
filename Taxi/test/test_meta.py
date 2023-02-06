# -*- coding: utf-8 -*-
import pytest

from suite.gp import validate_identifier, get_gptype, GPTypes


@pytest.mark.fast
@pytest.mark.parametrize(
    'name,result,max_len',
    [
        ('qwerty', '"qwerty"', 999),
        ('"qwerty"', '"qwerty"', 63),
        ('123456789', '"12345"', 5),
    ]
)
def test_validate_identifier(name: str, result: str, max_len: int):
    assert result == validate_identifier(name, max_len=max_len)


@pytest.mark.fast
@pytest.mark.parametrize(
    'name,result',
    [
        ('toast', GPTypes.TOAST),
        ('view', GPTypes.VIEW),
        ('partition', GPTypes.PARTITION),
        ('table', GPTypes.TABLE),
        ('database', GPTypes.DATABASE),
        ('null', GPTypes.UNKNOWN),
        (None, GPTypes.UNKNOWN),
    ]
)
def test_get_gptype(name: str, result: str):
    assert result == get_gptype(name)
