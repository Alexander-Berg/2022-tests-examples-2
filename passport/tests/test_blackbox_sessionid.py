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
    BLACKBOX_SESSIONID_DISABLED_STATUS,
    BLACKBOX_SESSIONID_EXPIRED_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BLACKBOX_SESSIONID_NEED_RESET_STATUS,
    BLACKBOX_SESSIONID_NOAUTH_STATUS,
    BLACKBOX_SESSIONID_VALID_STATUS,
)
from passport.backend.core.builders.blackbox.constants import SECURITY_IDENTITY
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_response,
    FakeBlackbox,
)
from passport.backend.core.eav_type_mapping import (
    ATTRIBUTE_NAME_TO_TYPE as AT,
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING,
    EXTENDED_ATTRIBUTES_WEBAUTHN_NAME_TO_TYPE_MAPPING as WEBAUTHN_NAME_MAPPING,
)
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    with_settings,
)
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
class TestBlackboxRequestSessionidParse(BaseBlackboxRequestTestCase):
    def test_sessionid_basic(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111114533",
                "hosted" : false,
                "lite" : false
            },
            "ttl" : "0",
            "status" : {
                "value" : "%s",
                "id" : 0
            },
            "age" : 176,
            "karma" : {
                "value" : 85,
                "allow-until" : 1377784338
            },
            "login" : "scullyx13-test22",
            "aliases": {
                "1": "scullyx13-test22"
            },
            "auth" : {
                "allow_plain_text" : true,
                "have_password" : true,
                "password_verification_age" : 176,
                "secure" : true
                },
            "new-session": {
                "value": "test-cookie",
                "domain": ".yandex.ru",
                "expires": 0
            },
            "new-sslsession": {
                "value": "test-ssl-cookie",
                "domain": ".ssl.yandex.ru",
                "expires": 0
            },
            "karma_status" : {
                "value" : 85
            },
            "error" : "OK"
        }
        ''' % BLACKBOX_SESSIONID_VALID_STATUS)
        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
        eq_(response['status'], BLACKBOX_SESSIONID_VALID_STATUS)
        eq_(response['age'], 176)
        eq_(response['ttl'], 0)
        ok_(response['auth']['allow_plain_text'])
        ok_(response['auth']['have_password'])
        eq_(response['auth']['password_verification_age'], 176)
        ok_(response['auth']['secure'])
        ok_('social' not in response)

        eq_(response['new-session']['value'], 'test-cookie')
        eq_(response['new-session']['domain'], '.yandex.ru')
        ok_(not response['new-session']['expires'])
        eq_(response['new-sslsession']['value'], 'test-ssl-cookie')
        eq_(response['new-sslsession']['domain'], '.ssl.yandex.ru')
        ok_(not response['new-sslsession']['expires'])

        eq_(response['uid'], 111114533)
        eq_(response['login'], 'scullyx13-test22')
        eq_(response['aliases'], {'1': 'scullyx13-test22'})
        eq_(response['is_lite_session'], False)
        eq_(response['hosted'], False)
        eq_(response['karma'], 85)
        eq_(response['domid'], None)
        eq_(response['domain'], None)

    def test_sessionid_some_attributes_are_always_there(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111114533",
                "hosted" : false,
                "lite" : false
            },
            "ttl" : "0",
            "status" : {
                "value" : "%s",
                "id" : 0
            },
            "age" : 176,
            "karma" : {
                "value" : 85,
                "allow-until" : 1377784338
            },
            "login" : "scullyx13-test22",
            "aliases": {
                "1": "scullyx13-test22"
            },
            "auth" : {
                "allow_plain_text" : true,
                "have_password" : true,
                "password_verification_age" : 176,
                "secure" : true
                },
            "new-session": {
                "value": "test-cookie",
                "domain": ".yandex.ru",
                "expires": 0
            },
            "new-sslsession": {
                "value": "test-ssl-cookie",
                "domain": ".ssl.yandex.ru",
                "expires": 0
            },
            "karma_status" : {
                "value" : 85
            },
            "attributes": {},
            "error" : "OK"
        }
        ''' % BLACKBOX_SESSIONID_VALID_STATUS)

        for attr_name, default_value in (
            ('account.is_disabled', '0'),
            ('account.global_logout_datetime', '1'),
            ('revoker.tokens', '1'),
            ('revoker.app_passwords', '1'),
            ('revoker.web_sessions', '1'),
        ):
            response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
            ok_(
                str(AT[attr_name]) not in response['attributes'],
                'We didn\'t ask for attribute %s, but there it is.' % attr_name,
            )

            response = self.blackbox.sessionid(
                'sessionid', '127.0.0.1', 'host',
                attributes=[attr_name],
            )
            eq_(
                response['attributes'][str(AT[attr_name])],
                default_value,
                'Default value for attribute "%s" is "%s", but found "%s"' % (
                    attr_name,
                    default_value,
                    response['attributes'][str(AT[attr_name])],
                ),
            )

    def test_parse_sessionid_with_dbfields(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111114533",
                "hosted" : false,
                "lite" : true
            },
            "ttl" : "0",
            "status" : {
                "value" : "%s",
                "id" : 0
            },
            "age" : 176,
            "karma" : {
                "value" : 85,
                "allow-until" : 1377784338
            },
            "login" : "scullyx13-test22",
            "auth" : {
                "allow_plain_text" : true,
                "have_password" : true,
                "password_verification_age" : 176,
                "secure" : true
                },
            "karma_status" : {
                "value" : 85
            },
            "dbfields" : {
               "accounts.ena.uid": "1",
               "subscription.login.8": "scullyx13-test22",
               "subscription.login_rule.8": "1",
               "subscription.suid.8": "544793454",
               "userinfo.sex.uid": "0"
            },
            "display_name" : {
               "name" : "test",
               "social" : {
                  "provider" : "fb",
                  "redirect_target" : "1392719558.99952.1.7fa3e7fafe6dc7ee10dc93469437b170",
                  "profile_id" : "1"
               }
            },
            "error" : "OK"
        }
        ''' % BLACKBOX_SESSIONID_VALID_STATUS)

        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
        eq_(response['status'], BLACKBOX_SESSIONID_VALID_STATUS)
        eq_(response['uid'], 111114533)
        eq_(response['accounts.ena.uid'], 1)
        eq_(
            response['subscriptions'],
            {
                8: {'sid': 8, 'suid': 544793454, 'login': 'scullyx13-test22',
                    'login_rule': 1},
            },
        )
        eq_(response['userinfo.sex.uid'], 0)
        eq_(response['display_name']['name'], 'test')
        eq_(response['is_lite_session'], True)

    def test_sessionid_invalid(self):
        self.set_blackbox_response_value('''
        {
            "status" : {
                "value" : "%s",
                "id" : 5
            },
            "error" : "signature has bad format or is broken"
        }
        ''' % BLACKBOX_SESSIONID_INVALID_STATUS)
        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
        waiting_response = {
            'status': BLACKBOX_SESSIONID_INVALID_STATUS,
            'cookie_status': BLACKBOX_SESSIONID_INVALID_STATUS,
            'error': 'signature has bad format or is broken',
        }
        eq_(response, waiting_response)

    def test_sessionid_expired(self):
        self.set_blackbox_response_value('''
        {
            "status" : {
                "value" : "%s",
                "id" : 2
            },
            "error" : "OK"
        }
        ''' % BLACKBOX_SESSIONID_EXPIRED_STATUS)
        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
        waiting_response = {
            'status': BLACKBOX_SESSIONID_EXPIRED_STATUS,
            'cookie_status': BLACKBOX_SESSIONID_EXPIRED_STATUS,
            'error': 'OK',
        }
        eq_(response, waiting_response)

    def test_sessionid_disabled(self):
        self.set_blackbox_response_value('''
        {
            "status" : {
                "value" : "%s",
                "id" : 4
            },
            "error" : "OK"
        }
        ''' % BLACKBOX_SESSIONID_DISABLED_STATUS)
        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
        waiting_response = {
            'status': BLACKBOX_SESSIONID_DISABLED_STATUS,
            'cookie_status': BLACKBOX_SESSIONID_DISABLED_STATUS,
            'error': 'OK',
        }
        eq_(response, waiting_response)

    def test_sessionid_need_reset(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111114533",
                "hosted" : false,
                "lite" : false
            },
            "ttl" : "0",
            "status" : {
                "value" : "%s",
                "id" : 1
            },
            "age" : 176,
            "karma" : {
                "value" : 85,
                "allow-until" : 1377784338
            },
            "login" : "scullyx13-test22",
            "auth" : {
                "allow_plain_text" : true,
                "have_password" : true,
                "password_verification_age" : 176,
                "secure" : true
            },
            "karma_status" : {
                "value" : 85
            },
            "error" : "OK"
        }
        ''' % BLACKBOX_SESSIONID_NEED_RESET_STATUS)
        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
        eq_(response['status'], BLACKBOX_SESSIONID_NEED_RESET_STATUS)
        eq_(response['age'], 176)
        eq_(response['ttl'], 0)
        ok_(response['auth']['allow_plain_text'])
        ok_(response['auth']['have_password'])
        eq_(response['auth']['password_verification_age'], 176)
        ok_(response['auth']['secure'])

        eq_(response['uid'], 111114533)

    def test_sessionid_noauth(self):
        self.set_blackbox_response_value('''
        {
            "status" : {
                "value" : "%s",
                "id" : 3
            },
            "error" : "OK"
        }
        ''' % BLACKBOX_SESSIONID_NOAUTH_STATUS)
        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
        waiting_response = {
            'status': BLACKBOX_SESSIONID_NOAUTH_STATUS,
            'cookie_status': BLACKBOX_SESSIONID_NOAUTH_STATUS,
            'error': 'OK',
        }
        eq_(response, waiting_response)

    def test_sessionid_with_sslsession(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111114533",
                "hosted" : false,
                "lite" : false
            },
            "ttl" : "0",
            "status" : {
                "value" : "%s",
                "id" : 0
            },
            "age" : 176,
            "karma" : {
                "value" : 85,
                "allow-until" : 1377784338
            },
            "login" : "scullyx13-test22",
            "auth" : {
                "allow_plain_text" : true,
                "have_password" : true,
                "password_verification_age" : 176,
                "secure" : true
            },
            "karma_status" : {
                "value" : 85
            },
            "error" : "OK"
        }
        ''' % BLACKBOX_SESSIONID_VALID_STATUS)
        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
        eq_(response['status'], BLACKBOX_SESSIONID_VALID_STATUS)
        eq_(response['age'], 176)
        eq_(response['ttl'], 0)
        ok_(response['auth']['allow_plain_text'])
        ok_(response['auth']['have_password'])
        eq_(response['auth']['password_verification_age'], 176)
        ok_(response['auth']['secure'])

        eq_(response['uid'], 111114533)

    def test_sessionid_for_social_user(self):
        self.set_blackbox_response_value('''
        {
            "uid" : {
                "value" : "111111183",
                "hosted" : false,
                "lite" : false
            },
            "ttl" : "5",
            "status" : {
                "value" : "%s",
                "id" : 0
            },
            "age" : 176,
            "karma" : {
                "value" : 85,
                "allow-until" : 1377784338
            },
            "login" : "social-test",
            "auth" : {
                "allow_plain_text" : true,
                "have_password" : false,
                "password_verification_age" : -1,
                "secure" : true,
                "social" : {
                    "profile_id":"2"
                }
            },
            "karma_status" : {
                "value" : 0
            },
            "error" : "OK"
        }
        ''' % BLACKBOX_SESSIONID_VALID_STATUS)
        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
        eq_(response['status'], BLACKBOX_SESSIONID_VALID_STATUS)
        eq_(response['age'], 176)
        eq_(response['ttl'], 5)
        ok_(response['auth']['allow_plain_text'])
        ok_(not response['auth']['have_password'])
        eq_(response['auth']['password_verification_age'], -1)
        ok_(response['auth']['secure'])
        eq_(response['auth']['social']['profile_id'], 2)

        eq_(response['uid'], 111111183)

    def test_sessionid_for_multisession(self):
        self.set_blackbox_response_value('''
        {
           "default_uid" : "11806301",
           "ttl" : "0",
           "status" : { "value" : "VALID", "id" : 0 },
           "error" : "OK",
           "users" : [
              {
                 "dbfields" : { "subscription.suid.2" : "27561617" },
                 "have_password" : true,
                 "uid" : { "value" : "11806301", "hosted" : false, "lite" : false },
                 "status" : { "value" : "VALID", "id" : 0 },
                 "have_hint" : true,
                 "karma" : { "value" : 85 },
                 "login" : "junit-test",
                 "auth" : {
                    "allow_plain_text" : true,
                    "have_password" : true,
                    "password_verification_age" : -1,
                    "secure" : true
                 },
                 "karma_status" : { "value" : 85 },
                 "id" : "11806301"
              },
              {
                 "dbfields" : { "subscription.suid.2" : "27561631" },
                 "have_password" : true,
                 "uid" : { "value" : "11806307", "hosted" : false, "lite" : false },
                 "status" : { "value" : "VALID", "id" : 0 },
                 "have_hint" : true,
                 "karma" : { "value" : 0 },
                 "login" : "dot.user",
                 "auth" : {
                    "allow_plain_text" : true,
                    "have_password" : true,
                    "password_verification_age" : -1,
                    "secure" : true
                 },
                 "karma_status" : { "value" : 0 },
                 "id" : "11806307"
              }
           ],
           "age" : 174
        }
        ''')
        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
        eq_(response['status'], BLACKBOX_SESSIONID_VALID_STATUS)
        eq_(response['cookie_status'], BLACKBOX_SESSIONID_VALID_STATUS)
        eq_(response['age'], 174)
        eq_(response['ttl'], 0)
        eq_(response['default_uid'], 11806301)
        ok_('users' in response)
        eq_(len(response['users']), 2)

        eq_(response['users'][11806301]['uid'], 11806301)
        eq_(response['users'][11806301]['status'], BLACKBOX_SESSIONID_VALID_STATUS)
        eq_(response['users'][11806301]['auth']['password_verification_age'], -1)
        eq_(response['users'][11806301]['login'], 'junit-test')

        eq_(response['users'][11806307]['uid'], 11806307)
        eq_(response['users'][11806307]['status'], BLACKBOX_SESSIONID_VALID_STATUS)
        eq_(response['users'][11806307]['auth']['password_verification_age'], -1)
        eq_(response['users'][11806307]['login'], 'dot.user')

        eq_(response['uid'], 11806301)
        eq_(response['login'], 'junit-test')
        eq_(response['is_lite_session'], False)
        eq_(response['karma'], 85)
        eq_(response['auth']['password_verification_age'], -1)

    def test_sessionid_for_multisession_with_disabled_invalid_deleted_accounts(self):
        self.set_blackbox_response_value('''
        {
           "default_uid" : "11806301",
           "ttl" : "0",
           "status" : { "value" : "VALID", "id" : 0 },
           "error" : "OK",
           "users" : [
              {
                 "uid" : { "value" : "11806301", "hosted" : false, "lite" : false },
                 "status" : { "value" : "DISABLED", "id" : 0 },
                 "have_hint" : true,
                 "karma" : { "value" : 85 },
                 "login" : "junit-test",
                 "karma_status" : { "value" : 85 },
                 "id" : "11806301"
              },
              {
                 "uid" : { "value" : "11806307", "hosted" : false, "lite" : false },
                 "status" : { "value" : "INVALID", "id" : 0 },
                 "have_hint" : true,
                 "karma" : { "value" : 0 },
                 "login" : "dot.user",
                 "karma_status" : { "value" : 0 },
                 "id" : "11806307"
              },
              {
                 "status" : { "value" : "INVALID", "id" : 0 },
                 "id" : "11806308"
              }
           ],
           "age" : 174
        }
        ''')
        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
        eq_(response['cookie_status'], BLACKBOX_SESSIONID_VALID_STATUS)
        eq_(response['status'], BLACKBOX_SESSIONID_DISABLED_STATUS)

        eq_(response['age'], 174)
        eq_(response['ttl'], 0)
        eq_(response['default_uid'], 11806301)
        ok_('users' in response)
        eq_(len(response['users']), 3)

        eq_(response['users'][11806301]['status'], BLACKBOX_SESSIONID_DISABLED_STATUS)
        eq_(response['users'][11806301]['uid'], 11806301)
        eq_(response['users'][11806301]['login'], 'junit-test')

        eq_(response['users'][11806307]['status'], BLACKBOX_SESSIONID_INVALID_STATUS)
        eq_(response['users'][11806307]['uid'], 11806307)
        eq_(response['users'][11806307]['login'], 'dot.user')

        eq_(response['users'][11806308]['status'], BLACKBOX_SESSIONID_INVALID_STATUS)

    def test_sessionid_with_family_info(self):
        self.set_blackbox_response_value('''
           {
               "uid" : {
                   "value" : "111114533",
                   "hosted" : false,
                   "lite" : false
               },
               "ttl" : "0",
               "status" : {
                   "value" : "%s",
                   "id" : 0
               },
               "age" : 176,
               "karma" : {
                   "value" : 85,
                   "allow-until" : 1377784338
               },
               "login" : "test22",
               "aliases": {
                   "1": "test22"
               },
               "karma_status" : {
                   "value" : 85
               },
               "family_info" : {
                   "admin_uid" : "111114533",
                   "family_id" : "f1"
               },
               "error" : "OK"
           }
           ''' % BLACKBOX_SESSIONID_VALID_STATUS)
        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')
        eq_(response['status'], BLACKBOX_SESSIONID_VALID_STATUS)
        eq_(response['family_info'], {'admin_uid': '111114533', 'family_id': 'f1'})

    def test_sessionid_with_family_info_for_multisession(self):
        self.set_blackbox_response_value('''
        {
           "default_uid" : "11806301",
           "ttl" : "0",
           "status" : { "value" : "VALID", "id" : 0 },
           "error" : "OK",
           "users" : [
              {
                 "uid" : { "value" : "11806301", "hosted" : false, "lite" : false },
                 "status" : { "value" : "%s", "id" : 0 },
                 "have_hint" : true,
                 "karma" : { "value" : 85 },
                 "login" : "junit-test",
                 "karma_status" : { "value" : 85 },
                 "family_info" : { "admin_uid" : "11806301", "family_id" : "f1" },
                 "id" : "11806301"
              },
              {
                 "uid" : { "value" : "11806307", "hosted" : false, "lite" : false },
                 "status" : { "value" : "%s", "id" : 0 },
                 "have_hint" : true,
                 "karma" : { "value" : 0 },
                 "login" : "dot.user",
                 "karma_status" : { "value" : 0 },
                 "family_info" : { "admin_uid" : "11806307", "family_id" : "f2" },
                 "id" : "11806307"
              }
           ],
           "age" : 174
        }
        ''' % (BLACKBOX_SESSIONID_VALID_STATUS, BLACKBOX_SESSIONID_VALID_STATUS))
        response = self.blackbox.sessionid(
            'sessionid', '127.0.0.1', 'host', get_family_info=True)

        eq_(
            response['users'][11806301]['family_info'],
            {'admin_uid': '11806301', 'family_id': 'f1'},
        )
        eq_(
            response['users'][11806307]['family_info'],
            {'admin_uid': '11806307', 'family_id': 'f2'},
        )

    def is_scholar_session(self):
        self.set_blackbox_response_value(blackbox_sessionid_response(is_scholar_session=True))

        response = self.blackbox.sessionid('sessionid', '127.0.0.1', 'host', allow_scholar=True)

        assert response.get('is_scholar_session')

    @raises(AccessDenied)
    def test_blackbox_error_raises_exception(self):
        self.set_blackbox_response_value('''{"exception":{"value":"ACCESS_DENIED","id":21},
                       "error":"BlackBox error: Access denied"}''')
        self.blackbox.sessionid('sessionid', '127.0.0.1', 'host')


@with_settings(
    BLACKBOX_URL='http://localhost/',
    BLACKBOX_FIELDS=[],
    BLACKBOX_ATTRIBUTES=['account.normalized_login'],
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=[u'number', u'created', u'bound'],
)
class TestBlackboxRequestSessionidUrl(BaseBlackboxRequestTestCase):
    SESSIONID = '1322489952.-136:'
    IP = '127.0.0.1'
    HOST = 'yandex.ru'

    def setUp(self):
        super(TestBlackboxRequestSessionidUrl, self).setUp()
        self._phone_args_assertions = TestPhoneArguments(self._build_request_info)
        self._phone_args_assertions = TestPhoneArguments(self._build_request_info)

    def sessionid_params(self, **kwargs):
        return self.base_params(
            {
                'sessionid': self.SESSIONID,
                'userip': self.IP,
                'host': self.HOST,
                'format': 'json',
                'method': 'sessionid',
                'authid': 'yes',
                'regname': 'yes',
                'get_public_name': 'yes',
                'is_display_name_empty': 'yes',
                'full_info': 'yes',
                'aliases': 'all_with_hidden',
                'attributes': '1008',
            },
            **kwargs
        )

    def test_sessionid_basic(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
        )

        check_all_url_params_match(request_info.url, self.sessionid_params())
        eq_(request_info.headers, {})

    def test_sessionid_wo_hidden_aliases(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            get_hidden_aliases=False,
        )

        check_all_url_params_match(request_info.url, self.sessionid_params(aliases='all'))
        eq_(request_info.headers, {})

    def test_sessionid_guard_hosts_wo_duplicates(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            guard_hosts=['passport.yandex.ru', 'mail.yandex.ru', 'passport.yandex.ru'],
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(
                guard_hosts='passport.yandex.ru,mail.yandex.ru',
            ),
        )
        eq_(request_info.headers, {})

    def test_sessionid_with_sslsessionid(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            sslsessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(sslsessionid=self.SESSIONID),
        )

    def test_sessionid_with_sessguard(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            sessguard='guard',
            guard_hosts=['passport.yandex.ru', 'mail.yandex.ru'],
            request_id='req-id',
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(
                sessguard='guard',
                guard_hosts='passport.yandex.ru,mail.yandex.ru',
                request_id='req-id',
            ),
        )

    def test_sessionid_with_dbfields(self):
        dbfields = ['field1', 'field2']
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            dbfields=dbfields,
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(dbfields=u','.join(dbfields)),
        )

    def test_sessionid_without_attributes(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            attributes=[],
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(exclude=['attributes']),
        )

    def test_sessionid_emails(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            emails=True,
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(emails='getall'),
        )

    def test_sessionid_email_attributes(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            email_attributes='all',
        )
        eq_(
            request_info.get_args,
            self.sessionid_params(
                sessionid=self.SESSIONID,
                getemails='all',
                email_attributes='all',
                host=self.HOST,
            ),
        )

    def test_sessionid_specific_email_attributes(self):
        attributes = [
            'address',
            'created',
            'confirmed',
        ]
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            email_attributes=attributes,
        )
        eq_(
            request_info.get_args,
            self.sessionid_params(**{
                'sessionid': self.SESSIONID,
                'getemails': 'all',
                'email_attributes': ','.join([
                    str(EMAIL_NAME_MAPPING[attr])
                    for attr in attributes
                ]),
            }),
        )

    def test_sessionid_get_webauthn_credentials(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            get_webauthn_credentials=True,
        )
        eq_(
            request_info.get_args,
            self.sessionid_params(
                sessionid=self.SESSIONID,
                get_webauthn_credentials='all',
                webauthn_credential_attributes='all',
                host=self.HOST,
            ),
        )

    def test_sessionid_get_webauthn_credentials__specific_attributes(self):
        attributes = [
            'external_id',
            'sign_count',
            'created',
        ]
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            get_webauthn_credentials=True,
            webauthn_credential_attributes=attributes,
        )
        eq_(
            request_info.get_args,
            self.sessionid_params(
                sessionid=self.SESSIONID,
                host=self.HOST,
                get_webauthn_credentials='all',
                webauthn_credential_attributes=','.join([
                    str(WEBAUTHN_NAME_MAPPING[attr])
                    for attr in attributes
                ]),
            ),
        )

    def test_sessionid_with_prolong(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            prolong_cookies=True,
            yandexuid='yu',
            useragent='ua',
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(resign='yes', yandexuid='yu', useragent='ua'),
        )

    def test_sessionid_with_force_prolong(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            prolong_cookies=True,
            force_prolong=True,
            yandexuid='yu',
            useragent='ua',
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(resign='yes', force_resign='yes', yandexuid='yu', useragent='ua'),
        )

    def test_sessionid_with_resign_for_domains(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            resign_for_domains=['yandex.ru', 'kinopoisk.ru', 'edadeal.ru'],
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(resign_for_domains='edadeal.ru,kinopoisk.ru,yandex.ru'),
        )

    def test_sessionid_without_authid(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            prolong_cookies=True,
            authid=False,
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(resign='yes', exclude=['authid']),
        )

    def test_sessionid_with_multisession(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            prolong_cookies=True,
            multisession=True,
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(resign='yes', multisession='yes'),
        )

    def test_sessionid_no_aliases(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            need_aliases=False,
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(exclude=['aliases']),
        )

    def test_sessionid_with_get_user_ticket(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            get_user_ticket=True,
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(
                get_user_ticket='yes',
            ),
        )
        eq_(
            request_info.headers,
            {'X-Ya-Service-Ticket': TEST_TICKET},
        )

    def test_sessionid_with_sslsessionid_and_get_user_ticket(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            sslsessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            get_user_ticket=True,
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(
                sslsessionid=self.SESSIONID,
                get_user_ticket='yes',
            ),
        )
        eq_(
            request_info.headers,
            {'X-Ya-Service-Ticket': TEST_TICKET},
        )

    def test_sessionid_with_family_info(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            get_family_info=True,
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(get_family_info='yes'),
        )

    def test_sessionid_with_public_id(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            get_public_id=True,
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(get_public_id='yes'),
        )

    def test_sessionid_force_show_mail_subscription(self):
        request_info = Blackbox().build_sessionid_request(
            sessionid=self.SESSIONID,
            ip=self.IP,
            host=self.HOST,
            force_show_mail_subscription=True,
        )

        check_all_url_params_match(
            request_info.url,
            self.sessionid_params(force_show_mail_subscription='yes'),
        )

    @raises(TypeError)
    def test_sessionid_without_args(self):
        Blackbox().build_sessionid_request()

    def test_request_phones_is_all_when_phones_arg_value_is_all(self):
        self._phone_args_assertions.assert_request_phones_is_all_when_phones_arg_value_is_all()

    def test_request_has_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_not_empty(self):
        self._phone_args_assertions.assert_request_has_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_not_empty()

    def test_request_has_no_phone_attributes_when_phone_attributes_is_empty(self):
        self._phone_args_assertions.assert_request_has_no_phone_attributes_when_phone_attributes_is_empty()

    def test_request_has_no_phone_attributes_when_phones_is_none_and_phone_attributes_is_not_empty(self):
        self._phone_args_assertions.assert_request_has_no_phone_attributes_when_phones_is_none_and_phone_attributes_is_not_empty()

    def test_request_has_default_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_none(self):
        self._phone_args_assertions.assert_request_has_default_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_none()

    def test_request_get_phone_operations_is_one_when_need_phone_operations_is_true(self):
        self._phone_args_assertions.assert_request_get_phone_operations_is_one_when_need_phone_operations_is_true()

    def test_request_has_no_phone_operations_when_need_phone_operations_is_false(self):
        self._phone_args_assertions.assert_request_has_no_phone_operations_when_need_phone_operations_is_false()

    def test_phone_bindings(self):
        self._phone_args_assertions.test_phone_bindings()

    def test_allow_scholar(self):
        request_info = self._build_request_info(allow_scholar=True)
        check_all_url_params_match(request_info.url, self.sessionid_params(allow_scholar='yes'))

        request_info = self._build_request_info(allow_scholar=False)
        check_all_url_params_match(request_info.url, self.sessionid_params())

        request_info = self._build_request_info()
        check_all_url_params_match(request_info.url, self.sessionid_params())

    def _build_request_info(self, **kwargs):
        kwargs.setdefault(u'sessionid', self.SESSIONID)
        kwargs.setdefault(u'ip', self.IP)
        kwargs.setdefault(u'host', self.HOST)
        return Blackbox().build_sessionid_request(**kwargs)


@with_settings(
    BLACKBOX_URL=u'http://bl.ackb.ox/',
    BLACKBOX_ATTRIBUTES=[],
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=[],
)
class RequestTestSessionidParsePhones(BaseBlackboxTestCase):
    SESSIONID = '1322489952.-136:'
    IP = '127.0.0.1'
    HOST = 'yandex.ru'

    def setUp(self):
        super(RequestTestSessionidParsePhones, self).setUp()
        self._blackbox = Blackbox()
        self._faker = FakeBlackbox()
        self._faker.start()

    def tearDown(self):
        self._faker.stop()
        del self._faker
        super(RequestTestSessionidParsePhones, self).tearDown()

    def test_phone_with_empty_attributes_when_response_has_phone_and_empty_attributes(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phones=[{u'id': 22}]),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
            ip=self.IP,
            phones=u'all',
            phone_attributes=None,
        )

        eq_(response[u'phones'], {22: {u'id': 22, u'attributes': {}}})

    def test_phone_attribute_phone_number_equals_to_response_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(
                phones=[{u'id': 1, u'number': u'+79036655444'}],
            ),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
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
            u'sessionid',
            blackbox_sessionid_response(
                phones=[{u'id': 1, u'created': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
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
            u'sessionid',
            blackbox_sessionid_response(
                phones=[{u'id': 1, u'bound': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
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
            u'sessionid',
            blackbox_sessionid_response(
                phones=[{u'id': 1, u'confirmed': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
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
            u'sessionid',
            blackbox_sessionid_response(
                phones=[{u'id': 1, u'admitted': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
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
            u'sessionid',
            blackbox_sessionid_response(
                phones=[{u'id': 1, u'secured': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
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
            u'sessionid',
            blackbox_sessionid_response(
                phones=[{u'id': 1, u'is_default': 1}],
            ),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
            ip=self.IP,
            phones=u'all',
            phone_attributes=[u'is_default'],
        )

        ok_(response[u'phones'][1][u'attributes'][u'is_default'])

    def test_operation_id_equals_to_operation_id_from_response(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        ok_(5 in response[u'phone_operations'])
        eq_(response[u'phone_operations'][5][u'id'], 5)

    def test_single_operation_when_response_has_single_operations(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(len(response[u'phone_operations']), 1)

    def test_many_operations_when_response_has_many_operations(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[
                {u'id': 5, u'phone_number': u'+79047766555'},
                {u'id': 6, u'phone_number': u'+79036655444'},
            ]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(len(response[u'phone_operations']), 2)

    def test_operation_phone_id_equals_to_operation_phone_id_from_response(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_id': 7,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id'], 7)

    def test_operation_phone_is_none_when_response_has_not_operation_phone_id(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_id': None,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id'], None)

    def test_operation_security_identity_is_like_phone_number_when_operation_is_not_on_secure_phone_number(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'security_identity'], 79047766555)

    def test_operation_security_identity_is_predefined_value_when_operation_is_on_secure_phone_number(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'security_identity': SECURITY_IDENTITY,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'security_identity'],
            SECURITY_IDENTITY,
        )

    def test_phone_operation_started_equals_to_response_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'started': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'started'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_started_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'started': None,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'started'],
            None,
        )

    def test_phone_operation_finished_equals_to_response_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'finished': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'finished'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_finished_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'finished': None,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'finished'],
            None,
        )

    def test_phone_operation_code_last_sent_equals_to_response_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_last_sent': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'code_last_sent'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_code_last_sent_is_empty_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_last_sent': None,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_last_sent'], None)

    def test_phone_operation_code_confirmed_equals_to_response_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_confirmed': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'code_confirmed'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_code_confirmed_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_confirmed': None,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'code_confirmed'],
            None,
        )

    def test_phone_operation_password_verified_equals_to_response_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'password_verified': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'password_verified'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_password_verified_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'password_verified': None,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'password_verified'],
            None,
        )

    def test_phone_operation_code_send_count_equals_to_response_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_send_count': 7,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_send_count'], 7)

    def test_phone_operation_code_send_count_is_zero_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_send_count': None,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_send_count'], 0)

    def test_phone_operation_phone_id2_equals_to_response_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'phone_id2': 31,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id2'], 31)

    def test_phone_operation_phone_id2_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'phone_id2': None,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id2'], None)

    def test_phone_operation_flags_equals_to_response_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'flags': PhoneOperationFlags(1),
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'flags'],
            int(PhoneOperationFlags(1)),
        )

    def test_phone_operation_flags_equals_to_zero_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'flags': None,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'flags'],
            int(PhoneOperationFlags(0)),
        )

    def test_phone_operation_code_checks_count_equals_to_response_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_checks_count': 16,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_checks_count'], 16)

    def test_phone_operation_code_checks_count_is_zero_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_checks_count': None,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_checks_count'], 0)

    def test_phone_operation_code_value_equals_to_response_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_value': u'1234',
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_value'], u'1234')

    def test_phone_operation_code_value_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_value': None,
            }]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_value'], None)

    def test_phone_operation_is_attached_to_phone(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(
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

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
            ip=self.IP,
        )

        ok_(response[u'phones'][14][u'operation'] is response[u'phone_operations'][5])

    def test_no_phones_and_no_phone_operations_when_response_has_no_phone_and_no_phone_operations(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
            ip=self.IP,
            phones=u'all',
        )

        ok_(u'phones' not in response)
        ok_(u'phone_operations' not in response)

    def test_empty_phones_when_response_has_empty_phones(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phones=[]),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
            ip=self.IP,
            phones=u'all',
        )

        ok_(u'phones' in response)
        eq_(len(response[u'phones']), 0)

    def test_no_phones_and_empty_operations_when_response_has_no_phones_and_empty_operations(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phone_operations=[]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, need_phone_operations=True)

        ok_(u'phones' not in response)
        ok_(u'phone_operations' in response)
        eq_(len(response[u'phone_operations']), 0)

    def test_no_operation_in_phone_when_response_has_phone_and_no_operation(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(phones=[{u'id': 14}]),
        )

        response = self._blackbox.sessionid(sessionid=self.SESSIONID, host=self.HOST, ip=self.IP, phones=u'all')

        ok_(u'phones' in response)
        ok_(u'phone_operations' not in response)
        ok_(u'operation' not in response[u'phones'][14])

    def test_phone_operation_is_on_phone_when_response_has_phone_and_operation_on_it(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(
                phones=[{u'id': 14}],
                phone_operations=[{
                    u'id': 5,
                    u'phone_id': 14,
                    u'phone_number': u'+79047766555',
                }],
            ),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
            ip=self.IP,
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(u'phones' in response)
        ok_(u'phone_operations' in response)
        ok_(u'operation' in response[u'phones'][14])

    def test_phone_operation_on_phone_is_none_when_response_has_phones_and_empty_operations(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(
                phones=[{u'id': 14}],
                phone_operations=[],
            ),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
            ip=self.IP,
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(u'phones' in response)
        ok_(u'phone_operations' in response)
        ok_(response[u'phones'][14][u'operation'] is None)

    def test_phone_operation_is_in_phone_operations_and_phone_operation_on_phone_is_none_when_response_has_zombie_operation(self):
        self._faker.set_response_value(
            u'sessionid',
            blackbox_sessionid_response(
                phones=[{u'id': 14}],
                phone_operations=[{
                    u'id': 5,
                    u'phone_id': 15,
                    u'phone_number': u'+79047766555',
                }],
            ),
        )

        response = self._blackbox.sessionid(
            sessionid=self.SESSIONID,
            host=self.HOST,
            ip=self.IP,
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(response[u'phones'][14][u'operation'] is None)
        ok_(5 in response[u'phone_operations'])
