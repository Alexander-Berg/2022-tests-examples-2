# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.api.yasms.controllers.check_phone import CheckPhoneForm
from passport.backend.api.yasms.controllers.check_user import CheckUserForm
from passport.backend.api.yasms.controllers.confirm import ConfirmForm
from passport.backend.api.yasms.controllers.delete_phone import DeletePhoneForm
from passport.backend.api.yasms.controllers.drop_phone import DropPhoneForm
from passport.backend.api.yasms.controllers.have_user_once_validated_phone import HaveUserOnceValidatedPhoneForm
from passport.backend.api.yasms.controllers.prolong_valid import ProlongValidForm
from passport.backend.api.yasms.controllers.register import RegisterForm
from passport.backend.api.yasms.controllers.remove_user_phones import RemoveUserPhonesForm
from passport.backend.api.yasms.controllers.user_phones import UserPhonesForm
from passport.backend.api.yasms.controllers.validations_number_of_user_phones import ValidationsNumberOfUserPhonesForm
from passport.backend.api.yasms.forms import (
    form_encode_invalid_to_field_and_code,
    Invalid,
    OptionalSenderForm,
    RequiredSenderForm,
)
from passport.backend.core.test.test_utils.form_utils import check_equality
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.utils.common import merge_dicts


TEST_SENDER = u'dev'
TEST_UID = 2810
TEST_PHONE_NUMBER = u'+79889911334'


def build_out_args(**default_output):
    def out_args(**kwargs):
        return merge_dicts(default_output, kwargs)
    return out_args


def build_in_args(**default_input):
    def in_args(**kwargs):
        args = merge_dicts(default_input, kwargs)
        return {key: args[key] for key in args if args[key] is not None}
    return in_args


class TestCheckForm(TestCase):
    def test_pass(self):
        valid_tests = [({u'sender': TEST_SENDER}, {u'sender': TEST_SENDER})]
        invalid_tests = [({u'sender': u'\u0000'}, (u'sender', u'invalid'))]
        check_form(OptionalSenderForm(), invalid_tests, valid_tests)

    @raises(AssertionError)
    def test_assertion_error(self):
        check_form(
            OptionalSenderForm(),
            [({u'sender': TEST_SENDER}, {u'sender': TEST_SENDER})],
            [],
        )


def check_form(form, invalid_tests, valid_tests):
    for invalid_params, expected in invalid_tests:
        try:
            form.to_python(invalid_params)
            raise AssertionError(
                u'Form (%s) validation expected to fail with params: %s' %
                (form.__class__.__name__, repr(invalid_params)),
            )
        except Invalid as e:
            field, code = form_encode_invalid_to_field_and_code(e)
            eq_((field, code), expected)

    for p in valid_tests:
        check_equality(form, p)


def test_optional_sender_form():
    valid_tests = [
        # не задан
        ({}, {u'sender': None}),

        # пустой
        ({u'sender': u''}, {u'sender': None}),

        # пустой после урезки
        ({u'sender': u'  '}, {u'sender': None}),

        # переданный
        ({u'sender': TEST_SENDER}, {u'sender': TEST_SENDER}),

        # дополнительные параметры игнорируются
        (
            {u'sender': TEST_SENDER, u'extra': u'extra'},
            {u'sender': TEST_SENDER},
        ),
    ]

    invalid_tests = [
        ({u'sender': u'\u0000'}, (u'sender', u'invalid')),
    ]

    check_form(OptionalSenderForm(), invalid_tests, valid_tests)


def check_optional_sender_uid_form(form):
    valid_tests = [
        # обычные параметры
        (
            {u'uid': str(TEST_UID), u'sender': TEST_SENDER},
            {u'uid': TEST_UID, u'sender': TEST_SENDER},
        ),
    ]

    invalid_tests = [
        ({u'sender': TEST_SENDER}, (u'uid', u'missingValue')),
        ({u'sender': TEST_SENDER, u'uid': u''}, (u'uid', u'empty')),
        (
            {u'uid': u'non_number_uid', u'sender': TEST_SENDER},
            (u'uid', u'integer'),
        ),
    ]

    check_form(form, invalid_tests, valid_tests)


def test_validations_number_of_user_phones_form():
    check_optional_sender_uid_form(ValidationsNumberOfUserPhonesForm())


