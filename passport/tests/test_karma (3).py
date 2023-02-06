# -*- coding: utf-8 -*-

from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import (
    KarmaPrefix,
    KarmaSuffix,
)
import pytest


@pytest.mark.parametrize('valid_suffix', ['0', '75', '80', '85', '100'])
def test_karma_suffix(valid_suffix):
    check_equality(KarmaSuffix(), (valid_suffix, int(valid_suffix)))


@pytest.mark.parametrize('invalid_suffix', ['-1', 'BAD', '101', ''])
def test_karma_suffix_invalid(invalid_suffix):
    check_raise_error(KarmaSuffix(), invalid_suffix)


@pytest.mark.parametrize('valid_prefix', [str(i) for i in range(10)])
def test_karma_prefix(valid_prefix):
    check_equality(KarmaPrefix(), (valid_prefix, int(valid_prefix)))


@pytest.mark.parametrize('invalid_prefix', ['-1', 'BAD', '11', ''])
def test_karma_prefix_invalid(invalid_prefix):
    check_raise_error(KarmaPrefix(), invalid_prefix)
