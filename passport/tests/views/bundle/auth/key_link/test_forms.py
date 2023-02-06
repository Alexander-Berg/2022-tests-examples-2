# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.auth.key_link.forms import SubmitKeyLinkForm

from .base_test_data import (
    TEST_PERSISTENT_TRACK_ID,
    TEST_PERSISTENT_TRACK_KEY,
    TEST_UID,
)


class TestForms(unittest.TestCase):
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
                {'secret_key': TEST_PERSISTENT_TRACK_KEY},
                {
                    'secret_key': {
                        'track_key': TEST_PERSISTENT_TRACK_KEY,
                        'uid': int(TEST_UID, 16),
                        'track_id': TEST_PERSISTENT_TRACK_ID,
                    },
                },
            ),
        ]

        check_form(SubmitKeyLinkForm(), invalid_params, valid_params)