def test_have_user_once_validated_phone_form():
    check_optional_sender_uid_form(HaveUserOnceValidatedPhoneForm())


def test_user_phones_form():
    in_args = build_in_args(**{
        u'uid': str(TEST_UID),
        u'sender': TEST_SENDER,
        u'format': u'xml',
    })
    out_args = build_out_args(**{
        u'uid': TEST_UID,
        u'sender': TEST_SENDER,
        u'format': u'xml',
    })
    valid_tests = [
        (in_args(format=u'xml'), out_args(format=u'xml')),
        (in_args(format=None), out_args(format=u'xml')),
        (in_args(format=u''), out_args(format=u'xml')),
        (in_args(format=u'json'), out_args(format=u'json')),
    ]

    invalid_tests = [
        (in_args(uid=None), (u'uid', u'missingValue')),
        (in_args(uid=u''), (u'uid', u'empty')),
        (in_args(uid=u'non_number_uid'), (u'uid', u'integer')),
        (in_args(format=u'invalid'), (u'format', u'invalid')),
    ]

    check_form(UserPhonesForm(), invalid_tests, valid_tests)


def test_check_user_form():
    check_optional_sender_uid_form(CheckUserForm())


def test_required_sender_form():
    valid_tests = [
        ({u'sender': u'some_sender'}, {u'sender': u'some_sender'}),
    ]

    invalid_tests = [
        ({}, (u'sender', u'missingValue')),
        ({u'sender': u''}, (u'sender', u'empty')),
        ({u'sender': u'\u0000'}, (u'sender', u'invalid')),
        ({u'sender': u'send!r'}, (u'sender', u'invalid')),
    ]

    check_form(RequiredSenderForm(), invalid_tests, valid_tests)


def test_check_phone_form():
    valid_tests = [
        (
            {u'sender': u'some_sender', u'phone': u'+79010000001'},
            {
                u'sender': u'some_sender',
                u'phone': u'+79010000001',
                u'all': False,
            },
        ),
        (
            {u'sender': u'some_sender', u'phone': u'+79010000001', u'all': u'0'},
            {u'sender': u'some_sender', u'phone': u'+79010000001', u'all': False},
        ),
        (
            {u'sender': u'some_sender', u'phone': u'+79010000001', u'all': u'1'},
            {u'sender': u'some_sender', u'phone': u'+79010000001', u'all': True},
        ),
        (
            {u'sender': u'some_sender', u'phone': u'89010000001'},
            {
                u'sender': u'some_sender',
                u'phone': u'89010000001',
                u'all': False,
            },
        ),
        (
            {u'sender': u'some_sender', u'phone': u'abcdef'},
            {u'sender': u'some_sender', u'phone': u'abcdef', 'all': False},
        ),
        (
            {u'sender': u'some_sender', u'phone': u'+7654'},
            {u'sender': u'some_sender', u'phone': u'+7654', 'all': False},
        ),
    ]

    invalid_tests = [
        ({u'sender': u'some_sender'}, (u'phone', u'missingValue')),
        ({u'sender': u'some_sender', u'phone': u''}, (u'phone', u'empty')),
        (
            {
                u'sender': u'some_sender',
                u'phone': u'+79010000001',
                u'all': u'some shit',
            },
            (u'all', u'string'),
        )
    ]

    check_form(CheckPhoneForm(), invalid_tests, valid_tests)


def test_prolong_valid_form():
    valid_tests = [
        (
            {u'sender': u'some_sender', u'number': u'+79010000001', u'uid': u'3895'},
            {u'sender': u'some_sender', u'number': u'+79010000001', u'uid': 3895},
        ),
        (
            {u'sender': u'some_sender', u'number': u'89010000001', u'uid': u'3895'},
            {u'sender': u'some_sender', u'number': u'89010000001', u'uid': 3895},
        ),
        (
            {u'sender': u'some_sender', u'uid': u'1244', u'number': u'+7832'},
            {u'sender': u'some_sender', u'uid': 1244, u'number': u'+7832'},
        ),
        (
            {u'sender': u'some_sender', u'uid': u'1244', u'number': u'abcdefghijkl'},
            {u'sender': u'some_sender', u'uid': 1244, u'number': u'abcdefghijkl'},
        ),
    ]

    invalid_tests = [
        (
            {
                u'sender': u'some_sender',
                u'number': u'+79010000001',
            },
            (u'uid', u'missingValue'),
        ),
        (
            {
                u'sender': u'some_sender',
                u'uid': u'',
                u'number': u'+79010000001',
            },
            (u'uid', u'empty'),
        ),
        (
            {
                u'sender': u'some_sender',
                u'uid': u'not number',
                u'number': u'+79010000001',
            },
            (u'uid', u'integer'),
        ),
        (
            {
                u'sender': u'some_sender',
                u'uid': u'1244',
            },
            (u'number', u'missingValue'),
        ),
        (
            {
                u'sender': u'some_sender',
                u'uid': u'1244',
                u'number': u'',
            },
            (u'number', u'empty'),
        ),
    ]

    check_form(ProlongValidForm(), invalid_tests, valid_tests)


