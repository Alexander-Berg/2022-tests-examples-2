# -*- coding: utf-8 -*-
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import CaptchaChecks
import pytest


@pytest.mark.parametrize('valid_value', ['1', '2', '8', '9'])
def test_capthca_check_valid(valid_value):
    check_equality(CaptchaChecks(), (valid_value, int(valid_value)))


@pytest.mark.parametrize('invalid_value', ['', '-1', '0', '10', '255'])
def test_capthca_check_invalid(invalid_value):
    check_raise_error(CaptchaChecks(), invalid_value)
