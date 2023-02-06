# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.account.userapprove.forms import (
    UserApproveCommitForm,
    UserApproveSubmitForm,
)
from passport.backend.core import validators
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.test.test_utils.utils import with_settings


@with_settings()
class TestUserApproveForms(unittest.TestCase):
    def test_submit_form(self):
        valid_params = [
            (
                {},
                {
                    'retpath': None,
                },
            ),
            (
                {
                    'retpath': '',
                },
                {
                    'retpath': None,
                },
            ),
            (
                {
                    'retpath': 'http://yandex.ru',
                },
                {
                    'retpath': 'http://yandex.ru',
                },
            ),
            (
                {
                    'retpath': 'retpath-baad',
                },
                {
                    'retpath': None,
                },
            ),
        ]
        state = validators.State(mock_env())
        check_form(UserApproveSubmitForm(), [], valid_params, state)

    def test_commit_form(self):
        valid_params = [
            (
                {
                    'text': 'a' * 20,
                },
                {
                    'retpath': None,
                    'text': 'a' * 20,
                },
            ),
            (
                {
                    'retpath': ' ',
                    'text': u'Фыр-фыр, верните доступ, пожалуйста',
                },
                {
                    'retpath': None,
                    'text': u'Фыр-фыр, верните доступ, пожалуйста',
                },
            ),
            (
                {
                    'retpath': 'http://yandex.ru',
                    'text': '   Фыр-фыр, верните доступ, пожалуйста     ',
                },
                {
                    'retpath': 'http://yandex.ru',
                    'text': u'Фыр-фыр, верните доступ, пожалуйста',
                },
            ),
        ]
        invalid_params = [
            (
                {'text': ' '},
                ['text.empty'],
            ),
            (
                {'text': 123},
                ['text.short']
            ),
            (
                {},
                ['text.empty'],
            ),
        ]
        state = validators.State(mock_env())
        check_form(UserApproveCommitForm(), invalid_params, valid_params, state)
