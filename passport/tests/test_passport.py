# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.core.builders.passport import (
    Passport,
    PassportAccountDisabledError,
    PassportAccountNotFoundError,
    PassportActionNotRequiredError,
    PassportInvalidAccountTypeError,
    PassportLoginNotavailableError,
    PassportNoSubscriptionError,
    PassportPermanentError,
    PassportPhoneOperationExistsError,
    PassportPhonishCompletionNotStartedError,
    PassportPhonishCompletionOtherStartedError,
    PassportReceiverAccountNotFoundError,
    PassportTemporaryError,
    PassportTooFrequentChangePasswordError,
    PassportTrackInvalidStateError,
    PassportTrackNotFoundError,
    PassportUserNotVerifiedError,
)
from passport.backend.core.builders.passport.faker import (
    FakePassport,
    passport_bundle_api_error_response,
    passport_ok_response,
    passport_old_api_error_response,
)
from passport.backend.core.builders.passport.passport import bundle_api_error_detector
from passport.backend.core.test.consts import (
    TEST_TRACK_ID1,
    TEST_USER_IP1,
)
from passport.backend.core.test.test_utils import with_settings


TEST_UID = 1
TEST_UID2 = 2
TEST_LOGIN = 'log-in'
TEST_SID = 'mail'
TEST_TIMESTAMP = 100000
TEST_APP_TYPE = 'mail'
TEST_APP_NAME = u'Почта для бабушки'
TEST_CLIENT_ID = 'f' * 32
TEST_DEVICE_NAME = u'Айфон 9S'
TEST_IP = '1.2.3.4'
TEST_HOST = 'yandex.ru'
TEST_COOKIE = 'Session_id=foo;'
TEST_USER_AGENT = 'curl'
TEST_MESSAGE_ID = '123'
TEST_AVATAR_KEY = '1/2-3'
TEST_PUBLIC_NAME = 'Elon M.'


@with_settings(
    PASSPORT_URL='http://localhost/',
    PASSPORT_CONSUMER='passport',
    PASSPORT_TIMEOUT=1,
    PASSPORT_RETRIES=2,
)
class TestPassportCommon(unittest.TestCase):
    def setUp(self):
        self.passport = Passport()
        self.passport.useragent.request = mock.Mock()

        self.response = mock.Mock()
        self.passport.useragent.request.return_value = self.response
        self.response.content = json.dumps(passport_ok_response())
        self.response.status_code = 200

    def tearDown(self):
        del self.passport
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 400
        self.response.content = b'not a json'
        with assert_raises(PassportPermanentError):
            self.passport.subscribe(uid=TEST_UID, sid=TEST_SID)

    def test_server_temporary_error(self):
        self.response.status_code = 503
        self.response.content = b'"server temporarily unavailable"'
        with assert_raises(PassportTemporaryError):
            self.passport.subscribe(uid=TEST_UID, sid=TEST_SID)

    def test_server_error(self):
        self.response.status_code = 500
        self.response.content = b'"server is down"'
        with assert_raises(PassportPermanentError):
            self.passport.subscribe(uid=TEST_UID, sid=TEST_SID)

    def test_passport_default_initialization(self):
        passport = Passport()
        ok_(passport.useragent is not None)
        eq_(passport.url, 'http://localhost/')


