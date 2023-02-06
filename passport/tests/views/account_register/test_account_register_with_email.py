# -*- coding: utf-8 -*-

import json

import mock
from nose.tools import (
    eq_,
    istest,
    nottest,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.common.processes import PROCESS_WEB_REGISTRATION
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
    blackbox_hosted_domains_response,
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
)
from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.builders.frodo.utils import get_phone_number_hash
from passport.backend.core.counters import (
    registration_karma,
    sms_per_ip,
)
from passport.backend.core.eav_type_mapping import (
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING,
    EXTENDED_ATTRIBUTES_EMAIL_TYPE,
)
from passport.backend.core.frodo.exceptions import FrodoError
from passport.backend.core.models.password import PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON
from passport.backend.core.models.phones.faker import assert_secure_phone_bound
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
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import merge_dicts
from passport.backend.utils.time import get_unixtime


TEST_EMAIL_ADDRESS = 'test.testov@domain.ru'
TEST_ANOTHER_EMAIL_ADDRESS = 'another.test.testov@domain.ru'
TEST_NATIVE_EMAIL_ADDRESS = 'test.testov@yandex.ru'
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
TEST_USER_LOGIN = 'test.testov@domain.ru'
TEST_ACCEPT_LANGUAGE = 'ru'

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
    CLEAN_WEB_API_ENABLED=False,
)
@nottest
class TestAccountRegisterEmailBase(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['register_require_confirmed_email']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
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
            '/1/account/register/email/?consumer=%s' % consumer,
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
            mode='register_by_email',
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
            login=TEST_USER_LOGIN,
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
            login=TEST_USER_LOGIN,
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'registration_sms_per_ip_limit_has_exceeded',
            mode='register_by_email_with_phone',
            action='registration_with_sms',
            error='registration_sms_per_ip_limit_has_exceeded',
            ip=TEST_USER_IP,
            counter_prefix='registration:sms:ip',
            is_special_testing_ip='0',
        )

        self.env.statbox.bind_entry(
            'base_phone_entry',
            mode='register_by_email_with_phone',
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

    def check_statbox(self, has_hint=False, suid='-', bind_secure=False, **account_created_kwargs):
        entries = [
            self.env.statbox.entry('submitted'),
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
                operation='added',
                ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
                consumer='dev',
                entity='aliases',
                type='5',
                value=TEST_USER_LOGIN,
            ),
            self.env.statbox.entry(
                'account_modification',
                operation='added',
                ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
                consumer='dev',
                created_at=DatetimeNow(convert_to_datetime=True),
                entity='account.emails',
                is_unsafe='0',
                bound_at=DatetimeNow(convert_to_datetime=True),
                confirmed_at=DatetimeNow(convert_to_datetime=True),
                new=mask_email_for_statbox(TEST_EMAIL_ADDRESS),
                old='-',
                email_id='1',
                is_suitable_for_restore='1',
            ),
        ]
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
            ('password.encoding_version', {'old': '-', 'new': str(PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON)}),
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
        ]
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

    def setup_confirmed_email(self, address=TEST_EMAIL_ADDRESS):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.email_confirmation_passed_at = get_unixtime()
            track.email_confirmation_address = address

    def check_email_created(self):
        expected = [
            ('address', TEST_EMAIL_ADDRESS),
            ('created', TimeNow()),
            ('bound', TimeNow()),
            ('confirmed', TimeNow()),
        ]

        for attr, value in expected:
            self.env.db.check(
                'extended_attributes',
                'value',
                value,
                uid=1,
                type=EMAIL_NAME_MAPPING[attr],
                entity_type=EXTENDED_ATTRIBUTES_EMAIL_TYPE,
                db='passportdbshard1',
            )
        self.env.db.check(
            'email_bindings',
            'address',
            TEST_EMAIL_ADDRESS,
            uid=1,
            email_id=1,
            db='passportdbshard1',
        )

    def frodo_params(self, **kwargs):
        params = EmptyFrodoParams(**{
            'uid': '1',
            'login': TEST_USER_LOGIN,
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
        self.setup_confirmed_email()
        self.env.frodo.set_response_value(
            u'check',
            u'<spamlist><spam_user login="%s" weight="85" /></spamlist>' % (
                TEST_USER_LOGIN,
            ),
        )
        rv = self.account_register_request(
            query_params,
            headers,
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '85')

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
        self.setup_confirmed_email()

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
        eq_(track.machine_readable_login, TEST_USER_LOGIN)

        eq_(track.language, 'tr')
        eq_(track.have_password, True)
        eq_(track.is_successful_registered, True)
        eq_(track.allow_authorization, True)
        eq_(track.allow_oauth_authorization, True)

    def track_content_language_in_track(self):
        self.setup_confirmed_email()
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
        eq_(track.machine_readable_login, TEST_USER_LOGIN)

        eq_(track.language, 'en')
        eq_(track.have_password, True)
        eq_(track.is_successful_registered, True)
        eq_(track.allow_authorization, True)
        eq_(track.allow_oauth_authorization, True)

    def timezone_detection(self, central_query_count=4, shard_query_count=3):
        self.setup_confirmed_email()
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

    @parameterized.expand(['firstname', 'lastname'])
    def test_fraud(self, field):
        rv = self.account_register_request(
            self.query_params(**{field: u'Заходи дорогой, гостем будешь'}),
            build_headers(),
        )
        eq_(rv.status_code, 400)


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    **mock_counters()
)
@istest
class TestAccountRegisterEmailCommon(TestAccountRegisterEmailBase):
    def setUp(self):
        super(TestAccountRegisterEmailCommon, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION

    def query_params(self, exclude=None, **kwargs):
        base = {
            'validation_method': CAPTCHA_VALIDATION_METHOD,
            'hint_question_id': TEST_HINT_QUESTION_ID,
            'hint_answer': TEST_HINT_ANSWER,
        }
        kwargs = merge_dicts(base, kwargs)
        return super(TestAccountRegisterEmailCommon, self).query_params(exclude, **kwargs)

    def test_no_process_name(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = None
        rv = self.account_register_request(self.query_params(), build_headers())
        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': None,
                    u'code': 'track.invalid_state',
                }],
            },
        )

    def test_wrong_process_name(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION[::-1]
        rv = self.account_register_request(self.query_params(), build_headers())
        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': None,
                    u'code': 'track.invalid_state',
                }],
            },
        )

    def test_native_email(self):
        rv = self.account_register_request(self.query_params(login=TEST_NATIVE_EMAIL_ADDRESS), build_headers())
        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': 'login',
                    u'message': u'Address within Yandex native domain',
                    u'code': 'native',
                }],
            },
        )

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

    def test_domain_is_pdd(self):
        self.setup_confirmed_email()
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1),
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
                    'field': None,
                    'message': 'Domain not applicable for current operation',
                    'code': 'domaininvalidtype',
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

    def test_email_login_mismatch(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.email_confirmation_address = TEST_ANOTHER_EMAIL_ADDRESS

        rv = self.account_register_request(
            self.query_params(login=TEST_EMAIL_ADDRESS),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'Track state is invalid',
                    u'code': u'invalidtrackstate',
                }],
            },
        )

    def test_email_not_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.email_confirmation_passed_at = None
            track.email_confirmation_address = TEST_EMAIL_ADDRESS

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

    def test_invalid_track_state__no_address(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.email_confirmation_passed_at = get_unixtime()
            track.email_confirmation_address = ''

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
                    u'message': u'Track state is invalid',
                    u'code': u'invalidtrackstate',
                }],
            },
        )


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    **mock_counters()
)
@istest
class TestAccountRegisterEmailAndCaptcha(TestAccountRegisterEmailBase,
                                         make_clean_web_test_mixin('test_db_historydb_logs_statbox_logs', ['firstname', 'lastname'], is_bundle=False),
                                         ):
    def setUp(self):
        super(TestAccountRegisterEmailAndCaptcha, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION
            track.is_captcha_recognized = True

    def query_params(self, exclude=None, **kwargs):
        base = {
            'validation_method': CAPTCHA_VALIDATION_METHOD,
            'hint_question_id': TEST_HINT_QUESTION_ID,
            'hint_answer': TEST_HINT_ANSWER,
        }
        kwargs = merge_dicts(base, kwargs)
        return super(TestAccountRegisterEmailAndCaptcha, self).query_params(exclude, **kwargs)

    def test_eula_not_accepted(self):
        self.setup_confirmed_email()
        self.eula_not_accepted(
            self.query_params(eula_accepted='0'),
            build_headers(),
        )

    def test_invalid_password_error(self):
        self.setup_confirmed_email()
        self.invalid_password_error(
            self.query_params(),
            build_headers(),
        )

    def test_login_not_available(self):
        self.setup_confirmed_email()
        self.login_not_available(
            self.query_params(),
            build_headers(),
        )

    def test_frodo_call(self):
        self.setup_confirmed_email()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.captcha_generate_count.incr()
            track.captcha_key = '1p'
        self.frodo_call(
            self.query_params(),
            build_headers(),
            self.frodo_params(
                action='register_by_email_with_hint',
                hintqid='1',
                hintaex='2.4.0.0.0',
                hinta='6.0.6.0.0.0',
                captchacount='1',
            ),
            statbox_kwargs={
                'captcha_generation_number': '1',
                'mode': 'register_by_email_with_hint',
                'has_hint': True,
                'question_id': '1',
                'is_voice_generated': '0',
                'captcha_key': '1p',
            },
        )

    def test_frodo_error(self):
        self.setup_confirmed_email()
        self.frodo_error(
            self.query_params(),
            build_headers(),
        )

    def test_track_content(self):
        self.track_content()

    def test_track_content_language_in_track(self):
        self.track_content_language_in_track()

    def test_with_captcha_not_passed(self):
        self.setup_confirmed_email()
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
        self.setup_confirmed_email()
        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)
        eq_(len(self.env.yasms.requests), 0)

    def test_db_historydb_logs_statbox_logs(self):
        self.setup_confirmed_email()
        timenow = TimeNow()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.captcha_generate_count.incr()
            track.captcha_key = '1p'

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 3)
        eq_(self.env.db.query_count('passportdbshard1'), 3)

        self.env.db.check('aliases', 'lite', TEST_USER_LOGIN, uid=1, db='passportdbcentral')
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.city', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')
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

        self.check_email_created()

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=1, db='passportdbshard1')
        eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'account_register',
                'consumer': 'dev',
                'email.1.address': TEST_EMAIL_ADDRESS,
                'email.1': 'created',
                'email.1.bound_at': TimeNow(),
                'email.1.confirmed_at': TimeNow(),
                'email.1.created_at': TimeNow(),
                'email.1.is_unsafe': '0',
                'info.login': TEST_USER_LOGIN,
                'info.ena': '1',
                'info.disabled_status': '0',
                'info.firstname': 'firstname',
                'info.lastname': 'lastname',
                'info.sex': '1',
                'info.birthday': '1950-12-30',
                'info.tz': 'Europe/Paris',
                'info.country': 'tr',
                'info.password_quality': '80',
                'info.password': eav_pass_hash,
                'info.password_update_time': timenow,
                'info.lang': 'en',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'info.hintq': TEST_HINT_QUESTION,
                'info.hinta': 'answer',
                'sid.add': '8|%s' % TEST_USER_LOGIN,
                'alias.lite.add': TEST_USER_LOGIN,
                'info.karma': '0',
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'user_agent': 'curl',
            },
        )

        self.check_statbox(
            mode='register_by_email_with_hint',
            has_hint=True,
            captcha_generation_number='1',
            question_id='1',
            is_voice_generated='0',
            captcha_key='1p',
        )

    def test_timezone_detection(self):
        self.timezone_detection(central_query_count=3)

    def test_hint_question(self):
        self.setup_confirmed_email()
        rv = self.account_register_request(
            self.query_params(
                hint_question='Custom question',
                exclude=['hint_question_id'],
            ),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        self.check_email_created()

        self.env.db.check('attributes', 'hint.question.serialized', '99:Custom question', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'hint.answer.encrypted', TEST_HINT_ANSWER, uid=1, db='passportdbshard1')
        self.check_statbox(
            mode='register_by_email_with_hint',
            has_hint=True,
            question_id='99',
            captcha_generation_number='0',
            is_voice_generated='0',
        )

    def test_statbox_logs_with_voice_captcha(self):
        self.setup_confirmed_email()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = True
            track.voice_captcha_type = 'rus'
            track.captcha_key = '1p'

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        self.check_email_created()
        self.check_statbox(
            mode='register_by_email_with_hint',
            has_hint=True,
            question_id='1',
            captcha_generation_number='0',
            is_voice_generated='1',
            captcha_key='1p',
        )

    def test_captcha_registration__captcha_ok__sms_counter_not_incremented(self):
        """При регистрации с капчей, не увеличивается счетчик регистраций через sms"""
        self.setup_confirmed_email()
        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        self.check_email_created()

        sms_registation_counter = sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP)
        eq_(sms_registation_counter.get(TEST_USER_IP), 0)


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    **mock_counters()
)
@istest
class TestAccountRegisterEmailAndPhone(TestAccountRegisterEmailBase,
                                       make_clean_web_test_mixin('test_db_historydb_logs_statbox_logs', ['firstname', 'lastname'], statbox_action='phone_confirmed', is_bundle=False),
                                       ):
    def setUp(self):
        super(TestAccountRegisterEmailAndPhone, self).setUp()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

    def query_params(self, exclude=None, **kwargs):
        base = {
            'validation_method': PHONE_VALIDATION_METHOD,
        }
        kwargs = merge_dicts(base, kwargs)
        return super(TestAccountRegisterEmailAndPhone, self).query_params(exclude, **kwargs)

    def test_eula_not_accepted(self):
        self.setup_confirmed_email()
        self.eula_not_accepted(
            self.query_params(eula_accepted='0'),
            build_headers(),
        )

    def test_invalid_password_error(self):
        self.setup_confirmed_email()
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

    def test_login_not_available(self):
        self.login_not_available(
            self.query_params(),
            build_headers(),
        )

    def test_frodo_call(self):
        self.setup_confirmed_email()
        self.frodo_call(
            self.query_params(),
            build_headers(),
            self.frodo_params(
                action='register_by_email_with_phone',
                phonenumber=TEST_PHONE_NUMBER_MASKED_FOR_FRODO,
                v2_phonenumber_hash=get_phone_number_hash(TEST_PHONE_NUMBER.e164),
            ),
            statbox_kwargs={
                'bind_secure': True,
                'mode': 'register_by_email_with_phone',
            },
        )

    def test_frodo_error(self):
        self.setup_confirmed_email()
        self.frodo_error(
            self.query_params(),
            build_headers(),
        )

    def test_track_content(self):
        self.track_content()

    def test_track_content_language_in_track(self):
        self.track_content_language_in_track()

    def test_with_phone_not_confirmed(self):
        self.setup_confirmed_email()
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
        self.setup_confirmed_email()
        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)
        self.check_email_created()

        eq_(len(self.env.yasms.requests), 0)
        self.env.blackbox.requests[3].assert_query_contains({
            'method': 'phone_bindings',
            'numbers': TEST_PHONE_NUMBER.e164,
            'ignorebindlimit': '0',
            'type': 'current',
        })
        counter = self.get_registration_sms_counter()
        eq_(counter.get(TEST_USER_IP), 1)

    def test_db_historydb_logs_statbox_logs(self):
        self.setup_confirmed_email()
        timenow = TimeNow()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 7)

        self.env.db.check('aliases', 'lite', TEST_USER_LOGIN, uid=1, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')
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

        self.check_email_created()

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
        eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'account_register',
                'consumer': 'dev',
                'email.1.address': TEST_EMAIL_ADDRESS,
                'email.1': 'created',
                'email.1.bound_at': TimeNow(),
                'email.1.confirmed_at': TimeNow(),
                'email.1.created_at': TimeNow(),
                'email.1.is_unsafe': '0',
                'info.login': TEST_USER_LOGIN,
                'info.ena': '1',
                'info.disabled_status': '0',
                'info.firstname': 'firstname',
                'info.lastname': 'lastname',
                'info.sex': '1',
                'info.birthday': '1950-12-30',
                'info.tz': 'Europe/Paris',
                'info.country': 'tr',
                'info.password_quality': '80',
                'info.password': eav_pass_hash,
                'info.password_update_time': timenow,
                'info.lang': 'en',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'sid.add': '8|%s' % TEST_USER_LOGIN,
                'alias.lite.add': TEST_USER_LOGIN,
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
            },
        )

        self.check_statbox(
            bind_secure=True,
            mode='register_by_email_with_phone',
            retpath=TEST_RETPATH,
        )

    def test_timezone_detection(self):
        self.timezone_detection(
            central_query_count=4,
            shard_query_count=7,
        )

    def test_register__sms_counter_limit_exceeded__statbox_not_logged(self):
        self.setup_confirmed_email()

        counter = self.get_registration_sms_counter()
        for i in range(counter.limit - 1):
            counter.incr(TEST_USER_IP)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        self.check_email_created()

        ok_(counter.hit_limit(TEST_USER_IP))
        ok_('error' not in self.get_events_from_handler(self.env.statbox_handle_mock))

    def test_register__sms_counter_limit_already_exceeded__error_and_statbox_logged(self):
        """Если при альтернативной регистрации превышен лимит отправки СМС - запишем в statbox"""
        self.setup_confirmed_email()
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


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    **mock_counters()
)
@istest
class TestAccountRegisterEmailKarma(TestAccountRegisterEmailBase,
                                    make_clean_web_test_mixin('test_regkarma_good', ['firstname', 'lastname'], is_bundle=False),
                                    ):
    def setUp(self):
        super(TestAccountRegisterEmailKarma, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION

    def query_params(self, exclude=None, **kwargs):
        base = {
            'validation_method': CAPTCHA_VALIDATION_METHOD,
            'hint_question_id': TEST_HINT_QUESTION_ID,
            'hint_answer': TEST_HINT_ANSWER,
        }
        kwargs = merge_dicts(base, kwargs)
        return super(TestAccountRegisterEmailKarma, self).query_params(exclude, **kwargs)

    def test_regkarma(self):
        self.setup_confirmed_email()

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
                TEST_USER_LOGIN,
            ),
        )
        self.env.frodo.set_response_value(u'confirm', u'')

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        assert_builder_requested(self.env.frodo, times=2)
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        self.check_email_created()

        eq_(self.env.db.query_count('passportdbcentral'), 3)
        eq_(self.env.db.query_count('passportdbshard1'), 4)
        self.env.db.check('attributes', 'karma.value', '100', uid=1, db='passportdbshard1')

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '100')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '100')

        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 1)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 0)

    def test_regkarma_good(self):
        self.setup_confirmed_email()

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
        self.check_email_created()

        eq_(self.env.db.query_count('passportdbcentral'), 3)
        eq_(self.env.db.query_count('passportdbshard1'), 3)
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '0')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '0')

        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 1)
