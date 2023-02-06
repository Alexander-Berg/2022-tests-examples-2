# -*- coding: utf-8 -*-

from nose_parameterized import parameterized
from passport.backend.api.common import format_errors
from passport.backend.api.test.utils import assert_errors
from passport.backend.api.views.bundle.family.forms import (
    FamilyCreateInviteForm,
    FamilyRemoveMemberForm,
)
from passport.backend.core import validators
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.test.test_utils.form_utils import check_equality
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import merge_dicts


class TestFamilyForms(PassportTestCase):
    def check_form_errors(self, form, params, expected_errors, state=None):
        try:
            form.to_python(params, state)
            self.fail("Form (%s) validation expected to fail with params: %s" % (form.__class__.__name__, repr(params)))
        except validators.Invalid as e:
            assert_errors(format_errors(e), expected_errors)

    @parameterized.expand([
        (
            {'sms_phone': 'test@test.com'},
            [{'sms_phone': 'badphonenumber'}],
        ),
        (
            {'email': '799912345670a--11/'},
            [{'email': 'noat'}],
        ),
        (
            {'email': 'test@test.com', 'sms_phone': '79991234567'},
            [{'form': 'toomany'}],
        ),
        (
            {'scenario': ''},
            [{'scenario': 'empty'}],
        ),
    ])
    def test_family_create_invite_invalid(self, params, errors):
        self.check_form_errors(FamilyCreateInviteForm(), params, errors)

    family_create_invite_optional_defaults = dict(
        email=None,
        multisession_uid=None,
        sms_phone=None,
        sms_phone_country=None,
        uid=None,
        scenario=None,
    )

    @parameterized.expand([
        ({}, family_create_invite_optional_defaults),
        (
            {'email': 'test@test.com'},
            merge_dicts(family_create_invite_optional_defaults, {'email': 'test@test.com'}),
        ),
        (
            {'scenario': 'test-scenario'},
            merge_dicts(family_create_invite_optional_defaults, {'scenario': 'test-scenario'}),
        ),
        (
            {'sms_phone': '79991234567'},
            merge_dicts(family_create_invite_optional_defaults, {'sms_phone': PhoneNumber.parse('79991234567')}),
        ),
        (
            {'uid': '1234567'},
            merge_dicts(family_create_invite_optional_defaults, {'uid': 1234567}),
        ),
        (
            {'email': 'test@test.com', 'uid': '1234567'},
            merge_dicts(family_create_invite_optional_defaults, {'email': 'test@test.com', 'uid': 1234567}),
        ),
        (
            {'sms_phone': '79991234567', 'uid': '1234567'},
            merge_dicts(
                family_create_invite_optional_defaults,
                {'sms_phone': PhoneNumber.parse('79991234567'), 'uid': 1234567},
            ),
        ),
        (
            {'sms_phone': '89991234567', 'uid': '1234567', 'sms_phone_country': 'ru'},
            merge_dicts(
                family_create_invite_optional_defaults,
                {'sms_phone': PhoneNumber.parse('79991234567'), 'sms_phone_country': 'ru', 'uid': 1234567},
            ),
        ),
        (
            {'sms_phone': '8-999-123-45-67', 'uid': '1234567', 'sms_phone_country': 'ru'},
            merge_dicts(
                family_create_invite_optional_defaults,
                {'sms_phone': PhoneNumber.parse('79991234567'), 'sms_phone_country': 'ru', 'uid': 1234567},
            ),
        ),
        (
            {'sms_phone': '+79991234567', 'uid': '1234567'},
            merge_dicts(
                family_create_invite_optional_defaults,
                {'sms_phone': PhoneNumber.parse('79991234567'), 'uid': 1234567},
            ),
        ),
        (
            {'sms_phone': '+33-785-5566-26', 'uid': '1234567'},
            merge_dicts(
                family_create_invite_optional_defaults,
                {'sms_phone': PhoneNumber.parse('+33785556626'), 'uid': 1234567},
            ),
        ),
        (
            {'sms_phone': '+33-785-5566-26', 'uid': '1234567', 'sms_phone_country': 'fr'},
            merge_dicts(
                family_create_invite_optional_defaults,
                {'sms_phone': PhoneNumber.parse('+33785556626'), 'sms_phone_country': 'fr', 'uid': 1234567},
            ),
        ),
    ])
    def test_family_create_invite_valid(self, params, expect):
        check_equality(FamilyCreateInviteForm(), (params, expect))

    @parameterized.expand([
        (
            {'place_id': 1},
            [{'place_id': 'badtype'}],
        ),
        (
            {'place_id': '1'},
            [{'place_id': 'invalid'}],
        ),
        (
            {'place_id': 'f12345'},
            [{'place_id': 'invalid'}],
        ),
        (
            {'member_uid': 'abcd'},
            [{'member_uid': 'integer'}],
        ),
        (
            {'member_uid': 12345, 'place_id': 'f1:1'},
            [{'form': 'toomany'}],
        ),
        (
            {},
            [{'form': 'toofew'}],
        ),
    ])
    def test_family_remove_member_invalid(self, params, errors):
        self.check_form_errors(FamilyRemoveMemberForm(), params, errors)

    family_remove_member_optional_defaults = dict(
        place_id=None,
        member_uid=None,
        multisession_uid=None,
        uid=None,
    )

    @parameterized.expand([
        (
            {'place_id': 'f1:0'},
            merge_dicts(family_remove_member_optional_defaults, {'place_id': 'f1:0'}),
        ),
        (
            {'place_id': 'f1:10'},
            merge_dicts(family_remove_member_optional_defaults, {'place_id': 'f1:10'}),
        ),
        (
            {'member_uid': 0},
            merge_dicts(family_remove_member_optional_defaults, {'member_uid': 0}),
        ),
        (
            {'member_uid': 12345678},
            merge_dicts(family_remove_member_optional_defaults, {'member_uid': 12345678}),
        ),
        (
            {'member_uid': '0'},
            merge_dicts(family_remove_member_optional_defaults, {'member_uid': 0}),
        ),
        (
            {'member_uid': '12345678'},
            merge_dicts(family_remove_member_optional_defaults, {'member_uid': 12345678}),
        ),
        (
            {'member_uid': '12345678', 'uid': '12345679'},
            merge_dicts(family_remove_member_optional_defaults, {'member_uid': 12345678, 'uid': 12345679}),
        ),
    ])
    def test_family_remove_member_valid(self, params, expect):
        check_equality(FamilyRemoveMemberForm(), (params, expect))
