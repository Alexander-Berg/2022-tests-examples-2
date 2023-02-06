# -*- coding: utf-8 -*-
from datetime import timedelta
import json

import mock
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.common.common import check_spammer
from passport.backend.api.test.mixins import make_clean_web_test_mixin
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_createsession_response,
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.oauth import OAuthTemporaryError
from passport.backend.core.counters import sms_per_ip
from passport.backend.core.frodo.exceptions import FrodoError
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
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
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import (
    merge_dicts,
    remove_none_values,
)
import pytz


TEST_HOST = 'yandex.ru'
TEST_USER_IP = '37.9.101.188'
TEST_USER_AGENT = 'curl'
TEST_RETPATH = 'http://ya.ru'
TEST_ACCESS_TOKEN = 'a68d97976a66444496148b694802b009'
TEST_USER_LOGIN = 'test.test'
TEST_USER_LOGIN_NORMALIZED = 'test-test'
TEST_OPERATION_TTL = timedelta(seconds=60)

TEST_NATIVE_EMAIL_DOMAINS = ('yandex.ru', 'yandex.ua', 'yandex.by', 'yandex.kz', 'yandex.com', 'narod.ru', 'ya.ru')

TEST_PHONE_NUMBER = PhoneNumber.parse('+79991234567')

SUCCESSFUL_REGISTRATION_RESPONSE = {
    'status': 'ok',
    'access_token': TEST_ACCESS_TOKEN,
}


def build_headers(user_ip=None):
    return mock_headers(
        user_ip=user_ip or TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        x_forwarded_for=True,
        host='',
    )


class StatboxTestMixin(object):
    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='uncompleted',
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
            _exclude=['consumer', 'password_quality', 'ip'],
            country='tr',
            track_id=self.track_id,
            captcha_key='1p',
            login=TEST_USER_LOGIN_NORMALIZED,
            is_voice_generated='0',
        )
        self.env.statbox.bind_entry(
            'registration_sms_per_ip_limit_has_exceeded',
            mode='uncompleted',
            action='registration_with_sms',
            error='registration_sms_per_ip_limit_has_exceeded',
            ip=TEST_USER_IP,
            counter_prefix='registration:sms:ip',
            is_special_testing_ip='0',
        )

        self.env.statbox.bind_entry(
            'base_phone_entry',
            mode='uncompleted',
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            login=TEST_USER_LOGIN_NORMALIZED,
        )
        self.env.statbox.bind_entry(
            'local_secure_bind_operation_created',
            _exclude=['mode', 'login', 'track_id'],
            _inherit_from=['secure_bind_operation_created', 'base_phone_entry'],
            ip=TEST_USER_IP,
        )
        self.env.statbox.bind_entry(
            'local_phone_confirmed',
            _exclude=['consumer', 'ip', 'user_agent'],
            _inherit_from=['phone_confirmed', 'base_phone_entry'],
            phone_id='1',
            confirmation_time=DatetimeNow(convert_to_datetime=True),
            code_checks_count='0',
        )
        self.env.statbox.bind_entry(
            'local_secure_phone_bound',
            _exclude=['consumer', 'ip', 'user_agent'],
            _inherit_from=['secure_phone_bound', 'base_phone_entry'],
            phone_id='1',
        )
        self.env.statbox.bind_entry(
            'uncompleted_set_password',
            action='uncompleted_set_password',
            login=TEST_USER_LOGIN_NORMALIZED,
            uid='1',
            password_quality='80',
        )


