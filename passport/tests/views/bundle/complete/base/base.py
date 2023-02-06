# -*- coding: utf-8 -*-
from copy import deepcopy
from itertools import chain
import json

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import (
    EmailTestMixin,
    ProfileTestMixin,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_PHONE_ID1,
    TEST_PUBLIC_ID,
    TEST_UID2,
)
from passport.backend.api.views.bundle.constants import X_TOKEN_OAUTH_SCOPE
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_loginoccupation_response,
    blackbox_lrandoms_response,
    blackbox_oauth_response,
    blackbox_phone_bindings_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.builders.frodo.utils import get_phone_number_hash
from passport.backend.core.cookies import (
    cookie_l,
    cookie_lah,
    cookie_y,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.password import PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.services import Service
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.types.bit_vector import PhoneBindingsFlags
from passport.backend.core.types.login.login import normalize_login
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
    remove_none_values,
)

from .base_test_data import (
    COOKIE_L_VALUE,
    COOKIE_LAH_VALUE,
    COOKIE_YP_VALUE,
    COOKIE_YS_VALUE,
    EXPECTED_L_COOKIE,
    EXPECTED_LAH_COOKIE,
    EXPECTED_MDA2_BEACON_COOKIE,
    EXPECTED_SESSIONID_COOKIE,
    EXPECTED_SESSIONID_SECURE_COOKIE,
    EXPECTED_YANDEX_LOGIN_COOKIE,
    EXPECTED_YP_COOKIE,
    EXPECTED_YS_COOKIE,
    FRODO_RESPONSE_OK,
    MDA2_BEACON_VALUE,
    TEST_ACCEPT_LANGUAGE,
    TEST_APP_ID,
    TEST_AUTH_ID,
    TEST_COOKIE_TIMESTAMP,
    TEST_FIRSTNAME,
    TEST_FUID01_COOKIE,
    TEST_HOST,
    TEST_IP,
    TEST_LASTNAME,
    TEST_LITE_DISPLAY_NAME,
    TEST_LITE_LOGIN,
    TEST_LOGIN,
    TEST_NEOPHONISH_DISPLAY_NAME,
    TEST_NEOPHONISH_LOGIN,
    TEST_NOT_STRONG_PASSWORD_CLASSES_NUMBER,
    TEST_NOT_STRONG_PASSWORD_IS_SEQUENCE,
    TEST_NOT_STRONG_PASSWORD_IS_WORD,
    TEST_NOT_STRONG_PASSWORD_LENGTH,
    TEST_NOT_STRONG_PASSWORD_QUALITY,
    TEST_NOT_STRONG_PASSWORD_SEQUENCES_NUMBER,
    TEST_OPERATION_TTL,
    TEST_PASSWORD,
    TEST_PASSWORD_QUALITY,
    TEST_PHONE_NUMBER_OBJECT,
    TEST_RETPATH,
    TEST_SESSIONID,
    TEST_SOCIAL_DISPLAY_NAME,
    TEST_SOCIAL_DISPLAY_NAME_AFTER_COMPLETION,
    TEST_SOCIAL_LOGIN,
    TEST_SSL_SESSIONID,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
    TEST_WEAK_PASSWORD_HASH,
    TEST_YANDEX_GID_COOKIE,
    TEST_YANDEXUID_COOKIE,
)


def build_headers(**kwargs):
    defaults = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )
    for name, value in defaults.items():
        kwargs.setdefault(name, value)
    return mock_headers(**kwargs)


def get_account_info(login, display_login, display_name=None,
                     firstname=u'\\u0414', lastname=u'\\u0424', uid=TEST_UID,
                     **kwargs):
    return {
        'person': {
            'firstname': firstname,
            'language': 'ru',
            'gender': 1,
            'birthday': '1963-05-15',
            'lastname': lastname,
            'country': 'ru',
        },
        'login': login,
        'display_name': display_name or TEST_SOCIAL_DISPLAY_NAME,
        'uid': uid,
        'display_login': display_login,
        'public_id': TEST_PUBLIC_ID,
    }


common_userinfo_kwargs = {'uid': TEST_UID}
common_sessionid_kwargs = {}


def build_lite(account=None, has_password=True):
    account = deep_merge(
        {
            'userinfo': {},
            'sessionid': {},
            'oauth': {'scope': X_TOKEN_OAUTH_SCOPE},
            'login': {},
        },
        account or {},
    )

    custom_userinfo_kwargs = {
        'login': TEST_LITE_LOGIN,
        'aliases': {'lite': TEST_LITE_LOGIN},
        'display_name': TEST_LITE_DISPLAY_NAME,
        'dbfields': {},
        'attributes': {},
        'public_id': TEST_PUBLIC_ID,
    }
    if has_password:
        custom_userinfo_kwargs['dbfields'].update({
            'password_quality.quality.uid': 10,
            'password_quality.version.uid': 3,
        })
        custom_userinfo_kwargs['attributes']['password.encrypted'] = TEST_WEAK_PASSWORD_HASH

    account['userinfo'] = deep_merge(
        common_userinfo_kwargs,
        custom_userinfo_kwargs,
        account['userinfo'],
    )

    account['sessionid'] = deep_merge(
        common_sessionid_kwargs,
        {'have_password': has_password},
        account['sessionid'],
    )
    return account


def build_canonical_social(account=None):
    account = deep_merge(
        {
            'userinfo': {
                'login': TEST_SOCIAL_LOGIN,
                'public_id': TEST_PUBLIC_ID,
            },
        },
        account or {},
    )
    return build_common_social(account)


def build_social_with_custom_login(account=None):
    account = deep_merge(
        {
            'userinfo': {
                'login': TEST_LOGIN,
                'aliases': {'portal': TEST_LOGIN},
                'public_id': TEST_PUBLIC_ID,
            },
        },
        account or {},
    )
    return build_common_social(account)


