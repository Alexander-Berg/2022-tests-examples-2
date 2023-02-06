# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.billing import forms
from six.moves import xmlrpc_client


class TestForms(unittest.TestCase):
    def test_create_binding_form(self):
        valid_params = [
            (
                {},
                {
                    'return_path': None,
                    'back_url': None,
                    'timeout': None,
                    'currency': None,
                    'region_id': None,
                    'lang': None,
                    'template_tag': None,
                    'domain_sfx': None,
                },
            ),
            (
                {
                    'return_path': 'abcd',
                    'back_url': 'efgh',
                    'timeout': xmlrpc_client.MAXINT,
                    'currency': 'rur',
                    'region_id': xmlrpc_client.MININT,
                    'lang': 'ru',
                    'template_tag': 'mobile',
                    'domain_sfx': 'com.tr',
                },
                {
                    'return_path': 'abcd',
                    'back_url': 'efgh',
                    'timeout': xmlrpc_client.MAXINT,
                    'currency': 'rur',
                    'region_id': xmlrpc_client.MININT,
                    'lang': 'ru',
                    'template_tag': 'mobile',
                    'domain_sfx': 'com.tr',
                },
            ),
        ]

        invalid_params = [
            (
                {'timeout': -1},
                ['timeout.invalid'],
            ),
            (
                {'timeout': xmlrpc_client.MAXINT + 1},
                ['timeout.invalid'],
            ),
            (
                {'region_id': xmlrpc_client.MININT - 1},
                ['region_id.invalid'],
            ),
            (
                {'region_id': xmlrpc_client.MAXINT + 1},
                ['region_id.invalid'],
            ),
        ]

        check_form(forms.CreateBindingForm(), invalid_params, valid_params, None)