def test_remove_user_phones_form():
    valid_tests = [
        (
            {u'sender': u'passport', u'uid': u'358', u'block': u'0'},
            {u'sender': u'passport', u'uid': 358, u'block': False},
        ),
        (
            {u'sender': u'passport', u'uid': u'358', u'block': u'1'},
            {u'sender': u'passport', u'uid': 358, u'block': True},
        ),
        (
            {u'sender': u'passport', u'uid': u'358'},
            {u'sender': u'passport', u'uid': 358, u'block': False},
        ),
        (
            {u'sender': u'passport', u'block': u'0'},
            {u'sender': u'passport', u'uid': None, u'block': False},
        ),
        (
            {u'sender': u'passport', u'uid': u'-1', u'block': u'0'},
            {u'sender': u'passport', u'uid': None, u'block': False},
        ),
        (
            {u'sender': u'passport', u'uid': u'a', u'block': u'0'},
            {u'sender': u'passport', u'uid': None, u'block': False},
        ),
    ]
    invalid_tests = [
        (
            {u'sender': u'passport', u'uid': u'358', u'block': u'x'},
            (u'block', u'string'),
        ),
    ]
    check_form(RemoveUserPhonesForm, invalid_tests, valid_tests)


def test_delete_phone_form():
    valid_tests = [
        (
            {u'sender': u'passport', u'uid': u'4399', u'number': u'+79010000001'},
            {u'sender': u'passport', u'uid': 4399, u'number': u'+79010000001'},
        ),
        (
            {u'sender': u'passport', u'uid': u'4399', u'number': u'89010000001'},
            {u'sender': u'passport', u'uid': 4399, u'number': u'89010000001'},
        ),
        (
            {u'sender': u'passport', u'uid': u'4399', u'number': u'abcdef'},
            {u'sender': u'passport', u'uid': 4399, u'number': u'abcdef'},
        ),
    ]

    invalid_tests = [
        (
            {u'sender': u'passport', u'number': u'+79010000001'},
            (u'uid', u'missingValue'),
        ),
        (
            {u'sender': u'passport', u'uid': u'', u'number': u'+79010000001'},
            (u'uid', u'empty'),
        ),
        (
            {u'sender': u'passport', u'uid': u'x1r', u'number': u'+79010000001'},
            (u'uid', u'integer'),
        ),
        (
            {u'sender': u'passport', u'uid': u'-1', u'number': u'+79010000001'},
            (u'uid', u'tooLow'),
        ),
        (
            {u'sender': u'passport', u'uid': u'4399'},
            (u'number', u'missingValue'),
        ),
        (
            {u'sender': u'passport', u'uid': u'4399', u'number': u''},
            (u'number', u'empty'),
        ),
        # NOUID проверяется раньше,чем NOPHONE
        ({u'sender': u'passport'}, (u'uid', u'missingValue')),
    ]

    check_form(DeletePhoneForm(), invalid_tests, valid_tests)


