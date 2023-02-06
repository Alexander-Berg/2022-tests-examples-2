# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
import json
from time import time
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from nose_parameterized import parameterized
from passport.backend.core.builders.base.base import RequestInfo
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_userinfo_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.differ import (
    diff,
    Diff,
)
from passport.backend.core.eav_type_mapping import (
    ALIAS_NAME_TO_TYPE,
    ATTRIBUTE_NAME_TO_TYPE as AT,
)
from passport.backend.core.models.account import (
    Account,
    ACCOUNT_DISABLED,
    ACCOUNT_DISABLED_ON_DELETION,
    ACCOUNT_ENABLED,
    get_preferred_language,
    UnknownUid,
)
from passport.backend.core.models.faker.account import default_account
from passport.backend.core.models.phones.faker import PhoneIdGeneratorFaker
from passport.backend.core.models.phones.phones import Phones
from passport.backend.core.models.webauthn import WebauthnCredentials
from passport.backend.core.services import Service
from passport.backend.core.test.consts import (
    TEST_LOGIN1,
    TEST_PLUS_SUBSCRIBER_STATE1_BASE64,
    TEST_PLUS_SUBSCRIBER_STATE1_JSON,
    TEST_REGISTRAION_DATETIME1,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.time_utils.time_utils import unixtime
from passport.backend.core.types.account.account import (
    ACCOUNT_TYPE_FEDERAL,
    ACCOUNT_TYPE_KIDDISH,
    ACCOUNT_TYPE_KINOPOISK,
    ACCOUNT_TYPE_KOLONKISH,
    ACCOUNT_TYPE_LITE,
    ACCOUNT_TYPE_MAILISH,
    ACCOUNT_TYPE_NEOPHONISH,
    ACCOUNT_TYPE_NORMAL,
    ACCOUNT_TYPE_PDD,
    ACCOUNT_TYPE_SCHOLAR,
    ACCOUNT_TYPE_SOCIAL,
    ACCOUNT_TYPE_UBER,
    ACCOUNT_TYPE_YAMBOT,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.core.types.display_name import DisplayName
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.types.question import Question
from passport.backend.core.undefined import Undefined
from passport.backend.utils.time import (
    datetime_to_unixtime,
    get_unixtime,
)


TEST_UID = 123
TEST_PDD_UID = 1130000000000003
TEST_PHONE_NUMBER = PhoneNumber.parse('+79033123456')
TEST_PHONE_NUMBER2 = PhoneNumber.parse('+79026411724')
TEST_TIMESTAMP = unixtime(2000, 1, 23, 12, 34, 56)
TEST_DISPLAY_NAME = DisplayName(u'ДисплауНаме')


class TestAccount(TestCase):
    def test_set_unknown_field(self):
        acc = Account()
        with assert_raises(AttributeError):
            acc.unknown_field = 'value'

    def test_web_sessions_logout_datetime(self):
        acc = default_account(uid=TEST_UID)
        ok_(acc.web_sessions_logout_datetime is None)

        acc.global_logout_datetime = datetime.fromtimestamp(100)
        eq_(acc.web_sessions_logout_datetime, datetime.fromtimestamp(100))

        acc.web_sessions_revoked_at = datetime.fromtimestamp(101)
        eq_(acc.web_sessions_logout_datetime, datetime.fromtimestamp(101))

        acc.web_sessions_revoked_at = datetime.fromtimestamp(100)
        eq_(acc.web_sessions_logout_datetime, datetime.fromtimestamp(100))

    def test_account_without_aliases(self):
        acc = Account()
        with assert_raises(ValueError):
            ok_(acc.type)

    def test_set_portal_alias(self):
        acc = default_account(alias='phne-test', alias_type='phonish')
        acc.set_portal_alias('login')
        eq_(acc.login, 'login')
        eq_(acc.type, ACCOUNT_TYPE_NORMAL)
        ok_(acc.is_normal)

    def test_account_has_sid(self):
        acc = default_account()
        acc.parse({'uid': 10, 'subscriptions': {8: {'sid': 8, 'login_rule': 5}, 10: {'sid': 10}}})
        ok_(acc.has_sid(10))
        ok_(not acc.has_sid(100))

    def test_account_subscribed_but_has_not_sid(self):
        acc = default_account()
        acc.parse({
            'uid': 10,
            'subscriptions': {
                10: {'sid': 10},
            },
            'aliases': {
                '9': 'login@galatasaray.net',
            },
        })
        ok_(acc.is_subscribed(Service.by_sid(10)))
        ok_(acc.has_sid(10))
        ok_(acc.is_subscribed(Service.by_sid(61)))
        ok_(not acc.has_sid(61))

    def test_account_is_subscribed(self):
        acc = default_account()
        acc.parse({'uid': 10, 'subscriptions': {8: {'sid': 8, 'login_rule': 5}, 10: {'sid': 10}}})
        ok_(acc.is_subscribed(Service.by_sid(10)))
        ok_(not acc.is_subscribed(Service.by_sid(100)))

    @raises(ValueError)
    def test_account_is_subscribed_bad_service(self):
        acc = default_account()
        acc.parse({'uid': 10, 'subscriptions': {8: {'sid': 8, 'login_rule': 5}, 10: {'sid': 10}}})
        ok_(acc.is_subscribed(10))

    def test_account_have_password(self):
        acc = default_account(uid=10)
        acc.password.encrypted_password = 'abc'
        ok_(acc.have_password)

        acc = Account().parse({})
        acc.totp_secret.is_set = True
        ok_(acc.have_password)
        acc.password.encrypted_password = 'abc'
        ok_(acc.have_password)

    def test_account_is_password_set_or_promised(self):
        acc = default_account(uid=10)
        ok_(not acc.is_password_set_or_promised)
        acc.password.encrypted_password = 'abc'
        ok_(acc.is_password_set_or_promised)

        acc = Account().parse({})
        acc.totp_secret.is_set = True
        ok_(acc.is_password_set_or_promised)
        acc.password.encrypted_password = 'abc'
        ok_(acc.is_password_set_or_promised)

        acc = Account().parse({})
        acc.password.set('password', 1, get_hash_from_blackbox=True)
        ok_(not acc.have_password)
        ok_(acc.is_password_set_or_promised)

        # Значение после удаления пароля или 2фа-секрета
        acc = Account().parse({})
        acc.password = None
        ok_(not acc.is_password_set_or_promised)

        acc = Account().parse({})
        acc.totp_secret = None
        ok_(not acc.is_password_set_or_promised)

    def test_is_logouted_after(self):
        acc = default_account(uid=10)
        eq_(acc.is_logouted_after(datetime.now()), False)

        now = datetime.now()
        acc = Account().parse({'uid': 10, 'global_logout_datetime': datetime_to_unixtime(now)})
        eq_(acc.is_logouted_after(now - timedelta(seconds=1)), True)
        eq_(acc.is_logouted_after(now + timedelta(seconds=1)), False)

        now = datetime.now()
        acc = Account().parse({'uid': 10, 'revoker.web_sessions': datetime_to_unixtime(now)})
        eq_(acc.is_logouted_after(now - timedelta(seconds=1)), True)
        eq_(acc.is_logouted_after(now + timedelta(seconds=1)), False)

    def test_account_is_incomplete_autoregistered(self):
        acc = default_account()
        ok_(not acc.is_incomplete_autoregistered)

        acc.password.is_creating_required = True
        ok_(acc.is_incomplete_autoregistered)

        pdd_acc = default_account(alias_type='pdd')
        ok_(not pdd_acc.is_incomplete_autoregistered)

        pdd_acc.password.is_creating_required = True
        ok_(not pdd_acc.is_incomplete_autoregistered)


class TestAccountParse(TestCase):

    def test_basic_parse(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "dbfields": { "userinfo.reg_date.uid": "2013-09-17 18:27:12" },
            "attributes": { "3": "0", "1008": "test" },
            "aliases": {"1": "test", "9": "test@galatasaray.net"}}]
            }''',
        )
        acc = Account().parse(response)
        eq_(acc.uid, 3000062912)
        eq_(acc.registration_datetime, datetime(2013, 9, 17, 18, 27, 12))
        eq_(acc.karma.value, 85)
        eq_(acc.subscriptions, Undefined)
        eq_(acc.type, ACCOUNT_TYPE_NORMAL)
        eq_(acc.domain.id, Undefined)
        eq_(acc.domain.domain, None)
        eq_(acc.domain.is_enabled, Undefined)
        eq_(acc.is_user_enabled, True)
        eq_(acc.display_login, 'test')
        ok_(acc.is_subscribed(Service.by_sid(61)))

    def test_is_disabled_with_default_value(self):
        mocked_request = RequestInfo(
            url='userinfo',
            get_args=None,
            post_args={
                'attributes': '3',
            },
        )
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "dbfields": { "userinfo.reg_date.uid": "2013-09-17 18:27:12" },
            "attributes": { "1008": "test" },
            "aliases": {"1": "test"}}]
            }''',
            request=mocked_request,
        )
        acc = Account().parse(response)
        eq_(acc.disabled_status, ACCOUNT_ENABLED)
        eq_(acc.is_enabled, True)
        eq_(acc.is_user_enabled, True)

    def test_is_disabled_not_returned_by_bb(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "dbfields": { "userinfo.reg_date.uid": "2013-09-17 18:27:12" },
            "attributes": { "1008": "test" },
            "aliases": {"1": "test"}}]
            }''',
        )
        acc = Account().parse(response)
        eq_(acc.disabled_status, Undefined)
        eq_(acc.is_user_enabled, False)

    def test_repeated_collection_parse(self):
        acc = Account()

        acc.parse({'uid': 10, 'subscriptions': {8: {'sid': 8, 'login_rule': 5}, 10: {'sid': 10}}})

        eq_(acc.uid, 10)
        eq_(len(acc.subscriptions), 2)

        acc.parse({'subscriptions': {12: {'sid': 12}, 8: {'sid': 8}}})

        eq_(acc.uid, 10)
        eq_(len(acc.subscriptions), 3)
        ok_(8 in acc.subscriptions)
        ok_(10 in acc.subscriptions)
        ok_(12 in acc.subscriptions)
        ok_(not acc.subscriptions[8].login_rule)

    def test_repeated_with_domain_info_parse(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"%s", "lite":false, "domid":"12345", "domain":"okna.ru", "mx":"", "domain_ena":"1" },
            "login":"test@domain.ru",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "dbfields": { "accounts.ena.uid": "1" },
            "attributes": { "3": "0", "1008": "test" },
            "aliases": {"7": "test@domain.ru"}}]
            }''' % TEST_PDD_UID)
        acc = Account().parse(response)

        eq_(acc.uid, TEST_PDD_UID)
        eq_(acc.karma.value, 85)
        eq_(acc.type, ACCOUNT_TYPE_PDD)
        eq_(acc.domain.id, 12345)
        eq_(acc.domain.domain, 'okna.ru')
        eq_(acc.domain.is_enabled, True)
        eq_(acc.is_user_enabled, True)
        eq_(acc.domain.can_users_change_password, True)

        response = get_parsed_blackbox_response(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                domid=12345,
                domain='okna.ru',
                is_enabled=True,
                can_users_change_password=False,
            ),
        )
        acc.parse(response)

        eq_(acc.uid, TEST_PDD_UID)
        eq_(acc.karma.value, 85)
        eq_(acc.type, ACCOUNT_TYPE_PDD)
        eq_(acc.domain.id, 12345)
        eq_(acc.domain.domain, 'okna.ru')
        eq_(acc.domain.is_enabled, True)
        eq_(acc.is_user_enabled, True)
        eq_(acc.domain.can_users_change_password, False)

    def test_repeated_with_domain_info_parse_login(self):
        response = get_parsed_blackbox_response(
            'login_v2',
            json.dumps({
                "login_status": {"value": "VALID", "id": 1},
                "password_status": {"value": "VALID", "id": 1},
                "comment": "OK",
                "uid": {
                    "value": "1130000000038100",
                    "lite": False,
                    "hosted": True,
                    "domid": "30964",
                    "domain": "l.uda-test.ru",
                    "mx": "0",
                    "domain_ena": "1",
                    "catch_all": False
                },
                "login": "robbitter-2536251723@l.uda-test.ru",
                "have_password": True,
                "have_hint": True,
                "karma": {"value": 0},
                "karma_status": {"value": 0},
                "regname": "robbitter-2536251723@l.uda-test.ru",
                "display_name": {"name": "robbitter-2536251723@l.uda-test.ru"},
                "dbfields": {
                    "accounts.ena.uid": "1",
                    "password_quality.quality.uid": "90",
                    "password_quality.version.uid": "3",
                    "subscription.host_id.16": "4",
                    "subscription.host_id.2": "4",
                    "subscription.login.2": "robbitter-2536251723@l.uda-test.ru",
                    "subscription.login.8": "robbitter-2536251723@l.uda-test.ru",
                    "subscription.login_rule.2": "1",
                    "subscription.login_rule.8": "1",
                    "subscription.suid.102": "1",
                    "subscription.suid.16": "1130000000087752",
                    "subscription.suid.2": "1130000000087752",
                    "subscription.suid.8": "1",
                    "userinfo.reg_date.uid": "2014-04-18 16:42:14",
                    "userinfo.sex.uid": "1",
                    "userinfo_safe.hinta.uid": "\\u0424\\u0430\\u043C\\u0438\\u043B\\u0438\\u044F",
                    "userinfo_safe.hintq.uid": "12:\\u0424\\u0430\\u043C\\u0438\\u043B\\u0438\\u044F "
                                               "\\u0432\\u0430\\u0448\\u0435\\u0433\\u043E "
                                               "\\u043B\\u044E\\u0431\\u0438\\u043C\\u043E\\u0433\\u043E "
                                               "\\u043C\\u0443\\u0437\\u044B\\u043A\\u0430\\u043D\\u0442\\u0430",
                },
                "attributes": {
                    "100": "CAESCAgBEJ3ggZ0F",
                    "1003": "1",
                    "1008": "robbitter-2536251723",
                    "35": "",
                    "36": "",
                    "19": "1:$1$GRWQ8jpo$oPC04yvpd2.DqpLnEFD2z0",
                },
                "aliases": {"7": "test@domain.ru"},
                "address-list": [{
                    "address": "robbitter-2536251723@l.uda-test.ru",
                    "validated": True,
                    "default": True,
                    "prohibit-restore": False,
                    "rpop": False,
                    "unsafe": False,
                    "native": True,
                    "born-date": "2014-04-18 16:42:14"
                },  {
                    "address": "robbitter-2536251723@luda-test.alias",
                    "validated": True,
                    "default": False,
                    "prohibit-restore": False,
                    "rpop": False,
                    "unsafe": False,
                    "native": True,
                    "born-date": "2014-04-18 16:42:14"
                }],
            }, indent=4)
        )
        acc = Account().parse(response)
        snapshot = acc.snapshot()
        response = get_parsed_blackbox_response(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                domid=30964,
                domain='l.uda-test.ru',
                is_enabled=True,
                can_users_change_password=False,
            ),
        )
        acc.parse(response)
        differ = diff(snapshot, acc)

        eq_(
            differ.added,
            {
                'domain': {
                    'master_domain': '',
                    'registration_datetime': datetime(2010, 10, 12, 15, 3, 24),
                    'default_uid': 0,
                    'type': 'M',
                    'admin_uid': 42,
                },
            },
        )

        eq_(differ.changed.get('domain'), {'can_users_change_password': False})

        for key in differ.changed:
            if key != 'domain':
                eq_(differ.changed[key], {})

        eq_(differ.deleted, {})

    def test_repeated_with_bad_domain_info_parse(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"%s", "lite":false, "domid":"12345", "domain":"okna.ru", "mx":"", "domain_ena":"1" },
            "login":"test@domain.ru",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "dbfields": { "accounts.ena.uid": "1" },
            "attributes": { "1008": "test" },
            "aliases": {"7": "test@domain.ru"}}]}''' % TEST_PDD_UID)
        acc = Account().parse(response)

        eq_(acc.domain.can_users_change_password, True)

        response = get_parsed_blackbox_response(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='0',
                options_json='{a{b}',
            ),
        )
        acc.parse(response)

        eq_(acc.domain.can_users_change_password, True)

    def test_account_person_1(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users": [
            {
                "dbfields": {
                    "accounts.ena.uid": "1",
                    "userinfo.sex.uid": "1"
                },
                "attributes": {
                    "3": "0",
                    "27": "\\u0414",
                    "28": "\\u0424",
                    "30": "1963-05-15",
                    "33": "Europe/Moscow",
                    "34": "ru",
                    "1008": "test"
                },
                "aliases": {"1": "fel"},
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
                },
                "display_name": {
                    "name": ""
                } } ] }''')

        acc = Account().parse(response)

        eq_(acc.uid, 10)
        eq_(acc.is_enabled, True)
        eq_(acc.is_user_enabled, True)
        eq_(acc.person.parent, acc)
        eq_(acc.person.firstname, u'Д')
        eq_(acc.person.lastname, u'Ф')
        eq_(acc.person.display_name.name, '')
        eq_(acc.person.gender, 1)
        eq_(acc.person.timezone.zone, 'Europe/Moscow')
        eq_(acc.person.language, 'ru')

    def test_account_person_2(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users": [
            {
                "dbfields": {
                    "accounts.ena.uid": "1",
                    "userinfo.sex.uid": null
                },
                "attributes": {
                    "3": "0",
                    "27": "\\u0414",
                    "28": "\\u0424",
                    "30": "1963-05-15",
                    "33": "Europe/Moscow",
                    "34": "ru",
                    "1008": "test"
                },
                "aliases": {"1": "fel"},
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
                } } ] }''')

        acc = Account().parse(response)

        eq_(acc.uid, 10)
        eq_(acc.is_enabled, 1)
        eq_(acc.is_user_enabled, True)
        eq_(acc.person.parent, acc)
        eq_(acc.person.firstname, u'Д')
        eq_(acc.person.lastname, u'Ф')
        eq_(acc.person.display_name, Undefined)
        eq_(acc.person.gender, None)
        eq_(acc.person.timezone.zone, 'Europe/Moscow')
        eq_(acc.person.language, 'ru')
        eq_(acc.person.city, Undefined)

    def test_type_normal(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"1", "lite":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "attributes": { "1008": "test" },
            "aliases": { "%d": "test" }}]}''' % ALIAS_NAME_TO_TYPE['portal'])
        acc = Account().parse(response)

        eq_(acc.uid, 1)
        eq_(acc.karma.value, 85)
        eq_(acc.type, ACCOUNT_TYPE_NORMAL)
        ok_(acc.is_normal)

    def test_type_pdd(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{"users":[{
            "uid": { "value": "%s", "lite":false, "domid":"12345", "domain":"okna.ru", "mx":"", "domain_ena":"1" },
            "login":"test@domain.ru",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "dbfields": { "accounts.ena.uid": "1" },
            "attributes": { "%d": "0", "%d": "test" },
            "aliases": { "%d": "test@domain.ru" }
            }]}''' % (
                TEST_PDD_UID,
                AT['account.is_disabled'],
                AT['account.normalized_login'],
                ALIAS_NAME_TO_TYPE['pdd'],
            ),
        )

        acc = Account().parse(response)

        eq_(acc.uid, TEST_PDD_UID)
        eq_(acc.karma.value, 85)
        eq_(acc.type, ACCOUNT_TYPE_PDD)
        ok_(acc.is_pdd)
        eq_(acc.domain.id, 12345)
        eq_(acc.domain.domain, 'okna.ru')
        eq_(acc.domain.is_enabled, True)
        eq_(acc.is_user_enabled, True)

    def test_type_lite(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"1", "lite":false, "domid":"", "domain":"", "mx":"" },
            "login":"test@domain.ru",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "attributes": { "%d": "test@domain.ru" },
            "aliases": { "%d": "test@domain.ru" }}]}''' % (AT['account.normalized_login'], ALIAS_NAME_TO_TYPE['lite']))
        acc = Account().parse(response)

        eq_(acc.uid, 1)
        eq_(acc.karma.value, 85)
        eq_(acc.type, ACCOUNT_TYPE_LITE)
        ok_(acc.is_lite)

    def test_type_social(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"1", "lite":false, "domid":"", "domain":"", "mx":"" },
            "login":"uid-test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "attributes": { "%d": "uid-test" },
            "aliases": { "%d": "uid-test" }}]}''' % (AT['account.normalized_login'], ALIAS_NAME_TO_TYPE['social']))
        acc = Account().parse(response)

        eq_(acc.uid, 1)
        eq_(acc.karma.value, 85)
        eq_(acc.type, ACCOUNT_TYPE_SOCIAL)
        ok_(acc.is_social)

    def test_type_mailish(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"1", "lite":false, "domid":"", "domain":"", "mx":"" },
            "login":"test@domain.ru",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "attributes": { "%d": "test@domain.ru" },
            "aliases": { "%d": "test@domain.ru" }}]}''' % (AT['account.normalized_login'], ALIAS_NAME_TO_TYPE['mailish']))
        acc = Account().parse(response)

        eq_(acc.uid, 1)
        eq_(acc.karma.value, 85)
        eq_(acc.type, ACCOUNT_TYPE_MAILISH)
        ok_(acc.is_mailish)

    def test_type_kinopoisk(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"1", "lite":false, "domid":"", "domain":"", "mx":"" },
            "login":"",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "aliases": { "%d": "100500" }}]}''' % ALIAS_NAME_TO_TYPE['kinopoisk'])
        acc = Account().parse(response)

        eq_(acc.uid, 1)
        eq_(acc.karma.value, 85)
        eq_(acc.type, ACCOUNT_TYPE_KINOPOISK)
        ok_(acc.is_kinopoisk)

    def test_type_uber(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "id":"1",
            "uid":{"value":"1","lite":false,"hosted":false},
            "login":"228a0c5a1c394f17758663d92451b50a",
            "have_password":false,
            "have_hint":false,
            "aliases":{"%d":"228a0c5a1c394f17758663d92451b50a"},
            "karma":{"value":0},
            "karma_status":{"value":0}}]}
            ''' % ALIAS_NAME_TO_TYPE['uber'])

        acc = Account().parse(response)

        eq_(acc.uid, 1)
        eq_(acc.type, ACCOUNT_TYPE_UBER)
        eq_(acc.login, '228a0c5a1c394f17758663d92451b50a')
        ok_(acc.is_uber)

    def test_type_yambot(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "id":"1",
            "uid":{"value":"1","lite":false,"hosted":false},
            "login":"yambot-bot",
            "have_password":false,
            "have_hint":false,
            "aliases":{"%d":"yambot-bot"},
            "karma":{"value":0},
            "karma_status":{"value":0}}]}
            ''' % ALIAS_NAME_TO_TYPE['yambot'])

        acc = Account().parse(response)

        eq_(acc.uid, 1)
        eq_(acc.type, ACCOUNT_TYPE_YAMBOT)
        eq_(acc.login, 'yambot-bot')
        ok_(acc.is_yambot)

    def test_type_kolonkish(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
                    "id":"1",
                    "uid":{"value":"1","lite":false,"hosted":false},
                    "login":"kolonkish-123",
                    "have_password":false,
                    "have_hint":false,
                    "aliases":{"%d":"kolonkish-123"},
                    "attributes":{"%d": "123"},
                    "karma":{"value":0},
                    "karma_status":{"value":0}}]}
                    ''' % (ALIAS_NAME_TO_TYPE['kolonkish'], AT['account.creator_uid']))

        acc = Account().parse(response)

        eq_(acc.uid, 1)
        eq_(acc.type, ACCOUNT_TYPE_KOLONKISH)
        eq_(acc.login, 'kolonkish-123')
        ok_(acc.is_kolonkish)
        eq_(acc.creator_uid, 123)

    def test_type_neophonish(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
                    "id":"1",
                    "uid":{"value":"1","lite":false,"hosted":false},
                    "login":"nphne-PJAicnaocOAPINSCOPANScp",
                    "have_password":false,
                    "have_hint":false,
                    "aliases":{"%d":"nphne-PJAicnaocOAPINSCOPANScp"},
                    "karma":{"value":0},
                    "karma_status":{"value":0}}]}
                    ''' % ALIAS_NAME_TO_TYPE['neophonish'])

        acc = Account().parse(response)

        eq_(acc.uid, 1)
        eq_(acc.type, ACCOUNT_TYPE_NEOPHONISH)
        eq_(acc.login, 'nphne-PJAicnaocOAPINSCOPANScp')
        ok_(acc.is_neophonish)

    def test_type_kiddish(self):
        content_rating_class = 2
        music_content_rating_class = 3
        video_content_rating_class = 4

        response = blackbox_userinfo_response(
            aliases=dict(kiddish=TEST_LOGIN1),
            attributes={
                'account.content_rating_class': str(content_rating_class),
                'account.music_content_rating_class': str(music_content_rating_class),
                'account.video_content_rating_class': str(video_content_rating_class),
            },
            birthdate=None,
            city=None,
            dbfields={
                'userinfo.reg_date.uid': TEST_REGISTRAION_DATETIME1,
            },
            display_name=TEST_DISPLAY_NAME.as_dict(),
            firstname=None,
            gender=None,
            lastname=None,
            login=TEST_LOGIN1,
            uid=TEST_UID,
        )
        a = Account().parse(get_parsed_blackbox_response('userinfo', response))

        eq_(a.uid, TEST_UID)
        eq_(a.type, ACCOUNT_TYPE_KIDDISH)
        ok_(a.is_kiddish)
        eq_(a.login, TEST_LOGIN1)
        eq_(a.registration_datetime, datetime.strptime(TEST_REGISTRAION_DATETIME1, '%Y-%m-%d %H:%M:%S'))
        eq_(a.person.display_name, TEST_DISPLAY_NAME)
        eq_(a.content_rating_class, content_rating_class)
        eq_(a.music_content_rating_class, music_content_rating_class)
        eq_(a.video_content_rating_class, video_content_rating_class)

    def test_account_with_subscriptions(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login": "test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname": "test",
            "attributes": { "%d": "2" },
            "dbfields": { "subscription.suid.3": "50",
            "subscription.login_rule.3" : "1", "subscription.suid.5": "20"}}]}''' % AT['subscription.mail.status'])
        acc = Account().parse(response)

        eq_(acc.subscriptions[3].suid, 50)
        eq_(acc.subscriptions[3].service.sid, 3)
        eq_(acc.subscriptions[3].login_rule, 1)
        eq_(acc.subscriptions[5].suid, 20)
        eq_(acc.subscriptions[5].service.sid, 5)
        eq_(acc.mail_status, 2)

    def test_account_with_phonenumber_alias(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "aliases": { "11": "79096841646" }
            }]}''')
        acc = Account().parse(response)

        eq_(acc.phonenumber_alias.number, PhoneNumber.parse('+79096841646'))

    def test_empty_subscription_not_created(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "dbfields": { "subscription.suid.3": "50",
            "subscription.login_rule.3" : "1", "subscription.suid.5": ""}}]}''')
        acc = Account().parse(response)

        ok_(3 in acc.subscriptions)
        ok_(5 not in acc.subscriptions)

    def test_account_with_no_subscriptions(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "dbfields": { "subscription.suid.3": "",
            "subscription.login_rule.3" : "", "subscription.suid.5": ""}}]}''')
        acc = Account().parse(response)

        eq_(acc.subscriptions, {})

    def test_account_with_browser_key(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "attributes":{"%d":"key"}}]}''' % AT['account.browser_key'])
        acc = Account().parse(response)

        eq_(acc.browser_key.key, u'key')

    def test_account_with_family_pay(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{{"users":[{{
                    "uid": {{ "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" }},
                    "login":"test",
                    "karma": {{ "value":85, "allow-until":1321965947 }},
                    "karma_status": {{ "value":85 }},
                    "regname":"test",
                    "attributes":{{
                        "{family_pay_enabled}":"eda,mail"
                    }} }} ] }}'''.format(
                family_pay_enabled=AT['account.family_pay.enabled'],
            ),
        )
        acc = Account().parse(response)
        assert acc.family_pay_enabled == 'eda,mail'

    def test_account_with_plus(self):
        ts_1 = get_unixtime()
        ts_2 = get_unixtime() - 3600
        ts_3 = get_unixtime() - 3600 * 2
        ts_4 = get_unixtime() - 3600 * 3

        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{{"users":[{{
                    "uid": {{ "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" }},
                    "login":"test",
                    "karma": {{ "value":85, "allow-until":1321965947 }},
                    "karma_status": {{ "value":85 }},
                    "regname":"test",
                    "attributes":{{
                        "{plus_enabled}":"1",
                        "{have_plus}":"1",
                        "{plus_trial_used_ts}": "{ts_1}",
                        "{plus_subscription_stopped_ts}": "{ts_2}",
                        "{plus_subscription_expire_ts}": "{ts_3}",
                        "{plus_next_charge_ts}": "{ts_4}",
                        "{plus_ott_subscription}": "ott-subscription",
                        "{plus_family_role}": "family-role",
                        "{plus_cashback_enabled}": "1",
                        "{plus_subscription_level}": "3",
                        "{plus_is_frozen}": "1",
                        "{plus_subscriber_state}": "{plus_subscriber_state_value}"
                    }} }} ] }}'''.format(
                plus_enabled=AT['account.plus.enabled'],
                have_plus=AT['account.have_plus'],
                plus_trial_used_ts=AT['account.plus.trial_used_ts'], ts_1=ts_1,
                plus_subscription_stopped_ts=AT['account.plus.subscription_stopped_ts'], ts_2=ts_2,
                plus_subscription_expire_ts=AT['account.plus.subscription_expire_ts'], ts_3=ts_3,
                plus_next_charge_ts=AT['account.plus.next_charge_ts'], ts_4=ts_4,
                plus_ott_subscription=AT['account.plus.ott_subscription'],
                plus_family_role=AT['account.plus.family_role'],
                plus_cashback_enabled=AT['account.plus.cashback_enabled'],
                plus_subscription_level=AT['account.plus.subscription_level'],
                plus_is_frozen=AT['account.plus.is_frozen'],
                plus_subscriber_state=AT['account.plus.subscriber_state'],
                plus_subscriber_state_value=TEST_PLUS_SUBSCRIBER_STATE1_BASE64,
            ),
        )
        acc = Account().parse(response)

        eq_(acc.plus.enabled, True)
        eq_(acc.plus.trial_used_ts, datetime.fromtimestamp(ts_1))
        eq_(acc.plus.subscription_stopped_ts, datetime.fromtimestamp(ts_2))
        eq_(acc.plus.subscription_expire_ts, datetime.fromtimestamp(ts_3))
        eq_(acc.plus.next_charge_ts, datetime.fromtimestamp(ts_4))
        eq_(acc.plus.ott_subscription, 'ott-subscription')
        eq_(acc.plus.has_plus, True)
        eq_(acc.plus.family_role, 'family-role')
        eq_(acc.plus.cashback_enabled, True)
        eq_(acc.plus.subscription_level, 3)
        eq_(acc.plus.is_frozen, True)
        eq_(acc.plus.subscriber_state, TEST_PLUS_SUBSCRIBER_STATE1_JSON)

    def test_account_with_default_email(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "attributes":{"%d":"email"}}]}''' % AT['account.default_email'])
        acc = Account().parse(response)

        eq_(acc.default_email, u'email')

        # проверим, что повторный парсинг не портит значение атрибута
        response = get_parsed_blackbox_response(
            'hosted_domains',
            blackbox_hosted_domains_response(),
        )
        acc.parse(response)
        eq_(acc.default_email, u'email')

    def test_parse_account_with_new_bb_response(self):
        response = get_parsed_blackbox_response('userinfo', u'''{
            "users" : [
                {
                    "dbfields" : {
                        "subscription.suid.53" : "",
                        "subscription.suid.84" : "",
                        "subscription.suid.49" : "",
                        "userinfo_safe.hinta.uid" : "asdf",
                        "subscription.suid.76" : "",
                        "subscription.suid.47" : "",
                        "subscription.login_rule.44" : "",
                        "userinfo.sex.uid" : "0",
                        "password_quality.quality.uid" : "90",
                        "password_quality.version.uid" : "3",
                        "subscription.suid.670" : "",
                        "subscription.suid.27" : "",
                        "subscription.suid.77" : "",
                        "subscription.login_rule.100" : "",
                        "subscription.host_id.36" : "",
                        "subscription.suid.24" : "",
                        "subscription.suid.19" : "",
                        "userinfo_safe.hintq.uid" : "1:Девичья фамилия матери",
                        "subscription.suid.80" : "",
                        "subscription.suid.26" : "",
                        "subscription.suid.83" : "",
                        "subscription.suid.48" : "",
                        "subscription.suid.42" : "",
                        "subscription.suid.59" : "",
                        "subscription.suid.668" : "",
                        "subscription.suid.58" : "",
                        "subscription.suid.40" : "",
                        "subscription.login.68" : "",
                        "subscription.suid.41" : "",
                        "subscription.suid.87" : "",
                        "subscription.suid.88" : "",
                        "subscription.suid.100" : "",
                        "subscription.login_rule.2" : "",
                        "subscription.suid.9" : "",
                        "subscription.suid.85" : "",
                        "subscription.login.2" : "",
                        "subscription.suid.31" : "",
                        "subscription.suid.23" : "",
                        "subscription.suid.68" : "",
                        "subscription.suid.672" : "",
                        "subscription.host_id.16" : "",
                        "subscription.suid.86" : "",
                        "subscription.suid.30" : "",
                        "subscription.suid.54" : "",
                        "subscription.login.89" : "",
                        "subscription.suid.16" : "",
                        "subscription.suid.13" : "",
                        "userinfo.reg_date.uid" : "2013-11-01 16:28:56",
                        "subscription.login.58" : "",
                        "subscription.suid.33" : "",
                        "subscription.suid.78" : "",
                        "subscription.suid.6" : "",
                        "subscription.suid.51" : "",
                        "subscription.suid.67" : "",
                        "subscription.suid.57" : "",
                        "subscription.suid.55" : "",
                        "subscription.suid.102" : "",
                        "subscription.host_id.2" : "",
                        "subscription.host_id.42" : "",
                        "subscription.suid.17" : "",
                        "subscription.login.33" : "",
                        "subscription.suid.38" : "",
                        "subscription.login_rule.27" : "",
                        "subscription.suid.1000" : "",
                        "subscription.suid.90" : "",
                        "subscription.suid.671" : "",
                        "subscription.suid.39" : "",
                        "subscription.suid.52" : "",
                        "subscription.suid.5" : "",
                        "subscription.suid.60" : "",
                        "subscription.suid.2" : "",
                        "subscription.suid.29" : "",
                        "subscription.login.16" : "",
                        "subscription.suid.64" : "",
                        "subscription.suid.89" : "",
                        "subscription.suid.14" : "",
                        "subscription.suid.104" : "",
                        "accounts.ena.uid" : "1",
                        "subscription.suid.37" : "",
                        "subscription.login_rule.8" : "1",
                        "subscription.suid.25" : "",
                        "subscription.suid.666" : "",
                        "subscription.login.8" : "yandex-team2027348362",
                        "subscription.suid.36" : "",
                        "subscription.suid.81" : "",
                        "subscription.suid.44" : "",
                        "subscription.suid.8" : "1",
                        "subscription.suid.667" : "",
                        "subscription.suid.3" : "",
                        "subscription.suid.50" : ""
                    },
                    "attributes":{
                        "35": "",
                        "36": "",
                        "19": "1:$1$vJj6XuIb$BIcfkx/kDmYBeGk25anho/"
                    },
                    "have_password" : true,
                    "uid" : {
                        "value" : "3000348554",
                        "hosted" : false,
                        "lite" : false
                    },
                    "have_hint" : true,
                    "karma" : {
                        "value" : 100,
                        "allow-until" : 1383310535
                    },
                    "login" : "yandex-team2027348362",
                    "karma_status" : {
                        "value" : 100
                    },
                    "id" : "3000348554",
                    "display_name" : {
                        "name": "display",
                        "public_name": "public"
                    }
                }
            ]
        }
        ''')
        acc = Account().parse(response)

        eq_(acc.uid, 3000348554)
        eq_(acc.subscriptions[8].login_rule, 1)
        eq_(acc.person.display_name.name, 'display')
        eq_(acc.person.display_name.public_name, 'public')
        eq_(acc.phonenumber_alias.number, Undefined)

    @raises(UnknownUid)
    def test_account_with_empty_user(self):
        response = get_parsed_blackbox_response('userinfo', u'''
        {
            "users" : [
                {
                    "uid" : {},
                    "id" : "128280859"
                }
            ]
        }''')

        Account().parse(response)

    def test_parse_failed_pin_checks(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(attributes={'account.totp.failed_pin_checks_count': 12}),
        )
        acc = Account().parse(response)
        eq_(acc.totp_secret.failed_pin_checks_count, 12)

        # протестируем, что повторный парсинг не затирает значение поля
        response = get_parsed_blackbox_response(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='0'),
        )
        acc.parse(response)
        eq_(acc.totp_secret.failed_pin_checks_count, 12)

    def test_account_with_global_logout(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "regname":"test",
            "attributes":{
                "%d":"1247",
                "%d":"1247",
                "%d":"1247",
                "%d":"1247"
            }}]}''' % (
                AT['account.global_logout_datetime'],
                AT['revoker.tokens'],
                AT['revoker.app_passwords'],
                AT['revoker.web_sessions'],
            ),
        )
        acc = Account().parse(response)

        timestamp = datetime.fromtimestamp(1247)
        eq_(acc.global_logout_datetime, timestamp)
        eq_(acc.tokens_revoked_at, timestamp)
        eq_(acc.app_passwords_revoked_at, timestamp)
        eq_(acc.web_sessions_revoked_at, timestamp)

    def test_auth_email_datetime(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "regname":"test",
            "attributes":{
                "%d":"1247"
            }}]}''' % AT['account.auth_email_datetime'],
        )
        acc = Account().parse(response)
        eq_(acc.auth_email_datetime, datetime.fromtimestamp(1247))

    def test_is_money_agreement_accepted(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "regname":"test",
            "attributes":{
                "%d":"1"
            }}]}''' % AT['account.is_money_agreement_accepted'],
        )
        acc = Account().parse(response)
        ok_(acc.is_money_agreement_accepted)

    def test_failed_auth_challenge_checks_counter(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(
                attributes={
                    'account.failed_auth_challenge_checks_counter': '7:%d' % (time() + 100),
                },
            ),
        )
        acc = Account().parse(response)
        ok_(not acc.failed_auth_challenge_checks_counter.is_expired)
        eq_(acc.failed_auth_challenge_checks_counter.value, 7)

    def test_failed_auth_challenge_checks_counter_empty(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(
                attributes={},
            ),
        )
        acc = Account().parse(response)
        eq_(acc.failed_auth_challenge_checks_counter.value, 0)

    def test_additional_data_asked(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "regname":"test",
            "attributes":{
                "%d":"phone",
                "%d":"9090"
            }}]}''' % (
                AT['account.additional_data_asked'],
                AT['account.additional_data_ask_next_datetime'],
            ),
        )
        acc = Account().parse(response)
        eq_(acc.additional_data_asked, 'phone')
        eq_(acc.additional_data_ask_next_datetime, datetime.fromtimestamp(9090))

    def test_external_organization_ids(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(
                attributes={
                    'account.external_organization_ids': '1,3,2',
                },
            ),
        )
        acc = Account().parse(response)
        eq_(acc.external_organization_ids, {1, 2, 3})

    def test_billing_features(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{
                "users":[{
                    "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
                    "login":"test",
                    "regname":"test",
                    "billing_features": {
                        "100% cashback": {
                            "brand": "brand",
                            "in_trial": true,
                            "paid_trial": false,
                            "region_id": 0,
                            "trial_duration": 0
                        },
                        "Music_Premium": {
                            "region_id": 9999
                        }
                    }
                }]
            }
            ''',
        )
        acc = Account().parse(response)
        eq_(
            acc.billing_features,
            {
                u'Music_Premium': {u'region_id': 9999},
                u'100% cashback': {
                    u'paid_trial': False,
                    u'in_trial': True,
                    u'region_id': 0,
                    u'trial_duration': 0,
                    u'brand': 'brand',
                }
            }
        )

    def test_family_info(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(family_info={'family_id': 'f1', 'admin_uid': 1}),
        )
        acc = Account().parse(response)
        eq_(acc.family_info.family_id, 'f1')
        eq_(acc.family_info.admin_uid, 1)
        ok_(acc.has_family)

    def test_empty_family_info(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            u'''{"users":[{
                "uid": { "value":"1", "lite":false, "domid":"", "domain":"", "mx":"" },
                "login":"test",
                "karma": { "value":85, "allow-until":1321965947 },
                "karma_status": { "value":85 },
                "family_info": {},
                "regname":"test",
                "aliases": { "%d": "test" }}]}''' % ALIAS_NAME_TO_TYPE['portal'],
        )
        acc = Account().parse(response)
        ok_(not acc.family_info)
        ok_(not acc.has_family)

    def test_type_scholar(self):
        scholar_login = u'вовочка'
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(aliases=dict(scholar=scholar_login)),
        )
        acc = Account().parse(response)

        assert acc.is_scholar
        assert acc.login == scholar_login
        assert acc.scholar_alias.alias == scholar_login
        assert acc.type == ACCOUNT_TYPE_SCHOLAR


