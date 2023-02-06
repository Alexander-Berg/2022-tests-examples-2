# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.forms import (
    CAPTCHA_VALIDATION_METHOD,
    PHONE_VALIDATION_METHOD,
)
from passport.backend.api.test.mixins import make_clean_web_test_mixin
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.builders.frodo.utils import get_phone_number_hash
from passport.backend.core.counters import (
    registration_karma,
    sms_per_ip,
)
from passport.backend.core.frodo.exceptions import FrodoError
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.models.phones.faker import (
    assert_account_has_phonenumber_alias,
    assert_phonenumber_alias_missing,
    assert_secure_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)


TEST_HOST = 'yandex.ru'
TEST_USER_IP = '37.9.101.188'
TEST_USER_AGENT = 'curl'
TEST_RETPATH = 'http://ya.ru'
TEST_YANDEXUID_COOKIE = 'cookie_yandexuid'
TEST_YANDEX_GID_COOKIE = 'cookie_yandex_gid'
TEST_FUID01_COOKIE = 'cookie_fuid01'
TEST_USER_COOKIES = 'yandexuid=%s; yandex_gid=%s; fuid01=%s' % (
    TEST_YANDEXUID_COOKIE, TEST_YANDEX_GID_COOKIE, TEST_FUID01_COOKIE,
)
TEST_USER_LOGIN = 'test.login'
TEST_USER_LOGIN_NORMALIZED = 'test-login'
TEST_ACCEPT_LANGUAGE = 'ru'
TEST_ORIGIN = 'origin'

TEST_HINT_QUESTION_ID = '1'
TEST_HINT_QUESTION = '%s:Your mother\'s maiden name' % TEST_HINT_QUESTION_ID
TEST_HINT_ANSWER = 'answer'

TEST_PHONE_NUMBER = PhoneNumber.parse('+79999999999')
TEST_PHONE_NUMBER_MASKED_FOR_FRODO = '79990009999'

SUCCESSFUL_REGISTRATION_RESPONSE = {
    'status': 'ok',
    'uid': 1,
}