def test_drop_phone_form():
    valid_tests = [
        (
            {u'sender': u'passport', u'uid': u'4399', u'phoneid': u'2358'},
            {u'sender': u'passport', u'uid': 4399, u'phoneid': 2358},
        ),
    ]

    invalid_tests = [
        (
            {u'sender': u'passport', u'phoneid': u'2358'},
            (u'uid', u'missingValue'),
        ),
        (
            {u'sender': u'passport', u'uid': u'', u'phoneid': u'2358'},
            (u'uid', u'empty'),
        ),
        (
            {u'sender': u'passport', u'uid': u'x1r', u'phoneid': u'2358'},
            (u'uid', u'integer'),
        ),
        (
            {u'sender': u'passport', u'uid': u'-1', u'phoneid': u'2358'},
            (u'uid', u'tooLow'),
        ),
        ({u'sender': u'passport', u'uid': u'4399'}, (u'phoneid', u'missingValue')),
        ({u'sender': u'passport', u'uid': u'4399', u'phoneid': u''}, (u'phoneid', u'empty')),
        ({u'sender': u'passport', u'uid': u'4399', u'phoneid': u'x1r'}, (u'phoneid', u'integer')),
        ({u'sender': u'passport', u'uid': u'4399', u'phoneid': u'-1'}, (u'phoneid', u'tooLow')),
    ]

    check_form(DropPhoneForm(), invalid_tests, valid_tests)


@with_settings(
    DISPLAY_LANGUAGES=[u'ru', u'kr', u'en'],
)
def test_register_form():
    out_args = build_out_args(**{
        u'sender': u'passport',
        u'uid': 4399,
        u'number': u'+79010000001',
        u'secure': False,
        u'revalidate': False,
        u'withoutsms': False,
        u'ignore_bindlimit': False,
        u'ts': None,
        u'lang': u'ru',
    })

    in_args = build_in_args(**{
        u'sender': u'passport',
        u'uid': u'4399',
        u'number': u'+79010000001',
    })

    valid_tests = [
        (in_args(uid=u'2358'), out_args(uid=2358)),

        (in_args(number=u'+79010000001'), out_args(number=u'+79010000001')),
        (in_args(number=u'89010000001'), out_args(number=u'89010000001')),

        (in_args(secure=None), out_args(secure=False)),
        (in_args(secure=u''), out_args(secure=False)),
        (in_args(secure=u'0'), out_args(secure=False)),
        (in_args(secure=u'false'), out_args(secure=False)),
        (in_args(secure=u'no'), out_args(secure=False)),
        (in_args(secure=u'1'), out_args(secure=True)),
        (in_args(secure=u'true'), out_args(secure=True)),
        (in_args(secure=u'yes'), out_args(secure=True)),

        (in_args(revalidate=None), out_args(revalidate=False)),
        (in_args(revalidate=u''), out_args(revalidate=False)),
        (in_args(revalidate=u'0'), out_args(revalidate=False)),
        (in_args(revalidate=u'false'), out_args(revalidate=False)),
        (in_args(revalidate=u'no'), out_args(revalidate=False)),
        (in_args(revalidate=u'1'), out_args(revalidate=True)),
        (in_args(revalidate=u'true'), out_args(revalidate=True)),
        (in_args(revalidate=u'yes'), out_args(revalidate=True)),

        (in_args(withoutsms=None), out_args(withoutsms=False)),
        (in_args(withoutsms=u''), out_args(withoutsms=False)),
        (in_args(withoutsms=u'0'), out_args(withoutsms=False)),
        (in_args(withoutsms=u'false'), out_args(withoutsms=False)),
        (in_args(withoutsms=u'no'), out_args(withoutsms=False)),
        (in_args(withoutsms=u'1'), out_args(withoutsms=True)),
        (in_args(withoutsms=u'true'), out_args(withoutsms=True)),
        (in_args(withoutsms=u'yes'), out_args(withoutsms=True)),

        (in_args(ignore_bindlimit=None), out_args(ignore_bindlimit=False)),
        (in_args(ignore_bindlimit=u''), out_args(ignore_bindlimit=False)),
        (in_args(ignore_bindlimit=u'0'), out_args(ignore_bindlimit=False)),
        (in_args(ignore_bindlimit=u'false'), out_args(ignore_bindlimit=False)),
        (in_args(ignore_bindlimit=u'no'), out_args(ignore_bindlimit=False)),
        (in_args(ignore_bindlimit=u'1'), out_args(ignore_bindlimit=True)),
        (in_args(ignore_bindlimit=u'true'), out_args(ignore_bindlimit=True)),
        (in_args(ignore_bindlimit=u'yes'), out_args(ignore_bindlimit=True)),

        (in_args(ts=None), out_args(ts=None)),
        (in_args(ts=u''), out_args(ts=None)),
        (in_args(ts=u'-1'), out_args(ts=-1)),
        (in_args(ts=u'0'), out_args(ts=0)),
        (in_args(ts=u'1'), out_args(ts=1)),

        (in_args(lang=None), out_args(lang=u'ru')),
        (in_args(lang=u''), out_args(lang=u'ru')),
        (in_args(lang=u'kr'), out_args(lang=u'kr')),
        (in_args(lang=u'jp'), out_args(lang=u'en')),
    ]

    invalid_tests = [
        (in_args(uid=None), (u'uid', u'missingValue')),
        (in_args(uid=u''), (u'uid', u'empty')),
        (in_args(uid=u'-1'), (u'uid', u'tooLow')),
        (in_args(uid=u'0x1'), (u'uid', u'integer')),

        (in_args(number=None), (u'number', u'missingValue')),
        (in_args(number=u''), (u'number', u'empty')),
        (in_args(number=u'02'), (u'number', u'badPhone')),
        (in_args(number=u'ab'), (u'number', u'badPhone')),

        (in_args(secure=u'foo'), (u'secure', u'string')),
        (in_args(revalidate=u'foo'), (u'revalidate', u'string')),
        (in_args(withoutsms=u'foo'), (u'withoutsms', u'string')),
        (in_args(ignore_bindlimit=u'foo'), (u'ignore_bindlimit', u'string')),

        (in_args(ts=u'abcd'), (u'ts', u'integer')),
        (in_args(ts=str(2 ** 63 - 1)), (u'ts', u'tooHigh')),
        (in_args(ts=str(-(2 ** 63))), (u'ts', u'tooLow')),
    ]

    check_form(RegisterForm(), invalid_tests, valid_tests)


