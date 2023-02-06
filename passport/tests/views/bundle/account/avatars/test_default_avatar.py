# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_HOST,
    TEST_PDD_UID,
    TEST_SESSIONID_VALUE,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_AVATAR_KEY = 'avakey'
TEST_OLD_AVATAR_KEY = 'oldavakey'


@with_settings_hosts()
class BaseDefaultAvatarTestCase(BaseBundleTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'avatar': ['base', 'by_uid'],
        }))
        self.setup_blackbox_response()
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'account_modification',
            ip=TEST_USER_IP,
            uid=TEST_UID,
            consumer='dev',
        )

    def setup_blackbox_response(self):
        bb_data = dict(
            uid=TEST_UID,
            default_avatar_key=TEST_OLD_AVATAR_KEY,
        )
        sessionid_response = blackbox_sessionid_multi_response(**bb_data)
        userinfo_response = blackbox_userinfo_response(**bb_data)

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.db.serialize(userinfo_response)

    def check_ok(self, uid, rv, old_avatar=None):
        raise NotImplementedError()  # pragma: no cover

    def check_missing_extended_grants(self, uid=TEST_PDD_UID):
        self.env.grants.set_grants_return_value(mock_grants(grants={'avatar': ['base']}))
        rv = self.make_request(query_args=dict(uid=999))
        self.assert_error_response(
            rv,
            status_code=403,
            error_codes=['access.denied'],
            ignore_error_message=False,
            error_message="Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: None. Required grants: ['avatar.by_uid']",
        )

    def check_missing_client_ip(self):
        rv = self.make_request(query_args=dict(uid=TEST_UID), exclude_headers=['user_ip'])
        self.assert_error_response(rv, ['ip.empty'])

    def check_missing_host(self):
        rv = self.make_request(
            headers=dict(
                cookie='Session_id=%s' % TEST_SESSIONID_VALUE,
                host=None,
            ),
        )
        self.assert_error_response(rv, ['host.empty'])

    def check_empty_request(self):
        rv = self.make_request()
        self.assert_error_response(rv, ['request.credentials_all_missing'])

    def check_invalid_uid(self):
        rv = self.make_request(query_args=dict(uid='hi'))
        self.assert_error_response(rv, ['uid.invalid'])

    def check_sessionid_and_uid_valid(self):
        rv = self.make_request(
            query_args=dict(uid=TEST_UID),
            headers=dict(cookie='Session_id=%s' % TEST_SESSIONID_VALUE),
        )
        self.assert_error_response(rv, ['request.credentials_several_present'])

    def check_invalid_sessionid(self):
        bb_response = blackbox_sessionid_multi_response(
            status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            uid=TEST_UID,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )
        rv = self.make_request(
            headers=dict(cookie='Session_id='),
        )
        self.assert_error_response(rv, ['sessionid.invalid'])

    def check_invalid_sessionid_with_account_info(self):
        bb_response = blackbox_sessionid_multi_response(
            status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            uid=TEST_UID,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )
        rv = self.make_request(
            headers=dict(cookie='Session_id='),
        )
        self.assert_error_response(rv, ['sessionid.invalid'])

    def check_unknown_uid(self):
        blackbox_response = blackbox_userinfo_response(uid=None)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        rv = self.make_request(query_args=dict(uid=TEST_UID))
        self.assert_error_response(rv, ['account.not_found'])

    def check_disabled_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                enabled=False,
            ),
        )
        rv = self.make_request(query_args=dict(uid=TEST_UID))
        self.assert_error_response(rv, ['account.disabled'])

    def check_disabled_on_deletion_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        rv = self.make_request(query_args=dict(uid=TEST_UID))
        self.assert_error_response(rv, ['account.disabled_on_deletion'])

    def check_disabled_account_by_sessionid(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
            ),
        )
        rv = self.make_request(
            headers=dict(cookie='Session_id=%s' % TEST_SESSIONID_VALUE),
        )
        self.assert_error_response(rv, ['account.disabled'])

    def check_disabled_on_deletion_account_by_sessionid(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        rv = self.make_request(
            headers=dict(cookie='Session_id=%s' % TEST_SESSIONID_VALUE),
        )
        self.assert_error_response(rv, ['account.disabled_on_deletion'])

    def check_disabled_account_by_sessionid_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
            ),
        )
        rv = self.make_request(
            headers=dict(cookie='Session_id=%s' % TEST_SESSIONID_VALUE),
        )
        self.assert_error_response(rv, ['account.disabled'])

    def check_disabled_on_deletion_account_by_sessionid_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        rv = self.make_request(
            headers=dict(cookie='Session_id=%s' % TEST_SESSIONID_VALUE),
        )
        self.assert_error_response(rv, ['account.disabled_on_deletion'])

    def check_ok_by_uid(self, uid=TEST_UID, old_avatar=TEST_OLD_AVATAR_KEY, with_check_cookies=False, **kwargs):
        rv = self.make_request(query_args=dict(uid=uid), **kwargs)
        self.check_ok(uid, rv, old_avatar=old_avatar, with_check_cookies=with_check_cookies)

    def check_ok_by_sessionid(self, uid=TEST_UID, **kwargs):
        rv = self.make_request(
            headers=dict(cookie='Session_id=%s' % TEST_SESSIONID_VALUE),
            **kwargs
        )
        self.check_ok(uid, rv)


