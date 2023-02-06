# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
from functools import partial
import json
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS,
    BLACKBOX_CHECK_RFC_TOTP_INVALID_STATUS,
    BLACKBOX_CHECK_RFC_TOTP_VALID_STATUS,
    BLACKBOX_LOGIN_V1_SHOW_CAPTCHA_STATUS,
    BLACKBOX_SESSIONID_DISABLED_STATUS,
    BLACKBOX_SESSIONID_EXPIRED_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    SECURITY_IDENTITY,
)
from passport.backend.core.builders.blackbox.exceptions import AccessDenied
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_ip_response,
    blackbox_check_rfc_totp_response,
    blackbox_create_oauth_token_response,
    blackbox_create_pwd_hash_response,
    blackbox_createsession_response,
    blackbox_deletion_operations_response,
    blackbox_edit_totp_response,
    blackbox_editsession_delete_empty_response,
    blackbox_editsession_response,
    blackbox_family_info_response,
    blackbox_find_pdd_accounts_response,
    blackbox_generate_public_id_response,
    blackbox_get_all_tracks_response,
    blackbox_get_hosts_response,
    blackbox_get_oauth_tokens_response,
    blackbox_get_recovery_keys_response,
    blackbox_get_track_response,
    blackbox_hosted_domains_response,
    blackbox_json_error_response,
    blackbox_login_response,
    blackbox_lrandoms_response,
    blackbox_oauth_response,
    blackbox_phone_bindings_response,
    blackbox_phone_operations_response,
    blackbox_pwdhistory_response,
    blackbox_sessionid_multi_append_invalid_session,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_sessionid_response,
    blackbox_test_pwd_hashes_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
    blackbox_webauthn_credentials_response,
    blackbox_yakey_backup_response,
    BlackboxYasmsConfigurator,
    FakeBlackbox,
)
from passport.backend.core.builders.blackbox.parsers import parse_phone_operation
from passport.backend.core.eav_type_mapping import (
    ATTRIBUTE_NAME_TO_TYPE as AT,
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_ANT,
    EXTENDED_ATTRIBUTES_WEBAUTHN_NAME_TO_TYPE_MAPPING as WEBAUTHN_ANT,
)
from passport.backend.core.test.test_utils import (
    iterdiff,
    with_settings,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    TimeNow,
    unixtime,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.bit_vector.bit_vector import (
    PhoneBindingsFlags,
    PhoneOperationFlags,
)
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime


__all__ = (
    'FakeBlackboxTestCase',
    'TestBlackboxYasmsConfigurator',
    'TestLoginResponse',
    'TestOauthResponse',
    'TestPhoneBindingsResponse',
    'TestSessionidMultiSessionManySessionsResponse',
    'TestSessionidMultiSessionSingleSessionResponse',
    'TestSessionidResponse',
    'TestUserinfoResponse',
)

TEST_EMAIL1 = 'yehlo@isis.us'
TEST_EMAIL_ID1 = 911
TEST_UNIXTIME1 = 946674000
TEST_UNIXTIME2 = 978296400
TEST_UNIXTIME3 = 1009918800


UID_ALPHA = 7227
UID_BETA = 3711
PHONE_NUMBER_ALPHA = u'+79076655444'
PHONE_NUMBER_BETA = u'+79043322111'
TEST_DATE = datetime(2104, 12, 22, 10, 54, 23)
MINUTE = timedelta(minutes=1)
PHONE_ID1 = 13

TEST_FAMILY_INFO = {'admin_uid': str(UID_ALPHA), 'family_id': 'f71'}

eq_ = iterdiff(eq_)


def _check_login_forms_in_userinfo_response(userinfo_response, login, display_login=None):
    user = userinfo_response['users'][0]
    display_login = display_login if display_login is not None else login
    eq_(user['login'], display_login)
    eq_(user['dbfields']['subscription.login.8'], display_login or login)
    eq_(user['attributes'][str(AT['account.normalized_login'])], login)


@with_settings_hosts(
    BLACKBOX_URL='http://localhost/',
    BLACKBOX_ATTRIBUTES=[],
)
class FakeBlackboxTestCase(TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()
        self.fake_blackbox = FakeBlackbox()
        self.fake_blackbox.start()

    def tearDown(self):
        self.fake_blackbox.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_blackbox
        del self.fake_tvm_credentials_manager

    def test_blackbox_userinfo_login_forms_for_portal_user(self):
        """Проверяем формы логина в ответе ЧЯ для портального пользователя"""
        normal_response = json.loads(
            blackbox_userinfo_response(
                uid=1,
                login='test-login',
                display_login='Test.Login',
            ),
        )
        _check_login_forms_in_userinfo_response(normal_response, login='test-login', display_login='Test.Login')

    def test_blackbox_userinfo_login_forms_for_pdd_user(self):
        """Проверяем формы логина в ответе ЧЯ для ПДД-пользователя"""
        pdd_response = json.loads(
            blackbox_userinfo_response(
                uid=11300000000000001,
                domid=1,
                login=u'test_login@окна.рф',
                aliases={
                    'pdd': u'test_login@окна.рф',
                },
                display_login=u'123',  # Для ПДД неприменимо
            ),
        )
        _check_login_forms_in_userinfo_response(pdd_response, login=u'test_login@окна.рф')
        eq_(pdd_response['users'][0]['uid']['domain'], u'xn--80atjc.xn--p1ai')

    def test_blackbox_userinfo_login_forms_for_lite_user(self):
        """Проверяем формы логина в ответе ЧЯ для лайт-пользователя"""
        lite_response = json.loads(
            blackbox_userinfo_response(
                uid=1,
                login='test_login@foobar.ru',
                aliases={
                    'lite': 'test_login@foobar.ru',
                },
                display_login='foobar',  # Для лайтов неприменимо
            ),
        )
        _check_login_forms_in_userinfo_response(lite_response, login=u'test_login@foobar.ru')

    def test_blackbox_userinfo_login_forms_for_social_user(self):
        """Проверяем формы логина в ответе ЧЯ для соц. пользователя"""
        social_response = json.loads(
            blackbox_userinfo_response(
                uid=1,
                login='uid-blabla',
                aliases={
                    'social': 'uid-blabla',
                },
                display_login='foobar',  # Для социальных пользователей неприменимо
            ),
        )
        _check_login_forms_in_userinfo_response(social_response, login=u'uid-blabla', display_login=u'')

    def test_blackbox_userinfo_login_forms_for_phonish_user(self):
        """Проверяем формы логина в ответе ЧЯ для phonish-пользователя"""
        phonish_response = json.loads(
            blackbox_userinfo_response(
                uid=1,
                login='phne-blabla',
                aliases={
                    'phonish': 'phne-blabla',
                },
                display_login='foobar',  # Для phonish-пользователей неприменимо
            ),
        )
        _check_login_forms_in_userinfo_response(phonish_response, login=u'phne-blabla', display_login=u'')

    def test_blackbox_userinfo_login_forms_for_mailish_user(self):
        """Проверяем формы логина в ответе ЧЯ для лайт-пользователя"""
        lite_response = json.loads(
            blackbox_userinfo_response(
                uid=1,
                login='test_login@foobar.ru',
                aliases={
                    'mailish': 'test_login@foobar.ru',
                },
                display_login='foobar',  # Для мейлишей неприменимо
            ),
        )
        _check_login_forms_in_userinfo_response(lite_response, login=u'test_login@foobar.ru')

    def test_set_userinfo_response_value(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                login='login',
                emails=[{'address': 'test@yandex.ru'}],
                default_avatar_key='key',
                aliases={'yandexoid': 'yastaff_login'},
                subscribed_to=[2],
                unsubscribed_from=[16],
                crypt_password='1:$123',
                display_name={'social': {'provider': 'fb', 'profile_id': 1}},
                is_display_name_empty=False,
                pin_status=True,
                birthdate='2000-01-01',
                firstname='firstname',
                lastname='lastname',
                gender='0',
                language='en',
                timezone='Europe/Berlin',
                country='US',
                city='St.Petersburg',
            ),
        )
        expected = {
            'domain': None,
            'uid': 1,
            'id': '1',
            'is_disabled': 0,
            'subscriptions': {
                8: {'login': 'login', 'suid': 1, 'login_rule': 1, 'sid': 8},
                2: {'suid': 1, 'sid': 2},
            },
            'accounts.ena.uid': 1,
            'value': 1,
            'userinfo.sex.uid': 0,
            'karma': 0,
            'domid': None,
            'login': 'login',
            'display_login': 'login',
            'dbfields': {
                'accounts.ena.uid': 1,
                'userinfo.sex.uid': 0,
            },
            'attributes': {
                '3': '0',
                '19': '1:$123',
                '27': 'firstname',
                '28': 'lastname',
                '30': '2000-01-01',
                '31': 'US',
                '32': 'St.Petersburg',
                '33': 'Europe/Berlin',
                '34': 'en',
                '1008': 'login',
                '1009': '1',
            },
            'account.normalized_login': 'login',
            'account.is_available': '1',
            'person.firstname': 'firstname',
            'person.lastname': 'lastname',
            'person.birthday': '2000-01-01',
            'person.country': 'US',
            'person.city': 'St.Petersburg',
            'person.timezone': 'Europe/Berlin',
            'person.language': 'en',
            'password.encrypted': '1:$123',
            'address-list': [
                {
                    'default': False,
                    'prohibit-restore': False,
                    'validated': False,
                    'native': False,
                    'rpop': False,
                    'unsafe': False,
                    'silent': False,
                    'address': 'test@yandex.ru',
                    'born-date': '2013-09-12 16:33:59',
                },
            ],
            'display_name': {
                'name': '',
                'avatar': {
                    'default': 'key',
                    'empty': False,
                },
                'social': {
                    'profile_id': 1,
                    'provider': 'fb',
                },
                'display_name_empty': False,
            },
            'aliases': {
                '13': 'yastaff_login',
            },
            'pin_status': True,
        }
        eq_(Blackbox().userinfo(uid=1), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_userinfo_get_family_info(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=1,
                family_info=TEST_FAMILY_INFO,
            ),
        )

        eq_(
            Blackbox().userinfo(1, get_family_info=True)['family_info'],
            TEST_FAMILY_INFO,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_userinfo_get_public_id(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=1,
                public_id='TEST_PUBLIC_ID',
            ),
        )

        eq_(
            Blackbox().userinfo(1, get_public_id=True)['public_id'],
            'TEST_PUBLIC_ID',
        )
        ok_(self.fake_blackbox._mock.request.called)

    @raises(ValueError)
    def test_cannot_set_crypt_password_without_version(self):
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                crypt_password='blabla',
            ),
        )

    def test_set_userinfo_response_value_default(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(),
        )
        expected = {
            'domain': None,
            'uid': 1,
            'id': '1',
            'is_disabled': 0,
            'subscriptions': {
                8: {'login': 'test', 'suid': 1, 'login_rule': 1, 'sid': 8},
            },
            'accounts.ena.uid': 1,
            'value': 1,
            'userinfo.sex.uid': 1,
            'karma': 0,
            'domid': None,
            'login': 'test',
            'display_login': 'test',
            'dbfields': {
                'accounts.ena.uid': 1,
                'userinfo.sex.uid': 1,
            },
            'display_name': {
                'name': '',
                'display_name_empty': False,
            },
            'attributes': {
                '3': '0',
                '27': u'\\u0414',
                '28': u'\\u0424',
                '30': '1963-05-15',
                '31': 'ru',
                '32': u'\u041c\u043e\u0441\u043a\u0432\u0430',
                '33': 'Europe/Moscow',
                '34': 'ru',
                '1008': 'test',
                '1009': '1',
            },
            'account.normalized_login': 'test',
            'account.is_available': '1',
            'person.firstname': u'\\u0414',
            'person.lastname': u'\\u0424',
            'person.birthday': '1963-05-15',
            'person.country': 'ru',
            'person.city': u'\u041c\u043e\u0441\u043a\u0432\u0430',
            'person.timezone': 'Europe/Moscow',
            'person.language': 'ru',
            'aliases': {
                '1': 'test',
            },
        }

        eq_(Blackbox().userinfo(uid=1), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_userinfo_response_value_multiple(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uids=[1, 2, 3]),
        )
        uids = [x['uid'] for x in Blackbox().userinfo(uids=[1, 2, 3])]
        eq_(uids, [1, 2, 3])
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_userinfo_response_value_multiple_parameter_sets(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([{'uid': 1}, {'uid': 2}, {'uid': 3}]),
        )
        uids = [x['uid'] for x in Blackbox().userinfo(uids=[1, 2, 3])]
        eq_(uids, [1, 2, 3])
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_response_side_effect(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_side_effect('userinfo', TabError)
        with assert_raises(TabError):
            Blackbox().userinfo(123)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_userinfo_response_with_error(self):
        ok_(not self.fake_blackbox._mock.request.called)

        error_response = '''
        {
            "exception" : {
                "value" : "ACCESS_DENIED",
                "id" : 21
            },
            "error" : "BlackBox error: Unconfigured dbfield 'accounts.ena.uid'"
        }
        '''

        self.fake_blackbox.set_blackbox_response_value('userinfo', error_response)

        with assert_raises(AccessDenied):
            Blackbox().userinfo(123)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_find_pdd_accounts_response_value(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'find_pdd_accounts',
            blackbox_find_pdd_accounts_response(
                uids=[1, 2, 3],
                total_count=5,
                count=3,
            ),
        )
        expected = {
            'uids': [1, 2, 3],
            'total_count': 5,
            'count': 3,
        }
        eq_(
            Blackbox().find_pdd_accounts(domain='okna.ru', login='*'),
            expected,
        )

    def test_set_find_pdd_accounts_response_count_not_specified(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'find_pdd_accounts',
            blackbox_find_pdd_accounts_response(
                uids=[1, 2, 3],
            ),
        )
        expected = {
            'uids': [1, 2, 3],
            'total_count': 3,
            'count': 3,
        }
        eq_(
            Blackbox().find_pdd_accounts(domain='okna.ru', login='*'),
            expected,
        )

    def test_set_find_pdd_accounts_response_count_specified(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'find_pdd_accounts',
            blackbox_find_pdd_accounts_response(
                uids=[1, 2, 3],
                count=2,
            ),
        )
        expected = {
            'uids': [1, 2, 3],
            'total_count': 3,
            'count': 2,
        }
        eq_(
            Blackbox().find_pdd_accounts(domain='okna.ru', login='*'),
            expected,
        )

    def test_set_pwdhistory_response_value_found(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=True),
        )
        expected = {
            'found_in_history': True,
        }
        eq_(Blackbox().pwdhistory(uid=1, password='', depth=5), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_test_pwd_hashes_response_value_found(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(hashes={'hashA': True, 'hashB': False}),
        )
        eq_(
            Blackbox().test_pwd_hashes(password='pwd', hashes=['hashA', 'hashB']),
            {'hashA': True, 'hashB': False},
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_create_pwd_hash_response(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash='5:$1$3/TETQVg$v1e4l2vF.ygWiYoS0vXSG0'),
        )
        eq_(
            Blackbox().create_pwd_hash(password='pass', version='5', uid=123),
            '5:$1$3/TETQVg$v1e4l2vF.ygWiYoS0vXSG0',
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_hosted_domains_response_value(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(domain_admin='42'),
        )
        expected = {
            'hosted_domains': [
                {
                    u'admin': u'42',
                    u'born_date': u'2010-10-12 15:03:24',
                    u'default_uid': u'0',
                    u'domain': u'domain.ru',
                    u'domid': 1,
                    u'ena': u'0',
                    u'master_domain': u'',
                    u'mx': u'0',
                    u'options': u'',
                    u'slaves': u'',
                },
                {
                    u'admin': u'42',
                    u'born_date': u'2010-10-12 15:03:24',
                    u'default_uid': u'0',
                    u'domain': u'domain-1.ru',
                    u'domid': 2,
                    u'ena': u'0',
                    u'master_domain': u'',
                    u'mx': u'0',
                    u'options': u'',
                    u'slaves': u'',
                },
                {
                    u'admin': u'42',
                    u'born_date': u'2010-10-12 15:03:24',
                    u'default_uid': u'0',
                    u'domain': u'domain-2.ru',
                    u'domid': 3,
                    u'ena': u'0',
                    u'master_domain': u'',
                    u'mx': u'0',
                    u'options': u'',
                    u'slaves': u'',
                },
            ],
        }

        eq_(Blackbox().hosted_domains(domain_admin='42'), expected)
        ok_(self.fake_blackbox._mock.request.called)

        self.fake_blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(domain_admin='42', can_users_change_password='1',
                                             count=1, mx=1),
        )
        eq_(
            Blackbox().hosted_domains(domain_admin='42'),
            {
                'hosted_domains': [
                    {
                        'born_date': '2010-10-12 15:03:24',
                        'default_uid': '0',
                        'admin': '42',
                        'domid': 1,
                        'options': '{"can_users_change_password": "1"}',
                        'slaves': '',
                        'master_domain': '',
                        'mx': '1',
                        'domain': 'domain.ru',
                        'ena': '0',
                    },
                ],
            },
        )

    def test_set_pwdhistory_response_value_not_found(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )
        expected = {
            'found_in_history': False,
        }
        eq_(Blackbox().pwdhistory(uid=1, password='', depth=5), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def _get_sessionid_expected_response(self, user_status, uid_present=True, is_lite_session=False):
        expected = {
            'status': user_status,
            'id': '1',
            'cookie_status': user_status,
            'authid': {
                'id': 'authid_value',
                'ip': '8.8.8.8',
                'host': '8',
                'time': '123123',
            },
            'auth': {
                'password_verification_age': 0,
                'have_password': True,
                'allow_plain_text': True,
                'secure': True,
                'social': {'profile_id': 123},
            },
            'allow_more_users': True,
            'ttl': 0,
            'age': 0,
            'error': 'OK',
            'login': 'test',
            'address-list': [
                {
                    'default': False,
                    'prohibit-restore': False,
                    'validated': False,
                    'native': False,
                    'rpop': False,
                    'unsafe': False,
                    'silent': False,
                    'address': 'test@yandex.ru',
                    'born-date': '2013-09-12 16:33:59',
                },
            ],
            'attributes': {
                '3': '0',
                '27': u'\\u0414',
                '28': u'\\u0424',
                '30': '1963-05-15',
                '31': 'ru',
                '32': u'\u041c\u043e\u0441\u043a\u0432\u0430',
                '33': 'Europe/Moscow',
                '34': 'ru',
                '1008': 'test',
                '1009': '1',
            },
        }
        if uid_present:
            expected.update({
                'domain': None,
                'is_disabled': 0,
                'accounts.ena.uid': 1,
                'display_login': 'test',
                'uid': 1,
                'login': 'test',
                'subscriptions': {
                    8: {'login': 'test', 'suid': 1, 'login_rule': 1, 'sid': 8},
                },
                'display_name': {
                    'name': '',
                    'avatar': {
                        'default': 'key',
                        'empty': False,
                    },
                    'display_name_empty': False,
                },
                'aliases': {
                    '1': 'test',
                },
                'account.normalized_login': 'test',
                'account.is_available': '1',
                'person.firstname': u'\\u0414',
                'person.lastname': u'\\u0424',
                'person.birthday': '1963-05-15',
                'person.country': 'ru',
                'person.city': u'\u041c\u043e\u0441\u043a\u0432\u0430',
                'person.timezone': 'Europe/Moscow',
                'person.language': 'ru',
                'karma': 0,
                'domid': None,
                'dbfields': {
                    'accounts.ena.uid': 1,
                    'userinfo.sex.uid': 1,
                },
                'value': 1,
                'userinfo.sex.uid': 1,
                'is_lite_session': is_lite_session,
            })
        return expected

    def test_set_sessionid_response_value(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(
                social_profile_id=123,
                emails=[{'address': 'test@yandex.ru'}],
                authid='authid_value',
                ip='8.8.8.8',
                host='8',
                time='123123',
                default_avatar_key='key',
            ),
        )
        expected = self._get_sessionid_expected_response('VALID')
        eq_(Blackbox().sessionid('123', '127.0.0.1', 'yandex.ru'), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_sessionid_response_value_with_bad_statuses_and_full_info(self):
        ok_(not self.fake_blackbox._mock.request.called)
        for status in [
            BLACKBOX_SESSIONID_INVALID_STATUS,
            BLACKBOX_SESSIONID_EXPIRED_STATUS,
            BLACKBOX_SESSIONID_DISABLED_STATUS,
        ]:
            self.fake_blackbox.set_blackbox_response_value(
                'sessionid',
                blackbox_sessionid_response(
                    status=status,
                    social_profile_id=123,
                    emails=[{'address': 'test@yandex.ru'}],
                    authid='authid_value',
                    ip='8.8.8.8',
                    host='8',
                    time='123123',
                    default_avatar_key='key',
                    userinfo_for_invalid=True,
                ),
            )
            expected = self._get_sessionid_expected_response(status)
            eq_(Blackbox().sessionid('123', '127.0.0.1', 'yandex.ru'), expected)

    def test_set_sessionid_response_value_with_prolong_cookies_and_sessguard(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(
                prolong_cookies=True,
                sessguard_hosts=['passport.yandex.ru', 'mail.yandex.ru'],
            ),
        )
        response = Blackbox().sessionid('123', '127.0.0.1', 'yandex.ru')
        eq_(
            response['new-session'],
            {
                'domain': '.yandex.ru',
                'expires': 0,
                'secure': True,
                'value': '3:session',
            },
        )
        eq_(
            response['new-sslsession'],
            {
                'domain': '.yandex.ru',
                'expires': 0,
                'secure': True,
                'value': '3:sslsession',
            },
        )
        eq_(
            response['new-sessguards'],
            {
                'passport.yandex.ru': {
                    'sessguard': {
                        'domain': '.passport.yandex.ru',
                        'expires': 0,
                        'value': '1.sessguard',
                    },
                },
                'mail.yandex.ru': {
                    'sessguard': {
                        'domain': '.mail.yandex.ru',
                        'expires': 0,
                        'value': '1.sessguard',
                    },
                },
            },
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_sessionid_response_value_with_cookies_resigned_for_other_domains(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(resign_for_domains=['my.edadeal.ru', 'yandex.com']),
        )
        response = Blackbox().sessionid('123', '127.0.0.1', 'yandex.ru')
        eq_(
            response['resigned_cookies'],
            {
                'my.edadeal.ru': {
                    'new-session': {
                        'domain': '.edadeal.ru',
                        'expires': 0,
                        'secure': True,
                        'value': '3:session',
                    },
                    'new-sslsession': {
                        'domain': '.edadeal.ru',
                        'expires': 0,
                        'secure': True,
                        'value': '3:sslsession',
                    },
                },
                'yandex.com': {
                    'new-session': {
                        'domain': '.yandex.com',
                        'expires': 0,
                        'secure': True,
                        'value': '3:session',
                    },
                    'new-sslsession': {
                        'domain': '.yandex.com',
                        'expires': 0,
                        'secure': True,
                        'value': '3:sslsession',
                    },
                },
            },
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_sessionid_response_value_for_disabled(self):
        self.fake_blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(
                status=BLACKBOX_SESSIONID_DISABLED_STATUS,
                social_profile_id=123,
                emails=[{'address': 'test@yandex.ru'}],
                authid='authid_value',
                ip='8.8.8.8',
                host='8',
                time='123123',
                default_avatar_key='key',
                ttl=1,
                age=2,
            ),
        )
        response = Blackbox().sessionid('123', '127.0.0.1', 'yandex.ru')
        eq_(response['ttl'], 1)
        eq_(response['age'], 2)

    def test_set_sessionid_response_value_with_no_uid(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(
                uid=None,
                social_profile_id=123,
                emails=[{'address': 'test@yandex.ru'}],
                authid='authid_value',
                ip='8.8.8.8',
                host='8',
                time='123123',
                default_avatar_key='key',
            ),
        )

        expected = self._get_sessionid_expected_response('VALID', uid_present=False)
        eq_(Blackbox().sessionid('123', '127.0.0.1', 'yandex.ru'), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_sessionid_response_value_with_family_info(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(
                uid=1,
                social_profile_id=123,
                emails=[{'address': 'test@yandex.ru'}],
                authid='authid_value',
                ip='8.8.8.8',
                host='8',
                time='123123',
                default_avatar_key='key',
                family_info=TEST_FAMILY_INFO,
            ),
        )

        eq_(
            Blackbox().sessionid('123', '127.0.0.1', 'yandex.ru')['family_info'],
            TEST_FAMILY_INFO,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_sessionid_multi_response_value(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    social_profile_id=123,
                    authid='authid_value',
                    ip='8.8.8.8',
                    host='8',
                    time='123123',
                    default_avatar_key='key',
                    allow_more_users=False,
                    is_lite_session=True,
                    user_ticket='ticket',
                    family_info=TEST_FAMILY_INFO,
                ),
                uid=2,
                login='user2',
                social_profile_id=123,
                default_avatar_key='key',
            ),
        )

        expected = {
            'status': 'VALID',
            'cookie_status': 'VALID',
            'id': 1,
            'default_uid': 1,
            'value': 1,
            'ttl': 0,
            'age': 0,
            'error': 'OK',

            # Дефолтный пользователь
            'domain': None,
            'uid': 1,
            'is_lite_session': True,
            'subscriptions': {
                8: {'login': 'test', 'suid': 1, 'login_rule': 1, 'sid': 8},
            },
            'family_info': TEST_FAMILY_INFO,
            'accounts.ena.uid': 1,
            'authid': {
                'id': 'authid_value',
                'ip': '8.8.8.8',
                'host': '8',
                'time': '123123',
            },
            'auth': {
                'password_verification_age': 0,
                'have_password': True,
                'allow_plain_text': True,
                'secure': True,
                'social': {'profile_id': 123},
            },
            'allow_more_users': False,
            'domid': None,
            'userinfo.sex.uid': 1,
            'dbfields': {
                'accounts.ena.uid': 1,
                'userinfo.sex.uid': 1,
            },
            'is_disabled': 0,
            'attributes': {
                '3': '0',
                '27': u'\\u0414',
                '28': u'\\u0424',
                '30': '1963-05-15',
                '31': 'ru',
                '32': u'\u041c\u043e\u0441\u043a\u0432\u0430',
                '33': 'Europe/Moscow',
                '34': 'ru',
                '1008': 'test',
                '1009': '1',
            },
            'account.normalized_login': 'test',
            'account.is_available': '1',
            'person.firstname': u'\\u0414',
            'person.lastname': u'\\u0424',
            'person.birthday': '1963-05-15',
            'person.country': 'ru',
            'person.city': u'\u041c\u043e\u0441\u043a\u0432\u0430',
            'person.timezone': 'Europe/Moscow',
            'person.language': 'ru',
            'aliases': {
                '1': 'test',
            },
            'login': 'test',
            'display_login': 'test',
            'karma': 0,
            'display_name': {
                'name': '',
                'avatar': {
                    'default': 'key',
                    'empty': False,
                },
                'display_name_empty': False,
            },
            'user_ticket': 'ticket',
            'users': {
                1: {
                    'status': 'VALID',
                    'value': 1,
                    'domain': None,
                    'id': 1,
                    'uid': 1,
                    'is_lite_session': True,
                    'subscriptions': {
                        8: {'login': 'test', 'suid': 1, 'login_rule': 1, 'sid': 8},
                    },
                    'family_info': TEST_FAMILY_INFO,
                    'accounts.ena.uid': 1,
                    'auth': {
                        'password_verification_age': 0,
                        'have_password': True,
                        'allow_plain_text': True,
                        'secure': True,
                        'social': {'profile_id': 123},
                    },
                    'domid': None,
                    'userinfo.sex.uid': 1,
                    'dbfields': {
                        'accounts.ena.uid': 1,
                        'userinfo.sex.uid': 1,
                    },
                    'is_disabled': 0,
                    'attributes': {
                        '3': '0',
                        '27': u'\\u0414',
                        '28': u'\\u0424',
                        '30': '1963-05-15',
                        '31': 'ru',
                        '32': u'\u041c\u043e\u0441\u043a\u0432\u0430',
                        '33': 'Europe/Moscow',
                        '34': 'ru',
                        '1008': 'test',
                        '1009': '1',
                    },
                    'account.normalized_login': 'test',
                    'account.is_available': '1',
                    'person.firstname': u'\\u0414',
                    'person.lastname': u'\\u0424',
                    'person.birthday': '1963-05-15',
                    'person.country': 'ru',
                    'person.city': u'\u041c\u043e\u0441\u043a\u0432\u0430',
                    'person.timezone': 'Europe/Moscow',
                    'person.language': 'ru',
                    'aliases': {
                        '1': 'test',
                    },
                    'login': 'test',
                    'display_login': 'test',
                    'karma': 0,
                    'display_name': {
                        'name': '',
                        'avatar': {
                            'default': 'key',
                            'empty': False,
                        },
                        'display_name_empty': False,
                    },
                },
                2: {
                    'status': 'VALID',
                    'value': 2,
                    'domain': None,
                    'uid': 2,
                    'id': 2,
                    'is_lite_session': False,
                    'subscriptions': {
                        8: {'login': 'user2', 'suid': 1, 'login_rule': 1, 'sid': 8},
                    },
                    'accounts.ena.uid': 1,
                    'auth': {
                        'password_verification_age': 0,
                        'have_password': True,
                        'allow_plain_text': True,
                        'secure': True,
                        'social': {'profile_id': 123},
                    },
                    'domid': None,
                    'userinfo.sex.uid': 1,
                    'dbfields': {
                        'accounts.ena.uid': 1,
                        'userinfo.sex.uid': 1,
                    },
                    'is_disabled': 0,
                    'attributes': {
                        '3': '0',
                        '27': u'\\u0414',
                        '28': u'\\u0424',
                        '30': '1963-05-15',
                        '31': 'ru',
                        '32': u'\u041c\u043e\u0441\u043a\u0432\u0430',
                        '33': 'Europe/Moscow',
                        '34': 'ru',
                        '1008': 'user2',
                        '1009': '1',
                    },
                    'account.normalized_login': 'user2',
                    'account.is_available': '1',
                    'person.firstname': u'\\u0414',
                    'person.lastname': u'\\u0424',
                    'person.birthday': '1963-05-15',
                    'person.country': 'ru',
                    'person.city': u'\u041c\u043e\u0441\u043a\u0432\u0430',
                    'person.timezone': 'Europe/Moscow',
                    'person.language': 'ru',
                    'aliases': {
                        '1': 'user2',
                    },
                    'login': 'user2',
                    'display_login': 'user2',
                    'karma': 0,
                    'display_name': {
                        'name': '',
                        'avatar': {
                            'default': 'key',
                            'empty': False,
                        },
                        'display_name_empty': False,
                    },
                },
            },
        }

        eq_(Blackbox().sessionid('123', '127.0.0.1', 'yandex.ru'), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_sessionid_multi_response_value_invalid_session(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_invalid_session(
                blackbox_sessionid_multi_response(
                    social_profile_id=123,
                    authid='authid_value',
                    ip='8.8.8.8',
                    host='8',
                    time='123123',
                    default_avatar_key='key',
                    allow_more_users=False,
                ),
            ),
        )
        expected = {
            u'age': 0,
            u'allow_more_users': False,
            u'authid': {
                u'host': u'8',
                u'id': u'authid_value',
                u'ip': u'8.8.8.8',
                u'time': u'123123',
            },
            'cookie_status': u'VALID',
            u'default_uid': 1,
            u'error': u'OK',
            u'id': 1,
            u'status': u'INVALID',
            u'ttl': 0,
            u'users': {
                1: {
                    u'id': 1,
                    u'status': u'INVALID',
                },
            },
        }
        eq_(Blackbox().sessionid('123', '127.0.0.1', 'yandex.ru'), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_login_v2_response_value(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                bruteforce_policy=BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS,
                login='test',
                emails=[{'address': 'test@yandex.ru'}],
                restricted_session=True,
                totp_check_time=123,
                user_ticket='ticket',
            ),
        )
        expected = {
            'accounts.ena.uid': 1,
            'display_login': 'test',
            'dbfields': {
                'accounts.ena.uid': 1,
                'userinfo.sex.uid': 1,
            },
            'attributes': {
                '3': '0',
                '27': u'\\u0414',
                '28': u'\\u0424',
                '30': '1963-05-15',
                '31': 'ru',
                '32': u'\u041c\u043e\u0441\u043a\u0432\u0430',
                '33': 'Europe/Moscow',
                '34': 'ru',
                '1008': 'test',
                '1009': '1',
            },
            'account.normalized_login': 'test',
            'account.is_available': '1',
            'person.firstname': u'\\u0414',
            'person.lastname': u'\\u0424',
            'person.birthday': '1963-05-15',
            'person.country': 'ru',
            'person.city': u'\u041c\u043e\u0441\u043a\u0432\u0430',
            'person.timezone': 'Europe/Moscow',
            'person.language': 'ru',
            'aliases': {
                '1': 'test',
            },
            'domain': None,
            'domid': None,
            'error': 'OK',
            'is_disabled': 0,
            'karma': 0,
            'login': 'test',
            'login_status': 'VALID',
            'password_status': 'VALID',
            'subscriptions': {
                8: {u'login': 'test', 'login_rule': 1, 'sid': 8, 'suid': 1},
            },
            'uid': 1,
            'id': '1',
            'userinfo.sex.uid': 1,
            'value': 1,
            'bruteforce_policy': {
                'value': 'password_expired',
                'level': 0,
            },
            'bruteforce_status': 'password_expired',
            'address-list': [
                {
                    'default': False,
                    'prohibit-restore': False,
                    'validated': False,
                    'native': False,
                    'rpop': False,
                    'unsafe': False,
                    'silent': False,
                    'address': 'test@yandex.ru',
                    'born-date': '2013-09-12 16:33:59',
                },
            ],
            'restricted_session': True,
            'display_name': {
                'name': '',
                'display_name_empty': False,
            },
            'totp_check_time': 123,
            'user_ticket': 'ticket',
            'badauth_counts': {
                'login': {'value': 2, 'limit': 10},
                'login,ip': {'value': 1, 'limit': 5},
            },
        }
        eq_(Blackbox().login('test', 'testpassword', '127.0.0.1'), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_login_v1_response_value(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                version=1,
                login='test',
                emails=[{'address': 'test@yandex.ru'}],
                restricted_session=True,
                totp_check_time=123,
                allowed_second_steps=['rfc_totp', 'email_code'],
            ),
        )
        expected = {
            'accounts.ena.uid': 1,
            'display_login': 'test',
            'dbfields': {
                'accounts.ena.uid': 1,
                'userinfo.sex.uid': 1,
            },
            'attributes': {
                '3': '0',
                '27': u'\\u0414',
                '28': u'\\u0424',
                '30': '1963-05-15',
                '31': 'ru',
                '32': u'\u041c\u043e\u0441\u043a\u0432\u0430',
                '33': 'Europe/Moscow',
                '34': 'ru',
                '1008': 'test',
                '1009': '1',
            },
            'account.normalized_login': 'test',
            'account.is_available': '1',
            'person.firstname': u'\\u0414',
            'person.lastname': u'\\u0424',
            'person.birthday': '1963-05-15',
            'person.country': 'ru',
            'person.city': u'\u041c\u043e\u0441\u043a\u0432\u0430',
            'person.timezone': 'Europe/Moscow',
            'person.language': 'ru',
            'aliases': {
                '1': 'test',
            },
            'domain': None,
            'domid': None,
            'error': 'OK',
            'is_disabled': 0,
            'karma': 0,
            'login': 'test',
            'status': 'VALID',
            'subscriptions': {
                8: {u'login': 'test', 'login_rule': 1, 'sid': 8, 'suid': 1},
            },
            'uid': 1,
            'id': '1',
            'userinfo.sex.uid': 1,
            'value': 1,
            'address-list': [
                {
                    'default': False,
                    'prohibit-restore': False,
                    'validated': False,
                    'native': False,
                    'rpop': False,
                    'unsafe': False,
                    'silent': False,
                    'address': 'test@yandex.ru',
                    'born-date': '2013-09-12 16:33:59',
                },
            ],
            'restricted_session': True,
            'display_name': {
                'name': '',
                'display_name_empty': False,
            },
            'totp_check_time': 123,
            'allowed_second_steps': 'rfc_totp,email_code',
            'badauth_counts': {
                'login': {'value': 2, 'limit': 10},
                'login,ip': {'value': 1, 'limit': 5},
            },
        }
        eq_(Blackbox().login('test', 'testpassword', '127.0.0.1', version=1), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_login_v1_response_value_with_captcha(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                version=1,
                login='test',
                emails=[{'address': 'test@yandex.ru'}],
                restricted_session=True,
                totp_check_time=123,
                status=BLACKBOX_LOGIN_V1_SHOW_CAPTCHA_STATUS,
            ),
        )
        expected = {
            'error': 'OK',
            'status': 'SHOW_CAPTCHA',
            'badauth_counts': {
                'login': {'value': 2, 'limit': 10},
                'login,ip': {'value': 1, 'limit': 5},
            },
        }
        eq_(Blackbox().login('test', 'testpassword', '127.0.0.1', version=1), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_login_v1_response_value_with_family_info(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                version=1,
                login='test',
                emails=[{'address': 'test@yandex.ru'}],
                restricted_session=True,
                totp_check_time=123,
                allowed_second_steps=['rfc_totp', 'email_code'],
                family_info=TEST_FAMILY_INFO,
            ),
        )
        eq_(
            Blackbox().login('test', 'testpassword', '127.0.0.1', version=1)['family_info'],
            TEST_FAMILY_INFO,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_login_v2_response_value_with_family_info(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                bruteforce_policy=BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS,
                login='test',
                emails=[{'address': 'test@yandex.ru'}],
                restricted_session=True,
                totp_check_time=123,
                user_ticket='ticket',
                family_info=TEST_FAMILY_INFO,
            ),
        )
        eq_(
            Blackbox().login('test', 'testpassword', '127.0.0.1')['family_info'],
            TEST_FAMILY_INFO,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_createsession_response(self):
        self.fake_blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(
                default_uid=1,
                sessguard_hosts=['passport.yandex.ru', 'mail.yandex.ru'],
            ),
        )
        expected = {
            'login_id': '123:1422501443:126',
            u'authid': {
                u'host': u'126',
                u'id': u'123:1422501443:126',
                u'ip': u'84.201.166.67',
                u'time': u'123',
            },
            u'default_uid': 1,
            u'new-session': {
                u'domain': u'.yandex.ru',
                u'expires': 0,
                u'value': u'2:session',
            },
            u'new-sslsession': {
                u'domain': u'.yandex.ru',
                u'expires': 1370874827,
                u'secure': True,
                u'value': u'2:sslsession',
            },
            u'new-sessguards': {
                u'passport.yandex.ru': {
                    u'sessguard': {
                        u'domain': u'.passport.yandex.ru',
                        u'expires': 0,
                        u'value': u'1.sessguard',
                    },
                },
                u'mail.yandex.ru': {
                    u'sessguard': {
                        u'domain': u'.mail.yandex.ru',
                        u'expires': 0,
                        u'value': u'1.sessguard',
                    },
                },
            },
        }
        eq_(Blackbox().createsession(uid=1, ip='127.0.0.1', keyspace='space', ttl=5), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_editsession_response(self):
        self.fake_blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                session_value='session',
                ssl_session_value='sslsession',
                default_uid=1,
                sessguard_hosts=['passport.yandex.ru', 'mail.yandex.ru'],
            ),
        )
        expected = {
            'login_id': '123:1422501443:126',
            u'authid': {
                u'ip': u'84.201.166.67',
                u'host': u'126',
                u'id': u'123:1422501443:126',
                u'time': u'123',
            },
            u'new-session': {
                u'domain': u'.yandex.ru',
                u'expires': 0,
                u'value': u'session',
            },
            u'default_uid': 1,
            u'new-sslsession': {
                u'domain': u'.yandex.ru',
                u'expires': 1370874827,
                u'value': u'sslsession',
                u'secure': True,
            },
            u'new-sessguards': {
                u'passport.yandex.ru': {
                    u'sessguard': {
                        u'domain': u'.passport.yandex.ru',
                        u'expires': 0,
                        u'value': u'1.sessguard',
                    },
                },
                u'mail.yandex.ru': {
                    u'sessguard': {
                        u'domain': u'.mail.yandex.ru',
                        u'expires': 0,
                        u'value': u'1.sessguard',
                    },
                },
            },
        }
        eq_(
            Blackbox().editsession(op='add', sessionid='sessionid', uid=1, ip='127.0.0.1', host='yandex.ru'),
            expected,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_editsession_delete_empty_response(self):
        self.fake_blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_delete_empty_response(),
        )
        expected = {
            u'authid': {
                u'ip': u'84.201.166.67',
                u'host': u'126',
                u'id': u'123:1422501443:126',
                u'time': u'123',
            },
            u'default_uid': u'',
        }
        eq_(
            Blackbox().editsession(op='delete', sessionid='sessionid', uid=1, ip='127.0.0.1', host='yandex.ru'),
            expected,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_create_oauth_token_response(self):
        self.fake_blackbox.set_blackbox_response_value(
            'create_oauth_token',
            blackbox_create_oauth_token_response('test_token', 123),
        )
        expected = {
            'access_token': 'test_token',
            'token_id': 123,
        }
        eq_(
            Blackbox().create_oauth_token(uid=1, ip='127.0.0.1', client_id=2, scope_ids=[3, 4], expire_time=100500),
            expected,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_oauth_response(self):
        self.fake_blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                oauth_token_info={'token_id': '1', 'device_id': 'foo'},
                default_avatar_key='0/0-0',
                is_avatar_empty=True,
                is_display_name_empty=True,
                user_ticket='ticket',
            ),
        )
        expected = {
            u'accounts.ena.uid': 1,
            u'attributes': {
                u'3': u'0',
                u'27': u'\\u0414',
                u'28': u'\\u0424',
                u'30': u'1963-05-15',
                '31': 'ru',
                u'32': u'Москва',
                u'33': u'Europe/Moscow',
                u'34': u'ru',
                u'1008': u'test',
                u'1009': u'1',
            },
            u'account.normalized_login': u'test',
            u'account.is_available': u'1',
            u'person.firstname': u'\\u0414',
            u'person.lastname': u'\\u0424',
            u'person.birthday': u'1963-05-15',
            u'person.country': u'ru',
            u'person.city': u'Москва',
            u'person.timezone': u'Europe/Moscow',
            u'person.language': u'ru',
            u'aliases': {
                u'1': u'test',
            },
            u'is_disabled': 0,
            u'dbfields': {
                u'accounts.ena.uid': 1,
                u'userinfo.sex.uid': 1,
            },
            u'display_login': u'test',
            u'display_name': {
                u'name': u'',
                u'avatar': {
                    u'default': u'0/0-0',
                    u'empty': True,
                },
                u'display_name_empty': True,
            },
            u'domain': None,
            u'domid': None,
            u'error': u'OK',
            u'karma': 0,
            u'login': u'test',
            u'oauth': {
                u'scope': [u''],
                u'uid': 1,
                u'token_id': u'1',
                u'device_id': u'foo',
                u'client_id': u'fake_clid',
            },
            u'status': u'VALID',
            u'subscriptions': {
                8: {u'login': u'test', u'login_rule': 1, u'sid': 8, u'suid': 1},
            },
            u'uid': 1,
            u'id': u'1',
            u'userinfo.sex.uid': 1,
            u'value': 1,
            u'user_ticket': u'ticket',
        }
        eq_(
            Blackbox().oauth(),
            expected,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_oauth_response_without_user(self):
        self.fake_blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                oauth_token_info={'token_id': '1', 'device_id': 'foo'},
                has_user_in_token=False,
            ),
        )
        expected = {
            u'error': u'OK',
            u'oauth': {
                u'scope': [u''],
                u'uid': None,
                u'token_id': u'1',
                u'device_id': u'foo',
                u'client_id': u'fake_clid',
            },
            u'status': u'VALID',
            u'uid': None,
        }
        eq_(
            Blackbox().oauth(),
            expected,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_oauth_response_with_family_info(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                oauth_token_info={'token_id': '1', 'device_id': 'foo'},
                family_info=TEST_FAMILY_INFO,
            ),
        )
        eq_(
            Blackbox().oauth(get_family_info=True)['family_info'],
            TEST_FAMILY_INFO,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_lrandoms_response(self):
        self.fake_blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )
        expected = [
            {
                'body': '2dL9OKKqcKHbljKQI70PMaaB7R08VnEn3jo5iAI62gPeCQ5zgI5fjjczFOMRvvaQ',
                'created_timestamp': 1376769601,
                'id': '1002322',
            },
            {
                'body': '2dL9OKKqcKHbljKQI70PMaaB7R08VnEn3jo5iAI62gPeCQ5zgI5fjjczFOMRvvaQ',
                'created_timestamp': 1376769602,
                'id': '1002323',
            },
            {
                'body': '2dL9OKKqcKHbljKQI70PMaaB7R08VnEn3jo5iAI62gPeCQ5zgI5fjjczFOMRvvaQ',
                'created_timestamp': 1376769603,
                'id': '1002324',
            },
            {
                'body': '2dL9OKKqcKHbljKQI70PMaaB7R08VnEn3jo5iAI62gPeCQ5zgI5fjjczFOMRvvaQ',
                'created_timestamp': 1376769604,
                'id': '1002325',
            },
            {
                'body': '2dL9OKKqcKHbljKQI70PMaaB7R08VnEn3jo5iAI62gPeCQ5zgI5fjjczFOMRvvaQ',
                'created_timestamp': 1376769605,
                'id': '1002326',
            },
            {
                'body': '2dL9OKKqcKHbljKQI70PMaaB7R08VnEn3jo5iAI62gPeCQ5zgI5fjjczFOMRvvaQ',
                'created_timestamp': 1376769606,
                'id': '1002327',
            },
        ]
        eq_(
            Blackbox().lrandoms(),
            expected,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_getattr(self):
        eq_(self.fake_blackbox._mock.foo, self.fake_blackbox.foo)

    def test_set_edit_totp_response(self):
        self.fake_blackbox.set_blackbox_response_value(
            'edit_totp',
            blackbox_edit_totp_response(
                status=True,
                totp_check_time=125,
            ),
        )
        eq_(
            Blackbox().edit_totp(operation='create', uid=123, pin=4567, secret_id=1, secret='SECRET', otp='otp123'),
            {
                'error': 'OK',
                'totp_check_time': 125,
                'secret_value': 'encrypted_secret',
            },
        )

    def test_set_edit_totp_unsuccessful_response(self):
        self.fake_blackbox.set_blackbox_response_value(
            'edit_totp',
            blackbox_edit_totp_response(
                status=False,
                encrypted_secret='junk',
            ),
        )
        eq_(
            Blackbox().edit_totp(operation='create', uid=123, pin=4567, secret_id=1, secret='SECRET', otp='otp123'),
            {
                'error': 'ERROR',
                'junk_secret_value': 'junk',
            },
        )

    def test_set_check_rfc_totp_response(self):
        self.fake_blackbox.set_blackbox_response_value(
            'check_rfc_totp',
            blackbox_check_rfc_totp_response(
                status=BLACKBOX_CHECK_RFC_TOTP_VALID_STATUS,
                time=125,
            ),
        )
        eq_(
            Blackbox().check_rfc_totp(uid=1, totp='totp123'),
            {
                'status': BLACKBOX_CHECK_RFC_TOTP_VALID_STATUS,
                'time': 125,
            },
        )

    def test_get_hosts_default_response(self):
        self.fake_blackbox.set_blackbox_response_value(
            'get_hosts',
            blackbox_get_hosts_response(),
        )
        eq_(
            Blackbox().get_hosts(),
            [
                dict(
                    host_id='1', db_id='333', sid='2', host_number='0',
                    mx='mxc22.yandex.ru', host_name='', host_ip='', prio='-100',
                ),
                dict(
                    host_id='17', db_id='mxt', sid='99', host_number='777',
                    mx='mx10.yandex.test', host_name='mxt', host_ip='192.168.0.1', prio='99',
                ),
                dict(
                    host_id='19', db_id='lol', sid='-10', host_number='0',
                    mx='', host_name='teux-test', host_ip='', prio='0',
                ),
            ],
        )

    def test_get_hosts_response(self):
        params = dict(db_id='wonk', foo='bar', host_id='123')
        self.fake_blackbox.set_blackbox_response_value(
            'get_hosts',
            blackbox_get_hosts_response(**params),
        )
        eq_(
            Blackbox().get_hosts(),
            [{
                'db_id': 'wonk', 'prio': '-10', 'sid': '2',
                'host_id': '123', 'foo': 'bar', 'mx': 'mx',
            }],
        )

    def test_set_get_track_response(self):
        self.fake_blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(1, 'track_id'),
        )
        expected = {
            'uid': 1,
            'track_id': 'track_id',
            'created': '1123213213',
            'expired': '1123513213',
            'content': {'type': 1},
        }
        eq_(
            Blackbox().get_track(1, 'track_id'),
            expected,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_get_all_tracks_response(self):
        self.fake_blackbox.set_blackbox_response_value(
            'get_all_tracks',
            blackbox_get_all_tracks_response(),
        )
        expected = [
            {
                'uid': 1,
                'track_id': 'bc968a106e53c3a22ea1ceef3aa5ab12',
                'created': '1123213213',
                'expired': '1123513213',
                'content': {'type': 1},
            },
        ]
        eq_(
            Blackbox().get_all_tracks(1),
            expected,
        )
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_family_info_response(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'family_info',
            blackbox_family_info_response(
                family_id='f2',
                admin_uid='100',
                uids=[1, 2, 3],
            ),
        )
        expected = {
            'admin_uid': '100',
            'family_id': 'f2',
            'users': {
                1: {'uid': 1, 'place': 0},
                2: {'uid': 2, 'place': 1},
                3: {'uid': 3, 'place': 2},
            },
        }
        eq_(Blackbox().family_info('f2'), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_family_info_response_specific_places(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'family_info',
            blackbox_family_info_response(
                family_id='f2',
                admin_uid='100',
                uids=[1, 2, 3],
                places=[3, 4, 5],
            ),
        )
        expected = {
            'admin_uid': '100',
            'family_id': 'f2',
            'users': {
                1: {'uid': 1, 'place': 3},
                2: {'uid': 2, 'place': 4},
                3: {'uid': 3, 'place': 5},
            },
        }
        eq_(Blackbox().family_info('f2'), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_family_info_response_without_places(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'family_info',
            blackbox_family_info_response(
                family_id='f2',
                admin_uid='100',
                uids=[1, 2, 3],
                with_places=False,
            ),
        )
        expected = {
            'admin_uid': '100',
            'family_id': 'f2',
            'users': {
                1: {'uid': 1},
                2: {'uid': 2},
                3: {'uid': 3},
            },
        }
        eq_(Blackbox().family_info('f2'), expected)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_family_info_response_non_existent(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'family_info',
            blackbox_family_info_response(
                family_id='f2',
                exists=False,
            ),
        )
        eq_(Blackbox().family_info('f2'), None)
        ok_(self.fake_blackbox._mock.request.called)

    def test_set_generate_public_id_response_value(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'generate_public_id',
            blackbox_generate_public_id_response(
                public_id='test-public-id',
            ),
        )
        eq_(
            Blackbox().generate_public_id(uid='1234'),
            'test-public-id',
        )

    def test_set_webauthn_credentials_response_value(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'webauthn_credentials',
            blackbox_webauthn_credentials_response(
                credential_external_id='cred-id',
                uid=1,
            ),
        )
        eq_(
            Blackbox().webauthn_credentials(credential_external_id='cred-id'),
            {'cred-id': {'uid': 1}},
        )

    def test_set_get_oauth_tokens_response(self):
        ok_(not self.fake_blackbox._mock.request.called)
        self.fake_blackbox.set_blackbox_response_value(
            'get_oauth_tokens',
            blackbox_get_oauth_tokens_response([
                dict(),
                dict(
                    status_value='INVALID',
                    status_id=4,
                    error='some_error',
                    login_id='login-id1',
                    ctime=datetime(2021, 6, 30, 19, 24, 1),
                    issue_time=datetime(2021, 6, 30, 19, 25, 1),
                    expire_time=datetime(2021, 6, 30, 20, 25, 1),
                    some_oauth_field='abcdef',
                ),
                dict(
                    issue_time='2021-06-30 19:14:01',
                    ctime='2021-07-01 19:14:01',
                    expire_time='2021-07-01 19:15:01',
                ),
            ]),
        )
        eq_(
            Blackbox().get_oauth_tokens(uid='12345'),
            [
                {
                    'status': {
                        'value': 'VALID',
                        'id': 0,
                    },
                    'error': 'OK',
                    'oauth': {},
                },
                {
                    'status': {
                        'value': 'INVALID',
                        'id': 4,
                    },
                    'error': 'some_error',
                    'login_id': 'login-id1',
                    'oauth': {
                        'ctime': datetime(2021, 6, 30, 19, 24, 1),
                        'issue_time': datetime(2021, 6, 30, 19, 25, 1),
                        'expire_time': datetime(2021, 6, 30, 20, 25, 1),
                        'some_oauth_field': 'abcdef',
                    },
                },
                {
                    'status': {
                        'value': 'VALID',
                        'id': 0,
                    },
                    'error': 'OK',
                    'oauth': {
                        'issue_time': datetime(2021, 6, 30, 19, 14, 1),
                        'ctime': datetime(2021, 7, 1, 19, 14, 1),
                        'expire_time': datetime(2021, 7, 1, 19, 15, 1),
                    },
                },
            ],
        )


class TestPhoneBindingsResponse(TestCase):
    def test_defaults(self):
        eq_(
            json.loads(blackbox_phone_bindings_response([{}])),
            {
                u'phone_bindings': [{
                    u'type': u'history',
                    u'number': u'79011111111',
                    u'phone_id': u'1',
                    u'uid': u'1',
                    u'bound': u'12345',
                    u'flags': u'0',
                }],
            },
        )

    def test_overrides(self):
        eq_(
            json.loads(blackbox_phone_bindings_response([{
                u'type': u'current',
                u'number': u'+79023332233',
                u'phone_id': 2,
                u'uid': 3,
                u'bound': datetime(2015, 5, 3, 15, 20, 10),
                u'flags': 2,
            }])),
            {
                u'phone_bindings': [{
                    u'type': u'current',
                    u'number': u'79023332233',
                    u'phone_id': u'2',
                    u'uid': u'3',
                    u'bound': str(unixtime(2015, 5, 3, 15, 20, 10)),
                    u'flags': u'2',
                }],
            },
        )

    def test_no_phone_id(self):
        response = json.loads(blackbox_phone_bindings_response([{u'phone_id': None}]))
        eq_(response[u'phone_bindings'][0][u'phone_id'], u'')


class PhonesTestMixin(object):
    """Тесты для генераторов ответов с телефонами."""
    def test_phones__no_phones_when_phones_arg_is_not_specified(self):
        response = self._build_response()

        user_info = self._get_user(response)
        ok_(u'phones' not in user_info)

    def test_phones__empty_phones_when_phones_arg_is_empty_list(self):
        response = self._build_response(phones=[])

        user_info = self._get_user(response)
        eq_(user_info[u'phones'], [])

    @raises(KeyError)
    def test_phones__key_error_when_phone_without_id(self):
        self._build_response(phones=[{}])

    def test_phones__phone_id(self):
        response = self._build_response(phones=[{u'id': 44}])

        user_info = self._get_user(response)
        eq_(user_info[u'phones'][0][u'id'], u'44')

    def test_phones__single_phone(self):
        response = self._build_response(phones=[{u'id': 44}])

        user_info = self._get_user(response)
        eq_(len(user_info[u'phones']), 1)

    def test_phones__many_phones(self):
        response = self._build_response(phones=[{u'id': 44}, {u'id': 41}])

        user_info = self._get_user(response)
        eq_(len(user_info[u'phones']), 2)

    def test_phones__no_attrs(self):
        response = self._build_response(phones=[{u'id': 44}])

        user_info = self._get_user(response)
        eq_(user_info[u'phones'][0][u'attributes'], {})

    def test_phones__omit_none_attr(self):
        response = self._build_response(phones=[{
            u'id': 44,
            u'number': None,
        }])

        user_info = self._get_user(response)
        eq_(user_info[u'phones'][0][u'attributes'], {})

    def test_phones__phone_number(self):
        response = self._build_response(phones=[{
            u'id': 44,
            u'number': u'+79019988777',
        }])

        user_info = self._get_user(response)
        eq_(
            user_info[u'phones'][0][u'attributes'],
            {u'1': u'79019988777'},
        )

    @raises(ValueError)
    def test_phones__value_error_when_phone_number_of_phone_not_starts_with_plus_sign(self):
        self._build_response(phones=[{
            u'id': 44,
            u'number': u'89019988777',
        }])

    def test_phones__created_time(self):
        response = self._build_response(phones=[{
            u'id': 44,
            u'created': datetime(2001, 1, 20, 0, 1, 1),
        }])

        user_info = self._get_user(response)
        eq_(
            user_info[u'phones'][0][u'attributes'],
            {u'2': str(unixtime(2001, 1, 20, 0, 1, 1))},
        )

    def test_phones__bound_time(self):
        response = self._build_response(phones=[{
            u'id': 44,
            u'bound': datetime(2001, 1, 20, 0, 1, 1),
        }])

        user_info = self._get_user(response)
        eq_(
            user_info[u'phones'][0][u'attributes'],
            {u'3': str(unixtime(2001, 1, 20, 0, 1, 1))},
        )

    def test_phones__confirmed_time(self):
        response = self._build_response(phones=[{
            u'id': 44,
            u'confirmed': datetime(2001, 1, 20, 0, 1, 1),
        }])

        user_info = self._get_user(response)
        eq_(
            user_info[u'phones'][0][u'attributes'],
            {u'4': str(unixtime(2001, 1, 20, 0, 1, 1))},
        )

    def test_phones__admitted_time(self):
        response = self._build_response(phones=[{
            u'id': 44,
            u'admitted': datetime(2001, 1, 20, 0, 1, 1),
        }])

        user_info = self._get_user(response)
        eq_(
            user_info[u'phones'][0][u'attributes'],
            {u'5': str(unixtime(2001, 1, 20, 0, 1, 1))},
        )

    def test_phones__secured_time(self):
        response = self._build_response(phones=[{
            u'id': 44,
            u'secured': datetime(2001, 1, 20, 0, 1, 1),
        }])

        user_info = self._get_user(response)
        eq_(
            user_info[u'phones'][0][u'attributes'],
            {u'6': str(unixtime(2001, 1, 20, 0, 1, 1))},
        )

    def test_phones__str_time(self):
        response = self._build_response(phones=[{
            u'id': 44,
            u'created': '123456',
        }])

        user_info = self._get_user(response)
        eq_(user_info[u'phones'][0][u'attributes'], {u'2': '123456'})


class PhoneOperationsTestMixin(object):
    """Тесты для генераторов ответов с телефонными операциями."""
    def test_phone_ops__no_phone_ops_when_phone_ops_arg_is_not_specified(self):
        response = self._build_response()

        user_info = self._get_user(response)
        ok_(u'phone_operations' not in user_info)

    def test_phone_ops__empty_phone_ops_when_phone_ops_arg_is_empty_list(self):
        response = self._build_response(phone_operations=[])

        user_info = self._get_user(response)
        eq_(user_info[u'phone_operations'], {})

    @raises(ValueError)
    def test_phone_ops__value_error_when_no_security_identity_and_no_phone_number_in_phone_op(self):
        self._build_response(phone_operations=[{u'phone_id': 73}])

    @raises(ValueError)
    def test_phone_ops__value_error_when_phone_number_of_op_not_starts_with_plus_sign(self):
        self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'89028877666',
        }])

    def test_phone_ops__operation_id(self):
        response = self._build_response(phone_operations=[{
            u'id': 81,
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        ok_(u'81' in user_info[u'phone_operations'])

        op = parse_phone_operation(user_info[u'phone_operations'][u'81'])
        eq_(op[u'id'], 81)

    def test_phone_ops__single_operation(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        eq_(len(user_info[u'phone_operations']), 1)

    def test_phone_ops__many_operations(self):
        response = self._build_response(phone_operations=[
            {
                u'phone_id': 73,
                u'phone_number': u'+79028877666',
            },
            {
                u'phone_id': 74,
                u'phone_number': u'+79037766555',
            },
        ])

        user_info = self._get_user(response)
        eq_(len(user_info[u'phone_operations']), 2)

    def test_phone_ops__operation_id_are_genererated_automatically_when_not_specified(self):
        response = self._build_response(phone_operations=[
            {
                u'id': 5,
                u'phone_id': 73,
                u'phone_number': u'+79028877666',
            },
            {
                u'phone_id': 74,
                u'phone_number': u'+79037766555',
            },
        ])

        user_info = self._get_user(response)
        ok_(u'6' in user_info[u'phone_operations'])

        op = parse_phone_operation(user_info[u'phone_operations'][u'6'])
        eq_(op[u'id'], 6)

    def test_phone_ops__phone_id(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'phone_id'], 73)

    def test_phone_ops__security_identity_when_op_is_not_on_secure_number(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'security_identity'], 79028877666)

    def test_phone_ops__security_identity_when_op_is_on_secure_number(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'security_identity': SECURITY_IDENTITY,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'security_identity'], SECURITY_IDENTITY)

    def test_phone_ops__op_type_is_bind(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'type': u'bind',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'type'], u'bind')

    def test_phone_ops__op_type_is_bind_when_not_specified(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'type'], u'bind')

    def test_phone_ops__op_type_is_remove(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'type': u'remove',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'type'], 'remove')

    def test_phone_ops__op_type_is_securify(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'type': u'securify',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'type'], u'securify')

    def test_phone_ops__op_type_is_replace(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'type': u'replace',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'type'], u'replace')

    def test_phone_ops__started(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'started': datetime(2003, 4, 5, 1, 1, 0),
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'started'], unixtime(2003, 4, 5, 1, 1, 0))

    def test_phone_ops__started_default_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'started'], unixtime(2000, 1, 20, 0, 0, 1))

    def test_phone_ops__started_none_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'started': None,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'started'], None)

    def test_phone_ops__finished(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'finished': datetime(2003, 4, 5, 1, 1, 0),
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'finished'], unixtime(2003, 4, 5, 1, 1, 0))

    def test_phone_ops__finished_default_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'finished'], None)

    def test_phone_ops__finished_none_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'finished': None,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'finished'], None)

    def test_phone_ops__code_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'code_value': u'0000',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_value'], u'0000')

    def test_phone_ops__code_value_default_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_value'], u'3232')

    def test_phone_ops__code_value_none_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'code_value': None,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_value'], None)

    def test_phone_ops__code_checks_count(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'code_checks_count': 4,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_checks_count'], 4)

    def test_phone_ops__code_checks_count_default_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_checks_count'], 0)

    def test_phone_ops__code_checks_count_none_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'code_checks_count': None,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_checks_count'], 0)

    def test_phone_ops__code_send_count(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'code_send_count': 4,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_send_count'], 4)

    def test_phone_ops__code_send_count_default_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_send_count'], 1)

    def test_phone_ops__code_send_count_none_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'code_send_count': None,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_send_count'], 0)

    def test_phone_ops__code_last_sent(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'code_last_sent': datetime(2003, 4, 5, 1, 1, 0),
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_last_sent'], unixtime(2003, 4, 5, 1, 1, 0))

    def test_phone_ops__code_last_sent_default_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_last_sent'], unixtime(2000, 1, 20, 0, 0, 1))

    def test_phone_ops__code_last_sent_none_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'code_last_sent': None,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_last_sent'], None)

    def test_phone_ops__code_confirmed(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'code_confirmed': datetime(2003, 4, 5, 1, 1, 0),
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_confirmed'], unixtime(2003, 4, 5, 1, 1, 0))

    def test_phone_ops__code_confirmed_default_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_confirmed'], None)

    def test_phone_ops__code_confirmed_none_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'code_confirmed': None,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'code_confirmed'], None)

    def test_phone_ops__password_verified(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'password_verified': datetime(2003, 4, 5, 1, 1, 0),
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'password_verified'], unixtime(2003, 4, 5, 1, 1, 0))

    def test_phone_ops__password_verified_default_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'password_verified'], None)

    def test_phone_ops__password_verified_none_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'password_verified': None,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'password_verified'], None)

    def test_phone_ops__flags(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'flags': PhoneOperationFlags(1),
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'flags'], int(PhoneOperationFlags(1)))

    def test_phone_ops__flags_default_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'flags'], int(PhoneOperationFlags(0)))

    def test_phone_ops__flags_none_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'flags': None,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'flags'], int(PhoneOperationFlags(0)))

    def test_phone_ops__phone_id2(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'phone_id2': 74,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'phone_id2'], 74)

    def test_phone_ops__phone_id2_default_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'phone_id2'], None)

    def test_phone_ops__phone_id2_none_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'phone_id2': None,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'phone_id2'], None)

    def test_phone_ops__uid(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
            u'uid': UID_ALPHA,
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'uid'], UID_ALPHA)

    def test_phone_ops__uid_default_value(self):
        response = self._build_response(phone_operations=[{
            u'phone_id': 73,
            u'phone_number': u'+79028877666',
        }])

        user_info = self._get_user(response)
        op = parse_phone_operation(user_info[u'phone_operations'][u'1'])
        eq_(op[u'uid'], 1)


