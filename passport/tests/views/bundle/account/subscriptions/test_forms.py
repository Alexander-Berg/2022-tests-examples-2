# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.account.subscriptions import (
    SubscribeForm,
    UnsubscribeCommitForm,
    UnsubscribeSubmitForm,
)
from passport.backend.core import validators
from passport.backend.core.services import get_service
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.test.test_utils.utils import with_settings


@with_settings()
class TestSubscriptionsForms(unittest.TestCase):
    def test_subscribe_form(self):
        valid_params = [
            (
                {
                    'service': 'mail',
                },
                {
                    'service': get_service(slug='mail'),
                    'retpath': None,
                },
            ),
            (
                {
                    'service': 'bad-service',
                    'retpath': 'http://yandex.ru',
                },
                {
                    'service': None,
                    'retpath': 'http://yandex.ru',
                },
            ),
        ]
        invalid_params = [
            (
                {},
                ['service.empty'],
            ),
            (
                {
                    'service': ' ',
                },
                ['service.empty'],
            ),
            (
                {
                    'service': 'mail',
                    'retpath': 'retpath-baad',
                },
                ['retpath.invalid'],
            ),
        ]
        state = validators.State(mock_env())
        check_form(SubscribeForm(), invalid_params, valid_params, state)

    def test_unsubscribe_submit_form(self):
        valid_params = [
            (
                {
                    'service': 'mail',
                },
                {
                    'service': get_service(slug='mail'),
                    'retpath': None,
                },
            ),
            (
                {
                    'service': 'music',
                    'retpath': 'http://yandex.ru',
                },
                {
                    'service': get_service(slug='music'),
                    'retpath': 'http://yandex.ru',
                },
            ),
        ]

        invalid_params = [
            (
                {},
                ['service.empty'],
            ),
            (
                {
                    'service': 'bad-service',
                },
                ['service.invalid'],
            ),
        ]

        state = validators.State(mock_env())
        check_form(UnsubscribeSubmitForm(), invalid_params, valid_params, state)

    def test_unsubscribe_commit_form(self):
        valid_params = [
            (
                {'password': '  qwerty'},
                {'password': '  qwerty'},
            ),
        ]

        invalid_params = [
            (
                {},
                ['password.empty'],
            ),
            (
                {'password': ''},
                ['password.empty'],
            ),
        ]

        state = validators.State(mock_env())
        check_form(UnsubscribeCommitForm(), invalid_params, valid_params, state)
