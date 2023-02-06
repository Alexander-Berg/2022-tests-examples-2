# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.suggest.forms import SuggestLoginForm
from passport.backend.core import validators
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.test.test_utils.utils import with_settings


@with_settings(
    DISPLAY_LANGUAGES=['ru', 'en', 'kz'],
    ALL_SUPPORTED_LANGUAGES={
        'all': ['ru', 'en', 'kz', 'brr'],
        'default': 'ru',
    },
)
class TestConstructLoginForm(unittest.TestCase):
    def test_form(self):
        valid_params = [
            (
                {
                    'first_name': 'qwert',
                    'last_name': u'йцуке',
                    'login': 'bor',
                    'language': 'ru',
                },
                {
                    'first_name': 'qwert',
                    'last_name': u'йцуке',
                    'login': 'bor',
                    'language': 'ru',
                },
            ),
            (
                {
                    'first_name': 'qwert     ',
                    'login': 'bor',
                    'language': 'kz',
                },
                {
                    'first_name': 'qwert',
                    'last_name': None,
                    'login': 'bor',
                    'language': 'kz',
                },
            ),
            (
                {
                    'login': 'bor   ',
                    'language': 'brr',
                },
                {
                    'first_name': None,
                    'last_name': None,
                    'login': 'bor',
                    'language': 'ru',
                },
            ),
            (
                {
                    'first_name': '    qwert\t',
                    'last_name': 'a' * 300,
                },
                {
                    'first_name': 'qwert',
                    'last_name': 'a' * 50,
                    'login': None,
                    'language': None,
                },
            ),
            (
                {
                    'first_name': u'Анна',
                },
                {
                    'first_name': u'Анна',
                    'last_name': None,
                    'login': None,
                    'language': None,
                },
            ),
            (
                {
                    'last_name': u'Васильев',
                },
                {
                    'first_name': None,
                    'last_name': u'Васильев',
                    'login': None,
                    'language': None,
                },
            ),
        ]
        invalid_params = [
            (
                {'language': ' ', 'login': 'test', 'first_name': '', 'last_name': '\n'},
                ['language.empty', 'first_name.empty', 'last_name.empty'],
            ),
            (
                {'language': 'ru'},
                ['form.invalid'],
            ),
            (
                {'login': 'a' * 101},
                ['login.long'],
            ),
        ]
        state = validators.State(mock_env())
        check_form(SuggestLoginForm(), invalid_params, valid_params, state)