class PhoneBindingsTestMixin(object):
    def test_phone_bindings__default(self):
        response = self._build_response()
        user_info = self._get_user(response)
        ok_('phone_bindings' not in user_info)

    def test_phone_bindings__none(self):
        response = self._build_response(phone_bindings=None)
        user_info = self._get_user(response)
        ok_('phone_bindings' not in user_info)

    def test_phone_bindings__no_bindings(self):
        response = self._build_response(phone_bindings=[])

        user_info = self._get_user(response)

        eq_(user_info['phone_bindings'], [])

    def test_phone_bindings__default_binding(self):
        response = self._build_response(phone_bindings=[{}])

        user_info = self._get_user(response)

        eq_(
            user_info['phone_bindings'],
            [{
                'uid': '1',
                'type': 'history',
                'number': '79011111111',
                'phone_id': '1',
                'bound': '12345',
                'flags': '0',
            }],
        )

    def test_phone_bindings__override_default(self):
        flags = PhoneBindingsFlags()
        flags.should_ignore_binding_limit = True
        response = self._build_response(
            phone_bindings=[{
                'uid': UID_ALPHA,
                'type': 'current',
                'number': PHONE_NUMBER_ALPHA,
                'phone_id': PHONE_ID1,
                'bound': TEST_DATE,
                'flags': flags,
            }],
        )

        user_info = self._get_user(response)

        eq_(
            user_info['phone_bindings'],
            [{
                'uid': str(UID_ALPHA),
                'type': 'current',
                'number': str(int(PHONE_NUMBER_ALPHA)),
                'phone_id': str(PHONE_ID1),
                'bound': str(to_unixtime(TEST_DATE)),
                'flags': '1',
            }],
        )

    def test_phone_bindings__many_bindings(self):
        response = self._build_response(
            phone_bindings=[
                {
                    'type': 'current',
                    'phone_id': PHONE_ID1,
                },
                {
                    'type': 'history',
                    'phone_id': None,
                },
            ],
        )

        user_info = self._get_user(response)

        eq_(
            user_info['phone_bindings'],
            [
                {
                    'uid': '1',
                    'type': 'current',
                    'number': '79011111111',
                    'phone_id': str(PHONE_ID1),
                    'bound': '12345',
                    'flags': '0',
                },
                {
                    'uid': '1',
                    'type': 'history',
                    'number': '79011111111',
                    'phone_id': '',
                    'bound': '12345',
                    'flags': '0',
                },
            ],
        )


