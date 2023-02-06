# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import Blackbox as BlackboxBuilder
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response_multiple,
    FakeBlackbox,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.yasms.utils import get_many_accounts_with_phones_by_uids

from .consts import (
    TEST_UID1,
    TEST_UID2,
    TEST_UID3,
)


@with_settings_hosts(
    BLACKBOX_URL='http://blackbox.url/',
    BLACKBOX_ATTRIBUTES=tuple(),
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=('number', 'created'),
    BLACKBOX_MAX_UIDS_PER_REQUEST=2,
)
class TestGetManyAccountsByUids(TestCase):
    def setUp(self):
        self._fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self._fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self._fake_tvm_credentials_manager.start()

        self._blackbox_builder = BlackboxBuilder()

        self._blackbox_builder_faker = FakeBlackbox()
        self._blackbox_builder_faker.start()

    def tearDown(self):
        self._blackbox_builder_faker.stop()
        self._fake_tvm_credentials_manager.stop()
        del self._blackbox_builder_faker
        del self._fake_tvm_credentials_manager

    def test_ok(self):
        self._blackbox_builder_faker.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response_multiple([
                    {'uid': TEST_UID1, 'id': TEST_UID1},
                    {'uid': TEST_UID2, 'id': TEST_UID2},
                ]),
                blackbox_userinfo_response_multiple([
                    {'uid': TEST_UID3, 'id': TEST_UID3},
                ]),
            ],
        )

        accounts, _ = get_many_accounts_with_phones_by_uids(
            [TEST_UID1, TEST_UID2, TEST_UID3],
            self._blackbox_builder,
        )

        eq_(len(accounts), 3)
        eq_(accounts[0].uid, TEST_UID1)
        eq_(accounts[1].uid, TEST_UID2)
        eq_(accounts[2].uid, TEST_UID3)

        eq_(len(self._blackbox_builder_faker.requests), 2)
        for request in self._blackbox_builder_faker.requests:
            request.assert_post_data_contains({
                'emails': 'getall',
                'phone_attributes': '1,2',
            })
