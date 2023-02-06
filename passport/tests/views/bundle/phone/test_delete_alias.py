# -*- coding: utf-8 -*-

import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.emails import assert_user_notified_about_alias_as_login_and_email_disabled
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.views.bundle.phone.controllers import DELETE_ALIAS_STATE
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
    BLACKBOX_LOGIN_DISABLED_STATUS,
    BLACKBOX_LOGIN_NOT_FOUND_STATUS,
    BLACKBOX_LOGIN_UNKNOWN_STATUS,
    BLACKBOX_PASSWORD_BAD_STATUS,
    BLACKBOX_SESSIONID_DISABLED_STATUS,
    BLACKBOX_SESSIONID_EXPIRED_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BLACKBOX_SESSIONID_NOAUTH_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_login_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.models.phones.faker import assert_phonenumber_alias_removed
from passport.backend.core.test.consts import (
    TEST_PASSWORD_HASH1,
    TEST_SOCIAL_LOGIN1,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts

from .base import (
    BaseConfirmCommitterTestCase,
    BaseConfirmSubmitterTestCase,
    ConfirmCommitterTestMixin,
    ConfirmSubmitterSpecificTestMixin,
    HEADERS_WITH_SESSIONID,
    TEST_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_SESSION_ID,
    TEST_UID,
)


@with_settings_hosts
class TestDeleteAliasSubmitter(BaseConfirmSubmitterTestCase,
                               ConfirmSubmitterSpecificTestMixin):

    track_state = DELETE_ALIAS_STATE
    url = '/1/bundle/phone/delete_alias/submit/?consumer=dev'
    with_check_cookies = False

    def setUp(self):
        super(TestDeleteAliasSubmitter, self).setUp()

        self.setup_account()

        # Переопределяю базовый ответ, потому что в запросе нет телефона
        self.base_response = {u'status': u'ok'}

        self.additional_ok_response_params = {'is_password_required': True}

    def setup_account(
        self,
        alias_type='portal',
        crypt_password=TEST_PASSWORD_HASH1,
        login=TEST_LOGIN,
    ):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=login,
            crypt_password=crypt_password,
            aliases={
                alias_type: login,
                'phonenumber': TEST_PHONE_NUMBER.digital,
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo_response)

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'number': TEST_PHONE_NUMBER.e164,
            'display_language': 'ru',
            'track_id': self.track_id,
            'uid': TEST_UID,
        }
        if exclude is not None:
            for key in exclude:
                del base_params[key]
        return merge_dicts(base_params, kwargs)

    def ok_response(self, **kwargs):
        return merge_dicts(
            self.base_submitter_response,
            self.additional_ok_response_params,
            kwargs,
        )

    def make_request_with_sessionid(self):
        return self.make_request(
            self.query_params(sessionid=TEST_SESSION_ID, exclude=['uid']),
        )

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.ok_response())

        eq_(len(self.env.blackbox.requests), 1)

        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        eq_(track.phone_confirmation_phone_number, TEST_PHONE_NUMBER.e164)
        eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER.original)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('success'),
        ])

    def test_ok_by_sessionid(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                aliases={
                    'portal': TEST_LOGIN,
                    'phonenumber': TEST_PHONE_NUMBER.digital,
                },
                attributes={'password.encrypted': '1:testpassword'},
                age=100500,
            ),
        )

        rv = self.make_request_with_sessionid()

        self.assert_ok_response(rv, **self.ok_response())

        eq_(len(self.env.blackbox.requests), 1)

        track = self.track_manager.read(self.track_id)
        ok_(track.country is None)
        eq_(track.uid, str(TEST_UID))

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('success'),
        ])

    def test_account_not_found(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {u'status': u'error', u'errors': [u'account.not_found'], u'track_id': str(self.track_id)},
        )
        eq_(len(self.env.blackbox.requests), 1)

        self.env.statbox.assert_has_written([])

    def test_invalid_sessionid(self):
        for status in [BLACKBOX_SESSIONID_EXPIRED_STATUS,
                       BLACKBOX_SESSIONID_NOAUTH_STATUS,
                       BLACKBOX_SESSIONID_INVALID_STATUS]:
            self.env.blackbox.set_blackbox_response_value(
                'sessionid',
                blackbox_sessionid_multi_response(status=status),
            )

            rv = self.make_request_with_sessionid()

            eq_(rv.status_code, 200, rv.data)
            eq_(
                json.loads(rv.data),
                {u'status': u'error', u'errors': [u'sessionid.invalid'], u'track_id': str(self.track_id)},
            )

        eq_(self.env.blackbox._mock.request.call_count, 3)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')] * 3)

    def test_disabled_account_by_uid(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={'password.encrypted': '1:testpassword'},
                enabled=False,
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {u'status': u'error', u'errors': [u'account.disabled'], u'track_id': str(self.track_id)},
        )

        eq_(len(self.env.blackbox.requests), 1)
        eq_(len(self.env.yasms.requests), 0)

        self.env.statbox.assert_has_written([])

    def test_disabled_account_by_session_id(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_DISABLED_STATUS),
        )

        rv = self.make_request_with_sessionid()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {u'status': u'error', u'errors': [u'account.disabled'], u'track_id': str(self.track_id)},
        )

        eq_(len(self.env.blackbox.requests), 1)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_disabled_on_deletion_account_by_uid(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={'password.encrypted': '1:testpassword'},
                enabled=False,
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {u'status': u'error', u'errors': [u'account.disabled'], u'track_id': str(self.track_id)},
        )

        eq_(len(self.env.blackbox.requests), 1)
        eq_(len(self.env.yasms.requests), 0)

        self.env.statbox.assert_has_written([])

    def test_disabled_on_deletion_account_by_session_id(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_DISABLED_STATUS,
                attributes={
                    'account.is_disabled': '2',
                }
            ),
        )

        rv = self.make_request_with_sessionid()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {u'status': u'error', u'errors': [u'account.disabled_on_deletion'], u'track_id': str(self.track_id)},
        )

        eq_(len(self.env.blackbox.requests), 1)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_without_alias_on_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={'password.encrypted': '1:testpassword'},
                aliases={'portal': TEST_LOGIN},
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {u'status': u'error', u'errors': [u'phone_alias.not_found'], u'track_id': str(self.track_id)},
        )

        self.env.statbox.assert_has_written([])

    def test_passwordless_account(self):
        self.setup_account(
            alias_type='social',
            crypt_password=None,
            login=TEST_SOCIAL_LOGIN1,
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.ok_response(is_password_required=False)
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        eq_(track.phone_confirmation_phone_number, TEST_PHONE_NUMBER.e164)
        eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER.original)