class EmailsTestMixin(object):
    def test_emails__no_emails(self):
        response = self._build_response()

        user_info = self._get_user(response)
        ok_('emails' not in user_info)

    def test_emails__empty_emails(self):
        response = self._build_response(email_attributes=[])

        user_info = self._get_user(response)
        ok_('emails' not in user_info)

    def test_emails__simple(self):
        email = {
            'id': TEST_EMAIL_ID1,
            'attributes': {
                EMAIL_ANT['address']: TEST_EMAIL1,
                EMAIL_ANT['created']: TEST_UNIXTIME1,
                EMAIL_ANT['confirmed']: TEST_UNIXTIME2,
                EMAIL_ANT['bound']: TEST_UNIXTIME3,
                EMAIL_ANT['is_rpop']: True,
                EMAIL_ANT['is_unsafe']: True,
                EMAIL_ANT['is_silent']: True,
            },
        }
        response = self._build_response(email_attributes=[email])

        user_info = self._get_user(response)
        eq_(
            user_info['emails'],
            [
                {
                    'id': TEST_EMAIL_ID1,
                    'attributes': {
                        '1': TEST_EMAIL1,
                        '2': TEST_UNIXTIME1,
                        '3': TEST_UNIXTIME2,
                        '4': TEST_UNIXTIME3,
                        '5': True,
                        '6': True,
                        '7': True,
                    },
                },
            ],
        )


