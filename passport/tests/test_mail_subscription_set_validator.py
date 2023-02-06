# -*- coding: utf-8 -*-
import json

from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import MailSubscriptionSetValidator
import pytest


@pytest.mark.parametrize('valid_value', [
    {},
    {1: True, 2: True},
    {1: False, 2: False},
    {3: True},
    ])
def test_mail_subscription_set_validator(valid_value):
    validator = MailSubscriptionSetValidator()

    input_value = json.dumps(valid_value)
    check_equality(validator, (input_value, valid_value))


@pytest.mark.parametrize('invalid_value', [
    json.dumps([]),
    json.dumps({'1': 'foo'}),
    json.dumps({'invalid_key': 'invalid_value'}),
    json.dumps({'invalid_key': True}),
    ])
def test_mail_subscription_set_validator_invalid(invalid_value):
    validator = MailSubscriptionSetValidator()

    check_raise_error(validator, invalid_value)
