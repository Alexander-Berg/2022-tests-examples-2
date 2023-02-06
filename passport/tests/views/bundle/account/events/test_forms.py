# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.account.events import forms
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts(
    ACCOUNT_EVENTS_MAX_LIMIT=10,
    ACCOUNT_EVENTS_DEFAULT_LIMIT=50,
)
class TestEventsForms(unittest.TestCase):
    def test_events_form(self):
        valid_params = [
            (
                {
                    'uid': '123',
                    'limit': '1',
                    'from_timestamp': '',
                    'hours_limit': 123,
                },
                {
                    'uid': 123,
                    'limit': 1,
                    'from_timestamp': None,
                    'hours_limit': 123,
                },
            ),
            (
                {
                    'uid': '123',
                    'limit': '10',
                },
                {
                    'uid': 123,
                    'limit': 10,
                    'from_timestamp': None,
                    'hours_limit': None,
                },
            ),
            (
                {
                    'limit': 1,
                },
                {
                    'uid': None,
                    'limit': 1,
                    'from_timestamp': None,
                    'hours_limit': None,
                },
            ),
            (
                {
                    'uid': '123',
                },
                {
                    'uid': 123,
                    'limit': 50,
                    'from_timestamp': None,
                    'hours_limit': None,
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
                    'limit': 'bla',
                },
                ['uid.invalid', 'limit.invalid'],
            ),
            (
                {
                    'uid': '-1',
                    'limit': '0',
                },
                ['uid.invalid', 'limit.invalid'],
            ),
            (
                {
                    'uid': '-1',
                    'limit': '11',
                },
                ['uid.invalid', 'limit.invalid'],
            ),
            (
                {
                    'uid': '-1',
                    'from_timestamp': 'bla',
                },
                ['uid.invalid', 'from_timestamp.invalid'],
            ),
            (
                {
                    'uid': '123',
                    'hours_limit': '',
                },
                ['hours_limit.empty'],
            ),
            (
                {
                    'uid': '123',
                    'hours_limit': '0',
                },
                ['hours_limit.invalid'],
            ),
            (
                {
                    'uid': '123',
                    'hours_limit': str(forms.HALF_A_YEAR_IN_HOURS + 1),
                },
                ['hours_limit.invalid'],
            ),
            (
                {
                    'uid': '123',
                    'hours_limit': 'bla',
                },
                ['hours_limit.invalid'],
            ),
        ]

        check_form(forms.EventsForm(), invalid_params, valid_params, None)
