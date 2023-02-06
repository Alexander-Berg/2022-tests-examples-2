# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.auth.forwarding.forms import (
    AUTH_LINK_PLACEHOLDER,
    CommitForm,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestForms(unittest.TestCase):
    def test_commit_form(self):
        invalid_params = [
            (
                {},
                ['template.empty'],
            ),
            (
                {
                    'template': '',
                    'retpath': '',
                },
                [
                    'template.empty',
                    'retpath.empty',
                ],
            ),
            (
                {'template': '1' * (len(AUTH_LINK_PLACEHOLDER) - 1)},
                ['template.short'],
            ),
            (
                {'template': '1' * len(AUTH_LINK_PLACEHOLDER)},
                ['template.invalid'],
            ),
            (
                {'template': '%s%s' % (AUTH_LINK_PLACEHOLDER, AUTH_LINK_PLACEHOLDER)},
                ['template.invalid'],
            ),
            (
                {'template': '1' * 901},
                ['template.long'],
            ),
            (
                {
                    'template': AUTH_LINK_PLACEHOLDER,
                    'retpath': 'bad',
                },
                ['retpath.invalid'],
            ),
        ]

        valid_params = [
            (
                {'template': AUTH_LINK_PLACEHOLDER},
                {
                    'template': AUTH_LINK_PLACEHOLDER,
                    'retpath': None,
                },
            ),
            (
                {'template': 'x' * (900 - len(AUTH_LINK_PLACEHOLDER)) + AUTH_LINK_PLACEHOLDER},
                {
                    'template': 'x' * (900 - len(AUTH_LINK_PLACEHOLDER)) + AUTH_LINK_PLACEHOLDER,
                    'retpath': None,
                },
            ),
            (
                {
                    'template': u'  Ссылка: %s   ' % AUTH_LINK_PLACEHOLDER,
                    'retpath': '  https://yandex.ru  ',
                },
                {
                    'template': u'Ссылка: %s' % AUTH_LINK_PLACEHOLDER,
                    'retpath': 'https://yandex.ru',
                },
            ),
        ]

        check_form(CommitForm(), invalid_params, valid_params)