@with_settings_hosts
class TestDeleteAliasCommitter(BaseConfirmCommitterTestCase,
                               ConfirmCommitterTestMixin, EmailTestMixin):
    track_state = DELETE_ALIAS_STATE
    url = '/1/bundle/phone/delete_alias/commit/?consumer=dev'
    with_check_cookies = False

    def make_account_kwargs(
        self,
        emails=None,
        alias_type='portal',
        crypt_password=TEST_PASSWORD_HASH1,
        enable_search_by_phone_alias='1',
        login=TEST_LOGIN,
    ):
        return dict(
            uid=TEST_UID,
            login=login,
            crypt_password=crypt_password,
            aliases={
                alias_type: login,
                'phonenumber': TEST_PHONE_NUMBER.digital,
            },
            emails=emails,
            attributes={'account.enable_search_by_phone_alias': enable_search_by_phone_alias},
        )

    def setup_account(
        self,
        emails=None,
        alias_type='portal',
        crypt_password=TEST_PASSWORD_HASH1,
        enable_search_by_phone_alias='1',
        login=TEST_LOGIN,
        method='login',
        setup_db=True,
    ):
        userinfo_kwargs = self.make_account_kwargs(
            emails=emails,
            alias_type=alias_type,
            crypt_password=crypt_password,
            enable_search_by_phone_alias=enable_search_by_phone_alias,
            login=login,
        )

        if method == 'login':
            self.blackbox_login_response = blackbox_login_response(**userinfo_kwargs)
            self.env.blackbox.set_response_value('login', self.blackbox_login_response)
            self.env.blackbox.set_response_side_effect('userinfo', NotImplementedError)

        elif method == 'userinfo':
            userinfo_response = blackbox_userinfo_response(**userinfo_kwargs)
            self.env.blackbox.set_response_value('userinfo', userinfo_response)
            self.env.blackbox.set_response_side_effect('login', NotImplementedError)

        if setup_db:
            self.env.db.serialize(blackbox_userinfo_response(**userinfo_kwargs))

    def setUp(self):
        super(TestDeleteAliasCommitter, self).setUp()
        self.setup_account(setup_db=False)

    def query_params(self, **kwargs):
        base_params = {
            'password': 'testpassword',
            'track_id': self.track_id,
        }

        return merge_dicts(base_params, kwargs)

    def assert_statbox_ok(self, with_check_cookies=False):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend(
            [
            self.env.statbox.entry('phonenumber_alias_removed'),
            self.env.statbox.entry('phonenumber_alias_subscription_removed'),
            self.env.statbox.entry('phonenumber_alias_taken_away'),
            self.env.statbox.entry('success'),
            ],
        )
        self.env.statbox.assert_has_written(entries)

    def test_ok(self):
        self.env.db.serialize(json.dumps({'users': [json.loads(self.blackbox_login_response)]}))

        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=TEST_UID, db='passportdbcentral')

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        assert_phonenumber_alias_removed(
            self.env.db,
            uid=TEST_UID,
            alias=TEST_PHONE_NUMBER.digital,
        )

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'alias.phonenumber.rm': str(TEST_PHONE_NUMBER),
                'action': 'phone_alias_delete',
                'user_agent': 'curl',
                'consumer': 'dev',
            },
        )

        self.assert_no_emails_sent()

        self.assert_statbox_ok(with_check_cookies=self.with_check_cookies)

    def test_ok_with_email(self):
        self.setup_account(emails=[
            self.create_native_email('user1', 'yandex.ru'),
            self.create_validated_external_email('user1', 'gmail.com'),
        ])

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        eq_(len(self.env.mailer.messages), 2)
        assert_user_notified_about_alias_as_login_and_email_disabled(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address='user1@gmail.com',
            firstname='\u0414',
            login=TEST_LOGIN,
            portal_email=TEST_LOGIN + '@yandex.ru',
            phonenumber_alias=TEST_PHONE_NUMBER.digital,
        )
        assert_user_notified_about_alias_as_login_and_email_disabled(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address='user1@yandex.ru',
            firstname='\u0414',
            login=TEST_LOGIN,
            portal_email=TEST_LOGIN + '@yandex.ru',
            phonenumber_alias=TEST_PHONE_NUMBER.digital,
        )

        self.assert_statbox_ok(with_check_cookies=self.with_check_cookies)

    def test_without_alias(self):
        blackbox_response = blackbox_login_response(uid=TEST_UID)
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_response,
        )

        self.env.db.serialize(json.dumps({'users': [json.loads(blackbox_response)]}))

        self.env.db.check_missing('aliases', 'phonenumber', uid=TEST_UID, db='passportdbcentral')

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'phone_alias.not_found']},
            )
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.assert_no_emails_sent()

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))

        self.env.statbox.assert_has_written(entries)

    def test_account_not_found(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                login_status=BLACKBOX_LOGIN_NOT_FOUND_STATUS,
                uid=TEST_UID,
            ),
        )

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'account.not_found']},
            )
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        self.env.statbox.assert_has_written(entries)

    def test_disabled_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                login_status=BLACKBOX_LOGIN_DISABLED_STATUS,
                uid=TEST_UID,
            ),
        )

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'account.disabled']},
            )
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))

        self.env.statbox.assert_has_written(entries)

    def test_disabled_on_deletion_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                login_status=BLACKBOX_LOGIN_DISABLED_STATUS,
                uid=TEST_UID,
                attributes={
                    'account.is_disabled': '2',
                }
            ),
        )

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'account.disabled_on_deletion']},
            )
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))

        self.env.statbox.assert_has_written(entries)

    def test_not_matched_password_by_bad_password_status(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_BAD_STATUS,
                uid=TEST_UID,
            ),
        )

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'password.not_matched']},
            )
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        track = self.track_manager.read(self.track_id)
        ok_(not track.is_captcha_recognized)
        ok_(not track.is_captcha_required)
        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('password_not_matched'))

        self.env.statbox.assert_has_written(entries)

    def test_blackbox_failed_by_invalid_login_status(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                login_status=BLACKBOX_LOGIN_UNKNOWN_STATUS,
                uid=TEST_UID,
            ),
        )

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'backend.blackbox_failed']},
            )
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        track = self.track_manager.read(self.track_id)
        ok_(not track.is_captcha_recognized)
        ok_(not track.is_captcha_required)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        self.env.statbox.assert_has_written(entries)

    def test_required_and_not_recognized_captcha(self):
        self.setup_track_for_commit(is_captcha_required='1')

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'captcha.required']},
            )
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 0)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))

        self.env.statbox.assert_has_written(entries)

    def test_bruteforce_and_required_and_recognized_captcha_and_good_password(self):
        self.env.db.serialize(json.dumps({'users': [json.loads(self.blackbox_login_response)]}))

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                bruteforce_policy=BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
                uid=TEST_UID,
                aliases={
                    'portal': TEST_LOGIN,
                    'phonenumber': TEST_PHONE_NUMBER.digital,
                },
                attributes={'account.enable_search_by_phone_alias': '1'},
            ),
        )

        self.setup_track_for_commit(
            is_captcha_required='1',
            is_captcha_checked='1',
            is_captcha_recognized='1',
        )

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data), self.base_response,
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        track = self.track_manager.read(self.track_id)

        ok_(track.is_captcha_required)
        ok_(not track.is_captcha_recognized)
        ok_(not track.is_captcha_checked)

        self.assert_statbox_ok(with_check_cookies=self.with_check_cookies)

    def test_bruteforce_and_required_and_recognized_captcha_and_bad_password(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                password_status=BLACKBOX_PASSWORD_BAD_STATUS,
                bruteforce_policy=BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )

        self.setup_track_for_commit(
            is_captcha_required='1',
            is_captcha_checked='1',
            is_captcha_recognized='1',
        )

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {
                    'status': 'error',
                    'errors': ['captcha.required', 'password.not_matched'],
                },
            ),
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        track = self.track_manager.read(self.track_id)

        ok_(track.is_captcha_required)
        ok_(not track.is_captcha_recognized)
        ok_(not track.is_captcha_checked)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('password_not_matched'))

        self.env.statbox.assert_has_written(entries)

    def test_required_and_recognized_captcha_and_bad_password(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                password_status=BLACKBOX_PASSWORD_BAD_STATUS,
            ),
        )

        self.setup_track_for_commit(
            is_captcha_required='1',
            is_captcha_checked='1',
            is_captcha_recognized='1',
        )

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {
                    'status': 'error',
                    'errors': ['password.not_matched'],
                },
            ),
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        track = self.track_manager.read(self.track_id)

        ok_(not track.is_captcha_required)
        ok_(not track.is_captcha_recognized)
        ok_(not track.is_captcha_checked)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('password_not_matched'))

        self.env.statbox.assert_has_written(entries)

    def test_required_and_recognized_captcha_and_good_password(self):
        self.env.db.serialize(json.dumps({'users': [json.loads(self.blackbox_login_response)]}))

        self.setup_track_for_commit(
            is_captcha_required='1',
            is_captcha_checked='1',
            is_captcha_recognized='1',
        )

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            self.base_response,
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        track = self.track_manager.read(self.track_id)

        ok_(not track.is_captcha_required)
        ok_(not track.is_captcha_recognized)
        ok_(not track.is_captcha_checked)

        self.assert_statbox_ok(with_check_cookies=self.with_check_cookies)

    def test_bruteforce_and_set_required_captcha(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                bruteforce_policy=BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
                uid=TEST_UID,
            ),
        )

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'captcha.required']},
            )
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))

        self.env.statbox.assert_has_written(entries)

    def test_dberror_on_delete_alias(self):
        self.env.db.serialize(json.dumps({'users': [json.loads(self.blackbox_login_response)]}))

        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=TEST_UID, db='passportdbcentral')

        self.setup_track_for_commit()

        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError)

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {
                    'status': 'error',
                    'errors': ['backend.database_failed'],
                },
            ),
        )

        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)

        # При ошибке записи в БД на старой схеме, запись в новую схему не производится
        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('phonenumber_alias_taken_away', error='alias.isnt_deleted'))

        self.env.statbox.assert_has_written(entries)

    def test_commit__blackbox_unexpected_response__error(self):
        """
        ЧЯ вернул что-то странное при запросе в метод login,
        то, чего возвращать он никак не должен. Проверим, что корректно
        отработаем данную ситуацию.
        """
        self.setup_track_for_commit()
        self.env.blackbox.set_blackbox_response_value(
            'login',
            json.dumps(
                {
                    'error': 'ok',
                    'login_status': {
                        'id': 111,
                        'value': 'upyachka',
                    },
                    'password_status': {
                        'id': 111,
                        'value': 'upyachka',
                    },
                },
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'backend.blackbox_permanent_error']},
            ),
        )

    def test_passwordless_account(self):
        self.setup_account(
            alias_type='social',
            login=TEST_SOCIAL_LOGIN1,
            crypt_password=None,
            method='userinfo',
        )

        self.setup_track_for_commit()

        rv = self.make_request(self.query_params(password=None))

        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        assert_phonenumber_alias_removed(
            self.env.db,
            uid=TEST_UID,
            alias=TEST_PHONE_NUMBER.digital,
        )

    def test_no_password_but_account_has_password(self):
        self.setup_account(method='userinfo')

        self.setup_track_for_commit()

        rv = self.make_request(self.query_params(password=None))

        self.assert_error_response(
            rv,
            ['password.not_matched'],
            check_content=False,
        )


