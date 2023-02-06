# -*- coding: utf-8 -*-
import base64
from datetime import (
    datetime,
    timedelta,
)
import json
import time

import ldap
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.authorization import (
    AUTHORIZATION_SESSION_POLICY_PERMANENT,
    AUTHORIZATION_SESSION_POLICY_SESSIONAL,
)
from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    EmailTestMixin,
    ProfileTestMixin,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    COOKIE_L_VALUE,
    COOKIE_LAH_VALUE,
    COOKIE_YP_VALUE,
    COOKIE_YS_VALUE,
    EXPECTED_L_COOKIE,
    EXPECTED_LAH_COOKIE,
    EXPECTED_MDA2_BEACON_COOKIE,
    EXPECTED_SESSIONID_COOKIE,
    EXPECTED_SESSIONID_SECURE_COOKIE,
    EXPECTED_YANDEX_LOGIN_COOKIE_TEMPLATE,
    EXPECTED_YP_COOKIE,
    EXPECTED_YS_COOKIE,
    FRODO_RESPONSE_OK,
    FRODO_RESPONSE_PROBABLY_SPAM_USER,
    FRODO_RESPONSE_SPAM_PDD_USER,
    FRODO_RESPONSE_SPAM_USER,
    MDA2_BEACON_VALUE,
    SESSION,
    TEST_ACCEPT_LANGUAGE,
    TEST_AUTH_ID,
    TEST_COOKIE_AGE,
    TEST_COOKIE_TIMESTAMP,
    TEST_DIFFERENT_PHONE_NUMBER,
    TEST_DOMAIN,
    TEST_FUID01_COOKIE,
    TEST_GLOBAL_LOGOUT_DATETIME,
    TEST_HOST,
    TEST_IP,
    TEST_LOGIN,
    TEST_NOT_STRONG_PASSWORD,
    TEST_NOT_STRONG_PASSWORD_CLASSES_NUMBER,
    TEST_NOT_STRONG_PASSWORD_IS_SEQUENCE,
    TEST_NOT_STRONG_PASSWORD_IS_WORD,
    TEST_NOT_STRONG_PASSWORD_LENGTH,
    TEST_NOT_STRONG_PASSWORD_QUALITY,
    TEST_NOT_STRONG_PASSWORD_SEQUENCES_NUMBER,
    TEST_OLD_AUTH_ID,
    TEST_PASSWORD,
    TEST_PASSWORD_HASH,
    TEST_PASSWORD_QUALITY,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_PHONE_NUMBER,
    TEST_RAW_ENV_FOR_PROFILE,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
    TEST_USER_PHONE,
    TEST_WEAK_PASSWORD,
    TEST_WEAK_PASSWORD_CLASSES_NUMBER,
    TEST_WEAK_PASSWORD_HASH,
    TEST_WEAK_PASSWORD_IS_SEQUENCE,
    TEST_WEAK_PASSWORD_IS_WORD,
    TEST_WEAK_PASSWORD_LENGTH,
    TEST_WEAK_PASSWORD_QUALITY,
    TEST_WEAK_PASSWORD_SEQUENCES_NUMBER,
    TEST_YANDEX_GID_COOKIE,
    TEST_YANDEXUID_COOKIE,
)
from passport.backend.api.views.bundle.auth.base import (
    CHANGE_PASSWORD_REASON_EXPIRED,
    CHANGE_PASSWORD_REASON_FLUSHED,
    CHANGE_PASSWORD_REASON_HACKED,
    CHANGE_PASSWORD_REASON_PWNED,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_ip_response,
    blackbox_create_pwd_hash_response,
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_lrandoms_response,
    blackbox_phone_bindings_response,
    blackbox_pwdhistory_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_test_pwd_hashes_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.builders.frodo.utils import get_phone_number_hash
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.conf import settings
from passport.backend.core.cookies import (
    cookie_l,
    cookie_lah,
    cookie_y,
)
from passport.backend.core.counters.change_password_counter import (
    get_per_phone_number_buckets,
    get_per_user_ip_buckets,
)
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.mailer.faker.mail_utils import assert_email_message_sent
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_being_replaced,
    assert_secure_phone_bound,
    assert_simple_phone_bound,
    assert_simple_phone_replace_secure,
    build_phone_bound,
    build_phone_secured,
    build_remove_operation,
    build_simple_replaces_secure_operations,
    event_lines_phone_secured,
    event_lines_replace_secure_operation_created,
    event_lines_secure_bind_operation_created,
    event_lines_secure_bind_operation_deleted,
    event_lines_secure_phone_bound,
    event_lines_securify_operation_created,
    event_lines_securify_operation_deleted,
    event_lines_simple_bind_operation_created,
    event_lines_simple_bind_operation_deleted,
    event_lines_simple_phone_bound,
    PhoneIdGeneratorFaker,
)
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.core.types.login.login import masked_login
from passport.backend.core.yasms.test.emails import (
    assert_user_notified_about_secure_phone_bound,
    assert_user_notified_about_secure_phone_replacement_started,
)
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)


eq_ = iterdiff(eq_)

SECURE_REPLACE_PENDING_UNTIL = 1238
TEST_SESSIONID = '0:old-session'

TEST_APP_ID = 'app-id'

TEST_PHONE_ID1 = 1
TEST_PHONE_ID2 = 2
TEST_PHONE_ID3 = 3

TEST_OPERATION_ID1 = 1
TEST_OPERATION_ID2 = 2
TEST_OPERATION_ID3 = 3
TEST_DATE = datetime(2014, 2, 26, 0, 0, 0)
PAST_DATE = datetime(2012, 2, 1, 10, 20, 30)


