# -*- coding: utf-8 -*-

from passport.backend.core.password import policy
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators.password.password import PasswordPolicy
import pytest


@pytest.mark.parametrize('valid_policy', policy.PASSWORD_POLICY_NAMES)
def test_password_policy(valid_policy):
    check_equality(PasswordPolicy(), (valid_policy, valid_policy))


@pytest.mark.parametrize('invalid_policy', [
    'abc',
    'a' * 100,
    ] + [
    ' %s ' % x for x in policy.PASSWORD_POLICY_NAMES
    ] + [
    x.upper() for x in policy.PASSWORD_POLICY_NAMES
    ])
def test_password_policy_invalid(invalid_policy):
    check_raise_error(PasswordPolicy(), invalid_policy)
