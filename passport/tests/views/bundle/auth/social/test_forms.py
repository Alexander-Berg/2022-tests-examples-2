# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.auth.social.forms import (
    NativeStartForm,
    StartForm,
)
from passport.backend.core.services import Service
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.utils.common import merge_dicts


@with_settings(
    ALLOWED_SOCIAL_RETPATH_SCHEMES=['scheme'],
    ALLOWED_SOCIAL_RETPATH_SCHEME_PREFIXES=['prefix'],
)
class TestForms(unittest.TestCase):
    def test_start_form(self):
        invalid_params = [
            (
                {},
                [
                    'retpath.empty',
                ],
            ),
            (
                {
                    'place': 'foo',
                    'retpath': 'badscheme://foo',
                    'code_challenge_method': 'unknown',
                },
                [
                    'place.invalid',
                    'retpath.invalid',
                    'code_challenge_method.invalid',
                ],
            ),
            (
                {
                    'retpath': 'schemebad://foo',
                    'code_challenge_method': 'plain',
                },
                [
                    'retpath.invalid',
                    'code_challenge_method.invalid',
                ],
            ),
            (
                {
                    'retpath': 'http://yandex.ru',
                    'code_challenge_method': 'S256',
                },
                [
                    'form.invalid',
                ],
            ),
            (
                {
                    'retpath': 'http://yandex.ru',
                    'code_challenge': 'foo',
                },
                [
                    'form.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'retpath': 'http://yandex.ru',
                },
                {
                    'application': None,
                    'broker_consumer': None,
                    'code_challenge': None,
                    'code_challenge_method': None,
                    'origin': None,
                    'place': None,
                    'provider': None,
                    'retpath': 'http://yandex.ru',
                    'return_brief_profile': None,
                    'service': None,
                    'process_uuid': None,
                },
            ),
            (
                {
                    'retpath': 'scheme://foo',
                },
                {
                    'application': None,
                    'broker_consumer': None,
                    'code_challenge': None,
                    'code_challenge_method': None,
                    'origin': None,
                    'place': None,
                    'provider': None,
                    'retpath': 'scheme://foo',
                    'return_brief_profile': None,
                    'service': None,
                    'process_uuid': None,
                },
            ),
            (
                {
                    'retpath': 'prefixed://foo',
                },
                {
                    'application': None,
                    'broker_consumer': None,
                    'code_challenge': None,
                    'code_challenge_method': None,
                    'origin': None,
                    'place': None,
                    'provider': None,
                    'retpath': 'prefixed://foo',
                    'return_brief_profile': None,
                    'service': None,
                    'process_uuid': None,
                },
            ),
            (
                {
                    'application': 'app',
                    'broker_consumer': 'mail',
                    'code_challenge': 'challenge*',
                    'code_challenge_method': 'S256',
                    'origin': 'origin*',
                    'place': 'fragment',
                    'provider': 'google',
                    'retpath': 'http://yandex.ru',
                    'return_brief_profile': '1',
                    'service': 'mail',
                    'process_uuid': 'process_uuid',
                },
                {
                    'application': 'app',
                    'broker_consumer': 'mail',
                    'code_challenge': 'challenge*',
                    'code_challenge_method': 'S256',
                    'origin': 'origin*',
                    'place': 'fragment',
                    'provider': 'google',
                    'retpath': 'http://yandex.ru',
                    'return_brief_profile': True,
                    'service': Service.by_slug('mail'),
                    'process_uuid': 'process_uuid',
                },
            ),
        ]

        check_form(StartForm(), invalid_params, valid_params, None)

    def test_native_start_form(self):
        invalid_params = [
            (
                {},
                [
                    'retpath.empty',
                    'broker_consumer.empty',
                    'provider_token.empty',
                ],
            ),
            (
                {
                    'application': 'foo',
                    'provider_token': 'bar',
                    'broker_consumer': 'mail',
                    'place': 'foo',
                    'retpath': 'badscheme://foo',
                },
                [
                    'place.invalid',
                    'retpath.invalid',
                ],
            ),
            (
                {
                    'application': 'foo',
                    'provider_token': 'bar',
                    'broker_consumer': 'mail',
                    'retpath': 'schemebad://foo',
                },
                [
                    'retpath.invalid',
                ],
            ),
            (
                {
                    'provider': 'google',
                    'provider_token': 'bar',
                    'broker_consumer': 'mail',
                    'retpath': 'prefixed://foo',
                },
                [
                    'retpath.invalid',
                ],
            ),
        ]

        default_values = {
            'origin': None,
            'place': None,
            'provider': None,
            'provider_token_secret': None,
            'scope': None,
            'process_uuid': None,
        }

        valid_params = [
            (
                {
                    'application': 'foo',
                    'provider_token': 'bar',
                    'broker_consumer': 'mail',
                    'retpath': 'http://yandex.ru',
                },
                merge_dicts(
                    default_values,
                    {
                        'application': 'foo',
                        'broker_consumer': 'mail',
                        'provider_token': 'bar',
                        'retpath': 'http://yandex.ru',
                    },
                ),
            ),
            (
                {
                    'application': 'foo',
                    'provider_token': 'bar',
                    'broker_consumer': 'mail',
                    'retpath': 'scheme://foo',
                },
                merge_dicts(
                    default_values,
                    {
                        'application': 'foo',
                        'broker_consumer': 'mail',
                        'provider_token': 'bar',
                        'retpath': 'scheme://foo',
                    },
                ),
            ),
            (
                {
                    'application': 'foo',
                    'broker_consumer': 'mail',
                    'origin': 'origin*',
                    'place': 'query',
                    'process_uuid': 'process_uuid',
                    'provider': 'google',
                    'provider_token': 'bar',
                    'provider_token_secret': 'secret*',
                    'retpath': 'scheme://foo',
                    'scope': 'scope*',
                },
                {
                    'application': 'foo',
                    'broker_consumer': 'mail',
                    'origin': 'origin*',
                    'place': 'query',
                    'process_uuid': 'process_uuid',
                    'provider': 'google',
                    'provider_token': 'bar',
                    'provider_token_secret': 'secret*',
                    'retpath': 'scheme://foo',
                    'scope': 'scope*',
                },
            ),
        ]

        check_form(NativeStartForm(), invalid_params, valid_params, None)
