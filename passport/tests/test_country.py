# -*- coding: utf-8 -*-

from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import CountryCode
import pytest


@with_settings()
@pytest.mark.parametrize('valid_country', ['AM', 'UA', 'GE'])
def test_country(valid_country):
    check_equality(CountryCode(), (valid_country, valid_country.lower()))


@with_settings()
@pytest.mark.parametrize('invalid_country', [
    '',
    'BADCOUNTRY',
    '     ',
    'AM     ',
    '     UA',
    '       ',
    ])
def test_country_invalid(invalid_country):
    check_raise_error(CountryCode(), invalid_country)
