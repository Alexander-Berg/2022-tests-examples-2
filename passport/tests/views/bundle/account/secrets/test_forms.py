# -*- coding: utf-8 -*-
from base64 import b64encode
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.account.secrets import forms
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_KEY = 'key'
TEST_KEY_B64 = b64encode(TEST_KEY)
TEST_KEY_ID = 'key_id'
TEST_KEY_ID_B64 = b64encode(TEST_KEY_ID)


@with_settings_hosts()
class TestSecretsForms(unittest.TestCase):
    def test_write_browser_key_form(self):
        valid_params = [
            (
                {'browser_key': TEST_KEY_B64},
                {'browser_key': TEST_KEY, 'append': False},
            ),
            (
                {'browser_key': TEST_KEY_B64, 'append': 'false'},
                {'browser_key': TEST_KEY, 'append': False},
            ),
            (
                {'browser_key': TEST_KEY_B64, 'append': 'true'},
                {'browser_key': TEST_KEY, 'append': True},
            ),
        ]

        invalid_params = [
            (
                {},
                ['browser_key.empty'],
            ),
            (
                {'browser_key': '  ', 'append': ' '},
                ['browser_key.empty', 'append.empty'],
            ),
            (
                {'browser_key': 'a' * 65},
                ['browser_key.long'],
            ),
            (
                {'browser_key': TEST_KEY_B64, 'append': 'foo'},
                ['append.invalid'],
            ),
        ]

        check_form(forms.SecretsWriteBrowserKeyForm(), invalid_params, valid_params, None)

    def test_write_passman_recovery_key_form(self):
        valid_params = [
            (
                {'key_id': TEST_KEY_ID_B64, 'recovery_key': TEST_KEY_B64},
                {'key_id': TEST_KEY_ID, 'recovery_key': TEST_KEY, 'uid': None},
            ),
            (
                {'key_id': TEST_KEY_ID_B64, 'recovery_key': TEST_KEY_B64, 'uid': '123'},
                {'key_id': TEST_KEY_ID, 'recovery_key': TEST_KEY, 'uid': 123},
            ),
        ]

        invalid_params = [
            (
                {},
                ['key_id.empty', 'recovery_key.empty'],
            ),
            (
                {'key_id': '  ', 'recovery_key': ' '},
                ['key_id.empty', 'recovery_key.empty'],
            ),
            (
                {'key_id': 'a' * 101, 'recovery_key': 'a' * 101, 'uid': 'foo'},
                ['key_id.long', 'recovery_key.long', 'uid.invalid'],
            ),
        ]

        check_form(forms.SecretsWritePassmanRecoveryKeyForm(), invalid_params, valid_params, None)
