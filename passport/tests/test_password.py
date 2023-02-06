# -*- coding: utf-8 -*-

import base64
from datetime import datetime
import unittest

from nose.tools import (
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.blackbox import BaseBlackboxError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_test_pwd_hashes_response,
    blackbox_userinfo_response,
    FakeBlackbox,
    get_parsed_blackbox_response,
)
from passport.backend.core.models.account import Account
from passport.backend.core.models.faker.account import default_account
from passport.backend.core.models.password import (
    build_password_subwords,
    check_password_equals_hash,
    default_encrypted_password,
    Password,
    PASSWORD_CHANGING_REASON_FLUSHED_BY_ADMIN,
    PASSWORD_CHANGING_REASON_HACKED,
    PASSWORD_CHANGING_REASON_PWNED,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_HEX,
    PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON,
    ScholarPassword,
)
from passport.backend.core.test.data import (
    TEST_PASSWORD_HASH_MD5_CRYPT_ARGON,
    TEST_PASSWORD_HASH_RAW_MD5_ARGON,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.test_utils.utils import PassportTestCase
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.undefined import Undefined


TEST_PASSWORD = 'abc'
TEST_PASSWORD_WITH_VERSION = '1:%s' % TEST_PASSWORD
TEST_MD5_CRYPT_HASH = '$1$aaaaaaaa$lWxWtPmiNjS/cwJnGm6fe0'
TEST_MD5_RAW_HASH = 'ab' * 16


@with_settings_hosts(BLACKBOX_URL='http://blackbox')
class BasePasswordTestCase(PassportTestCase):
    def __init__(self, *args, **kwargs):
        super(BasePasswordTestCase, self).__init__(*args, **kwargs)

        self.account = Account(uid=123)
        self.password = None

    def setUp(self):
        super(BasePasswordTestCase, self).setUp()

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

        self.blackbox = FakeBlackbox()
        self.blackbox.start()

    def tearDown(self):
        self.blackbox.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.blackbox
        del self.fake_tvm_credentials_manager

        super(BasePasswordTestCase, self).tearDown()


class PasswordTestMixin(object):
    def test_set_password(self):
        pas = self.password.set('test', 0, salt='aaaaaaaa')
        eq_(pas.encrypted_password, TEST_MD5_CRYPT_HASH)
        eq_(pas.encoding_version, PASSWORD_ENCODING_VERSION_MD5_CRYPT)
        eq_(
            pas.serialized_encrypted_password,
            '%s:%s' % (PASSWORD_ENCODING_VERSION_MD5_CRYPT, TEST_MD5_CRYPT_HASH),
        )
        eq_(pas.update_datetime, DatetimeNow())
        eq_(pas.quality, 0)
        eq_(pas.quality_version, 3)
        ok_(pas.is_set)
        ok_(pas.is_set_or_promised)

    def test_set_password_with_blackbox_hash_with_uid(self):
        self.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash='6:%s' % TEST_PASSWORD_HASH_MD5_CRYPT_ARGON),
        )

        pas = self.password.set('test', 0, get_hash_from_blackbox=True, version=6)
        eq_(pas.encrypted_password, TEST_PASSWORD_HASH_MD5_CRYPT_ARGON)
        eq_(pas.encoding_version, 6)
        eq_(pas.update_datetime, DatetimeNow())
        eq_(pas.quality, 0)
        eq_(pas.quality_version, 3)
        ok_(pas.is_set_or_promised)

    def test_set_password_with_blackbox_hash_without_uid(self):
        self.account.uid = Undefined
        pas = self.password.set('test', 0, get_hash_from_blackbox=True, version=5)
        eq_(pas.encrypted_password, Undefined)
        eq_(pas.encoding_version, Undefined)
        ok_(pas.is_set_or_promised)
        ok_(not pas.is_set)
        hash_provider = pas.password_hash_provider
        eq_(hash_provider.password, 'test')
        eq_(hash_provider.version, 5)
        assert_is_none(hash_provider.encrypted_password)
        eq_(pas.update_datetime, DatetimeNow())
        eq_(pas.quality, 0)
        eq_(pas.quality_version, 3)

    def test_set_password_with_blackbox_hash_fail(self):
        self.blackbox.set_blackbox_response_side_effect(
            'create_pwd_hash',
            BaseBlackboxError,
        )
        with assert_raises(BaseBlackboxError):
            self.password.set('test', 0, salt='aaaaaaaa', get_hash_from_blackbox=True, version=5)

    def test_set_password_with_blackbox_hash_bad_value(self):
        for value in (
            '',
            '123',
            ':10',
            '20:',
            ':',
            'xyz:123',
            '3:newhash',  # Версия, которую мы не просили
        ):
            self.blackbox.set_blackbox_response_value(
                'create_pwd_hash',
                blackbox_create_pwd_hash_response(password_hash=value),
            )
            with assert_raises(BaseBlackboxError):
                self.password.set('test', 0, salt='aaaaaaaa', get_hash_from_blackbox=True, version=5)

    def test_set_password_with_unknown_hash_version(self):
        with assert_raises(ValueError):
            self.password.set('test', 0, version=100500)

    def test_set_password_hash(self):
        pas = self.password.set_hash(TEST_MD5_CRYPT_HASH)
        eq_(pas.encrypted_password, TEST_MD5_CRYPT_HASH)
        eq_(pas.encoding_version, PASSWORD_ENCODING_VERSION_MD5_CRYPT)
        eq_(
            pas.serialized_encrypted_password,
            '%s:%s' % (PASSWORD_ENCODING_VERSION_MD5_CRYPT, TEST_MD5_CRYPT_HASH),
        )
        eq_(pas.update_datetime, DatetimeNow())

    def test_set_password_hash_with_blackbox(self):
        self.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash='%s:%s' % (
                PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON,
                TEST_PASSWORD_HASH_RAW_MD5_ARGON,
            )),
        )

        pas = self.password.set_hash(TEST_MD5_RAW_HASH, version=PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON)

        eq_(pas.encrypted_password, TEST_PASSWORD_HASH_RAW_MD5_ARGON)
        eq_(pas.encoding_version, PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON)
        eq_(
            pas.serialized_encrypted_password,
            '%s:%s' % (PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON, TEST_PASSWORD_HASH_RAW_MD5_ARGON),
        )
        eq_(pas.update_datetime, DatetimeNow())

    def test_set_password_hash_with_blackbox__blackbox_failed(self):
        self.blackbox.set_blackbox_response_side_effect(
            'create_pwd_hash',
            BaseBlackboxError,
        )
        with assert_raises(BaseBlackboxError):
            self.password.set_hash(TEST_MD5_RAW_HASH, version=PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON)

    def test_set_password_hash_with_different_version(self):
        pas = self.password.set_hash(
            'c4ca4238a0b923820dcc509a6f75849b',
            version=PASSWORD_ENCODING_VERSION_MD5_HEX,
        )
        eq_(pas.encrypted_password, 'c4ca4238a0b923820dcc509a6f75849b')
        eq_(pas.encoding_version, PASSWORD_ENCODING_VERSION_MD5_HEX)
        eq_(
            pas.serialized_encrypted_password,
            '%s:c4ca4238a0b923820dcc509a6f75849b' % PASSWORD_ENCODING_VERSION_MD5_HEX,
        )
        eq_(pas.update_datetime, DatetimeNow())

    def test_salt_is_random(self):
        pas = self.password.set('test', 0)
        hash1 = pas.encrypted_password

        pas.set('test', 0)
        hash2 = pas.encrypted_password

        ok_(hash1 != hash2)


