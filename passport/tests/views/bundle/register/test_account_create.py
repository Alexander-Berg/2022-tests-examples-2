# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.test.mixins import (
    EmailTestMixin,
    make_clean_web_test_mixin,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test.base_test_data import (
    build_headers,
    TEST_EMAIL,
    TEST_HOST,
    TEST_PERSISTENT_TRACK_ID,
    TEST_SERIALIZED_PASSWORD,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_FIRSTNAME,
    TEST_USER_IP,
    TEST_USER_PASSWORD,
    TEST_USER_PASSWORD_QUALITY,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.frodo.exceptions import FrodoError
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.utils.common import merge_dicts


TEST_USER_LOGIN = 'test.login'
TEST_USER_LOGIN_NORMALIZED = 'test-login'
TEST_USER_LASTNAME = 'lastname'
TEST_USER_LANGUAGE = 'ru'
TEST_USER_COUNTRY = 'tr'
TEST_USER_GENGER = 'm'
TEST_USER_BIRTHDAY = '1950-01-30'
TEST_USER_TIMEZONE = 'Europe/Paris'
TEST_SUID = 1
TEST_PERSISTENT_TRACK_KEY = TEST_PERSISTENT_TRACK_ID + str(TEST_UID)


@with_settings_hosts(
    FRODO_URL='http://localhost/',
    RESTORE_DEFAULT_URL_TEMPLATE="RESTORE_DEFAULT_URL_TEMPLATE?tld=%(tld)s",
    AUTH_BY_KEY_LINK_TEMPLATE_URL="AUTH_BY_KEY_LINK_TEMPLATE_URL?key=%(key)s&tld=%(tld)s",
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    CLEAN_WEB_API_ENABLED=False,
)
class TestAccountCreate(BaseBundleTestViews,
                        make_clean_web_test_mixin('test_ok', ['firstname', 'lastname']),
                        EmailTestMixin):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants())

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
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
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.setup_statbox_templates()

        self._generate_persistent_track_id_mock = mock.Mock(return_value=TEST_PERSISTENT_TRACK_ID)
        self._generate_persistent_track_id_patch = mock.patch(
            'passport.backend.core.models.persistent_track.generate_track_id',
            self._generate_persistent_track_id_mock,
        )
        self.generate_persistent_track_mock = self._generate_persistent_track_id_patch.start()

    def tearDown(self):
        self._generate_persistent_track_id_patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self._generate_persistent_track_id_mock
        del self._generate_persistent_track_id_patch
        del self.generate_persistent_track_mock

    def make_request(self, data, headers):
        return self.env.client.post(
            '/1/bundle/account/register/?consumer=dev',
            data=data,
            headers=headers,
        )

    def query_params(self, **kwargs):
        base_params = {
            'login': TEST_USER_LOGIN,
            'password': TEST_USER_PASSWORD,
            'firstname': TEST_USER_FIRSTNAME,
            'lastname': TEST_USER_LASTNAME,
            'language': TEST_USER_LANGUAGE,
            'country': TEST_USER_COUNTRY,
            'gender': TEST_USER_GENGER,
            'birthday': TEST_USER_BIRTHDAY,
            'timezone': TEST_USER_TIMEZONE,
            'track_id': self.track_id,
        }
        return merge_dicts(base_params, kwargs)

    def get_expected_frodo_params(self, **kwargs):
        params = EmptyFrodoParams(**{
            'uid': str(TEST_UID),
            'login': TEST_USER_LOGIN_NORMALIZED,
            'iname': TEST_USER_FIRSTNAME,
            'fname': TEST_USER_LASTNAME,
            'consumer': 'dev',
            'passwd': '10.0.9.1',
            'passwdex': '3.6.0.0',
            'v2_password_quality': str(TEST_USER_PASSWORD_QUALITY),
            'hintq': '0.0.0.0.0.0',
            'hintqex': '0.0.0.0.0.0',
            'hinta': '0.0.0.0.0.0',
            'hintaex': '0.0.0.0.0.0',
            'yandexuid': '',
            'v2_yandex_gid': '',
            'fuid': '',
            'useragent': TEST_USER_AGENT,
            'host': TEST_HOST,
            'social_provider': '',
            'ip_from': TEST_USER_IP,
            'v2_ip': TEST_USER_IP,
            'valkey': '0000000000',
            'step1time': '2000',
            'step2time': '2000',
            'action': 'admreg',
            'lang': TEST_USER_LANGUAGE,
            'xcountry': TEST_USER_COUNTRY,
            'v2_old_password_quality': '',
            'v2_account_country': TEST_USER_COUNTRY,
            'v2_account_language': TEST_USER_LANGUAGE,
            'v2_account_timezone': TEST_USER_TIMEZONE,
            'v2_account_karma': '',
            'v2_accept_language': 'ru',
            'v2_is_ssl': '1',
            'v2_has_cookie_l': '0',
            'v2_has_cookie_yandex_login': '0',
            'v2_has_cookie_my': '0',
            'v2_has_cookie_ys': '0',
            'v2_has_cookie_yp': '0',
            'v2_track_created': TimeNow(),
        })
        params.update(**kwargs)
        return params

    def assert_statbox_ok(self, yastaff=False, subscriptions=False,
                          is_creating_required=False, karma=0, email=False,
                          is_password_passed=True, is_enabled=True):
        expected_entries = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
                old='-',
                new='enabled' if is_enabled else 'disabled',
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
        ]

        if email:
            now = DatetimeNow(convert_to_datetime=True)
            expected_entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    bound_at=now,
                    confirmed_at=now,
                    created_at=now,
                    email_id='1',
                    entity='account.emails',
                    new=mask_email_for_statbox(TEST_EMAIL),
                    uid=str(TEST_UID),
                    is_unsafe='0',
                    operation='added',
                    is_suitable_for_restore='1',
                ),
            )

        for entity, value in (
            ('person.firstname', TEST_USER_FIRSTNAME),
            ('person.lastname', TEST_USER_LASTNAME),
            ('person.language', TEST_USER_LANGUAGE),
            ('person.country', TEST_USER_COUNTRY),
            ('person.gender', TEST_USER_GENGER),
            ('person.birthday', TEST_USER_BIRTHDAY),
            ('person.fullname', '{} {}'.format(TEST_USER_FIRSTNAME, TEST_USER_LASTNAME)),
        ):
            expected_entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity=entity,
                    new=value,
                ),
            )

        if is_password_passed:
            expected_entries.extend([
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
                    new=str(TEST_USER_PASSWORD_QUALITY),
                ),
            ])

        expected_entries.extend([
            self.env.statbox.entry(
                'account_modification',
                _exclude=['operation'],
                action='account_create',
                entity='karma',
                destination='frodo',
                registration_datetime=DatetimeNow(convert_to_datetime=True),
                login=TEST_USER_LOGIN_NORMALIZED,
                suid=str(TEST_SUID),
                new='0',
            ),
            self.env.statbox.entry('account_modification_subscription_8'),
        ])

        if yastaff:
            expected_entries.extend([
                self.env.statbox.entry('account_modification_subscription_2'),
                self.env.statbox.entry('account_modification_subscription_669'),
            ])
        elif subscriptions:
            expected_entries.extend([
                self.env.statbox.entry('account_modification_subscription_24'),
                self.env.statbox.entry('account_modification_subscription_2'),
                self.env.statbox.entry('account_modification_subscription_23'),
            ])
        elif is_creating_required:
            expected_entries.extend([
                self.env.statbox.entry('account_modification_subscription_2'),
                self.env.statbox.entry('account_modification_subscription_100'),
            ])
        else:
            expected_entries.extend([
                self.env.statbox.entry('account_modification_subscription_2'),
            ])

        if karma:
            expected_entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    _exclude=['operation'],
                    action='admreg',
                    entity='karma',
                    destination='frodo',
                    registration_datetime=DatetimeNow(convert_to_datetime=True),
                    login=TEST_USER_LOGIN_NORMALIZED,
                    suid=str(TEST_SUID),
                    old='0',
                    new=str(karma),
                ),
            ])

        expected_entries.extend([
            self.env.statbox.entry(
                'account_created',
                karma=str(karma),
                _exclude=['password_quality'] if not is_password_passed else [],
            ),
        ])

        self.env.statbox.assert_has_written(expected_entries)

    def assert_statbox_submitted(self):
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            _inherit_from='base',
            mode='account_create',
            user_agent='curl',
        )
        self.env.statbox.bind_entry(
            'local_base_with_uid',
            _inherit_from='local_base',
            uid=str(TEST_UID),
            login=TEST_USER_LOGIN_NORMALIZED,
        )
        self.env.statbox.bind_entry(
            'account_modification_base',
            event='account_modification',
            uid=str(TEST_UID),
            consumer='dev',
            ip=TEST_USER_IP,
            user_agent='curl',
            operation='created',
        )
        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from='account_modification_base',
            old='-',
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'account_modification_karma',
            _inherit_from='account_modification_base',
            entity='karma',
            action='account_register',
            destination='frodo',
            old='-',
            new='0',
            suid=str(TEST_SUID),
            login=TEST_USER_LOGIN_NORMALIZED,
            registration_datetime=DatetimeNow(convert_to_datetime=True),
        )
        self.env.statbox.bind_entry(
            'account_modification_subscription_2',
            _inherit_from='account_modification_base',
            entity='subscriptions',
            operation='added',
            sid='2',
            suid=str(TEST_SUID),
        )
        self.env.statbox.bind_entry(
            'account_modification_subscription_8',
            _inherit_from='account_modification_base',
            entity='subscriptions',
            operation='added',
            sid='8',
        )
        self.env.statbox.bind_entry(
            'account_modification_subscription_669',
            _inherit_from='account_modification_base',
            entity='subscriptions',
            operation='added',
            sid='669',
        )
        self.env.statbox.bind_entry(
            'account_modification_subscription_23',
            _inherit_from='account_modification_base',
            entity='subscriptions',
            operation='added',
            sid='23',
        )
        self.env.statbox.bind_entry(
            'account_modification_subscription_24',
            _inherit_from='account_modification_base',
            entity='subscriptions',
            operation='added',
            sid='24',
        )
        self.env.statbox.bind_entry(
            'account_modification_subscription_100',
            _inherit_from='account_modification_base',
            entity='subscriptions',
            operation='added',
            sid='100',
        )
        self.env.statbox.bind_entry(
            'account_created',
            _inherit_from='local_base_with_uid',
            action='account_created',
            country='tr',
            karma='0',
            password_quality=str(TEST_USER_PASSWORD_QUALITY),
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'email_validation_get_key',
            _inherit_from='local_base',
            _exclude=['user_agent'],
            action='get_key',
            mode='email_validation',
            uid=str(TEST_UID),
            host=TEST_HOST,
            email=mask_email_for_statbox(TEST_EMAIL),
        )
        self.env.statbox.bind_entry(
            'email_validation_confirm',
            _inherit_from='local_base',
            _exclude=['user_agent'],
            action='confirmed',
            mode='email_validation',
            uid=str(TEST_UID),
        )

    def assert_db_clear(self):
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def assert_db_ok(self, centraldb_queries=4, sharddb_queries=1,
                     karma=0, is_enabled=1, is_password_passed=True,
                     email_created=False):
        eq_(self.env.db.query_count('passportdbcentral'), centraldb_queries)
        eq_(self.env.db.query_count('passportdbshard1'), sharddb_queries)

        self.env.db.check_db_attr(TEST_UID, 'account.registration_datetime', TimeNow())

        self.env.db.check('aliases', 'portal', TEST_USER_LOGIN_NORMALIZED, uid=1, db='passportdbcentral')

        self.env.db.check_db_attr(TEST_UID, 'account.user_defined_login', TEST_USER_LOGIN)
        if is_password_passed:
            self.env.db.check_db_attr(TEST_UID, 'password.update_datetime', TimeNow())
            self.env.db.check_db_attr(TEST_UID, 'password.quality', '3:%s' % TEST_USER_PASSWORD_QUALITY)
            eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=1, db='passportdbshard1')
            if self.is_password_hash_from_blackbox:
                eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
            else:
                eq_(len(eav_pass_hash), 36)
                ok_(eav_pass_hash.startswith('%s:' % self.password_hash_version))
        else:
            self.env.db.check_db_attr_missing(TEST_UID, 'password.update_datetime')
            self.env.db.check_db_attr_missing(TEST_UID, 'password.quality')
            self.env.db.check_db_attr_missing(TEST_UID, 'password.encrypted')
            self.env.db.check_db_attr(TEST_UID, 'password.is_creating_required', '1')

        self.env.db.check_db_attr(TEST_UID, 'person.firstname', TEST_USER_FIRSTNAME)
        self.env.db.check_db_attr(TEST_UID, 'person.lastname', TEST_USER_LASTNAME)
        self.env.db.check_db_attr(TEST_UID, 'person.gender', TEST_USER_GENGER)
        self.env.db.check_db_attr(TEST_UID, 'person.birthday', TEST_USER_BIRTHDAY)
        self.env.db.check_db_attr(TEST_UID, 'person.country', TEST_USER_COUNTRY.lower())
        self.env.db.check_db_attr(TEST_UID, 'person.timezone', TEST_USER_TIMEZONE)
        # default city = None
        self.env.db.check_db_attr_missing(TEST_UID, 'person.city')
        # ru = default language
        self.env.db.check_db_attr_missing(TEST_UID, 'person.language')

        if karma:
            self.env.db.check_db_attr(TEST_UID, 'karma.value', str(karma))
        else:
            self.env.db.check_db_attr_missing(TEST_UID, 'karma.value')

        if not is_enabled:
            self.env.db.check_db_attr(TEST_UID, 'account.is_disabled', '1')
        else:
            self.env.db.check_db_attr_missing(TEST_UID, 'account.is_disabled')
        self.env.db.check_db_attr_missing(TEST_UID, 'hint.question.serialized')
        self.env.db.check_db_attr_missing(TEST_UID, 'hint.answer.encrypted')

    def assert_historydb_ok(self, is_password_passed=True,
                            email_created=False, **kwargs):
        events = {
            'action': 'account_create',
            'alias.portal.add': TEST_USER_LOGIN_NORMALIZED,
            'consumer': 'dev',
            'user_agent': 'curl',
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
            'info.lang': 'ru',
            'info.reg_date': DatetimeNow(convert_to_datetime=True),
            'mail.add': '1',
            'sid.add': '8|%s,2' % TEST_USER_LOGIN,
            'info.mail_status': '1',
            'info.karma': '0',
            'info.karma_full': '0',
            'info.karma_prefix': '0',
        }

        if is_password_passed:
            eav_pass_hash = self.env.db.get(
                'attributes',
                'password.encrypted',
                uid=TEST_UID,
                db='passportdbshard1',
            )
            events.update({
                'info.password_quality': str(TEST_USER_PASSWORD_QUALITY),
                'info.password': eav_pass_hash,
                'info.password_update_time': TimeNow(),
            })
        else:
            events.update({
                'sid.add': '8|%s,2,100' % TEST_USER_LOGIN,
            })

        events = merge_dicts(events, kwargs)

        if email_created:
            now = TimeNow()
            events.update({
                'email.1': 'created',
                'email.1.address': TEST_EMAIL,
                'email.1.confirmed_at': now,
                'email.1.bound_at': now,
                'email.1.created_at': now,
                'email.1.is_unsafe': '0',
            })

        events = [{'name': k, 'value': v} for k, v in events.items()]

        self.assert_events_are_logged(self.env.handle_mock, events)

    def assert_response_without_grants(self, rv, grant):
        self.assert_error_response(rv, ['access.denied'], status_code=403)
        response = json.loads(rv.data)
        message = 'Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: None. Required grants: %r' % grant
        eq_(
            response['error_message'],
            message,
            [rv.data, message],
        )

    def assert_frodo_ok(self, call_count=1, **kwargs):
        requests = self.env.frodo.requests
        eq_(len(requests), call_count)
        requests[0].assert_query_equals(self.get_expected_frodo_params(**kwargs))

    def assert_track_ok(self, is_password_passed=True):
        track = self.track_manager.read(self.track_id)
        eq_(track.allow_authorization, False)
        eq_(track.allow_oauth_authorization, False)
        eq_(track.uid, str(TEST_UID))
        eq_(track.login, TEST_USER_LOGIN)
        eq_(track.human_readable_login, TEST_USER_LOGIN)
        eq_(track.machine_readable_login, TEST_USER_LOGIN_NORMALIZED)
        eq_(track.is_password_passed, True)
        eq_(track.language, TEST_USER_LANGUAGE)
        eq_(track.have_password, is_password_passed)
        eq_(track.is_successful_registered, True)

    def assert_historydb_clear(self):
        self.assert_events_are_empty(self.env.handle_mock)

    def assert_statbox_clear(self):
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def assert_email_validator_called(self, call_count=2):
        pass

    def test_without_need_headers(self):
        rv = self.make_request(self.query_params(), {})
        self.assert_error_response(rv, ['ip.empty', 'useragent.empty'])
        self.assert_db_clear()
        self.assert_historydb_clear()
        self.assert_statbox_clear()

    def test_frodo_call(self):
        self.env.frodo.set_response_value(
            u'check',
            '<spamlist><spam_user login="%s" weight="85" /></spamlist>' % (
                TEST_USER_LOGIN_NORMALIZED,
            ),
        )
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_db_ok(sharddb_queries=2, karma=85)
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '85')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '85')
        self.assert_statbox_ok(karma=85)
        self.assert_track_ok()
        self.assert_frodo_ok(call_count=2)

    def test_frodo_error(self):
        self.env.frodo.set_response_side_effect(u'check', FrodoError('Failed'))

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_track_ok()

        self.assert_frodo_ok()

        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '0')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '0')

    @parameterized.expand(['firstname', 'lastname'])
    def test_fraud(self, field):
        rv = self.make_request(
            self.query_params(**{field: u'Заходи дорогой, гостем будешь диваны.рф'}),
            build_headers(),
        )
        self.assert_error_response(rv, ['{}.invalid'.format(field)])

    def test_ok(self):
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_track_ok()
        self.assert_frodo_ok()

    def test_yastaff_login(self):
        rv = self.make_request(self.query_params(yastaff_login='staff_login'), build_headers())
        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_db_ok(centraldb_queries=4)
        self.assert_historydb_ok(
            **{'alias.yandexoid.add': 'staff_login'}
        )
        self.assert_statbox_ok(yastaff=True)
        self.assert_track_ok()
        self.assert_frodo_ok()

        self.env.db.check('aliases', 'yandexoid', 'staff_login', uid=1, db='passportdbcentral')

    def test_yastaff_login_not_available(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=1),
        )
        rv = self.make_request(self.query_params(yastaff_login='staff_login'), build_headers())

        self.assert_error_response(rv, ['yastaff_login.notavailable'])
        self.assert_db_clear()
        self.assert_historydb_clear()
        self.assert_statbox_submitted()

    def test_is_creating_required(self):
        rv = self.make_request(self.query_params(is_creating_required='1'), build_headers())
        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_db_ok()
        self.assert_historydb_ok(
            **{'sid.add': '8|%s,2,100' % TEST_USER_LOGIN}
        )
        self.assert_statbox_ok(is_creating_required=True)
        self.assert_track_ok()
        self.assert_frodo_ok()

    def test_is_enabled(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'account': ['create', 'is_enabled'],
                    'ignore_stoplist': ['*'],
                },
            ),
        )
        rv = self.make_request(
            self.query_params(is_enabled='0'),
            build_headers(),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_db_ok(is_enabled=0)
        self.assert_historydb_ok(
            **{'info.ena': '0', 'info.disabled_status': '1'}
        )
        self.assert_statbox_ok(is_enabled=False)
        self.assert_track_ok()
        self.assert_frodo_ok()

        self.env.db.check_db_attr(TEST_UID, 'account.is_disabled', '1')

    def test_ignore_stoplist(self):
        rv = self.make_request(self.query_params(ignore_stoplist='1'), build_headers())

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_track_ok()
        self.assert_frodo_ok()
        self.env.blackbox.requests[0].assert_query_contains(dict(logins=TEST_USER_LOGIN, ignore_stoplist='1'))

    def test_subscriptions(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'account': ['create'],
                    'subscription': {'lenta': ['*'], 'partner': ['*']},
                },
            ),
        )
        sids = [23, 24]
        rv = self.make_request(
            self.query_params(
                subscriptions=','.join(map(str, sids)),
            ),
            build_headers(),
        )
        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_db_ok()
        self.assert_historydb_ok(
            **{'sid.add': '8|%s,24,2,23' % TEST_USER_LOGIN}
        )
        self.assert_statbox_ok(subscriptions=True)
        self.assert_track_ok()
        self.assert_frodo_ok()

        for sid in sids:
            self.env.db.check_db_attr(TEST_UID, 'subscription.%s' % sid, '1')

    def test_with_track_registration_already_completed_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_successful_registered = True

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )
        self.assert_error_response(rv, ['account.already_registered'])
        self.assert_db_clear()
        self.assert_historydb_clear()
        self.assert_statbox_submitted()

    def test_invalid_password_error(self):
        invalid_password_args = [
            (
                '.',
                ['password.short'],
            ),
            (
                TEST_USER_LOGIN,
                ['password.likelogin'],
            ),
            (
                'aaabbb',
                ['password.weak'],
            ),
        ]

        for password, expected_errors in invalid_password_args:
            rv = self.make_request(
                self.query_params(password=password),
                build_headers(),
            )

            self.assert_error_response(rv, expected_errors)
            self.assert_db_clear()
            self.assert_historydb_clear()

    def test_without_grant_ignore_stoplist(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['create']}))
        rv = self.make_request(
            self.query_params(ignore_stoplist='1'),
            build_headers(),
        )

        self.assert_response_without_grants(rv, ['ignore_stoplist'])
        self.assert_db_clear()
        self.assert_historydb_clear()
        self.assert_statbox_submitted()

    def test_without_grant_is_enabled(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['create']}))
        rv = self.make_request(
            self.query_params(is_enabled='0'),
            build_headers(),
        )

        self.assert_response_without_grants(rv, ['account.is_enabled'])
        self.assert_db_clear()
        self.assert_historydb_clear()
        self.assert_statbox_submitted()

    def test_without_grant_subscriptions(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['create']}))
        rv = self.make_request(
            self.query_params(subscriptions='23,24'),
            build_headers(),
        )

        self.assert_response_without_grants(rv, ['subscription.create.partner', 'subscription.create.lenta'])
        self.assert_db_clear()
        self.assert_historydb_clear()
        self.assert_statbox_submitted()

    def test_without_not_required_grant_is_enabled(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['create']}))
        rv = self.make_request(
            self.query_params(is_enabled='1'),
            build_headers(),
        )
        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_track_ok()
        self.assert_frodo_ok()

    def test_without_grant_recovery_email(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['create']}))
        rv = self.make_request(
            self.query_params(email=TEST_EMAIL),
            build_headers(),
        )
        self.assert_response_without_grants(rv, ['account.recovery_email'])
        self.assert_db_clear()
        self.assert_historydb_clear()
        self.assert_statbox_submitted()

    def test_invalid_email_error(self):
        rv = self.make_request(
            self.query_params(email='test'),
            build_headers(),
        )

        self.assert_error_response(rv, ['email.invalid'])
        self.assert_db_clear()
        self.assert_historydb_clear()
        self.assert_statbox_submitted()

    def test_email_ok(self):
        rv = self.make_request(
            self.query_params(email=TEST_EMAIL),
            build_headers(),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_db_ok(
            centraldb_queries=5,
            sharddb_queries=3,
            email_created=True,
        )
        self.assert_historydb_ok(email_created=True)
        self.assert_statbox_ok(email=True)
        self.assert_track_ok()
        self.assert_frodo_ok(email=TEST_EMAIL)
        self.assert_email_validator_called()

    def test_password_not_passed(self):
        rv = self.make_request(
            self.query_params(
                email=TEST_EMAIL,
                password=None,
            ),
            build_headers(),
        )
        self.assert_ok_response(rv, uid=TEST_UID)

        eq_(self.generate_persistent_track_mock.call_count, 1)

        emails = [
            {
                'language': 'ru',
                'addresses': [TEST_EMAIL],
                'subject': 'digitreg.subject',
                'tanker_keys': {
                    'greeting': {'FIRST_NAME': TEST_USER_FIRSTNAME},
                    'register.complete_account_by_key_email_message.notice': {
                        'LOGIN': TEST_USER_LOGIN,
                    },
                    'register.complete_account_by_key_email_message.completion': {
                        'COMPLETE_ACCOUNT_BY_KEY_LINK': 'AUTH_BY_KEY_LINK_TEMPLATE_URL?key=%(key)s&tld=ru' % dict(
                            key=TEST_PERSISTENT_TRACK_KEY,
                        ),
                    },
                    'register.complete_account_by_key_email_message.restoration': {
                        'RESTORATION_URL': 'RESTORE_DEFAULT_URL_TEMPLATE?tld=ru',
                    },
                },
            },
        ]
        self.assert_emails_sent(emails)
        self.assert_db_ok(
            centraldb_queries=5,
            sharddb_queries=4,
            is_password_passed=False,
            email_created=True,
        )
        self.assert_historydb_ok(
            is_password_passed=False,
            email_created=True,
        )
        self.assert_statbox_ok(
            is_password_passed=False,
            is_creating_required=True,
            email=True,
        )
        self.assert_track_ok(is_password_passed=False)
        self.assert_frodo_ok(
            email=TEST_EMAIL,
            passwd=u'0.0.0.0.0.0.0.0',
            passwdex=u'0.0.0.0.0.0.0.0',
            v2_password_quality=u'',
        )
        self.assert_email_validator_called(call_count=2)


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAccountCreateNoBlackboxHash(TestAccountCreate):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