def build_headers(**kwargs):
    base = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )
    base.update(kwargs)
    return mock_headers(**base)


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class ChangePasswordViewTestCaseBase(
    AccountModificationNotifyTestMixin,
    BaseBundleTestViews,
    EmailTestMixin,
    ProfileTestMixin,
):
    uid = TEST_UID
    login = TEST_LOGIN
    alias_type = 'portal'
    domain = ''
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    attributes_table = 'attributes'

    pwdhistory_table = 'password_history'

    dbshardname = 'passportdbshard1'

    def create_userinfo_response(self, subscribed_to=None, dbfields=None, enabled_2fa=False,
                                 custom_attributes=None, is_different_phone_bound=False,
                                 is_secure_phone_bound=True,
                                 is_secure_phone_being_removed=False,
                                 is_simple_phone_bound=False,
                                 is_replace_secure_operation=False,
                                 is_operation_finished=False,
                                 operation_flags=None,
                                 is_password_verified=True, karma=0):
        """Обычный для этого случая ответ о пользователе - ему установлен ТБВС"""
        actual_dbfields = {
            'password_quality.quality.uid': 10,
            'password_quality.version.uid': 3,
        }
        dbfields = {'subscription.login_rule.8': 4} if dbfields is None else dbfields
        if dbfields:
            actual_dbfields.update(dbfields)

        attributes = {
            'person.firstname': 'firstname',
            'person.lastname': 'lastname',
            'account.2fa_on': '1' if enabled_2fa else None,
            'password.forced_changing_reason': '1' if dbfields.get('subscription.login_rule.8') == 4 else None,
            'password.encrypted': TEST_WEAK_PASSWORD_HASH,
        }
        if custom_attributes:
            attributes.update(custom_attributes)

        kwargs = dict(
            uid=self.uid,
            login=self.login,
            karma=karma,
            aliases={
                self.alias_type: self.login,
            },
            subscribed_to=subscribed_to or [],
            dbfields=actual_dbfields,
            attributes=attributes,
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )

        if is_secure_phone_bound:
            kwargs = deep_merge(
                kwargs,
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                ),
            )
            if is_secure_phone_being_removed:
                remove_kwargs = dict(
                    operation_id=TEST_OPERATION_ID2,
                    phone_id=TEST_PHONE_ID1,
                )
                if is_operation_finished:
                    remove_kwargs.update(finished=datetime.now())
                kwargs = deep_merge(
                    kwargs,
                    build_remove_operation(**remove_kwargs),
                )
            if is_replace_secure_operation:
                replace_kwargs = dict(
                    secure_operation_id=TEST_OPERATION_ID1,
                    secure_phone_id=TEST_PHONE_ID1,
                    simple_operation_id=TEST_OPERATION_ID2,
                    simple_phone_id=TEST_PHONE_ID2,
                    simple_phone_number=TEST_DIFFERENT_PHONE_NUMBER.e164,
                    started=datetime.now(),
                    secure_code_confirmed=datetime.now(),
                    simple_code_confirmed=datetime.now(),
                    password_verified=datetime.now() if is_password_verified else None,
                )
                if is_operation_finished:
                    replace_kwargs.update(finished=datetime.now())
                if operation_flags:
                    replace_kwargs.update(flags=operation_flags)
                kwargs = deep_merge(
                    kwargs,
                    build_phone_bound(
                        TEST_PHONE_ID2,
                        TEST_DIFFERENT_PHONE_NUMBER.e164,
                    ),
                    build_simple_replaces_secure_operations(**replace_kwargs),
                )
        if is_simple_phone_bound:
            kwargs = deep_merge(
                kwargs,
                build_phone_bound(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                ),
            )
        if is_different_phone_bound:
            kwargs = deep_merge(
                kwargs,
                build_phone_bound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_DIFFERENT_PHONE_NUMBER.e164,
                ),
            )

        return blackbox_userinfo_response(**kwargs)

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = True
            track.is_password_passed = True
            track.have_password = True
            track.uid = self.uid
            track.login = self.login
            track.human_readable_login = self.login
            track.machine_readable_login = self.login
            track.authorization_session_policy = AUTHORIZATION_SESSION_POLICY_PERMANENT
            track.password_hash = TEST_WEAK_PASSWORD_HASH
            track.old_session_age = TEST_COOKIE_AGE
            track.old_session_ip = TEST_IP
            track.old_session_create_timestamp = TEST_COOKIE_TIMESTAMP
            track.change_password_reason = CHANGE_PASSWORD_REASON_EXPIRED
            track.auth_method = 'password'

        self.default_blackbox_response = self.create_userinfo_response()

        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(
                {
                    base64.b64encode(TEST_PASSWORD_HASH): False,
                    base64.b64encode(TEST_WEAK_PASSWORD_HASH): False,
                },
            ),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        self.env.blackbox.set_blackbox_response_value(
            'checkip',
            blackbox_check_ip_response(True),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_OK)

        self._cookie_l_pack = mock.Mock(return_value=COOKIE_L_VALUE)
        self._cookie_ys_pack = mock.Mock(return_value=COOKIE_YS_VALUE)
        self._cookie_yp_pack = mock.Mock(return_value=COOKIE_YP_VALUE)
        self._cookie_lah_pack = mock.Mock(return_value=COOKIE_LAH_VALUE)

        self._phone_id_generator = PhoneIdGeneratorFaker()
        self._phone_id_generator.set_list([TEST_PHONE_ID3])

        self.patches = [
            mock.patch.object(
                cookie_l.CookieL,
                'pack',
                self._cookie_l_pack,
            ),
            mock.patch.object(
                cookie_y.SessionCookieY,
                'pack',
                self._cookie_ys_pack,
            ),
            mock.patch.object(
                cookie_y.PermanentCookieY,
                'pack',
                self._cookie_yp_pack,
            ),
            mock.patch.object(
                cookie_lah.CookieLAH,
                'pack',
                self._cookie_lah_pack,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
            self._phone_id_generator,
        ]
        for patch in self.patches:
            patch.start()

        self.expected_accounts = [
            {
                'uid': self.uid,
                'login': TEST_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_LOGIN,
            },
        ]

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.setup_profile_patches()
        self.setup_statbox_templates()

        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(ip=TEST_IP)

    def set_and_serialize_userinfo(self, blackbox_response):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        self.env.db.serialize(blackbox_response)

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.teardown_profile_patches()
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.patches
        del self._cookie_l_pack
        del self._cookie_yp_pack
        del self._cookie_ys_pack
        del self._cookie_lah_pack
        del self._phone_id_generator

    def make_request(self, headers=None, **kwargs):
        data = {
            'track_id': self.track_id,
            'password': TEST_PASSWORD,
        }
        data.update(kwargs)
        headers = build_headers() if headers is None else headers
        return self.env.client.post(
            '/2/bundle/auth/password/change_password/?consumer=dev',
            data=data,
            headers=headers,
        )

    def check_frodo_call(self, **kwargs):
        requests = self.env.frodo.requests
        eq_(len(requests), 1)
        requests[0].assert_query_equals(self.create_frodo_params(**kwargs))

    def create_session_cookies(self):
        return [
            EXPECTED_SESSIONID_COOKIE,
            EXPECTED_SESSIONID_SECURE_COOKIE,
            EXPECTED_MDA2_BEACON_COOKIE,
        ]

    def create_other_cookies(self, with_lah=True):
        result = [
            EXPECTED_YP_COOKIE,
            EXPECTED_YS_COOKIE,
            EXPECTED_L_COOKIE,
            EXPECTED_YANDEX_LOGIN_COOKIE_TEMPLATE % self.login,
        ]
        if with_lah:
            result.append(EXPECTED_LAH_COOKIE)
        return result

    def create_cookies(self, with_lah=True):
        return self.create_session_cookies() + self.create_other_cookies(with_lah=with_lah)

    def create_frodo_params(self, karma=0, **kwargs):
        params = {
            'uid': str(self.uid),
            'login': self.login,
            'from': '',
            'consumer': 'dev',
            'passwd': '10.0.9.1',
            'passwdex': '3.6.0.0',
            'v2_password_quality': '80',
            'hintqid': '',
            'hintq': '0.0.0.0.0.0',
            'hintqex': '0.0.0.0.0.0',
            'hinta': '0.0.0.0.0.0',
            'hintaex': '0.0.0.0.0.0',
            'yandexuid': TEST_YANDEXUID_COOKIE,
            'v2_yandex_gid': TEST_YANDEX_GID_COOKIE,
            'fuid': TEST_FUID01_COOKIE,
            'useragent': TEST_USER_AGENT,
            'host': TEST_HOST,
            'ip_from': TEST_IP,
            'v2_ip': TEST_IP,
            'valkey': '0000000000',
            'action': 'change_password_force',
            'xcountry': 'ru',
            'lang': 'ru',
            'v2_track_created': TimeNow(),
            'v2_old_password_quality': '10',
            'v2_account_country': 'ru',
            'v2_account_language': 'ru',
            'v2_account_timezone': 'Europe/Moscow',
            'v2_accept_language': 'ru',
            'v2_account_karma': str(karma),
            'v2_is_ssl': '1',
            'v2_has_cookie_l': '1',
            'v2_has_cookie_yandex_login': '0',
            'v2_has_cookie_my': '1',
            'v2_has_cookie_ys': '0',
            'v2_has_cookie_yp': '0',
            'v2_cookie_my_block_count': '1',
            'v2_cookie_my_language': 'tt',
            'v2_cookie_l_login': TEST_LOGIN,
            'v2_cookie_l_uid': str(TEST_UID),
            'v2_cookie_l_timestamp': str(TEST_COOKIE_TIMESTAMP),
            'v2_session_age': '',
            'v2_session_ip': '',
            'v2_session_create_timestamp': '',
        }
        params.update(**kwargs)
        return EmptyFrodoParams(**params)

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'local_base',
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            consumer='dev',
            mode='change_password_force',
        )
        self.env.statbox.bind_entry(
            'local_account_modification',
            _inherit_from='local_base',
            _exclude=['mode', 'track_id'],
            operation='updated',
            event='account_modification',
            uid=str(self.uid),
        )
        self.env.statbox.bind_entry(
            'phone_operation',
            _inherit_from='local_base',
            uid=str(self.uid),
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'changed_password',
            _inherit_from='local_base',
            action='changed_password',
            uid=str(self.uid),
            password_quality='80',
        )
        self.env.statbox.bind_entry(
            'sms_sent',
            _inherit_from='phone_operation',
            action='change_password_notification.notification_sent',
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            sms_id='1',
        )
        self.env.statbox.bind_entry(
            '_base_password_validation_error',
            action='password_validation_error',
            is_additional_word=tskv_bool(False),
            additional_subwords_number='0',
            weak='1',
        )
        self.env.statbox.bind_entry(
            'strong_password_validation_error',
            _inherit_from='_base_password_validation_error',
            password_quality=str(TEST_NOT_STRONG_PASSWORD_QUALITY),
            length=str(TEST_NOT_STRONG_PASSWORD_LENGTH),
            classes_number=str(TEST_NOT_STRONG_PASSWORD_CLASSES_NUMBER),
            sequences_number=str(TEST_NOT_STRONG_PASSWORD_SEQUENCES_NUMBER),
            is_sequence=tskv_bool(TEST_NOT_STRONG_PASSWORD_IS_SEQUENCE),
            is_word=tskv_bool(TEST_NOT_STRONG_PASSWORD_IS_WORD),
            policy='strong',
        )
        self.env.statbox.bind_entry(
            'weak_password_validation_error',
            _inherit_from='_base_password_validation_error',
            password_quality=str(TEST_WEAK_PASSWORD_QUALITY),
            length=str(TEST_WEAK_PASSWORD_LENGTH),
            classes_number=str(TEST_WEAK_PASSWORD_CLASSES_NUMBER),
            sequences_number=str(TEST_WEAK_PASSWORD_SEQUENCES_NUMBER),
            is_sequence=tskv_bool(TEST_WEAK_PASSWORD_IS_SEQUENCE),
            is_word=tskv_bool(TEST_WEAK_PASSWORD_IS_WORD),
            policy='basic',
        )
        self.env.statbox.bind_entry(
            'checked_counter',
            _inherit_from='local_base',
            action='checked_counter',
            error='phone.compromised',
            uid=str(self.uid),
        )
        self.env.statbox.bind_entry(
            'analyzed_frodo',
            _inherit_from='local_base',
            action='analyzed_frodo',
            uid=str(self.uid),
        )
        self.env.statbox.bind_entry(
            'cookie_set',
            _inherit_from=['cookie_set', 'local_base'],
            _exclude=['consumer'],
            mode='any_auth',
            session_method='edit',
            uids_count='2',
            yandexuid=TEST_YANDEXUID_COOKIE,
            ip_country='ru',
        )

    def get_expected_response(self, with_lah=True, **kwargs):
        return merge_dicts(
            {
                'cookies': self.create_cookies(with_lah=with_lah),
                'default_uid': self.uid,
                'account': {
                    'uid': self.uid,
                    'login': TEST_LOGIN,
                    'display_login': TEST_LOGIN,
                },
                'accounts': self.expected_accounts,
            },
            kwargs,
        )

    def check_response_ok(self, response, **kwargs):
        self.assert_ok_response(response, ignore_order_for=['cookies'], **self.get_expected_response(**kwargs))

    def assert_sms_not_sent(self):
        requests = self.env.yasms.requests
        eq_(requests, [])

    def check_sms_sent(self):
        self.env.statbox.assert_contains([
            self.env.statbox.entry('sms_sent'),
        ], offset=8)
        requests = self.env.yasms.requests
        requests[-1].assert_query_contains({
            'from_uid': str(self.uid),
            'text': u'Пароль от Вашего аккаунта на Яндексе изменён. Подробности в Почте.',
        })

    def _assert_user_notified_about_password_change(self):
        assert_email_message_sent(
            mailer_faker=self.env.mailer,
            email_address='%s@%s' % (TEST_LOGIN, 'gmail.com'),
            subject=u'Аккаунт на Яндексе: изменение пароля',
            body=u'''
<!doctype html>
<html>
<head>
<meta http-equiv="Content-Type"  content="text/html; charset=UTF-8" />
<title></title>
<style>.mail-address a,
        .mail-address a[href] {
            text-decoration: none !important;
            color: #000000 !important;
        }</style>
</head>
<body>
<table cellpadding="0" cellspacing="0" align="center" width="770px">
  <tr>
    <td>
      <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/7F_vkMrD7zJqJbvEsNzd2YQleQI.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">
      <table width="100%%" cellpadding="0" cellspacing="0" align="center">
        <tr>
          <td>
            <p>Здравствуйте, firstname!</p>

            <p>Пароль к Вашему аккаунту %(login)s изменён. Если это сделали Вы, то
            не обращайте внимания на это письмо.</p>

            <p>Если Вы не изменяли пароль, это мог сделать злоумышленник.
            В таком случае перейдите на
            <a href='https://feedback2.yandex.ru/passport/security/'>страницу службы поддержки</a>
            и следуйте указанным на ней рекомендациям.</p>

            <p>С заботой о безопасности Вашего аккаунта,<br> команда Яндекс ID</p>
          </td>
        </tr>
      </table>
      <table width="100%%" cellpadding="0" cellspacing="0" align="center">
        <tr><td></td></tr>
        <tr>
          <td>Пожалуйста, не отвечайте на это письмо. Связаться со службой
            поддержки Яндекса Вы можете через
            <a href='https://feedback2.yandex.ru/'>форму обратной связи</a>.</td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>
        ''' % {'login': masked_login(self.login)},
        )

    def check_ok(self, response, check_db=True, central_query_count=0, sharddb_query_count=3,
                 check_frodo=True, check_statbox=True,
                 check_change_password_notify=True, yandexuid=TEST_YANDEXUID_COOKIE,
                 frodo_action=None, frodo_old_password_quality='10',
                 frodo_phone_number=None, response_args=None, check_replace_secure_notify=False,
                 check_secure_bound_notify=False,
                 password_history_reason=blackbox.constants.BLACKBOX_PWDHISTORY_REASON_COMPROMISED,
                 secure_phone_number=TEST_PHONE_NUMBER, check_phone_log=True, app_id=None):
        if response_args is None:
            response_args = {}

        self.check_response_ok(response, **response_args)

        if check_db:
            timenow = TimeNow()

            eq_(self.env.db.query_count('passportdbcentral'), central_query_count)
            eq_(self.env.db.query_count(self.dbshardname), sharddb_query_count)

            self.env.db.check(self.attributes_table, 'account.global_logout_datetime', timenow, uid=self.uid, db=self.dbshardname)
            self.env.db.check(self.attributes_table, 'password.update_datetime', timenow, uid=self.uid, db=self.dbshardname)
            self.env.db.check(self.attributes_table, 'password.quality', '3:80', uid=self.uid, db=self.dbshardname)
            self.env.db.check_missing(self.attributes_table, 'password.forced_changing_reason', uid=self.uid, db=self.dbshardname)
            self.env.db.check_missing(self.attributes_table, 'password.forced_changing_time', uid=self.uid, db=self.dbshardname)
            self.env.db.check_missing(self.attributes_table, 'password.is_creating_required', uid=self.uid, db=self.dbshardname)

            self.check_and_get_password()
            self.env.db.check(
                self.pwdhistory_table,
                'encrypted_password',
                TEST_WEAK_PASSWORD_HASH,
                uid=self.uid,
                db=self.dbshardname,
            )
            self.env.db.check(self.pwdhistory_table, 'ts', DatetimeNow(), uid=self.uid, db=self.dbshardname)
            self.env.db.check(self.pwdhistory_table, 'reason', password_history_reason, uid=self.uid, db=self.dbshardname)

        if frodo_action is None:
            frodo_action = 'change_password_force'

        if check_statbox:
            # Проверим последнуюю запись в statbox
            self.env.statbox.assert_contains([
                self.env.statbox.entry('changed_password'),
            ], offset=-1)

        track = self.track_manager.read(self.track_id)
        ok_(track.session)
        if check_frodo:
            frodo_args = dict(action=frodo_action, v2_old_password_quality=frodo_old_password_quality)
            if frodo_phone_number:
                frodo_args.update(
                    phonenumber=frodo_phone_number.masked_format_for_frodo,
                    v2_phonenumber_hash=get_phone_number_hash(frodo_phone_number.e164),
                )
            if app_id is not None:
                frodo_args.update(
                    v2_application=app_id,
                )
            self.check_frodo_call(**frodo_args)

        if check_change_password_notify:
            self._assert_user_notified_about_password_change()

        if check_replace_secure_notify:
            self._assert_user_notified_about_secure_phone_replace()

        if check_secure_bound_notify:
            self._assert_user_notified_about_secure_phone_bound()

        if check_phone_log:
            self.env.phone_logger.assert_has_written([
                self.env.phone_logger.get_log_entry(
                    self.uid,
                    secure_phone_number.e164,
                    yandexuid,
                ),
            ])

        userinfo_request = self.env.blackbox.requests[0]
        userinfo_request.assert_post_data_contains({
            'method': 'userinfo',
            'aliases': 'all_with_hidden',
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
        })
        userinfo_request.assert_contains_attributes({
            'phones.secure',
            'phones.default',
        })

    def _assert_user_notified_about_secure_phone_replace(self):
        assert_user_notified_about_secure_phone_replacement_started(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address='%s@%s' % (TEST_LOGIN, 'gmail.com'),
            firstname='firstname',
            login=masked_login(self.login),
        )
        assert_user_notified_about_secure_phone_replacement_started(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address='%s@%s' % (TEST_LOGIN, 'yandex.ru'),
            firstname='firstname',
            login=self.login,
        )

    def _assert_user_notified_about_secure_phone_bound(self):
        assert_user_notified_about_secure_phone_bound(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address='%s@%s' % (TEST_LOGIN, 'gmail.com'),
            firstname='firstname',
            login=masked_login(self.login),
        )
        assert_user_notified_about_secure_phone_bound(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address='%s@%s' % (TEST_LOGIN, 'yandex.ru'),
            firstname='firstname',
            login=self.login,
        )

    def check_and_get_password(self):
        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=self.uid, db=self.dbshardname)
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('1:'))
            ok_(eav_pass_hash != '1:' + TEST_PASSWORD_HASH)

        return eav_pass_hash

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])


