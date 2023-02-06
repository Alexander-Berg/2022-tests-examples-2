# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from io import StringIO
from signal import (
    SIGTTIN,
    SIGTTOU,
)

from mock import (
    DEFAULT,
    Mock,
    patch,
)
from nose.tools import eq_
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.env import Environment
from passport.backend.core.models.phones.faker import (
    assert_account_has_phonenumber_alias,
    assert_phonenumber_alias_missing,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.dbscripts.split_phonenumber_alias.base import split_phonenumber_aliases
from passport.backend.dbscripts.split_phonenumber_alias.cli import run
from passport.backend.dbscripts.test.base import TestCase
from passport.backend.dbscripts.test.consts import (
    TEST_LOGIN1,
    TEST_LOGIN2,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER2,
    TEST_UID1,
    TEST_UID2,
)
from passport.backend.utils.common import deep_merge


class _BaseTestCase(TestCase):
    def _setup_blackbox(self, accounts):
        userinfo_args = [a['userinfo'] for a in accounts]
        userinfo_response = blackbox_userinfo_response_multiple(userinfo_args)
        self._blackbox_faker.set_response_value('userinfo', userinfo_response)

    def _setup_db(self, accounts):
        for account in accounts:
            userinfo = account['userinfo']
            if 'uid' not in userinfo or userinfo['uid'] is not None:
                userinfo_response = blackbox_userinfo_response(**account['userinfo'])
                self._db_faker.serialize(userinfo_response)

    def _build_account(self, uid=TEST_UID1, alias_phone_number=None,
                       enabled_search_for_alias=True, enabled=True,
                       portal_alias=TEST_LOGIN1, secure_phone_id=TEST_PHONE_ID1):
        userinfo = dict(
            uid=uid,
            aliases={'portal': portal_alias},
            enabled=enabled,
        )
        if alias_phone_number:
            userinfo = deep_merge(
                userinfo,
                build_phone_secured(
                    secure_phone_id,
                    alias_phone_number.e164,
                    is_alias=True,
                    is_enabled_search_for_alias=enabled_search_for_alias,
                ),
            )
        return dict(userinfo=userinfo)

    def _build_not_existent_account(self, uid):
        return dict(userinfo=dict(uid=None, id=uid))

    def _setup_account_not_found(self):
        account = self._build_not_existent_account(TEST_UID1)
        self._setup_blackbox([account])

    def _setup_account_without_phonenumber_alias(self, uid):
        account = self._build_account(uid=uid, alias_phone_number=None)
        self._setup_blackbox([account])
        self._setup_db([account])

    def _setup_account_with_enabled_search_of_phonenumber_alias(self, uid, phone_number):
        account = self._build_account(uid=uid, alias_phone_number=phone_number)
        self._setup_blackbox([account])
        self._setup_db([account])

    def _setup_account_with_disabled_search_of_phonenumber_alias(self, uid, phone_number):
        account = self._build_account(
            uid=uid,
            alias_phone_number=phone_number,
            enabled_search_for_alias=False,
        )
        self._setup_blackbox([account])
        self._setup_db([account])

    def _setup_disabled_account_with_disabled_search_of_phonenumber_alias(self, uid, phone_number):
        account = self._build_account(
            uid=uid,
            alias_phone_number=phone_number,
            enabled_search_for_alias=False,
            enabled=False,
        )
        self._setup_blackbox([account])
        self._setup_db([account])


class TestSplitPhonenumberAliases(_BaseTestCase):
    def setUp(self):
        super(TestSplitPhonenumberAliases, self).setUp()
        self._env = Environment()

    def test_no_uids(self):
        split_phonenumber_aliases([], self._env)

    def test_account_not_found(self):
        self._setup_account_not_found()
        split_phonenumber_aliases([TEST_UID1], self._env)

    def test_no_alias(self):
        self._setup_account_without_phonenumber_alias(TEST_UID1)
        split_phonenumber_aliases([TEST_UID1], self._env)
        assert_phonenumber_alias_missing(self._db_faker, TEST_UID1)

    def test_search_enabled(self):
        self._setup_account_with_enabled_search_of_phonenumber_alias(
            TEST_UID1,
            TEST_PHONE_NUMBER1,
        )

        split_phonenumber_aliases([TEST_UID1], self._env)

        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
        )

    def test_search_disabled(self):
        self._setup_account_with_disabled_search_of_phonenumber_alias(
            TEST_UID1,
            TEST_PHONE_NUMBER1,
        )

        split_phonenumber_aliases([TEST_UID1], self._env)

        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
        )

    def test_account_disabled(self):
        self._setup_disabled_account_with_disabled_search_of_phonenumber_alias(
            TEST_UID1,
            TEST_PHONE_NUMBER1,
        )

        split_phonenumber_aliases([TEST_UID1], self._env)

        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
        )

    def test_blackbox_request(self):
        self._setup_account_not_found()

        split_phonenumber_aliases([TEST_UID1], self._env)

        eq_(len(self._blackbox_faker.requests), 1)
        eq_(self._blackbox_faker.requests[0].post_args['uid'], str(TEST_UID1))
        eq_(self._blackbox_faker.requests[0].post_args['aliases'], 'all_with_hidden')
        self._blackbox_faker.requests[0].assert_contains_attributes({'account.enable_search_by_phone_alias'})

    def test_many_accounts(self):
        accounts = [
            self._build_account(
                uid=TEST_UID1,
                portal_alias=TEST_LOGIN1,
                alias_phone_number=TEST_PHONE_NUMBER1,
                enabled_search_for_alias=False,
                secure_phone_id=TEST_PHONE_ID1,
            ),
            self._build_account(
                uid=TEST_UID2,
                portal_alias=TEST_LOGIN2,
                alias_phone_number=TEST_PHONE_NUMBER2,
                enabled_search_for_alias=False,
                secure_phone_id=TEST_PHONE_ID2,
            ),
        ]
        self._setup_blackbox(accounts)
        self._setup_db(accounts)

        split_phonenumber_aliases([TEST_UID1, TEST_UID2], self._env)

        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
        )
        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID2,
            TEST_PHONE_NUMBER2.digital,
        )

    def test_many_accounts_but_one_not_found(self):
        accounts = [
            self._build_not_existent_account(TEST_UID2),
            self._build_account(
                uid=TEST_UID1,
                alias_phone_number=TEST_PHONE_NUMBER1,
                enabled_search_for_alias=False,
            ),
        ]
        self._setup_blackbox(accounts)
        self._setup_db(accounts)

        split_phonenumber_aliases([TEST_UID1, TEST_UID2], self._env)

        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
        )

    def test_many_accounts_database_fails_on_first(self):
        accounts = [
            self._build_account(
                uid=TEST_UID1,
                portal_alias=TEST_LOGIN1,
                alias_phone_number=TEST_PHONE_NUMBER1,
                enabled_search_for_alias=False,
                secure_phone_id=TEST_PHONE_ID1,
            ),
            self._build_account(
                uid=TEST_UID2,
                portal_alias=TEST_LOGIN2,
                alias_phone_number=TEST_PHONE_NUMBER2,
                enabled_search_for_alias=False,
                secure_phone_id=TEST_PHONE_ID2,
            ),
        ]
        self._setup_blackbox(accounts)
        self._setup_db(accounts)
        self._db_faker.set_side_effect_for_db(
            'passportdbshard1',
            [DBError, DEFAULT],
        )

        split_phonenumber_aliases([TEST_UID1, TEST_UID2], self._env)

        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
            enable_search=False,
        )
        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID2,
            TEST_PHONE_NUMBER2.digital,
        )