class TestAccountDeletionOperation(TestCase):
    def test_ok(self):
        account = Account()
        started_at = unixtime(2012, 12, 12, 13, 13, 13)

        account.parse({'account_deletion_operation': {'started_at': started_at}})

        ok_(account.deletion_operation)
        eq_(account.deletion_operation.started_at, datetime.fromtimestamp(started_at))

    def test_no_started_at(self):
        account = Account()

        with assert_raises(KeyError):
            account.parse({'account_deletion_operation': {}})
        ok_(not account.deletion_operation)

    def test_no_operation(self):
        account = Account()
        account.parse({})
        ok_(not account.deletion_operation)


class TestAccountProperties(TestCase):
    def setUp(self):
        self._phone_id_faker = PhoneIdGeneratorFaker()
        self._phone_id_faker.start()
        self._phone_id_faker.set_list(range(100, 105))

    def tearDown(self):
        self._phone_id_faker.stop()
        del self._phone_id_faker

    def test_account_sid_properties(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "dbfields": {"subscription.suid.668": "20"}}]}''')
        acc = Account().parse(response)

        eq_(acc.is_betatester, True)
        eq_(acc.is_yandexoid, False)

    def test_account_multiple_sid_properties(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "dbfields": {"subscription.suid.668": "20"}}]}''')
        acc = Account().parse(response)

        eq_(acc.is_betatester, True)

    def test_account_set_sid_property(self):
        response = get_parsed_blackbox_response('userinfo', u'''{"users":[{
            "uid": { "value":"3000062912", "lite":false, "hosted":false, "domid":"", "domain":"", "mx":"" },
            "login":"test",
            "karma": { "value":85, "allow-until":1321965947 },
            "karma_status": { "value":85 },
            "regname":"test",
            "dbfields": {"subscription.suid.668": "20"}}]}''')
        acc = Account().parse(response)

        eq_(acc.is_betatester, True)

        acc.is_betatester = False
        eq_(acc.is_betatester, False)
        ok_(668 not in acc.subscriptions)

    def test_account_readable_login(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login='test-test',
                dbfields={'subscription.login.8': 'test.test'},
            ),
        )

        acc = Account().parse(response)
        eq_(acc.human_readable_login, u'test.test')
        eq_(acc.machine_readable_login, 'test-test')

    def test_account_readable_login_pdd(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_PDD_UID,
                login=u'test-test@xn--80atjc.xn--p1ai',
                dbfields={'subscription.login.8': 'test.test'},
                aliases={
                    'pdd': u'test-test@окна.рф',
                },
            ),
        )
        acc = Account().parse(response)
        eq_(acc.human_readable_login, u'test-test@окна.рф')
        eq_(acc.machine_readable_login, 'test-test@xn--80atjc.xn--p1ai')

    def test_account_normalized_login_pdd_portalized_blackbox(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_PDD_UID,
                login=u'test-test@окна.рф',
                dbfields={'subscription.login.8': 'test.test'},
                aliases={
                    'pdd': u'test-test@окна.рф',
                },
            ),
        )
        acc = Account().parse(response)
        eq_(acc.normalized_login, u'test-test')

    def test_account_is_pdd_admin(self):
        acc = Account().parse({
            'uid': 1,
            'subscriptions': {
                '8': {'suid': '1', 'login': 'login', 'sid': 8},
            },
            'aliases': {
                str(ALIAS_NAME_TO_TYPE['pdd']): u'login@окна.рф',
            },
        })
        acc.is_pdd_admin = True
        ok_(104 in acc.subscriptions)

    def test_account_is_pdd_workspace_user(self):
        acc = Account().parse({
            'uid': 1,
            'subscriptions': {
                '8': {'suid': '1', 'login': 'login', 'sid': 8},
            },
            'aliases': {
                str(ALIAS_NAME_TO_TYPE['pdd']): u'login@окна.рф',
            },
            'have_organization_name': '1',
        })
        ok_(acc.is_pdd_workspace_user)
        ok_(not acc.is_connect_admin)

    def test_account_is_connect_admin(self):
        acc = Account().parse({
            'uid': 1,
            'subscriptions': {
                '8': {'suid': '1', 'login': 'login', 'sid': 8},
            },
            'aliases': {
                str(ALIAS_NAME_TO_TYPE['pdd']): u'login@окна.рф',
            },
            'account.is_connect_admin': '1',
        })
        ok_(acc.is_connect_admin)

    def test_account_is_complete_pdd(self):
        acc = Account().parse({
            'uid': TEST_PDD_UID,
            'subscriptions': {
                '8': {'suid': '1', 'login': 'login', 'sid': 8},
            },
            'aliases': {
                str(ALIAS_NAME_TO_TYPE['pdd']): u'login@окна.рф',
            },
        })
        eq_(acc.uid, TEST_PDD_UID)
        eq_(acc.type, ACCOUNT_TYPE_PDD)
        ok_(not acc.is_complete_pdd)

        acc.is_pdd_agreement_accepted = True
        ok_(102 in acc.subscriptions)
        ok_(not acc.is_complete_pdd)

        acc.person.firstname = 'Firstname'
        ok_(not acc.is_complete_pdd)

        acc.person.lastname = 'Lastname'
        ok_(not acc.is_complete_pdd)

        acc.hint.answer = 'answer'
        ok_(not acc.is_complete_pdd)

        acc.hint.question = Question(u'Тестовый вопрос', 99)
        ok_(acc.is_complete_pdd)

    def test_account_is_complete_pdd_phone_old_scheme(self):
        r"""
        У пользователя есть телефон в старой схеме Я.СМС, и нет КВ\КО
        """

        acc = Account().parse({
            'uid': TEST_PDD_UID,
            'subscriptions': {
                '8': {'suid': '1', 'login': 'login', 'sid': 8},
            },
            'aliases': {
                str(ALIAS_NAME_TO_TYPE['pdd']): u'login@окна.рф',
            },
        })
        acc.is_pdd_agreement_accepted = True
        acc.person.firstname = 'Firstname'
        acc.person.lastname = 'Lastname'
        acc.phones.secure = acc.phones.create(
            number=TEST_PHONE_NUMBER,
            confirmed=datetime(2000, 1, 2, 12, 34, 56),
            secured=datetime(2000, 1, 2, 12, 34, 56),
            bound=datetime(2000, 1, 2, 12, 34, 56),
        )
        ok_(acc.is_complete_pdd)

    def test_account_is_complete_pdd_phone_new_scheme(self):
        r"""
        У пользователя есть телефон в новой схеме Я.СМС, и нет КВ\КО
        """
        acc = Account().parse({
            'uid': TEST_PDD_UID,
            'subscriptions': {
                '8': {'suid': '1', 'login': 'login', 'sid': 8},
            },
            'aliases': {
                str(ALIAS_NAME_TO_TYPE['pdd']): u'login@окна.рф',
            },
        })
        acc.is_pdd_agreement_accepted = True
        acc.person.firstname = 'Firstname'
        acc.person.lastname = 'Lastname'
        acc.phones = Phones().parse({
            'uid': 1,
            'phones.secure': 1,
            'phones': {
                1: {
                    'id': 1,
                    'attributes': {
                        'number': TEST_PHONE_NUMBER.e164,
                        'bound': TEST_TIMESTAMP,
                        'secured': TEST_TIMESTAMP,
                        'confirmed': TEST_TIMESTAMP,
                    },
                },
            },
        })
        ok_(acc.is_complete_pdd)

    def test_account_is_complete_pdd_workspace_user(self):
        acc = Account().parse({
            'uid': TEST_PDD_UID,
            'subscriptions': {
                '8': {'suid': '1', 'login': 'login', 'sid': 8},
            },
            'aliases': {
                str(ALIAS_NAME_TO_TYPE['pdd']): u'login@окна.рф',
            },
            'have_organization_name': '1',
        })
        eq_(acc.uid, TEST_PDD_UID)
        eq_(acc.type, ACCOUNT_TYPE_PDD)
        ok_(not acc.is_complete_pdd)
        ok_(acc.is_pdd_workspace_user)

        acc.is_pdd_agreement_accepted = True
        ok_(102 in acc.subscriptions)
        ok_(acc.is_complete_pdd)

    def test_account_is_complete_federal(self):
        acc = Account().parse({
            'uid': TEST_PDD_UID,
            'subscriptions': {
                '8': {'suid': '1', 'login': 'login', 'sid': 8},
            },
            'aliases': {
                str(ALIAS_NAME_TO_TYPE['pdd']): u'login@окна.рф',
                str(ALIAS_NAME_TO_TYPE['federal']): u'login@окна.рф',
            },
        })
        eq_(acc.type, ACCOUNT_TYPE_FEDERAL)
        ok_(not acc.is_complete_federal)

        acc.is_pdd_agreement_accepted = True
        ok_(acc.is_complete_federal)

    @raises(TypeError)
    def test_account_is_complete_federal_for_not_federal(self):
        acc = default_account().parse({
            'uid': 1,
            'subscriptions': {
                '8': {'suid': '1', 'login': 'login', 'sid': 8},
            },
        })
        acc.is_complete_federal

    def test_account_is_enabled_getter(self):
        """
        Проверяем, что значение свойства is_enabled зависит от
        атрибута disabled_status.
        """
        acc = default_account()
        for status, expected in [
            (ACCOUNT_ENABLED, True),
            (ACCOUNT_DISABLED, False),
            (ACCOUNT_DISABLED_ON_DELETION, False),
            (Undefined, False),
        ]:
            acc.disabled_status = status
            eq_(acc.is_enabled, expected)

    def test_account_is_enabled_setter(self):
        """
        Проверяем, что установка значения свойства is_enabled автоматически
        меняет значение атрибута disabled_status.
        """
        acc = default_account()
        for value, expected_status in [
            (True, ACCOUNT_ENABLED),
            (False, ACCOUNT_DISABLED),
            (None, ACCOUNT_DISABLED),
            (Undefined, ACCOUNT_DISABLED),
        ]:
            acc.is_enabled = value
            eq_(acc.disabled_status, expected_status)

    @raises(TypeError)
    def test_account_is_complete_pdd_for_not_pdd(self):
        acc = default_account().parse({
            'uid': 1,
            'subscriptions': {
                '8': {'suid': '1', 'login': 'login', 'sid': 8},
            },
        })
        acc.is_complete_pdd

    @parameterized.expand(
        [
            ('audience_on', 'audience_on'),
            ('is_shared', 'is_shared'),
            ('enable_app_password', 'enable_app_password'),
            ('magic_link_login_forbidden', 'account.magic_link_login_forbidden'),
            ('qr_code_login_forbidden', 'account.qr_code_login_forbidden'),
            ('sms_code_login_forbidden', 'account.sms_code_login_forbidden'),
            ('takeout.subscription', 'takeout.subscription'),
            ('is_easily_hacked', 'account.is_easily_hacked'),
            ('force_challenge', 'account.force_challenge'),
            ('plus.cashback_enabled', 'account.plus.cashback_enabled'),
            ('plus.is_frozen', 'account.plus.is_frozen'),
            ('sms_2fa_on', 'account.sms_2fa_on'),
            ('forbid_disabling_sms_2fa', 'account.forbid_disabling_sms_2fa'),
            ('is_verified', 'account.is_verified'),
            ('is_child', 'account.is_child'),
            ('hide_yandex_domains_emails', 'account.hide_yandex_domains_emails'),
            ('takeout.delete_subscription', 'takeout.delete.subscription'),
            ('personal_data_public_access_allowed', 'account.personal_data_public_access_allowed'),
            ('personal_data_third_party_processing_allowed', 'account.personal_data_third_party_processing_allowed'),
        ]
    )
    def test_boolean_flag_change(self, model_field_name, blackbox_attribute_name):
        def get_account_attribute(account, attribute_path):
            temp_obj = account
            for attr_key in attribute_path.split('.'):
                temp_obj = getattr(temp_obj, attr_key)

            return temp_obj

        acc = Account().parse({'login': 'test'})
        eq_(get_account_attribute(acc, model_field_name), Undefined)

        acc = Account().parse({
            'login': 'test',
            blackbox_attribute_name: '1',
        })
        eq_(get_account_attribute(acc, model_field_name), True)

        acc = Account().parse({
            'login': 'test',
            blackbox_attribute_name: '0',
        })
        eq_(get_account_attribute(acc, model_field_name), False)