class BaseTestCase(ChangePasswordViewTestCaseBase):
    def setUp(self):
        super(BaseTestCase, self).setUp()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.change_password_reason = CHANGE_PASSWORD_REASON_HACKED

    def assert_yasms_phone_updated(self, phone_number=TEST_PHONE_NUMBER):
        assert_secure_phone_bound.check_db(
            db_faker=self.env.db,
            uid=self.uid,
            phone_attributes={
                'id': TEST_PHONE_ID1,
                'number': phone_number.e164,
                'confirmed': DatetimeNow(),
            },
        )

    def check_log_entries(self, password_hash,
                          old_secure_phone=None, update_old_secure_phone=False,
                          new_phone=None, replace_secure_phone=False,
                          bind_new_secure_phone=False,
                          is_conflicted_operation_exists=False,
                          is_yasms_errors_when_replacing_phone=False,
                          show_2fa_promo=None, new_phone_id=TEST_PHONE_ID1,
                          operation_id1=1, old_secure_phone_id=TEST_PHONE_ID1,
                          operation_id2=2, is_phone_securified=False):
        self.check_historydb(
            password_hash=password_hash,
            old_secure_phone=old_secure_phone,
            update_old_secure_phone=update_old_secure_phone,
            new_phone=new_phone,
            replace_secure_phone=replace_secure_phone,
            bind_new_secure_phone=bind_new_secure_phone,
            is_conflicted_operation_exists=is_conflicted_operation_exists,
            is_yasms_errors_when_replacing_phone=is_yasms_errors_when_replacing_phone,
            new_phone_id=new_phone_id,
            operation_id1=operation_id1,
            old_secure_phone_id=old_secure_phone_id,
            operation_id2=operation_id2,
            is_phone_securified=is_phone_securified,
        )
        self.check_statbox(
            old_secure_phone=old_secure_phone,
            update_old_secure_phone=update_old_secure_phone,
            new_phone=new_phone,
            replace_secure_phone=replace_secure_phone,
            bind_new_secure_phone=bind_new_secure_phone,
            is_conflicted_operation_exists=is_conflicted_operation_exists,
            is_yasms_errors_when_replacing_phone=is_yasms_errors_when_replacing_phone,
            show_2fa_promo=show_2fa_promo,
        )

    def check_historydb(self, password_hash,
                        old_secure_phone=None, update_old_secure_phone=False,
                        new_phone=None, replace_secure_phone=False,
                        bind_new_secure_phone=False,
                        is_conflicted_operation_exists=False,
                        is_yasms_errors_when_replacing_phone=False,
                        new_phone_id=TEST_PHONE_ID1,
                        operation_id1=1, old_secure_phone_id=TEST_PHONE_ID1,
                        operation_id2=2, is_phone_securified=False, user_agent=TEST_USER_AGENT):
        # Одна запись в historydb о смене пароля
        self.env.event_logger.assert_contains([
            {'uid': str(self.uid), 'name': 'info.password_quality', 'value': '80'},
            {'uid': str(self.uid), 'name': 'info.password', 'value': password_hash},
            {'uid': str(self.uid), 'name': 'info.glogout', 'value': TimeNow()},
            {'uid': str(self.uid), 'name': 'info.password_update_time', 'value': TimeNow()},
            {'uid': str(self.uid), 'name': 'sid.login_rule', 'value': '8|1'},
            {'uid': str(self.uid), 'name': 'action', 'value': 'change_password'},
            {'uid': str(self.uid), 'name': 'consumer', 'value': 'dev'},
            {'uid': str(self.uid), 'name': 'user_agent', 'value': user_agent},
        ])
        # Запись в auth-log о создании сессии
        expected_log_records = [
            [
                ('uid', str(self.uid)),
                ('status', 'ses_create'),
                ('type', authtypes.AUTH_TYPE_WEB),
                ('client_name', 'passport'),
                ('useragent', user_agent),
                ('ip_from', TEST_IP),
            ],
        ]
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            expected_log_records,
        )

        if update_old_secure_phone:
            self.env.event_logger.assert_contains([
                {'uid': str(self.uid), 'name': 'action', 'value': 'change_password'},
                {'uid': str(self.uid), 'name': 'phone.1.number', 'value': old_secure_phone.e164},
                {'uid': str(self.uid), 'name': 'phone.1.action', 'value': 'changed'},
                {'uid': str(self.uid), 'name': 'phone.1.confirmed', 'value': TimeNow()},
                {'uid': str(self.uid), 'name': 'consumer', 'value': 'dev'},
                {'uid': str(self.uid), 'name': 'user_agent', 'value': user_agent},
            ])

        if bind_new_secure_phone:
            if not is_phone_securified:
                self.env.event_logger.assert_contains(
                    event_lines_secure_bind_operation_created(
                        uid=self.uid,
                        phone_id=new_phone_id,
                        phone_number=new_phone,
                        operation_id=operation_id1,
                        operation_ttl=timedelta(seconds=60),
                    ) +
                    (
                        {'uid': str(self.uid), 'name': 'action', 'value': 'acquire_phone'},
                        {'uid': str(self.uid), 'name': 'consumer', 'value': 'dev'},
                        {'uid': str(self.uid), 'name': 'user_agent', 'value': user_agent},
                    ) +
                    event_lines_secure_bind_operation_deleted(
                        uid=self.uid,
                        phone_id=new_phone_id,
                        phone_number=new_phone,
                        operation_id=operation_id1,
                        action='change_password',
                        user_agent=user_agent,
                    ) +
                    event_lines_secure_phone_bound(
                        uid=self.uid,
                        phone_id=new_phone_id,
                        phone_number=new_phone,
                        operation_id=operation_id1,
                        action='change_password',
                        user_agent=user_agent,
                    ),
                )
            else:
                self.env.event_logger.assert_contains(
                    event_lines_securify_operation_created(
                        uid=self.uid,
                        phone_id=new_phone_id,
                        phone_number=new_phone,
                        operation_id=operation_id1,
                        operation_ttl=timedelta(seconds=60),
                        user_agent=user_agent,
                    ) +
                    event_lines_securify_operation_deleted(
                        uid=self.uid,
                        phone_id=new_phone_id,
                        phone_number=new_phone,
                        operation_id=operation_id1,
                        action='change_password',
                        user_agent=user_agent,
                    ) +
                    event_lines_phone_secured(
                        uid=self.uid,
                        phone_id=new_phone_id,
                        phone_number=new_phone,
                        action='change_password',
                        user_agent=user_agent,
                    ),
                )

        if replace_secure_phone:
            self.env.event_logger.assert_contains(
                event_lines_replace_secure_operation_created(
                    uid=self.uid,
                    replacement_phone_id=new_phone_id,
                    replacement_phone_number=new_phone,
                    replacement_operation_id=operation_id2,
                    secure_phone_id=old_secure_phone_id,
                    secure_phone_number=old_secure_phone,
                    secure_operation_id=operation_id1,
                    operation_ttl=timedelta(seconds=60),
                    user_agent=user_agent,
                ) +
                event_lines_simple_phone_bound(
                    uid=self.uid,
                    phone_id=new_phone_id,
                    phone_number=new_phone,
                    operation_id=operation_id2,
                    action='change_password',
                    user_agent=user_agent,
                ) +
                event_lines_simple_bind_operation_deleted(
                    uid=self.uid,
                    phone_id=new_phone_id,
                    phone_number=new_phone,
                    operation_id=operation_id2,
                    action='change_password',
                    user_agent=user_agent,
                ) +
                event_lines_replace_secure_operation_created(
                    uid=self.uid,
                    replacement_phone_id=new_phone_id,
                    replacement_phone_number=new_phone,
                    replacement_operation_id=operation_id2 + 1,
                    secure_phone_id=old_secure_phone_id,
                    secure_phone_number=old_secure_phone,
                    secure_operation_id=operation_id1,
                    operation_ttl=timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                    is_replacement_phone_bound=True,
                    user_agent=user_agent,
                ),
            )

        if is_conflicted_operation_exists or is_yasms_errors_when_replacing_phone:
            self.env.event_logger.assert_contains(
                event_lines_simple_bind_operation_created(
                    uid=self.uid,
                    phone_id=new_phone_id,
                    phone_number=new_phone,
                    operation_id=operation_id1,
                    operation_ttl=timedelta(seconds=60),
                    user_agent=user_agent,
                ) +
                event_lines_simple_bind_operation_deleted(
                    uid=self.uid,
                    phone_id=new_phone_id,
                    phone_number=new_phone,
                    operation_id=operation_id1,
                    action='change_password',
                    user_agent=user_agent,
                ) +
                event_lines_simple_phone_bound(
                    uid=self.uid,
                    phone_id=new_phone_id,
                    phone_number=new_phone,
                    operation_id=operation_id1,
                    action='change_password',
                    user_agent=user_agent,
                ),
            )

    def check_statbox(self, old_secure_phone=None, update_old_secure_phone=False,
                      new_phone=None, replace_secure_phone=False,
                      bind_new_secure_phone=False,
                      is_conflicted_operation_exists=False,
                      is_yasms_errors_when_replacing_phone=False,
                      show_2fa_promo=None):

        expected_log_entries = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'analyzed_frodo',
                karma_prefix='0',
                is_karma_prefix_returned='0',
            ),
        ]

        if update_old_secure_phone:
            statbox_update_old_secure_phone_lines = [
                self.env.statbox.entry(
                    'phone_operation',
                    operation='update',
                    number=old_secure_phone.masked_format_for_statbox,
                ),
            ]
        if bind_new_secure_phone or is_conflicted_operation_exists or is_yasms_errors_when_replacing_phone:
            statbox_bind_new_phone_lines = [
                self.env.statbox.entry(
                    'phone_operation',
                    operation='save',
                    number=new_phone.masked_format_for_statbox,
                ),
            ]
        if replace_secure_phone:
            if not is_yasms_errors_when_replacing_phone:
                statbox_replace_secure_phone_lines = [
                    self.env.statbox.entry(
                        'phone_operation',
                        operation='replace',
                        number=new_phone.masked_format_for_statbox,
                    ),
                ]
            else:
                statbox_replace_secure_phone_lines = [
                    self.env.statbox.entry(
                        'phone_operation',
                        operation='replace',
                        error='phone.isnt_saved',
                        number=new_phone.masked_format_for_statbox,
                    ),
                ]

        expected_log_entries += [
            self.env.statbox.entry(
                'local_account_modification',
                entity='password.encrypted',
            ),
            self.env.statbox.entry(
                'local_account_modification',
                entity='password.quality',
                old='10',
                new=str(TEST_PASSWORD_QUALITY),
            ),
        ]

        if update_old_secure_phone:
            expected_log_entries += statbox_update_old_secure_phone_lines

        if bind_new_secure_phone:
            expected_log_entries += statbox_bind_new_phone_lines

        if replace_secure_phone:
            expected_log_entries += statbox_replace_secure_phone_lines

        if is_conflicted_operation_exists or is_yasms_errors_when_replacing_phone:
            expected_log_entries += statbox_bind_new_phone_lines

        expected_log_entries += [
            self.env.statbox.entry(
                'cookie_set',
                input_login=self.login,
                session_method='create',
                uids_count='1',
            ),
            self.env.statbox.entry(
                'changed_password',
                is_bound_new_secure_phone=tskv_bool(bind_new_secure_phone),
                is_updated_current_secure_phone=tskv_bool(update_old_secure_phone),
                is_replaced_phone_with_quarantine=tskv_bool(
                    replace_secure_phone and
                    not is_yasms_errors_when_replacing_phone and
                    not is_conflicted_operation_exists,
                ),
                is_conflicted_operation_exists=tskv_bool(is_conflicted_operation_exists),
                is_yasms_errors_when_replacing_phone=tskv_bool(is_yasms_errors_when_replacing_phone),
            ),
        ]

        # Обновляем информацию про телефон в последней записи в статбокс
        if show_2fa_promo:
            expected_log_entries[-1]['show_2fa_promo'] = '1'

        self.env.statbox.assert_contains(expected_log_entries)