@with_settings_hosts(
    DATABASE_WRITE_LOAD_PER_SECOND=1,
    UIDS_IN_BLACKBOX_REQUEST=1,
)
class _BaseRunTestCase(_BaseTestCase):
    def setUp(self):
        super(_BaseRunTestCase, self).setUp()

        self._throttler = Mock(name='throttler')
        self._throttler_patch = patch(
            'passport.backend.dbscripts.split_phonenumber_alias.cli.Throttler',
            self._throttler,
        )
        self._throttler_patch.start()

        self._throttler_control = Mock(name='throttler_control')
        self._throttler_control_patch = patch(
            'passport.backend.dbscripts.split_phonenumber_alias.cli.ThrottlerControl',
            self._throttler_control,
        )
        self._throttler_control_patch.start()

    def tearDown(self):
        self._throttler_control_patch.stop()
        self._throttler_patch.stop()
        super(_BaseRunTestCase, self).tearDown()

    def _setup_blackbox(self, accounts):
        responses = []
        for account in accounts:
            userinfo_response = blackbox_userinfo_response_multiple([account['userinfo']])
            responses.append(userinfo_response)
        self._blackbox_faker.set_response_side_effect('userinfo', responses)

    def _build_file_with_uids(self, uids):
        return StringIO('\n'.join(map(str, uids)))