@with_settings(
    PASSPORT_URL='http://localhost/',
    PASSPORT_CONSUMER='passport',
    PASSPORT_TIMEOUT=1,
    PASSPORT_RETRIES=2,
)
class TestPassportMethods(unittest.TestCase):
    def setUp(self):
        self.fake_passport = FakePassport()
        self.fake_passport.start()
        self.fake_passport.set_response_value_without_method(json.dumps(passport_ok_response()))
        self.passport = Passport()

    def tearDown(self):
        self.fake_passport.stop()
        del self.fake_passport

    def test_subscribe_ok(self):
        response = self.passport.subscribe(uid=TEST_UID, sid=TEST_SID)
        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/account/%d/subscription/mail/?consumer=passport' % TEST_UID,
        )

    def test_subscribe_unknown_error(self):
        self.fake_passport.set_response_value(
            'subscribe',
            json.dumps(passport_old_api_error_response('SubscriptionImpossible', '')),
        )
        with assert_raises(PassportPermanentError):
            self.passport.subscribe(uid=TEST_UID, sid=TEST_SID)

    def test_unsubscribe_ok(self):
        response = self.passport.unsubscribe(uid=TEST_UID, sid=TEST_SID)
        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='DELETE',
            url='http://localhost/1/account/%d/subscription/mail/?consumer=passport' % TEST_UID,
        )

    def test_unsubscribe_no_subscription(self):
        self.fake_passport.set_response_value(
            'unsubscribe',
            json.dumps(passport_old_api_error_response('NoSubscription', '')),
        )
        with assert_raises(PassportNoSubscriptionError):
            self.passport.unsubscribe(uid=TEST_UID, sid=TEST_SID)

    def test_unsubscribe_unknown_error(self):
        self.fake_passport.set_response_value(
            'unsubscribe',
            json.dumps(passport_old_api_error_response('BlackboxFailed', '')),
        )
        with assert_raises(PassportPermanentError):
            self.passport.unsubscribe(uid=TEST_UID, sid=TEST_SID)

    def test_app_password_created_send_notifications_ok(self):
        response = self.passport.app_password_created_send_notifications(
            uid=TEST_UID,
            app_type=TEST_APP_TYPE,
            app_name=TEST_APP_NAME,
            user_ip=TEST_USER_IP1,
        )
        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/account/app_passwords/create/send_notifications/?consumer=passport',
            post_args={'uid': TEST_UID, 'app_type': TEST_APP_TYPE, 'app_name': TEST_APP_NAME},
            headers={'Ya-Consumer-Client-Ip': TEST_USER_IP1},
        )

    def test_app_password_created_send_notifications_unknown_error(self):
        self.fake_passport.set_response_value(
            'app_password_created_send_notifications',
            json.dumps(passport_bundle_api_error_response('exception.unhandled')),
        )
        with assert_raises(PassportPermanentError):
            self.passport.app_password_created_send_notifications(
                uid=TEST_UID,
                app_type=TEST_APP_TYPE,
                app_name=TEST_APP_NAME,
                user_ip=TEST_USER_IP1,
            )

    def test_oauth_client_edited_send_notifications_ok(self):
        response = self.passport.oauth_client_edited_send_notifications(
            client_id=TEST_CLIENT_ID,
            client_title=TEST_APP_NAME,
            redirect_uris_changed=True,
            scopes_changed=False,
            uid=TEST_UID,
            user_ip=TEST_IP,
            cookies=TEST_COOKIE,
            host=TEST_HOST,
        )
        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/oauth/client/edit/send_notifications/?consumer=passport',
            post_args={
                'client_id': TEST_CLIENT_ID,
                'client_title': TEST_APP_NAME,
                'redirect_uris_changed': 1,
                'scopes_changed': 0,
                'uid': TEST_UID,
            },
            headers={
                'Ya-Consumer-Client-Ip': TEST_IP,
                'Ya-Client-Cookie': TEST_COOKIE,
                'Ya-Client-Host': TEST_HOST,
            },
        )

    def test_oauth_client_edited_send_notifications_default_uid_ok(self):
        response = self.passport.oauth_client_edited_send_notifications(
            client_id=TEST_CLIENT_ID,
            client_title=TEST_APP_NAME,
            redirect_uris_changed=True,
            scopes_changed=False,
            user_ip=TEST_IP,
            cookies=TEST_COOKIE,
            host=TEST_HOST,
        )
        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/oauth/client/edit/send_notifications/?consumer=passport',
            post_args={
                'client_id': TEST_CLIENT_ID,
                'client_title': TEST_APP_NAME,
                'redirect_uris_changed': 1,
                'scopes_changed': 0,
            },
            headers={
                'Ya-Consumer-Client-Ip': TEST_IP,
                'Ya-Client-Cookie': TEST_COOKIE,
                'Ya-Client-Host': TEST_HOST,
            },
        )

    def test_send_challenge_email_ok(self):
        response = self.passport.send_challenge_email(
            uid=TEST_UID,
            device_name=TEST_DEVICE_NAME,
            user_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            is_challenged=True,
        )
        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/auth/password/challenge/send_email/?consumer=passport',
            post_args={'uid': TEST_UID, 'device_name': TEST_DEVICE_NAME, 'is_challenged': 1},
            headers={
                'Ya-Consumer-Client-Ip': TEST_IP,
                'Ya-Client-User-Agent': TEST_USER_AGENT,
            },
        )

    def test_password_options_ok(self):
        response = self.passport.password_options(
            uid=TEST_UID,
            is_changing_required=True,
            update_timestamp=TEST_TIMESTAMP,
        )
        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/2/account/%d/password_options/?consumer=passport' % TEST_UID,
            post_args={
                'is_changing_required': 1,
                'update_timestamp': TEST_TIMESTAMP,
            },
        )

    def test_password_options_ok_all_params(self):
        response = self.passport.password_options(
            uid=TEST_UID,
            is_changing_required=True,
            max_change_frequency_in_days=14,
            notify_by_sms=True,
            show_2fa_promo=True,
            update_timestamp=TEST_TIMESTAMP,
            global_logout=True,
            comment='comment',
            admin='admin',
        )
        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/2/account/%s/password_options/?consumer=passport' % str(TEST_UID),
            post_args={
                'is_changing_required': 1,
                'max_change_frequency_in_days': 14,
                'notify_by_sms': 1,
                'show_2fa_promo': 1,
                'update_timestamp': TEST_TIMESTAMP,
                'global_logout': 1,
                'comment': 'comment',
                'admin_name': 'admin',
            },
        )

    def test_password_options_invalid_account_type(self):
        self.fake_passport.set_response_value(
            'password_options',
            json.dumps(passport_bundle_api_error_response('account.invalid_type')),
        )
        with assert_raises(PassportInvalidAccountTypeError):
            self.passport.password_options(
                uid=TEST_UID,
                is_changing_required=True,
                update_timestamp=TEST_TIMESTAMP,
            )

    def test_password_options_password_too_frequent_change(self):
        self.fake_passport.set_response_value(
            'password_options',
            json.dumps(passport_bundle_api_error_response('password.too_frequent_change')),
        )
        with assert_raises(PassportTooFrequentChangePasswordError):
            self.passport.password_options(
                uid=TEST_UID,
                is_changing_required=True,
                update_timestamp=TEST_TIMESTAMP,
            )

    def test_password_options_action_not_required(self):
        self.fake_passport.set_response_value(
            'password_options',
            json.dumps(passport_bundle_api_error_response('action.not_required')),
        )
        with assert_raises(PassportActionNotRequiredError):
            self.passport.password_options(
                uid=TEST_UID,
                is_changing_required=True,
                update_timestamp=TEST_TIMESTAMP,
            )

    def test_password_options_unknown_error(self):
        self.fake_passport.set_response_value(
            'password_options',
            json.dumps(passport_bundle_api_error_response('exception.unhandled')),
        )
        with assert_raises(PassportPermanentError):
            self.passport.password_options(
                uid=TEST_UID,
                is_changing_required=True,
                update_timestamp=TEST_TIMESTAMP,
            )

    def test_create_restoration_link_ok(self):
        response = self.passport.create_restoration_link(
            uid=TEST_UID,
            link_type=1,
            ip=TEST_IP,
            host=TEST_HOST,
            admin='admin',
        )
        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/restore/create_link/?consumer=passport',
            post_args={
                'uid': TEST_UID,
                'link_type': 1,
                'admin_name': 'admin',
            },
            headers={
                'Ya-Consumer-Client-Ip': TEST_IP,
                'Ya-Client-Host': TEST_HOST,
            },
        )

    def test_create_restoration_link_with_comment_ok(self):
        response = self.passport.create_restoration_link(
            uid=TEST_UID,
            link_type=1,
            ip=TEST_IP,
            host=TEST_HOST,
            admin='admin',
            comment='comment',
        )
        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/restore/create_link/?consumer=passport',
            post_args={
                'uid': TEST_UID,
                'link_type': 1,
                'admin_name': 'admin',
                'comment': 'comment',
            },
            headers={
                'Ya-Consumer-Client-Ip': TEST_IP,
                'Ya-Client-Host': TEST_HOST,
            },
        )

    def test_create_restoration_link_propagates_error(self):
        self.fake_passport.set_response_value(
            'create_restoration_link',
            json.dumps(passport_bundle_api_error_response('exception.unhandled')),
        )
        response = self.passport.create_restoration_link(
            uid=TEST_UID,
            link_type=1,
            ip=TEST_IP,
            host=TEST_HOST,
            admin='admin',
        )
        eq_(
            response,
            passport_bundle_api_error_response('exception.unhandled'),
        )

    def test_create_restoration_link_with_error_detector_raises_error(self):
        self.fake_passport.set_response_value(
            'create_restoration_link',
            json.dumps(passport_bundle_api_error_response('exception.unhandled')),
        )
        with assert_raises(PassportPermanentError):
            self.passport.create_restoration_link(
                uid=TEST_UID,
                link_type=1,
                ip=TEST_IP,
                host=TEST_HOST,
                admin='admin',
                error_detector=bundle_api_error_detector,
            )

    def test_finish_phonish_completion__ok(self):
        response = self.passport.finish_phonish_completion(
            uid=TEST_UID,
            completion_id='completion_id',
            version='version',
            completion_args='completion_args',
        )

        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/complete/finish_phonish_completion/?consumer=passport',
            post_args={
                'uid': str(TEST_UID),
                'completion_id': 'completion_id',
                'version': 'version',
                'completion_args': 'completion_args',
            },
            headers=None,
        )

    @parameterized.expand([
        ('account.not_found', PassportAccountNotFoundError),
        ('login.notavailable', PassportLoginNotavailableError),
        ('phonish_completion.not_started', PassportPhonishCompletionNotStartedError),
        ('phonish_completion.other_started', PassportPhonishCompletionOtherStartedError),
    ])
    def test_finish_phonish_completion__fails(self, error_code, exception_cls):
        self.fake_passport.set_response_value(
            'finish_phonish_completion',
            json.dumps(passport_bundle_api_error_response(error_code)),
        )

        with assert_raises(exception_cls):
            self.passport.finish_phonish_completion(
                uid=TEST_UID,
                completion_id='completion_id',
                version='version',
                completion_args='completion_args',
            )

    def test_finish_phonish_migration__ok(self):
        response = self.passport.finish_phonish_migration(
            phonish_uid=TEST_UID,
            receiver_uid=TEST_UID2,
            migration_id='completion_id',
            version='version',
            migration_args='completion_args',
        )

        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/complete/finish_phonish_migration/?consumer=passport',
            post_args={
                'phonish_uid': str(TEST_UID),
                'receiver_uid': str(TEST_UID2),
                'migration_id': 'completion_id',
                'version': 'version',
                'migration_args': 'completion_args',
            },
            headers=None,
        )

    @parameterized.expand([
        ('receiver_account.not_found', PassportReceiverAccountNotFoundError),
        ('backend.music_failed', PassportTemporaryError),
        ('backend.billing_failed', PassportTemporaryError),
    ])
    def test_finish_phonish_migration__fails(self, error_code, exception_cls):
        self.fake_passport.set_response_value(
            'finish_phonish_migration',
            json.dumps(passport_bundle_api_error_response(error_code)),
        )

        with assert_raises(exception_cls):
            self.passport.finish_phonish_migration(
                phonish_uid=TEST_UID,
                receiver_uid=TEST_UID2,
                migration_id='completion_id',
                version='version',
                migration_args='completion_args',
            )

    def test_rfc_2fa_enable__ok(self):
        response = self.passport.rfc_2fa_enable(login=TEST_LOGIN)
        eq_(
            response,
            passport_ok_response(),
        )

    def test_rfc_2fa_enable__failed(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_enable',
            json.dumps(passport_bundle_api_error_response('account.without_password')),
        )

        with assert_raises(PassportPermanentError):
            self.passport.rfc_2fa_enable(login=TEST_LOGIN)

    def test_rfc_2fa_disable__ok(self):
        response = self.passport.rfc_2fa_disable(login=TEST_LOGIN)
        eq_(
            response,
            passport_ok_response(),
        )

    def test_rfc_2fa_disable__action_not_required(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_disable',
            json.dumps(passport_bundle_api_error_response('action.not_required')),
        )

        with assert_raises(PassportActionNotRequiredError):
            self.passport.rfc_2fa_disable(login=TEST_LOGIN)

    def test_rfc_2fa_set_check_time__failed(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_set_time',
            json.dumps(passport_bundle_api_error_response('exception.unhandled')),
        )

        with assert_raises(PassportPermanentError):
            self.passport.rfc_2fa_set_time(uid=TEST_UID, totp_check_time=TEST_TIMESTAMP)

    def test_rfc_2fa_set_check_time__ok(self):
        response = self.passport.rfc_2fa_set_time(uid=TEST_UID, totp_check_time=TEST_TIMESTAMP)
        eq_(
            response,
            passport_ok_response(),
        )

    def test_bind_phone_from_phonish_to_portal__ok(self):
        response = self.passport.bind_phone_from_phonish_to_portal(
            portal_uid=TEST_UID,
            phonish_uid=TEST_UID2,
            user_ip=TEST_IP,
        )

        eq_(response, passport_ok_response())
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/2/bundle/phone/bind_phone_from_phonish_to_portal/?consumer=passport',
            post_args={
                'portal_uid': str(TEST_UID),
                'phonish_uid': str(TEST_UID2),
            },
            headers={
                'Ya-Consumer-Client-Ip': str(TEST_IP),
            },
        )

    @parameterized.expand([
        ('operation.exists', PassportPhoneOperationExistsError),
        ('account.not_found', PassportAccountNotFoundError),
        ('account.disabled', PassportAccountDisabledError),
        ('account.invalid_type', PassportInvalidAccountTypeError),
        ('backend.blackbox_failed', PassportTemporaryError),
        ('backend.database_failed', PassportTemporaryError),
        ('internal.temporary', PassportTemporaryError),
        ('unexpected.exception', PassportPermanentError),
    ])
    def test_bind_phone_from_phonish_to_portal__fails(self, error_code, exception_cls):
        self.fake_passport.set_response_value(
            'bind_phone_from_phonish_to_portal',
            json.dumps(passport_bundle_api_error_response(error_code)),
        )
        with assert_raises(exception_cls):
            self.passport.bind_phone_from_phonish_to_portal(
                portal_uid=TEST_UID,
                phonish_uid=TEST_UID2,
                user_ip=TEST_IP,
            )

    def test_takeout_finish_extract__ok(self):
        response = self.passport.takeout_finish_extract(
            uid=TEST_UID,
            archive_s3_key='key',
            archive_password='password',
        )

        eq_(response, passport_ok_response())
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/takeout/extract/finish/?consumer=passport',
            post_args={
                'uid': TEST_UID,
                'archive_s3_key': 'key',
                'archive_password': 'password',
            },
        )

    def test_takeout_start_extract__ok(self):
        response = self.passport.takeout_start_extract(uid=TEST_UID)

        eq_(response, passport_ok_response())
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/takeout/extract/start/?consumer=passport',
            post_args={
                'uid': TEST_UID,
            },
        )

    def test_takeout_finish_extract__action_not_required(self):
        self.fake_passport.set_response_value(
            'takeout_finish_extract',
            json.dumps(passport_bundle_api_error_response('action.not_required')),
        )

        with assert_raises(PassportActionNotRequiredError):
            self.passport.takeout_finish_extract(
                uid=TEST_UID,
                archive_s3_key='key',
                archive_password='password',
            )

    def test_takeout_delete_extract_result__ok(self):
        response = self.passport.takeout_delete_extract_result(uid=TEST_UID)

        eq_(response, passport_ok_response())
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/takeout/extract/delete_result/?consumer=passport',
            post_args={
                'uid': TEST_UID,
            },
        )

    def test_reset_avatar__ok(self):
        response = self.passport.reset_avatar(uid=TEST_UID, avatar_key=TEST_AVATAR_KEY)

        eq_(response, passport_ok_response())
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/account/reset/avatar/?consumer=passport',
            post_args={
                'uid': TEST_UID,
                'avatar_key': TEST_AVATAR_KEY,
            },
        )

    @parameterized.expand([
        ('public_name',),
        ('full_name',),
    ])
    def test_reset_display_name__ok(self, field):
        response = self.passport.reset_display_name(uid=TEST_UID, **{field: TEST_PUBLIC_NAME})

        eq_(response, passport_ok_response())
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/bundle/account/reset/display_name/?consumer=passport',
            post_args={
                'uid': TEST_UID,
                field: TEST_PUBLIC_NAME,
            },
        )

    def test_set_default_avatar__ok(self):
        response = self.passport.set_default_avatar(uid=TEST_UID, key=TEST_AVATAR_KEY, user_ip=TEST_IP)

        eq_(response, passport_ok_response())
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/account/avatars/default/?consumer=passport',
            post_args={
                'uid': TEST_UID,
                'key': TEST_AVATAR_KEY,
            },
            headers={
                'Ya-Consumer-Client-Ip': TEST_IP,
            },
        )

    def test_account_options_ok(self):
        response = self.passport.account_options(
            uid=TEST_UID,
            takeout_subscription=True,
            takeout_delete_subscription=True,
        )
        eq_(
            response,
            passport_ok_response(),
        )
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/2/account/%d/options/?consumer=passport' % TEST_UID,
            post_args={
                'takeout_subscription': 1,
                'takeout_delete_subscription': 1,
            },
        )

    def test_get_phonish_uid_by_phone_ok(self):
        response = self.passport.get_phonish_uid_by_phone(
            track_id=TEST_TRACK_ID1,
            user_ip=TEST_USER_IP1,
        )

        eq_(response, passport_ok_response())

        request = self.fake_passport.requests[0]
        request.assert_properties_equal(
            method='GET',
            headers={'Ya-Consumer-Client-Ip': TEST_USER_IP1},
        )
        request.assert_url_starts_with('http://localhost/1/bundle/account/phonish/uid_by_phone/?')
        request.assert_query_equals(
            dict(
                consumer='passport',
                track_id=TEST_TRACK_ID1,
                use_device_id='False',
            ),
        )

    @parameterized.expand([
        ('account.not_found', PassportAccountNotFoundError),
        ('account.disabled', PassportAccountDisabledError),
        ('backend.blackbox_failed', PassportTemporaryError),
        ('backend.database_failed', PassportTemporaryError),
        ('internal.temporary', PassportTemporaryError),
        ('track.invalid_state', PassportTrackInvalidStateError),
        ('track.not_found', PassportTrackNotFoundError),
        ('unexpected.exception', PassportPermanentError),
        ('user.not_verified', PassportUserNotVerifiedError),
    ])
    def test_get_phonish_uid_by_phone_failed(self, error_code, exception_cls):
        self.fake_passport.set_response_value(
            'get_phonish_uid_by_phone',
            json.dumps(passport_bundle_api_error_response(error_code)),
        )

        with assert_raises(exception_cls):
            self.passport.get_phonish_uid_by_phone(
                track_id=TEST_TRACK_ID1,
                user_ip=TEST_USER_IP1,
            )

    def test_send_account_modification_notifications(self):
        response = self.passport.send_account_modification_notifications(
            host=TEST_HOST,
            user_ip=TEST_USER_IP1,
            uid=TEST_UID,
            event_name='social_add',
            social_provider='vkek',
        )

        eq_(response, passport_ok_response())
        request = self.fake_passport.requests[0]
        request.assert_properties_equal(
            method='POST',
            headers={
                'Ya-Consumer-Client-Ip': TEST_USER_IP1,
                'Ya-Client-Host': TEST_HOST,
            },
        )
        request.assert_url_starts_with('http://localhost/1/bundle/account/modification/send_notifications/?')
        request.assert_query_equals(
            dict(
                consumer='passport',
            ),
        )
        request.assert_post_data_equals(dict(
            uid=TEST_UID,
            event_name='social_add',
            mail_enabled='1',
            push_enabled='1',
            social_provider='vkek',
        ))