class WebauthnCredentialsTestMixin(object):
    def test_no_creds(self):
        response = self._build_response()

        user_info = self._get_user(response)
        ok_('webauthn_credentials' not in user_info)

    def test_empty_creds(self):
        response = self._build_response(webauthn_credentials=[])

        user_info = self._get_user(response)
        eq_(user_info['webauthn_credentials'], [])

    def test_simple(self):
        cred = {
            'id': 2,
            'external_id': 'cred-id',
            'public_key': '1:pub-key',
            'sign_count': 42,
            'device_name': 'device-name',
            'created': TEST_DATE,
        }
        response = self._build_response(webauthn_credentials=[cred])

        user_info = self._get_user(response)
        eq_(
            user_info['webauthn_credentials'],
            [
                {
                    'id': '2',
                    'attributes': {
                        str(WEBAUTHN_ANT['external_id']): 'cred-id',
                        str(WEBAUTHN_ANT['public_key']): '1:pub-key',
                        str(WEBAUTHN_ANT['sign_count']): '42',
                        str(WEBAUTHN_ANT['device_name']): 'device-name',
                        str(WEBAUTHN_ANT['created']): str(to_unixtime(TEST_DATE)),
                    },
                },
            ],
        )


class ScholarTestMixin(object):
    def test_scholar_session(self):
        response = self._build_response(is_scholar_session=True)
        user_info = self._get_user(response)
        assert user_info.get('auth', dict()).get('is_scholar_session')