class TestRun(_BaseRunTestCase):
    def test_no_uids(self):
        run(uids=[])


class TestRunSingleUid(_BaseRunTestCase):
    def setUp(self):
        super(TestRunSingleUid, self).setUp()
        accounts = [
            self._build_account(
                uid=TEST_UID1,
                portal_alias=TEST_LOGIN1,
                alias_phone_number=TEST_PHONE_NUMBER1,
                enabled_search_for_alias=False,
                secure_phone_id=TEST_PHONE_ID1,
            ),
        ]
        self._setup_blackbox(accounts)
        self._setup_db(accounts)

    def test_enable_search_attribute(self):
        run(uids=[TEST_UID1])

        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
        )

    def test_file(self):
        run(_file=self._build_file_with_uids([TEST_UID1]))

        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
        )


class TestRunManyUids(_BaseRunTestCase):
    def setUp(self):
        super(TestRunManyUids, self).setUp()
        accounts = [
            self._build_account(
                uid=TEST_UID1,
                portal_alias=TEST_LOGIN1,
                alias_phone_number=TEST_PHONE_NUMBER1,
                enabled_search_for_alias=False,
                secure_phone_id=TEST_PHONE_ID1,
            ),
            self._build_account(
                uid=TEST_UID2,
                portal_alias=TEST_LOGIN2,
                alias_phone_number=TEST_PHONE_NUMBER2,
                enabled_search_for_alias=False,
                secure_phone_id=TEST_PHONE_ID2,
            ),
        ]
        self._setup_blackbox(accounts)
        self._setup_db(accounts)

    def test_throttler_init(self):
        run(uids=[TEST_UID1, TEST_UID2])
        self._throttler.assert_called_once_with(rps=1.0)

    def test_throttling(self):
        run(uids=[TEST_UID1, TEST_UID2])

        throttler_object = self._throttler.return_value
        eq_(throttler_object.throttle.call_count, 2)

    def test_throttler_control(self):
        run(uids=[TEST_UID1, TEST_UID2])

        throttler_object = self._throttler.return_value
        self._throttler_control.assert_called_once_with(
            throttler_object,
            decrease_signum=SIGTTIN,
            increase_signum=SIGTTOU,
        )

        throttler_control_object = self._throttler_control.return_value
        throttler_control_object.setup.assert_called_once_with()

    def test_enable_search_attribute(self):
        run(uids=[TEST_UID1, TEST_UID2])

        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
        )
        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID2,
            TEST_PHONE_NUMBER2.digital,
        )

    def test_file(self):
        run(_file=self._build_file_with_uids([TEST_UID1, TEST_UID2]))

        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID1,
            TEST_PHONE_NUMBER1.digital,
        )
        assert_account_has_phonenumber_alias(
            self._db_faker,
            TEST_UID2,
            TEST_PHONE_NUMBER2.digital,
        )


@with_settings_hosts(
    DATABASE_WRITE_LOAD_PER_SECOND=2,
    UIDS_IN_BLACKBOX_REQUEST=1,
)
class TestRunDatabaseWriteLoadPerSecond(_BaseRunTestCase):
    def test_throttler_init(self):
        run(uids=[])
        self._throttler.assert_called_once_with(rps=2.0)


@with_settings_hosts(
    DATABASE_WRITE_LOAD_PER_SECOND=1,
    UIDS_IN_BLACKBOX_REQUEST=2,
)
class TestRunUidsInBlackboxRequest(_BaseRunTestCase):
    def test_throttler_init(self):
        run(uids=[])
        self._throttler.assert_called_once_with(rps=0.5)
