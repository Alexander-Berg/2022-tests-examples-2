# -*- coding: utf-8 -*-
import copy
from datetime import datetime

from passport.backend.api.test.utils import (
    check_bundle_form as check_form,
    check_jsonschema_form,
)
from passport.backend.api.views.bundle.restore.semi_auto.step_forms import (
    MAX_SOCIAL_ACCOUNTS_COUNT,
    RestoreSemiAutoMultiStepForm,
    STEP_1_PERSONAL_DATA_SCHEMA,
    STEP_1_PERSONAL_DATA_STRICT_SCHEMA,
    STEP_2_RECOVERY_TOOLS_SCHEMA,
    STEP_2_RECOVERY_TOOLS_STRICT_SCHEMA,
    STEP_3_REGISTRATION_DATA_SCHEMA,
    STEP_3_REGISTRATION_DATA_STRICT_SCHEMA,
    STEP_4_USED_SERVICES_SCHEMA,
    STEP_4_USED_SERVICES_STRICT_SCHEMA,
    STEP_5_SERVICES_DATA_SCHEMA,
    STEP_5_SERVICES_DATA_STRICT_SCHEMA,
    STEP_6_FINAL_INFO_SCHEMA,
    STEP_6_FINAL_INFO_STRICT_SCHEMA,
)
from passport.backend.core import validators
from passport.backend.core.conf import settings
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.core.types.file import File
from six import StringIO


@with_settings(
    DISPLAY_LANGUAGES=('ru', 'en'),
)
def test_multi_step_basic_form():
    invalid_params = [
        (
            {},
            ['json_data.empty'],
        ),
        (
            {
                'json_data': '1',
                'language': 'pp',
            },
            [
                'json_data.invalid',
                'language.invalid',
            ],
        ),
        (
            {'json_data': '[]'},  # Проверяем, что пришел JSON-объект
            ['json_data.invalid'],
        ),
    ]

    valid_params = [
        (
            {'json_data': '{"a":[]}'},
            {
                'json_data': {'a': []},
                'language': 'ru',
                'photo_file': None,
            },
        ),
    ]

    check_form(RestoreSemiAutoMultiStepForm(), invalid_params, valid_params, None)


@with_settings(
    RESTORE_SEMI_AUTO_MAX_PHOTO_FILE_BYTES=10,
    DISPLAY_LANGUAGES=('ru', 'en'),
)
def test_multi_step_basic_form_with_file():
    valid_state = validators.State(mock_env())
    valid_photo_file = File(filename='file', stream=StringIO('datadatada'))
    valid_state.files = dict(photo_file=[valid_photo_file])

    invalid_state = validators.State(mock_env())
    invalid_photo_file = File(
        filename='file',
        stream=StringIO('d' * settings.RESTORE_SEMI_AUTO_MAX_PHOTO_FILE_BYTES + ' '),
    )
    invalid_state.files = dict(photo_file=[invalid_photo_file])

    valid_data = {
        'language': u'en',
        'json_data': '{}',
    }
    valid_data_processed = dict(
        valid_data,
        photo_file=valid_photo_file,
        json_data={},
    )
    check_form(
        RestoreSemiAutoMultiStepForm(),
        [],
        [(
            valid_data,
            valid_data_processed,
        )],
        valid_state,
    )
    check_form(
        RestoreSemiAutoMultiStepForm(),
        [(
            valid_data,
            ['photo_file.file_too_large'],
        )],
        [],
        invalid_state,
    )