def test_confirm_form():
    in_args = build_in_args(**{u'sender': u'passport', u'uid': u'2525', u'code': u'1111', u'phoneid': u'1313'})
    out_args = build_out_args(**{u'sender': u'passport', u'uid': 2525, u'code': u'1111', u'phoneid': 1313, u'number': None})

    valid_tests = [
        (
            in_args(phoneid=u'1313', number=None),
            out_args(phoneid=1313, number=None),
        ),
        (
            in_args(phoneid=None, number=u'89076655444'),
            out_args(phoneid=None, number=u'89076655444'),
        ),
        (
            in_args(phoneid=None, number=u'+79037766555'),
            out_args(phoneid=None, number=u'+79037766555'),
        ),
        (
            in_args(phoneid=None, number=u'02'),
            out_args(phoneid=None, number=u'02'),
        ),
        (
            in_args(phoneid=None, number=u'hello'),
            out_args(phoneid=None, number=u'hello'),
        ),
        (
            in_args(phoneid=u'1313', number=u'+79037766555'),
            out_args(phoneid=1313, number=u'+79037766555'),
        ),
        (in_args(code=u'333'), out_args(code=u'333')),
        (in_args(code=u'4444'), out_args(code=u'4444')),
        (in_args(code=u'55555'), out_args(code=u'55555')),
        (in_args(code=u'abcd'), out_args(code=u'abcd')),
        (in_args(code=u'a@b.c'), out_args(code=u'a@b.c')),
        (in_args(code=u'казик07'), out_args(code=u'казик07')),
        (in_args(code=u'+79010000001'), out_args(code=u'+79010000001')),
        (
            in_args(code=u'https://yastatic.net/mail/1.png'),
            out_args(code=u'https://yastatic.net/mail/1.png'),
        ),
    ]

    invalid_tests = [
        (in_args(uid=None), (u'uid', u'missingValue')),
        (in_args(uid=u''), (u'uid', u'empty')),
        (in_args(uid=u'e4z'), (u'uid', u'integer')),
        (in_args(uid=u'-1'), (u'uid', u'tooLow')),

        (in_args(code=None), (u'code', u'missingValue')),
        (in_args(code=u'0'), (u'code', u'invalid')),
        (in_args(code=u''), (u'code', u'empty')),

        (in_args(phoneid=u'k5a'), (u'phoneid', u'integer')),
        (in_args(phoneid=u'-1'), (u'phoneid', u'tooLow')),

        (in_args(phoneid=None, number=None), (u'number_or_phoneid', u'tooFew')),
        (in_args(phoneid=u'', number=u''), (u'number_or_phoneid', u'tooFew')),
    ]

    check_form(ConfirmForm(), invalid_tests, valid_tests)
