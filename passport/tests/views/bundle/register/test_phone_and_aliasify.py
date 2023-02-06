# -*- coding: utf-8 -*-

from functools import partial
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.templatetags import span
from passport.backend.api.test.emails import assert_user_notified_about_alias_as_login_and_email_owner_changed
from passport.backend.api.test.mixins import (
    EmailTestMixin,
    make_clean_web_test_mixin,
    ProfileTestMixin,
)
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test import StatboxTestMixin
from passport.backend.api.tests.views.bundle.register.test.base_test_data import *
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.builders.frodo.utils import get_phone_number_hash
from passport.backend.core.builders.yasms.exceptions import YaSmsError
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.counters import (
    registration_karma,
    sms_per_ip,
)
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.frodo.exceptions import FrodoError
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.phones.faker import assert_secure_phone_bound
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import merge_dicts


TEST_USER_COOKIES = 'yandexuid=cookie_yandexuid; yandex_gid=cookie_yandex_gid; fuid01=cookie_fuid01'


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
    YASMS_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    BLACKBOX_URL='http://localhost',
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    CLEAN_WEB_API_ENABLED=False,
    **mock_counters()
)
class TestAccountRegisterPhoneAndAliasify(
    BaseTestViews,
    StatboxTestMixin,
    EmailTestMixin,
    make_clean_web_test_mixin('test_successful_register', ['firstname', 'lastname'], statbox_action='phone_confirmed'),
    ProfileTestMixin,
):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['register_phone_and_aliasify']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')
        self.setup_statbox_templates()
        self.patches = []
        self.setup_profile_patches()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.teardown_profile_patches()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.patches

    def account_register_request(self, data, headers):
        return self.env.client.post(
            '/1/bundle/account/register/phone_and_aliasify/?consumer=dev',
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
            'mode': 'digitsreg',
            'eula_accepted': 'True',
            'email_domain': 'yandex.ru',
        }
        return merge_dicts(base_params, kwargs)

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='digitsreg',
            ip=TEST_USER_IP,
            user_agent='curl',
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_search_enabled',
            _exclude=['mode'],
            ip=TEST_USER_IP,
        )
        super(TestAccountRegisterPhoneAndAliasify, self).setup_statbox_templates()

    def assert_statbox_ok(self, dealiasify=False, dealiasify_error=False,
                          suid='1', **account_created_kwargs):
        entries = [
            self.env.statbox.entry(
                'submitted',
            ),
        ]

        if dealiasify_error:
            entries.extend([
                self.env.statbox.entry('phonenumber_alias_taken_away'),
                self.env.statbox.entry('dealiasify_error'),
            ])
            self.env.statbox.assert_has_written(entries)
            return

        if dealiasify:
            entries.extend([
                self.env.statbox.entry('phonenumber_alias_taken_away'),
                self.env.statbox.entry('phonenumber_alias_removed'),
                self.env.statbox.entry('phonenumber_alias_subscription_removed'),
            ])

        entries.extend([
            self.env.statbox.entry(
                'aliasify',
                uid='-',
                login=TEST_USER_LOGIN,
                is_owner_changed=tskv_bool(dealiasify),
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
                operation='created',
                old='-',
                new='enabled',
            ),
            self.env.statbox.entry(
                'account_modification',
                operation='created',
                entity='account.mail_status',
                old='-',
                new='active',
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='user_defined_login',
                old='-',
                new=TEST_USER_LOGIN,
            ),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['old', 'new'],
                entity='aliases',
                operation='added',
                type=str(ANT['portal']),
                value=TEST_USER_LOGIN_NORMALIZED,
            ),
            self.env.statbox.entry('phonenumber_alias_added'),
            self.env.statbox.entry(
                'account_modification',
                entity='phones.secure',
                new=TEST_PHONE_NUMBER.masked_format_for_statbox,
                old_entity_id='-',
                new_entity_id='1',
            ),
        ])

        for entity, new in [
            ('person.firstname', 'firstname'),
            ('person.lastname', 'lastname'),
            ('person.language', 'ru'),
            ('person.country', 'ru'),
            ('person.fullname', 'firstname lastname'),
        ]:
            entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity=entity,
                    new=new,
                ),
            )
        entries.extend([
            self.env.statbox.entry(
                'account_modification',
                _exclude=['old', 'new'],
                entity='password.encrypted',
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='password.encoding_version',
                new=str(self.password_hash_version),
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='password.quality',
                new=TEST_PASSWORD_QUALITY,
            ),
        ])
        entries.append(
            self.env.statbox.entry(
                'account_register',
                login=account_created_kwargs.get('login', TEST_USER_LOGIN_NORMALIZED),
                suid=suid,
            ),
        )
        entries.extend([
            self.env.statbox.entry(
                'subscriptions',
                sid='8',
            ),
            self.env.statbox.entry(
                'subscriptions',
                sid='2',
                suid=str(TEST_SUID),
            ),
            self.env.statbox.entry(
                'subscriptions',
                sid='65',
            ),
            self.env.statbox.entry('phonenumber_alias_search_enabled'),
        ])
        entries.extend([
            self.env.statbox.entry('phone_confirmed'),
            self.env.statbox.entry('secure_phone_bound'),
        ])
        entries.append(self.env.statbox.entry('notification_sent'))
        # Если карма НЕ 0, то был вызов к ФО, который добавляет запись в лог.
        karma_value = account_created_kwargs.get('karma')
        if karma_value and karma_value != '0':
            entries.append(
                self.env.statbox.entry(
                    'phonereg',
                    new=karma_value,
                    login=TEST_USER_LOGIN_NORMALIZED,
                    suid=suid,
                ),
            )

        entries.append(
            self.env.statbox.entry(
                'account_created',
                **account_created_kwargs
            ),
        )
        self.env.statbox.assert_has_written(entries)

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
            'yandexuid': 'cookie_yandexuid',
            'v2_yandex_gid': 'cookie_yandex_gid',
            'fuid': 'cookie_fuid01',
            'useragent': 'curl',
            'host': 'yandex.ru',
            'ip_from': TEST_USER_IP,
            'v2_ip': TEST_USER_IP,
            'valkey': '0000000000',
            'action': 'phonereg',
            'lang': 'ru',
            'xcountry': 'ru',
            'phonenumber': TEST_PHONE_NUMBER.masked_format_for_frodo,
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

    def test_empty_request(self):
        rv = self.account_register_request({}, {})

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['track_id.empty'],
            },
        )

    def test_eula_not_accepted(self):
        rv = self.account_register_request(
            self.query_params(eula_accepted='False'),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['eula_accepted.not_accepted'],
            },
        )

    def test_invalid_password(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.country = 'ru'

        for password, codes in [
            ('.', ['password.short']),
            (TEST_USER_LOGIN, ['password.likelogin']),
            ('aaabbb', ['password.weak']),
            (TEST_PHONE_NUMBER.e164, ['password.likephonenumber']),
            (
                TEST_PHONE_NUMBER.national,
                [
                    'password.likephonenumber',
                    'password.prohibitedsymbols',
                ],
            ),
        ]:
            rv = self.account_register_request(
                self.query_params(password=password),
                build_headers(),
            )

            eq_(rv.status_code, 200)
            eq_(
                json.loads(rv.data),
                {
                    'status': 'error',
                    'errors': codes,
                },
            )

    def test_phone_not_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = False

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['user.not_verified'],
            },
        )

    def test_already_registered(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['account.already_registered'],
            },
        )

    def test_register__registration_sms_limit_reached__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        counter = sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP)
        for i in range(counter.limit + 1):
            counter.incr(TEST_USER_IP)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['account.registration_limited'],
            },
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'submitted',
            ),
            self.env.statbox.entry(
                'registration_with_sms_error',
                counter_current_value=str(counter.limit + 1),
                counter_limit_value=str(counter.limit),
            ),
        ])

    def test_successful_register(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.retpath = TEST_RETPATH

        timenow = TimeNow()

        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 0)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 6)

        self.env.db.check('suid2', 'suid', 1, uid=1, db='passportdbcentral')
        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=1, db='passportdbcentral')

        self.env.db.check('aliases', 'portal', 'test-login', uid=1, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.user_defined_login', TEST_USER_LOGIN, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.quality', '3:80', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.firstname', 'firstname', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.lastname', 'lastname', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.display_name', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.gender', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.birthday', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.timezone', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.country', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.city', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.language', uid=1, db='passportdbshard1')

        assert_secure_phone_bound.check_db(
            self.env.db,
            uid=1,
            phone_attributes={
                'id': 1,
                'number': TEST_PHONE_NUMBER.e164,
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

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            [
                {'name': 'info.login', 'value': TEST_USER_LOGIN_NORMALIZED},
                {'name': 'info.login_wanted', 'value': TEST_USER_LOGIN},
                {'name': 'info.ena', 'value': '1'},
                {'name': 'info.disabled_status', 'value': '0'},
                {'name': 'info.reg_date', 'value': DatetimeNow(convert_to_datetime=True)},
                {'name': 'info.mail_status', 'value': '1'},
                {'name': 'info.firstname', 'value': 'firstname'},
                {'name': 'info.lastname', 'value': 'lastname'},
                {'name': 'info.country', 'value': 'ru'},
                {'name': 'info.tz', 'value': 'Europe/Moscow'},
                {'name': 'info.lang', 'value': 'ru'},
                {'name': 'info.password', 'value': eav_pass_hash},
                {'name': 'info.password_quality', 'value': '80'},
                {'name': 'info.password_update_time', 'value': TimeNow()},
                {'name': 'info.karma_prefix', 'value': '0'},
                {'name': 'info.karma_full', 'value': '0'},
                {'name': 'info.karma', 'value': '0'},
                {'name': 'alias.portal.add', 'value': TEST_USER_LOGIN_NORMALIZED},
                {'name': 'alias.phonenumber.add', 'value': TEST_PHONE_NUMBER.international},
                {'name': 'info.phonenumber_alias_search_enabled', 'value': '1'},
                {'name': 'mail.add', 'value': '1'},
                {'name': 'sid.add', 'value': '8|test.login,2'},
                {'name': 'phone.1.action', 'value': 'created'},
                {'name': 'phone.1.bound', 'value': timenow},
                {'name': 'phone.1.confirmed', 'value': timenow},
                {'name': 'phone.1.created', 'value': timenow},
                {'name': 'phone.1.number', 'value': TEST_PHONE_NUMBER.e164},
                {'name': 'phone.1.secured', 'value': timenow},
                {'name': 'phones.secure', 'value': '1'},
                {'name': 'action', 'value': 'account_register'},
                {'name': 'consumer', 'value': 'dev'},
                {'name': 'user_agent', 'value': 'curl'},
            ],
        )

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'from_uid': '1',
            'phone': TEST_PHONE_NUMBER.e164,
            'text': u'Ваш логин для восстановления пароля: %s' % TEST_USER_LOGIN,
            'identity': 'phone_registration_login_reminder.notify',
        })

        assert_builder_requested(self.env.frodo, times=1)
        eq_(self.env.mailer.message_count, 1)

        self.assert_statbox_ok(retpath=TEST_RETPATH)

        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 1)
        eq_(sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP).get(TEST_USER_IP), 1)

        track = self.track_manager.read(self.track_id)
        eq_(track.uid, '1')
        eq_(track.login, 'test.login')
        eq_(track.human_readable_login, 'test.login')
        eq_(track.machine_readable_login, 'test-login')

        eq_(track.language, 'ru')
        eq_(track.have_password, True)
        eq_(track.is_successful_registered, True)
        eq_(track.allow_authorization, True)
        eq_(track.allow_oauth_authorization, True)

    def test_register_with_env_profile_modification(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.retpath = TEST_RETPATH

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )
        profile = self.make_user_profile(
            raw_env={'ip': TEST_USER_IP, 'yandexuid': 'cookie_yandexuid', 'user_agent_info': {}},
        )
        self.assert_profile_written_to_auth_challenge_log(profile)

    def test_timezone_detection(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.retpath = TEST_RETPATH

        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 0)
        rv = self.account_register_request(
            self.query_params(),
            build_headers(user_ip='8.8.8.8'),
        )
        eq_(rv.status_code, 200)

        self.env.db.check('attributes', 'person.timezone', 'America/New_York', uid=1, db='passportdbshard1')

    def test_register_with_frodo_spam_user(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.sanitize_phone_changed_phone = True
            track.sanitize_phone_error = True
            for _ in range(2):
                track.phone_confirmation_sms_count.incr()
            for _ in range(3):
                track.phone_confirmation_confirms_count.incr()
            track.service = 'test_service'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        self.env.frodo.set_response_value(
            u'check',
            '<spamlist><spam_user login="%s" weight="85" /></spamlist>' % (
                TEST_USER_LOGIN_NORMALIZED,
            ),
        )
        self.env.frodo.set_response_value(u'confirm', u'')

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )

        eq_(self.env.mailer.message_count, 1)

        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(self.frodo_params())

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 7)
        self.env.db.check('attributes', 'karma.value', '85', uid=1, db='passportdbshard1')

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '85')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '85')

        self.assert_statbox_ok(karma='85')

    def test_register_with_frodo_change_pass(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

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

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )

        assert_builder_requested(self.env.frodo, times=2)
        eq_(self.env.mailer.message_count, 1)

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 7)
        self.env.db.check('attributes', 'karma.value', '7000', uid=1, db='passportdbshard1')

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_prefix', '7')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '7000')

        self.assert_statbox_ok(karma='7000')

    def test_register_with_frodo_side_effect(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        self.env.frodo.set_response_side_effect(u'check', FrodoError('Failed'))

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )
        assert_builder_requested(self.env.frodo, times=1)
        eq_(self.env.mailer.message_count, 1)

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 6)
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '0')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '0')

        self.assert_statbox_ok()

    def test_regkarma_bad(self):
        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 0)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

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

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )

        assert_builder_requested(self.env.frodo, times=2)
        eq_(self.env.mailer.message_count, 1)

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 7)
        self.env.db.check('attributes', 'karma.value', '100', uid=1, db='passportdbshard1')

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '100')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '100')

        self.assert_statbox_ok(karma='100')

        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 1)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 0)

    def test_successful_register_with_delete_alias(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        blackbox_response_with_alias = blackbox_userinfo_response(
            uid='2',
            login=TEST_PHONE_NUMBER.digital,
            aliases={
                'portal': TEST_OTHER_LOGIN,
                'phonenumber': TEST_PHONE_NUMBER.digital,
            },
            attributes={'account.enable_search_by_phone_alias': '1'},
            emails=[{
                'default': True,
                'native': True,
                'validated': True,
                'address': 'withalias@yandex.ru',
            }],
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response_with_alias,
        )

        self.env.db.check_missing('aliases', 'phonenumber', uid=2, db='passportdbcentral')

        self.env.db.serialize(blackbox_response_with_alias)

        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=2, db='passportdbcentral')

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )

        self.assert_emails_sent([
            partial(
                assert_user_notified_about_alias_as_login_and_email_owner_changed,
                mailer_faker=self.env.mailer,
                language='ru',
                email_address='withalias@yandex.ru',
                firstname='\u0414',
                login='login',
                portal_email='login@yandex.ru',
                phonenumber_alias=TEST_PHONE_NUMBER.digital,
            ),
            {
                'language': 'ru',
                'addresses': ['%s@%s' % (TEST_PHONE_NUMBER.digital, 'yandex.ru')],
                'subject': 'digitreg.subject',
                'tanker_keys': {
                    'signature.mail': {},
                    'digitreg.notebook_url': {},
                    'digitreg.explanation': {
                        'PHONE_ALIAS_LOGIN': span(TEST_PHONE_NUMBER.digital, 'font-weight: bold;'),
                        'PORTAL_LOGIN': self.get_portal_login_markup(TEST_USER_LOGIN),
                    },
                },
            },
        ])

        eq_(self.env.db.query_count('passportdbcentral'), 7)
        eq_(self.env.db.query_count('passportdbshard1'), 7)

        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=1, db='passportdbcentral')
        self.env.db.check_missing('aliases', 'phonenumber', uid=2, db='passportdbcentral')
        self.env.db.check('removed_aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=2, db='passportdbcentral')

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=1, db='passportdbshard1')
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('%s:' % self.password_hash_version))

        timenow = TimeNow()
        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            [
                # Удаление алиаса
                {'name': 'alias.phonenumber.rm', 'value': str(TEST_PHONE_NUMBER)},
                {'name': 'action', 'value': 'phone_alias_delete'},
                {'name': 'consumer', 'value': 'dev'},
                # Регистрация аккаунта
                {'name': 'info.login', 'value': TEST_USER_LOGIN_NORMALIZED},
                {'name': 'info.login_wanted', 'value': TEST_USER_LOGIN},
                {'name': 'info.ena', 'value': '1'},
                {'name': 'info.disabled_status', 'value': '0'},
                {'name': 'info.reg_date', 'value': DatetimeNow(convert_to_datetime=True)},
                {'name': 'info.mail_status', 'value': '1'},
                {'name': 'info.firstname', 'value': 'firstname'},
                {'name': 'info.lastname', 'value': 'lastname'},
                {'name': 'info.country', 'value': 'ru'},
                {'name': 'info.tz', 'value': 'Europe/Moscow'},
                {'name': 'info.lang', 'value': 'ru'},
                {'name': 'info.password', 'value': eav_pass_hash},
                {'name': 'info.password_quality', 'value': '80'},
                {'name': 'info.password_update_time', 'value': timenow},
                {'name': 'info.karma_prefix', 'value': '0'},
                {'name': 'info.karma_full', 'value': '0'},
                {'name': 'info.karma', 'value': '0'},
                {'name': 'alias.portal.add', 'value': TEST_USER_LOGIN_NORMALIZED},
                {'name': 'alias.phonenumber.add', 'value': TEST_PHONE_NUMBER.international},
                {'name': 'info.phonenumber_alias_search_enabled', 'value': '1'},
                {'name': 'mail.add', 'value': '1'},
                {'name': 'sid.add', 'value': '8|test.login,2'},
                {'name': 'phone.1.action', 'value': 'created'},
                {'name': 'phone.1.bound', 'value': timenow},
                {'name': 'phone.1.confirmed', 'value': timenow},
                {'name': 'phone.1.created', 'value': timenow},
                {'name': 'phone.1.number', 'value': TEST_PHONE_NUMBER.e164},
                {'name': 'phone.1.secured', 'value': timenow},
                {'name': 'phones.secure', 'value': '1'},
                {'name': 'action', 'value': 'account_register'},
                {'name': 'consumer', 'value': 'dev'},
                {'name': 'user_agent', 'value': 'curl'},
            ],
        )

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'from_uid': '1',
            'phone': TEST_PHONE_NUMBER.e164,
            'text': u'Ваш логин для восстановления пароля: %s' % TEST_USER_LOGIN,
            'identity': 'phone_registration_login_reminder.notify',
        })

        assert_builder_requested(self.env.frodo, times=1)
        self.assert_statbox_ok(dealiasify=True)

    def test_with_yasmserror_on_send_sms(self):
        self.env.yasms.set_response_side_effect('send_sms', YaSmsError('error message'))

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )

        eq_(self.env.mailer.message_count, 1)

        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 6)

        assert_builder_requested(self.env.frodo, times=1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'from_uid': '1',
            'phone': TEST_PHONE_NUMBER.e164,
            'text': u'Ваш логин для восстановления пароля: %s' % TEST_USER_LOGIN,
            'identity': 'phone_registration_login_reminder.notify',
        })

    def test_not_register_with_delete_alias(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        blackbox_response_with_alias = blackbox_userinfo_response(
            uid='2',
            login=TEST_PHONE_NUMBER.digital,
            aliases={
                'portal': TEST_PHONE_NUMBER.digital,
                'phonenumber': TEST_PHONE_NUMBER.digital,
            },
            attributes={'account.enable_search_by_phone_alias': '1'},
            emails=[{
                'default': True,
                'native': True,
                'validated': True,
                'address': 'withalias@yandex.ru',
            }],
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response_with_alias,
        )

        self.env.db.serialize(blackbox_response_with_alias)

        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=2, db='passportdbcentral')

        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['backend.database_failed'],
            },
        )
        self.assert_statbox_ok(
            dealiasify=True,
            dealiasify_error=True,
        )

    def test_successful_register_with_turkey_email(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        eq_(registration_karma.get_bad_buckets().get(TEST_USER_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_USER_IP), 0)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(host='yandex.com.tr'),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )

        self.assert_emails_sent([
            {
                'language': 'ru',
                'addresses': ['%s@%s' % (TEST_PHONE_NUMBER.digital, 'yandex.com')],
                'subject': 'digitreg.subject',
                'tanker_keys': {
                    'signature.mail': {},
                    'digitreg.notebook_url': {},
                    'digitreg.explanation': {
                        'PHONE_ALIAS_LOGIN': span(TEST_PHONE_NUMBER.digital, 'font-weight: bold;'),
                        'PORTAL_LOGIN': self.get_portal_login_markup(TEST_USER_LOGIN),
                    },
                },
            },
        ])


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAccountRegisterPhoneAndAliasifyNoBlackboxHash(TestAccountRegisterPhoneAndAliasify):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
