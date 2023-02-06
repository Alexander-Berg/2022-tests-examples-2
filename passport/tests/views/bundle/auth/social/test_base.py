# -*- coding: utf-8 -*-

from mock import Mock
from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.tests.views.bundle.auth.base_test_data import TEST_USER_COOKIES
from passport.backend.api.views.bundle.auth.social.base import (
    AccountDisabledError,
    AccountDisabledOnDeletionError,
    BaseSocialAuthView,
    UnknownUid,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import BaseTestCase
from .base_test_data import *


def build_headers(host=None, cookie=None):
    return mock_headers(
        host=host or TEST_HOST,
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        x_forwarded_for=True,
        cookie=cookie or TEST_USER_COOKIES,
        accept_language='ru',
    )


@with_settings_hosts()
class TestBaseSocialView(BaseTestCase):
    def setUp(self):
        super(TestBaseSocialView, self).setUp()

        self.track_id = self.env.track_manager.create_test_track()

        view = BaseSocialAuthView()
        self.account = Mock(login='userlogin', is_pdd=False)
        view.account = self.account
        self.profile = {
            'userid': 100500,
            'firstname': 'fn',
            'lastname': 'ln',
            'gender': 1,
            'provider': TEST_PROVIDER,
        }
        self.task_data = {
            'profile': self.profile,
        }

        with self.track_transaction() as track:
            track.retpath = TEST_RETPATH
            track.social_task_data = self.task_data
            track.is_captcha_required = False
            track.social_task_id = TEST_TASK_ID

            view.track = track

        self.view = view
        self.patch_check_session_cookie()

    def tearDown(self):
        self.unpatch_check_session_cookie()

        del self.track_id
        del self.view
        del self.account

        super(TestBaseSocialView, self).tearDown()

    def test_assert_disabled_account_enabled(self):
        self.account.is_user_enabled = True
        self.view.check_account_enabled()

    def test_assert_disabled_account_disabled_on_deletion(self):
        self.account.is_user_enabled = False
        self.account.disabled_status = ACCOUNT_DISABLED_ON_DELETION
        self.account.is_disabled = True
        with self.assertRaises(AccountDisabledOnDeletionError):
            self.view.check_account_enabled()

    def test_assert_disabled_account_disabled_nomoney(self):
        self.account.is_user_enabled = False
        self.account.is_subscribed = Mock(return_value=False)

        with self.assertRaises(AccountDisabledError):
            self.view.check_account_enabled()

    def test_get_accounts(self):
        blackbox_response = blackbox_userinfo_response_multiple([{'uid': 1}, {'uid': 3}])
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        accounts = self.view.get_accounts([1, 2, 3])
        eq_(accounts[0].uid, 1)
        eq_(accounts[1].uid, 3)

    def test_get_accounts_disabled_on_deletion(self):
        blackbox_response = blackbox_userinfo_response_multiple([
            {'uid': 1},
            {
                'uid': 2,
                'attributes': {
                    'account.is_disabled': '2',
                }
            },
            {
                'uid': 3,
                'attributes': {
                    'account.is_disabled': '1',
                },
            }]
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        accounts = self.view.get_accounts([1, 2, 3])
        eq_(accounts[0].uid, 1)
        eq_(accounts[1].uid, 3)

    def test_single_uid(self):
        blackbox_response = blackbox_userinfo_response(uid=1)
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        accounts = self.view.get_accounts([1])
        eq_(accounts[0].uid, 1)
        eq_(len(accounts), 1)

    def test_ignore_unknownuid(self):
        self.env.blackbox.set_blackbox_response_side_effect('userinfo', UnknownUid)
        accounts = self.view.get_accounts([1])
        eq_(len(accounts), 0)

    def test_load_task_data(self):
        self.view.statbox = Mock()
        self.view.load_task_data()
        eq_(self.view.task_data, self.task_data)
        eq_(self.view.provider, TEST_PROVIDER)
        eq_(self.view.response_values['provider'], TEST_PROVIDER)
        eq_(self.view.profile, self.profile)