def test_step_1_personal_data_form():
    invalid_params = [
        (
            {
                'real_reason': '',
                'birthday': '2000-10-100',
                'contact_email': {},
                'firstnames': [],
                'lastnames': None,
                'passwords': 1,
                'password_auth_date': '',
                'eula_accepted': [],
            },
            [
                'real_reason.empty',
                'birthday.invalid',
                'contact_email.invalid',
                'firstnames.invalid',
                'lastnames.invalid',
                'passwords.invalid',
                'password_auth_date.empty',
                'eula_accepted.invalid',
            ],
        ),
        (
            {
                'real_reason': 'new',
                'birthday': '2000-10-10',
                'contact_email': 'email@email.email',
                'firstnames': [1, 'Vasia'],
                'lastnames': ['Pupkin', u'Пупкин', 'TooMuch'],  # слишком много элементов
                'passwords': ['p1', 'p2', 'p2  ', 'p4'],
                'password_auth_date': '1999-10-10',  # год основания Яндекса - 2000
                'eula_accepted': True,
            },
            [
                'firstnames.invalid',
                'lastnames.invalid',
                'passwords.invalid',
                'passwords.duplicate',
                'password_auth_date.tooearly',
                'real_reason.invalid',
            ],
        ),
        (
            {
                'birthday': '2000-10-10',
                'contact_email': u'email@почта.рф',
                'firstnames': [u'Василий', 'Vasia'],
                'lastnames': [u'Пупкин'],
                'passwords': [],
                'password_auth_date': '1999-01-41',
                'eula_accepted': True,
            },
            [
                'passwords.invalid',
                'password_auth_date.invalid',
            ],
        ),
        (
            {
                'real_reason': ' ',
                'birthday': '2000-10-10',
                'contact_email': u'email@почта.рф',
                'firstnames': [u'Василий', 'Vasia'],
                'lastnames': [u'Пупкин'],
                'passwords': ['p'],
                'password_auth_date': '9999-12-31',
                'eula_accepted': True,
            },
            [
                'real_reason.empty',
                'password_auth_date.invalid',
            ],
        ),
    ]
    invalid_params_strict_form = copy.deepcopy(invalid_params) + [
        (
            {},
            [
                'birthday.empty',
                'contact_email.empty',
                'firstnames.empty',
                'lastnames.empty',
                'passwords.empty',
                'password_auth_date.empty',
                'eula_accepted.empty',
            ],
        ),
    ]

    valid_params_strict_form = [
        (
            {
                'real_reason': 'restore',
                'birthday': '2000-10-10',
                'contact_email': u'email@почта.рф',
                'firstnames': [u'Василий', 'Vasia'],
                'lastnames': [u'Пупкин'],
                'passwords': [u'xxxx'],
                'password_auth_date': '2000-00-00',
                'eula_accepted': False,
            },
            {
                'real_reason': 'restore',
                'birthday': '2000-10-10',
                'contact_email': u'email@почта.рф',
                'firstnames': [u'Василий', 'Vasia'],
                'lastnames': [u'Пупкин'],
                'passwords': [u'xxxx'],
                'password_auth_date': datetime(2000, 1, 1),
                'eula_accepted': False,
            },
        ),
        (
            {
                'real_reason': ' killkvko',
                'birthday': '2000-10-10',
                'contact_email': u'email@почта.рф',
                'firstnames': [u'Василий'],
                'lastnames': [u'Пупкин', u'Козлов'],
                'passwords': [u'  xxxx', u'yy   ', u'z'],
                'password_auth_date': '2014-10-10',
                'eula_accepted': True,
            },
            {
                'real_reason': 'killkvko',
                'birthday': '2000-10-10',
                'contact_email': u'email@почта.рф',
                'firstnames': [u'Василий'],
                'lastnames': [u'Пупкин', u'Козлов'],
                'passwords': [u'xxxx', u'yy', u'z'],
                'password_auth_date': datetime(2014, 10, 10),
                'eula_accepted': True,
            },
        ),
    ]
    valid_params = copy.deepcopy(valid_params_strict_form) + [
        (
            {},
            {},
        ),
        (
            {'birthday': '2000-10-10'},
            {'birthday': '2000-10-10'},
        ),
        (
            {'contact_email': u'email@почта.рф'},
            {'contact_email': u'email@почта.рф'},
        ),
        (
            {'firstnames': [u'Василий']},
            {'firstnames': [u'Василий']},
        ),
        (
            {'lastnames': [u'Пупкин', u'Козлов']},
            {'lastnames': [u'Пупкин', u'Козлов']},
        ),
        (
            {'passwords': [u'  xxxx', u'yy   ', u'z']},
            {'passwords': [u'xxxx', u'yy', u'z']},
        ),
        (
            {'password_auth_date': '2014-10-10'},
            {'password_auth_date': datetime(2014, 10, 10)},
        ),
        (
            {'eula_accepted': True},
            {'eula_accepted': True},
        ),
    ]

    check_jsonschema_form(STEP_1_PERSONAL_DATA_STRICT_SCHEMA, invalid_params_strict_form, valid_params_strict_form)
    check_jsonschema_form(STEP_1_PERSONAL_DATA_SCHEMA, invalid_params, valid_params)