class TestUserinfoResponse(TestCase,
                           PhonesTestMixin,
                           PhoneOperationsTestMixin,
                           PhoneBindingsTestMixin,
                           EmailsTestMixin,
                           WebauthnCredentialsTestMixin):
    def _get_user(self, response):
        response_dict = json.loads(response)
        return response_dict[u'users'][0]

    def _build_response(self, **kwargs):
        return blackbox_userinfo_response(**kwargs)


class TestLoginResponse(
    TestCase,
    PhonesTestMixin,
    PhoneOperationsTestMixin,
    PhoneBindingsTestMixin,
    EmailsTestMixin,
    WebauthnCredentialsTestMixin,
):
    def _get_user(self, response):
        return json.loads(response)

    def _build_response(self, **kwargs):
        return blackbox_login_response(**kwargs)

    def test_scholar_session(self):
        response = self._build_response(is_scholar_session=True)
        user_info = self._get_user(response)
        assert user_info.get('is_scholar_session')


class TestSessionidResponse(
    TestCase,
    PhonesTestMixin,
    PhoneOperationsTestMixin,
    PhoneBindingsTestMixin,
    WebauthnCredentialsTestMixin,
    ScholarTestMixin,

):
    def _get_user(self, response):
        return json.loads(response)

    def _build_response(self, **kwargs):
        return blackbox_sessionid_response(**kwargs)


