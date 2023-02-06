# -*- coding: utf-8 -*
from passport.backend.core.services import get_service
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import Service
import pytest


@pytest.mark.parametrize('ignore_unknown_service', [True, False])
@pytest.mark.parametrize(('value', 'expected_value'), [
    ('mail', get_service(slug='mail')),
    ('lenta', get_service(slug='lenta')),
    ('2', get_service(sid=2)),
    ('23', get_service(sid=23)),
    (get_service(sid=23), get_service(sid=23)),
    ('', None),
    (None, None),
    ])
def test_service(ignore_unknown_service, value, expected_value):
    check_equality(Service(ignore_unknown_service=ignore_unknown_service), (value, expected_value))


@pytest.mark.parametrize('invalid_value', [
    'blabla',
    '12141414',
    object(),
    [],
    {},
    0,
    100500,
    ])
def test_service_invalid(invalid_value):
    check_raise_error(Service(), invalid_value)


@pytest.mark.parametrize('unknown_value', [
    'blabla',
    '12141414',
    ])
def test_service_unknown(unknown_value):
    check_equality(Service(ignore_unknown_service=True), (unknown_value, None))
