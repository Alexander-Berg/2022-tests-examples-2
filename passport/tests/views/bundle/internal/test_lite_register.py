# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_loginoccupation_response,
)
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import merge_dicts


TEST_USER_IP = '37.9.101.188'

TEST_USER_LOGIN = 'testlogin@moikrug.ru'

TEST_NOT_AVAILABLE_LOGIN = 'user@moikrug.ru'


def build_headers():
    return mock_headers(
        user_ip=TEST_USER_IP,
    )


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
)
class TestLiteAccountRegister(BaseTestViews):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'internal': ['register_lite']}))
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(
                {
                    TEST_USER_LOGIN: 'free',
                    TEST_NOT_AVAILABLE_LOGIN: 'occupied',
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def account_register_request(self, data, headers):
        return self.env.client.post(
            '/1/bundle/test/register_lite/?consumer=dev',
            data=data,
            headers=headers,
        )

    def query_params(self, **kwargs):
        base_params = {
            'login': TEST_USER_LOGIN,
            'password': 'aaa1bbbccc',
        }
        return merge_dicts(base_params, kwargs)

    def test_empty_request(self):
        rv = self.account_register_request({}, {})

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['ip.empty'],
            },
        )

    def test_not_lite_login(self):
        rv = self.account_register_request(
            self.query_params(login='username'),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['login.invalid'],
            },
        )

    def test_native_login(self):
        rv = self.account_register_request(
            self.query_params(login='username@yandex.ru'),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['login.native'],
            },
        )

    def test_login_not_available(self):
        rv = self.account_register_request(
            self.query_params(login=TEST_NOT_AVAILABLE_LOGIN),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['login.notavailable'],
            },
        )

    def test_password_too_weak(self):
        rv = self.account_register_request(
            self.query_params(password='123456'),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['password.weak'],
            },
        )

    def test_successful_register(self):
        timenow = TimeNow()

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

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check('aliases', 'lite', TEST_USER_LOGIN, uid=1, db='passportdbcentral')
        self.env.db.check_missing('attributes', 'account.user_defined_login', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.quality', '3:80', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.firstname', TEST_USER_LOGIN, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.lastname', TEST_USER_LOGIN, uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.gender', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.birthday', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.timezone', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.city', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.language', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.country', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.display_name', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=1, db='passportdbshard1')
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('%s:' % self.password_hash_version))

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            [
                {'name': 'info.login', 'value': TEST_USER_LOGIN},
                {'name': 'info.ena', 'value': '1'},
                {'name': 'info.disabled_status', 'value': '0'},
                {'name': 'info.reg_date', 'value': DatetimeNow(convert_to_datetime=True)},
                {'name': 'info.firstname', 'value': TEST_USER_LOGIN},
                {'name': 'info.lastname', 'value': TEST_USER_LOGIN},
                {'name': 'info.country', 'value': 'ru'},
                {'name': 'info.tz', 'value': 'Europe/Moscow'},
                {'name': 'info.lang', 'value': 'ru'},
                {'name': 'info.password', 'value': eav_pass_hash},
                {'name': 'info.password_quality', 'value': '80'},
                {'name': 'info.password_update_time', 'value': TimeNow()},
                {'name': 'info.karma_prefix', 'value': '0'},
                {'name': 'info.karma_full', 'value': '0'},
                {'name': 'info.karma', 'value': '0'},
                {'name': 'alias.lite.add', 'value': TEST_USER_LOGIN},
                {'name': 'sid.add', 'value': '8|%s,33' % TEST_USER_LOGIN},
                {'name': 'action', 'value': 'account_register_lite'},
                {'name': 'consumer', 'value': 'dev'},
            ],
        )

    @parameterized.expand(
        [
            ('first', 'second', 'first', 'second'),
            ('', None, None, TEST_USER_LOGIN),
            (None, '', TEST_USER_LOGIN, None),
        ]
    )
    def test_ok_with_names(self, firstname, lastname, expected_db_firstname, expected_db_lastname):
        rv = self.account_register_request(
            self.query_params(firstname=firstname, lastname=lastname),
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

        self.env.db.check('attributes', 'person.firstname', expected_db_firstname, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.lastname', expected_db_lastname, uid=1, db='passportdbshard1')


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestLiteAccountRegisterNoBlackboxHash(TestLiteAccountRegister):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
