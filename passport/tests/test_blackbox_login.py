# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.blackbox import (
    AccessDenied,
    Blackbox,
    BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
    BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS,
    BLACKBOX_LOGIN_DISABLED_STATUS,
    BLACKBOX_LOGIN_NOT_FOUND_STATUS,
    BLACKBOX_LOGIN_UNKNOWN_STATUS,
    BLACKBOX_LOGIN_V1_INVALID_STATUS,
    BLACKBOX_LOGIN_V1_SECOND_STEP_REQUIRED_STATUS,
    BLACKBOX_LOGIN_V1_VALID_STATUS,
    BLACKBOX_LOGIN_VALID_STATUS,
    BLACKBOX_PASSWORD_BAD_STATUS,
    BLACKBOX_PASSWORD_COMPROMISED_STATUS,
    BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
    BLACKBOX_PASSWORD_UNKNOWN_STATUS,
    BLACKBOX_PASSWORD_VALID_STATUS,
)
from passport.backend.core.builders.blackbox.constants import SECURITY_IDENTITY
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_build_badauth_counts,
    blackbox_login_response,
    FakeBlackbox,
)
from passport.backend.core.eav_type_mapping import (
    ATTRIBUTE_NAME_TO_TYPE as AT,
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.time_utils.time_utils import unixtime
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import TEST_TICKET
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
    TestPhoneArguments,
)


