# -*- coding: utf-8 -*-
import unittest

import mock
from passport.backend.api.test.utils import check_bundle_form
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CYRILLIC_DOMAIN,
    TEST_CYRILLIC_DOMAIN_IDNA,
)
from passport.backend.api.views.bundle.register import forms
from passport.backend.core import validators
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
    FakeBlackbox,
)
from passport.backend.core.conf import settings
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
    PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON,
)
from passport.backend.core.services import Service
from passport.backend.core.test.test_utils.mock_objects import (
    mock_env,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.birthday import Birthday
from passport.backend.core.types.display_name import DisplayName
from passport.backend.core.types.gender import Gender
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.validators import YandexTeamLogin
from passport.backend.utils.common import merge_dicts
import pytz


TEST_MD5_CRYPT_HASH = '$1$aaaaaaaa$lWxWtPmiNjS/cwJnGm6fe0'
TEST_MD5_RAW_HASH = 'ab' * 16
TEST_MAILISH_ID = 'ORSXg5BNNvqws3djoNUC22LE'
TEST_MAILISH_LOWER_ID = TEST_MAILISH_ID.lower()


def build_params_builder(default_valid_params):
    def params_builder(params, expected):
        return (merge_dicts(default_valid_params, params), expected)
    return params_builder


@with_settings(
    BLACKBOX_URL='localhost',
    BASIC_PASSWORD_POLICY_MIN_QUALITY=10,
    ALT_DOMAINS={
        'galatasaray.net': 2,
        'auto.ru': 1120001,
    },
)
class TestRegisterForms(unittest.TestCase):
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

        self.track_id = '0a' * settings.TRACK_RANDOM_BYTES_COUNT + '00'
        self.blackbox = FakeBlackbox()
        self.grants = FakeGrants()
        self.blackbox.start()
        self.grants.start()
        self.grants.set_grants_return_value(mock_grants())
        self.validators_patch = mock.patch(
            'passport.backend.core.validators.validators.ALT_DOMAIN_LOGIN_VALIDATORS',
            {'auto.ru': YandexTeamLogin},
        )
        self.validators_patch.start()

        self.state = validators.State(mock_env(user_ip='127.0.0.1'))

    def tearDown(self):
        self.blackbox.stop()
        self.grants.stop()
        self.validators_patch.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.blackbox
        del self.grants
        del self.validators_patch
        del self.state
        del self.fake_tvm_credentials_manager

    def test_account_register_phone_and_aliasify(self):
        DEFAULT_VALID_PARAMS = {
            'birthday': '1950-05-01',
            'consumer': 'dev',
            'country': 'ru',
            'eula_accepted': 'True',
            'gender': 'm',
            'firstname': 'testfirstname',
            'lastname': 'testlastname',
            'language': 'ru',
            'login': 'test',
            'password': 'testpasswd',
            'timezone': 'Europe/Moscow',
            'track_id': self.track_id,
        }

        build_params = build_params_builder(DEFAULT_VALID_PARAMS)

        invalid_params = [
            # missing
            ({'consumer': 'dev'},
             ['country.empty', 'eula_accepted.empty',
              'firstname.empty', 'language.empty', 'lastname.empty',
              'login.empty', 'password.empty', 'track_id.empty']),
            # empty
            ({'consumer': 'dev', 'track_id': self.track_id, 'country': '',
              'login': '', 'password': '', 'firstname': '', 'lastname': '',
              'language': '', 'eula_accepted': ''},
             ['country.empty', 'eula_accepted.empty',
              'firstname.empty', 'language.empty', 'lastname.empty',
              'login.empty', 'password.empty']),
            # consumer
            build_params({'consumer': 'bad consumer'},
                         ['consumer.invalid']),
            # birthday
            build_params({'birthday': 'birthday'},
                         ['birthday.invalid']),
            # country
            build_params({'country': 'country'},
                         ['country.invalid']),
            # eula_accepted
            build_params({'eula_accepted': 'noooooo'},
                         ['eula_accepted.invalid']),
            # eula_accepted empty
            build_params({'eula_accepted': ' '},
                         ['eula_accepted.empty']),
            # gender
            build_params({'gender': 'gender'},
                         ['gender.invalid']),
            # empty firstname
            build_params({'firstname': ''},
                         ['firstname.empty']),
            # empty lastname
            build_params({'lastname': ''},
                         ['lastname.empty']),
            # empty firstname 2
            build_params({'firstname': '  '},
                         ['firstname.empty']),
            # empty lastname 2
            build_params({'lastname': '  '},
                         ['lastname.empty']),
            # language
            build_params({'language': 'language'},
                         ['language.invalid']),
            # login
            build_params({'login': '  '},
                         ['login.empty']),
            # timezone
            build_params({'timezone': 'timezone'},
                         ['timezone.invalid']),
            # track_id
            build_params({'track_id': '0'},
                         ['track_id.invalid']),
        ]

        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )

        valid_params = [
            # just default
            build_params(
                {},
                {
                    'birthday': Birthday.parse('1950-05-01'),
                    'consumer': 'dev',
                    'country': 'ru',
                    'eula_accepted': True,
                    'gender': Gender.Male,
                    'firstname': 'testfirstname',
                    'lastname': 'testlastname',
                    'language': 'ru',
                    'login': 'test',
                    'password': 'testpasswd',
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'track_id': self.track_id,
                    'force_clean_web': False,
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_bundle_form(forms.AccountRegisterRequireConfirmedPhoneAndAliasify(), invalid_params, valid_params, state)

    def test_account_register_directory_form(self):
        DEFAULT_VALID_PARAMS = {
            'firstname': 'Firstname',
            'lastname': 'Lastname',
            'domain': 'sigur.org',
            'login': '---ros..',
            'password': 'testP@ssw0rd',
            'eula_accepted': 't',
        }
        EXPECTED_VALID_PARAMS = dict(
            DEFAULT_VALID_PARAMS,
            eula_accepted=True,
            organization=None,
            force_clean_web=False,
        )

        def build_params(test_params, expected):
            if test_params is None:
                return {}, expected
            return (
                merge_dicts(
                    DEFAULT_VALID_PARAMS,
                    test_params,
                ),
                expected,
            )

        empty_response = [
            'firstname.empty',
            'lastname.empty',
            'domain.empty',
            'login.empty',
            'password.empty',
            'eula_accepted.empty',
        ]
        invalid_params = [
            # отсутствует поле
            (
                None,
                empty_response,
            ),
            # пустое поле
            (
                {
                    'firstname': '  ',
                    'lastname': '  ',
                    'domain': '',
                    'login': '  ',
                    'password': '',
                    'eula_accepted': '',
                },
                empty_response,
            ),
            # невалидный домен
            (
                {'domain': 'a_b_c_d_e'},
                ['domain.invalid'],
            ),
            # невалидный логин
            (
                {'login': u'#' * 50},
                [
                    'login.long',
                    'login.prohibitedsymbols',
                ],
            ),
            # невалидное поле eula_accepted
            (
                {'eula_accepted': 'F a lse'},
                ['eula_accepted.invalid'],
            ),

        ]
        valid_params = [
            # default valid values
            (
                {},
                EXPECTED_VALID_PARAMS,
            ),
            # юникодный домен
            (
                {'domain': u'домен.рф'},
                {'domain': u'домен.рф'},
            ),
            # пуникодный домен
            (
                {'domain': u'xn--80acjdh5bchf2j.org'},
                {'domain': u'розапобеды.org'},
            ),
            # юникодный пароль
            (
                {'password': u'дерП@р0л'},
                {'password': u'дерП@р0л'},
            ),
            # удаление пробелов у логина
            (
                {'login': u'    1'},
                {'login': u'1'},
            ),
            # указано имя организации
            (
                {'organization': u'Министерство Правды'},
                {'organization': u'Министерство Правды'},
            ),
        ]
        state = validators.State(mock_env(user_ip='127.0.0.1'))

        invalid_params = [build_params(
            params,
            expected_params,
        ) for params, expected_params in invalid_params]

        valid_params = [build_params(
            params,
            merge_dicts(
                EXPECTED_VALID_PARAMS,
                expected_params,
            ),
        ) for params, expected_params in valid_params]

        check_bundle_form(
            forms.AccountRegisterDirectoryForm(),
            invalid_params,
            valid_params,
            state,
        )

    def test_account_register_by_middleman(self):
        DEFAULT_VALID_PARAMS = {
            'firstname': 'testfirstname',
            'lastname': 'testlastname',
            'login': 'test',
            'password': 'testpasswd',
            'language': 'ru',
            'country': 'ru',
        }

        build_params = build_params_builder(DEFAULT_VALID_PARAMS)

        invalid_params = [
            # missing
            (
                {'consumer': 'dev'},
                [
                    'country.empty', 'language.empty',
                    'login.empty', 'password.empty',
                ],
            ),
            # empty
            (
                {'login': '', 'password': '', 'firstname': '', 'lastname': '', 'country': '', 'language': ''},
                [
                    'country.empty', 'language.empty',
                    'login.empty', 'password.empty',
                ],
            ),
            # empty login
            build_params({'login': ''}, ['login.empty']),
            build_params({'login': '  '}, ['login.empty']),
            # empty country
            build_params({'country': ''}, ['country.empty']),
            # empty language
            build_params({'language': ''}, ['language.empty']),
        ]

        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )

        valid_params = [
            # missing
            (
                {
                    'login': 'test',
                    'password': 'testpasswd',
                    'language': 'ru',
                    'country': 'ru',
                },
                {
                    'firstname': None,
                    'lastname': None,
                    'login': 'test',
                    'password': 'testpasswd',
                    'language': 'ru',
                    'country': 'ru',
                    'force_clean_web': False,
                },
            ),
            # empty firstname
            build_params(
                {
                    'firstname': '',
                },
                {
                    'firstname': None,
                    'lastname': 'testlastname',
                    'login': 'test',
                    'password': 'testpasswd',
                    'language': 'ru',
                    'country': 'ru',
                    'force_clean_web': False,
                },
            ),
            # empty lastname
            build_params(
                {
                    'lastname': '',
                },
                {
                    'firstname': 'testfirstname',
                    'lastname': None,
                    'login': 'test',
                    'password': 'testpasswd',
                    'language': 'ru',
                    'country': 'ru',
                    'force_clean_web': False,
                },
            ),
            # empty firstname 2
            build_params(
                {
                    'firstname': '  ',
                },
                {
                    'firstname': None,
                    'lastname': 'testlastname',
                    'login': 'test',
                    'password': 'testpasswd',
                    'language': 'ru',
                    'country': 'ru',
                    'force_clean_web': False,
                },
            ),
            # empty lastname 2
            build_params(
                {
                    'lastname': '  ',
                },
                {
                    'firstname': 'testfirstname',
                    'lastname': None,
                    'login': 'test',
                    'password': 'testpasswd',
                    'language': 'ru',
                    'country': 'ru',
                    'force_clean_web': False,
                },
            ),
            # just default
            build_params(
                {},
                {
                    'firstname': 'testfirstname',
                    'lastname': 'testlastname',
                    'login': 'test',
                    'password': 'testpasswd',
                    'language': 'ru',
                    'country': 'ru',
                    'force_clean_web': False,
                },
            ),
            build_params(
                {
                    'firstname': ' test  first  name ',
                    'lastname': ' test  last  name ',
                    'login': ' test ',
                },
                {
                    'firstname': 'test first name',
                    'lastname': 'test last name',
                    'login': 'test',
                    'password': 'testpasswd',
                    'language': 'ru',
                    'country': 'ru',
                    'force_clean_web': False,
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_bundle_form(forms.AccountRegisterByMiddlemanForm(), invalid_params, valid_params, state)

    def test_register_with_hint(self):
        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )

        DEFAULT_PARAMS = {
            'validation_method': 'captcha',
            'login': 'test',
            'password': 'testpasswd',
            'firstname': 'test first name',
            'lastname': 'test last name',
            'hint_question': 'ping',
            'hint_answer': 'pong',
            'language': 'ru',
            'country': 'ru',
            'gender': 'm',
            'birthday': '2000-01-01',
            'timezone': 'Europe/Moscow',
            'eula_accepted': '1',
        }

        invalid_params = [
            (
                {},
                [
                    'validation_method.empty',
                    'login.empty',
                    'password.empty',
                    'firstname.empty',
                    'lastname.empty',
                    'hint_answer.empty',
                    'language.empty',
                    'country.empty',
                    'eula_accepted.empty',
                ],
            ),
            (
                {
                    'validation_method': '',
                    'login': '',
                    'password': '',
                    'firstname': '',
                    'lastname': '',
                    'hint_question': '',
                    'hint_answer': '',
                    'language': '',
                    'country': '',
                    'eula_accepted': '',
                },
                [
                    'validation_method.empty',
                    'login.empty',
                    'password.empty',
                    'hint_question.empty',
                    'hint_answer.empty',
                    'language.empty',
                    'country.empty',
                    'eula_accepted.empty',
                ],
            ),
            (
                merge_dicts(DEFAULT_PARAMS, {
                    'validation_method': 'bad-value',
                }),
                ['validation_method.invalid'],
            ),
            (
                merge_dicts(DEFAULT_PARAMS, {
                    'hint_question_id': '',
                    'hint_question': '',
                }),
                ['hint_question_id.empty', 'hint_question.empty'],
            ),
            (
                merge_dicts(DEFAULT_PARAMS, {
                    'hint_question_id': '1',
                }),
                ['form.invalid'],
            ),
        ]

        valid_params = [
            (
                DEFAULT_PARAMS.copy(),
                {
                    'validation_method': 'captcha',
                    'login': 'test',
                    'password': 'testpasswd',
                    'firstname': 'test first name',
                    'lastname': 'test last name',
                    'hint_question': 'ping',
                    'hint_question_id': None,
                    'hint_answer': 'pong',
                    'language': 'ru',
                    'country': 'ru',
                    'gender': 1,
                    'birthday': Birthday(2000, 1, 1),
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'eula_accepted': True,
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_bundle_form(forms.AccountRegisterWithHintForm(), invalid_params, valid_params, state)

    def test_register_alternative_easy(self):
        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )

        DEFAULT_PARAMS = {
            'validation_method': 'phone',
            'login': 'test',
            'password': 'testpasswd',
            'language': 'ru',
            'country': 'ru',
            'gender': 'm',
            'birthday': '2000-01-01',
            'timezone': 'Europe/Moscow',
            'eula_accepted': '1',
            'phone_number': '79161234567',
        }

        invalid_params = [
            (
                {},
                [
                    'validation_method.empty',
                    'login.empty',
                    'password.empty',
                    'language.empty',
                    'country.empty',
                    'eula_accepted.empty',
                    'phone_number.empty',
                ],
            ),
            (
                merge_dicts(
                    DEFAULT_PARAMS,
                    {
                        'phone_number': '+7960',
                    },
                ),
                ['phone_number.invalid'],
            ),
        ]

        valid_params = [
            (
                DEFAULT_PARAMS.copy(),
                {
                    'validation_method': 'phone',
                    'login': 'test',
                    'password': 'testpasswd',
                    'firstname': None,
                    'lastname': None,
                    'language': 'ru',
                    'country': 'ru',
                    'gender': 1,
                    'birthday': Birthday(2000, 1, 1),
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'phone_number': PhoneNumber.parse('+79161234567'),
                    'eula_accepted': True,
                    'create_phone_alias': False,
                },
            ),
            (
                dict(
                    DEFAULT_PARAMS,
                    create_phone_alias='1',
                ),
                {
                    'validation_method': 'phone',
                    'login': 'test',
                    'password': 'testpasswd',
                    'firstname': None,
                    'lastname': None,
                    'language': 'ru',
                    'country': 'ru',
                    'gender': 1,
                    'birthday': Birthday(2000, 1, 1),
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'phone_number': PhoneNumber.parse('+79161234567'),
                    'eula_accepted': True,
                    'create_phone_alias': True,
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_bundle_form(forms.AccountRegisterEasyForm(), invalid_params, valid_params, state)

    def test_register_intranet(self):
        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                'test': 'free',
                'auto_ru_alias@auto.ru': 'free',
            }),
        )

        invalid_params = [
            (
                {},
                [
                    'login.empty',
                ],
            ),
            (
                {
                    'login': '',
                    'external_email': '',
                    'altdomain_alias': '',
                },
                [
                    'login.empty',
                    'external_email.empty',
                    'altdomain_alias.empty',
                ],
            ),
            (
                {
                    'login': '1test',
                    'external_email': 'bad-email',
                    'is_maillist': '1234',
                    'altdomain_alias': 'xxx@unknown-domain.ru',
                },
                [
                    'external_email.invalid',
                    'is_maillist.invalid',
                    'altdomain_alias.invalid',
                ],
            ),
            (
                {
                    'login': 'test',
                    'altdomain_alias': '-xxx-@auto.ru',
                },
                [
                    'altdomain_alias.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'login': 'test',
                },
                {
                    'login': 'test',
                    'external_email': None,
                    'is_maillist': False,
                    'altdomain_alias': None,
                    'firstname_global': None,
                    'lastname_global': None,
                },
            ),
            (
                {
                    'login': 'test',
                    'external_email': u'рассылка@рассылки.рф',
                    'is_maillist': 'yes',
                    'firstname_global': 'first',
                    'lastname_global': 'last',
                },
                {
                    'login': 'test',
                    'external_email': u'рассылка@рассылки.рф',
                    'is_maillist': True,
                    'altdomain_alias': None,
                    'firstname_global': 'first',
                    'lastname_global': 'last',
                },
            ),
            (
                {
                    'login': 'test',
                    'altdomain_alias': 'Auto_Ru_Alias@AUTO.RU',
                },
                {
                    'login': 'test',
                    'altdomain_alias': 'auto_ru_alias@auto.ru',
                    'external_email': None,
                    'is_maillist': False,
                    'firstname_global': None,
                    'lastname_global': None,
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_bundle_form(forms.AccountRegisterIntranetForm(), invalid_params, valid_params, state)

    def test_register_pdd(self):
        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(
                {
                    'login123@pdd-domain.ru': 'free',
                    u'login123@окна.рф': 'free',
                    'pdd.does.____0.whatever.wants@pdd.com': 'free',
                },
            ),
        )

        DEFAULT_PARAMS = {
            'login': 'login123',
            'domain': 'pdd-domain.ru',
        }

        def default(d):
            return merge_dicts(DEFAULT_PARAMS, d)

        invalid_params = [
            (
                default({
                    'password': 'password',
                    'password_hash': TEST_MD5_CRYPT_HASH,
                }),
                ['form.invalid'],
            ),
            (
                default({
                    'password': 'password',
                    'no_password': 'true',
                }),
                ['form.invalid'],
            ),
            (
                default({
                    'password_hash': TEST_MD5_CRYPT_HASH,
                    'no_password': 'true',
                }),
                ['form.invalid'],
            ),
            (
                default({}),
                ['form.invalid'],
            ),
            (
                {
                    'domain': '123.456',
                },
                [
                    'login.empty',
                ],
            ),
            (
                default({
                    'hint_answer': 'hey',
                }),
                ['form.invalid'],
            ),
            (
                default({
                    'hint_question': 'hey',
                }),
                ['form.invalid'],
            ),
            (
                default({
                    'domain': 'xn--ads.ru',
                }),
                ['domain.invalid'],
            ),
        ]

        VALID_RESPONSE = {
            'login': 'login123',
            'domain': 'pdd-domain.ru',
            'password': None,
            'firstname': None,
            'gender': None,
            'birthday': None,
            'hint_answer': None,
            'hint_question': None,
            'country': None,
            'language': None,
            'is_creating_required': False,
            'is_maillist': False,
            'is_enabled': True,
            'lastname': None,
            'no_password': None,
            'password_hash': None,
            'weak_password': False,
            'with_yambot_alias': False,
            'force_clean_web': False,
        }

        valid_deltas = [
            (
                dict(password='123'),
                dict(password='123'),
            ),
            (
                dict(password_hash=TEST_MD5_CRYPT_HASH),
                dict(password_hash=(PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON, TEST_MD5_CRYPT_HASH)),
            ),
            (
                dict(password_hash=TEST_MD5_RAW_HASH),
                dict(password_hash=(PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON, TEST_MD5_RAW_HASH)),
            ),
            (
                dict(no_password='true'),
                dict(no_password=True),
            ),
            (
                {
                    'password': '123',
                    'weak_password': 'true',
                },
                {
                    'password': '123',
                    'weak_password': True,
                },
            ),
            (
                {
                    'password': '123',
                    'firstname': 'first',
                    'lastname': 'last',
                    'gender': 'm',
                    'birthday': '2000-01-01',
                },
                {
                    'password': '123',
                    'firstname': 'first',
                    'gender': 1,
                    'birthday': Birthday(2000, 1, 1),
                    'lastname': 'last',
                },
            ),
            (
                {
                    'password': '123',
                    'hint_question': 'q',
                    'hint_answer': 'a',
                },
                {
                    'password': '123',
                    'hint_answer': 'a',
                    'hint_question': 'q',
                },
            ),
            (
                {
                    'password': '123',
                    'is_creating_required': 'true',
                    'is_enabled': 'true',
                },
                {
                    'password': '123',
                    'is_creating_required': True,
                    'is_enabled': True,
                },
            ),
            (
                {
                    'password': '123',
                    'is_maillist': 'true',
                },
                {
                    'password': '123',
                    'is_maillist': True,
                },
            ),
            (
                {
                    'password': '123',
                    'language': 'fi',
                    'country': 'us',
                },
                {
                    'password': '123',
                    'language': 'fi',
                    'country': 'us',
                },
            ),
            (
                {
                    'password': '123',
                    'domain': TEST_CYRILLIC_DOMAIN_IDNA,
                },
                {
                    'password': '123',
                    'domain': TEST_CYRILLIC_DOMAIN,
                },
            ),
            (
                {
                    'password': '123',
                    'domain': TEST_CYRILLIC_DOMAIN,
                },
                {
                    'password': '123',
                    'domain': TEST_CYRILLIC_DOMAIN,
                },
            ),
            (
                {
                    'login': 'pdd.does.____0.whatever.wants',
                    'domain': 'pdd.com',
                    'password': '09ad32-/~^%$',
                },
                {
                    'login': 'pdd.does.____0.whatever.wants',
                    'domain': 'pdd.com',
                    'password': '09ad32-/~^%$',
                },
            ),
            (
                {
                    'password': '123',
                    'with_yambot_alias': 'yes',
                },
                {
                    'password': '123',
                    'with_yambot_alias': True,
                },
            ),
        ]

        valid_params = [
            (default(params_delta), merge_dicts(VALID_RESPONSE, response_delta))
            for params_delta, response_delta
            in valid_deltas
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))
        check_bundle_form(
            forms.AccountRegisterPddForm(),
            invalid_params,
            valid_params,
            state,
        )

    def test_base_oauth_form(self):
        invalid_cases = [
            ({}, ['client_id.empty', 'client_secret.empty']),
            (
                {'client_id': '', 'client_secret': ''},
                ['client_id.empty', 'client_secret.empty'],
            ),
        ]

        empty_params = dict.fromkeys([
            'am_version',
            'am_version_name',
            'app_id',
            'app_platform',
            'manufacturer',
            'model',
            'app_version',
            'app_version_name',
            'uuid',
            'deviceid',
            'ifv',
            'device_name',
            'device_id',
            'os_version',
        ])

        valid_cases = [
            (
                {
                    'client_id': 'foo',
                    'client_secret': 'bar',
                },
                merge_dicts(
                    empty_params,
                    {
                        'client_id': 'foo',
                        'client_secret': 'bar',
                    },
                ),
            ),
            (
                {
                    'client_id': 'foo',
                    'client_secret': 'bar',
                    'am_version': 'am-version',
                    'am_version_name': 'am-version',
                    'app_id': 'test-id',
                    'app_platform': 'android',
                    'manufacturer': 'samsung',
                    'model': 'galaxy',
                    'app_version': '1.2.3-4',
                    'app_version_name': '1.2.3-4',
                    'uuid': 'test-uuid',
                    'deviceid': 'test-dev-id',
                    'ifv': 'test-ifv',
                    'device_name': 'test-name',
                    'device_id': 'test-id',
                    'os_version': 'cp/m',
                },
                {
                    'client_id': 'foo',
                    'client_secret': 'bar',
                    'am_version': 'am-version',
                    'am_version_name': 'am-version',
                    'app_id': 'test-id',
                    'app_platform': 'android',
                    'manufacturer': 'samsung',
                    'model': 'galaxy',
                    'app_version': '1.2.3-4',
                    'app_version_name': '1.2.3-4',
                    'uuid': 'test-uuid',
                    'deviceid': 'test-dev-id',
                    'ifv': 'test-ifv',
                    'device_name': 'test-name',
                    'device_id': 'test-id',
                    'os_version': 'cp/m',
                },
            ),
        ]

        check_bundle_form(forms.BaseOAuthForm(), invalid_cases, valid_cases)

    def test_get_or_create_mailish_form(self):
        invalid_cases = [
            (
                {
                    'client_id': 'foo',
                    'client_secret': 'bar',
                },
                ['email.empty', 'mailish_id.empty'],
            ),
            (
                {
                    'client_id': 'foo',
                    'client_secret': 'bar',
                    'email': '',
                    'mailish_id': '',
                },
                ['email.empty', 'mailish_id.empty'],
            ),
            (
                {
                    'client_id': 'foo',
                    'client_secret': 'bar',
                    'email': 'trash',
                    'mailish_id': 'foo',
                },
                ['email.invalid', 'mailish_id.invalid'],
            ),
            (
                {
                    'client_id': 'foo',
                    'client_secret': 'bar',
                    'email': 'admin@yandex.ru',
                    'mailish_id': TEST_MAILISH_ID,
                },
                ['email.native'],
            ),
            (
                {
                    'client_id': 'foo',
                    'client_secret': 'bar',
                    'email': 'admin@gmail.com',
                    'mailish_id': TEST_MAILISH_ID,
                    'task_id': 'hello',
                },
                ['task_id.invalid'],
            ),
        ]

        empty_params = dict.fromkeys([
            'am_version',
            'am_version_name',
            'app_id',
            'app_platform',
            'manufacturer',
            'model',
            'app_version',
            'app_version_name',
            'uuid',
            'deviceid',
            'ifv',
            'device_name',
            'device_id',
            'os_version',
        ])

        valid_cases = [
            (
                {
                    'client_id': 'foo',
                    'client_secret': 'bar',
                    'email': 'admin@gmail.com',
                    'mailish_id': TEST_MAILISH_ID,
                },
                merge_dicts(
                    empty_params,
                    {
                        'client_id': 'foo',
                        'client_secret': 'bar',
                        'email': 'admin@gmail.com',
                        'mailish_id': TEST_MAILISH_LOWER_ID,
                        'task_id': None,
                        'code_verifier': None,
                    },
                ),
            ),
            (
                {
                    'client_id': 'foo',
                    'client_secret': 'bar',
                    'email': 'admin@gmail.com',
                    'mailish_id': TEST_MAILISH_LOWER_ID,
                    'task_id': 'deadbeef',
                    'code_verifier': 'verifier',
                },
                merge_dicts(
                    empty_params,
                    {
                        'client_id': 'foo',
                        'client_secret': 'bar',
                        'email': 'admin@gmail.com',
                        'mailish_id': TEST_MAILISH_LOWER_ID,
                        'task_id': 'deadbeef',
                        'code_verifier': 'verifier',
                    },
                ),
            ),
        ]

        check_bundle_form(forms.GetOrCreateMailishForm(), invalid_cases, valid_cases)

    def test_register_kolonkish(self):
        invalid_cases = [
            (
                {
                    'device_id': '12345',  # len(device_id) должна быть >= 6, чтобы быть валидной
                },
                [
                    'device_id.invalid',
                ],
            ),
            (
                {
                    'device_id': 'a' * 51,  # len(device_id) должна быть <= 50, чтобы быть валидной
                    'device_name': 'a' * 101,  # len(device_name) <= 100
                },
                [
                    'device_id.invalid',
                    'device_name.long',
                ],
            ),
        ]
        valid_cases = [
            (
                {},
                {
                    'display_name': None,
                    'device_id': None,
                    'device_name': None,
                },
            ),
            (
                {
                    'device_id': '   foobar   ',
                    'device_name': '   bar   ',
                },
                {
                    'display_name': None,
                    'device_id': 'foobar',
                    'device_name': 'bar',
                },
            ),
            (
                {
                    'device_id': 'foobar',
                },
                {
                    'display_name': None,
                    'device_id': 'foobar',
                    'device_name': None,
                },
            ),
            (
                {
                    'device_name': 'bar',
                },
                {
                    'display_name': None,
                    'device_id': None,
                    'device_name': 'bar',
                },
            ),
            (
                {
                    'device_id': 'a' * 6,
                    'device_name': '',
                },
                {
                    'display_name': None,
                    'device_id': 'a' * 6,
                    'device_name': None,
                },
            ),
            (
                {
                    'device_id': 'a' * 6,
                    'device_name': 'a',
                },
                {
                    'display_name': None,
                    'device_id': 'a' * 6,
                    'device_name': 'a',
                },
            ),
            (
                {
                    'display_name': 'a',
                    'device_id': 'a' * 50,
                    'device_name': 'a' * 100,
                },
                {
                    'display_name': DisplayName(name='a'),
                    'device_id': 'a' * 50,
                    'device_name': 'a' * 100,
                },
            ),
        ]

        check_bundle_form(forms.AccountRegisterKolonkishForm(), invalid_cases, valid_cases)

    def test_get_or_create_uber_user(self):
        invalid_cases = [
            (
                {},
                ['uber_id.empty'],
            ),
            (
                {
                    'uber_id': ' ',
                },
                ['uber_id.empty'],
            ),
            (
                {
                    'uber_id': 'a' * 41,
                },
                ['uber_id.long'],
            ),
            (
                {
                    'uber_id': 'ф' * 10,
                },
                ['uber_id.invalid'],
            ),
        ]

        empty_params = dict.fromkeys([
            'am_version',
            'am_version_name',
            'app_id',
            'app_platform',
            'manufacturer',
            'model',
            'app_version',
            'app_version_name',
            'uuid',
            'deviceid',
            'ifv',
            'device_name',
            'device_id',
            'os_version',
        ])

        valid_cases = [
            (
                {
                    'uber_id': ' foo ',
                    'client_id': 'bar',
                    'client_secret': 'baz',
                },
                merge_dicts(
                    empty_params,
                    {
                        'uber_id': 'foo',
                    },
                ),
            ),
            (
                {
                    # только строки
                    'uber_id': '123',
                },
                merge_dicts(
                    empty_params,
                    {
                        'uber_id': '123',
                    },
                ),
            ),
            (
                {
                    'uber_id': '!@#$%#^%$*&^--&*GJGJH<',
                },
                merge_dicts(
                    empty_params,
                    {
                        'uber_id': '!@#$%#^%$*&^--&*gjgjh<',
                    },
                ),
            ),
            (
                {
                    'uber_id': 'ABC..ABC--',
                },
                merge_dicts(
                    empty_params,
                    {
                        'uber_id': 'abc--abc--',
                    },
                ),
            ),
        ]
        check_bundle_form(forms.GetOrCreateUberUserForm(), invalid_cases, valid_cases)

    def test_account_create_form(self):
        DEFAULT_VALID_PARAMS = {
            'consumer': 'dev',
            'login': 'test',
            'password': 'testpasswd',
        }

        build_params = build_params_builder(DEFAULT_VALID_PARAMS)

        invalid_params = [
            # missing
            (
                {'consumer': 'dev'},
                [
                    'login.empty',
                ],
            ),
            # empty
            (
                {
                    'login': '',
                    'ignore_stoplist': '',
                    'is_enabled': '',
                    'password': '',
                    'is_creating_required': '',
                    'password_policy': '',
                    'yastaff_login': '',
                    'firstname': '',
                    'lastname': '',
                    'language': '',
                    'country': '',
                    'gender': '',
                    'birthday': '',
                    'timezone': '',
                    'subscriptions': '',
                },
                [
                    'country.empty',
                    'firstname.empty',
                    'ignore_stoplist.empty',
                    'is_creating_required.empty',
                    'is_enabled.empty',
                    'language.empty',
                    'lastname.empty',
                    'login.empty',
                    'subscriptions.empty',
                    'yastaff_login.empty',
                ],
            ),
            # login
            build_params(
                {'login': '  '},
                ['login.empty'],
            ),
            # email
            build_params(
                {
                    'login': 'test',
                    'email': '',
                },
                [
                    'email.empty',
                ],
            ),
            # ignore_stoplist
            build_params(
                {'ignore_stoplist': 'bla'},
                ['ignore_stoplist.invalid'],
            ),
            # is_enabled
            build_params(
                {'is_enabled': 'bla'},
                ['is_enabled.invalid'],
            ),
            # is_creating_required
            build_params(
                {'is_creating_required': 'bla'},
                ['is_creating_required.invalid'],
            ),
            # language
            build_params(
                {'language': 'language'},
                ['language.invalid'],
            ),
            # country
            build_params(
                {'country': 'country'},
                ['country.invalid'],
            ),
            # gender
            build_params(
                {'gender': 'gender'},
                ['gender.invalid'],
            ),
            # birthday
            build_params(
                {'birthday': 'birthday'},
                ['birthday.invalid'],
            ),
            # timezone
            build_params(
                {'timezone': 'timezone'},
                ['timezone.invalid'],
            ),
            # subscriptions
            build_params(
                {'subscriptions': 'service'},
                ['subscriptions.invalid'],
            ),
            build_params(
                {'subscriptions': '100,669'},
                ['subscriptions.invalid'],
            ),
            # email
            build_params(
                {'email': 'test'},
                ['email.invalid'],
            ),
        ]

        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )
        self.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        valid_params = [
            # Проверка значений по-умолчанию
            build_params(
                {},
                {
                    'login': 'test',
                    'password': 'testpasswd',
                    'ignore_stoplist': False,
                    'is_enabled': True,
                    'is_creating_required': False,
                    'language': None,
                    'country': None,
                    'gender': None,
                    'birthday': None,
                    'timezone': None,
                    'firstname': None,
                    'lastname': None,
                    'yastaff_login': None,
                    'subscriptions': None,
                    'email': None,
                    'force_clean_web': False,
                },
            ),
            # Все параметры
            build_params(
                {
                    'ignore_stoplist': '1',
                    'is_enabled': '0',
                    'is_creating_required': '1',
                    'language': 'ru',
                    'country': 'tr',
                    'gender': 'm',
                    'birthday': '1950-05-01',
                    'timezone': 'Europe/Moscow',
                    'firstname': 'firstname',
                    'lastname': 'lastname',
                    'yastaff_login': 'yastaff',
                    'subscriptions': 'lenta,lenta,partner',
                    'track_id': self.track_id,
                    'email': 'test@example.com',
                },
                {
                    'login': 'test',
                    'password': 'testpasswd',
                    'ignore_stoplist': True,
                    'is_enabled': False,
                    'is_creating_required': True,
                    'language': 'ru',
                    'country': 'tr',
                    'gender': Gender.Male,
                    'birthday': Birthday.parse('1950-05-01'),
                    'timezone': pytz.timezone('Europe/Moscow'),
                    'firstname': 'firstname',
                    'lastname': 'lastname',
                    'yastaff_login': 'yastaff',
                    'subscriptions': [Service.by_sid(23), Service.by_sid(24)],
                    'email': 'test@example.com',
                    'force_clean_web': False,
                },
            ),
        ]

        state = validators.State(mock_env(user_ip='127.0.0.1'))

        check_bundle_form(forms.AccountCreateForm(), invalid_params, valid_params, state)

    def test_account_register_lite_submit_form(self):
        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test@test.ru': 'free'}),
        )
        invalid = [
            (
                {},
                ['language.empty'],
            ),
            (
                {'login': 'abc', 'language': 'qwe'},
                ['login.invalid', 'language.invalid'],
            ),
            (
                {'login': 'abc@yandex.ru', 'language': 'ru'},
                ['login.native'],
            ),
        ]
        valid = [
            (
                {
                    'login': 'test@test.ru',
                    'language': 'ru',
                },
                {
                    'login': 'test@test.ru',
                    'language': 'ru',
                },
            ),
            (
                {
                    'login': 'test@test.ru \t',
                    'language': 'ru',
                },
                {
                    'login': 'test@test.ru',
                    'language': 'ru',
                },
            ),
            (
                {
                    'language': 'ru',
                },
                {
                    'login': None,
                    'language': 'ru',
                },
            ),
        ]
        check_bundle_form(forms.AccountRegisterLiteSubmitForm(), invalid, valid)

    def test_account_register_lite_commit_form(self):
        self.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test@test.ru': 'free', 'test@occ.ru': 'occupied'}),
        )

        invalid = [
            (
                {},
                ['eula_accepted.empty'],
            ),
            (
                {
                    'eula_accepted': 'nope',
                    'lastname': '',
                    'login': 'xn--asd@yandex.ru',
                },
                ['eula_accepted.invalid', 'lastname.empty', 'login.invalid'],
            ),
            (
                {
                    'eula_accepted': 'yes',
                    'require_lastname': 'yes',
                },
                ['lastname.empty'],
            ),
            (
                {'eula_accepted': 'yes', 'login': 'test@occ.ru'},
                ['login.notavailable'],
            ),
            (
                {
                    'eula_accepted': 'yes',
                    'require_firstname': '1',
                    'firstname': u'Ваш подарок заберите на www.yandex.ru',
                    'lastname': u'Лучшие товары на lamoda.ru!',
                },
                ['firstname.invalid', 'lastname.invalid'],
            ),
        ]
        valid = [
            (
                {
                    'eula_accepted': 'no',
                    'firstname': 'TestName',
                },
                {
                    'password': None,
                    'eula_accepted': False,
                    'firstname': 'TestName',
                    'lastname': None,
                    'login': None,
                    'country': None,
                    'language': None,
                    'require_lastname': False,
                    'require_firstname': False,
                    'force_clean_web': False,
                    'unsubscribe_from_maillists': False,
                    'origin': None,
                    'app_id': None,
                },
            ),
            (
                {
                    'password': 'test',
                    'eula_accepted': 'yes',
                    'firstname': 'TestName',
                    'lastname': 'TestSurName',
                    'login': 'test@test.ru',
                    'language': 'ru',
                    'country': 'ru',
                    'require_lastname': 'yes',
                    'require_firstname': '1',
                    'unsubscribe_from_maillists': '1',
                    'origin': 'orig',
                    'app_id': 'app-id',
                },
                {
                    'password': 'test',
                    'eula_accepted': True,
                    'firstname': 'TestName',
                    'lastname': 'TestSurName',
                    'login': 'test@test.ru',
                    'country': 'ru',
                    'language': 'ru',
                    'require_lastname': True,
                    'require_firstname': True,
                    'force_clean_web': False,
                    'unsubscribe_from_maillists': True,
                    'origin': 'orig',
                    'app_id': 'app-id',
                },
            ),
        ]
        check_bundle_form(forms.AccountRegisterLiteCommitForm(), invalid, valid)

    def test_account_register_neophonish_form(self):
        invalid = [
            (
                {},
                ['eula_accepted.empty', 'firstname.empty', 'lastname.empty'],
            ),
            (
                {
                    'force_clean_web': 'nope',
                    'firstname': '',
                    'lastname': '',
                    'language': 'ZZZZ',
                    'country': 'XXXX',
                    'eula_accepted': 'yep',
                },
                [
                    'force_clean_web.invalid',
                    'firstname.empty',
                    'lastname.empty',
                    'language.invalid',
                    'country.invalid',
                    'eula_accepted.invalid',
                ],
            ),
            (
                {
                    'eula_accepted': 'yes',
                    'firstname': u'Ваш подарок заберите на www.yandex.ru',
                    'lastname': u'Лучшие товары на lamoda.ru!',
                },
                ['firstname.invalid', 'lastname.invalid'],
            ),
        ]
        valid = [
            (
                {
                    'eula_accepted': 'no',
                    'firstname': 'TestFirstName',
                    'lastname': 'TestLastName',
                },
                {
                    'force_clean_web': False,
                    'firstname': 'TestFirstName',
                    'lastname': 'TestLastName',
                    'language': None,
                    'country': None,
                    'eula_accepted': False,
                    'unsubscribe_from_maillists': False,
                    'origin': None,
                    'app_id': None,
                },
            ),
            (
                {
                    'eula_accepted': 'no',
                    'firstname': 'TestFirstName',
                    'lastname': 'TestLastName',
                    'language': 'en',
                    'country': 'ru',
                    'force_clean_web': 'yes',
                    'unsubscribe_from_maillists': '1',
                    'origin': 'orig',
                    'app_id': 'app-id',
                },
                {
                    'force_clean_web': True,
                    'firstname': 'TestFirstName',
                    'lastname': 'TestLastName',
                    'language': 'en',
                    'country': 'ru',
                    'eula_accepted': False,
                    'unsubscribe_from_maillists': True,
                    'origin': 'orig',
                    'app_id': 'app-id',
                },
            ),
        ]
        with settings_context(
            USE_NEW_SUGGEST_BY_PHONE=False,
        ):
            check_bundle_form(forms.AccountRegisterNeophonishForm(), invalid, valid)

    def test_account_register_neophonish_form_without_fio(self):
        invalid = [
            (
                {},
                ['eula_accepted.empty'],
            ),
            (
                {
                    'force_clean_web': 'nope',
                    'language': 'ZZZZ',
                    'country': 'XXXX',
                    'eula_accepted': 'yep',
                },
                [
                    'force_clean_web.invalid',
                    'language.invalid',
                    'country.invalid',
                    'eula_accepted.invalid',
                ],
            ),
            (
                {
                    'eula_accepted': 'yes',
                    'firstname': u'Ваш подарок заберите на www.yandex.ru',
                    'lastname': u'Лучшие товары на lamoda.ru!',
                },
                ['firstname.invalid', 'lastname.invalid'],
            ),
        ]
        valid = [
            (
                {
                    'eula_accepted': 'no',
                },
                {
                    'force_clean_web': False,
                    'firstname': None,
                    'lastname': None,
                    'language': None,
                    'country': None,
                    'eula_accepted': False,
                    'unsubscribe_from_maillists': False,
                    'origin': None,
                    'app_id': None,
                },
            ),
            (
                {
                    'eula_accepted': 'no',
                    'firstname': 'TestFirstName',
                    'lastname': 'TestLastName',
                    'language': 'en',
                    'country': 'ru',
                    'force_clean_web': 'yes',
                    'unsubscribe_from_maillists': '1',
                    'origin': 'orig',
                    'app_id': 'app-id',
                },
                {
                    'force_clean_web': True,
                    'firstname': 'TestFirstName',
                    'lastname': 'TestLastName',
                    'language': 'en',
                    'country': 'ru',
                    'eula_accepted': False,
                    'unsubscribe_from_maillists': True,
                    'origin': 'orig',
                    'app_id': 'app-id',
                },
            ),
        ]
        with settings_context(
            USE_NEW_SUGGEST_BY_PHONE=True,
        ):
            check_bundle_form(forms.AccountRegisterNeophonishForm(), invalid, valid)


@with_settings(
    PORTAL_LANGUAGES=('ru',),
)
def test_send_registration_comfirmation_code_form():
    valid_tests = [
        (
            {
                'email': 'foo@bar.ru',
                'language': 'ru',
            },
            {
                'email': 'foo@bar.ru',
                'language': 'ru',
            },
        ),
    ]

    invalid_tests = [
        (
            {},
            ['email.empty', 'language.empty'],
        ),
        (
            {
                'email': '',
                'language': '',
            },
            ['email.empty', 'language.empty'],
        ),
        (
            {'email': 'native@yandex.ru',
             'language': 'ru',
             },
            ['email.native'],
        ),
        (
            {'email': 'foo@bar.ru',
             'language': 'en',
             },
            ['language.invalid'],
        ),
    ]

    check_bundle_form(forms.SendRegistrationConfirmationCodeForm(), invalid_tests, valid_tests)