@with_settings_hosts(
    PASSPORT_SUBDOMAIN='passport-test',
    FORBIDDEN_CHANGE_PASSWORD_WITH_BAD_FRODO_KARMA=False,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class ChangePasswordViewTestCase(ChangePasswordViewTestCaseBase):
    def test_ok(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)

        rv = self.make_request()

        self.check_ok(rv)

        # убедились, что не выставили флажок is_lite
        createsession = self.env.blackbox.get_requests_by_method('createsession')
        createsession[0].assert_query_contains({'is_lite': '0'})

        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='changed_password',
            uid=self.uid,
            title='Пароль в аккаунте {} успешно изменён'.format(TEST_LOGIN),
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
        )

    def test_ok_with_env_profile_modification(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)

        rv = self.make_request()

        self.check_response_ok(rv)
        profile = self.make_user_profile(raw_env=TEST_RAW_ENV_FOR_PROFILE)
        self.assert_profile_written_to_auth_challenge_log(profile)

    def test_password_strong_policy_ok(self):
        blackbox_response = self.create_userinfo_response(
            subscribed_to=[67],
            dbfields={
                'subscription.login_rule.67': 1,
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True

        self.set_and_serialize_userinfo(blackbox_response)

        rv = self.make_request()

        self.check_ok(
            rv,
            sharddb_query_count=3,
            frodo_action='change_password_to_strong',
            frodo_old_password_quality='10',
            password_history_reason=blackbox.constants.BLACKBOX_PWDHISTORY_REASON_STRONG_POLICY,
        )

        self.check_and_get_password()

        # убедились, что не выставили флажок is_lite
        createsession = self.env.blackbox.get_requests_by_method('createsession')
        createsession[0].assert_query_contains({'is_lite': '0'})

    def test_ok_short_session(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.authorization_session_policy = AUTHORIZATION_SESSION_POLICY_SESSIONAL

        self.set_and_serialize_userinfo(self.default_blackbox_response)
        rv = self.make_request()
        self.check_ok(
            rv,
            response_args={'with_lah': False},
        )

        # убедились, что не выставили флажок is_lite
        createsession = self.env.blackbox.get_requests_by_method('createsession')
        createsession[0].assert_query_contains({'is_lite': '0'})

    def test_ok_with_empty_headers(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)

        rv = self.make_request(
            headers=mock_headers(
                host=TEST_HOST,
                user_ip=TEST_IP,
                user_agent='',
                cookie='',
                referer='',
            ),
        )
        self.check_ok(
            rv,
            check_frodo=False,
            check_statbox=False,
            yandexuid='',
        )
        self.check_frodo_call(
            useragent='',
            v2_accept_language='',
            valkey='0000000100',
            fuid='',
            yandexuid='',
            v2_yandex_gid='',
            v2_has_cookie_my='0',
            v2_has_cookie_l='0',
            v2_cookie_my_block_count='',
            v2_cookie_my_language='',
            v2_cookie_l_uid='',
            v2_cookie_l_login='',
            v2_cookie_l_timestamp='',
        )
        self.env.statbox.assert_contains([
            self.env.statbox.entry('changed_password', user_agent=''),
        ], offset=-1)

    def test_change_passwd__wrong_host__error(self):
        rv = self.make_request(headers=mock_headers(
            host='google.com',
            user_ip=TEST_IP,
            user_agent='',
            cookie=TEST_USER_COOKIES,
        ))

        self.assert_error_response(rv, error_codes=['host.invalid'])

    def test_incomplete_track_no_uid_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = None

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['track.invalid_state'])

    def test_blackbox_userinfo_no_uid_error(self):
        """ЧЯ вернул пустой ответ по методу userinfo - ошибка обрабатывается"""
        userinfo_response = blackbox_userinfo_response(uid=None)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['account.not_found'])

    def test_blackbox_user_is_disabled_error(self):
        """Пользователь с этим uid "выкл" (disabled) - ошибка обрабатывается"""
        blackbox_response = blackbox_userinfo_response(enabled=False)
        self.set_and_serialize_userinfo(blackbox_response)

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['account.disabled'])

    def test_blackbox_user_is_disabled_on_deletion_error(self):
        """
        Пользователь с этим uid "выкл" (disabled), и он подписан на 20 сид --
        ошибка обрабатывается.
        """
        blackbox_response = blackbox_userinfo_response(
            enabled=False,
            attributes={
                'account.is_disabled': ACCOUNT_DISABLED_ON_DELETION,
            },
        )
        self.set_and_serialize_userinfo(blackbox_response)

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['account.disabled_on_deletion'])

    def test_2fa_password_change_not_required(self):
        """
        Нет смысла менять пароль, если у пользователя включен 2FA.
        """
        blackbox_response = self.create_userinfo_response(
            dbfields={},
            enabled_2fa=True,
        )
        self.set_and_serialize_userinfo(blackbox_response)

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['action.not_required'])

    def test_2fa_67_sid_password_change_not_required(self):
        """
        Если у пользователя включен 2FA, то даже наличие 67 сида - не повод
        менять пароль.
        """
        blackbox_response = self.create_userinfo_response(
            subscribed_to=[67],
            dbfields={'subscription.login_rule.67': 1},
            enabled_2fa=True,
        )
        self.set_and_serialize_userinfo(blackbox_response)

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['action.not_required'])

    def test_2fa_is_changing_required(self):
        """
        Если у пользователя включен 2FA и стоит флаг принудительной
        смены пароля, то все равно не даем сменить пароль.
        """
        blackbox_response = self.create_userinfo_response(
            dbfields={'subscription.login_rule.8': 4},
            enabled_2fa=True,
        )
        self.set_and_serialize_userinfo(blackbox_response)

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['action.not_required'])

    def test_no_67_sid_no_8_sid_error(self):
        blackbox_response = self.create_userinfo_response(dbfields={})
        self.set_and_serialize_userinfo(blackbox_response)

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['action.not_required'])

    def test_is_password_change_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = False

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['track.invalid_state'])

    def test_password_found_in_history_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=True),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True

        self.set_and_serialize_userinfo(self.default_blackbox_response)

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['password.found_in_history'])

    def test_strong_password_weak_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True

        self.set_and_serialize_userinfo(self.default_blackbox_response)

        rv = self.make_request(password=TEST_NOT_STRONG_PASSWORD)

        self.assert_error_response(rv, error_codes=['password.weak'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('strong_password_validation_error'),
        ])

    def test_password_too_weak_error(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)

        rv = self.make_request(password=TEST_WEAK_PASSWORD)

        self.assert_error_response(rv, error_codes=['password.weak'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('weak_password_validation_error'),
        ])

    def test_password_equals_previous_error(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.password_hash = TEST_PASSWORD_HASH
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(
                {
                    base64.b64encode(TEST_PASSWORD_HASH): True,
                },
            ),
        )

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['password.equals_previous'])

    def test_password_equals_phone_error(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_USER_PHONE
            track.phone_confirmation_is_confirmed = True

        rv = self.make_request(password=TEST_USER_PHONE)

        self.assert_error_response(rv, error_codes=['password.likephonenumber'])

    def test_account_global_logout_after_track_created_error(self):
        """
        Хотим сменить пароль на принудительной смене, но аккаунт был глобально
        разлогинен уже после того, как завели трек для принудительной смены.
        """
        self.set_and_serialize_userinfo(
            self.create_userinfo_response(
                custom_attributes={
                    'account.global_logout_datetime': str(int(time.time()) + 1),
                },
            ),
        )

        rv = self.make_request(password='brand_new_password')

        self.assert_error_response(rv, error_codes=['account.global_logout'])

    def test_passwd_change__passwd_changing_required__and_frodo_was_called_right(self):
        """
        В ФО сообщется верная причина смены пароля - пользователю выставлен
        ТБВС.
        """
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_SPAM_USER)
        self.env.frodo.set_response_value(u'confirm', u'')

        response = self.make_request()

        self.check_response_ok(response)

        self.env.db.check(
            self.attributes_table,
            'karma.value',
            '85',
            uid=self.uid,
            db=self.dbshardname,
        )

        # Проверяем параметры для frodo
        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(self.create_frodo_params())

    def test_passwd_change__67_sid__reported_to_frodo(self):
        """
        В ФО сообщется верная причина смены пароля - пароль устарел или слишком прост для sid=67
        На этапе смены пароля мы не можем различить эти два случая
        """
        blackbox_response = self.create_userinfo_response(
            subscribed_to=[67],
            dbfields={'subscription.login_rule.67': 1},
        )
        self.set_and_serialize_userinfo(blackbox_response)

        rv = self.make_request()

        self.check_ok(
            rv,
            sharddb_query_count=3,
            check_frodo=False,
            password_history_reason=blackbox.constants.BLACKBOX_PWDHISTORY_REASON_STRONG_POLICY,
        )
        self.check_frodo_call(action='change_password_to_strong')

    def test_change_password__frodo_changed_karma__report_to_statbox__sms_notification(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        self.env.frodo.set_response_value(
            u'check',
            FRODO_RESPONSE_PROBABLY_SPAM_USER,
        )
        self.env.frodo.set_response_value(u'confirm', u'')

        rv = self.make_request()

        self.check_ok(
            rv,
            sharddb_query_count=4,
            check_frodo=False,
            check_statbox=False,
        )

        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(self.create_frodo_params())

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'analyzed_frodo',
                karma_prefix='7',
                is_karma_prefix_returned='1',
            ),
            self.env.statbox.entry(
                'local_account_modification',
                entity='account.global_logout_datetime',
                new=DatetimeNow(convert_to_datetime=True),
                old=TEST_GLOBAL_LOGOUT_DATETIME,
            ),
            self.env.statbox.entry(
                'local_account_modification',
                entity='password.is_changing_required',
                operation='deleted',
                new='-',
                old='1',
            ),
        ], offset=2)

        self._assert_user_notified_about_password_change()
        self.check_sms_sent()

    def test_subscribe_user(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.service = 'lenta'

        self.set_and_serialize_userinfo(self.default_blackbox_response)

        rv = self.make_request()

        self.check_ok(
            rv,
            check_frodo=False,
        )

        self.env.db.check(
            self.attributes_table,
            'subscription.23',
            '1',
            uid=self.uid,
            db=self.dbshardname,
        )

        self.check_frodo_call(**{
            'from': 'lenta',
            'v2_session_create_timestamp': '',
            'v2_session_age': '',
            'v2_session_ip': '',
        })

        eav_pass_hash = self.check_and_get_password()

        actual_log_entries = {
            'action': 'change_password',
            'consumer': 'dev',
            'info.glogout': TimeNow(),
            # Пароль
            'info.password_quality': '80',
            'info.password': eav_pass_hash,
            'info.password_update_time': TimeNow(),
            'sid.login_rule': '8|1',
            'sid.add': '23',
            'user_agent': TEST_USER_AGENT,
        }
        self.assert_events_are_logged(self.env.handle_mock, actual_log_entries)

    def test_error_authorization_already_passed(self):
        """В треке указано, что авторизация уже пройдена"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = SESSION['session']['value']

        resp = self.make_request()

        self.assert_error_response(resp, error_codes=['account.auth_passed'])
        eq_(self.env.auth_handle_mock.call_count, 0)

    def test_error_captcha_required(self):
        """В треке указано, что нужна капча и она не пройдена"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True

        resp = self.make_request()

        self.assert_error_response(resp, error_codes=['captcha.required'])
        eq_(self.env.auth_handle_mock.call_count, 0)

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_recognized is None)

    def test_captcha_required_with_other_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.set_and_serialize_userinfo(self.default_blackbox_response)
        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError)

        resp = self.make_request()

        self.assert_error_response(resp, error_codes=['backend.database_failed'])
        eq_(self.env.auth_handle_mock.call_count, 0)

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_recognized)

    def test_captcha_required_and_passed(self):
        """В треке указано, что нужна капча и она пройдена"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.set_and_serialize_userinfo(self.default_blackbox_response)

        rv = self.make_request()
        self.check_ok(
            rv,
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_recognized)

    def test_change_password__db_error__respond_error(self):
        """При работе с БД возникла ошибка - ошибка обрабатывается"""
        self.set_and_serialize_userinfo(self.default_blackbox_response)

        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError)

        resp = self.make_request()

        # Штатная ошибка
        self.assert_error_response(resp, error_codes=['backend.database_failed'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'analyzed_frodo',
                karma_prefix='0',
                is_karma_prefix_returned='0',
            ),
            self.env.statbox.entry(
                'local_base',
                uid=str(self.uid),
                action='error',
                errors='backend.database_failed',
                password_quality=str(TEST_PASSWORD_QUALITY),
            ),
        ])

    def test_show_2fa_promo_flag__flag_unset(self):
        self.set_and_serialize_userinfo(self.create_userinfo_response(
            custom_attributes={
                'account.show_2fa_promo': '1',
            },
        ))

        resp = self.make_request()

        self.check_response_ok(resp)
        self.env.db.check_missing(
            self.attributes_table,
            'account.show_2fa_promo',
            uid=self.uid,
            db=self.dbshardname,
        )


@with_settings_hosts(
    PASSPORT_SUBDOMAIN='passport-test',
    IS_INTRANET=True,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class ChangePasswordIntranetTestCase(ChangePasswordViewTestCaseBase):
    def setUp(self):
        super(ChangePasswordIntranetTestCase, self).setUp()

        self.ldap_bind_mock = mock.Mock(return_value=None)
        self.ldap_search_mock = mock.Mock(return_value=[
            (
                'CN=Firstname Lastname,CN=Users,DC=tst,DC=virtual',
                {'cn': ['Firstname Lastname']},
            ),
        ])
        self.ldap_modify_mock = mock.Mock(return_value=None)
        self.ldap_mock = mock.Mock()
        self.ldap_mock.simple_bind_s = self.ldap_bind_mock
        self.ldap_mock.search_s = self.ldap_search_mock
        self.ldap_mock.modify_s = self.ldap_modify_mock
        self.ldap_patch = mock.patch('ldap.initialize', mock.Mock(return_value=self.ldap_mock))
        self.ldap_patch.start()

        self.set_and_serialize_userinfo(self.default_blackbox_response)

    def tearDown(self):
        self.ldap_patch.stop()
        super(ChangePasswordIntranetTestCase, self).tearDown()

    def test_ok(self):
        rv = self.make_request(current_password=TEST_WEAK_PASSWORD)

        self.check_ok(
            rv,
            check_db=False,
            check_frodo=False,
            check_statbox=False,
        )
        ok_(self.ldap_modify_mock.called)
        assert self.ldap_mock.simple_bind_s.call_args.args == (
            '%s@%s' % (settings.PASSPORT_ROBOT_LOGIN, settings.LDAP_USER_DOMAIN), settings.PASSPORT_ROBOT_PASSWORD,
        )

    def test_current_password_not_passed_error(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['current_password.empty'])
        ok_(not self.ldap_modify_mock.called)

    def test_current_password_not_matched_error(self):
        self.ldap_bind_mock.side_effect = ldap.INVALID_CREDENTIALS
        rv = self.make_request(current_password=TEST_WEAK_PASSWORD)

        self.assert_error_response(rv, ['password.not_matched'])
        ok_(not self.ldap_modify_mock.called)

    def test_new_password_invalid_error(self):
        self.ldap_modify_mock.side_effect = ldap.CONSTRAINT_VIOLATION
        rv = self.make_request(current_password=TEST_WEAK_PASSWORD)

        self.assert_error_response(rv, ['password.change_forbidden'])
        ok_(self.ldap_modify_mock.called)

    def test_ldap_unavailable_error(self):
        self.ldap_bind_mock.side_effect = ldap.LDAPError
        rv = self.make_request(current_password=TEST_WEAK_PASSWORD)

        self.assert_error_response(rv, ['backend.ldap_failed'])
        ok_(not self.ldap_modify_mock.called)


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=3,
    PASSPORT_SUBDOMAIN='passport-test',
    FORBIDDEN_CHANGE_PASSWORD_WITH_BAD_FRODO_KARMA=False,
    BIND_RELATED_PHONISH_ACCOUNT_APP_IDS={TEST_APP_ID},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class ChangePassword2FAPromoTestCase(BaseTestCase):
    """
    У пользователя установлен флаг для показа 2ФА промо
    """

    def get_trackid_and_patch(self):
        """Фиксируем идентификатор любого созданного трека"""
        tm, track_id = self.env.track_manager.get_manager_and_trackid()
        patch = mock.patch(
            'passport.backend.core.tracks.track_manager.create_track_id',
            mock.Mock(return_value=track_id),
        )
        return track_id, patch

    def assert_2fa_promo_unset(self):
        self.env.db.check_missing('attributes', 'account.show_2fa_promo', uid=self.uid, db=self.dbshardname)

    def assert_2fa_enable_track_contains_phone_number(self, track_id, phone_number):
        track = self.track_manager.read(track_id)
        eq_(track.uid, str(self.uid))
        eq_(track.is_it_otp_enable, True)
        eq_(track.is_otp_restore_passed, True)
        eq_(track.has_secure_phone_number, True)
        eq_(track.phone_confirmation_is_confirmed, True)
        eq_(track.can_use_secure_number_for_password_validation, True)
        eq_(track.phone_confirmation_phone_number, phone_number.e164)
        eq_(track.secure_phone_number, phone_number.e164)

    def test_change__new_phone_confirmed__enable_2fa_track_id(self):
        """
        У пользователя нет защищенного телефона
          >> Подтвердил новый телефон
          >> Ответил на КВ

          << Подготовлен трек с информацией о привязанном телефоне
          << Сброшен флаг account.show_2fa_promo
        """
        self.set_and_serialize_userinfo(self.create_userinfo_response(
            is_secure_phone_bound=False,
            is_different_phone_bound=True,  # Какой-то номер привязан
            custom_attributes={'account.show_2fa_promo': '1'},
        ))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_fuzzy_hint_answer_checked = True
            track.has_secure_phone_number = False
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164  # Подтвердили другой номер

        new_track_id, patch = self.get_trackid_and_patch()

        with patch:
            rv = self.make_request()

        self.check_ok(
            rv,
            sharddb_query_count=11,
            check_statbox=False,
            response_args={
                'is_conflicted_operation_exists': False,
                'is_bound_new_secure_phone': True,
                'is_yasms_errors_when_replacing_phone': False,
                'is_updated_current_secure_phone': False,
                'is_replaced_phone_with_quarantine': False,
                'enable_2fa_track_id': new_track_id,
            },
            frodo_phone_number=TEST_PHONE_NUMBER,
        )
        self.assert_2fa_enable_track_contains_phone_number(new_track_id, TEST_PHONE_NUMBER)
        pass_hash = self.check_and_get_password()
        self.check_log_entries(
            pass_hash,
            bind_new_secure_phone=True,
            new_phone=TEST_PHONE_NUMBER,
            show_2fa_promo=True,
            new_phone_id=TEST_PHONE_ID3,
        )
        self.env.social_binding_logger.assert_has_written([])
        self.assert_2fa_promo_unset()

    def test_change__new_phone_and_show_2fa_promo__enable_2fa_track_id(self):
        """
        У пользователя есть защищенный телефон
         >> Подтвердил свой телефон

         << Обновили время привязки телефона
         << Отдали трек с информацией о телефоне
         << Сняли флаг промо 2ФА
         << Записали событие, что можно попробовать привязать существующего фониша к этому аккаунту
        """
        self.set_and_serialize_userinfo(self.create_userinfo_response(
            custom_attributes={'account.show_2fa_promo': '1'},
        ))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.has_secure_phone_number = True
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.device_application = TEST_APP_ID

        new_track_id, patch = self.get_trackid_and_patch()

        with patch:
            rv = self.make_request()

        self.check_ok(
            rv,
            sharddb_query_count=4,
            check_statbox=False,
            response_args={
                'is_bound_new_secure_phone': False,
                'is_conflicted_operation_exists': False,
                'is_yasms_errors_when_replacing_phone': False,
                'is_updated_current_secure_phone': True,
                'is_replaced_phone_with_quarantine': False,
                'enable_2fa_track_id': new_track_id,
            },
            frodo_phone_number=TEST_PHONE_NUMBER,
            app_id=TEST_APP_ID,
        )
        ip_counter = get_per_user_ip_buckets()
        eq_(ip_counter.get(TEST_IP), 1)
        self.assert_2fa_enable_track_contains_phone_number(new_track_id, TEST_PHONE_NUMBER)
        pass_hash = self.check_and_get_password()
        self.check_log_entries(
            pass_hash,
            old_secure_phone=TEST_PHONE_NUMBER,
            update_old_secure_phone=True,
            show_2fa_promo='1',
        )

        self.assert_yasms_phone_updated()
        self.env.social_binding_logger.assert_has_written([
            self.env.social_binding_logger.entry(
                'bind_phonish_account_by_track',
                uid=str(TEST_UID),
                track_id=self.track_id,
                ip=TEST_IP,
            ),
        ])
        self.assert_2fa_promo_unset()

    def test_change__conflicted_op__no_track(self):
        """
        У пользователя есть защищенный телефон
         >> Подтвержден новый телефон
         >> Ответил на КВ
         >> ПРОИЗОШЛА ОШИБКА Я.СМС

         << Привязывается новый телефон как незащищенный
         << Нет приглашения на 2ФА промо
         << Сброшен флажок 2ФА промо
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_fuzzy_hint_answer_checked = True
            track.has_secure_phone_number = True
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164

        self.set_and_serialize_userinfo(self.create_userinfo_response(
            custom_attributes={'account.show_2fa_promo': '1'},
            is_secure_phone_being_removed=True,
        ))

        rv = self.make_request()

        self.check_ok(
            rv,
            sharddb_query_count=10,
            check_statbox=False,
            response_args={
                'is_bound_new_secure_phone': False,
                'is_conflicted_operation_exists': True,
                'is_yasms_errors_when_replacing_phone': False,
                'is_updated_current_secure_phone': False,
                'is_replaced_phone_with_quarantine': False,
            },
            frodo_phone_number=TEST_DIFFERENT_PHONE_NUMBER,
        )
        pass_hash = self.check_and_get_password()
        self.check_log_entries(
            pass_hash,
            new_phone=TEST_DIFFERENT_PHONE_NUMBER,
            new_phone_id=TEST_PHONE_ID3,
            operation_id1=TEST_OPERATION_ID3,
            is_conflicted_operation_exists=True,
            show_2fa_promo='1',
        )

        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=self.uid,
            phone_attributes={
                'id': TEST_PHONE_ID3,
                'number': TEST_DIFFERENT_PHONE_NUMBER.e164,
            },
        )

        counter = get_per_phone_number_buckets()
        eq_(counter.get(TEST_PHONE_NUMBER.e164), 0)
        eq_(counter.get(TEST_DIFFERENT_PHONE_NUMBER.e164), 0)
        ip_counter = get_per_user_ip_buckets()
        eq_(ip_counter.get(TEST_IP), 1)

        self.assert_2fa_promo_unset()

    def test_change__replace_secure_operation(self):
        """
        У пользователя есть защищенный телефон
         >> Защищенный телефон заменяется на новый телефон
         >> Защищенный телефон подтвержден
         >> Подтвержден новый телефон
         >> Ответил на КВ

         << Привязался новый телефон как защищенный
         << Нет приглашения на 2ФА промо
         << Сброшен флажок 2ФА промо
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_fuzzy_hint_answer_checked = True
            track.has_secure_phone_number = True
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164

        self.set_and_serialize_userinfo(
            self.create_userinfo_response(
                custom_attributes={'account.show_2fa_promo': '1'},
                is_simple_phone_bound=True,
                is_replace_secure_operation=True,
                is_password_verified=False,
            ),
        )
        rv = self.make_request()
        self.check_ok(
            rv,
            sharddb_query_count=9,
            check_statbox=False,
            response_args={
                'is_bound_new_secure_phone': False,
                'is_conflicted_operation_exists': False,
                'is_yasms_errors_when_replacing_phone': False,
                'is_updated_current_secure_phone': False,
                'is_replaced_phone_with_quarantine': True,
            },
            frodo_phone_number=TEST_DIFFERENT_PHONE_NUMBER,
            secure_phone_number=TEST_DIFFERENT_PHONE_NUMBER,
        )

        assert_secure_phone_bound.check_db(
            db_faker=self.env.db,
            uid=self.uid,
            phone_attributes={
                'id': TEST_PHONE_ID2,
                'number': TEST_DIFFERENT_PHONE_NUMBER.e164,
            },
        )

        counter = get_per_phone_number_buckets()
        eq_(counter.get(TEST_PHONE_NUMBER.e164), 0)
        eq_(counter.get(TEST_DIFFERENT_PHONE_NUMBER.e164), 1)
        ip_counter = get_per_user_ip_buckets()
        eq_(ip_counter.get(TEST_IP), 1)

        self.assert_2fa_promo_unset()

    def test_change_new_phone_confirmed_with_quarantine__no_track(self):
        """
        У пользователя есть защищенный телефон
         >> Подтвержден новый телефон
         >> Ответил на КВ

         << Привязывается новый защищенный телефон через карантин
         << Нет приглашения на 2ФА промо
         << Сброшен флажок 2ФА промо
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.has_secure_phone_number = True
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164
            track.is_fuzzy_hint_answer_checked = True

        self.set_and_serialize_userinfo(self.create_userinfo_response(
            custom_attributes={'account.show_2fa_promo': '1'},
        ))

        rv = self.make_request()

        self.check_ok(
            rv,
            sharddb_query_count=13,
            check_statbox=False,
            response_args={
                'secure_phone_pending_until': TimeNow(offset=settings.PHONE_QUARANTINE_SECONDS),
                'is_bound_new_secure_phone': False,
                'is_conflicted_operation_exists': False,
                'is_yasms_errors_when_replacing_phone': False,
                'is_updated_current_secure_phone': False,
                'is_replaced_phone_with_quarantine': True,
            },
            frodo_phone_number=TEST_DIFFERENT_PHONE_NUMBER,
            check_replace_secure_notify=True,
        )

        pass_hash = self.check_and_get_password()
        self.check_log_entries(
            pass_hash,
            replace_secure_phone=True,
            old_secure_phone=TEST_PHONE_NUMBER,
            new_phone=TEST_DIFFERENT_PHONE_NUMBER,
            new_phone_id=TEST_PHONE_ID3,
            show_2fa_promo='1',
        )

        assert_secure_phone_being_replaced.check_db(
            db_faker=self.env.db,
            uid=self.uid,
            phone_attributes={
                'id': TEST_PHONE_ID1,
                'number': TEST_PHONE_NUMBER.e164,
            },
            operation_attributes={
                'password_verified': DatetimeNow(),
                'code_confirmed': None,
                'finished': DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
            },
        )
        assert_simple_phone_replace_secure.check_db(
            db_faker=self.env.db,
            uid=self.uid,
            phone_attributes={
                'id': TEST_PHONE_ID3,
                'number': TEST_DIFFERENT_PHONE_NUMBER.e164,
            },
            operation_attributes={
                'password_verified': DatetimeNow(),
                'code_confirmed': DatetimeNow(),
                'finished': DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
            },
        )

        counter = get_per_phone_number_buckets()
        eq_(counter.get(TEST_PHONE_NUMBER.e164), 0)
        eq_(counter.get(TEST_DIFFERENT_PHONE_NUMBER.e164), 1)
        ip_counter = get_per_user_ip_buckets()
        eq_(ip_counter.get(TEST_IP), 1)

        self.assert_2fa_promo_unset()


