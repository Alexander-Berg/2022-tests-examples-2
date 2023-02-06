# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test import StatboxTestMixin
from passport.backend.api.tests.views.bundle.register.test.base_test_data import (
    TEST_PASSWORD_QUALITY,
    TEST_RETPATH,
    TEST_SERIALIZED_PASSWORD,
    TEST_SUID,
    TEST_USER_AGENT,
    TEST_USER_IP,
    TEST_USER_LOGIN,
    TEST_USER_LOGIN_NORMALIZED,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
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
from passport.backend.utils.common import merge_dicts


def build_headers():
    return mock_headers(
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
    )


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
)
class TestAccountRegisterByMiddleman(BaseTestViews,
                                     StatboxTestMixin):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['register_by_middleman']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
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
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def account_register_request(self, data, headers):
        return self.env.client.post(
            '/1/bundle/account/register/by_middleman/?consumer=dev',
            data=data,
            headers=headers,
        )

    def query_params(self, **kwargs):
        base_params = {
            'login': TEST_USER_LOGIN,
            'password': 'aaa1bbbccc',
            'firstname': 'firstname',
            'lastname': 'lastname',
            'country': 'ru',
            'language': 'ru',
        }
        return merge_dicts(base_params, kwargs)

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='register_by_middleman',
        )
        super(TestAccountRegisterByMiddleman, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'account_created',
            _exclude=[
                'ip',
                'is_suggested_login',
                'suggest_generation_number',
            ],
        )
        self.env.statbox.bind_entry(
            'reg_by_middleman',
            login=TEST_USER_LOGIN_NORMALIZED,
            old_karma='0',
            new_karma='1',
            user_ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            suid=str(TEST_SUID),
            action='reg_by_middleman',
        )

    def assert_statbox_ok(self, **account_created_kwargs):
        entries = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
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
        ]
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
                sid='100',
            ),
        ])
        if account_created_kwargs.get('karma'):
            entries.append(self.env.statbox.entry('reg_by_middleman'))
        entries.append(
            self.env.statbox.entry(
                'account_created',
                **account_created_kwargs
            ),
        )
        self.env.statbox.assert_has_written(entries)

    def test_already_registered(self):
        rv = self.account_register_request(
            self.query_params(track_id=self.track_id),
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
            self.query_params(track_id=self.track_id),
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

    def test_successful_register(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        timenow = TimeNow()

        rv = self.account_register_request(
            self.query_params(track_id=self.track_id),
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

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.user_defined_login', TEST_USER_LOGIN, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.firstname', 'firstname', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.lastname', 'lastname', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.quality', '3:80', uid=1, db='passportdbshard1')
        # Почтовый логин совпадает с portal => не создается aliases.mail
        self.env.db.check_missing('aliases', 'mail', uid=1, db='passportdbcentral')
        self.env.db.check_missing('attributes', 'subscription.mail.login_rule', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.display_name', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.gender', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.birthday', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.country', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.city', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.language', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.timezone', uid=1, db='passportdbshard1')

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
                {'name': 'info.password_update_time', 'value': timenow},
                {'name': 'info.karma_prefix', 'value': '0'},
                {'name': 'info.karma_full', 'value': '0'},
                {'name': 'info.karma', 'value': '0'},
                {'name': 'alias.portal.add', 'value': 'test-login'},
                {'name': 'mail.add', 'value': '1'},
                {'name': 'sid.add', 'value': '8|%s,2,100' % TEST_USER_LOGIN},
                {'name': 'action', 'value': 'account_register'},
                {'name': 'consumer', 'value': 'dev'},
                {'name': 'user_agent', 'value': 'curl'},
            ],
        )

        self.assert_statbox_ok(retpath=TEST_RETPATH)

        track = self.track_manager.read(self.track_id)
        eq_(track.uid, '1')
        eq_(track.login, TEST_USER_LOGIN)
        eq_(track.human_readable_login, TEST_USER_LOGIN)
        eq_(track.machine_readable_login, TEST_USER_LOGIN_NORMALIZED)

        eq_(track.have_password, True)
        eq_(track.is_successful_registered, True)
        eq_(track.allow_authorization, False)
        eq_(track.allow_oauth_authorization, False)

    def test_register_without_track(self):
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

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAccountRegisterByMiddlemanNoBlackboxHash(TestAccountRegisterByMiddleman):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
