# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.track.forms import InitializeTrackForm
from passport.backend.core.test.test_utils.utils import with_settings


@with_settings(DELETED_TRACK_TYPES=())
class TestForms(unittest.TestCase):
    def test_initialize_track_form(self):
        invalid_params = [
            (
                {
                    'track_type': 'foo',
                    'process_name': 'spam',
                    'uid': 'bar',
                },
                [
                    'track_type.invalid',
                    'process_name.invalid',
                    'uid.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {},
                {
                    'track_type': 'authorize',
                    'uid': None,
                    'process_name': None,
                },
            ),
            (
                {
                    'track_type': 'register',
                    'process_name': 'account_delete_v2_process',
                    'uid': '123',
                },
                {
                    'track_type': 'register',
                    'process_name': 'account_delete_v2_process',
                    'uid': 123,
                },
            ),
        ]

        check_form(InitializeTrackForm(), invalid_params, valid_params, None)