class TestPassword(
    PasswordTestMixin,
    BasePasswordTestCase,
):
    def setUp(self):
        super(TestPassword, self).setUp()
        self.password = Password(self.account)

    def tearDown(self):
        del self.password
        super(TestPassword, self).tearDown()

    def test_set_quality(self):
        pas = self.password.set('testpass', quality=20)
        eq_(len(pas.encrypted_password), 34)
        eq_(pas.quality, 20)
        eq_(pas.quality_version, 3)
        eq_(pas.update_datetime, DatetimeNow())

    def test_set_hash_dont_change_quality(self):
        pas = self.password.set_hash(TEST_MD5_CRYPT_HASH)
        eq_(pas.quality, Undefined)
        eq_(pas.quality_version, Undefined)

    def test_set_hash_with_blackbox_dont_change_quality(self):
        self.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash='%s:%s' % (
                PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON,
                TEST_PASSWORD_HASH_RAW_MD5_ARGON,
            )),
        )

        pas = self.password.set_hash(TEST_MD5_RAW_HASH, version=PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON)

        eq_(pas.quality, Undefined)
        eq_(pas.quality_version, Undefined)

    def test_set_passwd_with_hosted_account_checks_email_for_password_quality(self):
        acc = Account().parse({'login': 'username', 'domain': 'test.com'})
        self.password.parent = acc

        self.password.set('username@test.com', quality=2)
        eq_(self.password.quality, 2)

    def test_set_passwd_with_cyrilic_domain_checks_email_for_password_quality(self):
        login = 'username'
        domain = u'окна.рф'.encode('idna').decode('utf-8')
        acc = Account().parse({'login': login, 'domain': domain})
        self.password.parent = acc

        email = '%s@%s' % (login, domain)
        self.password.set(email, quality=6)
        eq_(self.password.quality, 6)


