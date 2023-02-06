# -*- coding: utf-8 -*-

from datetime import datetime
import json

from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.blackbox import (
    AccessDenied,
    Blackbox,
)
from passport.backend.core.builders.blackbox.constants import SECURITY_IDENTITY
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    FakeBlackbox,
)
from passport.backend.core.builders.blackbox.parsers import SUBSCRIPTION_ATTR_TO_SID
from passport.backend.core.eav_type_mapping import (
    ATTRIBUTE_NAME_TO_TYPE,
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING,
)
from passport.backend.core.test.test_utils import (
    settings_context,
    with_settings,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import unixtime
from passport.backend.core.types.bit_vector.bit_vector import (
    PhoneBindingsFlags,
    PhoneOperationFlags,
)
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import merge_dicts
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
    TestPhoneArguments,
)


TEST_PHONE_ID1 = 3
TEST_PHONE_ID2 = 5
TEST_TIME1 = datetime(2001, 2, 3)
TEST_PHONE_NUMBER1 = PhoneNumber.parse('+79259164525')


@with_settings_hosts(
    BLACKBOX_URL='http://localhost/',
    BLACKBOX_ATTRIBUTES=[],
)
class TestBlackboxRequestInfo(BaseBlackboxRequestTestCase):
    def test_basic_user_info(self):
        self.set_blackbox_response_value(
            '''{"users":[{"id":"680","uid":{"value":"680","lite":false,"hosted":false,"domid":"","domain":"","mx":""},
            "aliases":{"1":"test"},"login":"test","karma":{"value":75},"karma_status":{"value":75}}]}''',
        )
        response = self.blackbox.userinfo(uid=680)
        eq_(response['uid'], 680)
        eq_(response['hosted'], False)
        eq_(response['karma'], 75)
        eq_(response['domid'], None)
        eq_(response['domain'], None)
        eq_(response['aliases'], {'1': 'test'})
        ok_('subscriptions' not in response)

    def test_get_full_user_info(self):
        self.set_blackbox_response_value(u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "aliases": { "6":"uid-sjywgxrn" },
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status":{ "value":85 },
            "regname":"test",
            "display_name": { "name":"Козьма Прутков",
                "public_name":"Козьма П.",
                "social": { "profile_id":"5328", "provider":"tw",
                    "redirect_target":"1323266014.26924.5328.9e5e3b502d5ee16abc40cf1d972a1c17" } },
            "attributes": { "1008": "test" },
            "address-list": [ { "address":"test@yandex.ru", "validated":true, "default":true,
                "prohibit-restore":false, "rpop":false, "unsafe":false, "native":true,
                "born-date":"2011-11-16 00:00:00" } ] }]}''')

        response = self.blackbox.userinfo(uid=1)
        eq_(response['uid'], 3000062912)
        eq_(response['display_login'], 'test')
        eq_(response['karma'], 85)
        eq_(response['login'], "test")
        eq_(response['account.normalized_login'], "test")
        eq_(response['lite'], False)
        eq_(response['hosted'], False)
        eq_(response['aliases']['6'], "uid-sjywgxrn")
        eq_(response['address-list'][0]['address'], "test@yandex.ru")
        eq_(response['display_name']['name'], u"Козьма Прутков")
        eq_(response['display_name']['public_name'], u"Козьма П.")
        eq_(response['display_name']['social']['profile_id'], "5328")
        eq_(response['display_name']['social']['provider'], "tw")
        eq_(response['domid'], None)
        eq_(response['domain'], None)

    def test_userinfo_dbfields(self):
        self.set_blackbox_response_value(u'''{"users": [
            {
                "dbfields": {
                    "accounts.ena.uid": "1",
                    "userinfo.sex.uid": "1"
                },
                "id": "1",
                "karma": { "value": 100 },
                "karma_status": { "value": 3000 },
                "login": "fel",
                "uid": {
                    "domain": "",
                    "domid": "",
                    "hosted": false,
                    "lite": false,
                    "mx": "",
                    "value": "10"
                } } ] } ''')

        response = self.blackbox.userinfo(uid=1)

        eq_(response['userinfo.sex.uid'], 1)

    def test_empty_subscriptions(self):
        self.set_blackbox_response_value(u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "aliases": { "6":"uid-sjywgxrn" },
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status":{ "value":85 },
            "dbfields": {
                "subscription.suid.5": "", "subscription.login_rule.3": "",
                "subscription.login_rule.5": "", "subscription.suid.3": ""
            }}]}''')

        response = self.blackbox.userinfo(uid=1)
        eq_(response['uid'], 3000062912)
        eq_(response['karma'], 85)
        eq_(response['login'], "test")
        eq_(response['subscriptions'], {})

    def test_enable_app_password(self):
        self.set_blackbox_response_value(u'''
            {
                "users":[{
                    "uid": {
                        "value": "1",
                        "lite": false,
                        "hosted": false,
                        "domid": "",
                        "domain" :"",
                        "mx": ""
                    },
                    "attributes": {
                        "%d": "1"
                    }
                }]
            }
        ''' % ATTRIBUTE_NAME_TO_TYPE['account.enable_app_password'])

        response = self.blackbox.userinfo(uid=1)
        eq_(response['enable_app_password'], '1')

    def test_is_shared(self):
        self.set_blackbox_response_value(u'''
            {
                "users":[{
                    "uid": {
                        "value": "1",
                        "lite": false,
                        "hosted": false,
                        "domid": "",
                        "domain" :"",
                        "mx": ""
                    },
                    "attributes": {
                        "%d": "1"
                    }
                }]
            }
        ''' % ATTRIBUTE_NAME_TO_TYPE['account.is_shared'])

        response = self.blackbox.userinfo(uid=1)
        eq_(response['is_shared'], '1')

    def test_is_easily_hacked(self):
        self.set_blackbox_response_value(u'''
            {
                "users":[{
                    "uid": {
                        "value": "1",
                        "lite": false,
                        "hosted": false,
                        "domid": "",
                        "domain" :"",
                        "mx": ""
                    },
                    "attributes": {
                        "%d": "1"
                    }
                }]
            }
        ''' % ATTRIBUTE_NAME_TO_TYPE['account.is_easily_hacked'])

        response = self.blackbox.userinfo(uid=1)
        eq_(response['account.is_easily_hacked'], '1')

    def test_is_connect_admin(self):
        self.set_blackbox_response_value(u'''
            {
                "users":[{
                    "uid": {
                        "value": "1",
                        "lite": false,
                        "hosted": false,
                        "domid": "",
                        "domain" :"",
                        "mx": ""
                    },
                    "attributes": {
                        "%d": "1"
                    }
                }]
            }
        ''' % ATTRIBUTE_NAME_TO_TYPE['account.is_connect_admin'])

        response = self.blackbox.userinfo(uid=1)
        eq_(response['account.is_connect_admin'], '1')

    def test_password_update_datetime(self):
        self.set_blackbox_response_value(
            u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "aliases": { "6":"uid-sjywgxrn" },
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status":{ "value":85 },
            "attributes": {
                "%d": "test-timestamp"
            }}]}''' % ATTRIBUTE_NAME_TO_TYPE['password.update_datetime'],
        )

        response = self.blackbox.userinfo(uid=1)
        eq_(response['password.update_datetime'], 'test-timestamp')

    def test_subscription_info(self):
        self.set_blackbox_response_value(u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "aliases": { "6":"uid-sjywgxrn" },
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status":{ "value":85 },
            "dbfields": {
                "subscription.suid.5": "10", "subscription.login_rule.3": "1",
                "subscription.login_rule.5": "0", "subscription.suid.3": "20",
                "subscription.born_date.3": "2000-01-01 12:34:56"
            }}]}''')

        response = self.blackbox.userinfo(uid=1)
        eq_(response['uid'], 3000062912)
        eq_(response['karma'], 85)
        eq_(response['login'], "test")
        eq_(response['subscriptions'][5], {"sid": 5, "login_rule": 0, "suid": 10})
        eq_(response['subscriptions'][3], {"sid": 3, "login_rule": 1, "suid": 20, "born_date": '2000-01-01 12:34:56'})

    def test_subscription_info_2(self):
        self.set_blackbox_response_value(u''' {"users":[{"id":"10","uid":{"value":"10","lite":false,"hosted":false,"domid":"",
            "domain":"","mx":""},"login":"test","karma":{"value":100},"karma_status":{"value":3000},
            "attributes": {"1008": "test"},
            "dbfields":{"accounts.ena.uid":"1",
            "subscription.login.3":"test","subscription.login.5":"",
            "subscription.login_rule.100":"","subscription.login_rule.3":"1",
            "subscription.login_rule.5":"","subscription.login_rule.8":"", "subscription.suid.100": "",
            "subscription.login_rule.800":"1","subscription.suid.3":"110603",
            "subscription.suid.5":"","subscription.suid.668":"",
            "subscription.suid.67":"","subscription.suid.8":"","subscription.suid.800":"23440274",
            "userinfo.sex.uid":"1"}}]}''')

        response = self.blackbox.userinfo(uid=1)

        eq_(response['uid'], 10)
        eq_(response['karma'], 3000)
        eq_(response['login'], "test")

        ok_(100 not in response['subscriptions'])
        eq_(response['subscriptions'][3], {"sid": 3, "login": "test", "login_rule": 1, "suid": 110603})
        eq_(response['subscriptions'][800], {"sid": 800, "login_rule": 1, "suid": 23440274})

    def test_subscription_from_attributes(self):
        attr_codes, sids = SUBSCRIPTION_ATTR_TO_SID.keys(), SUBSCRIPTION_ATTR_TO_SID.values()
        attributed_subscriptions = ['"%d": 1' % attr for attr in attr_codes]
        sid_not_in_attrs = max(sids) + 1

        self.set_blackbox_response_value(u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "aliases": { "6":"uid-sjywgxrn" },
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status":{ "value":85 },
            "attributes": {
                %s
            },
            "dbfields": {
                "subscription.suid.%d": "1"
            }}]}''' % (', '.join(attributed_subscriptions), sid_not_in_attrs))
        response = self.blackbox.userinfo(uid=1)

        # Проверяем, что все SIDы из атрибутов попали в подписки
        ok_(set(sids).issubset(set(response['subscriptions'].keys())))
        # Проверяем, что мы только дополняем массив подписок, но не затираем его
        ok_(sid_not_in_attrs in response['subscriptions'])
        # Проверяем формат созданных записей о подписках
        for attr_sid in sids:
            ok_(response['subscriptions'][attr_sid] == {'sid': attr_sid})

    def test_subscription_from_attributes_without_dbfields(self):
        """
        Проверим, что подписки корректно вычитываются из атрибутов,
        даже если dbfields не пришли в ответе ЧЯ.
        """
        attr_codes, sids = SUBSCRIPTION_ATTR_TO_SID.keys(), SUBSCRIPTION_ATTR_TO_SID.values()
        attributed_subscriptions = ['"%d": 1' % attr for attr in attr_codes]

        self.set_blackbox_response_value(u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "aliases": { "6":"uid-sjywgxrn" },
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status":{ "value":85 },
            "attributes": {
                %s
            }}]}''' % (', '.join(attributed_subscriptions)))
        response = self.blackbox.userinfo(uid=1)

        # Проверяем, что все SIDы из атрибутов попали в подписки
        ok_(set(sids).issubset(set(response['subscriptions'].keys())))
        # Проверяем формат созданных записей о подписках
        for attr_sid in sids:
            ok_(response['subscriptions'][attr_sid] == {'sid': attr_sid})

    def test_empty_user_info(self):
        self.set_blackbox_response_value('{"users":[{"id":"5","uid":{},"login":"","karma":{"value":0},'
                                         '"karma_status":{"value":0},"dbfields":{}}]}')
        response = self.blackbox.userinfo(uid=1)
        eq_(response['uid'], None)
        eq_(response['karma'], 0)

    def test_nullify_params(self):
        self.set_blackbox_response_value(u'''{"users":[{"id":"9887422","uid":{"value":"9887422","lite":false,
            "hosted":false,"domid":"","domain":"","mx":""},"login":"X-ScUlly",
            "karma":{"value":100},"karma_status":{"value":3000},
            "attributes": {"1008": "X-ScUlly"},
            "person.city":null,
            "dbfields":{"accounts.ena.uid":"0",
            "subscription.login_rule.100":"","subscription.login_rule.8":"1",
            "subscription.suid.100":"","subscription.suid.668":"",
            "subscription.suid.67":"","subscription.suid.8":"22579928",
            "userinfo.sex.uid":null}}]}''')
        response = self.blackbox.userinfo(uid=1)
        eq_(response['uid'], 9887422)
        eq_(response['userinfo.sex.uid'], None)
        eq_(response['person.city'], None)

    def test_empty_login_on_social_user(self):
        self.set_blackbox_response_value(u'''{"users":[{"id":"123200948","uid":{"value":"123200948","lite":false,
            "hosted":false},"login":"","karma":{"value":0},"karma_status":{"value":0},
            "attributes": {"1008": "uid-sialqpkj"},
            "dbfields":{"accounts.ena.uid":"1",
            "subscription.login_rule.100":"","subscription.login_rule.8":"1",
            "subscription.suid.100":"","subscription.suid.52":"",
            "subscription.suid.668":"","subscription.suid.67":"",
            "subscription.suid.8":"346299500",
            "userinfo.sex.uid":"1"}}]}''')
        response = self.blackbox.userinfo(uid=1)
        eq_(response['uid'], 123200948)
        eq_(response['login'], 'uid-sialqpkj')

    @raises(AccessDenied)
    def test_blackbox_error_raises_exception(self):
        self.set_blackbox_response_value('''{"exception":{"value":"ACCESS_DENIED","id":21},
            "error":"BlackBox error: Unconfigured dbfield 'subscription.login_rule.7'"}''')

        self.blackbox.userinfo(uid=1)

    def test_pdd_userinfo(self):
        self.set_blackbox_response_value(u'''{"users":[{"id":"1130000004124554","uid":{"value":"1130000004124554",
            "lite":false,"hosted":true,"domid":"12345","domain":"kompolan.ru",
            "mx":"1","domain_ena":"1"},"login":"info","karma":{"value":0},
            "attributes": {"1008": "info"},
            "karma_status":{"value":0},"dbfields":{"accounts.ena.uid":"1",
            "subscription.login_rule.100":"",
            "subscription.login_rule.8":"1","subscription.suid.100":"",
            "subscription.suid.55":"","subscription.suid.668":"",
            "subscription.suid.67":"","subscription.suid.8":"1130000011278679",
            "userinfo.sex.uid":"1"}}]}''')
        response = self.blackbox.userinfo(uid=1)
        eq_(response['uid'], 1130000004124554)
        eq_(response['login'], 'info')
        eq_(response['domid'], 12345)
        eq_(response['domain'], 'kompolan.ru')

    def test_userinfo_emails_response(self):
        self.set_blackbox_response_value('''
        {
            "users" : [
                {
                    "uid" : {
                        "value" : "1",
                        "hosted" : false,
                        "lite" : false
                    },
                    "karma_status" : {
                        "value" : 3075
                    },
                    "address-list" : [
                        {
                            "default" : false,
                            "prohibit-restore" : false,
                            "validated" : true,
                            "native" : true,
                            "rpop" : false,
                            "silent": false,
                            "unsafe" : false,
                            "address" : "test@ya.ru",
                            "born-date" : "2012-04-25 00:00:00"
                        },
                        {
                            "default" : false,
                            "prohibit-restore" : true,
                            "validated" : true,
                            "native" : false,
                            "rpop" : false,
                            "silent": true,
                            "unsafe" : true,
                            "address" : "maillist@maillist.ru",
                            "born-date" : "2015-04-25 00:00:00"
                        }
                    ],
                    "id" : "1",
                    "karma" : {
                        "value" : 100
                    },
                    "login" : "test"
                }
            ]
        }
        ''')
        response = self.blackbox.userinfo(uid=1)

        eq_(response['uid'], 1)
        eq_(len(response['address-list']), 2)

        eq_(
            response['address-list'][0],
            {
                u'rpop': False,
                u'silent': False,
                u'default': False,
                u'unsafe': False,
                u'prohibit-restore': False,
                u'validated': True,
                u'native': True,
                u'address': u'test@ya.ru',
                u'born-date': u'2012-04-25 00:00:00',
            },
        )
        eq_(
            response['address-list'][1],
            {
                u'rpop': False,
                u'silent': True,
                u'default': False,
                u'unsafe': True,
                u'prohibit-restore': True,
                u'validated': True,
                u'native': False,
                u'address': u'maillist@maillist.ru',
                u'born-date': u'2015-04-25 00:00:00',
            },
        )

    def test_parse_with_empty_user(self):
        self.set_blackbox_response_value(u'''
        {
            "users" : [
                {
                    "uid" : {},
                    "id" : "128280859"
                }
            ]
        }''')

        response = self.blackbox.userinfo(uid=1)

        assert_is_none(response['display_login'])
        assert_is_none(response['karma'])
        assert_is_none(response['uid'])
        assert_is_none(response['domain'])
        assert_is_none(response['domid'])
        assert_is_none(response['domain'])

    def test_parse_employee(self):
        self.set_blackbox_response_value(
            '''
            {
                "users" : [
                    {
                        "have_password" : true,
                        "uid" : {
                            "value" : "1",
                            "hosted" : false,
                            "lite" : false
                        },
                        "have_hint" : true,
                        "karma" : {
                            "value" : 0
                        },
                        "login" : "testlogin",
                        "karma_status" : {
                            "value" : 0
                        },
                        "id" : "1",
                        "attributes" : {
                            "12" : "1"
                        }
                    }
                ]
            }
            ''',
        )
        response = self.blackbox.userinfo(uid=1)

        eq_(response['is_employee'], '1')
        ok_('is_maillist' not in response)

    def test_parse_maillist(self):
        self.set_blackbox_response_value(
            '''
            {
                "users" : [
                    {
                        "have_password" : true,
                        "uid" : {
                            "value" : "1",
                            "hosted" : false,
                            "lite" : false
                        },
                        "have_hint" : true,
                        "karma" : {
                            "value" : 0
                        },
                        "login" : "testlogin",
                        "karma_status" : {
                            "value" : 0
                        },
                        "id" : "1",
                        "attributes" : {
                            "13" : "1"
                        }
                    }
                ]
            }
            ''',
        )
        response = self.blackbox.userinfo(uid=1)

        eq_(response['is_maillist'], '1')
        ok_('is_employee' not in response)

    def test_parse_default_email(self):
        self.set_blackbox_response_value(
            '''
            {
                "users" : [
                    {
                        "have_password" : true,
                        "uid" : {
                            "value" : "1",
                            "hosted" : false,
                            "lite" : false
                        },
                        "have_hint" : true,
                        "karma" : {
                            "value" : 0
                        },
                        "login" : "testlogin",
                        "karma_status" : {
                            "value" : 0
                        },
                        "id" : "1",
                        "attributes" : {
                            "14" : "email@default.com"
                        }
                    }
                ]
            }
            ''',
        )
        response = self.blackbox.userinfo(uid=1)

        eq_(response['default_email'], 'email@default.com')

    def test_parse_failed_pin_checks_count(self):
        self.set_blackbox_response_value(
            '''
            {
                "users" : [
                    {
                        "have_password" : true,
                        "uid" : {
                            "value" : "1",
                            "hosted" : false,
                            "lite" : false
                        },
                        "have_hint" : true,
                        "karma" : {
                            "value" : 0
                        },
                        "login" : "testlogin",
                        "karma_status" : {
                            "value" : 0
                        },
                        "id" : "1",
                        "attributes" : {
                            "118" : "2"
                        }
                    }
                ]
            }
            ''',
        )
        response = self.blackbox.userinfo(uid=1)

        eq_(response['totp.failed_pin_checks_count'], 2)
        ok_('totp.update_datetime' not in response)

    def test_parse_totp_update_datetime(self):
        self.set_blackbox_response_value(
            '''
            {
                "users" : [
                    {
                        "have_password" : true,
                        "uid" : {
                            "value" : "1",
                            "hosted" : false,
                            "lite" : false
                        },
                        "have_hint" : true,
                        "karma" : {
                            "value" : 0
                        },
                        "login" : "testlogin",
                        "karma_status" : {
                            "value" : 0
                        },
                        "id" : "1",
                        "attributes" : {
                            "123" : "123456"
                        }
                    }
                ]
            }
            ''',
        )
        response = self.blackbox.userinfo(uid=1)

        eq_(response['totp.update_datetime'], 123456)
        ok_('totp.failed_pin_checks_count' not in response)

    def test_parse_2fa_on(self):
        self.set_blackbox_response_value(
            '''
            {
                "users" : [
                    {
                        "have_password" : true,
                        "uid" : {
                            "value" : "1",
                            "hosted" : false,
                            "lite" : false
                        },
                        "have_hint" : true,
                        "karma" : {
                            "value" : 0
                        },
                        "login" : "testlogin",
                        "karma_status" : {
                            "value" : 0
                        },
                        "id" : "1",
                        "attributes" : {
                            "123" : "123456",
                            "1003": "1"
                        }
                    }
                ]
            }
            ''',
        )
        response = self.blackbox.userinfo(uid=1)

        ok_(response['2fa_on'])
        eq_(response['totp.update_datetime'], 123456)
        ok_('totp.failed_pin_checks_count' not in response)

    def test_parse_without_2fa_on(self):
        self.set_blackbox_response_value(
            '''
            {
                "users" : [
                    {
                        "have_password" : true,
                        "uid" : {
                            "value" : "1",
                            "hosted" : false,
                            "lite" : false
                        },
                        "have_hint" : true,
                        "karma" : {
                            "value" : 0
                        },
                        "login" : "testlogin",
                        "karma_status" : {
                            "value" : 0
                        },
                        "id" : "1",
                        "attributes" : {
                        }
                    }
                ]
            }
            ''',
        )
        response = self.blackbox.userinfo(uid=1)

        ok_('2fa_on' not in response)

    def test_parse_phones_default(self):
        self.set_blackbox_response_value(
            blackbox_userinfo_response(
                uid=1,
                attributes={u'phones.default': u'1'},
            ),
        )

        response = self.blackbox.userinfo(uid=1)

        eq_(response['phones.default'], u'1')

    def test_parse_phones_secure(self):
        self.set_blackbox_response_value(
            blackbox_userinfo_response(
                uid=1,
                attributes={u'phones.secure': u'1'},
            ),
        )

        response = self.blackbox.userinfo(uid=1)

        eq_(response['phones.secure'], u'1')

    def test_parse_is_disabled_always_there(self):
        self.set_blackbox_response_value(
            '''
            {
                "users" : [
                    {
                        "have_password" : true,
                        "uid" : {
                            "value" : "1",
                            "hosted" : false,
                            "lite" : false
                        },
                        "have_hint" : true,
                        "karma" : {
                            "value" : 0
                        },
                        "login" : "testlogin",
                        "karma_status" : {
                            "value" : 0
                        },
                        "id" : "1",
                        "attributes" : {}
                    }
                ]
            }
            ''',
        )
        response = self.blackbox.userinfo(
            uid=1,
            attributes=[],
        )
        ok_('3' not in response['attributes'])

        response = self.blackbox.userinfo(
            uid=1,
            attributes=[
                'account.is_disabled',
            ],
        )
        eq_(response['attributes']['3'], '0')

    def test_account_deletion_operation(self):
        self.set_blackbox_response_value(
            json.dumps({
                'users': [
                    {
                        'id': '1',
                        'uid': {'value': '1'},
                        'attributes': {'153': '3'},
                    },
                ],
            }),
        )

        response = self.blackbox.userinfo(uid=1)

        eq_(
            response.get('account_deletion_operation'),
            {
                'started_at': 3,
            },
        )

    def test_no_account_deletion_operation(self):
        self.set_blackbox_response_value(
            json.dumps({
                'users': [
                    {
                        'id': '1',
                        'uid': {'value': '1'},
                    },
                ],
            }),
        )

        response = self.blackbox.userinfo(uid=1)

        ok_('account_deletion_operation' not in response)

    def test_search_phone_alias_is_set(self):
        self.set_blackbox_response_value(
            blackbox_userinfo_response(
                uid=1,
                attributes={'account.enable_search_by_phone_alias': '1'},
            ),
        )

        response = self.blackbox.userinfo(uid=1)

        eq_(response.get('account.enable_search_by_phone_alias'), '1')

    def test_search_phone_alias_is_unset(self):
        self.set_blackbox_response_value(
            blackbox_userinfo_response(
                uid=1,
                attributes={'account.enable_search_by_phone_alias': '0'},
            ),
        )

        response = self.blackbox.userinfo(uid=1)

        eq_(response.get('account.enable_search_by_phone_alias'), '0')

    def test_search_phone_alias_requested_but_not_in_response(self):
        self.set_blackbox_response_value(blackbox_userinfo_response(uid=1, attributes={}))

        response = self.blackbox.userinfo(
            uid=1,
            attributes=['account.enable_search_by_phone_alias'],
        )

        ok_('account.enable_search_by_phone_alias' not in response)

    def test_parse_family_info(self):
        self.set_blackbox_response_value(
            '''{"users":[{"id":"680","uid":{"value":"680","lite":false,"hosted":false,"domid":"","domain":"","mx":""},
            "family_info":{"admin_uid":"680","family_id":"f1"},
            "aliases":{"1":"test"},"login":"test","karma":{"value":75},"karma_status":{"value":75}}]}''',
        )
        response = self.blackbox.userinfo(uid=680, get_family_info=True)
        eq_(response['family_info'], {'admin_uid': '680', 'family_id': 'f1'})
        ok_('subscriptions' not in response)


