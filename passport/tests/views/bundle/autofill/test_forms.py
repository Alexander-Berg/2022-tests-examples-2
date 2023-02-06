# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.autofill import forms
from passport.backend.core.test.test_utils.utils import with_settings


@with_settings(
    RETPATH_BAD_SYMBOLS=[],
)
class TestForms(unittest.TestCase):
    def test_validate_partner_form(self):
        invalid_params = [
            (
                {},
                ['partner_id.empty', 'page_url.empty'],
            ),
            (
                {
                    'partner_id': '',
                    'page_url': '',
                },
                ['partner_id.empty', 'page_url.empty'],
            ),
            (
                {
                    'partner_id': 'foo',
                    'page_url': '???',
                },
                ['page_url.invalid'],
            ),
            (
                {
                    'partner_id': 'foo',
                    'page_url': 'https:///path',  # нет хоста
                },
                ['page_url.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'partner_id': 'foo',
                    'page_url': 'https://yandex.ru',
                },
                {
                    'partner_id': 'foo',
                    'page_url': 'https://yandex.ru',
                },
            ),
            (
                {
                    'partner_id': 'foo',
                    'page_url': 'https://host.ru:443/path1/path2?arg=value#fragment',
                },
                {
                    'partner_id': 'foo',
                    'page_url': 'https://host.ru:443/path1/path2?arg=value#fragment',
                },
            ),
            (
                {
                    'partner_id': 'foo',
                    'page_url': u'https://хост.рф:443/путь1/путь2?параметр=значение#фрагмент',
                },
                {
                    'partner_id': 'foo',
                    'page_url': u'https://хост.рф:443/путь1/путь2?параметр=значение#фрагмент',
                },
            ),
        ]

        check_form(forms.ValidatePartnerForm(), invalid_params, valid_params, None)