@with_settings_hosts(
    ENABLE_SMS_2FA_AFTER_CHANGE_PASSWORD=True,
    PASSPORT_SUBDOMAIN='passport-test',
    FORBIDDEN_CHANGE_PASSWORD_WITH_BAD_FRODO_KARMA=False,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class ChangePasswordMultiAuthViewTestCase(ChangePasswordViewTestCaseBase):
    def setUp(self):
        super(ChangePasswordMultiAuthViewTestCase, self).setUp()
        self.expected_accounts = [
            {
                'uid': self.uid,
                'login': TEST_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_LOGIN,
            },
        ]

        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )

    def get_expected_response(self):
        return {
            'status': 'ok',
            'cookies': self.create_cookies(),
            'default_uid': self.uid,
            'account': {
                'uid': self.uid,
                'login': TEST_LOGIN,
                'display_login': TEST_LOGIN,
            },
            'accounts': self.expected_accounts,
        }

    def assert_sessionid_called(self):
        sessionid_request = self.env.blackbox.get_requests_by_method('sessionid')[0]
        sessionid_request.assert_query_contains({
            'method': 'sessionid',
            'multisession': 'yes',
            'sessionid': TEST_SESSIONID,
        })

    def assert_createsession_called(self):
        createsession_request = self.env.blackbox.get_requests_by_method('createsession')[0]
        createsession_request.assert_query_equals(
            {
                'is_lite': '0',
                'method': 'createsession',
                'lang': '0',
                'have_password': u'1',
                'ver': u'3',
                'uid': str(self.uid),
                'format': 'json',
                'keyspace': 'yandex.ru',
                'ttl': '5',
                'userip': TEST_IP,
                'host_id': '7f',
                'password_check_time': TimeNow(),
                'create_time': TimeNow(),
                'auth_time': TimeNow(as_milliseconds=True),
                'guard_hosts': 'passport-test.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )

    def assert_editsession_called(self):
        editsession_request = self.env.blackbox.get_requests_by_method('editsession')[0]
        editsession_request.assert_query_equals(
            {
                'uid': str(self.uid),
                'format': 'json',
                'sessionid': TEST_SESSIONID,
                'host': 'passport-test.yandex.ru',
                'userip': TEST_IP,
                'method': 'editsession',
                'op': 'add',
                'have_password': u'1',
                'new_default': '1',
                'keyspace': 'yandex.ru',
                'password_check_time': TimeNow(),
                'create_time': TimeNow(),
                'guard_hosts': 'passport-test.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )

    def build_auth_log_entry(self, status, uid):
        return [
            ('uid', str(uid)),
            ('status', status),
            ('type', authtypes.AUTH_TYPE_WEB),
            ('client_name', 'passport'),
            ('useragent', TEST_USER_AGENT),
            ('ip_from', TEST_IP),
        ]

    def assert_auth_and_event_log_ok(self, password_hash, expected_auth_log_records, sms_2fa_enabled=False):
        events = {
            'info.password_quality': '80',
            'info.password': password_hash,
            'info.glogout': TimeNow(),
            'info.password_update_time': TimeNow(),
            'sid.login_rule': '8|1',
            'action': 'change_password',
            'consumer': 'dev',
            'user_agent': TEST_USER_AGENT,
        }
        if sms_2fa_enabled:
            events['info.sms_2fa_on'] = '1'

        self.assert_events_are_logged(
            self.env.handle_mock,
            events,
        )
        eq_(self.env.auth_handle_mock.call_count, len(expected_auth_log_records))
        # Остальные записи об апдейте сессий для каждого валидного пользователя в куке
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            expected_auth_log_records,
        )

    def assert_statbox_cookie_set(self, **kwargs):
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'cookie_set',
                input_login=self.login,
                **kwargs
            ),
        ], offset=-2)

    def test_with_cookies__overflow_error(self):
        """
        Пришли с мультикукой, на которую
        ЧЯ говорит, что в куку больше нельзя дописать пользователей
        """
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                authid=TEST_OLD_AUTH_ID,
                age=TEST_COOKIE_AGE,
                ttl=5,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
                allow_more_users=False,
            ),
        )
        resp = self.make_request(
            headers=build_headers(cookie='Session_id=0:old-session;%s' % TEST_USER_COOKIES),
        )
        self.assert_error_response(resp, ['sessionid.overflow'])

    def test_ok_without_cookie(self):
        """
        Принудительно меняем пароль пользователю вообще без куки
        Вызов должен проходить так же как для моноавторизации
        """
        self.set_and_serialize_userinfo(self.default_blackbox_response)

        rv = self.make_request()

        self.check_ok(
            rv,
            check_frodo=False,
        )
        # Проверим фродо вручную, т.к. нужно задать часть параметров
        self.check_frodo_call(
            v2_session_create_timestamp='',
            v2_session_age='',
            v2_session_ip='',
        )
        self.assert_createsession_called()

    def test_ok_with_invalid_cookie(self):
        """
        Принудительно меняем пароль пользователю вообще c невалидной полностью кукой
        Вызов должен проходить так же как для моноавторизации
        """
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        rv = self.make_request(
            headers=build_headers(cookie='Session_id=0:old-session;%s' % TEST_USER_COOKIES),
        )

        self.check_ok(
            rv,
            check_frodo=False,
        )
        # Проверим фродо вручную, т.к. нужно задать часть параметров
        self.check_frodo_call(
            v2_session_create_timestamp='',
            v2_session_age='',
            v2_session_ip='',
        )

        self.assert_sessionid_called()
        self.assert_createsession_called()

    def test_ok_with_wrong_sessguard(self):
        """
        Поведение с неверным sessguard аналогично поведению с невалидной кукой
        """
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
            ),
        )

        rv = self.make_request(
            headers=build_headers(cookie='Session_id=0:old-session;%s' % TEST_USER_COOKIES),
        )

        self.check_ok(
            rv,
            check_frodo=False,
        )
        # Проверим фродо вручную, т.к. нужно задать часть параметров
        self.check_frodo_call(
            v2_session_create_timestamp='',
            v2_session_age='',
            v2_session_ip='',
        )

        self.assert_sessionid_called()
        self.assert_createsession_called()

    def test_ok_with_cookie_with_other_account(self):
        """
        Принудительно меняем пароль пользователю с мультикукой
        Проверим что записали в auth логи и статбокc все верно
        """
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                age=TEST_COOKIE_AGE,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
                ttl=5,
            ),
        )
        self.expected_accounts = [
            {
                'uid': 1234,
                'login': 'other_login',
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': 'other_login',
            },
            {
                'uid': self.uid,
                'login': TEST_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_LOGIN,
            },
        ]
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.old_session = TEST_SESSIONID

        rv = self.make_request(
            headers=build_headers(cookie='Session_id=0:old-session;%s' % TEST_USER_COOKIES),
        )

        self.check_ok(
            rv,
            check_frodo=False,
        )
        self.check_frodo_call(
            v2_session_create_timestamp=str(TEST_COOKIE_TIMESTAMP),
            v2_session_age=str(TEST_COOKIE_AGE),
            v2_session_ip=TEST_IP,
        )
        self.assert_sessionid_called()
        self.assert_editsession_called()

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=self.uid, db='passportdbshard1')

        self.assert_auth_and_event_log_ok(
            eav_pass_hash,
            [
                self.build_auth_log_entry('ses_update', '1234'),
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_statbox_cookie_set(old_session_uids='1234')

    def test_ok_with_cookie_with_same_valid_and_other_invalid_account(self):
        """
        Принудительно меняем пароль пользователю с мультикукой,
        в которой есть текущий аккаунт и некорректный другой.
        Проверим что записали в auth логи и статбокc все верно
        """
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=self.uid,
                    login=TEST_LOGIN,
                    age=TEST_COOKIE_AGE,
                    ip=TEST_IP,
                    time=TEST_COOKIE_TIMESTAMP,
                    ttl=5,
                ),
                uid='1234',
                login='other_login',
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )
        self.expected_accounts = [
            {
                'uid': self.uid,
                'login': TEST_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_LOGIN,
            },
            {
                'uid': 1234,
                'login': 'other_login',
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': 'other_login',
            },
        ]
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.old_session = TEST_SESSIONID
            track.change_password_reason = CHANGE_PASSWORD_REASON_PWNED

        rv = self.make_request(
            headers=build_headers(cookie='Session_id=0:old-session;%s' % TEST_USER_COOKIES),
        )

        self.check_ok(
            rv,
            check_frodo=False,
        )
        self.check_frodo_call(
            v2_session_create_timestamp=str(TEST_COOKIE_TIMESTAMP),
            v2_session_age=str(TEST_COOKIE_AGE),
            v2_session_ip=TEST_IP,
        )
        self.assert_sessionid_called()
        self.assert_editsession_called()

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=self.uid, db=self.dbshardname)

        self.assert_auth_and_event_log_ok(
            eav_pass_hash,
            [
                self.build_auth_log_entry('ses_update', self.uid),
            ],
            sms_2fa_enabled=True,
        )
        self.assert_statbox_cookie_set(old_session_uids='1,1234')

    def test_ok_and_sms_2fa_not_enabled_due_to_quarantine(self):
        flags = PhoneOperationFlags()
        flags.in_quarantine = True

        self.set_and_serialize_userinfo(
            self.create_userinfo_response(
                is_simple_phone_bound=True,
                is_replace_secure_operation=True,
                operation_flags=flags,
            )
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=self.uid,
                    login=TEST_LOGIN,
                    age=TEST_COOKIE_AGE,
                    ip=TEST_IP,
                    time=TEST_COOKIE_TIMESTAMP,
                    ttl=5,
                ),
                uid='1234',
                login='other_login',
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )
        self.expected_accounts = [
            {
                'uid': self.uid,
                'login': TEST_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_LOGIN,
            },
            {
                'uid': 1234,
                'login': 'other_login',
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': 'other_login',
            },
        ]

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.old_session = TEST_SESSIONID
            track.change_password_reason = CHANGE_PASSWORD_REASON_PWNED

        rv = self.make_request(headers=build_headers(cookie='Session_id=0:old-session;%s' % TEST_USER_COOKIES))
        self.check_ok(
            rv,
            check_frodo=False,
        )

        self.assert_sessionid_called()
        self.assert_editsession_called()

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=self.uid, db=self.dbshardname)

        self.assert_auth_and_event_log_ok(
            eav_pass_hash,
            [
                self.build_auth_log_entry('ses_update', self.uid),
            ],
        )
        self.assert_statbox_cookie_set(old_session_uids='1,1234')

        self.env.db.check_missing('attributes', 'account.sms_2fa_on', uid=TEST_UID, db='passportdbshard1')