class TestScholarPassword(
    PasswordTestMixin,
    BasePasswordTestCase,
):
    def setUp(self):
        super(TestScholarPassword, self).setUp()
        self.password = ScholarPassword(self.account)

    def tearDown(self):
        del self.password
        super(TestScholarPassword, self).tearDown()

    def test_fields(self):
        self.password.set_hash('pwd')

        assert dict(self.password) == dict(
            encoding_version=1,
            encrypted_password='pwd',
            serialized_encrypted_password='1:pwd',
            update_datetime=DatetimeNow(),
        )

    def test_parse(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(
                attributes={
                    'account.scholar_password': '2:pwd',
                },
            ),
        )
        acc = Account().parse(response)

        assert acc.scholar_password
        assert acc.scholar_password.encoding_version == 2
        assert acc.scholar_password.encrypted_password == 'pwd'
        assert acc.scholar_password.parent is acc
        assert not acc.scholar_password.password_hash_provider
        assert not acc.scholar_password.update_datetime


class TestPasswordSidProperties(unittest.TestCase):

    def test_simple_is_changing_required(self):
        acc = default_account(uid=10, alias='testlogin').parse({
            'password.forced_changing_reason': '1',
            'subscriptions': {8: {'login_rule': 4, 'sid': 8}},
        })
        eq_(acc.password.forced_changing_reason, '1')
        eq_(acc.password.is_changing_required, True)

        acc = default_account(uid=10, alias='testlogin').parse({
            'subscriptions': {8: {'login_rule': 1, 'sid': 8}},
        })
        eq_(acc.password.forced_changing_reason, Undefined)
        eq_(acc.password.is_changing_required, False)

        acc.password.setup_password_changing_requirement()
        eq_(acc.subscriptions[8].database_login, 'testlogin')

        acc.password.setup_password_changing_requirement(is_required=True)
        eq_(acc.password.forced_changing_reason, PASSWORD_CHANGING_REASON_HACKED)
        eq_(acc.password.forced_changing_time, DatetimeNow())

        acc.password.setup_password_changing_requirement(is_required=False)
        eq_(acc.password.forced_changing_reason, None)
        eq_(acc.password.forced_changing_time, None)

    def test_is_changing_required_set_suspend(self):
        acc = default_account()
        eq_(acc.password.forced_changing_reason, Undefined)

        acc.password.setup_password_changing_requirement(is_required=True)
        eq_(acc.password.forced_changing_reason, PASSWORD_CHANGING_REASON_HACKED)
        eq_(acc.password.pwn_forced_changing_suspended_at, Undefined)

        acc.password.setup_password_changing_requirement(is_required=False)
        eq_(acc.password.forced_changing_reason, None)
        eq_(acc.password.pwn_forced_changing_suspended_at, Undefined)

        acc.password.setup_password_changing_requirement(is_required=True, changing_reason=PASSWORD_CHANGING_REASON_PWNED)
        eq_(acc.password.forced_changing_reason, PASSWORD_CHANGING_REASON_PWNED)
        eq_(acc.password.pwn_forced_changing_suspended_at, Undefined)

        acc.password.setup_password_changing_requirement(is_required=False)
        eq_(acc.password.forced_changing_reason, None)
        eq_(acc.password.pwn_forced_changing_suspended_at, DatetimeNow())

    def test_is_creating_required(self):
        acc = Account(uid=10).parse({})
        eq_(acc.password.is_creating_required, False)

        acc = Account(uid=10).parse({'subscriptions': {100: {'login_rule': 0, 'sid': 100}}})
        eq_(acc.password.is_creating_required, False)

        acc = Account(uid=10).parse({'subscriptions': {100: {'login_rule': 1, 'sid': 100}}})
        eq_(acc.password.is_creating_required, True)

        acc = Account(uid=10).parse({'subscriptions': {100: {'login_rule': 2, 'sid': 100}}})
        eq_(acc.password.is_creating_required, False)

    def test_is_strong_password_required(self):
        acc = Account(uid=10).parse({})
        eq_(acc.is_strong_password_required, False)

        acc = Account(uid=10).parse({
            'login': 'testlogin',
            'subscriptions': {67: {'sid': 67}},
        })
        eq_(acc.is_strong_password_required, True)

        acc.is_strong_password_required = False
        ok_(67 not in acc.subscriptions)

        acc.is_strong_password_required = True
        ok_(67 in acc.subscriptions)
        eq_(acc.subscriptions[67].database_login, 10)

    def test_unset_is_creating_required(self):
        acc = Account(uid=10).parse({})
        acc.password.is_creating_required = False
        ok_(not acc.subscriptions)

        acc = Account(uid=10).parse({'subscriptions': {100: {'login_rule': 0, 'sid': 100}}})
        acc.password.is_creating_required = False
        ok_(100 not in acc.subscriptions)

        acc = Account(uid=10).parse({'subscriptions': {100: {'login_rule': 1, 'sid': 100}}})
        acc.password.is_creating_required = False
        ok_(100 not in acc.subscriptions)

        acc = Account(uid=10).parse({'subscriptions': {100: {'login_rule': 2, 'sid': 100}}})
        acc.password.is_creating_required = False
        ok_(100 not in acc.subscriptions)

    def test_set_is_creating_required(self):
        acc = Account(uid=10).parse({})
        acc.password.is_creating_required = True
        eq_(acc.subscriptions[100].login_rule, 1)

        acc = Account(uid=10).parse({'subscriptions': {100: {'login_rule': 0, 'sid': 100}}})
        acc.password.is_creating_required = True
        eq_(acc.subscriptions[100].login_rule, 1)

        acc = Account(uid=10).parse({'subscriptions': {100: {'login_rule': 1, 'sid': 100}}})
        acc.password.is_creating_required = True
        eq_(acc.subscriptions[100].login_rule, 1)

        acc = Account(uid=10).parse({'subscriptions': {100: {'login_rule': 2, 'sid': 8}}})
        acc.password.is_creating_required = True
        eq_(acc.subscriptions[100].login_rule, 1)

    def test_is_set(self):
        acc = Account(uid=10).parse({})
        eq_(acc.password.is_set, False)

        acc.password.encrypted_password = TEST_PASSWORD
        eq_(acc.password.is_set, True)

    def test_is_weak_by_unknown_quality(self):
        acc = Account(uid=10).parse({})
        acc.password.encrypted_password = TEST_PASSWORD

        eq_(acc.password.quality, Undefined)
        eq_(acc.password.quality_version, Undefined)

        eq_(acc.password.is_weak, True)

    def test_is_weak_by_quality(self):
        acc = Account(uid=10).parse({
            'password_quality.quality.uid': 39,
            'password_quality.version.uid': 2,
        })
        acc.password.encrypted_password = TEST_PASSWORD

        eq_(acc.password.quality, 39)
        eq_(acc.password.quality_version, 2)

        eq_(acc.password.is_weak, True)

    def test_is_weak_by_quality_for_strong_policy(self):
        acc = Account(uid=10).parse({
            'password.encrypted': TEST_PASSWORD_WITH_VERSION,
            'password_quality.quality.uid': 50,
            'password_quality.version.uid': 2,
        })
        ok_(not acc.is_strong_password_required)
        ok_(not acc.password.is_weak)

        acc = Account(uid=10).parse({
            'login': 'testlogin',
            'subscriptions': {67: {'sid': 67}},
            'password.encrypted': TEST_PASSWORD_WITH_VERSION,
            'password_quality.quality.uid': 50,
            'password_quality.version.uid': 2,
        })
        ok_(acc.is_strong_password_required)
        ok_(acc.password.is_weak)

    def test_error_is_weak_password_not_set(self):
        acc = Account(uid=10).parse({})
        acc.password.encrypted_password = ''

        assert_raises(ValueError, lambda: acc.password.is_weak)

    def test_is_weak_by_length(self):
        acc = Account(uid=10).parse({
            'password.encrypted': TEST_PASSWORD_WITH_VERSION,
            'password_quality.quality.uid': 90,
            'password_quality.version.uid': 2,
        })
        ok_(not acc.password.is_weak)

        acc.password.length = 1
        ok_(acc.password.is_weak)

        acc.password.length = 20
        ok_(not acc.password.is_weak)

    def test_is_weak_by_length_for_strong_policy(self):
        acc = Account(uid=10).parse({
            'password.encrypted': TEST_PASSWORD_WITH_VERSION,
            'password_quality.quality.uid': 50,
            'password_quality.version.uid': 2,
        })
        acc.password.length = 8

        ok_(not acc.is_strong_password_required)
        ok_(not acc.password.is_weak)

        acc = Account(uid=10).parse({
            'login': 'testlogin',
            'subscriptions': {67: {'sid': 67}},
            'password.encrypted': TEST_PASSWORD_WITH_VERSION,
            'password_quality.quality.uid': 50,
            'password_quality.version.uid': 2,
        })

        ok_(acc.is_strong_password_required)
        ok_(acc.password.is_weak)

    def test_is_complication_required(self):
        acc = Account(uid=10).parse({})

        ok_(not acc.password.is_complication_required)

        acc = Account(uid=10).parse({
            'password.encrypted': TEST_PASSWORD_WITH_VERSION,
            'password_quality.quality.uid': 90,
            'password_quality.version.uid': 2,
        })

        acc.password.quality_version = 2
        acc.password.quality = 90
        ok_(not acc.password.is_complication_required)

        acc = Account(uid=10).parse({
            'password.encrypted': TEST_PASSWORD_WITH_VERSION,
            'password_quality.quality.uid': 10,
            'password_quality.version.uid': 2,
        })
        ok_(not acc.password.is_complication_required)

        acc = Account(uid=10).parse({
            'subscriptions': {67: {'sid': 67}},
            'password.encrypted': TEST_PASSWORD_WITH_VERSION,
            'password_quality.quality.uid': 10,
            'password_quality.version.uid': 2,
        })
        ok_(acc.password.is_complication_required)

    def test_is_password_flushed_by_admin(self):
        acc = default_account().parse({
            'password.forced_changing_reason': PASSWORD_CHANGING_REASON_FLUSHED_BY_ADMIN,
            'subscriptions': {8: {'login_rule': 1, 'sid': 8}},
        })
        eq_(acc.password.forced_changing_reason, PASSWORD_CHANGING_REASON_FLUSHED_BY_ADMIN)
        ok_(acc.password.is_changing_required)
        ok_(acc.password.is_password_flushed_by_admin)

        acc = default_account().parse({
            'password.forced_changing_reason': PASSWORD_CHANGING_REASON_HACKED,
            'subscriptions': {8: {'login_rule': 1, 'sid': 8}},
        })
        eq_(acc.password.forced_changing_reason, PASSWORD_CHANGING_REASON_HACKED)
        ok_(acc.password.is_changing_required)
        ok_(not acc.password.is_password_flushed_by_admin)


