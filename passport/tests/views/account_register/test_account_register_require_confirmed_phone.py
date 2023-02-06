# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    istest,
    nottest,
    ok_,
)
from nose_parameterized import parameterized
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
)
from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.builders.frodo.utils import get_phone_number_hash
from passport.backend.core.counters import (
    sms_per_ip,
    sms_per_phone,
)
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
from passport.backend.utils.common import merge_dicts


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
TEST_ACCEPT_LANGUAGE = 'ru'

TEST_PHONE_NUMBER = PhoneNumber.parse('+79999999999')
TEST_PHONE_NUMBER_MASKED_FOR_FRODO = '79990009999'

TEST_USER_LOGIN = 'test.login'
TEST_USER_LOGIN_NORMALIZED = 'test-login'


def build_headers(host=None):
    return mock_headers(
        host=host or TEST_HOST,
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        x_forwarded_for=True,
        cookie=TEST_USER_COOKIES,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    CLEAN_WEB_API_ENABLED=False,
)
@nottest
class TestAccountRegisterRequireConfirmedPhoneBase(BaseTestViews):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['register_require_confirmed_phone']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'free'}),
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

        self.setup_statbox_templates()

        self.patches = []

    def tearDown(self):
        self.env.stop()
        for p in self.patches:
            p.stop()
        del self.env
        del self.track_manager
        del self.patches

    def account_register_request(self, data, headers):
        return self.env.client.post(
            '/1/account/register/phone/?consumer=dev',
            data=data,
            headers=headers,
        )

    def query_params(self, **kwargs):
        base_params = {
            'track_id': self.track_id,
            'login': TEST_USER_LOGIN,
            'password': 'aaa1bbbccc',
            'firstname': 'firstname',
            'lastname': 'lastname',
            'country': 'ru',
            'language': 'ru',
            'display_language': 'ru',
            'mode': 'phonereg',
            'eula_accepted': 'True',
        }
        return merge_dicts(base_params, kwargs)

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='phonereg',
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
            country='ru',
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'registration_sms_per_ip_limit_has_exceeded',
            mode='phonereg',
            action='registration_with_sms',
            error='registration_sms_per_ip_limit_has_exceeded',
            ip=TEST_USER_IP,
            counter_prefix='registration:sms:ip',
            is_special_testing_ip='0',
        )

        self.env.statbox.bind_entry(
            'registration_sms_per_phone_limit_has_exceeded',
            mode='phonereg',
            action='registration_with_sms',
            error='registration_sms_per_phone_limit_has_exceeded',
            counter_prefix='registration:sms:phone',
            is_phonish='0',
        )

        self.env.statbox.bind_entry(
            'base_phone_entry',
            mode='phonereg',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'local_phone_confirmed',
            _inherit_from=['phone_confirmed', 'base_phone_entry'],
            _exclude={'operation_id'},
            phone_id='1',
            code_checks_count='0',
            confirmation_time=DatetimeNow(convert_to_datetime=True),
        )
        self.env.statbox.bind_entry(
            'local_secure_phone_bound',
            _inherit_from=['secure_phone_bound', 'base_phone_entry'],
            _exclude={'operation_id'},
            phone_id='1',
        )

    def check_statbox(self, suid='1', **account_created_kwargs):
        names_values = [
            ('person.firstname', {'old': '-', 'new': 'firstname'}),
            ('person.lastname', {'old': '-', 'new': 'lastname'}),
            ('person.language', {'old': '-', 'new': 'ru'}),
            ('person.country', {'old': '-', 'new': 'ru'}),
            ('person.fullname', {'old': '-', 'new': 'firstname lastname'}),
            ('password.encrypted', {}),
            ('password.encoding_version', {'old': '-', 'new': str(self.password_hash_version)}),
            ('password.quality', {'old': '-', 'new': '80'}),
        ]
        login = account_created_kwargs.get('login', TEST_USER_LOGIN_NORMALIZED)
        user_defined_login = account_created_kwargs.pop('user_defined_login', TEST_USER_LOGIN)

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
                entity='account.mail_status',
                old='-',
                new='active',
            ),
        ]
        if user_defined_login != login:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    operation='created',
                    ip=TEST_USER_IP,
                    user_agent=TEST_USER_AGENT,
                    consumer='dev',
                    entity='user_defined_login',
                    old='-',
                    new=user_defined_login,
                ),
            ]
        entries += [
            self.env.statbox.entry(
                'account_modification',
                operation='added',
                ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
                consumer='dev',
                entity='aliases',
                type='1',
                value=login,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='phones.secure',
                operation='created',
                old='-',
                old_entity_id='-',
                new=TEST_PHONE_NUMBER.masked_format_for_statbox,
                new_entity_id='1',
                ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
                consumer='dev',
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
                suid=suid,
                login=login,
            ),
            self.env.statbox.entry('subscriptions', sid='8'),
            self.env.statbox.entry('subscriptions', sid='2', suid=suid),
        ]

        entries += [
            self.env.statbox.entry('local_phone_confirmed'),
            self.env.statbox.entry('local_secure_phone_bound'),
        ]

        karma_value = account_created_kwargs.get('karma')
        if karma_value and karma_value != '0':
            entries.append(
                self.env.statbox.entry(
                    'frodo_karma',
                    action='phonereg',
                    suid=suid,
                    old='0',
                    new=karma_value,
                ),
            )

        entries.append(
            self.env.statbox.entry('account_created', **account_created_kwargs),
        )
        self.env.statbox.assert_has_written(entries)

    def get_registration_sms_counter(self):
        return sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP)

    def get_registration_sms_per_phone_counter(self):
        return sms_per_phone.get_per_phone_on_registration_buckets()

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
    FRODO_URL='http://localhost/',
    **mock_counters()
)
@istest
class TestAccountRegisterRequireConfirmedPhone(TestAccountRegisterRequireConfirmedPhoneBase,
                                               make_clean_web_test_mixin('test_register', ['firstname', 'lastname'], statbox_action='phone_confirmed', is_bundle=False),
                                               ):
    def frodo_params(self, **kwargs):
        params = EmptyFrodoParams(**{
            'uid': '1',
            'login': TEST_USER_LOGIN_NORMALIZED,
            'iname': 'firstname',
            'fname': 'lastname',
            'from': 'test_service',
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
            'action': 'phonereg',
            'lang': 'ru',
            'xcountry': 'ru',
            'phonenumber': TEST_PHONE_NUMBER_MASKED_FOR_FRODO,
            'v2_phonenumber_hash': get_phone_number_hash(TEST_PHONE_NUMBER.e164),
            'v2_phone_validation_changes': '1',
            'v2_phone_validation_error': '1',
            'v2_phone_confirmation_sms_count': '2',
            'v2_phone_confirmation_confirms_count': '3',
            'v2_track_created': TimeNow(),
            'v2_old_password_quality': '',
            'v2_account_country': 'ru',
            'v2_account_language': 'ru',
            'v2_account_timezone': 'Europe/Moscow',
            'v2_account_karma': '',
            'v2_accept_language': TEST_ACCEPT_LANGUAGE,
            'v2_is_ssl': '1',
            'v2_has_cookie_l': '0',
            'v2_has_cookie_yandex_login': '0',
            'v2_has_cookie_my': '0',
            'v2_has_cookie_ys': '0',
            'v2_has_cookie_yp': '0',
        })
        params.update(**kwargs)
        return params

    def test_without_need_headers(self):

        rv = self.account_register_request(
            self.query_params(),
            {},
        )

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

    def test_eula_not_accepted(self):

        rv = self.account_register_request(
            self.query_params(eula_accepted='False'),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [
                    {
                        u'field': None,
                        u'message': u'Eula is not accepted',
                        u'code': u'eulaisnotacceptederror',
                    },
                ],
            },
        )

    def test_phone_not_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = False

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None, u'message': u'User was not verified', u'code': u'usernotverifiederror'}]},
        )

    def test_register(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 5)

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

        self.check_statbox(
            retpath=TEST_RETPATH,
        )

        counter = self.get_registration_sms_counter()
        eq_(counter.get(TEST_USER_IP), 1)

        self.env.event_logger.assert_contains([
            {'uid': '1', 'name': 'phone.1.action', 'value': 'created'},
            {'uid': '1', 'name': 'phone.1.created', 'value': TimeNow()},
            {'uid': '1', 'name': 'phone.1.bound', 'value': TimeNow()},
            {'uid': '1', 'name': 'phone.1.secured', 'value': TimeNow()},
            {'uid': '1', 'name': 'phone.1.confirmed', 'value': TimeNow()},
            {'uid': '1', 'name': 'phone.1.number', 'value': TEST_PHONE_NUMBER.e164},

            {'uid': '1', 'name': 'phones.secure', 'value': '1'},
        ])

    def test_register_with_suggested_login(self):

        login = 'suggested'

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({login: 'free'}),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.suggested_logins.append(login, 'aaa')

        rv = self.account_register_request(
            self.query_params(
                login=login,
            ),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 5)

        self.check_statbox(
            login=login,
            user_defined_login=login,
            is_suggested_login='1',
        )

    def test_register_with_login_normalization(self):
        login = 'test.login'
        timenow = TimeNow()

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({login: 'free'}),
        )

        rv = self.account_register_request(
            self.query_params(
                login=login,
            ),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 5)

        self.env.db.check('aliases', 'portal', TEST_USER_LOGIN_NORMALIZED, uid=1, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.user_defined_login', TEST_USER_LOGIN, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.quality', '3:80', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.firstname', 'firstname', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.lastname', 'lastname', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.gender', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.birthday', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.timezone', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.country', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.city', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.language', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')

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
                'info.tz': 'Europe/Moscow',
                'info.country': 'ru',
                'info.lang': 'ru',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'info.password_quality': '80',
                'info.password': eav_pass_hash,
                'info.password_update_time': TimeNow(),
                'sid.add': '8|test.login,2',
                'mail.add': '1',
                'info.mail_status': '1',
                'alias.portal.add': TEST_USER_LOGIN_NORMALIZED,
                'info.karma': '0',
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'user_agent': 'curl',

                'phone.1.action': 'created',
                'phone.1.number': TEST_PHONE_NUMBER.e164,
                'phone.1.created': TimeNow(),
                'phone.1.confirmed': TimeNow(),
                'phone.1.bound': TimeNow(),
                'phone.1.secured': TimeNow(),
                'phones.secure': '1',
            },
        )

        self.check_statbox(
            login=TEST_USER_LOGIN_NORMALIZED,
            user_defined_login=TEST_USER_LOGIN,
        )

    def test_register_with_frodo_spam_user(self):

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.sanitize_phone_changed_phone = True
            track.sanitize_phone_error = True
            for _ in range(2):
                track.phone_confirmation_sms_count.incr()
            for _ in range(3):
                track.phone_confirmation_confirms_count.incr()
            track.service = 'test_service'

        self.env.frodo.set_response_value(
            u'check',
            u'<spamlist><spam_user login="%s" weight="85" /></spamlist>' % (
                TEST_USER_LOGIN_NORMALIZED,
            ),
        )
        self.env.frodo.set_response_value(u'confirm', u'')

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(self.frodo_params())

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 6)
        self.env.db.check('attributes', 'karma.value', '85', uid=1, db='passportdbshard1')

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '85')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '85')

        self.check_statbox(
            karma='85',
        )

    def test_register_with_frodo_change_pass(self):

        self.env.frodo.set_response_value(
            u'check',
            u'<spamlist><change_pass login="%s" weight="85" /></spamlist>' % (
                TEST_USER_LOGIN_NORMALIZED,
            ),
        )
        self.env.frodo.set_response_value(u'confirm', u'')

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 6)
        self.env.db.check('attributes', 'karma.value', '7000', uid=1, db='passportdbshard1')

        assert_builder_requested(self.env.frodo, times=2)

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_prefix', '7')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '7000')

        self.check_statbox(
            karma='7000',
        )

    def test_register_with_frodo_side_effect(self):

        self.env.frodo.set_response_side_effect(u'check', FrodoError('Failed'))

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 5)
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')

        assert_builder_requested(self.env.frodo, times=1)
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '0')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '0')

        self.check_statbox(
        )

    def test_registration_already_completed_error(self):

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        rv = self.account_register_request(
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

    def test_registration_with_phone__registration_sms_per_ip_limit_exceeded__statbox_not_logged(self):
        counter = self.get_registration_sms_counter()
        for i in range(counter.limit - 1):
            counter.incr(TEST_USER_IP)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), {'status': 'ok', 'uid': 1})
        ok_(counter.hit_limit(TEST_USER_IP))
        ok_('error' not in self.get_events_from_handler(self.env.statbox_handle_mock))

    def test_registration_with_phone__registration_sms_per_phone_limit_exceeded__statbox_not_logged(self):
        counter = self.get_registration_sms_per_phone_counter()
        for i in range(counter.limit - 1):
            counter.incr(TEST_PHONE_NUMBER.e164)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), {'status': 'ok', 'uid': 1})
        ok_('error' not in self.get_events_from_handler(self.env.statbox_handle_mock))

    def test_registration_with_phone__registration_sms_per_ip_limit_already_exceeded__error_and_statbox_logged(self):
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

    def test_registration_with_phone__registration_sms_per_phone_limit_already_exceeded__error_and_statbox_logged(self):
        counter = self.get_registration_sms_per_phone_counter()
        for i in range(counter.limit):
            counter.incr(TEST_PHONE_NUMBER.e164)

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
                'registration_sms_per_phone_limit_has_exceeded',
                counter_current_value=str(counter.limit),
                counter_limit_value=str(counter.limit),
            ),
        ])