class TestSessionidMultiSessionSingleSessionResponse(
    TestCase,
    PhonesTestMixin,
    PhoneOperationsTestMixin,
    PhoneBindingsTestMixin,
    EmailsTestMixin,
    WebauthnCredentialsTestMixin,
    ScholarTestMixin,
):
    def _get_user(self, response):
        response_dict = json.loads(response)
        return response_dict[u'users'][0]

    def _build_response(self, **kwargs):
        return blackbox_sessionid_multi_response(**kwargs)


class TestSessionidMultiSessionManySessionsResponse(
    TestCase,
    PhonesTestMixin,
    PhoneOperationsTestMixin,
    PhoneBindingsTestMixin,
    EmailsTestMixin,
    WebauthnCredentialsTestMixin,
    ScholarTestMixin,
):
    def _get_user(self, response):
        response_dict = json.loads(response)
        return response_dict[u'users'][1]

    def _build_response(self, **kwargs):
        response = blackbox_sessionid_multi_response()
        return blackbox_sessionid_multi_append_user(response, **kwargs)


class TestOauthResponse(TestCase,
                        PhonesTestMixin,
                        PhoneOperationsTestMixin,
                        PhoneBindingsTestMixin,
                        EmailsTestMixin,
                        WebauthnCredentialsTestMixin):
    def _get_user(self, response):
        return json.loads(response)

    def _build_response(self, **kwargs):
        return blackbox_oauth_response(**kwargs)


