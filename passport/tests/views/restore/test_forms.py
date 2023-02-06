# -*- coding: utf-8 -*-

from unittest import TestCase

from passport.backend.adm_api.test.utils import check_form
from passport.backend.adm_api.tests.views.restore.data import TEST_RESTORE_ID
from passport.backend.adm_api.views.restore.forms import (
    RestoreSemiAutoAttemptForm,
    RestoreSemiAutoAttemptsForm,
    RestoreSemiAutoSupportDecisionForm,
)
from passport.backend.core.types.restore_id import RestoreId


class RestoreAttemptFormsTestCase(TestCase):

    def test_restore_semi_auto_attempt_form(self):
        invalid_params = [
            ({},
             ['restore_id.empty']),
            ({'restore_id': ''},
             ['restore_id.empty']),
            ({'restore_id': '123,123,123'},
             ['restore_id.invalid']),
        ]

        valid_params = [
            (
                {'restore_id': TEST_RESTORE_ID},
                {
                    'restore_id': RestoreId.from_string(TEST_RESTORE_ID),
                },
            ),
        ]

        check_form(RestoreSemiAutoAttemptForm(), invalid_params, valid_params, None)

    def test_restore_semi_auto_attempts_form(self):
        invalid_params = [
            ({},
             ['form.invalid']),
            ({'restore_id': ''},
             ['restore_id.empty']),
            ({'restore_id': '123,123,123'},
             ['restore_id.invalid']),
            ({'uid': '123,123'},
             ['uid.invalid']),
            ({'uid': '123123', 'restore_id': TEST_RESTORE_ID},
             ['form.invalid']),
        ]

        valid_params = [
            (
                {'restore_id': TEST_RESTORE_ID},
                {
                    'restore_id': RestoreId.from_string(TEST_RESTORE_ID),
                    'uid': None,
                },
            ),
            (
                {'uid': '0'},
                {
                    'restore_id': None,
                    'uid': 0,
                },
            ),
        ]

        check_form(RestoreSemiAutoAttemptsForm(), invalid_params, valid_params, None)

    def test_restore_semi_auto_support_decision_form(self):
        invalid_params = [
            ({},
             ['passed.empty', 'restore_id.empty']),
            ({'restore_id': ''},
             ['passed.empty', 'restore_id.empty']),
            ({'restore_id': '123,123,123', 'passed': 'false'},
             ['restore_id.invalid']),
            ({'passed': '123', 'restore_id': TEST_RESTORE_ID},
             ['passed.invalid']),
            ({'passed': 'yes', 'restore_id': TEST_RESTORE_ID, 'regenerate_link': 'xyz'},
             ['regenerate_link.invalid']),
        ]

        valid_params = [
            (
                {'restore_id': TEST_RESTORE_ID, 'passed': 'yes'},
                {
                    'restore_id': RestoreId.from_string(TEST_RESTORE_ID),
                    'passed': True,
                    'regenerate_link': False,
                },
            ),
            (
                {'restore_id': TEST_RESTORE_ID, 'passed': '1', 'regenerate_link': 'yes'},
                {
                    'restore_id': RestoreId.from_string(TEST_RESTORE_ID),
                    'passed': True,
                    'regenerate_link': True,
                },
            ),
            (
                {'restore_id': TEST_RESTORE_ID, 'passed': '0'},
                {
                    'restore_id': RestoreId.from_string(TEST_RESTORE_ID),
                    'passed': False,
                    'regenerate_link': False,
                },
            ),
        ]

        check_form(RestoreSemiAutoSupportDecisionForm(), invalid_params, valid_params, None)