class AvatarSetDefaultTestCase(BaseDefaultAvatarTestCase):

    default_url = '/1/account/avatars/default/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(key=TEST_AVATAR_KEY)
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
    )

    def check_ok(self, uid, response, old_avatar=TEST_OLD_AVATAR_KEY, with_check_cookies=True):
        self.assert_ok_response(response)
        shard = 'passportdbshard1'

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count(shard), 1)
        self.env.db.check('attributes', 'avatar.default', TEST_AVATAR_KEY, uid=uid, db=shard)

        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(
            self.env.statbox.entry(
                'account_modification',
                entity='person.default_avatar',
                uid=str(uid),
                old=old_avatar or '-',
                new=TEST_AVATAR_KEY,
                operation='created' if not old_avatar else 'updated',
            ),
        )
        self.env.statbox.assert_has_written(entries)
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'set_default_avatar',
                'info.default_avatar': TEST_AVATAR_KEY,
                'consumer': 'dev',
            },
        )
        eq_(self.env.handle_mock.call_count, 3)

    def test_missing_extended_grants(self):
        self.check_missing_extended_grants()

    def test_missing_client_ip(self):
        self.check_missing_client_ip()

    def test_missing_host(self):
        self.check_missing_host()

    def test_empty_request(self):
        self.check_empty_request()

    def test_invalid_uid(self):
        self.check_invalid_uid()

    def test_sessionid_and_uid_valid(self):
        self.check_sessionid_and_uid_valid()

    def test_invalid_sessionid(self):
        self.check_invalid_sessionid()

    def test_invalid_sessionid_with_account_info(self):
        self.check_invalid_sessionid_with_account_info()

    def test_unknown_uid(self):
        self.check_unknown_uid()

    def test_disabled_account(self):
        self.check_disabled_account()

    def test_disabled_on_deletion_account(self):
        self.check_disabled_on_deletion_account()

    def test_disabled_account_by_sessionid(self):
        self.check_disabled_account_by_sessionid()

    def test_disabled_on_deletion_account_by_sessionid(self):
        self.check_disabled_on_deletion_account_by_sessionid()

    def test_disabled_account_by_sessionid_with_account_info(self):
        self.check_disabled_account_by_sessionid_with_account_info()

    def test_disabled_on_deletion_account_by_sessionid_with_account_info(self):
        self.check_disabled_on_deletion_account_by_sessionid_with_account_info()

    def test_ok_by_uid(self):
        self.check_ok_by_uid()

    def test_ok_by_sessionid(self):
        self.check_ok_by_sessionid()

    def test_ok_by_uid_without_old_avatar(self):
        bb_response = blackbox_userinfo_response(
            uid=555,
            login='foobar',
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            bb_response,
        )
        self.env.db.serialize(bb_response)
        self.check_ok_by_uid(555, old_avatar=None)

    def test_ok_by_uid_with_old_avatar_eq_new(self):
        rv = self.make_request(query_args=dict(uid=TEST_UID, key=TEST_OLD_AVATAR_KEY))

        self.assert_ok_response(rv)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        eq_(self.env.handle_mock.call_count, 0)
