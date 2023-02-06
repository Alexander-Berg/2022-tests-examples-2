# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.api.views.bundle.phone.helpers import (
    code_possible_splits,
    load_phones,
    split_code_by_3,
)
from passport.backend.api.yasms.api import Yasms as YasmsApi
from passport.backend.core.builders.blackbox.blackbox import get_blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import FakeBlackbox
from passport.backend.core.builders.yasms import get_yasms
from passport.backend.core.env.env import Environment
from passport.backend.core.models.phones.faker import (
    build_account,
    build_phone_being_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
)
import pytest

from .base import (
    TEST_OPERATION_ID,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_UID,
)


@pytest.mark.parametrize(
    ('before', 'after'),
    [
        ('', set([])),
        ('1', {'1'}),
        ('12', {'12', '1 2'}),
        ('123', {'123', '1 2 3', '12 3', '1 23'}),
        ('1234', {'1 2 3 4', '1 2 34', '1 23 4', '1 234', '12 3 4', '12 34', '123 4', '1234'}),
    ],
)
def test_code_possible_splits(before, after):
    eq_(set(code_possible_splits(before)), after)


@pytest.mark.parametrize(
    ('before', 'after'),
    [
        ('123', ['123']),
        ('123 ', ['123']),
        ('123 456 ', ['123', '456']),
        (' 123456  789', ['123', '456', '789']),
    ],
)
def test_split_code_by_3(before, after):
    eq_(split_code_by_3(before), after)


@pytest.mark.parametrize('code', [0, '', '1234', ' '])
def test_split_code_by_3_bad(code):
    with assert_raises(ValueError):
        split_code_by_3(code)


@with_settings
class TestLoadPhones(unittest.TestCase):
    def setUp(self):
        self.fake_blackbox = FakeBlackbox()
        self.fake_blackbox.start()
        self.tvm_credentials_manager = FakeTvmCredentialsManager()
        self.tvm_credentials_manager.start()
        self.tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'yasms',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )

    def tearDown(self):
        self.tvm_credentials_manager.stop()
        self.fake_blackbox.stop()
        del self.fake_blackbox
        del self.tvm_credentials_manager

    def build_yasms_api(self):
        return YasmsApi(get_blackbox(), get_yasms(), Environment())

    def test_load_phones_with_valid_phone_number(self):
        account = build_account(
            uid=TEST_UID,
            **build_phone_being_bound(
                operation_id=TEST_OPERATION_ID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
            )
        )

        phones = load_phones(self.build_yasms_api(), account)
        eq_(phones._by_number.items(), [])

    def test_load_phones_with_valid_phone_number_and_valid_status(self):
        account = build_account(
            uid=TEST_UID,
            **build_phone_secured(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
            )
        )

        phones = load_phones(self.build_yasms_api(), account)
        eq_(len(phones._by_number.items()), 1)
