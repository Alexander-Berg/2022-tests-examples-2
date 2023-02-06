# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.email_validator import forms
from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.validators import State


TEST_ADDRESS = u'test@gmail.com'
TEST_CYRILLIC_ADDRESS = u'тест@гмэйл.ком'
TEST_UID = 12345


class TestForms(unittest.TestCase):

    def setUp(self):
        self.state = State(mock_env(user_ip='127.0.0.1'))

    def tearDown(self):
        del self.state

    def test_ok(self):
        form = forms.AddRPOPForm()

        invalid_params = [
            (
                {},
                [
                    'uid.empty',
                    'email.empty',
                ],
            ),
            (
                {
                    'uid': TEST_UID,
                },
                ['email.empty'],
            ),
            (
                {
                    'email': TEST_ADDRESS,
                },
                ['uid.empty'],
            ),
            (
                {
                    'uid': TEST_ADDRESS,
                    'email': TEST_UID,
                },
                ['uid.invalid', 'email.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'uid': TEST_UID,
                    'email': TEST_ADDRESS,
                },
                {
                    'uid': TEST_UID,
                    'email': TEST_ADDRESS,
                },
            ),
        ]
        check_form(form, invalid_params, valid_params, self.state)