class TestParsePassword(unittest.TestCase):
    def test_parse_cryptpassword(self):
        acc = Account().parse({
            'uid': 1,
            'password.encrypted': '3:secret',
        })

        eq_(acc.uid, 1)
        eq_(acc.password.is_set, True)
        eq_(acc.password.encoding_version, 3)
        eq_(acc.password.encrypted_password, 'secret')
        eq_(acc.password.serialized_encrypted_password, '3:secret')
        ok_(not acc.password.is_expired)
        ok_(acc.password.is_set_or_promised)

    def test_parse_invalid_password_encrypted(self):
        for value in (
            'abcd',
            '123x:1234',
            ':',
            '::',
            ':x',
            '1:',
        ):
            acc = Account().parse({
                'uid': 1,
                'password.encrypted': value,
            })

            eq_(acc.password.encrypted_password, Undefined)
            eq_(acc.password.encoding_version, Undefined)
            eq_(acc.password.serialized_encrypted_password, Undefined)
            ok_(not acc.password.is_set)
            ok_(not acc.password.is_set_or_promised)

    def test_parse_password_quality(self):
        """Парсинг полей про качество пароля из ЧЯ в модель"""
        acc = Account().parse({
            'uid': 1,
            'password.encrypted': '1:secret',
            'password_quality.quality.uid': 50,
            'password_quality.version.uid': 2,
        })

        eq_(acc.uid, 1)
        eq_(acc.password.quality, 50)
        eq_(acc.password.quality_version, 2)
        ok_(not acc.password.is_expired)

    def test_parse_expired(self):
        """Парсинг статуса актуальности сильного пароля"""
        acc = Account().parse({
            'uid': 1,
            'subscriptions': {67: {'sid': 67}},
            'bruteforce_policy': {'value': 'password_expired'},
        })

        eq_(acc.uid, 1)
        ok_(acc.password.is_expired)

    def test_multiple_parse_expired(self):
        """Парсинг статуса актуальности сильного пароля, повторный вызов
        без bruteforce_policy не приводит к сбросу флага"""
        acc = Account().parse({
            'uid': 1,
            'subscriptions': {67: {'sid': 67}},
            'bruteforce_policy': {'value': 'password_expired'},
        })
        acc = acc.parse({
            'domain': 'domain.com',
        })

        eq_(acc.uid, 1)
        ok_(acc.password.is_expired)

    def test_update_datetime__ok(self):
        acc = Account().parse({'login': 'test'})
        eq_(acc.password.update_datetime, Undefined)

        acc = Account().parse({'login': 'test', 'password.update_datetime': ''})
        eq_(acc.password.update_datetime, Undefined)

        ts = 12345678
        acc = Account().parse({'login': 'test', 'password.update_datetime': str(ts)})
        eq_(acc.password.update_datetime, datetime.fromtimestamp(ts))

    def test_password_forced_changing_time__ok(self):
        acc = Account().parse({'login': 'test'})
        eq_(acc.password.forced_changing_time, Undefined)

        acc = Account().parse({'login': 'test', 'password.forced_changing_time': ''})
        eq_(acc.password.forced_changing_time, Undefined)

        ts = 12345678
        acc = Account().parse({'login': 'test', 'password.forced_changing_time': str(ts)})
        eq_(acc.password.forced_changing_time, datetime.fromtimestamp(ts))

    def test_password_pwn_forced_changing_suspended_at__ok(self):
        acc = Account().parse({'login': 'test'})
        eq_(acc.password.pwn_forced_changing_suspended_at, Undefined)

        ts = 12345678
        acc = Account().parse({'login': 'test', 'password.pwn_forced_changing_suspended_at': ts})
        eq_(acc.password.pwn_forced_changing_suspended_at, datetime.fromtimestamp(ts))


