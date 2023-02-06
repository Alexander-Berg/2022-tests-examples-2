# -*- coding: utf-8 -*-

from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import Blackbox as BlackboxBuilder
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response_multiple,
    FakeBlackbox,
    get_parsed_blackbox_response,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.utils.blackbox import (
    get_many_accounts_by_uids,
    get_many_accounts_by_userinfo_list,
)


TEST_UID1 = 11
TEST_UID2 = 12
TEST_UID3 = 13


@with_settings_hosts(
    BLACKBOX_URL='http://blackbox.url/',
    BLACKBOX_ATTRIBUTES=tuple(),
    BLACKBOX_MAX_UIDS_PER_REQUEST=2,
)
class TestGetManyAccountsByUids(PassportTestCase):
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

    def test_need_no(self):
        """
        Запрашиваем 0 uid'ов.
        """
        accounts, unknown_uids = get_many_accounts_by_uids(
            [],
            self._blackbox_builder,
        )

        eq_(accounts, [])
        eq_(unknown_uids, set())

    def test_need_one__know_one(self):
        """
        Запрашиваем 1 uid.
        Есть сведения.
        """
        self._blackbox_builder_faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([
                {'uid': TEST_UID1, 'id': TEST_UID1},
            ]),
        )

        accounts, unknown_uids = get_many_accounts_by_uids(
            [TEST_UID1],
            self._blackbox_builder,
        )

        eq_(len(accounts), 1)
        eq_(accounts[0].uid, TEST_UID1)
        eq_(unknown_uids, set())

    def test_need_one__know_nothing(self):
        """
        Запрашиваем 1 uid.
        Нет сведений.
        """
        self._blackbox_builder_faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([
                {'uid': None, 'id': TEST_UID1},
            ]),
        )

        accounts, unknown_uids = get_many_accounts_by_uids(
            [TEST_UID1],
            self._blackbox_builder,
        )

        eq_(accounts, [])
        eq_(unknown_uids, {TEST_UID1})

    def test_need_two__know_two(self):
        """
        Запрашиваем 2 uid'а.
        Есть сведения о всех uid'ах.
        """
        self._blackbox_builder_faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([
                {'uid': TEST_UID1, 'id': TEST_UID1},
                {'uid': TEST_UID2, 'id': TEST_UID2},
            ]),
        )

        accounts, unknown_uids = get_many_accounts_by_uids(
            [TEST_UID1, TEST_UID2],
            self._blackbox_builder,
        )

        eq_(len(accounts), 2)
        eq_(accounts[0].uid, TEST_UID1)
        eq_(accounts[1].uid, TEST_UID2)
        eq_(unknown_uids, set())

    def test_need_two__know_one(self):
        """
        Запрашиваем 2 uid'а.
        Есть инфа о части uid'ов.
        """
        self._blackbox_builder_faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([
                {'uid': TEST_UID1, 'id': TEST_UID1},
                {'uid': None, 'id': TEST_UID2},
            ]),
        )

        accounts, unknown_uids = get_many_accounts_by_uids(
            [TEST_UID1, TEST_UID2],
            self._blackbox_builder,
        )

        eq_(len(accounts), 1)
        eq_(accounts[0].uid, TEST_UID1)
        eq_(unknown_uids, {TEST_UID2})

    def test_many_requests(self):
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

        accounts, _ = get_many_accounts_by_uids(
            [TEST_UID1, TEST_UID2, TEST_UID3],
            self._blackbox_builder,
        )

        eq_(len(accounts), 3)
        eq_(accounts[0].uid, TEST_UID1)
        eq_(accounts[1].uid, TEST_UID2)
        eq_(accounts[2].uid, TEST_UID3)


@with_settings_hosts()
class TestGetManyAccountsByUserinfoList(PassportTestCase):
    def _build_userinfo_list(self, userinfo_args_list):
        response = blackbox_userinfo_response_multiple(userinfo_args_list)
        return get_parsed_blackbox_response('userinfo', response)

    def test_many_ok(self):
        userinfo_list = self._build_userinfo_list(
            [
                dict(uid=TEST_UID1),
                dict(uid=TEST_UID2),
            ],
        )

        accounts, unknown_uids = get_many_accounts_by_userinfo_list(userinfo_list)

        eq_(len(accounts), 2)
        eq_(accounts[0].uid, TEST_UID1)
        eq_(accounts[1].uid, TEST_UID2)
        eq_(unknown_uids, set())

    def test_unknown_uids(self):
        userinfo_list = self._build_userinfo_list(
            [
                dict(uid=None, id=TEST_UID1),
                dict(uid=TEST_UID2),
            ],
        )

        accounts, unknown_uids = get_many_accounts_by_userinfo_list(userinfo_list)

        eq_(len(accounts), 1)
        eq_(accounts[0].uid, TEST_UID2)
        eq_(unknown_uids, {TEST_UID1})