class TestAccountEmails(TestCase):
    def test_undefined_emails(self):
        response = get_parsed_blackbox_response('userinfo', '''
        {
            "users" : [
                {
                    "uid" : {
                        "value" : "11",
                        "hosted" : false,
                        "lite" : false
                    },
                    "karma_status" : {
                        "value" : 3075
                    },
                    "id" : "11",
                    "karma" : {
                        "value" : 100
                    },
                    "login" : "test"
                }
            ]
        }
        ''')

        acc = Account().parse(response)

        eq_(acc.uid, 11)
        eq_(list(acc.emails.all), [])


class TestAccountPhones(TestCase):
    """
    Базовые тесты на то, что парсер подели телефона подключился и
    правильно обрабатывает основные случаи.
    """
    def test_account_without_phones(self):
        data = {
            'uid': 1,
        }
        acc = Account().parse(data)

        ok_(isinstance(acc.phones, Phones))
        eq_(acc.phones.all(), {})

    def test_simple_account_phones_diff(self):
        """
        Добавим аккаунт и посмотрим на полученный diff.
        """
        data = {
            'uid': 1,
            'phones': {
                1: {
                    'id': 1,
                    'attributes': {
                        u'number': '+79030915478',
                    },
                    'operation': {
                        'type': 'optype',
                        'started': unixtime(2000, 1, 23, 12, 34, 56),
                    },
                },
            },
        }

        acc = Account().parse(data)

        snapshot = acc.snapshot()

        acc.phones.remove(1)

        phone = {
            'number': PhoneNumber.parse('+79030915478'),
            'id': 1,
            'operation': {
                'started': datetime(2000, 1, 23, 12, 34, 56),
                'type': 'optype',
                'flags': PhoneOperationFlags(0),
                'code_checks_count': 0,
                'code_send_count': 0,
            },
        }

        eq_(diff(acc, snapshot), Diff({'phones': {'_phones': {1: phone}}}, {}, {}))


