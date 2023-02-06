# -*- coding: utf-8 -*-

from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import Consumer
import pytest


@pytest.mark.parametrize(
    'consumer',
    [
        'not_in_services',
        '   not_in_services   ',
    ],
)
def test_valid_consumer(consumer):
    with FakeGrants() as grants:
        grants.set_grants_return_value({'not_in_services': {}})
        check_equality(Consumer(), (consumer, consumer.strip()))


@pytest.mark.parametrize(
    'consumer',
    [
        '',
        'DOES_NOT_EXIST',
    ],
)
def test_invalid_consumer(consumer):
    with FakeGrants() as grants:
        grants.set_grants_return_value({'not_in_services': {}})
        check_raise_error(Consumer(), consumer)
