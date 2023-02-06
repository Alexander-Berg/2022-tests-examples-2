# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.auth.sso import forms
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestForms(unittest.TestCase):
    def test_submit_form(self):
        invalid_params = [
            (
                {
                    'code_challenge': 'abc',
                },
                [
                    'form.invalid',
                ],
            ),
            (
                {
                    'code_challenge_method': 'S256',
                },
                [
                    'form.invalid',
                ],
            ),
            (
                {
                    'code_challenge': 'abc',
                    'code_challenge_method': 'S257',
                },
                [
                    'code_challenge_method.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {},
                {
                    'code_challenge': None,
                    'code_challenge_method': None,
                },
            ),
            (
                {
                    'code_challenge': 'abc',
                    'code_challenge_method': 'S256',
                },
                {
                    'code_challenge': 'abc',
                    'code_challenge_method': 'S256',
                },
            ),
        ]

        check_form(forms.SubmitForm(), invalid_params, valid_params, None)

    def test_commit_form(self):
        invalid_params = [
            (
                {
                    'relay_state': '',
                    'saml_response': '',
                },
                [
                    'saml_response.empty',
                    'relay_state.empty',
                ],
            ),
            (
                {
                    'relay_state': '123',
                    'saml_response': '***',
                },
                ['saml_response.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'relay_state': 'any',
                    'saml_response': '0KbQvtC5INC20LjQsiE=',
                },
                {
                    'relay_state': 'any',
                    'saml_response': '0KbQvtC5INC20LjQsiE=',
                },
            ),
            (
                {
                    'relay_state': '   any ',
                    'saml_response': '  0KbQvtC5INC20LjQsiE=   ',
                },
                {
                    'relay_state': 'any',
                    'saml_response': '0KbQvtC5INC20LjQsiE=',
                },
            ),
        ]

        check_form(forms.CommitForm(), invalid_params, valid_params, None)

    def test_logout_federal_form(self):
        invalid_params = [
            (
                {
                    'relay_state': '',
                    'saml_request': '',
                },
                [
                    'saml_request.empty',
                    'relay_state.empty',
                ],
            ),
            (
                {
                    'saml_request': '***',
                },
                ['saml_request.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'relay_state': 'any',
                    'saml_request': '0KbQvtC5INC20LjQsiE=',
                },
                {
                    'relay_state': 'any',
                    'saml_request': '0KbQvtC5INC20LjQsiE=',
                },
            ),
            (
                {
                    'saml_request': '0KbQvtC5INC20LjQsiE=',
                },
                {
                    'relay_state': None,
                    'saml_request': '0KbQvtC5INC20LjQsiE=',
                },
            ),
            (
                {
                    'relay_state': '   any ',
                    'saml_request': '  0KbQvtC5INC20LjQsiE=   ',
                },
                {
                    'relay_state': 'any',
                    'saml_request': '0KbQvtC5INC20LjQsiE=',
                },
            ),
        ]

        check_form(forms.LogoutFederalForm(), invalid_params, valid_params, None)
