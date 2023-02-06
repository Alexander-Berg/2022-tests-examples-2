# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import unittest

from nose.tools import eq_
from passport.backend.core.builders.blackbox.constants import BLACKBOX_PWDHISTORY_REASON_COMPROMISED
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_pwdhistory_response,
    blackbox_test_pwd_hashes_response,
    FakeBlackbox,
)
from passport.backend.core.builders.shakur.faker.fake_shakur import (
    FakeShakur,
    shakur_check_password_no_postfix,
)
from passport.backend.core.password import policy
from passport.backend.core.test.test_utils import (
    settings_context,
    with_settings,
)
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_error_codes,
    check_raise_error,
)
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.validators import State
from passport.backend.core.validators.password.password import Password
from passport.backend.utils.string import smart_bytes


TEST_COMPROMISED_PASSWORD_SEARCH_DEPTH = 3
TEST_PWNED_PASSWORD = 'foo_pwned'
TEST_WHITELIST_SHAKUR_LOGIN = 'no_shakur'


@with_settings(
    BLACKBOX_URL='http://localhost/',
    BASIC_PASSWORD_POLICY_PWDHISTORY_SEARCH_DEPTH=TEST_COMPROMISED_PASSWORD_SEARCH_DEPTH,
    CHECK_SHAKUR_DURING_PASSWORD_VALIDATION=True,
    SHAKUR_URL='http://localhost/',
    SHAKUR_LIMIT=100,
    SHAKUR_RETRIES=1,
    SHAKUR_TIMEOUT=1,
    SHAKUR_USE_TVM=False,
    IS_SHAKUR_CHECK_DISABLED=False,
    SHAKUR_WHITELIST_LOGIN_MASKS=[TEST_WHITELIST_SHAKUR_LOGIN],
)
class TestPassword(unittest.TestCase):
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
        self.blackbox = FakeBlackbox()
        self.blackbox.start()
        self.shakur = FakeShakur()
        self.shakur.start()
        self.shakur.set_response_value(
            'check_password',
            json.dumps(shakur_check_password_no_postfix(hashlib.sha1(smart_bytes(TEST_PWNED_PASSWORD)).hexdigest())),
        )
        self.state = State(mock_env(user_ip='127.0.0.1'))

    def tearDown(self):
        self.blackbox.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.shakur
        del self.blackbox
        del self.fake_tvm_credentials_manager
        del self.state

    def test_valid_passwords(self):
        valid_passwords = [
            ({'password': None},
             {'password': None}),
            ({'password': 'foobar'},
             {'password': 'foobar', 'quality': 15, 'lt_middle_quality': True}),
            ({'password': 'foobar123'},
             {'password': 'foobar123', 'quality': 49}),
            ({'password': 'abcde' * 51},
             {'password': 'abcde' * 51, 'quality': 100}),
            ({'password': 'foo-bar'},
             {'password': 'foo-bar', 'quality': 63}),
            ({'password': 'foo!@#$%^&*()+_:;.,'},
             {'password': 'foo!@#$%^&*()+_:;.,', 'quality': 100}),
            ({'password': '`"]|}/\\{[=<?>'},
             {'password': '`"]|}/\\{[=<?>', 'quality': 100}),
            ({'password': '-a-zA-Z0-9`!@#$%^&*()_=+\\[\\]{};:"\\|,.<>/?'},
             {'password': '-a-zA-Z0-9`!@#$%^&*()_=+\\[\\]{};:"\\|,.<>/?', 'quality': 100}),
            ({'password': ''.join([chr(x) for x in range(0x21, 0x7e + 1) if chr(x) not in '\'~'])},
             {'password': '!"#$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}', 'quality': 100}),
            ({'login': 'login', 'password': 'foobar'},
             {'login': 'login', 'password': 'foobar', 'quality': 15, 'lt_middle_quality': True}),
            ({'login': 'login', 'password': 'St40nGPasswd', 'policy': 'strong'},
             {'login': 'login', 'password': 'St40nGPasswd', 'policy': 'strong', 'quality': 100}),
            ({'login': 'login@domain.com', 'password': 'foobar'},
             {'login': 'login@domain.com', 'password': 'foobar', 'quality': 15, 'lt_middle_quality': True}),
            ({'login': 'login', 'password': 'login@domain.com'},
             {'login': 'login', 'password': 'login@domain.com', 'quality': 42}),
            ({'login': 'login', 'password': 'login@yandex.ru', 'emails': ['login@foo.bar']},
             {'login': 'login', 'password': 'login@yandex.ru', 'quality': 47, 'emails': ['login@foo.bar']}),
            ({'login': 'login@domain.com', 'password': 'login@domain-com'},
             {'login': 'login@domain.com', 'password': 'login@domain-com', 'quality': 42}),
            # Пароль не очищается от "запрещенных комбинаций символов" при сравнении с login
            ({'login': 'login@domain.com', 'password': 'login@domain..com'},
             {'login': 'login@domain.com', 'password': 'login@domain..com', 'quality': 45}),
            ({'login': 'a-login@domain.com', 'password': 'a--login@domain.com'},
             {'login': 'a-login@domain.com', 'password': 'a--login@domain.com', 'quality': 100}),
            ({'login': None, 'password': 'foobar'},
             {'login': None, 'password': 'foobar', 'quality': 15, 'lt_middle_quality': True}),
            ({'login': u'кириллица', 'password': 'St40nGPasswd', 'policy': 'strong'},
             {'login': u'кириллица', 'password': 'St40nGPasswd', 'policy': 'strong', 'quality': 100}),
            ({'password': 'foobar', 'policy': 'unknown-as-basic'},
             {'password': 'foobar', 'policy': 'unknown-as-basic', 'quality': 15, 'lt_middle_quality': True}),
            ({'password': 'foobar', 'policy': None},
             {'password': 'foobar', 'policy': None, 'quality': 15, 'lt_middle_quality': True}),
            ({'password': '78qa22!#', 'phone_number': PhoneNumber.parse('+380967730479'), 'country': 'RU'},
             {'password': '78qa22!#', 'phone_number': PhoneNumber.parse('+380967730479'), 'country': 'RU', 'quality': 96}),
            ({'password': '+7(926)-123-45-67a', 'phone_number': PhoneNumber.parse('+79261234567'), 'country': 'RU'},
             {'password': '+7(926)-123-45-67a', 'phone_number': PhoneNumber.parse('+79261234567'), 'country': 'RU', 'quality': 100}),
            ({'password': '+7(926)-123-45-67o*o', 'phone_number': PhoneNumber.parse('+79261234567'), 'country': 'RU'},
             {'password': '+7(926)-123-45-67o*o', 'phone_number': PhoneNumber.parse('+79261234567'), 'country': 'RU', 'quality': 100}),
            ({'password': '+7(926)-123-x45-67', 'phone_number': PhoneNumber.parse('+79261234567'), 'country': 'RU'},
             {'password': '+7(926)-123-x45-67', 'phone_number': PhoneNumber.parse('+79261234567'), 'country': 'RU', 'quality': 100}),
            ({'password': '926123-45-99', 'phone_number': PhoneNumber.parse('+79261234567'), 'country': 'RU'},
             {'password': '926123-45-99', 'phone_number': PhoneNumber.parse('+79261234567'), 'country': 'RU', 'quality': 72}),
            # Слитый пароль, но логин входит с список исключений
            ({'login': TEST_WHITELIST_SHAKUR_LOGIN, 'password': TEST_PWNED_PASSWORD},
             {'login': TEST_WHITELIST_SHAKUR_LOGIN, 'password': TEST_PWNED_PASSWORD, 'quality': 100}),
        ]

        for valid_password, expected_password in valid_passwords:
            check_equality(Password(), (valid_password, expected_password))

    def test_invalid_passwords_simple(self):
        invalid_passwords = [
            {'password': ''},
            {'password': 'foobar∞'},
            {'password': 'foo–bar'},
            {'password': 'short'},
            {'password': 'long' * 100},
            {'login': 'login', 'password': 'foobar', 'policy': 'strong'},
            {'login': 'foobar', 'password': 'foobar'},
            {'login': 'FooBar', 'password': 'foobar'},
            {'login': 'sim-ple-reg', 'password': 'sim.ple-reg'},
            # Проверка совпадения с нормализованным login'ом без учета доменной части
            {'login': 'super.macho@domain.com', 'password': 'super-macho'},
            {'login': 'super-macho@domain.com', 'password': 'super.macho'},
            # Проверка совпадения с нормализованным email
            {'login': 'super-macho@okna.ru', 'password': 'super-macho@okna.ru'},
            {'login': 'super.macho@okna.ru', 'password': 'SUPER.macho@OKNA.RU'},
            # Проверка совпадения с переданным email
            {'password': 'foo@bar.com', 'login': 'foo', 'emails': ['foo@bar.com']},
            # Контрольный пример
            {'login': 'a.b-caaaa00@d.e-f', 'password': 'a.b-caaaa00@d.e-f'},
            {'password': u'username@окна.рф'},
            {'password': '      '},
            # Слитый пароль
            {'password': TEST_PWNED_PASSWORD},
        ]

        for invalid_password in invalid_passwords:
            check_raise_error(Password(), invalid_password)

    def test_error_codes_for_invalid_password(self):
        foo_hash = '1:$1$il.3rA5/$IpaMws5kGWYpbT7A3HC/3.'
        foobar_hash = '1:$1$nbPtTWDF$VJSRhPcGQ8TBzyzSFS83O1'
        self.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(
                {
                    base64.b64encode(foo_hash.encode('utf8')).decode('utf8'): True,
                    base64.b64encode(foobar_hash.encode('utf8')).decode('utf8'): True
                },
            ),
        )
        params = [
            ({'password': 'foo'}, {'password': ['tooShort']}),
            ({'password': 'foo£'}, {'password': ['tooShort', 'prohibitedSymbols']}),
            ({'password': '1foobar£' + 'a' * 300}, {'password': ['tooLong', 'prohibitedSymbols']}),
            ({'password': 'a' * 256}, {'password': ['tooLong']}),
            ({'password': 'foobar', 'login': 'foobar'}, {'password': ['likeLogin']}),
            ({'password': 'foobar', 'login': 'foobar@yandex.ru'}, {'password': ['likeLogin']}),
            ({'password': 'foobar', 'login': 'foobar@narod.ru'}, {'password': ['likeLogin']}),
            ({'password': 'foo@bar.com', 'login': 'foo@bar.com'}, {'password': ['likeLogin']}),
            ({'password': 'Foo.Bar@the.BAZ.com', 'login': 'foo-bar@the.baz.com'}, {'password': ['likeLogin']}),
            ({'password': 'foo@bar.com', 'login': 'foo-bar', 'emails': ['foo@bar.com']}, {'password': ['likeLogin']}),
            ({'password': 'foo', 'old_password_hash': foo_hash},
             {'password': ['tooShort']}),
            ({'password': 'foobar', 'old_password_hash': foobar_hash},
             {'password': ['likeOldPassword']}),
            ({'password': 'foobar', 'old_password_hash': 'c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2'},
             {'password': ['likeOldPassword']}),
            ({'password': u'русский+текст', 'old_password_hash': '1:$1$7vM69rLF$v5uGWB4tI0dxq7xknCARe0'},
             {'password': ['prohibitedSymbols']}),
            ({'password': u'+79261234567', 'phone_number': '+7 926 123 45 67'},
             {'password': ['likePhoneNumber']}),
            ({'password': u'+7(926)-123-45-67', 'phone_number': '+79261234567'},
             {'password': ['likePhoneNumber']}),
            ({'password': u'8(926)-123-45-67', 'phone_number': '+79261234567', 'country': 'RU'},
             {'password': ['likePhoneNumber']}),
            ({'password': u'7926123-45-67', 'phone_number': '+79261234567', 'country': 'RU'},
             {'password': ['likePhoneNumber']}),
            ({'password': u'926123-45-67', 'phone_number': '+79261234567', 'country': 'RU'},
             {'password': ['likePhoneNumber']}),
            ({'password': u'89261234567', 'phone_number': '+79261234567', 'country': 'TR'},
             {'password': ['likePhoneNumber']}),
            ({'password': u'foo', 'phone_number': '+79261234567', 'country': 'RU'},
             {'password': ['tooShort']}),
            ({'password': TEST_PWNED_PASSWORD, 'phone_number': '+79261234567', 'country': 'RU'},
             {'password': ['weak']}),
        ]

        for password_params, expected_codes in params:
            check_error_codes(Password(), password_params, expected_codes)

    def test_password_constructor_custom_args(self):
        p = Password(password_field='foo', login_field='bar', policy_name_field='zar')
        eq_(p._password_field, 'foo')
        eq_(p._login_field, 'bar')
        eq_(p._policy_name_field, 'zar')

    def test_password_constructor_form_args(self):
        p = Password()
        eq_(p._password_field, 'password')
        eq_(p._login_field, 'login')
        eq_(p._policy_name_field, 'policy')

    def test_password_policy_changing(self):
        p = Password()

        with settings_context(
            BASIC_PASSWORD_POLICY_MIN_QUALITY=0,
            BASIC_PASSWORD_POLICY_MIDDLE_QUALITY=0,
            CHECK_SHAKUR_DURING_PASSWORD_VALIDATION=True,
            SHAKUR_URL='http://localhost/',
            SHAKUR_LIMIT=100,
            SHAKUR_RETRIES=1,
            SHAKUR_TIMEOUT=1,
            SHAKUR_USE_TVM=False,
            IS_SHAKUR_CHECK_DISABLED=False,
            SHAKUR_WHITELIST_LOGIN_MASKS=[],
        ):
            check_equality(p, ({'password': 'foobar'}, {'password': 'foobar', 'quality': 15}))

        with settings_context(
            BASIC_PASSWORD_POLICY_MIN_QUALITY=10,
            BASIC_PASSWORD_POLICY_MIDDLE_QUALITY=0,
            CHECK_SHAKUR_DURING_PASSWORD_VALIDATION=True,
            SHAKUR_URL='http://localhost/',
            SHAKUR_LIMIT=100,
            SHAKUR_RETRIES=1,
            SHAKUR_TIMEOUT=1,
            SHAKUR_USE_TVM=False,
            IS_SHAKUR_CHECK_DISABLED=False,
            SHAKUR_WHITELIST_LOGIN_MASKS=[],
        ):
            check_equality(p, ({'password': 'foobar'}, {'password': 'foobar', 'quality': 15}))

        with settings_context(
            BASIC_PASSWORD_POLICY_MIN_QUALITY=10,
            BASIC_PASSWORD_POLICY_MIDDLE_QUALITY=30,
            CHECK_SHAKUR_DURING_PASSWORD_VALIDATION=True,
            SHAKUR_URL='http://localhost/',
            SHAKUR_LIMIT=100,
            SHAKUR_RETRIES=1,
            SHAKUR_TIMEOUT=1,
            SHAKUR_USE_TVM=False,
            IS_SHAKUR_CHECK_DISABLED=False,
            SHAKUR_WHITELIST_LOGIN_MASKS=[],
        ):
            check_equality(p, ({'password': 'foobar'}, {'password': 'foobar', 'quality': 15, 'lt_middle_quality': True}))

        with settings_context(
            BASIC_PASSWORD_POLICY_MIN_QUALITY=20,
            BASIC_PASSWORD_POLICY_MIDDLE_QUALITY=30,
            CHECK_SHAKUR_DURING_PASSWORD_VALIDATION=True,
            SHAKUR_WHITELIST_LOGIN_MASKS=[],
        ):
            check_raise_error(p, {'password': 'foobar'})

    def test_password_validation_state(self):
        p = Password()
        p.to_python({'login': 'bla', 'password': 'foobar'}, self.state),
        eq_(
            self.state.password_quality,
            {
                'is_additional_word': False,
                'classes_number': 1,
                'additional_subwords_number': 0,
                'real_quality': 15,
                'bonus': 5,
                'quality': 15,
                'unique_chars_number': 5,
                'chars_number_by_class': {'lower': 6},
                'class_switching_number': 0,
                'penalty': 2,
                'grade': 1,
                'length': 6,
                'is_sequence': False,
                'sequences': [],
                'is_word': False,
                'sequences_number': 0,
                'unique_chars': set(['a', 'r', 'b', 'o', 'f']),
                'additional_subwords': {'bla'},
            },
        )

    def test_password_found_in_history_for_strong_policy(self):
        """Требование сильного пароля, пароль найден в истории"""
        self.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=True),
        )
        check_error_codes(
            Password(required_check_password_history=True),
            {'password': 'fooooobar2', 'policy': 'strong', 'uid': '1'},
            {'password': ['foundInHistory']},
        )
        self.blackbox.requests[0].assert_post_data_equals({
            'method': 'pwdhistory',
            'password': 'fooooobar2',
            'uid': '1',
            'depth': policy.strong().search_depth,
            'format': 'json',
        })

    def test_password_found_in_history_for_password_changing_required(self):
        """Требование смены пароля, скомпрометированный пароль найден в истории"""
        self.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=True),
        )
        check_error_codes(
            Password(required_check_password_history=True),
            {'password': 'fooooobar2', 'policy': 'basic', 'uid': '1'},
            {'password': ['foundInHistory']},
            state=self.state,
        )
        self.blackbox.requests[0].assert_post_data_equals({
            'method': 'pwdhistory',
            'password': 'fooooobar2',
            'uid': '1',
            'depth': TEST_COMPROMISED_PASSWORD_SEARCH_DEPTH,
            'reason': str(BLACKBOX_PWDHISTORY_REASON_COMPROMISED),
            'format': 'json',
        })

    def test_password_not_searched_in_history_by_default(self):
        """По умолчанию не ищем пароль в истории"""
        password = {'password': 'fooooobar2', 'policy': 'strong', 'uid': '1'}
        check_equality(
            Password(),
            (password, dict(password, quality=90)),
        )
        eq_(len(self.blackbox.requests), 0)

    def test_password_not_searched_in_history_if_equals_to_old_password(self):
        password_hash = '1:$1$H8z/ARIX$BNKjgwx9LtmUpIx5qBUZ.0'
        self.blackbox.set_blackbox_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(hashes={
                base64.b64encode(password_hash.encode('utf8')).decode('utf8'): True,
            }),
        )
        check_error_codes(
            Password(),
            {
                'password': 'foobarfoobar',
                'old_password_hash': password_hash,
                'policy': 'strong',
                'uid': '1',
            },
            {'password': ['likeOldPassword']},
            state=self.state,
        )
        eq_(len(self.blackbox.requests), 1)
        request = self.blackbox.requests[0]
        request.assert_post_data_contains(
            {
                'method': 'test_pwd_hashes',
                'password': 'foobarfoobar',
                'hashes': base64.b64encode(password_hash.encode('utf8')).decode('utf8'),
                'uid': '1',
            },
        )
