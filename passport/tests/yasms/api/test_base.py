# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import raises
from passport.backend.api.yasms.api import (
    get_time_of_last_confirmation_code_sending,
    get_validation_state,
)
from passport.backend.core.models.phones.faker import build_account


UID = 86
PHONE_NUMBER = u'+79998877666'
TEST_DATE = datetime(2011, 1, 2, 3, 4, 5)
CONSUMER_IP = u'1.2.3.4'


@raises(ValueError)
def test_get_validation_state_inappropriate_phone():
    account = build_account(
        uid=72,
        phones=[{'id': 2, 'number': PHONE_NUMBER, 'created': TEST_DATE}],
    )
    phone = account.phones.by_id(2)
    get_validation_state(phone)


@raises(ValueError)
def test_get_time_of_last_confirmation_code_sending_inappropriate_phone():
    account = build_account(
        uid=72,
        phones=[{'id': 2, 'number': PHONE_NUMBER, 'created': TEST_DATE}],
    )
    phone = account.phones.by_id(2)
    get_time_of_last_confirmation_code_sending(phone)