@with_settings_hosts(
    FRODO_URL='http://localhost/',
)
@istest
class TestAccountRegisterRequireConfirmedPhoneTrackContent(TestAccountRegisterRequireConfirmedPhoneBase,
                                                           make_clean_web_test_mixin('test_basic', ['firstname', 'lastname'], statbox_action='phone_confirmed', is_bundle=False),
                                                           ):
    def test_basic(self):
        rv = self.account_register_request(
            self.query_params(language='tr'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

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

    def test_language_in_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.language = 'en'

        rv = self.account_register_request(
            self.query_params(language='tr'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

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


@with_settings_hosts()
@istest
class TestPhone(TestAccountRegisterRequireConfirmedPhoneBase,
                make_clean_web_test_mixin('test_with_phone_is_confirmed', ['firstname', 'lastname'], statbox_action='phone_confirmed', is_bundle=False),
                ):
    def test_with_phone_is_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.account_register_request(self.query_params(), build_headers())

        rv = json.loads(rv.data)
        eq_(rv['status'], 'ok')

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

        counter = self.get_registration_sms_counter()
        eq_(counter.get(TEST_USER_IP), 1)

        self.env.event_logger.assert_contains([
            {'uid': '1', 'name': 'phone.1.action', 'value': 'created'},
            {'uid': '1', 'name': 'phone.1.created', 'value': TimeNow()},
            {'uid': '1', 'name': 'phone.1.bound', 'value': TimeNow()},
            {'uid': '1', 'name': 'phone.1.secured', 'value': TimeNow()},
            {'uid': '1', 'name': 'phone.1.confirmed', 'value': TimeNow()},
            {'uid': '1', 'name': 'phone.1.number', 'value': TEST_PHONE_NUMBER.e164},

            {'uid': '1', 'name': 'phones.secure', 'value': '1'},
        ])

        self.check_statbox(
        )


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAccountRegisterRequireConfirmedPhoneNoBlackboxHash(TestAccountRegisterRequireConfirmedPhone):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
