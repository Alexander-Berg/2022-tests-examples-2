# -*- coding: utf-8 -*-
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import Birthday
import pytest


@pytest.mark.parametrize('valid_birthday', [
    ('0000-05-01', '0000-05-01'),
    ('2007-01-01', '2007-01-01'),
    ('2012-11-20', '2012-11-20'),
    ('1999-12-31', '1999-12-31'),
    ('2012-02-29', '2012-02-29'),
    ('0000-02-29', '0000-02-29'),
    ('0000-00-29', '0000-00-29'),
    ('0000-02-00', '0000-02-00'),
    # пустые значения - преобразуются в None
    ('', None),
    (None, None),
    ])
def test_valid_birthday(valid_birthday):
    check_equality(Birthday(), valid_birthday)


@pytest.mark.parametrize('invalid_birthday', [
    '0001-05-01',
    '1111-12-31',
    '5000-12-06',
    '2012-31-31',
    '2012-11-40',
    '2012-02-30',
    '2011-02-29',
    object(),
    {1: 2},
    1000,
    0,
    [],
    {},
    ])
def test_invalid_birthday(invalid_birthday):
    check_raise_error(Birthday(), invalid_birthday)


@pytest.mark.parametrize('invalid_birthday', [
    '0000-00-00',
    '1999-01-00',
    '1999-00-20',
    '1999-00-00',
    ])
def test_invalid_birthday_full(invalid_birthday):
    check_raise_error(Birthday(need_full=True), invalid_birthday)
