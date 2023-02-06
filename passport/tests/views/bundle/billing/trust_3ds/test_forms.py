# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.billing.trust_3ds import forms
from passport.backend.core.test.test_utils import with_settings


@with_settings(
    RETPATH_BAD_SYMBOLS=[],
)
class TestForms(unittest.TestCase):
    def test_submit_form(self):
        invalid_params = [
            (
                {'frontend_url': 'foo'},
                ['frontend_url.invalid'],
            ),
        ]

        valid_params = [
            (
                {},
                {
                    'frontend_url': None,
                    'use_new_trust_form': False,
                    'use_mobile_layout': False,
                },
            ),
            (
                {
                    'use_new_trust_form': 'false',
                    'use_mobile_layout': '0',
                },
                {
                    'frontend_url': None,
                    'use_new_trust_form': False,
                    'use_mobile_layout': False,
                },
            ),
            (
                {
                    'frontend_url': 'https://yandex.ru',
                    'use_new_trust_form': 'true',
                    'use_mobile_layout': 'yes',
                },
                {
                    'frontend_url': 'https://yandex.ru',
                    'use_new_trust_form': True,
                    'use_mobile_layout': True,
                },
            ),
        ]

        check_form(forms.Trust3DSSubmitForm(), invalid_params, valid_params, None)
