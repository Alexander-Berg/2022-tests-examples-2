# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.cookies.forms import Cookie


class TestForms(unittest.TestCase):
    def test_cookie_check(self):
        invalid_params = [
            ({},
             ['cookie.empty']),
            ({'cookie': ''},
             ['cookie.empty']),
            ({'cookie': ' '},
             ['cookie.empty']),
        ]

        valid_params = [
            ({'cookie': 'cookie_value'},
             {'cookie': 'cookie_value'}),
        ]

        check_form(Cookie(), invalid_params, valid_params, None)
