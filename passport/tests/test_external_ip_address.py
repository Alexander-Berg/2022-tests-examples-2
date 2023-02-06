# -*- coding: utf-8 -*-

from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import ExternalIPAddress
import pytest


@with_settings()
@pytest.mark.parametrize('valid_ip', [
    '8.8.8.8',
    '127.0.0.1',
    ])
def test_external_ip_address(valid_ip):
    check_equality(ExternalIPAddress(), (valid_ip, valid_ip.strip()))


@with_settings()
@pytest.mark.parametrize('invalid_ip', [
    None,
    '',
    '    ',
    'test',
    '37.9.101.169',
    ])
def test_external_ip_address_invalid(invalid_ip):
    check_raise_error(ExternalIPAddress(), invalid_ip)