def test_step_2_recovery_tools_form():
    invalid_params = [
        (
            {
                'phone_numbers': '',
                'emails': None,
                'question_answer': '',
            },
            [
                'emails.invalid',
                'phone_numbers.invalid',
                'question_answer.invalid',
            ],
        ),
        (
            {
                'phone_numbers': [1, 2, '79151234567', '79151234567'],
                'emails': ['a@b.c.', 'a@b.c.'],
                'question_answer': {},
            },
            [
                'emails.invalid',
                'emails.duplicate',
                'phone_numbers.invalid',
                'phone_numbers.duplicate',
                'question_answer.answer.empty',
                'question_answer.question.empty',
                'question_answer.question_id.empty',
            ],
        ),
        (
            {
                'phone_numbers': [],
                'emails': [],
                'question_answer': {
                    'question': '',
                    'answer': '',
                    'question_id': '',
                },
            },
            [
                'question_answer.answer.empty',
                'question_answer.question.empty',
                'question_answer.question_id.invalid',
            ],
        ),
        (
            {
                'phone_numbers': ['79151234567', '79151234568', '79151234569', '79151234510', '123', '11'],
                'emails': ['a@b.cd', 'a@b.c2d', 'a@b.c3d', 'a@b.c4d', 'a@b.c5d', 'a@b.c6d'],
                'question_answer': {
                    'question': 'qqqqqq',
                    'answer': 'aaa',
                    'question_id': '100400',
                },
            },
            [
                'emails.invalid',
                'phone_numbers.invalid',
                'question_answer.question_id.invalid',
            ],
        ),
        (
            {
                'phone_numbers': [],
                'emails': [],
                'question_answer': {
                    'question': 'q' * 2000,
                    'answer': 'a' * 2000,
                    'question_id': 1,
                },
            },
            [
                'question_answer.question.long',
                'question_answer.answer.long',
            ],
        ),
    ]
    invalid_params_strict_form = copy.deepcopy(invalid_params)

    valid_params = [
        (
            {},
            {},
        ),
        (
            {
                'emails': [u'email@почта.рф'],
                'question_answer': {
                    'question': u'вопрос',
                    'answer': u'ответ',
                    'question_id': 10,
                },
                'phone_numbers': [
                    '89142341234',
                    '89142341212',
                ],
            },
            {
                'emails': [u'email@почта.рф'],
                'question_answer': {
                    'question': u'вопрос',
                    'answer': u'ответ',
                    'question_id': 10,
                },
                'phone_numbers': [
                    '89142341234',
                    '89142341212',
                ],
            },
        ),
    ]
    valid_params_strict_form = copy.deepcopy(valid_params)

    check_jsonschema_form(STEP_2_RECOVERY_TOOLS_STRICT_SCHEMA, invalid_params_strict_form, valid_params_strict_form)
    check_jsonschema_form(STEP_2_RECOVERY_TOOLS_SCHEMA, invalid_params, valid_params)


def test_step_3_registration_data_form():
    invalid_params = [
        (
            {
                'registration_date': '1999-02-29',  # невалидная дата
                'registration_country': u'Россия',
            },
            [
                'registration_date.invalid',
            ],
        ),
        (
            {
                'registration_date': '1999-10-10',  # год основания Яндекса - 2000
                'registration_country': 'Russia',
            },
            [
                'registration_date.tooearly',
            ],
        ),
        (
            {
                'registration_date': '3999-10-10',
                'registration_country': 'Russia',
            },
            [
                'registration_date.invalid',
            ],
        ),
        (
            {
                'registration_date': {},
                'registration_country': [],
                'registration_country_id': '95',
                'registration_city': {1: 2},
                'registration_city_id': '100',
            },
            [
                'registration_city.invalid',
                'registration_city_id.invalid',
                'registration_country.invalid',
                'registration_country_id.invalid',
                'registration_date.invalid',
            ],
        ),
    ]
    invalid_params_strict_form = copy.deepcopy(invalid_params) + [
        (
            {},
            [
                'registration_country.empty',
                'registration_date.empty',
            ],
        ),
    ]

    valid_params_strict_form = [
        (
            {
                'registration_date': '2000-00-00',
                'registration_country': 'Zimbabwe',
            },
            {
                'registration_date': datetime(2000, 1, 1),
                'registration_country': 'Zimbabwe',
            },
        ),
        (
            {
                'registration_date': '2010-10-10',
                'registration_country': 'Zimbabwe',
                'registration_country_id': 10,
                'registration_city': 'asdfg',
                'registration_city_id': 20,
            },
            {
                'registration_date': datetime(2010, 10, 10),
                'registration_country': 'Zimbabwe',
                'registration_country_id': 10,
                'registration_city': 'asdfg',
                'registration_city_id': 20,
            },
        ),
    ]
    valid_params = copy.deepcopy(valid_params_strict_form) + [
        (
            {},
            {},
        ),
        (
            {'registration_date': '2000-00-00'},
            {'registration_date': datetime(2000, 1, 1)},
        ),
        (
            {'registration_country': 'Zimbabwe'},
            {'registration_country': 'Zimbabwe'},
        ),
        (
            {'registration_city': 'asdfg'},
            {'registration_city': 'asdfg'},
        ),
    ]

    check_jsonschema_form(STEP_3_REGISTRATION_DATA_STRICT_SCHEMA, invalid_params_strict_form, valid_params_strict_form)
    check_jsonschema_form(STEP_3_REGISTRATION_DATA_SCHEMA, invalid_params, valid_params)