class TestBlackboxPhoneOperationsResponse(TestCase):
    def test_empty(self):
        rv = blackbox_phone_operations_response([])

        rv = json.loads(rv)
        eq_(rv, {'phone_operations': [], 'total_count': 0, 'count': 0})

    def test_default(self):
        rv = blackbox_phone_operations_response([{'phone_number': '+70987654321'}])

        rv = json.loads(rv)
        eq_(
            rv,
            {
                'phone_operations': [
                    '1,1,0,70987654321,1,%d,0,3232,0,1,%d,0,0,0,0' % (
                        to_unixtime(datetime(2000, 1, 20, 0, 0, 1)),
                        to_unixtime(datetime(2000, 1, 20, 0, 0, 1)),
                    ),
                ],
                'total_count': 1,
                'count': 1,
            },
        )

    def test_override_defaults(self):
        flags = PhoneOperationFlags()
        flags.should_ignore_binding_limit = True
        started = datetime(2000, 1, 1)
        finished = datetime(2000, 1, 5)
        code_last_sent = datetime(2000, 1, 2)
        code_confirmed = datetime(2000, 1, 3)
        password_verified = datetime(2000, 1, 4)
        rv = blackbox_phone_operations_response([{
            'id': 13,
            'uid': 17,
            'phone_id': 19,
            'security_identity': 1,
            'type': 'remove',
            'started': started,
            'finished': finished,
            'code_value': '1234',
            'code_checks_count': 7,
            'code_send_count': 3,
            'code_last_sent': code_last_sent,
            'code_confirmed': code_confirmed,
            'password_verified': password_verified,
            'flags': flags,
            'phone_id2': '23',
        }])

        rv = json.loads(rv)
        eq_(
            rv,
            {
                'phone_operations': [
                    '13,17,19,1,2,%d,%d,1234,7,3,%d,%d,%d,2,23' % (
                        to_unixtime(started),
                        to_unixtime(finished),
                        to_unixtime(code_last_sent),
                        to_unixtime(code_confirmed),
                        to_unixtime(password_verified),
                    ),
                ],
                'total_count': 1,
                'count': 1,
            },
        )


class TestBlackboxJsonErrorResponse(TestCase):
    def test_invalid_params(self):
        response = json.loads(
            blackbox_json_error_response(u'INVALID_PARAMS'),
        )
        eq_(
            response[u'exception'],
            {
                u'id': 2,
                u'value': u'INVALID_PARAMS',
            },
        )

    def test_message(self):
        response = json.loads(
            blackbox_json_error_response(u'test_code', u'test message'),
        )
        eq_(response[u'error'], u'test message')


class TestBlackboxYakeyBackupResponse(TestCase):
    def test_defaults(self):
        response = json.loads(blackbox_yakey_backup_response())
        eq_(len(response['yakey_backups']), 1)
        eq_(
            response['yakey_backups'][0],
            dict(
                phone_number=79261234567,
                backup='abc123456def',
                updated=TimeNow(),
                device_name=None,
            ),
        )

    def test_info_only(self):
        response = json.loads(blackbox_yakey_backup_response(info_only=True))
        eq_(len(response['yakey_backups']), 1)
        eq_(
            response['yakey_backups'][0],
            dict(
                phone_number=79261234567,
                updated=TimeNow(),
                device_name=None,
            ),
        )

    def test_found(self):
        response = json.loads(
            blackbox_yakey_backup_response(
                phone_number=79090000001,
                backup='found_backup',
                device_name='my device',
            ),
        )
        eq_(len(response['yakey_backups']), 1)
        eq_(
            response['yakey_backups'][0],
            dict(
                phone_number=79090000001,
                backup='found_backup',
                updated=TimeNow(),
                device_name='my device',
            ),
        )

    def test_not_found(self):
        response = json.loads(blackbox_yakey_backup_response(is_found=False))
        eq_(response['yakey_backups'], [])


class TestBlackboxDeletionOperationsResponse(TestCase):
    def test_defaults(self):
        response = json.loads(blackbox_deletion_operations_response())
        eq_(response, {'deletion_operations': [{'uid': '1'}]})

    def test_empty(self):
        response = json.loads(blackbox_deletion_operations_response([]))
        eq_(response, {'deletion_operations': []})

    def test_many(self):
        response = json.loads(blackbox_deletion_operations_response([{'uid': 1}, {'uid': 2}]))
        eq_(response, {'deletion_operations': [{'uid': '1'}, {'uid': '2'}]})


class TestBlackboxGetRecoveryKeysResponse(TestCase):
    def test_ok(self):
        response = json.loads(blackbox_get_recovery_keys_response('key'))
        eq_(
            response,
            {
                'recovery_key': 'key',
            },
        )

    def test_not_found(self):
        response = json.loads(blackbox_get_recovery_keys_response(None))
        eq_(
            response,
            {
                'recovery_key': '',
            },
        )


class TestBlackboxCheckRfcTotpResponse(TestCase):
    def test_ok(self):
        response = json.loads(blackbox_check_rfc_totp_response())
        eq_(
            response,
            {
                'status': BLACKBOX_CHECK_RFC_TOTP_VALID_STATUS,
                'time': 100500,
            },
        )

    def test_invalid(self):
        response = json.loads(blackbox_check_rfc_totp_response(status=BLACKBOX_CHECK_RFC_TOTP_INVALID_STATUS))
        eq_(
            response,
            {
                'status': BLACKBOX_CHECK_RFC_TOTP_INVALID_STATUS,
            },
        )