class TestDeleteAliasSubmitterV2(TestDeleteAliasSubmitter):
    url = '/2/bundle/phone/delete_alias/submit/?consumer=dev'
    with_check_cookies = True

    def make_request_with_sessionid(self):
        return self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.build_headers(HEADERS_WITH_SESSIONID),
        )

    def test_password_not_required(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                aliases={
                    'portal': TEST_LOGIN,
                    'phonenumber': TEST_PHONE_NUMBER.digital,
                },
                attributes={'password.encrypted': '1:testpassword'},
                age=30,
            ),
        )

        rv = self.make_request_with_sessionid()

        self.assert_ok_response(rv, **self.ok_response(is_password_required=False))


class TestDeleteAliasCommitterV2(TestDeleteAliasCommitter):
    url = '/2/bundle/phone/delete_alias/commit/?consumer=dev'
    with_check_cookies = True

    def setup_account(
        self,
        emails=None,
        alias_type='portal',
        crypt_password=TEST_PASSWORD_HASH1,
        enable_search_by_phone_alias='1',
        login=TEST_LOGIN,
        method='login',
        password_age=100500,
        setup_db=True,
    ):
        userinfo_kwargs = self.make_account_kwargs(
            emails=emails,
            alias_type=alias_type,
            crypt_password=crypt_password,
            enable_search_by_phone_alias=enable_search_by_phone_alias,
            login=login,
        )

        # в sessionid ходим всегда, а в login - только если нужно проверять пароль
        blackbox_sessionid_response = blackbox_sessionid_multi_response(age=password_age, **userinfo_kwargs)
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response)

        if method == 'login':
            self.blackbox_login_response = blackbox_login_response(**userinfo_kwargs)
            self.env.blackbox.set_response_value('login', self.blackbox_login_response)
        else:
            self.env.blackbox.set_response_side_effect('login', NotImplementedError)

        if setup_db:
            self.env.db.serialize(blackbox_userinfo_response(**userinfo_kwargs))

    def build_headers(self, headers=None):
        return super(TestDeleteAliasCommitterV2, self).build_headers(
            merge_dicts(HEADERS_WITH_SESSIONID, headers or {}),
        )

    def test_no_password_but_account_has_password(self):
        self.setup_account(method='sessionid')

        self.setup_track_for_commit()

        rv = self.make_request(self.query_params(password=None))

        self.assert_error_response(
            rv,
            ['password.required'],
            check_content=False,
        )
