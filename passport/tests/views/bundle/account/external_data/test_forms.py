# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.account.external_data import forms
from passport.backend.core.test.test_utils.utils import with_settings


@with_settings(
    PORTAL_LANGUAGES=('ru', 'en'),
)
class TestForms(unittest.TestCase):
    def test_afisha_order_info_form(self):
        invalid_params = [
            (
                {},
                ['order_id.empty'],
            ),
            (
                {
                    'order_id': '  ',
                },
                ['order_id.empty'],
            ),
            (
                {
                    'order_id': 'a' * 31,
                },
                ['order_id.short'],
            ),
            (
                {
                    'order_id': 'a' * 101,
                },
                ['order_id.long'],
            ),
            (
                {
                    'order_id': u'кириллица' + 'a' * 32,
                },
                ['order_id.invalid'],
            ),
        ]
        valid_params = [
            (
                {
                    'order_id': 'a' * 32,
                },
                {
                    'order_id': 'a' * 32,
                },
            ),
        ]

        check_form(forms.BiletApiOrderInfoForm(), invalid_params, valid_params, None)

    def test_pagination_form(self):
        invalid_params = [
            (
                {'page': 'foo', 'page_size': 'foo'},
                ['page.invalid', 'page_size.invalid'],
            ),
            (
                {'page': '0', 'page_size': '0'},
                ['page.invalid', 'page_size.invalid'],
            ),
            (
                {'page': '1', 'page_size': '101'},
                ['page_size.invalid'],
            ),
        ]
        valid_params = [
            (
                {},
                {'page': 1, 'page_size': 10},
            ),
            (
                {'page': '2', 'page_size': '11'},
                {'page': 2, 'page_size': 11},
            ),
            (
                {'page': '99', 'page_size': '100'},
                {'page': 99, 'page_size': 100},
            ),
        ]

        check_form(forms.PaginationForm(), invalid_params, valid_params, None)

    def test_afisha_favourites_form(self):
        invalid_params = [
            (
                {'page': 'foo', 'page_size': 'foo', 'period': 'foo'},
                ['page.invalid', 'page_size.invalid', 'period.invalid'],
            ),
            (
                {'page': '0', 'page_size': '0', 'period': 0},
                ['page.invalid', 'page_size.invalid', 'period.invalid'],
            ),
        ]
        valid_params = [
            (
                {},
                {'page': 1, 'page_size': 10, 'period': 180},
            ),
            (
                {'page': '2', 'page_size': '11', 'period': '7'},
                {'page': 2, 'page_size': 11, 'period': 7},
            ),
        ]

        check_form(forms.AfishaFavouritesForm(), invalid_params, valid_params, None)

    def test_bookmark_info_form(self):
        invalid_params = [
            (
                {},
                ['uri.empty', 'language.empty'],
            ),
            (
                {'uri': '', 'language': ''},
                ['uri.empty', 'language.empty'],
            ),
            (
                {'uri': ' \t', 'language': 'tz'},
                ['uri.empty', 'language.invalid'],
            ),
        ]

        valid_params = [
            (
                {'uri': 'foo', 'language': 'ru'},
                {'uri': 'foo', 'language': 'ru'},
            ),
            (
                {'uri': 'foo://bar.baz?org=123 ', 'language': 'en'},
                {'uri': 'foo://bar.baz?org=123', 'language': 'en'},
            ),
        ]

        check_form(forms.MapsBookmarkInfoForm(), invalid_params, valid_params, None)