class TestBlackboxCheckIpResponse(TestCase):
    def test_ok(self):
        response = json.loads(blackbox_check_ip_response(yandexip=True))
        eq_(
            response,
            {
                'yandexip': True,
            },
        )


@with_settings(
    BLACKBOX_URL=u'http://blac.kb.ox/',
    BLACKBOX_ATTRIBUTES=[],
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=[],
)
class TestBlackboxYasmsConfigurator(TestCase):
    def setUp(self):
        self._fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self._fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self._fake_tvm_credentials_manager.start()

        self._blackbox_builder_faker = FakeBlackbox()
        self._blackbox_builder_faker.start()

        self._confr = BlackboxYasmsConfigurator(self._blackbox_builder_faker)
        self._blackbox_builder = Blackbox()

    def tearDown(self):
        self._blackbox_builder_faker.stop()
        self._fake_tvm_credentials_manager.stop()
        del self._blackbox_builder_faker
        del self._fake_tvm_credentials_manager

    def test_userinfo_initial_state(self):
        user_info = self._blackbox_builder.userinfo(
            uid=UID_ALPHA,
            phones=u'all',
            need_phone_operations=True,
        )

        eq_(user_info[u'uid'], UID_ALPHA)
        eq_(user_info[u'phones'], {})
        eq_(user_info[u'phone_operations'], {})

    def test_phone_bindings_initial_state(self):
        bindings = self._blackbox_builder.phone_bindings(
            need_current=True,
            need_history=True,
            phone_numbers=[PHONE_NUMBER_ALPHA, PHONE_NUMBER_BETA],
        )

        eq_(bindings, [])

    def test_user_info_after_register_phone(self):
        self._confr.register_phone(UID_ALPHA, PHONE_NUMBER_ALPHA, TEST_DATE)

        user_info = self._blackbox_builder.userinfo(
            uid=UID_ALPHA,
            phones=u'all',
            phone_attributes=[u'number', u'created', u'bound'],
            need_phone_operations=True,
        )

        eq_(user_info[u'uid'], UID_ALPHA)
        eq_(
            user_info[u'phones'][1][u'attributes'][u'number'],
            PHONE_NUMBER_ALPHA,
        )
        eq_(
            user_info[u'phones'][1][u'attributes'][u'created'],
            to_unixtime(TEST_DATE),
        )
        ok_(u'bound' not in user_info[u'phones'][1][u'attributes'])
        eq_(user_info[u'phones'][1][u'operation'][u'type'], u'bind')

    def test_phone_bindings_after_register_phone(self):
        self._confr.register_phone(UID_ALPHA, PHONE_NUMBER_ALPHA, TEST_DATE)

        bindings = self._blackbox_builder.phone_bindings(
            need_current=True,
            need_history=True,
            phone_numbers=[PHONE_NUMBER_ALPHA, PHONE_NUMBER_BETA],
        )

        eq_(bindings, [])

    def test_user_info_after_confirm_phone(self):
        self._confr.register_phone(UID_ALPHA, PHONE_NUMBER_ALPHA, TEST_DATE)
        self._confr.confirm_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            TEST_DATE + MINUTE,
        )

        user_info = self._blackbox_builder.userinfo(
            uid=UID_ALPHA,
            phones=u'all',
            phone_attributes=[u'number', u'created', u'bound'],
            need_phone_operations=True,
        )

        eq_(user_info[u'uid'], UID_ALPHA)
        eq_(
            user_info[u'phones'][1][u'attributes'][u'number'],
            PHONE_NUMBER_ALPHA,
        )
        eq_(
            user_info[u'phones'][1][u'attributes'][u'created'],
            to_unixtime(TEST_DATE),
        )
        eq_(
            user_info[u'phones'][1][u'attributes'][u'bound'],
            to_unixtime(TEST_DATE + MINUTE),
        )
        ok_(user_info[u'phones'][1][u'operation'] is None)

    def test_phone_bindings_after_confirm_phone(self):
        self._confr.register_phone(UID_ALPHA, PHONE_NUMBER_ALPHA, TEST_DATE)
        self._confr.confirm_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            TEST_DATE + MINUTE,
        )
        self._confr.register_phone(UID_ALPHA, PHONE_NUMBER_BETA, TEST_DATE)
        self._confr.confirm_phone(
            UID_ALPHA,
            PHONE_NUMBER_BETA,
            TEST_DATE,
        )

        bindings = self._blackbox_builder.phone_bindings(
            need_current=True,
            need_history=True,
            phone_numbers=[PHONE_NUMBER_ALPHA],
        )

        assert bindings ==\
               [
                   {
                       u'type': u'history',
                       u'uid': UID_ALPHA,
                       u'phone_number': PhoneNumber.parse(PHONE_NUMBER_ALPHA),
                       u'phone_id': 1,
                       u'binding_time': to_unixtime(TEST_DATE + MINUTE),
                       u'should_ignore_binding_limit': 0,
                   },
                   {
                       u'type': u'current',
                       u'uid': UID_ALPHA,
                       u'phone_number': PhoneNumber.parse(PHONE_NUMBER_ALPHA),
                       u'phone_id': 1,
                       u'binding_time': to_unixtime(TEST_DATE + MINUTE),
                       u'should_ignore_binding_limit': 0,
                   },
               ]

    def test_user_info_after_delete_phone(self):
        self._confr.register_phone(UID_ALPHA, PHONE_NUMBER_ALPHA, TEST_DATE)
        self._confr.confirm_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            TEST_DATE + MINUTE,
        )
        self._confr.delete_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            TEST_DATE + 2 * MINUTE,
        )

        user_info = self._blackbox_builder.userinfo(
            uid=UID_ALPHA,
            phones=u'all',
            phone_attributes=[u'number', u'created', u'bound'],
            need_phone_operations=True,
        )

        eq_(user_info[u'uid'], UID_ALPHA)
        eq_(user_info[u'phones'], {})

    def test_phone_bindings_after_delete_phone(self):
        self._confr.register_phone(UID_ALPHA, PHONE_NUMBER_ALPHA, TEST_DATE)
        self._confr.confirm_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            TEST_DATE + MINUTE,
        )
        self._confr.delete_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            TEST_DATE + 2 * MINUTE,
        )

        bindings = self._blackbox_builder.phone_bindings(
            need_current=True,
            need_history=True,
            phone_numbers=[PHONE_NUMBER_ALPHA],
        )

        eq_(
            bindings,
            [
                {
                    u'type': u'history',
                    u'uid': UID_ALPHA,
                    u'phone_number': PhoneNumber.parse(PHONE_NUMBER_ALPHA),
                    u'phone_id': 1,
                    u'binding_time': to_unixtime(TEST_DATE + MINUTE),
                    u'should_ignore_binding_limit': False,
                },
            ],
        )

    def test_user_info_after_confirm_and_delete_phone(self):
        self._confr.confirm_and_delete_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            [TEST_DATE, TEST_DATE + MINUTE],
        )

        user_info = self._blackbox_builder.userinfo(
            uid=UID_ALPHA,
            phones=u'all',
            phone_attributes=[u'number', u'created', u'bound'],
            need_phone_operations=True,
        )

        eq_(user_info[u'uid'], UID_ALPHA)
        eq_(user_info[u'phones'], {})

    def test_phone_bindings_after_confirm_and_delete_phone(self):
        self._confr.confirm_and_delete_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            [TEST_DATE, TEST_DATE + MINUTE],
        )

        bindings = self._blackbox_builder.phone_bindings(
            need_current=True,
            need_history=True,
            phone_numbers=[PHONE_NUMBER_ALPHA],
        )

        eq_(
            bindings,
            [
                {
                    u'type': u'history',
                    u'uid': UID_ALPHA,
                    u'phone_number': PhoneNumber.parse(PHONE_NUMBER_ALPHA),
                    u'phone_id': 1,
                    u'binding_time': to_unixtime(TEST_DATE),
                    u'should_ignore_binding_limit': False,
                },
                {
                    u'type': u'history',
                    u'uid': UID_ALPHA,
                    u'phone_number': PhoneNumber.parse(PHONE_NUMBER_ALPHA),
                    u'phone_id': 2,
                    u'binding_time': to_unixtime(TEST_DATE + MINUTE),
                    u'should_ignore_binding_limit': False,
                },
            ],
        )

    def test_user_info_after_confirm_phone_by_many_users(self):
        for uid in (UID_ALPHA, UID_BETA):
            self._confr.register_phone(uid, PHONE_NUMBER_ALPHA, TEST_DATE)
            self._confr.confirm_phone(
                uid,
                PHONE_NUMBER_ALPHA,
                TEST_DATE + MINUTE,
            )

        user_info = self._blackbox_builder.userinfo(
            uid=UID_ALPHA,
            phones=u'all',
            phone_attributes=[u'number', u'created', u'bound'],
            need_phone_operations=True,
        )

        eq_(user_info[u'uid'], UID_ALPHA)
        eq_(
            user_info[u'phones'][1][u'attributes'][u'number'],
            PHONE_NUMBER_ALPHA,
        )

        user_info = self._blackbox_builder.userinfo(
            uid=UID_BETA,
            phones=u'all',
            phone_attributes=[u'number', u'created', u'bound'],
            need_phone_operations=True,
        )

        eq_(user_info[u'uid'], UID_BETA)
        eq_(
            user_info[u'phones'][2][u'attributes'][u'number'],
            PHONE_NUMBER_ALPHA,
        )


@with_settings_hosts(
    BLACKBOX_URL='http://localhost/',
    BLACKBOX_ATTRIBUTES=[],
)
class TestBlackboxRequest(TestCase):
    def setUp(self):
        self._fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self._fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self._fake_tvm_credentials_manager.start()

        self._blackbox = Blackbox()
        self._fake_blackbox = FakeBlackbox()
        self._fake_blackbox.start()
        self._fake_blackbox.set_response_value('userinfo', blackbox_userinfo_response(uid=UID_ALPHA))
        self._fake_blackbox.set_response_value('sessionid', blackbox_sessionid_response())
        self._fake_blackbox.set_response_value('login', blackbox_login_response())
        self._fake_blackbox.set_response_value('oauth', blackbox_oauth_response())

    def tearDown(self):
        self._fake_blackbox.stop()
        self._fake_tvm_credentials_manager.stop()
        del self._fake_blackbox
        del self._fake_tvm_credentials_manager

    def test_contains_attributes__ok(self):
        for i, do_request in enumerate(self._get_calls()):
            do_request(attributes=['account.registration_datetime', 'person.firstname'])
            request = self._fake_blackbox.requests[i]
            request.assert_contains_attributes({'account.registration_datetime', 'person.firstname'})

    def test_contains_attributes__not_found(self):
        for i, do_request in enumerate(self._get_calls()):
            do_request(attributes=['person.firstname'])
            request = self._fake_blackbox.requests[i]
            with assert_raises(AssertionError):
                request.assert_contains_attributes({'account.registration_datetime'})

    def _get_calls(self):
        return [
            partial(self._blackbox.userinfo, uid=UID_ALPHA),
            partial(self._blackbox.sessionid, sessionid='sessionid', ip='127.0.0.1', host='yandex.ru'),
            partial(self._blackbox.login, uid=UID_ALPHA, version='version', password='password', ip='127.0.0.1'),
            partial(self._blackbox.oauth),
        ]