def build_common_social(account=None):
    account = deep_merge(
        {
            'userinfo': {},
            'sessionid': {},
            'oauth': {'scope': X_TOKEN_OAUTH_SCOPE},
            'login': {},
        },
        account or {},
    )
    account['userinfo'] = deep_merge(
        common_userinfo_kwargs,
        {
            'aliases': {'social': TEST_SOCIAL_LOGIN},
            'display_name': TEST_SOCIAL_DISPLAY_NAME,
            'subscribed_to': [Service.by_slug('social')],
        },
        account['userinfo'],
    )
    account['sessionid'] = deep_merge(
        common_sessionid_kwargs,
        {'have_password': False},
        account['sessionid'],
    )
    return account


def build_neophonish(account=None):
    account = deep_merge(
        {
            'userinfo': {},
            'sessionid': {},
            'oauth': {'scope': X_TOKEN_OAUTH_SCOPE},
            'login': {},
        },
        account or {},
    )

    binding_flags = PhoneBindingsFlags()
    binding_flags.should_ignore_binding_limit = False
    custom_userinfo_kwargs = deep_merge(
        {
            'login': TEST_NEOPHONISH_LOGIN,
            'aliases': {
                'neophonish': TEST_NEOPHONISH_LOGIN,
                'phonenumber': TEST_PHONE_NUMBER_OBJECT.digital,
            },
            'display_name': TEST_NEOPHONISH_DISPLAY_NAME,
            'dbfields': {},
            'attributes': {},
        },
        build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER_OBJECT.e164, binding_flags=binding_flags),
    )

    account['userinfo'] = deep_merge(
        common_userinfo_kwargs,
        custom_userinfo_kwargs,
        account['userinfo'],
    )

    account['sessionid'] = deep_merge(
        common_sessionid_kwargs,
        {'have_password': False},
        account['sessionid'],
    )
    return account