@with_settings_hosts(
    PASSPORT_SUBDOMAIN='passport-test',
    FORBIDDEN_CHANGE_PASSWORD_WITH_BAD_FRODO_KARMA=False,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class ChangePasswordViewTestCaseWithPDD(ChangePasswordViewTestCaseBase):
    uid = TEST_PDD_UID
    login = TEST_PDD_LOGIN
    alias_type = 'pdd'
    domain = TEST_DOMAIN

    dbshardname = 'passportdbshard2'

    def get_expected_response(self, **kwargs):
        return {
            'cookies': self.create_cookies(),
            'default_uid': TEST_PDD_UID,
            'accounts': [
                {
                    'login': TEST_PDD_LOGIN,
                    'display_name': {'default_avatar': '', 'name': ''},
                    'uid': TEST_PDD_UID,
                    'display_login': TEST_PDD_LOGIN,
                },
            ],
            'account': {
                'uid': self.uid,
                'login': TEST_PDD_LOGIN,
                'domain': {
                    'punycode': self.domain,
                    'unicode': self.domain,
                },
                'display_login': TEST_PDD_LOGIN,
            },
        }

    def setUp(self):
        super(ChangePasswordViewTestCaseWithPDD, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.domain = self.domain
            track.human_readable_login = self.login
            track.machine_readable_login = self.login

        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

    def test_ok(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)

        rv = self.make_request()

        self.check_ok(rv)

    def test_reason_hacked_without_hint_answer(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.change_password_reason = CHANGE_PASSWORD_REASON_HACKED
            track.is_fuzzy_hint_answer_checked = False

        rv = self.make_request()
        self.assert_error_response(rv, error_codes=['answer.required'])

    def test_reason_hacked_with_hint_answer(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.change_password_reason = CHANGE_PASSWORD_REASON_HACKED
            track.is_fuzzy_hint_answer_checked = True

        rv = self.make_request()
        self.check_ok(rv)

    def test_reason_flushed_ok(self):
        userinfo = self.create_userinfo_response(
            custom_attributes={'password.forced_changing_reason': '2'},
            is_secure_phone_bound=False,
        )
        self.set_and_serialize_userinfo(userinfo)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.change_password_reason = CHANGE_PASSWORD_REASON_FLUSHED

        rv = self.make_request()
        self.check_ok(
            rv,
            frodo_action='change_flushed_password',
            check_phone_log=False,
        )

    def test_ok_with_frodo(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        self.env.frodo.set_response_value(
            u'check',
            FRODO_RESPONSE_SPAM_PDD_USER,
        )
        self.env.frodo.set_response_value(u'confirm', u'')

        rv = self.make_request()
        self.check_response_ok(rv)

        self.env.db.check(
            self.attributes_table,
            'karma.value',
            '85',
            uid=self.uid,
            db=self.dbshardname,
        )

        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(self.create_frodo_params())

    def test_error_domain_disabled(self):
        blackbox_response = blackbox_userinfo_response(
            uid=self.uid,
            login=self.login,
            aliases={
                self.alias_type: self.login,
            },
            domain_enabled=False,
            dbfields={'subscription.login_rule.8': 4},
        )
        self.set_and_serialize_userinfo(blackbox_response)

        resp = self.make_request()

        self.assert_error_response(resp, error_codes=['account.disabled'])


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=3,
    PASSPORT_SUBDOMAIN='passport-test',
    FORBIDDEN_CHANGE_PASSWORD_WITH_BAD_FRODO_KARMA=False,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class ChangePasswordWithSuspectedRobotTestCase(BaseTestCase):
    """
    Если пользователь пришел на смену пароля из-за ТБВС, нужно отправить ему sms на защищенный номер.
    Если пользователь не ввел код из sms, нельзя менять его пароль
    Новая версия ручки - меняем телефон через карантин
    """

    # TODO: Это должно быть рядом с passport.test.utils.check_statbox_log_entry()
    def assert_statbox_contains_no_error(self):
        last_call_arg = self.env.statbox_handle_mock.call_args_list[-1]
        line = str(last_call_arg[0][0]).replace('tskv', '', 1).strip()
        statbox_params = set()
        for field in line.split('\t'):
            name, _ = field.split('=')
            statbox_params.add(name)

        ok_('error' not in statbox_params)

    def test_change_password__not_verified_by_sms__error(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = False
            track.phone_confirmation_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['phone.required'])

    def test_change_password_no_sms(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_change_password_sms_validation_required = False
            track.is_fuzzy_hint_answer_checked = True

        rv = self.make_request()

        self.check_ok(
            rv,
            check_statbox=False,
        )

    def test_change_password__phone_confirmed_not_secure_number_without_hint_answer(self):
        """
        1) У пользователя есть защищенный телефон
        2) Пользователь подтвердил телефон отличный от защищенного
        3) На контрольный вопрос пользователь не ответил
        Результат: ошибка answer.required
        """
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.has_secure_phone_number = True
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164
            track.is_fuzzy_hint_answer_checked = False

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['answer.required'])

    def test_change_password__phone_confirmed_not_secure_with_hint_answer__ok(self):
        """
        1) У пользователя есть защищенный телефон
        2) Пользователь подтвердил телефон отличный от защищенного
        3) На контрольный вопрос пользователь ответил
        4) Конфликтующих операций нет.
        Результат: начали операцию по замене старого защищенного телефона на новый через карантин.
        Уведомили фронтенд о том, когда операция применится.
        """
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.has_secure_phone_number = True
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164
            track.is_fuzzy_hint_answer_checked = True

        rv = self.make_request()

        self.check_ok(
            rv,
            sharddb_query_count=13,
            check_statbox=False,
            response_args={
                'secure_phone_pending_until': TimeNow(offset=settings.PHONE_QUARANTINE_SECONDS),
                'is_bound_new_secure_phone': False,
                'is_conflicted_operation_exists': False,
                'is_yasms_errors_when_replacing_phone': False,
                'is_updated_current_secure_phone': False,
                'is_replaced_phone_with_quarantine': True,
            },
            frodo_phone_number=TEST_DIFFERENT_PHONE_NUMBER,
            check_replace_secure_notify=True,
        )

        eav_pass_hash = self.check_and_get_password()
        self.check_log_entries(
            eav_pass_hash,
            replace_secure_phone=True,
            new_phone=TEST_DIFFERENT_PHONE_NUMBER,
            new_phone_id=TEST_PHONE_ID3,
            old_secure_phone=TEST_PHONE_NUMBER,
        )

        assert_secure_phone_being_replaced.check_db(
            db_faker=self.env.db,
            uid=self.uid,
            phone_attributes={
                'id': TEST_PHONE_ID1,
                'number': TEST_PHONE_NUMBER.e164,
            },
            operation_attributes={
                'password_verified': DatetimeNow(),
                'code_confirmed': None,
            },
        )
        assert_simple_phone_replace_secure.check_db(
            db_faker=self.env.db,
            uid=self.uid,
            phone_attributes={
                'id': TEST_PHONE_ID3,
                'number': TEST_DIFFERENT_PHONE_NUMBER.e164,
            },
            operation_attributes={
                'password_verified': DatetimeNow(),
                'code_confirmed': DatetimeNow(),
            },
        )

        self.assert_statbox_contains_no_error()

        counter = get_per_phone_number_buckets()
        eq_(counter.get(TEST_PHONE_NUMBER.e164), 0)
        eq_(counter.get(TEST_DIFFERENT_PHONE_NUMBER.e164), 1)
        ip_counter = get_per_user_ip_buckets()
        eq_(ip_counter.get(TEST_IP), 1)

    def test_change_password__phone_confirmed_not_secure_with_hint_answer_conflict_operation_ok(self):
        """
        1) У пользователя есть защищенный телефон
        2) Пользователь подтвердил телефон отличный от защищенного
        3) На контрольный вопрос пользователь ответил
        4) Есть конфликтующая операция при привязке защищенного телефона
        Результат:
            подтвержденный телефон привязан как незащищенный, говорим об этом фронту.
        """
        self.set_and_serialize_userinfo(
            self.create_userinfo_response(is_secure_phone_being_removed=True),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_fuzzy_hint_answer_checked = True
            track.has_secure_phone_number = True
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164

        rv = self.make_request()

        self.check_ok(
            rv,
            sharddb_query_count=10,
            check_statbox=False,
            response_args={
                'is_bound_new_secure_phone': False,
                'is_conflicted_operation_exists': True,
                'is_yasms_errors_when_replacing_phone': False,
                'is_updated_current_secure_phone': False,
                'is_replaced_phone_with_quarantine': False,
            },
            frodo_phone_number=TEST_DIFFERENT_PHONE_NUMBER,
        )

        eav_pass_hash = self.check_and_get_password()
        self.check_log_entries(
            eav_pass_hash,
            new_phone=TEST_DIFFERENT_PHONE_NUMBER,
            new_phone_id=TEST_PHONE_ID3,
            operation_id1=TEST_OPERATION_ID3,
            is_conflicted_operation_exists=True,
        )

        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=self.uid,
            phone_attributes={
                'id': TEST_PHONE_ID3,
                'number': TEST_DIFFERENT_PHONE_NUMBER.e164,
            },
        )

        self.assert_statbox_contains_no_error()

        counter = get_per_phone_number_buckets()
        eq_(counter.get(TEST_PHONE_NUMBER.e164), 0)
        eq_(counter.get(TEST_DIFFERENT_PHONE_NUMBER.e164), 0)
        ip_counter = get_per_user_ip_buckets()
        eq_(ip_counter.get(TEST_IP), 1)

    def test_change_password__phone_confirmed_and_new_secure_number__error(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.has_secure_phone_number = False
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['phone_secure.bound_and_confirmed'])

    def test_change_password__phone_confirmed_not_secure_with_short_form__ok(self):
        """
        1) У пользователя есть защищенный телефон
        2) Пользователь подтвердил телефон отличный от защищенного
        3) На контрольный вопрос пользователь НЕ ответил, но прошел короткую анкету.
        4) Конфликтующих операций нет.
        Результат: начали операцию по замене старого защищенного телефона на новый через карантин.
        Уведомили фронтенд о том, когда операция применится.
        """
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_short_form_factors_checked = True
            track.is_fuzzy_hint_answer_checked = False
            track.has_secure_phone_number = True
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164

        rv = self.make_request()

        self.check_ok(
            rv,
            sharddb_query_count=13,
            check_statbox=False,
            response_args={
                'is_bound_new_secure_phone': False,
                'is_conflicted_operation_exists': False,
                'secure_phone_pending_until': TimeNow(offset=settings.PHONE_QUARANTINE_SECONDS),
                'is_yasms_errors_when_replacing_phone': False,
                'is_updated_current_secure_phone': False,
                'is_replaced_phone_with_quarantine': True,
            },
            frodo_phone_number=TEST_DIFFERENT_PHONE_NUMBER,
            check_replace_secure_notify=True,
        )

        eav_pass_hash = self.check_and_get_password()
        self.check_log_entries(
            eav_pass_hash,
            replace_secure_phone=True,
            new_phone=TEST_DIFFERENT_PHONE_NUMBER,
            new_phone_id=TEST_PHONE_ID3,
            old_secure_phone=TEST_PHONE_NUMBER,
        )

        assert_secure_phone_being_replaced.check_db(
            db_faker=self.env.db,
            uid=self.uid,
            phone_attributes={
                'id': TEST_PHONE_ID1,
                'number': TEST_PHONE_NUMBER.e164,
            },
            operation_attributes={
                'password_verified': DatetimeNow(),
                'code_confirmed': None,
            },
        )
        assert_simple_phone_replace_secure.check_db(
            db_faker=self.env.db,
            uid=self.uid,
            phone_attributes={
                'id': TEST_PHONE_ID3,
                'number': TEST_DIFFERENT_PHONE_NUMBER.e164,
            },
            operation_attributes={
                'password_verified': DatetimeNow(),
                'code_confirmed': DatetimeNow(),
            },
        )

        self.assert_statbox_contains_no_error()

        counter = get_per_phone_number_buckets()
        eq_(counter.get(TEST_PHONE_NUMBER.e164), 0)
        eq_(counter.get(TEST_DIFFERENT_PHONE_NUMBER.e164), 1)
        ip_counter = get_per_user_ip_buckets()
        eq_(ip_counter.get(TEST_IP), 1)

    def test_change_password_phone_confirmed_not_secure_with_hint_answer_and_per_phone_counter_reached__error(self):
        """
        1) У пользователя есть незащищенный телефон
        2) Пользователь подтвердил другой телефон
        3) На контрольный вопрос пользователь ответил
        4) Счетчик привязок для подтвержденного телефона достиг лимита
        Результат: ошибка phone.compromised
        """
        self.set_and_serialize_userinfo(self.create_userinfo_response(
            is_simple_phone_bound=True,
            is_secure_phone_bound=False,
        ))

        counter = get_per_phone_number_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_DIFFERENT_PHONE_NUMBER.e164)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_fuzzy_hint_answer_checked = True
            track.has_secure_phone_number = True
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164

        # Запрос с превышением счетчика - ошибка
        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['phone.compromised'])

        # Записали событие в statbox как ошибку
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'checked_counter',
                counter_current_value=str(counter.get(TEST_DIFFERENT_PHONE_NUMBER.e164)),
                counter_limit_value=str(counter.limit),
            ),
        ], offset=-1)
        eq_(counter.get(TEST_DIFFERENT_PHONE_NUMBER.e164), counter.limit)

    def test_change_password__sms_verification_have_secure_phone__ok(self):
        self.set_and_serialize_userinfo(self.default_blackbox_response)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.has_secure_phone_number = True
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request()

        self.check_ok(
            rv,
            sharddb_query_count=4,
            check_statbox=False,
            response_args={
                'is_bound_new_secure_phone': False,
                'is_conflicted_operation_exists': False,
                'is_yasms_errors_when_replacing_phone': False,
                'is_updated_current_secure_phone': True,
                'is_replaced_phone_with_quarantine': False,
            },
            frodo_phone_number=TEST_PHONE_NUMBER,
        )
        ip_counter = get_per_user_ip_buckets()
        eq_(ip_counter.get(TEST_IP), 1)

        eav_pass_hash = self.check_and_get_password()
        self.assert_yasms_phone_updated()
        self.check_log_entries(
            eav_pass_hash,
            old_secure_phone=TEST_PHONE_NUMBER,
            update_old_secure_phone=True,
        )

    def test_change_password__sms_verification_havent_secure_phone__without_hint_answer(self):
        """
        1) У пользователя есть незащищенный телефон
        2) Пользователь подтвердил другой телефон
        3) На контрольный вопрос пользователь не ответил
        Результат: ошибка answer.required
        """
        self.set_and_serialize_userinfo(self.create_userinfo_response(
            is_simple_phone_bound=True,
            is_secure_phone_bound=False,
        ))

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.has_secure_phone_number = False
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.is_fuzzy_hint_answer_checked = False

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['answer.required'])

    def test_change_password__sms_verification_havent_secure_phone__with_hint_answer_ok(self):
        """
        1) У пользователя есть незащищенный телефон
        2) Пользователь подтвердил привязанный телефон
        3) На контрольный вопрос пользователь ответил
        Результат: привязан защищенный телефон.
        """
        self.set_and_serialize_userinfo(self.create_userinfo_response(
            is_simple_phone_bound=True,
            is_secure_phone_bound=False,
        ))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_fuzzy_hint_answer_checked = True
            track.has_secure_phone_number = False
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request()

        self.check_ok(
            rv,
            sharddb_query_count=7,
            check_statbox=False,
            response_args={
                'is_conflicted_operation_exists': False,
                'is_bound_new_secure_phone': True,
                'is_yasms_errors_when_replacing_phone': False,
                'is_updated_current_secure_phone': False,
                'is_replaced_phone_with_quarantine': False,
            },
            frodo_phone_number=TEST_PHONE_NUMBER,
            check_change_password_notify=True,
            check_secure_bound_notify=True,
        )

        eav_pass_hash = self.check_and_get_password()
        self.check_log_entries(
            eav_pass_hash,
            bind_new_secure_phone=True,
            new_phone=TEST_PHONE_NUMBER,
            is_phone_securified=True,
        )

        assert_secure_phone_bound.check_db(
            db_faker=self.env.db,
            uid=self.uid,
            phone_attributes={
                'id': TEST_PHONE_ID1,
                'number': TEST_PHONE_NUMBER.e164,
            },
        )

        self.assert_statbox_contains_no_error()

        counter = get_per_phone_number_buckets()
        ok_(counter.get(TEST_PHONE_NUMBER.e164), 1)
        ip_counter = get_per_user_ip_buckets()
        eq_(ip_counter.get(TEST_IP), 1)

    def test_change_password_per_phone_counter_reached__error(self):
        self.set_and_serialize_userinfo(self.create_userinfo_response(
            is_simple_phone_bound=True,
            is_secure_phone_bound=False,
        ))

        counter = get_per_phone_number_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE_NUMBER.e164)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_change_password_sms_validation_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        # Запрос с превышением счетчика - ошибка
        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['phone.compromised'])

        # Записали событие в statbox как ошибку
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'checked_counter',
                counter_current_value=str(counter.get(TEST_PHONE_NUMBER.e164)),
                counter_limit_value=str(counter.limit),
            ),
        ], offset=-1)
        eq_(counter.get(TEST_PHONE_NUMBER.e164), counter.limit)

    def test_change_password_expired_operation_error(self):
        """
        1) У пользователя есть защищенный телефон
        2) Но приходит он с другим подтвержденным номером
        3) На контрольный вопрос пользователь ответил
        4) На другом номере есть протухшая операция по замене на защищенный
        Результат: ошибка Operation expired ведущая к internal.temporary
        """
        self.set_and_serialize_userinfo(
            self.create_userinfo_response(
                is_replace_secure_operation=True,
                is_operation_finished=True,
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.has_secure_phone_number = True
            track.phone_confirmation_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164
            track.is_change_password_sms_validation_required = True
            track.is_fuzzy_hint_answer_checked = True
            track.phone_confirmation_is_confirmed = True

        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['internal.temporary'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'analyzed_frodo',
                karma_prefix='0',
                is_karma_prefix_returned='0',
            ),
        ])