def build_headers(host=None, user_ip=None):
    return mock_headers(
        host=host or TEST_HOST,
        user_ip=user_ip or TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        x_forwarded_for=True,
        cookie=TEST_USER_COOKIES,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    CLEAN_WEB_API_ENABLED=False,
    SENDER_MAIL_SUBSCRIPTION_SERVICES=[
        {
            'id': 1,
            'origin_prefixes': [TEST_ORIGIN],
            'app_ids': [],
            'slug': None,
            'external_list_ids': [],
        },
        {
            'id': 2,
            'origin_prefixes': [],
            'app_ids': ['ru.yandex.smth_other'],
            'slug': None,
            'external_list_ids': [],
        },
    ],
)
class TestAccountRegisterAlternativeBase(BaseTestViews):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['register_alternative']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )
        self.setup_statbox_templates()

        self.patches = []

    def tearDown(self):
        self.env.stop()
        for p in self.patches:
            p.stop()
        del self.env
        del self.patches
        del self.track_manager

    def account_register_request(self, data, headers, consumer='dev'):
        return self.env.client.post(
            '/1/account/register/alternative/?consumer=%s' % consumer,
            data=data,
            headers=headers,
        )

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'track_id': self.track_id,
            'login': TEST_USER_LOGIN,
            'firstname': 'firstname',
            'lastname': 'lastname',
            'language': 'en',
            'country': 'tr',
            'gender': '1',
            'birthday': '1950-12-30',
            'timezone': 'Europe/Paris',
            'eula_accepted': 'True',
            'display_language': 'en',
            'password': 'aaa1bbbccc',
        }
        params = merge_dicts(base_params, kwargs)
        if exclude is not None:
            for key in exclude:
                del params[key]
        return params

    def get_registration_sms_counter(self):
        return sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP)

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='alternative',
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'submitted',
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'frodo_karma',
            _exclude=['mode', 'track_id'],
            uid='1',
            login=TEST_USER_LOGIN_NORMALIZED,
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            consumer='dev',
            registration_datetime=DatetimeNow(convert_to_datetime=True),
        )
        self.env.statbox.bind_entry(
            'subscriptions',
            _exclude=['mode', 'track_id'],
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            consumer='dev',
            operation='added',
        )
        self.env.statbox.bind_entry(
            'account_created',
            ip=TEST_USER_IP,
            country='tr',
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'registration_sms_per_ip_limit_has_exceeded',
            mode='alternative_phone',
            action='registration_with_sms',
            error='registration_sms_per_ip_limit_has_exceeded',
            ip=TEST_USER_IP,
            counter_prefix='registration:sms:ip',
            is_special_testing_ip='0',
        )

        self.env.statbox.bind_entry(
            'base_phone_entry',
            mode='alternative_phone',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'local_phone_confirmed',
            _inherit_from=['phone_confirmed', 'base_phone_entry'],
            _exclude={'operation_id'},
            phone_id='1',
            confirmation_time=DatetimeNow(convert_to_datetime=True),
            code_checks_count='0',
        )
        self.env.statbox.bind_entry(
            'local_secure_phone_bound',
            _inherit_from=['secure_phone_bound', 'base_phone_entry'],
            _exclude={'operation_id'},
            phone_id='1',
        )

    def check_statbox(self, has_hint=False, suid='1', bind_secure=False,
                      with_phonenumber_alias=False, **account_created_kwargs):
        entries = [self.env.statbox.entry('submitted')]
        if with_phonenumber_alias:
            entries.extend([self.env.statbox.entry('phonenumber_alias_given_out')])
        entries.extend([
            self.env.statbox.entry(
                'account_modification',
                operation='created',
                ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
                consumer='dev',
                entity='account.disabled_status',
                old='-',
                new='enabled',
            ),
            self.env.statbox.entry(
                'account_modification',
                operation='created',
                ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
                consumer='dev',
                entity='account.mail_status',
                old='-',
                new='active',
            ),
            self.env.statbox.entry(
                'account_modification',
                operation='created',
                ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
                consumer='dev',
                entity='user_defined_login',
                old='-',
                new=TEST_USER_LOGIN,
            ),
            self.env.statbox.entry(
                'account_modification',
                operation='added',
                ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
                consumer='dev',
                entity='aliases',
                type='1',
                value=TEST_USER_LOGIN_NORMALIZED,
            ),
        ])
        if with_phonenumber_alias:
            entries.extend([self.env.statbox.entry('phonenumber_alias_added')])
        if bind_secure:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    operation='created',
                    ip=TEST_USER_IP,
                    user_agent=TEST_USER_AGENT,
                    consumer='dev',
                    entity='phones.secure',
                    old='-',
                    old_entity_id='-',
                    new=TEST_PHONE_NUMBER.masked_format_for_statbox,
                    new_entity_id='1',
                ),
            ])

        names_values = []
        names_values += [
            ('person.firstname', {'old': '-', 'new': 'firstname'}),
            ('person.lastname', {'old': '-', 'new': 'lastname'}),
            ('person.language', {'old': '-', 'new': 'en'}),
            ('person.country', {'old': '-', 'new': 'tr'}),
            ('person.gender', {'old': '-', 'new': 'm'}),
            ('person.birthday', {'old': '-', 'new': '1950-12-30'}),
            ('person.fullname', {'old': '-', 'new': 'firstname lastname'}),
            ('password.encrypted', {}),
            ('password.encoding_version', {'old': '-', 'new': str(self.password_hash_version)}),
            ('password.quality', {'old': '-', 'new': '80'}),
        ]
        if has_hint:
            names_values += [
                ('hint.question', {}),
                ('hint.answer', {}),
            ]

        entries += [
            self.env.statbox.entry(
                'account_modification',
                operation='created',
                ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
                consumer='dev',
                entity=entity,
                **kwargs
            )
            for entity, kwargs in names_values
        ] + [
            self.env.statbox.entry(
                'frodo_karma',
                action='account_register',
                suid=suid,
            ),
            self.env.statbox.entry('subscriptions', sid='8'),
            self.env.statbox.entry('subscriptions', sid='2', suid=suid),
        ]
        if with_phonenumber_alias:
            entries.extend([
                self.env.statbox.entry('phonenumber_alias_subscription_added'),
                self.env.statbox.entry('phonenumber_alias_search_disabled'),
            ])
        if bind_secure:
            entries += [
                self.env.statbox.entry('local_phone_confirmed'),
                self.env.statbox.entry('local_secure_phone_bound'),
            ]

        karma_value = account_created_kwargs.get('karma')
        if karma_value and karma_value != '0':
            frodo_action = account_created_kwargs.pop('frodo_action', '')
            entries.append(
                self.env.statbox.entry(
                    'frodo_karma',
                    action=frodo_action,
                    suid=suid,
                    old='0',
                    new=karma_value,
                ),
            )

        entries.append(
            self.env.statbox.entry('account_created', **account_created_kwargs),
        )
        self.env.statbox.assert_has_written(entries)

    def frodo_params(self, **kwargs):
        params = EmptyFrodoParams(**{
            'uid': '1',
            'login': TEST_USER_LOGIN_NORMALIZED,
            'iname': 'firstname',
            'fname': 'lastname',
            'consumer': 'dev',
            'passwd': '10.0.9.1',
            'passwdex': '3.6.0.0',
            'v2_password_quality': '80',
            'hintq': '0.0.0.0.0.0',
            'hintqex': '0.0.0.0.0.0',
            'hinta': '0.0.0.0.0.0',
            'hintaex': '0.0.0.0.0.0',
            'yandexuid': TEST_YANDEXUID_COOKIE,
            'v2_yandex_gid': TEST_YANDEX_GID_COOKIE,
            'fuid': TEST_FUID01_COOKIE,
            'useragent': 'curl',
            'host': 'yandex.ru',
            'ip_from': TEST_USER_IP,
            'v2_ip': TEST_USER_IP,
            'valkey': '0000000000',
            'action': 'postregistration',
            'lang': 'en',
            'xcountry': 'tr',
            'v2_track_created': TimeNow(),
            'v2_old_password_quality': '',
            'v2_account_country': 'tr',
            'v2_account_language': 'en',
            'v2_account_timezone': 'Europe/Paris',
            'v2_account_karma': '',
            'v2_accept_language': 'ru',
            'v2_is_ssl': '1',
            'v2_has_cookie_l': '0',
            'v2_has_cookie_yandex_login': '0',
            'v2_has_cookie_my': '0',
            'v2_has_cookie_ys': '0',
            'v2_has_cookie_yp': '0',
        })
        params.update(**kwargs)
        return params

    def eula_not_accepted(self, query_params, headers):
        rv = self.account_register_request(
            query_params,
            headers,
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'Eula is not accepted',
                    u'code': u'eulaisnotacceptederror',
                }],
            },
        )

    def invalid_password_error(self, query_params, headers, extra_invalid_args=None):
        invalid_password_args = [
            (
                '.',
                [{
                    u'field': u'password',
                    u'code': u'tooshort',
                    u'message': u'Password has less 6 symbols',
                }],
            ),
            (
                TEST_USER_LOGIN,
                [{
                    u'field': u'password',
                    u'code': u'likelogin',
                    u'message': u'Password is the same as login',
                }],
            ),
            (
                'aaabbb',
                [{
                    u'field': u'password',
                    u'code': u'weak',
                    u'message': u'Password is not strong',
                }],
            ),
            (
                '%s@yandex.ru' % TEST_USER_LOGIN,
                [{
                    u'field': u'password',
                    u'code': u'likelogin',
                    u'message': u'Password is the same as login',
                }],
            ),
        ]
        if extra_invalid_args:
            invalid_password_args.extend(extra_invalid_args)

        for password, expected_errors in invalid_password_args:
            rv = self.account_register_request(
                merge_dicts(query_params, dict(password=password)),
                headers,
            )

            eq_(rv.status_code, 400, [rv.status_code, rv.data])
            eq_(
                json.loads(rv.data),
                {
                    u'status': u'error',
                    u'errors': expected_errors,
                },
            )

    def login_not_available(self, query_params, headers):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'occupied'}),
        )

        rv = self.account_register_request(
            query_params,
            headers,
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': [{
                    'field': 'login',
                    'message': 'Login is not available',
                    'code': 'notavailable',
                }],
            },
        )

    def frodo_call(self, query_params, headers, frodo_params, statbox_kwargs=None):
        self.env.frodo.set_response_value(
            u'check',
            u'<spamlist><spam_user login="%s" weight="85" /></spamlist>' % (
                TEST_USER_LOGIN_NORMALIZED,
            ),
        )
        rv = self.account_register_request(
            query_params,
            headers,
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '85')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '85')

        self.env.db.check('attributes', 'karma.value', '85', uid=1, db='passportdbshard1')

        # Проверяем параметры для frodo
        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(frodo_params)
        self.check_statbox(karma='85', frodo_action=frodo_params['action'], **(statbox_kwargs or {}))

    def frodo_error(self, query_params, headers):
        self.env.frodo.set_response_side_effect(u'check', FrodoError('Failed'))

        rv = self.account_register_request(
            query_params,
            headers,
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)

        assert_builder_requested(self.env.frodo, times=1)

        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '0')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '0')

    def track_content(self):
        rv = self.account_register_request(
            self.query_params(language='tr'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)

        track = self.track_manager.read(self.track_id)
        eq_(track.uid, '1')
        eq_(track.login, TEST_USER_LOGIN)
        eq_(track.user_entered_login, TEST_USER_LOGIN)
        eq_(track.human_readable_login, TEST_USER_LOGIN)
        eq_(track.machine_readable_login, TEST_USER_LOGIN_NORMALIZED)

        eq_(track.language, 'tr')
        eq_(track.have_password, True)
        eq_(track.is_successful_registered, True)
        eq_(track.allow_authorization, True)
        eq_(track.allow_oauth_authorization, True)

    def track_content_language_in_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.language = 'en'

        rv = self.account_register_request(
            self.query_params(language='tr'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)

        track = self.track_manager.read(self.track_id)
        eq_(track.uid, '1')
        eq_(track.login, TEST_USER_LOGIN)
        eq_(track.user_entered_login, TEST_USER_LOGIN)
        eq_(track.human_readable_login, TEST_USER_LOGIN)
        eq_(track.machine_readable_login, TEST_USER_LOGIN_NORMALIZED)

        eq_(track.language, 'en')
        eq_(track.have_password, True)
        eq_(track.is_successful_registered, True)
        eq_(track.allow_authorization, True)
        eq_(track.allow_oauth_authorization, True)

    def timezone_detection(self, central_query_count=4, shard_query_count=1):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
        rv = self.account_register_request(
            self.query_params(exclude=['timezone']),
            build_headers(user_ip='8.8.8.8'),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), central_query_count)
        eq_(self.env.db.query_count('passportdbshard1'), shard_query_count)
        self.env.db.check('attributes', 'person.timezone', 'America/New_York', uid=1, db='passportdbshard1')


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    **mock_counters()
)
class TestAccountRegisterAlternativeCommon(TestAccountRegisterAlternativeBase):
    def query_params(self, exclude=None, **kwargs):
        base = {
            'validation_method': CAPTCHA_VALIDATION_METHOD,
            'hint_question_id': TEST_HINT_QUESTION_ID,
            'hint_answer': TEST_HINT_ANSWER,
        }
        kwargs = merge_dicts(base, kwargs)
        return super(TestAccountRegisterAlternativeCommon, self).query_params(exclude, **kwargs)

    def test_without_need_headers(self):
        rv = self.account_register_request(self.query_params(), {})

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'Missing required headers: "Ya-Client-User-Agent, Ya-Consumer-Client-Ip"',
                    u'code': u'missingheader',
                }],
            },
        )

    def test_without_consumer(self):
        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
            consumer='',
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': u'consumer',
                    u'message': u'Missing value',
                    u'code': u'missingvalue',
                }],
            },
        )

    def test_without_track(self):
        rv = self.account_register_request(
            self.query_params(exclude=['track_id']),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': u'track_id',
                    u'message': u'Missing value',
                    u'code': u'missingvalue',
                }],
            },
        )

    def test_login_not_available(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'occupied'}),
        )

        rv = self.account_register_request(
            self.query_params(login=TEST_USER_LOGIN),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': [{
                    'field': 'login',
                    'message': 'Login is not available',
                    'code': 'notavailable',
                }],
            },
        )

    def test_unknown_alternative(self):
        with mock.patch('passport.backend.api.forms.AccountRegisterSelectAlternative.to_python') as form_mock:
            form_mock.return_value = {'validation_method': 'bla', 'consumer': 'dev'}
            rv = self.account_register_request(
                self.query_params(login=TEST_USER_LOGIN),
                build_headers(),
            )

            eq_(rv.status_code, 500, [rv.status_code, rv.data])
            eq_(
                json.loads(rv.data),
                {
                    'status': 'error',
                    'errors': [{
                        'field': None,
                        'message': 'Unknown alternative registration type',
                        'code': 'unknownalternativeregistrationtypeerror',
                    }],
                },
            )

    @parameterized.expand(['firstname', 'lastname'])
    def test_fraud(self, field):
        rv = self.account_register_request(
            self.query_params(**{field: u'Заходи дорогой, гостем будешь диваны.рф'}),
            build_headers(),
        )
        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': field,
                    u'message': u'Invalid value',
                    u'code': u'invalid',
                }],
            },
        )


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    **mock_counters()
)
class TestAccountRegisterAlternativeCaptcha(TestAccountRegisterAlternativeBase,
                                            make_clean_web_test_mixin('test_db_historydb_logs_statbox_logs', ['firstname', 'lastname'], is_bundle=False),
                                            ):
    def setUp(self):
        super(TestAccountRegisterAlternativeCaptcha, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = True

    def query_params(self, exclude=None, **kwargs):
        base = {
            'validation_method': CAPTCHA_VALIDATION_METHOD,
            'hint_question_id': TEST_HINT_QUESTION_ID,
            'hint_answer': TEST_HINT_ANSWER,
        }
        kwargs = merge_dicts(base, kwargs)
        return super(TestAccountRegisterAlternativeCaptcha, self).query_params(exclude, **kwargs)

    def test_eula_not_accepted(self):
        self.eula_not_accepted(
            self.query_params(eula_accepted='0'),
            build_headers(),
        )

    def test_invalid_password_error(self):
        self.invalid_password_error(
            self.query_params(),
            build_headers(),
        )

    def test_login_not_available(self):
        self.login_not_available(
            self.query_params(),
            build_headers(),
        )

    def test_frodo_call(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.captcha_generate_count.incr()
            track.captcha_key = '1p'
        self.frodo_call(
            self.query_params(),
            build_headers(),
            self.frodo_params(
                action='alternative_hint',
                hintqid='1',
                hintaex='2.4.0.0.0',
                hinta='6.0.6.0.0.0',
                captchacount='1',
            ),
            statbox_kwargs={
                'captcha_generation_number': '1',
                'mode': 'alternative_hint',
                'has_hint': True,
                'question_id': '1',
                'is_voice_generated': '0',
                'captcha_key': '1p',
            },
        )

    def test_frodo_error(self):
        self.frodo_error(
            self.query_params(),
            build_headers(),
        )

    def test_track_content(self):
        self.track_content()

    def test_track_content_language_in_track(self):
        self.track_content_language_in_track()

    def test_with_captcha_not_passed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False
        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'User was not verified',
                    u'code': u'usernotverifiederror',
                }],
            },
        )

    def test_not_call_yasms(self):
        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)
        eq_(len(self.env.yasms.requests), 0)

    def test_db_historydb_logs_statbox_logs(self):
        timenow = TimeNow()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.captcha_generate_count.incr()
            track.captcha_key = '1p'

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check('aliases', 'portal', TEST_USER_LOGIN_NORMALIZED, uid=1, db='passportdbcentral')
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.city', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.user_defined_login', TEST_USER_LOGIN, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.firstname', 'firstname', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.lastname', 'lastname', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.gender', 'm', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.birthday', '1950-12-30', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.timezone', 'Europe/Paris', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.country', 'tr', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.language', 'en', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.quality', '3:80', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'hint.question.serialized', TEST_HINT_QUESTION, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'hint.answer.encrypted', TEST_HINT_ANSWER, uid=1, db='passportdbshard1')

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=1, db='passportdbshard1')
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('%s:' % self.password_hash_version))

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'account_register',
                'consumer': 'dev',
                'info.login': TEST_USER_LOGIN_NORMALIZED,
                'info.login_wanted': TEST_USER_LOGIN,
                'info.ena': '1',
                'info.disabled_status': '0',
                'info.firstname': 'firstname',
                'info.lastname': 'lastname',
                'info.sex': '1',
                'info.birthday': '1950-12-30',
                'info.tz': 'Europe/Paris',
                'info.country': 'tr',
                'info.mail_status': '1',
                'info.password_quality': '80',
                'info.password': eav_pass_hash,
                'info.password_update_time': timenow,
                'info.lang': 'en',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'info.hintq': TEST_HINT_QUESTION,
                'info.hinta': 'answer',
                'sid.add': '8|%s,2' % TEST_USER_LOGIN,
                'mail.add': '1',
                'alias.portal.add': TEST_USER_LOGIN_NORMALIZED,
                'info.karma': '0',
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'user_agent': 'curl',
            },
        )

        self.check_statbox(
            mode='alternative_hint',
            has_hint=True,
            captcha_generation_number='1',
            question_id='1',
            is_voice_generated='0',
            captcha_key='1p',
        )

    def test_timezone_detection(self):
        self.timezone_detection()

    def test_hint_question(self):
        rv = self.account_register_request(
            self.query_params(
                hint_question='Custom question',
                exclude=['hint_question_id'],
            ),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        self.env.db.check('attributes', 'hint.question.serialized', '99:Custom question', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'hint.answer.encrypted', TEST_HINT_ANSWER, uid=1, db='passportdbshard1')
        self.check_statbox(
            mode='alternative_hint',
            has_hint=True,
            question_id='99',
            captcha_generation_number='0',
            is_voice_generated='0',
        )

    def test_plus_promo_code(self):
        plus_promo_code = '1234567890'
        rv = self.account_register_request(
            self.query_params(
                hint_question='Custom question',
                plus_promo_code=plus_promo_code,
                exclude=['hint_question_id'],
            ),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        assert self.env.mailer.message_count
        message = self.env.mailer.messages[0]
        assert plus_promo_code in message.body
        assert message.recipients == [('', TEST_USER_LOGIN + '@yandex.ru')]

        self.check_statbox(
            # про этот тест
            with_plus_promo_code='1',
            # boilerplate
            mode='alternative_hint',
            has_hint=True,
            question_id='99',
            captcha_generation_number='0',
            is_voice_generated='0',
        )

    def test_plus_promo_code_html_tags(self):
        plus_promo_code = '<plus_promo_code>'
        rv = self.account_register_request(
            self.query_params(
                hint_question='Custom question',
                plus_promo_code=plus_promo_code,
                exclude=['hint_question_id'],
            ),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        assert self.env.mailer.message_count
        message = self.env.mailer.messages[0]
        assert plus_promo_code not in message.body
        assert '&lt;plus_promo_code&gt;' in message.body
        assert message.recipients == [('', TEST_USER_LOGIN + '@yandex.ru')]
        assert message.sender == (u'Яндекс.Плюс', 'hello@plus.yandex.ru')

    def test_plus_promo_code_too_long(self):
        plus_promo_code = 'a' * 51
        rv = self.account_register_request(
            self.query_params(
                hint_question='Custom question',
                plus_promo_code=plus_promo_code,
                exclude=['hint_question_id'],
            ),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        assert not self.env.mailer.message_count

    def test_plus_promo_code_comge(self):
        plus_promo_code = '1234567890'
        rv = self.account_register_request(
            self.query_params(
                hint_question='Custom question',
                plus_promo_code=plus_promo_code,
                exclude=['hint_question_id'],
            ),
            build_headers(
                host='yandex.com.ge'
            ),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        self.env.db.check('attributes', 'hint.question.serialized', '99:Custom question', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'hint.answer.encrypted', TEST_HINT_ANSWER, uid=1, db='passportdbshard1')

        assert self.env.mailer.message_count
        message = self.env.mailer.messages[0]
        assert plus_promo_code in message.body
        assert message.recipients == [('', TEST_USER_LOGIN + '@yandex.com.ge')]
        assert message.sender == (u'Яндекс.Плюс', 'hello@plus.yandex.ru')

        self.check_statbox(
            # про этот тест
            with_plus_promo_code='1',
            # boilerplate
            mode='alternative_hint',
            has_hint=True,
            question_id='99',
            captcha_generation_number='0',
            is_voice_generated='0',
        )

    def test_statbox_logs_with_voice_captcha(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = True
            track.voice_captcha_type = 'rus'
            track.captcha_key = '1p'

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        self.check_statbox(
            mode='alternative_hint',
            has_hint=True,
            question_id='1',
            captcha_generation_number='0',
            is_voice_generated='1',
            captcha_key='1p',
        )

    def test_captcha_registration__captcha_ok__sms_counter_not_incremented(self):
        """При регистрации с капчей, не увеличивается счетчик регистраций через sms"""
        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        sms_registation_counter = sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP)
        eq_(sms_registation_counter.get(TEST_USER_IP), 0)


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    **mock_counters()
)
class TestAccountRegisterAlternativePhone(TestAccountRegisterAlternativeBase,
                                          make_clean_web_test_mixin('test_db_historydb_logs_statbox_logs', ['firstname', 'lastname'], statbox_action='phone_confirmed', is_bundle=False),
                                          ):
    def setUp(self):
        super(TestAccountRegisterAlternativePhone, self).setUp()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

    def setup_statbox_templates(self):
        super(TestAccountRegisterAlternativePhone, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'phonenumber_alias_given_out',
            mode='alternative_phone',
            login=TEST_USER_LOGIN,
            uid='-',
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            ip=TEST_USER_IP,
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_added',
            _exclude=['mode', 'track_id'],
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_subscription_added',
            _exclude=['mode', 'track_id'],
            ip=TEST_USER_IP,
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_search_disabled',
            _inherit_from=['phonenumber_alias_search_enabled'],
            _exclude=['mode', 'track_id'],
            new='0',
            ip=TEST_USER_IP,
        )

    def query_params(self, exclude=None, **kwargs):
        base = {
            'validation_method': PHONE_VALIDATION_METHOD,
        }
        kwargs = merge_dicts(base, kwargs)
        return super(TestAccountRegisterAlternativePhone, self).query_params(exclude, **kwargs)

    def test_eula_not_accepted(self):
        self.eula_not_accepted(
            self.query_params(eula_accepted='0'),
            build_headers(),
        )

    def test_invalid_password_error(self):
        invalid_args = [
            (
                TEST_PHONE_NUMBER.e164,
                [{
                    u'field': u'password',
                    u'code': u'likephonenumber',
                    u'message': u'Password is the same as phone number',
                }],
            ),
        ]
        self.invalid_password_error(
            self.query_params(),
            build_headers(),
            extra_invalid_args=invalid_args,
        )

    def test_invalid_password_ignored_for_mobileproxy(self):
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='mobileproxy', grants={'account': ['register_alternative']}),
        )

        rv = self.account_register_request(
            self.query_params(password=TEST_PHONE_NUMBER.e164),
            build_headers(),
            consumer='mobileproxy',
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)

        eq_(len(self.env.yasms.requests), 0)
        self.env.blackbox.requests[3 if self.is_password_hash_from_blackbox else 2].assert_query_contains({
            'method': 'phone_bindings',
            'numbers': TEST_PHONE_NUMBER.e164,
            'ignorebindlimit': '0',
            'type': 'current',
        })
        counter = self.get_registration_sms_counter()
        eq_(counter.get(TEST_USER_IP), 1)

    def test_login_not_available(self):
        self.login_not_available(
            self.query_params(),
            build_headers(),
        )

    def test_frodo_call(self):
        self.frodo_call(
            self.query_params(),
            build_headers(),
            self.frodo_params(
                action='alternative_phone',
                phonenumber=TEST_PHONE_NUMBER_MASKED_FOR_FRODO,
                v2_phonenumber_hash=get_phone_number_hash(TEST_PHONE_NUMBER.e164),
            ),
            statbox_kwargs={
                'bind_secure': True,
                'mode': 'alternative_phone',
                'with_phonenumber_alias': True,
            },
        )

    def test_frodo_error(self):
        self.frodo_error(
            self.query_params(),
            build_headers(),
        )

    def test_track_content(self):
        self.track_content()

    def test_track_content_language_in_track(self):
        self.track_content_language_in_track()

    def test_with_phone_not_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = False
        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'User was not verified',
                    u'code': u'usernotverifiederror',
                }],
            },
        )

    def test_with_phone_is_confirmed(self):
        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)

        eq_(len(self.env.yasms.requests), 0)
        call_index = 3 if self.is_password_hash_from_blackbox else 2
        self.env.blackbox.requests[call_index].assert_query_contains({
            'method': 'phone_bindings',
            'numbers': TEST_PHONE_NUMBER.e164,
            'ignorebindlimit': '0',
            'type': 'current',
        })
        counter = self.get_registration_sms_counter()
        eq_(counter.get(TEST_USER_IP), 1)

    def test_db_historydb_logs_statbox_logs(self):
        timenow = TimeNow()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 6)

        self.env.db.check('aliases', 'portal', TEST_USER_LOGIN_NORMALIZED, uid=1, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.user_defined_login', TEST_USER_LOGIN, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.firstname', 'firstname', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.lastname', 'lastname', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.gender', 'm', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.birthday', '1950-12-30', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.timezone', 'Europe/Paris', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.country', 'tr', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.language', 'en', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.quality', '3:80', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.city', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'hint.question.serialized', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'hint.answer.encrypted', uid=1, db='passportdbshard1')

        assert_secure_phone_bound.check_db(
            self.env.db,
            uid=1,
            phone_attributes={
                'id': 1,
                'created': DatetimeNow(),
                'bound': DatetimeNow(),
                'confirmed': DatetimeNow(),
                'secured': DatetimeNow(),
            },
        )

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=1, db='passportdbshard1')
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('%s:' % self.password_hash_version))

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'account_register',
                'consumer': 'dev',
                'info.login': TEST_USER_LOGIN_NORMALIZED,
                'info.login_wanted': TEST_USER_LOGIN,
                'info.ena': '1',
                'info.disabled_status': '0',
                'info.firstname': 'firstname',
                'info.lastname': 'lastname',
                'info.sex': '1',
                'info.birthday': '1950-12-30',
                'info.tz': 'Europe/Paris',
                'info.country': 'tr',
                'info.mail_status': '1',
                'info.password_quality': '80',
                'info.password': eav_pass_hash,
                'info.password_update_time': timenow,
                'info.lang': 'en',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'sid.add': '8|%s,2' % TEST_USER_LOGIN,
                'mail.add': '1',
                'alias.portal.add': TEST_USER_LOGIN_NORMALIZED,
                'info.karma': '0',
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'user_agent': 'curl',
                'phone.1.action': 'created',
                'phone.1.created': TimeNow(),
                'phone.1.bound': TimeNow(),
                'phone.1.secured': TimeNow(),
                'phone.1.confirmed': TimeNow(),
                'phone.1.number': TEST_PHONE_NUMBER.e164,
                'phones.secure': '1',
                'alias.phonenumber.add': TEST_PHONE_NUMBER.international,
                'info.phonenumber_alias_search_enabled': '0',
            },
        )

        self.check_statbox(
            bind_secure=True,
            mode='alternative_phone',
            retpath=TEST_RETPATH,
            with_phonenumber_alias=True,
        )

    def test_timezone_detection(self):
        self.timezone_detection(
            central_query_count=5,
            shard_query_count=6,
        )

    def test_register__sms_counter_limit_exceeded__statbox_not_logged(self):
        counter = self.get_registration_sms_counter()
        for i in range(counter.limit - 1):
            counter.incr(TEST_USER_IP)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        ok_(counter.hit_limit(TEST_USER_IP))
        ok_('error' not in self.get_events_from_handler(self.env.statbox_handle_mock))

    def test_register__sms_counter_limit_already_exceeded__error_and_statbox_logged(self):
        """Если при альтернативной регистрации превышен лимит отправки СМС - запишем в statbox"""
        counter = self.get_registration_sms_counter()
        for i in range(counter.limit):
            counter.incr(TEST_USER_IP)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': [{
                    'field': None,
                    'message': 'Reached limit for sms per ip in registration',
                    'code': 'registrationsmssendperiplimitexceeded',
                }],
            },
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'registration_sms_per_ip_limit_has_exceeded',
                counter_current_value=str(counter.limit),
                counter_limit_value=str(counter.limit),
            ),
        ])

    def test_unsubscribe_from_maillists__known_origin__ok(self):
        rv = self.account_register_request(
            self.query_params(unsubscribe_from_maillists='True', origin=TEST_ORIGIN),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        self.env.db.check('attributes', 'account.unsubscribed_from_maillists', '1', uid=1, db='passportdbshard1')

    def test_unsubscribe_from_maillists__no_origin__ok(self):
        rv = self.account_register_request(
            self.query_params(unsubscribe_from_maillists='True'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        self.env.db.check('attributes', 'account.unsubscribed_from_maillists', 'all', uid=1, db='passportdbshard1')

    def test_unsubscribe_from_maillists__unknown_origin__ok(self):
        rv = self.account_register_request(
            self.query_params(unsubscribe_from_maillists='True', origin='foo'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        self.env.db.check('attributes', 'account.unsubscribed_from_maillists', 'all', uid=1, db='passportdbshard1')

    def test_phonenumber_alias_occupied(self):
        userinfo_response = blackbox_userinfo_response(
            **deep_merge(
                dict(
                    uid=2,
                    aliases={'portal': 'other_login'},
                ),
                build_phone_secured(
                    phone_id=2,
                    phone_number=TEST_PHONE_NUMBER.e164,
                    is_alias=True,
                ),
            )
        )
        self.env.blackbox.set_response_value('userinfo', userinfo_response)
        self.env.db.serialize(userinfo_response)

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        assert_secure_phone_bound.check_db(
            self.env.db,
            uid=1,
            phone_attributes={
                'id': 1,
                'number': TEST_PHONE_NUMBER.e164,
            },
        )
        assert_phonenumber_alias_missing(db_faker=self.env.db, uid=1)
        assert_account_has_phonenumber_alias(
            db_faker=self.env.db,
            uid=2,
            alias=TEST_PHONE_NUMBER.digital,
            enable_search=True,
        )

    def test_phonenumber_alias_occupied__allow_to_take_busy_alias(self):
        userinfo_response = blackbox_userinfo_response(
            **deep_merge(
                dict(
                    uid=2,
                    aliases={'portal': 'other_login'},
                ),
                build_phone_secured(
                    phone_id=2,
                    phone_number=TEST_PHONE_NUMBER.e164,
                    is_alias=True,
                ),
            )
        )
        self.env.blackbox.set_response_value('userinfo', userinfo_response)
        self.env.db.serialize(userinfo_response)

        rv = self.account_register_request(
            self.query_params(allow_to_take_busy_alias='1'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        assert_secure_phone_bound.check_db(
            self.env.db,
            uid=1,
            phone_attributes={
                'id': 1,
                'number': TEST_PHONE_NUMBER.e164,
            },
        )
        assert_account_has_phonenumber_alias(
            db_faker=self.env.db,
            uid=1,
            alias=TEST_PHONE_NUMBER.digital,
            enable_search=False,
        )
        assert_phonenumber_alias_missing(db_faker=self.env.db, uid=2)


@with_settings_hosts(
    **mock_counters()
)
class TestAccountRegisterAlternativeKarma(TestAccountRegisterAlternativeBase,
                                          make_clean_web_test_mixin('test_regkarma_good', ['firstname', 'lastname'], is_bundle=False),
                                          ):
    def query_params(self, exclude=None, **kwargs):
        base = {
            'validation_method': CAPTCHA_VALIDATION_METHOD,
            'hint_question_id': TEST_HINT_QUESTION_ID,
            'hint_answer': TEST_HINT_ANSWER,
        }
        kwargs = merge_dicts(base, kwargs)
        return super(TestAccountRegisterAlternativeKarma, self).query_params(exclude, **kwargs)

    def test_regkarma(self):
        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 0)

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'free'}),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.captcha_key = '1p'
            track.is_captcha_recognized = True

        self.env.frodo.set_response_value(
            u'check',
            u'<spamlist><spam_user login="%s" weight="100" /></spamlist>' % (
                TEST_USER_LOGIN_NORMALIZED,
            ),
        )
        self.env.frodo.set_response_value(u'confirm', u'')

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        assert_builder_requested(self.env.frodo, times=2)
        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 2)
        self.env.db.check('attributes', 'karma.value', '100', uid=1, db='passportdbshard1')

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '100')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '100')

        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 1)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 0)

    def test_regkarma_good(self):
        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 0)

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'free'}),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.captcha_key = '1p'
            track.is_captcha_recognized = True

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        assert_builder_requested(self.env.frodo, times=1)
        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '0')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '0')

        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 1)


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAccountRegisterAlternativeCommonNoBlackboxHash(TestAccountRegisterAlternativeCommon):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAccountRegisterAlternativeCaptchaNoBlackboxHash(TestAccountRegisterAlternativeCaptcha):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAccountRegisterAlternativePhoneNoBlackboxHash(TestAccountRegisterAlternativePhone):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAccountRegisterAlternativeKarmaNoBlackboxHash(TestAccountRegisterAlternativeKarma):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