def test_step_4_used_services_form():
    invalid_params = [
        (
            {
                'social_accounts': None,
                'services': 'food',
            },
            [
                'social_accounts.invalid',
                'services.invalid',
            ],
        ),
        (
            {
                'social_accounts': ['123', '0x456', '123', 'fff', 'ddd', 'eee'],
                'services': [1, {}, 1, 'disk', 'food', 1],
            },
            [
                'social_accounts.invalid',
                'social_accounts.duplicate',
                'services.invalid',
                'services.duplicate',
            ],
        ),
        (
            {
                'social_accounts': map(str, range(MAX_SOCIAL_ACCOUNTS_COUNT + 1)),
                'services': ['disk'],
            },
            [
                'social_accounts.invalid',
            ],
        ),
    ]
    invalid_params_strict_form = copy.deepcopy(invalid_params)

    valid_params = [
        (
            {
                'social_accounts': [],
                'services': [],
            },
            {
                'social_accounts': [],
                'services': [],
            },
        ),
        (
            {
                'social_accounts': map(str, range(MAX_SOCIAL_ACCOUNTS_COUNT)),
                'services': [],
            },
            {
                'social_accounts': map(str, range(MAX_SOCIAL_ACCOUNTS_COUNT)),
                'services': [],
            },
        ),
        (
            {
                'social_accounts': [],
                'services': ['mail', 'yandsearch', 'disk', 'market', 'music', 'metrika'],
            },
            {
                'social_accounts': [],
                'services': ['mail', 'yandsearch', 'disk', 'market', 'music', 'metrika'],
            },
        ),
    ]
    valid_params_strict_form = copy.deepcopy(valid_params)

    check_jsonschema_form(STEP_4_USED_SERVICES_STRICT_SCHEMA, invalid_params_strict_form, valid_params_strict_form)
    check_jsonschema_form(STEP_4_USED_SERVICES_SCHEMA, invalid_params, valid_params)