@with_settings(
    BLACKBOX_URL='http://test.local/',
    BLACKBOX_FIELDS=[],
    BLACKBOX_ATTRIBUTES=['account.normalized_login'],
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=[u'number', u'created', u'bound'],
)
class TestBlackboxRequestUserInfoRequest(BaseBlackboxTestCase):
    base_params = {
        'userip': '127.0.0.1',
        'regname': 'yes',
        'get_public_name': 'yes',
        'is_display_name_empty': 'yes',
        'method': 'userinfo',
        'format': 'json',
        'aliases': 'all_with_hidden',
        'attributes': '1008',
    }

    def setUp(self):
        super(TestBlackboxRequestUserInfoRequest, self).setUp()
        self._phone_args_assertions = TestPhoneArguments(self._build_request_info)

    def test_userinfo_uid_request(self):
        uid = 5
        request_info = Blackbox().build_userinfo_request(uid)
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'uid': uid}),
        )

    def test_userinfo_uid_request_wo_hidden_aliases(self):
        uid = 5
        request_info = Blackbox().build_userinfo_request(uid, get_hidden_aliases=False)
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'uid': uid, 'aliases': 'all'}),
        )

    def test_userinfo_uids_request(self):
        uids = [1, 2, 3]
        request_info = Blackbox().build_userinfo_request(uids=uids)
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'uid': u','.join(map(str, uids))}),
        )

    def test_userinfo_login_request(self):
        login = 'test'
        request_info = Blackbox().build_userinfo_request(login=login)
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'login': login}),
        )

    def test_userinfo_suid_and_sid_request(self):
        sid, suid = 2, 42
        request_info = Blackbox().build_userinfo_request(sid=sid, suid=suid)
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'suid': suid, 'sid': sid}),
        )

    def test_userinfo_public_id_request(self):
        public_id = 'test'
        request_info = Blackbox().build_userinfo_request(public_id=public_id)
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'public_id': public_id}),
        )

    def test_userinfo_userip_request(self):
        uid = 5
        ip = '0.0.0.0'
        request_info = Blackbox().build_userinfo_request(uid, ip=ip)
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'uid': uid, 'userip': ip}),
        )

    def test_userinfo_override_dbfields(self):
        login = 'test'
        dbfields = ['accounts.ena.uid']
        request_info = Blackbox().build_userinfo_request(
            login=login,
            dbfields=dbfields,
        )
        eq_(
            request_info.post_args,
            merge_dicts(
                self.base_params,
                {'login': login, 'dbfields': u','.join(dbfields)},
            ),
        )

    def test_userinfo_override_dbfields_with_empty_list(self):
        login = 'test'
        request_info = Blackbox().build_userinfo_request(
            login='test',
            dbfields=[],
        )
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'login': login}),
        )

    def test_userinfo_emails(self):
        login = 'test'
        request_info = Blackbox().build_userinfo_request(login='test', emails=True)
        eq_(
            request_info.post_args,
            merge_dicts(
                self.base_params,
                {
                    'login': login,
                    'emails': 'getall',
                },
            ),
        )

    def test_userinfo_email_attributes(self):
        login = 'test'
        request_info = Blackbox().build_userinfo_request(login='test', email_attributes='all')
        eq_(
            request_info.post_args,
            merge_dicts(
                self.base_params,
                {
                    'login': login,
                    'getemails': 'all',
                    'email_attributes': 'all',
                },
            ),
        )

    def test_userinfo_specific_email_attributes(self):
        attributes = [
            'address',
            'created',
            'confirmed',
        ]
        login = 'test'
        request_info = Blackbox().build_userinfo_request(
            login='test',
            email_attributes=attributes,
        )
        eq_(
            request_info.post_args,
            merge_dicts(
                self.base_params,
                {
                    'login': login,
                    'getemails': 'all',
                    'email_attributes': ','.join([
                        str(EMAIL_NAME_MAPPING[attr])
                        for attr in attributes
                    ]),
                },
            ),
        )

    def test_userinfo_get_all_email_attributes(self):
        login = 'test'
        request_info = Blackbox().build_userinfo_request(
            login='test',
            email_attributes='all',
        )
        eq_(
            request_info.post_args,
            merge_dicts(
                self.base_params,
                {
                    'login': login,
                    'getemails': 'all',
                    'email_attributes': 'all',
                },
            ),
        )

    def test_userinfo_get_specific_email_attributes(self):
        login = 'test'
        request_info = Blackbox().build_userinfo_request(
            login='test',
            email_attributes=[
                'address',
                'is_rpop',
            ],
        )
        eq_(
            request_info.post_args,
            merge_dicts(
                self.base_params,
                {
                    'login': login,
                    'getemails': 'all',
                    'email_attributes': ','.join([
                        str(EMAIL_NAME_MAPPING[attr])
                        for attr in ['address', 'is_rpop']
                    ]),
                },
            ),
        )

    def test_userinfo_test_pin(self):
        login = 'test'
        request_info = Blackbox().build_userinfo_request(
            login='test',
            pin_to_test='1234',
        )
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'login': login, 'pintotest': '1234'}),
        )

    def test_userinfo_with_idna_domain(self):
        request_info = Blackbox().build_userinfo_request(
            login=u'test@окна.рф',
        )
        eq_(
            request_info.post_args,
            merge_dicts(
                self.base_params,
                {'login': b'test@\xd0\xbe\xd0\xba\xd0\xbd\xd0\xb0.\xd1\x80\xd1\x84'.decode('utf-8')},
            ),
        )

    def test_userinfo_with_bad_idna_domain(self):
        request_info = Blackbox().build_userinfo_request(
            login=u'test@.рф',
        )
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'login': b'test@.\xd1\x80\xd1\x84'.decode('utf-8')}),
        )

    def test_cyrillic_login(self):
        request_info = Blackbox().build_userinfo_request(
            login=u'тестовыйлогин',
        )
        expected_login = b'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82\xd0\xbe\xd0\xb2\xd1\x8b\xd0\xb9\xd0\xbb\xd0\xbe\xd0\xb3'
        expected_login += b'\xd0\xb8\xd0\xbd'
        expected_login = expected_login.decode('utf-8')
        eq_(
            request_info.post_args,
            merge_dicts(
                self.base_params,
                {
                    'login': expected_login,
                },
            ),
        )

    def test_userinfo_no_aliases(self):
        login = 'test'
        request_info = Blackbox().build_userinfo_request(
            login='test',
            need_aliases=False,
        )

        expected_params = merge_dicts(self.base_params, {'login': login})
        del expected_params['aliases']
        eq_(
            request_info.post_args,
            expected_params,
        )

    def test_userinfo_only_public_aliases(self):
        login = 'test'
        with settings_context(
            BLACKBOX_URL='http://test.local/',
            BLACKBOX_FIELDS=[],
            BLACKBOX_ATTRIBUTES=['account.normalized_login'],
            BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=[u'number', u'created', u'bound'],
            BLACKBOX_GET_HIDDEN_ALIASES=False,
        ):
            request_info = Blackbox().build_userinfo_request(login='test')

        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'login': login, 'aliases': 'all'}),
        )

    @raises(ValueError)
    def test_userinfo_with_no_login_nor_uid_nor_suid(self):
        Blackbox().build_userinfo_request(login=None, uid=None, uids=None, suid=None)

    @raises(ValueError)
    def test_userinfo_with_suid_but_no_sid__error(self):
        Blackbox().build_userinfo_request(login=None, uid=None, uids=None, suid=42)

    @raises(ValueError)
    def test_userinfo_with_wrong_uids(self):
        Blackbox().build_userinfo_request(uids='1,2,3')

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

    def test_userinfo_not_pass_find_by_phone_alias(self):
        request_info = self._build_request_info(find_by_phone_alias=None)
        ok_('find_by_phone_alias' not in request_info.post_args)

    def test_userinfo_pass_find_by_phone_alias(self):
        request_info = self._build_request_info(find_by_phone_alias='xyz')
        eq_(request_info.post_args['find_by_phone_alias'], 'xyz')

    def test_userinfo_pass_country(self):
        request_info = self._build_request_info(country='FR')
        eq_(request_info.post_args['country'], 'FR')

    def test_userinfo_get_billing_features(self):
        login = 'test'
        request_info = Blackbox().build_userinfo_request(
            login='test',
            get_billing_features=True,
        )
        eq_(
            request_info.post_args,
            merge_dicts(
                self.base_params,
                {
                    'login': login,
                    'get_billing_features': 'all',
                },
            ),
        )

    def test_userinfo_family_info_request(self):
        uid = 1
        request_info = Blackbox().build_userinfo_request(
            uid, get_family_info=True)
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'uid': uid, 'get_family_info': 'yes'}),
        )

    def test_userinfo_public_id(self):
        uid = 1
        request_info = Blackbox().build_userinfo_request(
            uid, get_public_id=True)
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'uid': uid, 'get_public_id': 'yes'}),
        )

    def test_userinfo_force_show_mail_subscription(self):
        uid = 1
        request_info = Blackbox().build_userinfo_request(uid, force_show_mail_subscription=True)
        eq_(
            request_info.post_args,
            merge_dicts(self.base_params, {'uid': uid, 'force_show_mail_subscription': 'yes'}),
        )

    def test_userinfo_allow_scholar(self):
        request_info = self._build_request_info(allow_scholar=True)
        assert request_info.post_args['allow_scholar'] == 'yes'

        request_info = self._build_request_info(allow_scholar=False)
        assert 'allow_scholar' not in request_info.post_args

        request_info = self._build_request_info()
        assert 'allow_scholar' not in request_info.post_args

    def _build_request_info(self, **kwargs):
        default_args = {u'uid': 4}
        if not (u'uid' in kwargs or u'uids' in kwargs or u'login' in kwargs):
            kwargs = merge_dicts(default_args, kwargs)
        return Blackbox().build_userinfo_request(**kwargs)