@with_settings(
    BLACKBOX_URL='http://localhost/',
    BLACKBOX_ATTRIBUTES=[],
)
class TestBlackboxRequestLoginParse(BaseBlackboxRequestTestCase):
    def test_login_basic(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111114533",
                "hosted" : false,
                "lite" : false
            },
            "password_status" : {
                "value" : "%s",
                "id" : 1
            },
            "karma" : {
                "value" : 85,
                "allow-until" : 1377784338
            },
            "login" : "scullyx13-test22",
            "aliases": {
                "1": "scullyx13-test22",
                "6": "uid-sjywgxrn"
            },
            "comment" : "OK",
            "karma_status" : {
                "value" : 85
            },
            "login_status" : {
                "value" : "%s",
                "id" : 1
            }
        }
        ''' % (BLACKBOX_PASSWORD_VALID_STATUS, BLACKBOX_LOGIN_VALID_STATUS))

        response = self.blackbox.login('pass', '127.0.0.1', uid=1)
        eq_(response['login_status'], BLACKBOX_LOGIN_VALID_STATUS)
        eq_(response['password_status'], BLACKBOX_PASSWORD_VALID_STATUS)
        eq_(response['bruteforce_status'], None)
        ok_('bruteforce_policy' not in response)

        eq_(response['uid'], 111114533)
        eq_(response['login'], 'scullyx13-test22')
        eq_(response['aliases'], {'1': 'scullyx13-test22', '6': 'uid-sjywgxrn'})
        eq_(response['lite'], False)
        eq_(response['hosted'], False)
        eq_(response['karma'], 85)
        eq_(response['domid'], None)
        eq_(response['domain'], None)

    def test_login_version_1(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111114533",
                "hosted" : false,
                "lite" : false
            },
            "status" : {
                "value" : "%s",
                "id" : 1
            },
            "karma" : {
                "value" : 85,
                "allow-until" : 1377784338
            },
            "login" : "scullyx13-test22",
            "aliases": {
                "1": "scullyx13-test22",
                "6": "uid-sjywgxrn"
            },
            "comment" : "OK",
            "karma_status" : {
                "value" : 85
            }
        }
        ''' % BLACKBOX_LOGIN_V1_VALID_STATUS)

        response = self.blackbox.login('pass', '127.0.0.1', uid=1, version=1)
        eq_(response['status'], BLACKBOX_LOGIN_V1_VALID_STATUS)

        eq_(response['uid'], 111114533)
        eq_(response['login'], 'scullyx13-test22')
        eq_(response['aliases'], {'1': 'scullyx13-test22', '6': 'uid-sjywgxrn'})
        eq_(response['lite'], False)
        eq_(response['hosted'], False)
        eq_(response['karma'], 85)
        eq_(response['domid'], None)
        eq_(response['domain'], None)

    def test_login_version_1_is_disabled_always_there(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111114533",
                "hosted" : false,
                "lite" : false
            },
            "status" : {
                "value" : "%s",
                "id" : 1
            },
            "karma" : {
                "value" : 85,
                "allow-until" : 1377784338
            },
            "login" : "scullyx13-test22",
            "aliases": {
                "1": "scullyx13-test22",
                "6": "uid-sjywgxrn"
            },
            "comment" : "OK",
            "karma_status" : {
                "value" : 85
            },
            "attributes": {}
        }
        ''' % BLACKBOX_LOGIN_V1_VALID_STATUS)
        response = self.blackbox.login('pass', '127.0.0.1', uid=1, version=1)
        ok_(str(AT['account.is_disabled']) not in response['attributes'])

        response = self.blackbox.login(
            'pass',
            '127.0.0.1',
            uid=1,
            version=1,
            attributes=[
                'account.is_disabled',
            ],
        )
        eq_(response['attributes'][str(AT['account.is_disabled'])], '0')

    def test_login_with_captcha_bruteforce_policy(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111114533",
                "hosted" : false,
                "lite" : false
            },
            "password_status" : {
                "value" : "%s",
                "id" : 1
            },
            "karma" : {
                "value" : 85,
                "allow-until" : 1377784338
            },
            "login" : "scullyx13-test22",
            "comment" : "OK",
            "karma_status" : {
                "value" : 85
            },
            "login_status" : {
                "value" : "%s",
                "id" : 1
            },
           "bruteforce_policy" :
           {
                "value" : "captcha",
                "level" : "0"
           }
        }
        ''' % (BLACKBOX_PASSWORD_VALID_STATUS, BLACKBOX_LOGIN_VALID_STATUS))
        response = self.blackbox.login('pass', '127.0.0.1', uid=1)
        eq_(response['login_status'], BLACKBOX_LOGIN_VALID_STATUS)
        eq_(response['password_status'], BLACKBOX_PASSWORD_VALID_STATUS)
        eq_(response['bruteforce_status'], BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS)
        eq_(response['bruteforce_policy']['value'], BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS)
        eq_(response['bruteforce_policy']['level'], '0')

        eq_(response['uid'], 111114533)

    def test_login_with_password_bruteforce_policy(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111114533",
                "hosted" : false,
                "lite" : false
            },
            "password_status" : {
                "value" : "%s",
                "id" : 1
            },
            "karma" : {
                "value" : 85,
                "allow-until" : 1377784338
            },
            "login" : "scullyx13-test22",
            "comment" : "OK",
            "karma_status" : {
                "value" : 85
            },
            "login_status" : {
                "value" : "%s",
                "id" : 1
            },
           "bruteforce_policy" :
           {
                "value" : "password_expired"
           }
        }
        ''' % (BLACKBOX_PASSWORD_VALID_STATUS, BLACKBOX_LOGIN_VALID_STATUS))
        response = self.blackbox.login('pass', '127.0.0.1', uid=1)
        eq_(response['login_status'], BLACKBOX_LOGIN_VALID_STATUS)
        eq_(response['password_status'], BLACKBOX_PASSWORD_VALID_STATUS)
        eq_(response['bruteforce_status'], BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS)
        eq_(response['bruteforce_policy']['value'], BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS)

        eq_(response['uid'], 111114533)

    def test_login_with_dbfields(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111114533",
                "hosted" : false,
                "lite" : false
            },
            "password_status" : {
                "value" : "%s",
                "id" : 1
            },
            "karma" : {
                "value" : 85,
                "allow-until" : 1377784338
            },
            "login" : "scullyx13-test22",
            "comment" : "OK",
            "karma_status" : {
                "value" : 85
            },
            "login_status" : {
                "value" : "%s",
                "id" : 1
            },
            "dbfields" : {
               "accounts.ena.uid": "1",
               "subscription.login.8": "scullyx13-test22",
               "subscription.login_rule.8": "1",
               "subscription.suid.8": "544793454",
               "userinfo.sex.uid": "0",
               "password_quality.quality.uid": "50",
               "password_quality.version.uid": "2"
            },
            "display_name" : {
               "name" : ""
            }
        }
        ''' % (BLACKBOX_PASSWORD_VALID_STATUS, BLACKBOX_LOGIN_VALID_STATUS))
        response = self.blackbox.login('pass', '127.0.0.1', uid=1)
        eq_(response['login_status'], BLACKBOX_LOGIN_VALID_STATUS)
        eq_(response['password_status'], BLACKBOX_PASSWORD_VALID_STATUS)

        eq_(response['uid'], 111114533)
        eq_(response['accounts.ena.uid'], 1)
        eq_(
            response['subscriptions'],
            {
                8: {'sid': 8, 'suid': 544793454, 'login': 'scullyx13-test22',
                    'login_rule': 1},
            },
        )
        eq_(response['display_name']['name'], '')
        eq_(response['userinfo.sex.uid'], 0)
        eq_(response['password_quality.quality.uid'], 50)
        eq_(response['password_quality.version.uid'], 2)

    def test_login_not_found_with_unknown_password(self):
        self.set_blackbox_response_value('''
        {
            "comment" : "Login not found",
            "password_status" : {
                "value" : "%s",
                "id" : 0
            },
            "login_status" : {
                "value" : "%s",
                "id" : 3
            }
        }
        ''' % (BLACKBOX_PASSWORD_UNKNOWN_STATUS, BLACKBOX_LOGIN_NOT_FOUND_STATUS))
        response = self.blackbox.login('pass', '127.0.0.1', uid=1)
        eq_(response['login_status'], BLACKBOX_LOGIN_NOT_FOUND_STATUS)
        eq_(response['password_status'], BLACKBOX_PASSWORD_UNKNOWN_STATUS)

    def test_login_v1_invalid(self):
        self.set_blackbox_response_value('''
        {
            "error": "Bad password",
            "status" : {
                "value" : "%s",
                "id" : 0
            }
        }
        ''' % BLACKBOX_LOGIN_V1_INVALID_STATUS)
        response = self.blackbox.login('pass', '127.0.0.1', uid=1, version=1)
        eq_(response['status'], BLACKBOX_LOGIN_V1_INVALID_STATUS)
        ok_('login_status' not in response)
        ok_('password_status' not in response)

    def test_login_disabled(self):
        self.set_blackbox_response_value('''
        {
            "comment" : "Account disabled",
            "password_status" : {
                "value" : "%s",
                "id" : 1
            },
            "login_status" : {
                "value" : "%s",
                "id" : 4
            },
            "uid": {
                "value": 1
            }
        }
        ''' % (BLACKBOX_PASSWORD_VALID_STATUS, BLACKBOX_LOGIN_DISABLED_STATUS))
        response = self.blackbox.login('pass', '127.0.0.1', uid=1)
        eq_(response['login_status'], BLACKBOX_LOGIN_DISABLED_STATUS)
        eq_(response['password_status'], BLACKBOX_PASSWORD_VALID_STATUS)
        eq_(response['uid'], 1)

    def test_login_unknown(self):
        self.set_blackbox_response_value('''
        {
            "comment" : "Account disabled",
            "password_status" : {
                "value" : "%s",
                "id" : 1
            },
            "login_status" : {
                "value" : "%s",
                "id" : 4
            }
        }
        ''' % (BLACKBOX_PASSWORD_UNKNOWN_STATUS, BLACKBOX_LOGIN_UNKNOWN_STATUS))
        response = self.blackbox.login('pass', '127.0.0.1', uid=1)
        eq_(response['login_status'], BLACKBOX_LOGIN_UNKNOWN_STATUS)
        eq_(response['password_status'], BLACKBOX_PASSWORD_UNKNOWN_STATUS)

    def test_login_with_bad_password(self):
        self.set_blackbox_response_value('''
        {
            "comment" : "Bad password",
            "password_status" : {
                "value" : "%s",
                "id" : 2
            },
            "login_status" : {
                "value" : "%s",
                "id" : 1
            },
            "uid": {
                "value": 1
            }
        }
        ''' % (BLACKBOX_PASSWORD_BAD_STATUS, BLACKBOX_LOGIN_VALID_STATUS))
        response = self.blackbox.login('pass', '127.0.0.1', uid=1)
        eq_(response['login_status'], BLACKBOX_LOGIN_VALID_STATUS)
        eq_(response['password_status'], BLACKBOX_PASSWORD_BAD_STATUS)
        eq_(response['uid'], 1)

    def test_login_with_compromised_password(self):
        self.set_blackbox_response_value('''
        {
            "comment" : "Compromised password",
            "password_status" : {
                "value" : "%s",
                "id" : 3
            },
            "login_status" : {
                "value" : "%s",
                "id" : 1
            },
            "uid": {
                "value": 1
            }
        }
        ''' % (BLACKBOX_PASSWORD_COMPROMISED_STATUS, BLACKBOX_LOGIN_VALID_STATUS))
        response = self.blackbox.login('pass', '127.0.0.1', uid=1)
        eq_(response['login_status'], BLACKBOX_LOGIN_VALID_STATUS)
        eq_(response['password_status'], BLACKBOX_PASSWORD_COMPROMISED_STATUS)
        eq_(response['uid'], 1)

    def test_login_v1_with_second_step_required(self):
        self.set_blackbox_response_value('''
        {
            "error" : "Second step required",
            "status" : {
                "value" : "%s",
                "id" : 7
            },
            "uid": {
                "value": 1
            },
            "allowed_second_steps": "rfc_totp,email_code"
        }
        ''' % BLACKBOX_LOGIN_V1_SECOND_STEP_REQUIRED_STATUS)
        response = self.blackbox.login('pass', '127.0.0.1', uid=1, version=1)
        eq_(response['status'], BLACKBOX_LOGIN_V1_SECOND_STEP_REQUIRED_STATUS)
        eq_(response['allowed_second_steps'], ['rfc_totp', 'email_code'])
        eq_(response['uid'], 1)

    def test_login_v2_with_second_step_required(self):
        self.set_blackbox_response_value('''
        {
            "comment" : "Second step required",
            "password_status" : {
                "value" : "%s",
                "id" : 4
            },
            "login_status" : {
                "value" : "%s",
                "id" : 1
            },
            "uid": {
                "value": 1
            },
            "allowed_second_steps": "rfc_totp,email_code"
        }
        ''' % (BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS, BLACKBOX_LOGIN_VALID_STATUS))
        response = self.blackbox.login('pass', '127.0.0.1', uid=1)
        eq_(response['login_status'], BLACKBOX_LOGIN_VALID_STATUS)
        eq_(response['password_status'], BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS)
        eq_(response['allowed_second_steps'], ['rfc_totp', 'email_code'])
        eq_(response['uid'], 1)

    def test_login_with_totp_last_successful_period(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111114533",
                "hosted" : false,
                "lite" : false
            },
            "password_status" : {
                "value" : "%s",
                "id" : 1
            },
            "login" : "scullyx13-test22",
            "comment" : "OK",
            "karma_status" : {
                "value" : 85
            },
            "login_status" : {
                "value" : "%s",
                "id" : 1
            },
            "totp_check_time": 123
        }
        ''' % (
            BLACKBOX_PASSWORD_VALID_STATUS,
            BLACKBOX_LOGIN_VALID_STATUS,
        ))
        response = self.blackbox.login('pass', '127.0.0.1', uid=1)
        eq_(response['totp_check_time'], 123)

    def test_login_with_family_info(self):
        self.set_blackbox_response_value('''
          {
              "uid" : {
                  "value" : "111114533",
                  "hosted" : false,
                  "lite" : false
              },
              "password_status" : {
                  "value" : "%s",
                  "id" : 1
              },
              "karma" : {
                  "value" : 85,
                  "allow-until" : 1377784338
              },
              "login" : "scullyx13-test22",
              "karma_status" : {
                  "value" : 85
              },
              "login_status" : {
                  "value" : "%s",
                  "id" : 1
              },
              "family_info" : {
                "admin_uid" : "111114533",
                "family_id" : "f1"
              }
          }
          ''' % (BLACKBOX_PASSWORD_VALID_STATUS, BLACKBOX_LOGIN_VALID_STATUS))

        response = self.blackbox.login('pass', '127.0.0.1', uid=1)
        eq_(response['family_info'], {'admin_uid': '111114533', 'family_id': 'f1'})

    def test_badauth_counts(self):
        self.set_blackbox_response_value(blackbox_login_response())

        response = self.blackbox.login('pass', '127.0.0.1', uid=1)

        eq_(response['badauth_counts'], blackbox_build_badauth_counts())

    def test_scholar_session(self):
        self.set_blackbox_response_value(blackbox_login_response(is_scholar_session=True))

        response = self.blackbox.login('pass', '127.0.0.1', uid=1)

        assert response.get('is_scholar_session')

    @raises(AccessDenied)
    def test_blackbox_error_raises_exception(self):
        self.set_blackbox_response_value('''
        {
            "exception" : {
                "value" : "ACCESS_DENIED",
                "id" : 21
            },
            "error" : "BlackBox error: Unconfigured dbfield 'accounts.ena.uid'"
        }
        ''')
        self.blackbox.login('pass', '127.0.0.1', uid=1)


@with_settings(
    BLACKBOX_URL='http://localhost/',
    BLACKBOX_FIELDS=[],
    BLACKBOX_ATTRIBUTES=['account.normalized_login'],
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=[u'number', u'created', u'bound'],
)
class TestBlackboxRequestLoginParams(BaseBlackboxRequestTestCase):
    LOGIN = 'testlogin'
    PASSWORD = 'testpassword'
    IP = '127.0.0.1'

    def setUp(self):
        super(TestBlackboxRequestLoginParams, self).setUp()
        self._phone_tests = TestPhoneArguments(self._build_request_info)

    def login_params(self, exclude=None, **kwargs):
        return self.base_params(
            {
                'aliases': 'all_with_hidden',
                'attributes': '1008',
                'format': 'json',
                'full_info': 'yes',
                'get_badauth_counts': 'yes',
                'get_public_name': 'yes',
                'is_display_name_empty': 'yes',
                'login': self.LOGIN,
                'method': 'login',
                'password': self.PASSWORD,
                'regname': 'yes',
                'userip': self.IP,
                'ver': '2',
            },
            exclude=exclude,
            **kwargs
        )

    def test_login_url(self):
        request_info = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
        )
        eq_(request_info.url, 'http://localhost/blackbox/')

    def test_login_basic(self):
        """Строим запрос к ЧЯ и проверяем что указаны все обязательные поля"""
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
        )

        eq_(data.post_args, self.login_params())
        eq_(data.headers, {})

    def test_login_wo_hidden_aliases(self):
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            get_hidden_aliases=False,
        )

        eq_(data.post_args, self.login_params(aliases='all'))
        eq_(data.headers, {})

    def test_login_version_1(self):
        """Указываем первую версию метода"""
        data = Blackbox().build_login_request(
            version=1,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
        )

        eq_(data.post_args, self.login_params(ver='1'))
        eq_(data.headers, {})

    def test_login_version_1_without_captcha(self):
        """Указываем первую версию метода. Капчу уже проверили"""
        data = Blackbox().build_login_request(
            version=1,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            captcha_already_checked=True,
        )

        eq_(data.post_args, self.login_params(ver='1', captcha='no'))

    def test_login_with_authtype(self):
        """В запросе указываем тип авторизации"""
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            authtype='web',
        )

        eq_(
            data.post_args,
            self.login_params(authtype='web'),
        )

    def test_login_with_dbfields(self):
        """Строим запрос с дополнительными полями из БД ЧЯ"""
        dbfields = ['field1', 'field2']
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            dbfields=dbfields,
        )

        eq_(
            data.post_args,
            self.login_params(dbfields=u','.join(dbfields)),
        )

    def test_login_without_attributes(self):
        """Запрос без доп. атрибутов"""
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            attributes=[],
        )

        eq_(data.post_args, self.login_params(exclude=['attributes']))

    def test_login_with_uid(self):
        """Строим запрос авторизации через uid"""
        uid = '123'
        data = Blackbox().build_login_request(
            version=2,
            uid=uid,
            password=self.PASSWORD,
            ip=self.IP,
        )

        eq_(data.post_args, self.login_params(uid=uid, exclude=['login']))

    def test_login_emails(self):
        """Просим от ЧЯ список email'ов пользователя"""
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            emails=True,
        )

        eq_(data.post_args, self.login_params(emails='getall'))

    def test_login_from_service_by_sid(self):
        """Передаем в ЧЯ sid от сервиса, откуда пришел запрос"""
        sid = 'service'
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            sid=sid,
        )

        eq_(data.post_args, self.login_params(sid=sid))

    def test_login_from_some_service(self):
        """Передаем в ЧЯ информацию о сервисе, откуда пришел запрос - только from"""
        from_service = 'some_service'
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            from_service=from_service,
        )

        eq_(data.post_args, self.login_params(**{'from': from_service}))

    def test_login_with_useragent_referer_retpath(self):
        """Передаем в ЧЯ информацию о браузере пользователя"""
        useragent = 'Mozilla Firefox, you know'
        referer = 'http://yandex.ru/'
        retpath = 'http://mail.yandex.ru/'
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            useragent=useragent,
            referer=referer,
            retpath=retpath,
        )

        eq_(
            data.post_args,
            self.login_params(
                useragent=useragent,
                referer=referer,
                xretpath=retpath,
            ),
        )

    def test_login_with_cookie(self):
        """Укажем ЧЯ что пришли через https"""
        yandexuid = 'abc12345678'
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            yandexuid=yandexuid,
        )

        eq_(
            data.post_args,
            self.login_params(yandexuid=yandexuid),
        )

    def test_login_with_request_email_attributes(self):
        """Запросим дополнительные поля от ЧЯ"""
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            email_attributes='all',
        )

        eq_(
            data.post_args,
            self.login_params(
                getemails='all',
                email_attributes='all',
            ),
        )

    def test_login_with_request_specific_email_attributes(self):
        """Запросим дополнительные поля от ЧЯ"""
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            email_attributes=[
                'address',
                'created',
            ],
        )

        eq_(
            data.post_args,
            self.login_params(
                getemails='all',
                email_attributes=','.join([
                    str(EMAIL_NAME_MAPPING['address']),
                    str(EMAIL_NAME_MAPPING['created']),
                ]),
            ),
        )

    def test_login_without_aliases(self):
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            need_aliases=False,
        )

        eq_(
            data.post_args,
            self.login_params(exclude=['aliases']),
        )

    def test_login_with_idna_domain(self):
        data = Blackbox().build_login_request(
            version=2,
            login=u'test@окна.рф',
            password=self.PASSWORD,
            ip=self.IP,
        )

        eq_(
            data.post_args,
            self.login_params(
                login=u'test@окна.рф',
            ),
        )

    def test_login_with_bad_idna_domain(self):
        data = Blackbox().build_login_request(
            version=2,
            login=u'test@.рф',
            password=self.PASSWORD,
            ip=self.IP,
        )

        eq_(
            data.post_args,
            self.login_params(
                login=u'test@.рф',
            ),
        )

    def test_login_with_totp_secret(self):
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            secret='abcd==',
        )

        eq_(
            data.post_args,
            self.login_params(
                secret='abcd==',
            ),
        )

    def test_login_with_get_user_ticket(self):
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            get_user_ticket=True,
        )

        eq_(
            data.post_args,
            self.login_params(
                get_user_ticket='yes',
            ),
        )
        eq_(
            data.headers,
            {'X-Ya-Service-Ticket': TEST_TICKET},
        )

    def test_login_by_uid_with_get_user_ticket(self):
        uid = 123
        data = Blackbox().build_login_request(
            version=2,
            uid=uid,
            password=self.PASSWORD,
            ip=self.IP,
            get_user_ticket=True,
        )

        eq_(
            data.post_args,
            self.login_params(
                get_user_ticket='yes',
                uid=uid,
                exclude=['login'],
            ),
        )
        eq_(
            data.headers,
            {'X-Ya-Service-Ticket': TEST_TICKET},
        )

    @raises(ValueError)
    def test_login_without_uid_and_login(self):
        """Всегда нужен login или uid"""
        Blackbox().build_login_request(
            version=2,
            password=self.PASSWORD,
            ip=self.IP,
        )

    @raises(TypeError)
    def test_login_without_args(self):
        Blackbox().build_login_request()

    def test_request_phones_is_all_when_phones_arg_value_is_all(self):
        self._phone_tests.assert_request_phones_is_all_when_phones_arg_value_is_all()

    def test_request_has_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_not_empty(self):
        self._phone_tests.assert_request_has_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_not_empty()

    def test_request_has_no_phone_attributes_when_phone_attributes_is_empty(self):
        self._phone_tests.assert_request_has_no_phone_attributes_when_phone_attributes_is_empty()

    def test_request_has_no_phone_attributes_when_phones_is_none_and_phone_attributes_is_not_empty(self):
        self._phone_tests.assert_request_has_no_phone_attributes_when_phones_is_none_and_phone_attributes_is_not_empty()

    def test_request_has_default_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_none(self):
        self._phone_tests.assert_request_has_default_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_none()

    def test_request_get_phone_operations_is_one_when_need_phone_operations_is_true(self):
        self._phone_tests.assert_request_get_phone_operations_is_one_when_need_phone_operations_is_true()

    def test_request_has_no_phone_operations_when_need_phone_operations_is_false(self):
        self._phone_tests.assert_request_has_no_phone_operations_when_need_phone_operations_is_false()

    def test_phone_bindings(self):
        self._phone_tests.test_phone_bindings()

    def test_login_not_pass_find_by_phone_alias(self):
        request_info = self._build_request_info(find_by_phone_alias=None)
        ok_('find_by_phone_alias' not in request_info.post_args)

    def test_login_pass_find_by_phone_alias(self):
        request_info = self._build_request_info(find_by_phone_alias='xyz')
        eq_(request_info.post_args['find_by_phone_alias'], 'xyz')

    def test_login_pass_country(self):
        request_info = self._build_request_info(country='FR')
        eq_(request_info.post_args['country'], 'FR')

    def test_login_with_family_info(self):
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            get_family_info=True,
        )

        eq_(data.post_args, self.login_params(get_family_info='yes'))

    def test_login_public_id(self):
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            get_public_id=True,
        )

        eq_(data.post_args, self.login_params(get_public_id='yes'))

    def test_login_force_show_mail_subscription(self):
        data = Blackbox().build_login_request(
            version=2,
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            force_show_mail_subscription=True,
        )

        eq_(data.post_args, self.login_params(force_show_mail_subscription='yes'))

    def test_get_badauth_counts(self):
        data = self._build_request_info(get_badauth_counts=True)
        eq_(data.post_args, self.login_params(get_badauth_counts='yes'))

        data = self._build_request_info(get_badauth_counts=False)
        eq_(data.post_args, self.login_params(exclude=['get_badauth_counts']))

        data = self._build_request_info()
        eq_(data.post_args, self.login_params(get_badauth_counts='yes'))

    def test_allow_scholar(self):
        data = self._build_request_info(allow_scholar=True)
        assert data.post_args == self.login_params(allow_scholar='yes')

        data = self._build_request_info(allow_scholar=False)
        assert data.post_args == self.login_params()

        data = self._build_request_info()
        assert data.post_args == self.login_params()

    def _build_request_info(self, **kwargs):
        kwargs.setdefault(u'version', 2)
        kwargs.setdefault(u'password', self.PASSWORD)
        kwargs.setdefault(u'ip', self.IP)
        if not (u'uid' in kwargs or u'login' in kwargs):
            kwargs[u'login'] = self.LOGIN
        return Blackbox().build_login_request(**kwargs)


@with_settings(
    BLACKBOX_URL=u'http://bl.ackb.ox/',
    BLACKBOX_ATTRIBUTES=[],
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=[],
)
class RequestTestLoginParsePhones(BaseBlackboxTestCase):
    LOGIN = 'testlogin'
    PASSWORD = 'testpassword'
    IP = '127.0.0.1'

    def setUp(self):
        super(RequestTestLoginParsePhones, self).setUp()
        self._blackbox = Blackbox()
        self._faker = FakeBlackbox()
        self._faker.start()

    def tearDown(self):
        self._faker.stop()
        del self._faker
        super(RequestTestLoginParsePhones, self).tearDown()

    def test_phone_with_empty_attributes_when_response_has_phone_and_empty_attributes(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phones=[{u'id': 22}]),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
            phone_attributes=None,
        )

        eq_(response[u'phones'], {22: {u'id': 22, u'attributes': {}}})

    def test_phone_attribute_phone_number_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(
                phones=[{u'id': 1, u'number': u'+79036655444'}],
            ),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
            phone_attributes=[u'number'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'number'],
            u'+79036655444',
        )

    def test_phone_attribute_created_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(
                phones=[{u'id': 1, u'created': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
            phone_attributes=[u'created'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'created'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_bound_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(
                phones=[{u'id': 1, u'bound': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
            phone_attributes=[u'bound'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'bound'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_confirmed_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(
                phones=[{u'id': 1, u'confirmed': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
            phone_attributes=[u'confirmed'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'confirmed'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_admitted_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(
                phones=[{u'id': 1, u'admitted': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
            phone_attributes=[u'admitted'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'admitted'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_secured_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(
                phones=[{u'id': 1, u'secured': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
            phone_attributes=[u'secured'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'secured'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_is_default_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(
                phones=[{u'id': 1, u'is_default': 1}],
            ),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
            phone_attributes=[u'is_default'],
        )

        ok_(response[u'phones'][1][u'attributes'][u'is_default'])

    def test_operation_id_equals_to_operation_id_from_response(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        ok_(5 in response[u'phone_operations'])
        eq_(response[u'phone_operations'][5][u'id'], 5)

    def test_single_operation_when_response_has_single_operations(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(len(response[u'phone_operations']), 1)

    def test_many_operations_when_response_has_many_operations(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[
                {u'id': 5, u'phone_number': u'+79047766555'},
                {u'id': 6, u'phone_number': u'+79036655444'},
            ]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(len(response[u'phone_operations']), 2)

    def test_operation_phone_id_equals_to_operation_phone_id_from_response(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_id': 7,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id'], 7)

    def test_operation_phone_is_none_when_response_has_not_operation_phone_id(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_id': None,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id'], None)

    def test_operation_security_identity_is_like_phone_number_when_operation_is_not_on_secure_phone_number(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'security_identity'], 79047766555)

    def test_operation_security_identity_is_predefined_value_when_operation_is_on_secure_phone_number(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'security_identity': SECURITY_IDENTITY,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'security_identity'],
            SECURITY_IDENTITY,
        )

    def test_phone_operation_started_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'started': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'started'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_started_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'started': None,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'started'],
            None,
        )

    def test_phone_operation_finished_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'finished': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'finished'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_finished_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'finished': None,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'finished'],
            None,
        )

    def test_phone_operation_code_last_sent_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_last_sent': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'code_last_sent'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_code_last_sent_is_empty_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_last_sent': None,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_last_sent'], None)

    def test_phone_operation_code_confirmed_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_confirmed': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'code_confirmed'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_code_confirmed_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_confirmed': None,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'code_confirmed'],
            None,
        )

    def test_phone_operation_password_verified_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'password_verified': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'password_verified'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_password_verified_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'password_verified': None,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'password_verified'],
            None,
        )

    def test_phone_operation_code_send_count_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_send_count': 7,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_send_count'], 7)

    def test_phone_operation_code_send_count_is_zero_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_send_count': None,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_send_count'], 0)

    def test_phone_operation_phone_id2_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'phone_id2': 31,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id2'], 31)

    def test_phone_operation_phone_id2_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'phone_id2': None,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id2'], None)

    def test_phone_operation_flags_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'flags': PhoneOperationFlags(1),
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'flags'],
            int(PhoneOperationFlags(1)),
        )

    def test_phone_operation_flags_equals_to_zero_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'flags': None,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'flags'],
            int(PhoneOperationFlags(0)),
        )

    def test_phone_operation_code_checks_count_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_checks_count': 16,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_checks_count'], 16)

    def test_phone_operation_code_checks_count_is_zero_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_checks_count': None,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_checks_count'], 0)

    def test_phone_operation_code_value_equals_to_response_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_value': u'1234',
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_value'], u'1234')

    def test_phone_operation_code_value_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_value': None,
            }]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_value'], None)

    def test_phone_operation_is_attached_to_phone(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(
                phones=[{
                    u'id': 14,
                }],
                phone_operations=[{
                    u'id': 5,
                    u'phone_id': 14,
                    u'phone_number': u'+79047766555',
                }],
            ),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
        )

        ok_(response[u'phones'][14][u'operation'] is response[u'phone_operations'][5])

    def test_no_phones_and_no_phone_operations_when_response_has_no_phone_and_no_phone_operations(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
        )

        ok_(u'phones' not in response)
        ok_(u'phone_operations' not in response)

    def test_empty_phones_when_response_has_empty_phones(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phones=[]),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
        )

        ok_(u'phones' in response)
        eq_(len(response[u'phones']), 0)

    def test_no_phones_and_empty_operations_when_response_has_no_phones_and_empty_operations(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phone_operations=[]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, need_phone_operations=True)

        ok_(u'phones' not in response)
        ok_(u'phone_operations' in response)
        eq_(len(response[u'phone_operations']), 0)

    def test_no_operation_in_phone_when_response_has_phone_and_no_operation(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(phones=[{u'id': 14}]),
        )

        response = self._blackbox.login(login=self.LOGIN, password=self.PASSWORD, ip=self.IP, phones=u'all')

        ok_(u'phones' in response)
        ok_(u'phone_operations' not in response)
        ok_(u'operation' not in response[u'phones'][14])

    def test_phone_operation_is_on_phone_when_response_has_phone_and_operation_on_it(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(
                phones=[{u'id': 14}],
                phone_operations=[{
                    u'id': 5,
                    u'phone_id': 14,
                    u'phone_number': u'+79047766555',
                }],
            ),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(u'phones' in response)
        ok_(u'phone_operations' in response)
        ok_(u'operation' in response[u'phones'][14])

    def test_phone_operation_on_phone_is_none_when_response_has_phones_and_empty_operations(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(
                phones=[{u'id': 14}],
                phone_operations=[],
            ),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(u'phones' in response)
        ok_(u'phone_operations' in response)
        ok_(response[u'phones'][14][u'operation'] is None)

    def test_phone_operation_is_in_phone_operations_and_phone_operation_on_phone_is_none_when_response_has_zombie_operation(self):
        self._faker.set_response_value(
            u'login',
            blackbox_login_response(
                phones=[{u'id': 14}],
                phone_operations=[{
                    u'id': 5,
                    u'phone_id': 15,
                    u'phone_number': u'+79047766555',
                }],
            ),
        )

        response = self._blackbox.login(
            login=self.LOGIN,
            password=self.PASSWORD,
            ip=self.IP,
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(response[u'phones'][14][u'operation'] is None)
        ok_(5 in response[u'phone_operations'])
