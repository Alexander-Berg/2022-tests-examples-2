# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_DEFAULT_UID,
    TEST_EMAIL_RESTORATION_KEY,
    TEST_PDD_EMAIL_RESTORATION_KEY,
    TEST_PDD_UID,
    TEST_PERSISTENT_TRACK_ID,
    TEST_RETPATH,
)
from passport.backend.api.views.bundle.restore.base import (
    RESTORE_METHOD_HINT,
    RESTORE_METHOD_PHONE,
    RESTORE_METHOD_SEMI_AUTO_FORM,
)
from passport.backend.api.views.bundle.restore.forms import (
    RestoreCheck2FAFormForm,
    RestoreCheckAnswerForm,
    RestoreCheckEmailForm,
    RestoreCheckPhoneForm,
    RestoreCheckPinForm,
    RestoreCommitForm,
    RestoreCommitNewMethodForm,
    RestoreConfirmPhoneForm,
    RestoreCreateLinkForm,
    RestoreKeySubmitForm,
    RestoreSelectMethodForm,
    RestoreSubmitForm,
)
from passport.backend.core.support_link_types import SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.phone_number.phone_number import parse_phone_number


@with_settings_hosts()
class TestForms(unittest.TestCase):
    def test_submit(self):
        invalid_params = [
            (
                {},
                ['login.empty'],
            ),
            (
                {'login': '', 'retpath': '', 'gps_package_name': ''},
                ['login.empty', 'retpath.empty', 'gps_package_name.empty'],
            ),
            (
                {'login': 'foobar@', 'gps_package_name': 'BAD'},
                ['login.invalid', 'gps_package_name.invalid'],
            ),
        ]

        valid_params = [
            (
                {'login': 'login', 'retpath': TEST_RETPATH},
                {'login': 'login', 'retpath': TEST_RETPATH, 'gps_package_name': None},
            ),
            (
                {'login': 'login', 'retpath': '1234'},
                {'login': 'login', 'retpath': None, 'gps_package_name': None},
            ),
            (
                {'login': 'Login', 'gps_package_name': 'com.yandex.maps'},
                {'login': 'Login', 'retpath': None, 'gps_package_name': 'com.yandex.maps'},
            ),
        ]

        check_form(RestoreSubmitForm(), invalid_params, valid_params, None)

    def test_key_submit(self):
        invalid_params = [
            (
                {},
                ['secret_key.empty'],
            ),
            (
                {'secret_key': ''},
                ['secret_key.empty'],
            ),
            (
                {'secret_key': 'not-a-key'},
                ['secret_key.invalid'],
            ),
        ]

        valid_params = [
            (
                {'secret_key': TEST_EMAIL_RESTORATION_KEY},
                {
                    'secret_key': {
                        'track_key': TEST_EMAIL_RESTORATION_KEY,
                        'uid': TEST_DEFAULT_UID,
                        'track_id': TEST_PERSISTENT_TRACK_ID,
                    },
                },
            ),
            (
                {'secret_key': TEST_PDD_EMAIL_RESTORATION_KEY},
                {
                    'secret_key': {
                        'track_key': TEST_PDD_EMAIL_RESTORATION_KEY,
                        'uid': TEST_PDD_UID,
                        'track_id': TEST_PERSISTENT_TRACK_ID,
                    },
                },
            ),
        ]

        check_form(RestoreKeySubmitForm(), invalid_params, valid_params, None)

    def test_select_method(self):
        invalid_params = [
            (
                {},
                ['method.empty'],
            ),
            (
                {'method': ''},
                ['method.empty'],
            ),
            (
                {'method': 'foobar'},
                ['method.invalid'],
            ),
        ]

        valid_params = [
            (
                {'method': RESTORE_METHOD_PHONE},
                {'method': RESTORE_METHOD_PHONE},
            ),
            (
                {'method': RESTORE_METHOD_SEMI_AUTO_FORM + '    '},
                {'method': RESTORE_METHOD_SEMI_AUTO_FORM},
            ),
        ]

        check_form(RestoreSelectMethodForm(), invalid_params, valid_params, None)

    def test_commit(self):
        invalid_params = [
            (
                {},
                ['password.empty', 'display_language.empty'],
            ),
            (
                {'password': '', 'display_language': ''},
                ['password.empty', 'display_language.empty'],
            ),
        ]

        valid_params = [
            (
                {
                    'password': 'pwd',
                    'display_language': 'ru',
                },
                {
                    'password': 'pwd',
                    'display_language': 'ru',
                    'revoke_web_sessions': True,
                    'revoke_tokens': True,
                    'revoke_app_passwords': True,
                },
            ),
            (
                {
                    'password': ' pwd ',
                    'display_language': ' ru ',
                    'revoke_web_sessions': 'false',
                    'revoke_tokens': 'no',
                    'revoke_app_passwords': 'off',
                },
                {
                    'password': 'pwd',
                    'display_language': 'ru',
                    'revoke_web_sessions': False,
                    'revoke_tokens': False,
                    'revoke_app_passwords': False,
                },
            ),
        ]

        check_form(RestoreCommitForm(), invalid_params, valid_params, None)

    def test_commit_new_method_with_allowed_and_required_methods(self):
        invalid_params = [
            (
                {},
                ['new_method.empty'],
            ),
            (
                {'new_method': ''},
                ['new_method.empty'],
            ),
            (
                {'new_method': RESTORE_METHOD_SEMI_AUTO_FORM},
                ['new_method.invalid'],
            ),
            (
                {'new_method': RESTORE_METHOD_HINT},
                ['answer.empty'],
            ),
            (
                {'new_method': RESTORE_METHOD_HINT, 'answer': ''},
                ['answer.empty'],
            ),
            (
                {'new_method': RESTORE_METHOD_HINT, 'answer': 'ans'},
                ['form.invalid'],
            ),
            (
                {'new_method': RESTORE_METHOD_HINT, 'answer': 'ans', 'question': 'q', 'question_id': '1'},
                ['form.invalid'],
            ),
            (
                {'new_method': RESTORE_METHOD_HINT, 'question_id': 'abc'},
                ['question_id.invalid'],
            ),
        ]

        valid_params = [
            (
                {'new_method': RESTORE_METHOD_PHONE},
                {'new_method': RESTORE_METHOD_PHONE, 'answer': None, 'question': None, 'question_id': None},
            ),
            (
                {'new_method': RESTORE_METHOD_HINT, 'answer': 'ans', 'question': 'q'},
                {'new_method': RESTORE_METHOD_HINT, 'answer': 'ans', 'question': 'q', 'question_id': None},
            ),
            (
                {'new_method': RESTORE_METHOD_HINT, 'answer': 'ans', 'question_id': '1'},
                {'new_method': RESTORE_METHOD_HINT, 'answer': 'ans', 'question_id': 1, 'question': None},
            ),
        ]

        check_form(
            RestoreCommitNewMethodForm([RESTORE_METHOD_HINT, RESTORE_METHOD_PHONE], is_new_method_required=True),
            invalid_params,
            valid_params,
            None,
        )

    def test_commit_new_method_with_allowed_but_not_required_methods(self):
        invalid_params = [
            (
                {'new_method': RESTORE_METHOD_SEMI_AUTO_FORM},
                ['new_method.invalid'],
            ),
            (
                {'new_method': RESTORE_METHOD_HINT},
                ['answer.empty'],
            ),
            (
                {'new_method': RESTORE_METHOD_HINT, 'answer': ''},
                ['answer.empty'],
            ),
            (
                {'new_method': RESTORE_METHOD_HINT, 'answer': 'ans'},
                ['form.invalid'],
            ),
            (
                {'new_method': RESTORE_METHOD_HINT, 'answer': 'ans', 'question': 'q', 'question_id': '1'},
                ['form.invalid'],
            ),
            (
                {'new_method': RESTORE_METHOD_HINT, 'question_id': 'abc'},
                ['question_id.invalid'],
            ),
        ]

        valid_params = [
            (
                {},
                {'new_method': None, 'answer': None, 'question': None, 'question_id': None},
            ),
            (
                {'new_method': ''},
                {'new_method': None, 'answer': None, 'question': None, 'question_id': None},
            ),
            (
                {'new_method': RESTORE_METHOD_PHONE},
                {'new_method': RESTORE_METHOD_PHONE, 'answer': None, 'question': None, 'question_id': None},
            ),
            (
                {'new_method': RESTORE_METHOD_HINT, 'answer': 'ans', 'question': 'q'},
                {'new_method': RESTORE_METHOD_HINT, 'answer': 'ans', 'question': 'q', 'question_id': None},
            ),
            (
                {'new_method': RESTORE_METHOD_HINT, 'answer': 'ans', 'question_id': '1'},
                {'new_method': RESTORE_METHOD_HINT, 'answer': 'ans', 'question_id': 1, 'question': None},
            ),
        ]

        check_form(
            RestoreCommitNewMethodForm([RESTORE_METHOD_HINT, RESTORE_METHOD_PHONE], is_new_method_required=False),
            invalid_params,
            valid_params,
            None,
        )

    def test_commit_new_method_with_no_allowed_methods(self):
        invalid_params = [
            (
                {},
                ['new_method.empty'],
            ),
            (
                {'new_method': ''},
                ['new_method.empty'],
            ),
            (
                {'new_method': RESTORE_METHOD_HINT},
                ['new_method.invalid'],
            ),
        ]

        valid_params = []

        check_form(RestoreCommitNewMethodForm([], is_new_method_required=True), invalid_params, valid_params, None)

    def test_check_phone(self):
        invalid_params = [
            (
                {},
                ['phone_number.empty', 'display_language.empty'],
            ),
            (
                {'phone_number': '', 'display_language': '', 'country': '', 'code_format': ''},
                ['phone_number.empty', 'display_language.empty', 'country.empty', 'code_format.empty'],
            ),
            (
                {'phone_number': '1122', 'display_language': 'BAD', 'country': 'BAD', 'code_format': 'BAD'},
                ['display_language.invalid', 'country.invalid', 'code_format.invalid'],
            ),
            (
                {'phone_number': '89151234567', 'display_language': 'TR', 'country': 'tr'},
                ['phone_number.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'phone_number': '+79151234567',
                    'display_language': 'RU',
                },
                {
                    'phone_number': parse_phone_number('+79151234567'),
                    'confirm_method': 'by_sms',
                    'display_language': 'ru',
                    'country': None,
                    'code_format': None,
                },
            ),
            (
                {
                    'phone_number': '89151234567',
                    'display_language': 'RU',
                    'country': 'ru',
                    'code_format': 'by_3_dash',
                },
                {
                    'phone_number': parse_phone_number('+79151234567'),
                    'confirm_method': 'by_sms',
                    'display_language': 'ru',
                    'country': 'ru',
                    'code_format': 'by_3_dash',
                },
            ),
        ]

        check_form(RestoreCheckPhoneForm(), invalid_params, valid_params, None)

    def test_confirm_phone(self):
        invalid_params = [
            (
                {},
                ['code.empty'],
            ),
            (
                {'code': '  '},
                ['code.empty'],
            ),
        ]

        valid_params = [
            (
                {'code': ' 123456 '},
                {'code': '123456'},
            ),
        ]

        check_form(RestoreConfirmPhoneForm(), invalid_params, valid_params, None)

    def test_check_pin(self):
        invalid_params = [
            (
                {},
                ['pin.empty'],
            ),
            (
                {'pin': '  '},
                ['pin.empty'],
            ),
        ]

        valid_params = [
            (
                {'pin': ' 1234 '},
                {'pin': '1234'},
            ),
        ]

        check_form(RestoreCheckPinForm(), invalid_params, valid_params, None)

    def test_check_2fa_form(self):
        invalid_params = [
            (
                {},
                ['firstname.empty', 'lastname.empty', 'password.empty'],
            ),
            (
                {'firstname': '  ', 'lastname': '', 'answer': '1' * 1025, 'password': ''},
                ['firstname.empty', 'lastname.empty', 'password.empty', 'answer.long'],
            ),
        ]

        valid_params = [
            (
                {'firstname': ' vasia ', 'lastname': ' pupkin ', 'answer': ' answer ', 'password': ' passwd '},
                {'firstname': 'vasia', 'lastname': 'pupkin', 'answer': 'answer', 'password': 'passwd'},
            ),
            (
                {'firstname': u'Вася', 'lastname': u'Пупкин', 'password': ' passwd '},
                {'firstname': u'Вася', 'lastname': u'Пупкин', 'password': 'passwd', 'answer': None},
            ),
        ]

        check_form(RestoreCheck2FAFormForm(), invalid_params, valid_params, None)

    def test_check_email(self):
        invalid_params = [
            (
                {},
                ['email.empty', 'display_language.empty'],
            ),
            (
                {'email': '  ', 'display_language': '', 'is_simple_format': ' '},
                ['email.empty', 'display_language.empty', 'is_simple_format.empty'],
            ),
            (
                {'email': 'email.without.domain', 'display_language': 'vru', 'is_simple_format': '!'},
                ['email.invalid', 'display_language.invalid', 'is_simple_format.invalid'],
            ),
        ]

        valid_params = [
            (
                {'email': u' email@закодированный.домен ', 'display_language': '  tr  '},
                {'email': u'email@закодированный.домен', 'display_language': 'tr', 'is_simple_format': False},
            ),
            (
                {'email': u'email@yandex.ru', 'display_language': 'uk', 'is_simple_format': 'yes'},
                {'email': u'email@yandex.ru', 'display_language': 'uk', 'is_simple_format': True},
            ),
        ]

        check_form(RestoreCheckEmailForm(), invalid_params, valid_params, None)

    def test_check_answer(self):
        invalid_params = [
            (
                {},
                ['answer.empty'],
            ),
            (
                {'answer': '  '},
                ['answer.empty'],
            ),
            (
                {'answer': 'z' * 100500},
                ['answer.long'],
            ),
        ]

        valid_params = [
            (
                {'answer': ' answer '},
                {'answer': 'answer'},
            ),
        ]

        check_form(RestoreCheckAnswerForm(), invalid_params, valid_params, None)

    def test_create_link(self):
        invalid_params = [
            (
                {},
                ['uid.empty', 'link_type.empty', 'admin_name.empty'],
            ),
            (
                {'uid': '', 'link_type': '', 'admin_name': '', 'comment': ''},
                ['uid.empty', 'link_type.empty', 'admin_name.empty'],
            ),
            (
                {'uid': 'abcd', 'link_type': 'qwerty', 'admin_name': 'a', 'comment': 'c'},
                ['uid.invalid', 'link_type.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'uid': '10',
                    'link_type': SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                    'admin_name': ' a ',
                    'comment': ' b ',
                },
                {
                    'uid': 10,
                    'link_type': SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                    'admin_name': 'a',
                    'comment': 'b',
                },
            ),
        ]

        check_form(RestoreCreateLinkForm(), invalid_params, valid_params, None)