@with_settings_hosts(BLACKBOX_URL='http://localhost/')
class CheckPasswordEqualsHashTestCase(unittest.TestCase):
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

    def test_with_empty_hash(self):
        ok_(not check_password_equals_hash('pass', Undefined, 123))

    def test_with_serialized_hash_value(self):
        serialized_hash = b'3:16d7a4fca7442dda3ad93c9a726597e4'
        self.fake_blackbox.set_blackbox_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(hashes={base64.b64encode(serialized_hash).decode(): True}),
        )
        ok_(check_password_equals_hash('test1234', serialized_hash.decode(), 123))
        request = self.fake_blackbox.requests[0]
        request.assert_post_data_contains(
            {
                'method': 'test_pwd_hashes',
                'password': 'test1234',
                'hashes': base64.b64encode(serialized_hash).decode(),
                'uid': 123,
            },
        )


def test_build_password_subwords_normal_account_have_login_in_subwords():
    acc = default_account(alias='test')

    actual = build_password_subwords(acc)
    eq_(actual, ['test'])


def test_build_password_subwords_hosted_account_have_login_and_email_in_subwords():
    acc = default_account(alias='test').parse({'domain': 'domain.com'})

    actual = sorted(build_password_subwords(acc))
    eq_(actual, ['test', 'test@domain.com'])


def test_build_password_subwords_lite_account_have_login_and_email_in_subwords():
    lite_acc = default_account(alias='test@domain.com', alias_type='lite')

    actual = sorted(build_password_subwords(lite_acc))
    eq_(actual, ['test', 'test@domain.com'])


def test_default_encrypted_password():
    value = default_encrypted_password('test', 123, salt='aaaaaaaa')
    version, password_hash = value.split(':')
    eq_(version, '1')
    eq_(password_hash, TEST_MD5_CRYPT_HASH)
