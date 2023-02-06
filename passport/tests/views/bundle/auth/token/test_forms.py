# -*- coding: utf-8 -*-
from unittest import TestCase

from passport.backend.api.test.utils import check_bundle_form
from passport.backend.api.views.bundle.auth.token.forms import SubmitForm
from passport.backend.api.views.bundle.constants import X_TOKEN_TYPE
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_RETPATH = 'http://ya.ru'


@with_settings_hosts()
class SubmitFormTestCase(TestCase):

    def test_form(self):
        invalid_params = [
            (
                {},
                ['type.empty', 'retpath.empty'],
            ),
            (
                {
                    'type': '',
                    'retpath': '',
                },
                ['type.empty', 'retpath.empty'],
            ),
            (
                {
                    'type': 'bad-type',
                    'retpath': 'bad-retpath',
                },
                ['type.invalid', 'retpath.invalid'],
            ),
            (
                {
                    'type': '  ',
                    'retpath': 'http://google.com',
                },
                ['type.empty', 'retpath.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'type': X_TOKEN_TYPE,
                    'retpath': TEST_RETPATH,
                },
                {
                    'type': X_TOKEN_TYPE,
                    'retpath': TEST_RETPATH,
                },
            ),
        ]

        check_bundle_form(
            SubmitForm(),
            invalid_params,
            valid_params,
        )