class TestAccountWebauthnCredentials(TestCase):
    def test_account_without_creds(self):
        data = {
            'uid': 1,
        }
        acc = Account().parse(data)

        ok_(isinstance(acc.webauthn_credentials, WebauthnCredentials))
        eq_(acc.webauthn_credentials.all(), [])

    def test_account_with_creds(self):
        data = {
            'uid': 1,
            'webauthn_credentials': [
                {
                    'id': 1,
                    'attributes': {
                        'external_id': 'cred-id',
                    },
                },
            ],
        }
        acc = Account().parse(data)

        eq_(len(acc.webauthn_credentials.all()), 1)


@with_settings(
    DISPLAY_LANGUAGES=['ru', 'en', 'uk'],
    ALL_SUPPORTED_LANGUAGES={
        'all': ['ru', 'en', 'uk', 'zh'],
        'default': 'ru',
    },
)
class TestGetPreferredLanguage(TestCase):
    def test_has_language(self):
        """
        Возвращается язык, предпочитаемый пользователем.
        """
        account = Account().parse({'person.language': 'en'})
        eq_(get_preferred_language(account), u'en')

    def test_no_language(self):
        """
        Возвращается русский язык, когда пользователь не предпочёл какого-либо
        языка.
        """
        account = Account()
        eq_(get_preferred_language(account), u'ru')

    def test_unavailable_language(self):
        """
        Возвращается русский язык, когда пользователь предпочитает неизвестный
        Яндексу язык.
        """
        account = Account().parse({'person.language': 'zh'})
        eq_(get_preferred_language(account), u'ru')

    def test_selected_language(self):
        """
        Язык, переданный в ручку, приоритетней языка на модели.
        """
        account = Account().parse({'person.language': 'en'})
        eq_(get_preferred_language(account, 'uk'), u'uk')

    def test_unavailable_selected_language(self):
        """
        Возвращается русский язык, когда в ручку передаётся неизвестный Яндексу язык.
        """
        account = Account().parse({'person.language': 'en'})
        eq_(get_preferred_language(account, 'zh'), u'ru')