@with_settings(
    BLACKBOX_URL=u'http://bl.ackb.ox/',
    BLACKBOX_ATTRIBUTES=[],
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=[],
)
class RequestTestUserInfoParsePhones(BaseBlackboxTestCase):
    def setUp(self):
        super(RequestTestUserInfoParsePhones, self).setUp()
        self._blackbox = Blackbox()
        self._faker = FakeBlackbox()
        self._faker.start()

    def tearDown(self):
        self._faker.stop()
        del self._faker
        super(RequestTestUserInfoParsePhones, self).tearDown()

    def test_phone_with_empty_attributes_when_response_has_phone_and_empty_attributes(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phones=[{u'id': 22}]),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones=u'all',
            phone_attributes=None,
        )

        eq_(response[u'phones'], {22: {u'id': 22, u'attributes': {}}})

    def test_phone_attribute_phone_number_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': 1, u'number': u'+79036655444'}],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones=u'all',
            phone_attributes=['number'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'number'],
            u'+79036655444',
        )

    def test_phone_attribute_created_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': 1, u'created': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones=u'all',
            phone_attributes=[u'created'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'created'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_bound_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': 1, u'bound': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones=u'all',
            phone_attributes=[u'bound'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'bound'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_confirmed_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': 1, u'confirmed': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones=u'all',
            phone_attributes=[u'confirmed'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'confirmed'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_admitted_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': 1, u'admitted': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones=u'all',
            phone_attributes=[u'admitted'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'admitted'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_secured_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': 1, u'secured': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones=u'all',
            phone_attributes=[u'secured'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'secured'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_is_default_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': 1, u'is_default': 1}],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones=u'all',
            phone_attributes=[u'is_default'],
        )

        ok_(response[u'phones'][1][u'attributes'][u'is_default'])

    def test_operation_id_equals_to_operation_id_from_response(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        ok_(5 in response[u'phone_operations'])
        eq_(response[u'phone_operations'][5][u'id'], 5)

    def test_single_operation_when_response_has_single_operations(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(len(response[u'phone_operations']), 1)

    def test_many_operations_when_response_has_many_operations(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[
                {u'id': 5, u'phone_number': u'+79047766555'},
                {u'id': 6, u'phone_number': u'+79036655444'},
            ]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(len(response[u'phone_operations']), 2)

    def test_operation_phone_id_equals_to_operation_phone_id_from_response(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_id': 7,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id'], 7)

    def test_operation_phone_is_none_when_response_has_not_operation_phone_id(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_id': None,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id'], None)

    def test_operation_security_identity_is_like_phone_number_when_operation_is_not_on_secure_phone_number(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'security_identity'], 79047766555)

    def test_operation_security_identity_is_predefined_value_when_operation_is_on_secure_phone_number(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'security_identity': SECURITY_IDENTITY,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'security_identity'],
            SECURITY_IDENTITY,
        )

    def test_phone_operation_started_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'started': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'started'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_started_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'started': None,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'started'],
            None,
        )

    def test_phone_operation_finished_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'finished': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'finished'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_finished_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'finished': None,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'finished'],
            None,
        )

    def test_phone_operation_code_last_sent_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_last_sent': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'code_last_sent'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_code_last_sent_is_empty_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_last_sent': None,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_last_sent'], None)

    def test_phone_operation_code_confirmed_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_confirmed': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'code_confirmed'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_code_confirmed_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_confirmed': None,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'code_confirmed'],
            None,
        )

    def test_phone_operation_password_verified_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'password_verified': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'password_verified'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_password_verified_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'password_verified': None,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'password_verified'],
            None,
        )

    def test_phone_operation_code_send_count_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_send_count': 7,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_send_count'], 7)

    def test_phone_operation_code_send_count_is_zero_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_send_count': None,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_send_count'], 0)

    def test_phone_operation_phone_id2_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'phone_id2': 31,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id2'], 31)

    def test_phone_operation_phone_id2_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'phone_id2': None,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id2'], None)

    def test_phone_operation_flags_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'flags': PhoneOperationFlags(1),
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'flags'],
            int(PhoneOperationFlags(1)),
        )

    def test_phone_operation_flags_equals_to_zero_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'flags': None,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'flags'],
            int(PhoneOperationFlags(0)),
        )

    def test_phone_operation_code_checks_count_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_checks_count': 16,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_checks_count'], 16)

    def test_phone_operation_code_checks_count_is_zero_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_checks_count': None,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_checks_count'], 0)

    def test_phone_operation_code_value_equals_to_response_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_value': u'1234',
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_value'], u'1234')

    def test_phone_operation_code_value_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_value': None,
            }]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_value'], None)

    def test_phone_operation_is_attached_to_phone(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
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

        response = self._blackbox.userinfo(uid=1)

        ok_(response[u'phones'][14][u'operation'] is response[u'phone_operations'][5])

    def test_no_phones_and_no_phone_operations_when_response_has_no_phone_and_no_phone_operations(self):
        self._faker.set_response_value(u'userinfo', blackbox_userinfo_response())

        response = self._blackbox.userinfo(uid=1)

        ok_(u'phones' not in response)
        ok_(u'phone_operations' not in response)

    def test_empty_phones_when_response_has_empty_phones(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phones=[]),
        )

        response = self._blackbox.userinfo(uid=1, phones=u'all')

        ok_(u'phones' in response)
        eq_(len(response[u'phones']), 0)

    def test_no_phones_and_empty_operations_when_response_has_no_phones_and_empty_operations(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phone_operations=[]),
        )

        response = self._blackbox.userinfo(uid=1, need_phone_operations=True)

        ok_(u'phones' not in response)
        ok_(u'phone_operations' in response)
        eq_(len(response[u'phone_operations']), 0)

    def test_no_operation_in_phone_when_response_has_phone_and_no_operation(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(phones=[{u'id': 14}]),
        )

        response = self._blackbox.userinfo(uid=1, phones=u'all')

        ok_(u'phones' in response)
        ok_(u'phone_operations' not in response)
        ok_(u'operation' not in response[u'phones'][14])

    def test_phone_operation_is_on_phone_when_response_has_phone_and_operation_on_it(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': 14}],
                phone_operations=[{
                    u'id': 5,
                    u'phone_id': 14,
                    u'phone_number': u'+79047766555',
                }],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(u'phones' in response)
        ok_(u'phone_operations' in response)
        ok_(u'operation' in response[u'phones'][14])

    def test_phone_operation_on_phone_is_none_when_response_has_phones_and_empty_operations(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': 14}],
                phone_operations=[],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(u'phones' in response)
        ok_(u'phone_operations' in response)
        ok_(response[u'phones'][14][u'operation'] is None)

    def test_phone_operation_is_in_phone_operations_and_phone_operation_on_phone_is_none_when_response_has_zombie_operation(self):
        self._faker.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': 14}],
                phone_operations=[{
                    u'id': 5,
                    u'phone_id': 15,
                    u'phone_number': u'+79047766555',
                }],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(response[u'phones'][14][u'operation'] is None)
        ok_(5 in response[u'phone_operations'])

    def test_no_phone_bindings(self):
        self._faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': TEST_PHONE_ID1}],
            ),
        )

        response = self._blackbox.userinfo(uid=1, phones='all')

        ok_('phone_bindings' not in response)
        ok_('binding' not in response['phones'][TEST_PHONE_ID1])

    def test_empty_phone_bindings(self):
        self._faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': TEST_PHONE_ID1}],
                phone_bindings=[],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones='all',
            need_current_phone_bindings=True,
            need_unbound_phone_bindings=True,
        )

        eq_(response['phone_bindings'], [])
        eq_(response['phones'][TEST_PHONE_ID1]['binding'], None)

    def test_has_current_phone_binding(self):
        flags = PhoneBindingsFlags()
        flags.should_ignore_binding_limit = True

        self._faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': TEST_PHONE_ID1}],
                phone_bindings=[
                    {
                        'uid': 1,
                        'type': 'current',
                        'number': TEST_PHONE_NUMBER1.e164,
                        'phone_id': TEST_PHONE_ID1,
                        'bound': TEST_TIME1,
                        'flags': flags,
                    },
                ],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones='all',
            need_current_phone_bindings=True,
        )

        binding = {
            'uid': 1,
            'type': 'current',
            'phone_number': TEST_PHONE_NUMBER1,
            'phone_id': TEST_PHONE_ID1,
            'binding_time': to_unixtime(TEST_TIME1),
            'should_ignore_binding_limit': 1,
        }

        eq_(response['phone_bindings'], [binding])
        eq_(response['phones'][TEST_PHONE_ID1]['binding'], binding)

    def test_has_unbound_phone_binding(self):
        flags = PhoneBindingsFlags()

        self._faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': TEST_PHONE_ID1}],
                phone_bindings=[
                    {
                        'uid': 1,
                        'type': 'unbound',
                        'number': TEST_PHONE_NUMBER1.e164,
                        'phone_id': TEST_PHONE_ID1,
                        'bound': None,
                        'flags': flags,
                    },
                ],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones='all',
            need_unbound_phone_bindings=True,
        )

        binding = {
            'uid': 1,
            'type': 'unbound',
            'phone_number': TEST_PHONE_NUMBER1,
            'phone_id': TEST_PHONE_ID1,
            'binding_time': 0,
            'should_ignore_binding_limit': 0,
        }

        eq_(response['phone_bindings'], [binding])
        eq_(response['phones'][TEST_PHONE_ID1]['binding'], binding)

    def test_has_orphan_phone_binding(self):
        self._faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                phones=[{u'id': TEST_PHONE_ID1}],
                phone_bindings=[
                    {
                        'uid': 1,
                        'type': 'current',
                        'phone_id': TEST_PHONE_ID2,
                    },
                ],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones='all',
            need_current_phone_bindings=True,
        )

        eq_(len(response['phone_bindings']), 1)
        eq_(response['phones'][TEST_PHONE_ID1]['binding'], None)

    def test_complex_orphan_phone_operation(self):
        self._faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                phones=[{'id': 14}],
                phone_operations=[
                    {
                        'id': 5,
                        'phone_id': 15,
                        'phone_number': '+79047766555',
                        'phone_id2': 14,
                    },
                    {
                        'id': 6,
                        'phone_id': 14,
                        'phone_number': '+79047766555',
                        'phone_id2': 15,
                    },
                ],
            ),
        )

        response = self._blackbox.userinfo(
            uid=1,
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(response[u'phones'][14][u'operation'] is None)
        ok_(5 in response[u'phone_operations'])
        ok_(6 in response[u'phone_operations'])


@with_settings(
    BLACKBOX_URL=u'http://bl.ackb.ox/',
    BLACKBOX_ATTRIBUTES=[],
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=[],
)
class RequestTestUserInfoParseEmails(BaseBlackboxTestCase):
    def setUp(self):
        super(RequestTestUserInfoParseEmails, self).setUp()
        self._blackbox = Blackbox()
        self._faker = FakeBlackbox()
        self._faker.start()

    def tearDown(self):
        self._faker.stop()
        del self._faker
        super(RequestTestUserInfoParseEmails, self).tearDown()

    def test_parse_no_emails_in_response(self):
        self._faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=1),
        )
        response = self._blackbox.userinfo(uid=1, emails='all')

        ok_('emails' not in response)

    def test_parse_emails_get_instances(self):
        self._faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=1,
                email_attributes=[
                    {
                        'attributes': {
                            EMAIL_NAME_MAPPING['created']: '12345',
                            EMAIL_NAME_MAPPING['bound']: '12346',
                            EMAIL_NAME_MAPPING['confirmed']: '12346',
                            EMAIL_NAME_MAPPING['address']: 'test@test.ru',
                            EMAIL_NAME_MAPPING['is_rpop']: '1',
                            EMAIL_NAME_MAPPING['is_silent']: '1',
                            EMAIL_NAME_MAPPING['is_unsafe']: '1',
                        },
                        'id': 123,
                    },
                ],
            ),
        )
        response = self._blackbox.userinfo(uid=1, emails='all')

        ok_('emails' in response)
        eq_(
            response['emails'],
            [
                {
                    'created': '12345',
                    'confirmed': '12346',
                    'unsafe': '1',
                    'silent': '1',
                    'rpop': '1',
                    'address': 'test@test.ru',
                    'bound': '12346',
                    'id': 123,
                },
            ],
        )