@with_settings_hosts(
    SOCIAL_LOGIN_GENERATION_RETRIES=5,
    YASMS_URL='http://localhost/',
    OAUTH_URL='http://localhost/',
    CLEAN_WEB_API_ENABLED=False,
)
class TestAccountRegisterUncompleted(BaseTestViews,
                                     make_clean_web_test_mixin('test_db_historydb_logs_statbox_logs', ['firstname', 'lastname'], is_bundle=False),
                                     StatboxTestMixin):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['register_uncompleted']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_ACCESS_TOKEN,
                'token_type': 'bearer',
            },
        )

        self.is_required_captcha_mock = mock.Mock(return_value=False)
        self.is_required_captcha_patch = mock.patch(
            'passport.backend.core.counters.uncompleted_registration_captcha.is_required',
            self.is_required_captcha_mock,
        )
        self.is_required_captcha_patch.start()
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        self.is_required_captcha_patch.stop()
        del self.env
        del self.track_manager
        del self.is_required_captcha_mock
        del self.is_required_captcha_patch

    def make_request(self, data, headers):
        return self.env.client.post(
            '/1/account/register/uncompleted/?consumer=dev',
            data=data,
            headers=headers,
        )

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'track_id': self.track_id,
            'login': TEST_USER_LOGIN,
            'firstname': 'firstname',
            'lastname': 'lastname',
            'country': 'tr',
            'language': 'en',
            'gender': 'm',
            'birthday': '1950-01-30',
            'timezone': 'Europe/Paris',
        }
        if exclude:
            for key in exclude:
                del base_params[key]
        return merge_dicts(base_params, kwargs)

    def check_statbox(self, **account_created_kwargs):
        names_values = [
            ('person.firstname', {'old': '-', 'new': 'firstname'}),
            ('person.lastname', {'old': '-', 'new': 'lastname'}),
            ('person.language', {'old': '-', 'new': 'en'}),
            ('person.country', {'old': '-', 'new': 'tr'}),
            ('person.gender', {'old': '-', 'new': 'm'}),
            ('person.birthday', {'old': '-', 'new': '1950-01-30'}),
            ('person.fullname', {'old': '-', 'new': 'firstname lastname'}),
        ]

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
        ] + [
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
            ),
            self.env.statbox.entry('subscriptions', sid='8'),
        ]

        entries.append(
            self.env.statbox.entry('account_created', **account_created_kwargs),
        )
        self.env.statbox.assert_has_written(entries)

    @parameterized.expand(['firstname', 'lastname'])
    def test_fraud(self, field):
        rv = self.make_request(
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

    def test_without_need_headers(self):
        rv = self.make_request(self.query_params(), {})

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

    def test_login_not_available(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'occupied'}),
        )

        rv = self.make_request(
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

    def test_captcha_required_and_passed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = True
        self.is_required_captcha_mock.return_value = True

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        eq_(self.is_required_captcha_mock.call_args[0][0], TEST_USER_IP)
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {u'status': u'ok', u'access_token': TEST_ACCESS_TOKEN},
        )

    def test_captcha_required_and_not_passed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False
        self.is_required_captcha_mock.return_value = True

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        eq_(self.is_required_captcha_mock.call_args[0][0], TEST_USER_IP)
        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), {u'status': u'error',
                                  u'errors': [{u'field': None,
                                               u'message': u'User was not verified',
                                               u'code': u'usernotverifiederror'}]})

    def test_registration_already_completed_error(self):
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None, u'message': u'Repeated usage of the same track for registration',
                          u'code': u'registrationalreadycompletederror'}]},
        )

    def test_db_historydb_logs_statbox_logs(self):
        timenow = TimeNow()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = True
            track.captcha_key = '1p'
            track.retpath = TEST_RETPATH

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check('aliases', 'portal', TEST_USER_LOGIN_NORMALIZED, uid=1, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.user_defined_login', TEST_USER_LOGIN, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.firstname', 'firstname', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.lastname', 'lastname', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.gender', 'm', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.birthday', '1950-01-30', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.timezone', 'Europe/Paris', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.country', 'tr', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.language', 'en', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.city', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'password.quality', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'password.encrypted', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'password.update_datetime', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'hint.question.serialized', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'hint.answer.encrypted', uid=1, db='passportdbshard1')

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
                'info.birthday': '1950-01-30',
                'info.tz': 'Europe/Paris',
                'info.country': 'tr',
                'info.lang': 'en',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'sid.add': '8|%s' % TEST_USER_LOGIN,
                'alias.portal.add': TEST_USER_LOGIN_NORMALIZED,
                'info.karma': '0',
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'user_agent': 'curl',
            },
        )

        # Проверка отсутствия записи в auth.log
        self.check_auth_log_entries(self.env.auth_handle_mock, [])

        self.check_statbox(captcha_key='1p', retpath=TEST_RETPATH)

    def test_timezone_detection(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = True
            track.captcha_key = '1p'
            track.retpath = TEST_RETPATH

        rv = self.make_request(
            self.query_params(exclude=['timezone']),
            build_headers(user_ip='8.8.8.8'),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'person.timezone', 'America/New_York', uid=1, db='passportdbshard1')

    def test_track_content(self):
        rv = self.make_request(
            self.query_params(language='tr'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)

        track = self.track_manager.read(self.track_id)
        eq_(track.uid, '1')
        eq_(track.login, TEST_USER_LOGIN)
        eq_(track.language, 'tr')
        eq_(track.have_password, False)
        eq_(track.is_successful_registered, True)
        eq_(track.allow_authorization, False)
        ok_(not track.allow_oauth_authorization)

    def test_content_language_in_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.language = 'en'

        rv = self.make_request(
            self.query_params(language='tr'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), SUCCESSFUL_REGISTRATION_RESPONSE)

        track = self.track_manager.read(self.track_id)
        eq_(track.uid, '1')
        eq_(track.login, TEST_USER_LOGIN)
        eq_(track.language, 'tr')
        ok_(not track.have_password)
        ok_(track.is_successful_registered)

    def test_oauth_missing_token(self):
        self.env.oauth.set_response_value(
            '_token',
            {
                'error': 'code',
                'message': 'message',
            },
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 503, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), {u'status': u'error',
                                  u'errors': [{u'field': None,
                                               u'message': u'OAuth token not found in OAuth response',
                                               u'code': u'oauthtokennotfound'}]})

    def test_oauth_error(self):
        self.env.oauth.set_response_side_effect(
            '_token',
            OAuthTemporaryError('Failed'),
        )
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 503, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), {u'status': u'error',
                                  u'errors': [{u'field': None,
                                               u'message': u'OAuth failed',
                                               u'code': u'oauthfailed'}]})

    def test_statbox_logs_with_voice_captcha(self):
        self.is_required_captcha_mock.return_value = True

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.voice_captcha_type = 'rus'
            track.captcha_key = '1p'
            track.is_captcha_recognized = True

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        self.check_statbox(is_voice_generated='1')


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=3,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    NATIVE_EMAIL_DOMAINS=TEST_NATIVE_EMAIL_DOMAINS,
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    **mock_counters()
)
class UncompletedSetPasswordTestCase(BaseTestViews, StatboxTestMixin):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['uncompleted_set_password'],
        }))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(
            track_type_to_create='complete',
        )

        blackbox_response = blackbox_userinfo_response(
            uid='1',
            login=TEST_USER_LOGIN_NORMALIZED,
            dbfields={
                'userinfo.reg_date.uid': '2013-08-01 18:00:00',
            },
            attributes={
                'person.firstname': 'firstname',
                'person.lastname': 'lastname',
                'person.country': 'TR',
                'person.language': 'en',
            },
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

        self.expected_password = 'aaa1bbbccc'
        self.env.db.serialize(blackbox_response)
        self.phone_number = '+79991234567'

        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def historydb_entry(self, uid=None, name=None, value=None):
        entry = {
            'uid': uid,
            'name': name,
            'value': value,
        }
        return remove_none_values(entry)

    def make_request(self, headers=None, **kwargs):
        data = {
            'track_id': self.track_id,
            'password': self.expected_password,
            'eula_accepted': True,
        }
        data.update(kwargs)
        headers = build_headers() if headers is None else headers
        return self.env.client.post(
            '/1/account/register/uncompleted/setpassword/?consumer=dev',
            data=data,
            headers=headers,
        )

    def get_registration_sms_counter(self):
        return sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP)

    def check_ok(self, uid, response):
        timenow = TimeNow()
        eq_(response.status_code, 200)
        eq_(json.loads(response.data), {'status': 'ok'})

        eq_(self.env.db.query_count('passportdbcentral'), 3)
        eq_(self.env.db.query_count('passportdbshard1'), 9)
        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=uid, db='passportdbshard1')
        self.env.db.check('attributes', 'password.quality', '3:80', uid=uid, db='passportdbshard1')
        self.env.db.check('attributes', 'karma.value', '6000', uid=uid, db='passportdbshard1')
        assert_secure_phone_bound.check_db(
            self.env.db,
            uid=uid,
            phone_attributes={
                'id': 1,
                'created': DatetimeNow(),
                'bound': DatetimeNow(),
                'confirmed': DatetimeNow(),
                'secured': DatetimeNow(),
            },
        )

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=uid, db='passportdbshard1')
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('%s:' % self.password_hash_version))

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            [
                # Создание телефона на аккаунте
                self.historydb_entry(name='phone.1.action', value='created'),
                self.historydb_entry(name='phone.1.created', value=timenow),
                self.historydb_entry(name='phone.1.number', value=self.phone_number),
                self.historydb_entry(name='phone.1.operation.1.action', value='created'),
                self.historydb_entry(name='phone.1.operation.1.finished', value=TimeNow(offset=TEST_OPERATION_TTL.total_seconds())),
                self.historydb_entry(name='phone.1.operation.1.security_identity', value='1'),
                self.historydb_entry(name='phone.1.operation.1.started', value=timenow),
                self.historydb_entry(name='phone.1.operation.1.type', value='bind'),
                self.historydb_entry(name='action', value='acquire_phone'),
                self.historydb_entry(name='consumer', value='dev'),
                self.historydb_entry(name='user_agent', value='curl'),
                self.historydb_entry(name='info.mail_status', value='1'),
                # Установка пароля
                self.historydb_entry(name='info.password', value=eav_pass_hash),
                self.historydb_entry(name='info.password_quality', value='80'),
                self.historydb_entry(name='info.password_update_time', value=timenow),
                self.historydb_entry(name='info.karma_prefix', value='6'),
                self.historydb_entry(name='info.karma_full', value='6000'),
                self.historydb_entry(name='mail.add', value='1'),
                self.historydb_entry(name='sid.add', value='2'),

                self.historydb_entry(name='phone.1.action', value='changed'),
                self.historydb_entry(name='phone.1.bound', value=timenow),
                self.historydb_entry(name='phone.1.confirmed', value=timenow),
                self.historydb_entry(name='phone.1.number', value=self.phone_number),
                self.historydb_entry(name='phone.1.operation.1.action', value='deleted'),
                self.historydb_entry(name='phone.1.operation.1.security_identity', value='1'),
                self.historydb_entry(name='phone.1.operation.1.type', value='bind'),
                self.historydb_entry(name='phone.1.secured', value=timenow),
                self.historydb_entry(name='phones.secure', value='1'),
                self.historydb_entry(name='action', value='change_password'),
                self.historydb_entry(name='consumer', value='dev'),
                self.historydb_entry(name='user_agent', value='curl'),
            ],
        )

        self.check_statbox()

        # Blackbox
        requests = self.env.blackbox.requests
        requests_count = 5 if self.is_password_hash_from_blackbox else 4
        eq_(len(requests), requests_count)
        requests[0].assert_post_data_contains({
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })
        requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })
        requests[1].assert_query_contains({
            'method': 'phone_bindings',
            'numbers': self.phone_number,
            'type': 'history',
            'ignorebindlimit': '0',
        })
        phone_bindings_call_index = 3 if self.is_password_hash_from_blackbox else 2
        requests[phone_bindings_call_index].assert_query_contains({
            'method': 'phone_bindings',
            'numbers': self.phone_number,
            'type': 'current',
            'ignorebindlimit': '0',
        })

        track = self.track_manager.read(self.track_id)
        ok_(track.is_successful_completed)
        ok_(track.allow_authorization)
        ok_(track.allow_oauth_authorization)

        counter = self.get_registration_sms_counter()
        eq_(counter.get(TEST_USER_IP), 1)

    def check_statbox(self, karma_value=None):
        names_values = [
            ('password.encrypted', {}),
            ('password.encoding_version', {'old': '-', 'new': str(self.password_hash_version)}),
            ('password.quality', {'old': '-', 'new': '80'}),
        ]

        entries = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('local_secure_bind_operation_created'),
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
                entity='phones.secure',
                old='-',
                new=TEST_PHONE_NUMBER.masked_format_for_statbox,
                old_entity_id='-',
                new_entity_id='1',
            ),
        ] + [
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
                'account_modification',
                action='change_password',
                event='account_modification',
                entity='karma',
                old='0',
                suid='1',
                uid='1',
                destination='frodo',
                new='6000',
                login=TEST_USER_LOGIN_NORMALIZED,
                registration_datetime='2013-08-01 18:00:00',
                consumer='dev',
                ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
            ),
            self.env.statbox.entry('subscriptions', sid='2', suid='1'),
            self.env.statbox.entry('uncompleted_set_password'),
            self.env.statbox.entry('local_phone_confirmed'),
            self.env.statbox.entry('local_secure_phone_bound'),
        ]

        if karma_value and karma_value != '0':
            entries.append(
                self.env.statbox.entry(
                    'frodo_karma',
                    action='uncompleted_set_password',
                    old='6000',
                    new=karma_value,
                    registration_datetime='2013-08-01 18:00:00',
                    suid='1',
                ),
            )

        self.env.statbox.assert_has_written(entries)

    def frodo_params(self, **kwargs):
        base_params = {
            'login': TEST_USER_LOGIN_NORMALIZED,
            'iname': 'firstname',
            'fname': 'lastname',
            'email': '',
            'from': '',
            'passwd': '10.0.9.1',
            'passwdex': '3.6.0.0',
            'hintqid': '',
            'hintq': '0.0.0.0.0.0',
            'hintqex': '0.0.0.0.0.0',
            'hinta': '0.0.0.0.0.0',
            'hintaex': '0.0.0.0.0.0',
            'phonenumber': '79990004567',
            'yandexuid': '',
            'fuid': '',
            'useragent': 'curl',
            'host': '',
            'social_provider': '',
            'ip_from': TEST_USER_IP,
            'valkey': '0000000000',
            'lcheck': '',
            'captchacount': '',
            'step1time': '2000',
            'step2time': '2000',
            'action': 'uncompleted_set_password',
            'lang': 'en',
            'xcountry': 'TR',
            'v2_phone_confirmation_first_sms_send_at': '',
            'v2_phone_confirmation_first_code_checked': '',
            'v2_phone_validation_changes': '',
            'v2_phone_validation_error': '',
            'v2_phone_confirmation_sms_count': '',
            'v2_phone_confirmation_confirms_count': '',
            'v2_account_karma': '',
            'is_suggested_login': '',
        }
        return merge_dicts(base_params, kwargs)

    def test_eula_not_accepted(self):
        rv = self.make_request(eula_accepted=False)

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

        counter = self.get_registration_sms_counter()
        eq_(counter.get(TEST_USER_IP), 0)

    def test_invalid_password_error(self):
        invalid_password_args = [
            (
                '.',
                [{
                    u'field': u'password',
                    u'code': u'tooshort',
                    u'message': u'Password has less 6 symbols',
                }],
            ),
        ]

        for password, expected_errors in invalid_password_args:
            rv = self.make_request(password=password)

            eq_(rv.status_code, 400, [rv.status_code, rv.data])
            eq_(
                json.loads(rv.data),
                {
                    u'status': u'error',
                    u'errors': expected_errors,
                },
            )

    def test_without_need_headers(self):
        rv = self.make_request({})

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

    def test_set_password_invalid_track_type(self):
        _, track_id = self.env.track_manager.get_manager_and_trackid(
            track_type_to_create='register',
        )
        rv = self.make_request(track_id=track_id)
        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'Track type is invalid',
                    u'code': u'invalidtracktype',
                }],
            },
        )

    def test_set_password_already_completed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 1
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number
            track.is_successful_completed = True

        rv = self.make_request()
        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'Account is a portal account already',
                    u'code': u'accountalreadycompletederror',
                }],
            },
        )

    def test_set_password_track_no_uid(self):
        rv = self.make_request()
        eq_(rv.status_code, 400)
        errors = [{
            u'field': None,
            u'message': u'Track state is invalid',
            u'code': u'invalidtrackstate',
        }]
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': errors,
            },
        )

    def test_set_password_phone_not_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 123
        rv = self.make_request()
        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'Phone is not confirmed',
                    u'code': u'phonenotconfirmed',
                }],
            },
        )

    def test_set_password_track_phone_confirmation_phone_number_missing(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 123
            track.phone_confirmation_is_confirmed = True

        rv = self.make_request()
        eq_(rv.status_code, 400)
        errors = [{
            u'field': None,
            u'message': u'Track state is invalid',
            u'code': u'invalidtrackstate',
        }]
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': errors,
            },
        )

    def test_ok(self):
        uid = 1
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number

        rv = self.make_request()
        self.check_ok(uid, rv)

    def test_frodo_call(self):
        uid = 1
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number

        self.env.frodo.set_response_value(
            u'check',
            u'<spamlist><spam_user login="%s" weight="85" /></spamlist>' % (
                TEST_USER_LOGIN_NORMALIZED,
            ),
        )
        self.env.frodo.set_response_value(u'confirm', u'')

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok'})

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '85')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '85')

        eq_(self.env.db.query_count('passportdbcentral'), 3)
        eq_(self.env.db.query_count('passportdbshard1'), 10)
        self.env.db.check('attributes', 'karma.value', '85', uid=uid, db='passportdbshard1')

        # Проверяем параметры для frodo
        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_contains(self.frodo_params())

        # Проверяем, что записали карму в tskv-лог для фродо
        self.check_statbox(karma_value='85')

    def test_frodo_info_args(self):
        uid = 1
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.login = TEST_USER_LOGIN_NORMALIZED
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number

        with mock.patch('passport.backend.api.views.register.check_spammer') as check_spammer_mock:
            check_spammer_mock.side_effect = lambda *args: check_spammer(*args)
            rv = self.make_request()

            self.check_ok(uid, rv)

            eq_(check_spammer_mock.call_count, 1)
            # Третий аргумент - frodo_args
            eq_(
                check_spammer_mock.call_args[0][2],
                {
                    'phone_number': PhoneNumber.parse('+7 999 123-45-67'),
                    'phone_bindings_count': '0',
                    'firstname': u'firstname',
                    'lastname': u'lastname',
                    'language': u'en',
                    'country': u'TR',
                    'account_country': u'TR',
                    'account_language': u'en',
                    'account_timezone': pytz.timezone('Europe/Moscow'),
                    'eula_accepted': True,
                    'quality': 80,
                    'track_id': self.track_id,
                    'action': 'uncompleted_set_password',
                    'login': TEST_USER_LOGIN_NORMALIZED,
                    'password': u'aaa1bbbccc',
                    'consumer': u'dev',
                    'emails': {
                        u'test-test@yandex.ua',
                        u'test-test@yandex.kz',
                        u'test-test@yandex.com',
                        u'test-test@yandex.ru',
                        u'test-test@ya.ru',
                        u'test-test@narod.ru',
                        u'test-test@yandex.by',
                    },
                    'uid': 1,
                },
            )
            requests = self.env.frodo.requests
            eq_(len(requests), 1)

            self.env.db.check('attributes', 'karma.value', '6000', uid=uid, db='passportdbshard1')

    def test_frodo_error(self):
        uid = 1
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number

        self.env.frodo.set_response_side_effect(u'check', FrodoError(u'Failed'))

        rv = self.make_request()
        self.check_ok(uid, rv)

        requests = self.env.frodo.requests
        eq_(len(requests), 1)

        self.env.db.check('attributes', 'karma.value', '6000', uid=uid, db='passportdbshard1')

    def test_uncompleted_set_passwd__sms_per_ip_limit_exceeded__statbox_not_logged(self):
        uid = 1
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number

        counter = self.get_registration_sms_counter()
        for i in range(counter.limit - 1):
            counter.incr(TEST_USER_IP)

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok'})
        ok_(counter.hit_limit(TEST_USER_IP))
        ok_('error' not in self.get_events_from_handler(self.env.statbox_handle_mock))

    def test_uncompleted_set_passwd__sms_per_ip_limit_already_exceeded__error_and_statbox_logged(self):
        uid = 1
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number

        counter = self.get_registration_sms_counter()
        for i in range(counter.limit):
            counter.incr(TEST_USER_IP)

        rv = self.make_request()

        eq_(rv.status_code, 400)
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
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class UncompletedSetPasswordTestCaseNoBlackboxHash(UncompletedSetPasswordTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
