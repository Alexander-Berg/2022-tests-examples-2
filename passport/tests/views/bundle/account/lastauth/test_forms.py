# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.account.lastauth import forms
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestLastauthForms(unittest.TestCase):
    def test_lastauth_form(self):
        valid_params = [
            (
                {
                    'uid': '123',
                },
                {
                    'uid': 123,
                    'enabled_2fa_track_id': None,
                },
            ),
            (
                {
                    'uid': '123',
                    'enabled_2fa_track_id': None,
                },
                {
                    'uid': 123,
                    'enabled_2fa_track_id': None,
                },
            ),
            (
                {},
                {
                    'uid': None,
                    'enabled_2fa_track_id': None,
                },
            ),
        ]

        invalid_params = [
            (
                {
                    'uid': '',
                },
                ['uid.empty'],
            ),
            (
                {
                    'uid': 'bla',
                    'enabled_2fa_track_id': 'bla',
                },
                ['uid.invalid', 'enabled_2fa_track_id.invalid'],
            ),
        ]

        check_form(forms.LastauthForm(), invalid_params, valid_params, None)
