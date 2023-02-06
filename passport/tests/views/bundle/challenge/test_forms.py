# -*- coding: utf-8 -*-
from unittest import TestCase

from passport.backend.api.test.utils import check_bundle_form
from passport.backend.api.views.bundle.challenge.forms import ChallengeCommitForm


class FormsTestCase(TestCase):

    def test_challenge_commit_form(self):
        invalid = [
            (
                {},
                ['challenge.empty'],
            ),
            (
                {
                    'challenge': '  ',
                    'answer': '  ',
                },
                ['challenge.empty'],
            ),
            (
                {
                    'challenge': 'Rock-paper-scissors-lizard-Spock',
                    'answer': 'Spock',
                },
                ['challenge.invalid'],
            ),
            (
                {
                    'challenge': 'phone',
                },
                ['answer.empty'],
            ),
            (
                {
                    'challenge': 'email',
                    'answer': '  ',
                },
                ['answer.empty'],
            ),
        ]

        valid = [
            (
                {
                    'challenge': 'phone',
                    'answer': '42',
                },
                {
                    'challenge': 'phone',
                    'answer': '42',
                    'can_send_sms': True,
                },
            ),
            (
                {
                    'challenge': 'email',
                    'answer': '???',
                    'can_send_sms': 'false',
                },
                {
                    'challenge': 'email',
                    'answer': '???',
                    'can_send_sms': False,
                },
            ),
            (
                {
                    'challenge': 'phone_confirmation',
                },
                {
                    'challenge': 'phone_confirmation',
                    'answer': None,
                    'can_send_sms': True,
                },
            ),
        ]

        check_bundle_form(
            ChallengeCommitForm(),
            invalid,
            valid,
        )