def test_step_5_services_data_form():
    invalid_params = [
        (
            {
                'delivery_addresses': 10,
                'email_folders': {1: 2},
                'outbound_emails': 'zzz',
                'email_whitelist': -10,
                'email_blacklist': '',
                'email_collectors': {},
            },
            [
                'delivery_addresses.invalid',
                'email_blacklist.invalid',
                'email_collectors.invalid',
                'email_folders.invalid',
                'email_whitelist.invalid',
                'outbound_emails.invalid',
            ],
        ),
        (
            {
                'delivery_addresses': [{}, []],
                'email_folders': ['a', 'b', 'c', 'd', 'e', 'f'],
                'outbound_emails': ['bademail', 'abc@def.ru', 'bademail'],
                'email_whitelist': ['bbb'],
                'email_blacklist': [u'вася@пупкин.рф', 'aaa'],
                'email_collectors': [u'вася@google.ru', u'вася@google.ru'],
            },
            [
                'delivery_addresses.building.empty',
                'delivery_addresses.city.empty',
                'delivery_addresses.country.empty',
                'delivery_addresses.street.empty',
                'delivery_addresses.invalid',
                'email_blacklist.invalid',
                'email_collectors.duplicate',
                'email_folders.invalid',
                'email_whitelist.invalid',
                'outbound_emails.invalid',
                'outbound_emails.duplicate',
            ],
        ),
        (
            {
                'delivery_addresses': [
                    {'country': {}, 'city': 123, 'street': [], 'building': {1: 2}, 'suite': 1},
                ],
            },
            [
                'delivery_addresses.building.invalid',
                'delivery_addresses.city.invalid',
                'delivery_addresses.country.invalid',
                'delivery_addresses.street.invalid',
                'delivery_addresses.suite.invalid',
            ],
        ),
        (
            {
                'delivery_addresses': [
                    {'country': 'russia', 'city': 'moscow', 'street': 'tolstoy', 'building': '1a', 'suite': '1'},
                    {'country': 'russia', 'city': 'moscow', 'street': 'tolstoy', 'building': '1a', 'suite': '1'},
                ],
            },
            [
                'delivery_addresses.duplicate',
            ],
        ),
    ]
    invalid_params_strict_form = copy.deepcopy(invalid_params)

    valid_params = [
        (
            {
                'delivery_addresses': [],
                'email_folders': [],
                'outbound_emails': [],
                'email_whitelist': [],
                'email_blacklist': [],
                'email_collectors': [],
            },
            {
                'delivery_addresses': [],
                'email_folders': [],
                'outbound_emails': [],
                'email_whitelist': [],
                'email_blacklist': [],
                'email_collectors': [],
            },
        ),
        (
            {
                'delivery_addresses': [
                    {'country': 'russia', 'city': 'moscow', 'street': 'tolstoy', 'building': '1a'},
                    {'country': 'russia', 'city': 'moscow', 'street': 'tolstoy', 'building': '1a', 'suite': '1'},
                ],
                'email_folders': ['folder1', 'folder2', u'папка3'],
                'outbound_emails': [u'петя@mail.ru', 'asdf@ghjk.ru', 'a@bc.def'],
                'email_whitelist': ['white1@white.ru'],
                'email_blacklist': [u'черныйсписок@черный.рф'],
                'email_collectors': [u'rpop1@почта.ру'],
            },
            {
                'delivery_addresses': [
                    {'country': 'russia', 'city': 'moscow', 'street': 'tolstoy', 'building': '1a'},
                    {'country': 'russia', 'city': 'moscow', 'street': 'tolstoy', 'building': '1a', 'suite': '1'},
                ],
                'email_folders': ['folder1', 'folder2', u'папка3'],
                'outbound_emails': [u'петя@mail.ru', 'asdf@ghjk.ru', 'a@bc.def'],
                'email_whitelist': ['white1@white.ru'],
                'email_blacklist': [u'черныйсписок@черный.рф'],
                'email_collectors': [u'rpop1@почта.ру'],
            },
        ),
    ]
    valid_params_strict_form = copy.deepcopy(valid_params)

    check_jsonschema_form(STEP_5_SERVICES_DATA_STRICT_SCHEMA, invalid_params_strict_form, valid_params_strict_form)
    check_jsonschema_form(STEP_5_SERVICES_DATA_SCHEMA, invalid_params, valid_params)


def test_step_6_final_info_form():
    invalid_params = [
        (
            {
                'user_enabled': 23,
                'contact_reason': {},
            },
            [
                'contact_reason.invalid',
                'user_enabled.invalid',
            ],
        ),
    ]
    invalid_params_strict_form = copy.deepcopy(invalid_params) + [
        (
            {},
            [
                'user_enabled.empty',
            ],
        ),
    ]

    valid_params_strict_form = [
        (
            {
                'user_enabled': False,
            },
            {
                'user_enabled': False,
            },
        ),
        (
            {
                'user_enabled': False,
                'contact_reason': u'забыл пароль',
            },
            {
                'user_enabled': False,
                'contact_reason': u'забыл пароль',
            },
        ),
    ]
    valid_params = copy.deepcopy(valid_params_strict_form) + [
        (
            {},
            {},
        ),
        (
            {'contact_reason': u'забыл пароль'},
            {'contact_reason': u'забыл пароль'},
        ),
    ]

    check_jsonschema_form(STEP_6_FINAL_INFO_STRICT_SCHEMA, invalid_params_strict_form, valid_params_strict_form)
    check_jsonschema_form(STEP_6_FINAL_INFO_SCHEMA, invalid_params, valid_params)