@with_settings_hosts(
    BLACKBOX_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    PASSPORT_SUBDOMAIN='passport-test',
    FORBIDDEN_CHANGE_PASSWORD_WITH_BAD_FRODO_KARMA=True,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class FrodoChangePasswordViewTestCase(ChangePasswordViewTestCaseBase):
    def test_frodo_forbidden_change_password(self):
        self.set_and_serialize_userinfo(self.create_userinfo_response(karma=1000))
        self.env.frodo.set_response_value(
            u'check',
            FRODO_RESPONSE_PROBABLY_SPAM_USER,
        )
        self.env.frodo.set_response_value(u'confirm', u'')

        response = self.make_request()

        self.env.db.check(self.attributes_table, 'karma.value', '7000', uid=self.uid, db=self.dbshardname)

        # Проверяем параметры для frodo
        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(self.create_frodo_params(karma=1000))

        self.assert_error_response(response, error_codes=['account.compromised'])
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'analyzed_frodo',
                karma_prefix='7',
                is_karma_prefix_returned='1',
                error='account.compromised',
            ),
        ], offset=2)
        self.assert_sms_not_sent()
        self.assert_no_emails_sent()


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class ChangePasswordViewTestCaseNoBlackboxHash(ChangePasswordViewTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class ChangePassword2FAPromoTestCaseNoBlackboxHash(ChangePassword2FAPromoTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class ChangePasswordMultiAuthViewTestCaseNoBlackboxHash(ChangePasswordMultiAuthViewTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class ChangePasswordViewTestCaseWithPDDNoBlackboxHash(ChangePasswordViewTestCaseWithPDD):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class ChangePasswordViewTestCaseWithSuspectedRobotNoBlackboxHash(ChangePasswordWithSuspectedRobotTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class FrodoChangePasswordViewTestCaseNoBlackboxHash(FrodoChangePasswordViewTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