def complete(account):
    account = deep_merge(
        {
            'userinfo': {},
            'sessionid': {},
        },
        account,
    )
    account['userinfo'] = deep_merge(
        account['userinfo'],
        {
            'login': TEST_LOGIN,
            'aliases': {'portal': TEST_LOGIN},
            'dbfields': {
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            'attributes': {'password.encrypted': TEST_WEAK_PASSWORD_HASH},
        },
    )
    account['sessionid'] = deep_merge(account['sessionid'], {'have_password': True})
    return account


def build_complete(account={}):
    return deep_merge(
        {
            'userinfo': common_userinfo_kwargs,
            'sessionid': common_sessionid_kwargs,
        },
        {
            'userinfo': {
                'login': TEST_LOGIN,
                'aliases': {'portal': TEST_LOGIN},
                'dbfields': {
                    'password_quality.quality.uid': 10,
                    'password_quality.version.uid': 3,
                },
                'attributes': {'password.encrypted': TEST_WEAK_PASSWORD_HASH},
            },
            'sessionid': {
                'have_password': True,
            },
        },
        account,
    )


def enable_2fa(account):
    account = deepcopy(account)

    attributes = account['userinfo'].setdefault('attributes', {})
    attributes['account.2fa_on'] = '1'
    attributes.pop('password.encrypted', None)

    account['sessionid']['have_password'] = False

    return account


class BaseCompleteTest(BaseBundleTestViews):
    def historydb_entry(self, uid=1, name=None, value=None):
        entry = {
            'uid': str(uid),
            'name': name,
            'value': value,
        }
        return remove_none_values(entry)

    def assert_blackbox_sessionid_called(self, with_sslsession=True, sessionid_index=0, is_extended=True):
        params = {
            'method': 'sessionid',
            'multisession': 'yes',
            'sessionid': TEST_SESSIONID,
        }
        if is_extended:
            params.update({
                'getphones': 'all',
                'getphoneoperations': '1',
                'getphonebindings': 'all',
                'aliases': 'all_with_hidden',
            })
        if with_sslsession:
            params['sslsessionid'] = TEST_SSL_SESSIONID

        self.env.blackbox.requests[sessionid_index].assert_query_contains(params)

        if is_extended:
            self.env.blackbox.requests[sessionid_index].assert_contains_attributes({
                'phones.default',
                'phones.secure',
            })

    def assert_blackbox_userinfo_called(self):
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'uid': str(TEST_UID),
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

        self.env.blackbox.requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

    def get_account_kwargs(self, uid=TEST_UID, login=None, alias_type='portal',
                           phone_id=1, phone=TEST_PHONE_NUMBER_OBJECT, secure=True, **kwargs):
        account_kwargs = dict(
            uid=uid,
            login=login,
            aliases={
                alias_type: login,
            },
            public_id=TEST_PUBLIC_ID,
        )

        if phone:
            phone_builder = build_phone_secured if secure else build_phone_bound
            phone_kwargs = phone_builder(phone_id, phone.e164)
            account_kwargs = deep_merge(account_kwargs, phone_kwargs)

        account_kwargs = deep_merge(account_kwargs, kwargs)

        return account_kwargs

    def setup_track_for_auth_by_key(self):
        if not hasattr(self, 'track_id'):
            self.track_id = self.env.track_manager.create_test_track(self.track_manager, 'complete')
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.is_key_auth_passed = True
            track.uid = TEST_UID

    def assert_blackbox_editsession_called(self, editsession_index=-2):
        request = self.env.blackbox.requests[editsession_index]
        expected_args = {
            'method': 'editsession',
            'uid': str(TEST_UID),
            'format': 'json',
            'sessionid': TEST_SESSIONID,
            'sslsessionid': TEST_SSL_SESSIONID,
            'host': TEST_HOST,
            'userip': TEST_IP,
            'op': 'add',
            'password_check_time': TimeNow(),
            'have_password': '1',
            'new_default': str(TEST_UID),
            'keyspace': 'yandex.ru',
            'lang': '8',
            'create_time': TimeNow(),
            'guard_hosts': 'passport-test.yandex.ru,test.yandex.ru',
            'request_id': mock.ANY,
            'get_login_id': 'yes',
        }
        request.assert_query_equals(expected_args)

    def assert_blackbox_loginoccupation_called(self, login=TEST_LOGIN):
        loginoccupation_requests = self.env.blackbox.get_requests_by_method('loginoccupation')
        eq_(len(loginoccupation_requests), 1)
        loginoccupation_requests[0].assert_query_contains({'logins': login})

    def assert_statbox_has_written(self, entries):
        self.env.statbox.assert_has_written(entries)
        self.check_completion_done_entries_count(entries)

    def check_completion_done_entries_count(self, entries):
        # Нужно проверить, что среди записей находится не  больше одной с
        # ключами mode, uid, login, type. Т.к. на вики
        # https://wiki.yandex-team.ru/passport/statbox/#doregistracijaakkauntamodecomplete
        # сказано, что такой набор ключей, говорит о том что пользователь
        # дорегистрирован.
        COMPLETION_DONE_ENTRY_KEYS = ['mode', 'type', 'login', 'uid']
        done_entries = []
        for entry in entries:
            if all(k in entry for k in COMPLETION_DONE_ENTRY_KEYS):
                done_entries.append(entry)
        ok_(len(done_entries) <= 1, done_entries)


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    CLEAN_WEB_API_ENABLED=False,
    BIND_RELATED_PHONISH_ACCOUNT_APP_IDS={TEST_APP_ID},
)
class CompleteCommitTestCaseBase(BaseCompleteTest, EmailTestMixin, ProfileTestMixin):
    maxDiff = None
    url_method_name = None
    statbox_type = None
    track_type = 'complete'
    authentication_media = 'session'

    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['complete']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
            track.uid = TEST_UID
            track.login = TEST_SOCIAL_LOGIN
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_OK)
        self.env.frodo.set_response_value(u'confirm', u'')

        self._cookie_l_pack = mock.Mock(return_value=COOKIE_L_VALUE)
        self._cookie_ys_pack = mock.Mock(return_value=COOKIE_YS_VALUE)
        self._cookie_yp_pack = mock.Mock(return_value=COOKIE_YP_VALUE)
        self._cookie_lah_pack = mock.Mock(return_value=COOKIE_LAH_VALUE)

        self.cookies_patches = [
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
        ]
        for patch in self.cookies_patches:
            patch.start()

        self.setup_statbox_templates()
        self.setup_profile_patches()

    def tearDown(self):
        self.teardown_profile_patches()
        for patch in reversed(self.cookies_patches):
            patch.stop()

        self.env.stop()
        del self.env
        del self.track_manager
        del self.cookies_patches
        del self._cookie_l_pack
        del self._cookie_yp_pack
        del self._cookie_ys_pack
        del self._cookie_lah_pack

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'ser_statbox',
            consumer='dev',
            user_agent=TEST_USER_AGENT,
            ip=TEST_IP,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'usr_statbox',
            _inherit_from=['ser_statbox'],
            mode='complete',
            track_id=self.track_id,
        )

        self.env.statbox.bind_entry(
            'validated',
            _inherit_from=['usr_statbox'],
        )
        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from=['account_modification', 'ser_statbox'],
            operation='updated',
        )
        self.env.statbox.bind_entry(
            'cookie_set',
            _inherit_from=['cookie_set'],
            mode='any_auth',
            yandexuid=TEST_YANDEXUID_COOKIE,
            ip_country='us',
            uids_count='0',
            retpath=TEST_RETPATH,
            track_id=self.track_id,
            user_agent=TEST_USER_AGENT,
            ip=TEST_IP,
            uid=str(TEST_UID),
            ttl='0',
        )
        self.env.statbox.bind_entry(
            'multibrowser_update',
            old_multibrowser='0',
            new_multibrowser='1',
            action='multibrowser_update',
            mode='any_auth',
            yandexuid=TEST_YANDEXUID_COOKIE,
            user_agent=TEST_USER_AGENT,
            ip=TEST_IP,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'frodo_karma',
            _inherit_from=['frodo_karma', 'ser_statbox'],
            new='6000',
            old='0',
            registration_datetime='-',
            action='complete',
            suid='1',
        )
        self.env.statbox.bind_entry(
            'subscriptions',
            _inherit_from=['subscriptions', 'ser_statbox'],
            operation='added',
            sid='2',
            suid='1',
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_subscription_added',
            _inherit_from=['phonenumber_alias_subscription_added', 'ser_statbox'],
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_subscription_removed',
            _inherit_from=['phonenumber_alias_subscription_removed', 'ser_statbox'],
        )
        self.env.statbox.bind_entry(
            'secure_bind_operation_created',
            _inherit_from=['secure_bind_operation_created', 'ser_statbox'],
            number=TEST_PHONE_NUMBER_OBJECT.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _inherit_from=['phone_confirmed', 'usr_statbox'],
            code_checks_count='0',
            number=TEST_PHONE_NUMBER_OBJECT.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'secure_phone_bound',
            _inherit_from=['secure_phone_bound', 'usr_statbox'],
            number=TEST_PHONE_NUMBER_OBJECT.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'securify_operation_created',
            _inherit_from=['securify_operation_created', 'ser_statbox'],
            number=TEST_PHONE_NUMBER_OBJECT.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'phone_secured',
            _inherit_from=['phone_secured', 'usr_statbox'],
            number=TEST_PHONE_NUMBER_OBJECT.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'password_validation_error',
            track_id=self.track_id,
            action='password_validation_error',
            weak=tskv_bool(True),
            policy='strong',
            password_quality=str(TEST_NOT_STRONG_PASSWORD_QUALITY),
            length=str(TEST_NOT_STRONG_PASSWORD_LENGTH),
            classes_number=str(TEST_NOT_STRONG_PASSWORD_CLASSES_NUMBER),
            sequences_number=str(TEST_NOT_STRONG_PASSWORD_SEQUENCES_NUMBER),
            is_sequence=tskv_bool(TEST_NOT_STRONG_PASSWORD_IS_SEQUENCE),
            is_word=tskv_bool(TEST_NOT_STRONG_PASSWORD_IS_WORD),
            is_additional_word=tskv_bool(False),
            additional_subwords_number='0',
        )
        self.env.statbox.bind_entry(
            'registration_with_sms_error',
            action='registration_with_sms',
            error='registration_sms_per_ip_limit_has_exceeded',
            counter_prefix='registration:sms:ip',
            is_special_testing_ip='0',
            ip=TEST_IP,
            mode='complete',
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_given_out',
            _inherit_from=['phonenumber_alias_given_out', 'usr_statbox'],
            number=TEST_PHONE_NUMBER_OBJECT.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_taken_away',
            _inherit_from=['phonenumber_alias_taken_away', 'usr_statbox'],
            number=TEST_PHONE_NUMBER_OBJECT.masked_format_for_statbox,
        ),

    def make_request(self, headers=None, exclude=None, validation_method='captcha',
                     with_password=True, login=TEST_LOGIN, **kwargs):
        data = {
            'track_id': self.track_id,
            'display_language': 'ru',
            'login': login,
            # Персональные данные
            'firstname': TEST_FIRSTNAME,
            'lastname': TEST_LASTNAME,
            # Язык
            'language': 'tr',
            'country': 'tr',
            'gender': 'm',
            'birthday': '1950-05-01',
            'timezone': 'Europe/Moscow',
            'validation_method': validation_method,
            # КВ/КО
            'question': 'question',
            'answer': 'answer',
        }

        if with_password:
            data['password'] = TEST_PASSWORD

        data.update(kwargs)
        if exclude:
            for key in exclude:
                data.pop(key)
        headers = self.build_headers() if headers is None else headers
        return self.env.client.post(
            '/1/bundle/complete/%s/?consumer=dev' % self.url_method_name,
            data=data,
            headers=headers,
        )

    def build_headers(self, **kwargs):
        return build_headers(**kwargs)

    def check_ok(self, response, login=TEST_LOGIN, display_login='', display_name=None, display_name_updated=True,
                 retpath=TEST_RETPATH, login_created=True,
                 with_optional_params=True, captcha_passed=True, had_password=False,
                 check_frodo=True, check_event_log=True, bad_user_karma=None, multi=True,
                 additional_account=None, account_karma=0, with_cookies=True, with_lah=False, check_statbox=True,
                 check_db=True, check_track=True, validated_via=None, phone_validated=False,
                 subscribed=True, additional_account_index=1,
                 old_login=TEST_LOGIN, password_sent=True,
                 phone_securified=False, phone_aliasified=False,
                 firstname=TEST_FIRSTNAME, lastname=TEST_LASTNAME,
                 secure_phone_bound=False, phonenumber_alias_was_busy=False):
        response_data = json.loads(response.data)
        eq_(response_data['status'], 'ok', response_data)

        expected_response = {
            'account': {
                'person': {
                    'firstname': firstname if with_optional_params else '\\u0414',
                    'language': 'tr' if with_optional_params else 'ru',
                    'gender': 1,
                    'birthday': '1950-05-01' if with_optional_params else '1963-05-15',
                    'lastname': lastname if with_optional_params else u'\\u0424',
                    'country': 'tr' if with_optional_params else 'ru',
                },
                'login': login,
                'display_name': display_name or TEST_SOCIAL_DISPLAY_NAME_AFTER_COMPLETION,
                'uid': 1,
                'display_login': display_login,
                'public_id': TEST_PUBLIC_ID,
            },
            'retpath': 'http://test.yandex.ru',
            'track_id': self.track_id,
        }

        if with_cookies:
            expected_response['cookies'] = [
                EXPECTED_SESSIONID_COOKIE,
                EXPECTED_SESSIONID_SECURE_COOKIE,
                EXPECTED_YP_COOKIE,
                EXPECTED_YS_COOKIE,
                EXPECTED_L_COOKIE,
                EXPECTED_YANDEX_LOGIN_COOKIE % login,
            ]
            expected_response['default_uid'] = TEST_UID
            if with_lah:
                expected_response['cookies'].append(EXPECTED_LAH_COOKIE)

            expected_response['cookies'].append(EXPECTED_MDA2_BEACON_COOKIE)

        if multi:
            expected_response['accounts'] = [dict(expected_response['account'])]
            expected_response['accounts'][0]['display_name'] = display_name or TEST_SOCIAL_DISPLAY_NAME_AFTER_COMPLETION
            del expected_response['accounts'][0]['person']

            if additional_account is not None:
                expected_response['accounts'].insert(additional_account_index, additional_account)

        self.assert_ok_response(response, ignore_order_for=['cookies'], **expected_response)

        assert_builder_requested(self.env.blackbox)

        # Check frodo
        if check_frodo:
            self.check_frodo(
                bad_user_karma=bad_user_karma,
                with_optional_params=with_optional_params,
                multi=multi,
                account_karma=account_karma,
                with_password=not had_password,
                phone_number_present=phone_validated,
                password_sent=password_sent,
                frodo_kwargs={
                    'iname': firstname if with_optional_params else '',
                    'fname': lastname if with_optional_params else '',
                },
            )

        # Check event log
        if check_event_log:
            self.check_event_log(
                login=login if login_created else None,
                display_name=display_name,
                display_name_updated=display_name_updated,
                bad_user_karma=bad_user_karma,
                captcha_passed=captcha_passed,
                with_optional_params=with_optional_params,
                with_password=not had_password,
                subscribed=subscribed,
                secure_phone_bound=secure_phone_bound,
                phone_securified=phone_securified,
                phone_aliasified=phone_aliasified,
                phone_validated=phone_validated,
                firstname=firstname,
                lastname=lastname,
                phonenumber_alias_was_busy=phonenumber_alias_was_busy,
            )

        if check_statbox:
            self.check_statbox_entries(
                with_optional_params=with_optional_params,
                display_name=display_name,
                display_name_updated=display_name_updated,
                validated_via=validated_via,
                captcha_passed=captcha_passed,
                phone_validated=phone_validated,
                secure_phone_bound=secure_phone_bound,
                bad_user_karma=bad_user_karma,
                had_password=had_password,
                multi=multi,
                uids_count=2 if additional_account else 1,
                login=login,
                old_login=old_login,
                subscribed=subscribed,
                phone_securified=phone_securified,
                phone_aliasified=phone_aliasified,
                with_cookies=with_cookies,
                firstname=firstname,
                lastname=lastname,
                phonenumber_alias_was_busy=phonenumber_alias_was_busy,
            )

        if check_db:
            self.check_db(
                with_optional_params=with_optional_params,
                had_password=had_password,
            )

        if check_track:
            self.check_track(
                login=login,
                retpath=retpath,
            )

    def check_ok_action_not_required(self, rv, **kwargs):
        kwargs.setdefault('display_name', TEST_SOCIAL_DISPLAY_NAME)
        self.check_ok(
            rv,
            with_cookies=False,
            display_login=TEST_LOGIN,
            check_frodo=False,
            check_event_log=False,
            check_statbox=False,
            check_db=False,
            check_track=False,
            with_optional_params=False,
            display_name_updated=False,
            **kwargs
        )

    def check_frodo(self, bad_user_karma=None, with_optional_params=True,
                    multi=False, account_karma=0, with_password=True,
                    phone_number_present=False, frodo_kwargs=None, password_sent=True):
        requests = self.env.frodo.requests
        if bad_user_karma is None:
            expected_number_of_requests = 1
        else:
            expected_number_of_requests = 2
        eq_(len(requests), expected_number_of_requests)

        frodo_additional_args = {
            'v2_account_karma': str(account_karma),
        }
        if not with_optional_params:
            frodo_additional_args.update({
                'v2_account_timezone': 'America/New_York',
                'xcountry': 'ru',
                'v2_account_country': 'ru',
                'v2_account_language': 'ru',
                'lang': 'ru',
            })
        if multi:
            frodo_additional_args.update({
                'v2_session_create_timestamp': '123',
                'v2_session_age': '0',
                'v2_session_ip': '84.201.166.67',
            })
        if phone_number_present:
            frodo_additional_args.update({
                'phonenumber': TEST_PHONE_NUMBER_OBJECT.masked_format_for_frodo,
                'v2_phonenumber_hash': get_phone_number_hash(TEST_PHONE_NUMBER_OBJECT.e164),
            })

        if not with_password:
            frodo_additional_args.update({
                'v2_password_quality': '',
            })
        if not password_sent:
            frodo_additional_args.update({
                'passwd': '0.0.0.0.0.0.0.0',
                'passwdex': '0.0.0.0.0.0.0.0',
            })

        frodo_additional_args = merge_dicts(
            frodo_additional_args,
            frodo_kwargs or {},
        )

        requests[0].assert_query_equals(
            self.create_frodo_params(**frodo_additional_args),
        )
        if bad_user_karma is not None:
            requests[1].assert_query_equals({TEST_LOGIN: str(bad_user_karma)})

    def check_event_log(self, login=None, bad_user_karma=None, captcha_passed=True,
                        display_name=None, display_name_updated=True,
                        with_optional_params=False, with_password=False, subscribed=False,
                        secure_phone_bound=False, phone_securified=False,
                        phone_aliasified=False, phone_validated=False,
                        firstname=TEST_FIRSTNAME, lastname=TEST_LASTNAME,
                        phonenumber_alias_was_busy=False):
        historydb_entries = []

        if secure_phone_bound:
            historydb_entries.extend([
                self.historydb_entry(name='phone.1.action', value='created'),
                self.historydb_entry(name='phone.1.created', value=TimeNow()),
                self.historydb_entry(name='phone.1.number', value=TEST_PHONE_NUMBER_OBJECT.e164),
                self.historydb_entry(name='phone.1.operation.1.action', value='created'),
                self.historydb_entry(name='phone.1.operation.1.finished',
                                     value=TimeNow(offset=TEST_OPERATION_TTL.total_seconds())),
                self.historydb_entry(name='phone.1.operation.1.security_identity', value='1'),
                self.historydb_entry(name='phone.1.operation.1.started', value=TimeNow()),
                self.historydb_entry(name='phone.1.operation.1.type', value='bind'),
                self.historydb_entry(name='action', value='acquire_phone'),
                self.historydb_entry(name='consumer', value='dev'),
                self.historydb_entry(name='user_agent', value='curl'),
            ])

        if phone_securified:
            historydb_entries.extend([
                self.historydb_entry(name='phone.1.number',
                                     value=TEST_PHONE_NUMBER_OBJECT.e164),
                self.historydb_entry(name='phone.1.operation.1.action', value='created'),
                self.historydb_entry(name='phone.1.operation.1.finished',
                                     value=TimeNow(offset=TEST_OPERATION_TTL.total_seconds())),
                self.historydb_entry(name='phone.1.operation.1.security_identity', value='1'),
                self.historydb_entry(name='phone.1.operation.1.started', value=TimeNow()),
                self.historydb_entry(name='phone.1.operation.1.type', value='securify'),
                self.historydb_entry(name='action', value='acquire_phone'),
                self.historydb_entry(name='consumer', value='dev'),
                self.historydb_entry(name='user_agent', value='curl'),
            ])

        if phonenumber_alias_was_busy:
            historydb_entries.extend([
                self.historydb_entry(uid=str(TEST_UID2), name='alias.phonenumber.rm', value=TEST_PHONE_NUMBER_OBJECT.international),
                self.historydb_entry(uid=str(TEST_UID2), name='action', value='phone_alias_delete'),
                self.historydb_entry(uid=str(TEST_UID2), name='consumer', value='dev'),
            ])

        if login:
            historydb_entries.append({'name': 'info.login', 'value': normalize_login(login)})
            if login != normalize_login(login):
                historydb_entries.append(
                    {'name': 'info.login_wanted', 'value': login},
                )

        if subscribed:
            historydb_entries.append(
                {'name': 'info.mail_status', 'value': '1'},
            )

        if with_optional_params:
            historydb_entries += [
                {'name': 'info.firstname', 'value': firstname or '-'},
                {'name': 'info.lastname', 'value': lastname or '-'},
            ]
        if display_name_updated:
            if display_name and not display_name['name']:
                value = '-'
            else:
                value = 'p:%s' % TEST_SOCIAL_DISPLAY_NAME_AFTER_COMPLETION['name']
            historydb_entries += [
                {'name': 'info.display_name', 'value': value},
            ]
        if with_optional_params:
            historydb_entries += [
                {'name': 'info.birthday', 'value': '1950-05-01'},
                {'name': 'info.country', 'value': 'tr'},
                {'name': 'info.lang', 'value': 'tr'},
            ]
        else:
            historydb_entries += [
                {'name': 'info.tz', 'value': 'America/New_York'},
            ]

        if with_password:
            eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=TEST_UID, db='passportdbshard1')
            historydb_entries += [
                {'name': 'info.password', 'value': eav_pass_hash},
                {'name': 'info.password_quality', 'value': str(TEST_PASSWORD_QUALITY)},
                {'name': 'info.password_update_time', 'value': TimeNow()},
            ]
        if secure_phone_bound:
            historydb_entries.extend([
                self.historydb_entry(name='info.karma_prefix', value='6'),
                self.historydb_entry(name='info.karma_full', value='6000'),
            ])
        if captcha_passed:
            historydb_entries += [
                {'name': 'info.hintq', 'value': '99:question'},
                {'name': 'info.hinta', 'value': 'answer'},
            ]

        if login:
            historydb_entries.append(
                {'name': 'alias.portal.add', 'value': normalize_login(login)},
            )

        if phone_aliasified:
            historydb_entries.append(
                {'name': 'alias.phonenumber.add', 'value': TEST_PHONE_NUMBER_OBJECT.international},
            )

        if subscribed:
            historydb_entries += [
                {'name': 'mail.add', 'value': '1'},
                {'name': 'sid.add', 'value': '2'},
            ]

        if secure_phone_bound:
            historydb_entries.extend([
                self.historydb_entry(name='phone.1.action', value='changed'),
                self.historydb_entry(name='phone.1.bound', value=TimeNow()),
                self.historydb_entry(name='phone.1.confirmed', value=TimeNow()),
                self.historydb_entry(name='phone.1.number', value=TEST_PHONE_NUMBER_OBJECT.e164),
                self.historydb_entry(name='phone.1.operation.1.action', value='deleted'),
                self.historydb_entry(name='phone.1.operation.1.security_identity', value='1'),
                self.historydb_entry(name='phone.1.operation.1.type', value='bind'),
                self.historydb_entry(name='phone.1.secured', value=TimeNow()),
                self.historydb_entry(name='phones.secure', value='1'),
            ])
        if phone_securified:
            entries = [
                self.historydb_entry(name='phone.1.action', value='changed'),
                self.historydb_entry(name='phone.1.number',
                                     value=TEST_PHONE_NUMBER_OBJECT.e164),
                self.historydb_entry(name='phone.1.operation.1.action', value='deleted'),
                self.historydb_entry(name='phone.1.operation.1.security_identity', value='1'),
                self.historydb_entry(name='phone.1.operation.1.type', value='securify'),
                self.historydb_entry(name='phone.1.secured', value=TimeNow()),
                self.historydb_entry(name='phones.secure', value='1'),
            ]
            if phone_validated:
                entries.insert(
                    1,
                    self.historydb_entry(name='phone.1.confirmed', value=TimeNow()),
                )
            historydb_entries.extend(entries)

        historydb_entries += [
            {'name': 'action', 'value': 'complete'},
            {'name': 'consumer', 'value': 'dev'},
            {'name': 'user_agent', 'value': TEST_USER_AGENT},
        ]

        if bad_user_karma:
            if secure_phone_bound:
                historydb_entries.extend([
                    self.historydb_entry(name='info.karma_prefix', value='0'),
                    self.historydb_entry(name='info.karma_full', value=str(bad_user_karma)),
                ])
            historydb_entries += [
                {'name': 'info.karma', 'value': str(bad_user_karma)},
            ]
            if not secure_phone_bound:
                historydb_entries += [
                    {'name': 'info.karma_full', 'value': str(bad_user_karma)},
                ]
            historydb_entries += [
                {'name': 'action', 'value': 'complete'},
                {'name': 'consumer', 'value': 'dev'},
                {'name': 'user_agent', 'value': TEST_USER_AGENT},
            ]

        self.assert_events_are_logged_with_order(self.env.handle_mock, historydb_entries)

    def check_statbox_entries(self, with_optional_params=True, display_name=None, display_name_updated=True,
                              captcha_passed=True, bad_user_karma=None, had_password=False, multi=False,
                              uids_count=1, phone_validated=None, login=TEST_LOGIN,
                              subscribed=False, old_login=None,
                              phone_securified=False, phone_aliasified=False,
                              with_cookies=True, secure_phone_bound=False,
                              firstname=TEST_FIRSTNAME, lastname=TEST_LASTNAME,
                              phonenumber_alias_was_busy=False, validated_via=None, with_check_cookies=True):
        normalized_login = normalize_login(login)

        if captcha_passed:
            validated_via = validated_via or 'captcha'
        elif phone_validated:
            validated_via = validated_via or 'phone'
        entries = []

        if with_check_cookies:
            entries += [self.env.statbox.entry('check_cookies')]

        if secure_phone_bound:
            entries += [self.env.statbox.entry('secure_bind_operation_created')]
        if phone_securified:
            entries += [self.env.statbox.entry('securify_operation_created')]
        if phonenumber_alias_was_busy:
            entries += [
                self.env.statbox.entry('phonenumber_alias_taken_away', uid=str(TEST_UID2)),
                self.env.statbox.entry('phonenumber_alias_subscription_removed', uid=str(TEST_UID2)),
            ]
        if phone_aliasified:
            entries += [
                self.env.statbox.entry(
                    'phonenumber_alias_given_out',
                    is_owner_changed=str(int(phonenumber_alias_was_busy)),
                ),
            ]

        entries += [
            self.env.statbox.entry(
                'validated',
                _exclude=['validated'] if validated_via is None else [],
                type=self.statbox_type,
                login=normalized_login,
                validated=validated_via,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='account.mail_status',
                operation='created',
                old='-',
                new='active',
            ),
        ]

        if login != old_login:
            if normalized_login != login:
                entries += [
                    self.env.statbox.entry(
                        'account_modification',
                        entity='user_defined_login',
                        operation='created',
                        old='-',
                        new=login,
                    ),
                ]

            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    _exclude=['old', 'new'],
                    entity='aliases',
                    operation='added',
                    type=str(ANT['portal']),
                    value=normalized_login,
                ),
            ]

        if phone_securified or secure_phone_bound:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='phones.secure',
                    operation='created',
                    new=TEST_PHONE_NUMBER_OBJECT.masked_format_for_statbox,
                    new_entity_id=str(TEST_PHONE_ID1),
                    old='-',
                    old_entity_id='-',
                ),
            ]

        if with_optional_params:
            for entity, old, new in [
                ('person.firstname', '\\\\u0414', firstname),
                ('person.lastname', '\\\\u0424', lastname),
                ('person.language', 'ru', 'tr'),
                ('person.country', 'ru', 'tr'),
                ('person.birthday', '1963-05-15', '1950-05-01'),
            ]:
                entries += [
                    self.env.statbox.entry(
                        'account_modification',
                        entity=entity,
                        old=old,
                        new=new,
                    ),
                ]

        if display_name_updated:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.display_name',
                    old='s:123456:fb:Some User',
                    new=display_name['name'] if display_name else 'p:Some User',
                ),
            ]

        if with_optional_params:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.fullname',
                    old='\\\\u0414 \\\\u0424',
                    new='{} {}'.format(firstname, lastname),
                ),
            ]

        if not had_password:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='password.encrypted',
                    operation='created',
                    _exclude=['new', 'old'],
                ),
                self.env.statbox.entry(
                    'account_modification',
                    entity='password.encoding_version',
                    old='-',
                    operation='created',
                    new=str(self.password_hash_version),
                ),
                self.env.statbox.entry(
                    'account_modification',
                    entity='password.quality',
                    old='10' if had_password else '-',
                    operation='created',
                    new=str(TEST_PASSWORD_QUALITY),
                ),
            ]

        if captcha_passed:
            for entity, old, new in [
                ('hint.question', 'ru', 'tr'),
                ('hint.answer', '10' if had_password else '-', str(TEST_PASSWORD_QUALITY)),
            ]:
                entries += [
                    self.env.statbox.entry(
                        'account_modification',
                        _exclude=['old', 'new'],
                        entity=entity,
                        operation='created',
                    ),
                ]

        if secure_phone_bound:
            entries += [
                self.env.statbox.entry(
                    'frodo_karma',
                    _exclude=['suid'] if not subscribed else [],
                    login=old_login,
                ),
            ]

        if subscribed:
            entries += [self.env.statbox.entry('subscriptions')]

        if phone_aliasified:
            entries += [self.env.statbox.entry('phonenumber_alias_subscription_added')]

        if phone_validated:
            entries += [
                self.env.statbox.entry('phone_confirmed'),
            ]
        if phone_securified:
            entries += [self.env.statbox.entry('phone_secured')]

        if secure_phone_bound:
            entries += [self.env.statbox.entry('secure_phone_bound')]

        if with_cookies:
            entries += [
                self.env.statbox.entry(
                    'cookie_set',
                    input_login=login,
                    captcha_passed='1' if captcha_passed else '0',
                    uids_count=str(uids_count),
                    session_method='edit' if multi else 'create',
                    person_country='tr' if with_optional_params else 'ru',
                    old_session_uids=('1' if uids_count == 1 else '1,2') if multi else None,
                ),
                self.env.statbox.entry('multibrowser_update'),
            ]

        if bad_user_karma is not None:
            entries.append(
                self.env.statbox.entry(
                    'frodo_karma',
                    old='6000' if secure_phone_bound else '0',
                    new=str(bad_user_karma),
                    suid='1' if subscribed else '-',
                    login=login,
                ),
            )

        self.assert_statbox_has_written(entries)

    def check_response_error(self, response, errors, with_retpath=True, with_account=True,
                             login=TEST_SOCIAL_LOGIN, display_login='', display_name=None,
                             statbox_call_count=1, with_track_id=True):
        response_data = json.loads(response.data)

        expected_response = {
            'status': 'error',
            'errors': errors,
        }

        if with_track_id:
            expected_response['track_id'] = self.track_id

        if with_retpath:
            expected_response['retpath'] = TEST_RETPATH

        if with_account:
            expected_response['account'] = get_account_info(
                login=login,
                display_login=display_login,
                display_name=display_name,
                public_id=TEST_PUBLIC_ID,
            )

        eq_(response.status_code, 200)

        iterdiff(eq_)(
            response_data,
            expected_response,
        )

        eq_(self.env.auth_handle_mock.call_count, 0)
        eq_(len(self.env.frodo.requests), 0)
        eq_(self.env.statbox_handle_mock.call_count, statbox_call_count)

    def create_frodo_params(self, **kwargs):
        params = {
            'uid': str(TEST_UID),
            'login': TEST_LOGIN,
            'iname': TEST_FIRSTNAME,
            'fname': TEST_LASTNAME,
            'from': 'dev',
            'consumer': 'dev',
            'passwd': '10.0.9.1',
            'passwdex': '3.6.0.0',
            'v2_password_quality': str(TEST_PASSWORD_QUALITY),
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
            'action': 'complete',
            'v2_track_created': TimeNow(),
            'xcountry': 'tr',
            'lang': 'tr',
            'v2_account_karma': '0',
            'v2_old_password_quality': '',
            'v2_account_country': 'tr',
            'v2_account_language': 'tr',
            'v2_account_timezone': 'Europe/Moscow',
            'v2_accept_language': 'ru',
            'v2_is_ssl': '1',
            'v2_has_cookie_l': '1',
            'v2_has_cookie_yandex_login': '0',
            'v2_has_cookie_my': '1',
            'v2_has_cookie_ys': '0',
            'v2_has_cookie_yp': '0',
            'v2_cookie_my_block_count': '1',
            'v2_cookie_my_language': 'tt',
            'v2_cookie_l_login': 'test_user',
            'v2_cookie_l_uid': str(TEST_UID),
            'v2_cookie_l_timestamp': str(TEST_COOKIE_TIMESTAMP),
        }
        params.update(**kwargs)
        return EmptyFrodoParams(**params)

    def check_db(self, with_optional_params=True, had_password=False, dbshard_name='passportdbshard1'):
        timenow = TimeNow()

        if with_optional_params:
            self.env.db.check('attributes', 'person.country', 'tr', uid=TEST_UID, db=dbshard_name)
            self.env.db.check('attributes', 'person.language', 'tr', uid=TEST_UID, db=dbshard_name)
            self.env.db.check_missing('attributes', 'person.timezone', uid=TEST_UID, db=dbshard_name)
            self.env.db.check('attributes', 'person.birthday', '1950-05-01', uid=TEST_UID, db=dbshard_name)
        else:
            self.env.db.check_missing('attributes', 'person.country', uid=TEST_UID, db=dbshard_name)
            self.env.db.check_missing('attributes', 'person.language', uid=TEST_UID, db=dbshard_name)
            self.env.db.check('attributes', 'person.timezone', 'America/New_York', uid=TEST_UID, db=dbshard_name)
            self.env.db.check('attributes', 'person.birthday', '1963-05-15', uid=TEST_UID, db=dbshard_name)

        self.env.db.check('attributes', 'person.gender', 'm', uid=TEST_UID, db=dbshard_name)
        self.env.db.check_missing('attributes', 'password.is_creating_required', uid=TEST_UID, db=dbshard_name)
        self.env.db.check_missing('attributes', 'password.forced_changing_reason', uid=TEST_UID, db=dbshard_name)

        if not had_password:
            self.env.db.check('attributes', 'password.update_datetime', timenow, uid=TEST_UID, db=dbshard_name)
            self.env.db.check('attributes', 'password.quality', '3:%d' % TEST_PASSWORD_QUALITY, uid=TEST_UID,
                              db=dbshard_name)

    def check_track(self, retpath=TEST_RETPATH, login=TEST_LOGIN):
        track = self.track_manager.read(self.track_id)
        eq_(track.track_type, self.track_type)
        eq_(track.retpath, retpath)
        eq_(track.login, login)

    def build_account(self, account=None, registration_is_complete=False):
        account = account or {}
        account = deep_merge(account, {'userinfo': {'public_id': TEST_PUBLIC_ID}})

        account.setdefault(
            'loginoccupation',
            {'statuses': {TEST_LOGIN: 'free'}},
        )

        if registration_is_complete:
            account = complete(account)

        return account

    def setup_account(self, account=None, authentication_media=None):
        account = account or self.build_account()
        authentication_media = authentication_media or self.authentication_media
        self.setup_multi_accounts(
            incomplete_account=account,
            extra_accounts=[],
            authentication_media=authentication_media,
        )

    def setup_multi_accounts(self, incomplete_account, extra_accounts,
                             default_account=None,
                             authentication_media='session'):
        if default_account is None:
            default_account = incomplete_account

        self.setup_session(default_account, extra_accounts)

        if authentication_media in ['key', 'password']:
            userinfo_args = incomplete_account['userinfo']
            userinfo_response = blackbox_userinfo_response(**userinfo_args)
            self.env.blackbox.set_blackbox_response_value(
                'userinfo',
                userinfo_response,
            )

        serialized_accounts = []
        all_accounts = chain(
            [incomplete_account, default_account],
            extra_accounts,
        )
        for account in all_accounts:
            if account not in serialized_accounts and account is not None:
                self.env.db.serialize(
                    blackbox_userinfo_response(**account['userinfo']),
                )
                serialized_accounts.append(account)

        if incomplete_account is not None:
            loginoccupation_args = incomplete_account.get('loginoccupation')
            if loginoccupation_args is not None:
                self.env.blackbox.set_blackbox_response_value(
                    'loginoccupation',
                    blackbox_loginoccupation_response(**loginoccupation_args),
                )

        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

    def setup_session(self, default_account, extra_accounts):
        sessionid_args = deep_merge(
            default_account['userinfo'],
            default_account['sessionid'],
        )
        sessionid_response = blackbox_sessionid_multi_response(**sessionid_args)
        for extra_account in extra_accounts:
            sessionid_args = deep_merge(
                extra_account['userinfo'],
                extra_account['sessionid'],
            )
            sessionid_response = blackbox_sessionid_multi_append_user(
                sessionid_response,
                **sessionid_args
            )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

    def setup_multi_accounts_by_token(self, incomplete_account, extra_accounts=[]):
        self.setup_token(incomplete_account)

        serialized_accounts = []
        all_accounts = [incomplete_account] + extra_accounts
        for account in all_accounts:
            if account not in serialized_accounts and account is not None:
                self.env.db.serialize(
                    blackbox_userinfo_response(**account['userinfo']),
                )
                serialized_accounts.append(account)

        if incomplete_account is not None:
            loginoccupation_args = incomplete_account.get('loginoccupation')
            if loginoccupation_args is not None:
                self.env.blackbox.set_blackbox_response_value(
                    'loginoccupation',
                    blackbox_loginoccupation_response(**loginoccupation_args),
                )

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

    def setup_token(self, incomplete_account):
        oauth_args = deep_merge(
            incomplete_account['userinfo'],
            incomplete_account['oauth'],
        )
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(**oauth_args),
        )
