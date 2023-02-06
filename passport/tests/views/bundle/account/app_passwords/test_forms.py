# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.account.app_passwords import forms


class TestForms(unittest.TestCase):
    def test_app_password_add_form(self):
        invalid_params = [
            (
                {},
                ['uid.empty', 'app_type.empty'],
            ),
            (
                {
                    'uid': '  ',
                    'app_type': '  ',
                    'app_name': '   ',
                },
                ['uid.empty', 'app_type.invalid'],
            ),
            (
                {
                    'uid': 'bla',
                    'app_type': 'bla',
                    'app_name': 'bla',
                },
                ['uid.invalid', 'app_type.invalid'],
            ),
        ]
        valid_params = [
            (
                {
                    'uid': '123',
                    'app_type': 'mail',
                    'app_name': '  Android  ',
                },
                {
                    'uid': 123,
                    'app_type': 'mail',
                    'app_name': 'Android',
                },
            ),
        ]

        check_form(forms.AppPasswordCreateForm(), invalid_params, valid_params, None)
