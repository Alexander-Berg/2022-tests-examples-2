# -*- coding: utf-8 -*-
from unittest import TestCase

from passport.backend.api.test.utils import check_bundle_form
from passport.backend.api.views.bundle.auth.oauth.forms import (
    IssueCodeForAMForm,
    OpenAuthorizationForm,
    RecreateKolonkishTokenForm,
)
from passport.backend.api.views.bundle.constants import PDD_PARTNER_TOKEN_TYPE
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_UID = 123
TEST_RETPATH = 'http://ya.ru'


@with_settings_hosts()
class OpenAuthorizationFormTestCase(TestCase):

    def test_form(self):
        invalid = [
            (
                {
                    'type': '',
                    'retpath': '',
                },
                ['type.empty'],
            ),
            (
                {
                    'type': 'bad-type',
                },
                ['type.invalid'],
            ),
        ]

        valid = [
            (
                {
                    'type': PDD_PARTNER_TOKEN_TYPE,
                    'retpath': TEST_RETPATH,
                },
                {
                    'type': PDD_PARTNER_TOKEN_TYPE,
                    'retpath': TEST_RETPATH,
                },
            ),
            (
                {
                    'type': PDD_PARTNER_TOKEN_TYPE,
                },
                {
                    'type': PDD_PARTNER_TOKEN_TYPE,
                    'retpath': None,
                },
            ),
        ]

        check_bundle_form(
            OpenAuthorizationForm(),
            invalid,
            valid,
        )


class IssueCodeForAMFormTestCase(TestCase):
    def test_form(self):
        invalid = [
            (
                {
                    'client_id': 'foo',
                    'client_secret': '',
                },
                ['form.invalid'],
            ),
            (
                {
                    'client_id': '',
                    'client_secret': 'bar',
                },
                ['form.invalid'],
            ),
        ]

        valid = [
            (
                {},
                {
                    'client_id': None,
                    'client_secret': None,
                    'uid': None,
                },
            ),
            (
                {
                    'client_id': '',
                    'client_secret': '',
                    'uid': '',
                },
                {
                    'client_id': None,
                    'client_secret': None,
                    'uid': None,
                },
            ),
            (
                {
                    'client_id': ' ',
                    'client_secret': ' ',
                    'uid': ' ',
                },
                {
                    'client_id': None,
                    'client_secret': None,
                    'uid': None,
                },
            ),
            (
                {
                    'client_id': 'foo',
                    'client_secret': 'bar',
                    'uid': '1',
                },
                {
                    'client_id': 'foo',
                    'client_secret': 'bar',
                    'uid': 1,
                },
            ),
        ]

        check_bundle_form(
            IssueCodeForAMForm(),
            invalid,
            valid,
        )


class RecreateKolonkishTokenTestCase(TestCase):
    def test_form(self):
        invalid = [
            (
                {},
                ['uid.empty'],
            ),
            (
                {
                    'uid': 'foo',
                },
                ['uid.invalid'],
            ),
            (
                {'uid': ''},
                ['uid.empty'],
            ),
            (
                {
                    'uid': str(TEST_UID),
                    'device_id': '12345',  # len(device_id) должна быть >= 6, чтобы быть валидной
                },
                [
                    'device_id.invalid',
                ],
            ),
            (
                {
                    'uid': str(TEST_UID),
                    'device_id': 'a' * 51,  # len(device_id) должна быть <= 50, чтобы быть валидной
                    'device_name': 'a' * 101,  # len(device_name) <= 100
                },
                [
                    'device_id.invalid',
                    'device_name.long',
                ],
            ),
        ]

        valid = [
            (
                {
                    'uid': str(TEST_UID),
                },
                {
                    'uid': TEST_UID,
                    'device_id': None,
                    'device_name': None,
                },
            ),
            (
                {
                    'uid': str(TEST_UID),
                    'device_id': '  foobar  ',
                    'device_name': '  bar  ',
                },
                {
                    'uid': TEST_UID,
                    'device_id': 'foobar',
                    'device_name': 'bar',
                },
            ),
            (
                {
                    'uid': str(TEST_UID),
                    'device_id': 'foobar',
                },
                {
                    'uid': TEST_UID,
                    'device_id': 'foobar',
                    'device_name': None,
                },
            ),
            (
                {
                    'uid': str(TEST_UID),
                    'device_name': 'bar',
                },
                {
                    'uid': TEST_UID,
                    'device_id': None,
                    'device_name': 'bar',
                },
            ),
            (
                {
                    'uid': str(TEST_UID),
                    'device_id': 'a' * 6,
                    'device_name': '',
                },
                {
                    'uid': TEST_UID,
                    'device_id': 'a' * 6,
                    'device_name': None,
                },
            ),
            (
                {
                    'uid': str(TEST_UID),
                    'device_id': 'a' * 6,
                    'device_name': 'a',
                },
                {
                    'uid': TEST_UID,
                    'device_id': 'a' * 6,
                    'device_name': 'a',
                },
            ),
            (
                {
                    'uid': str(TEST_UID),
                    'device_id': 'a' * 50,
                    'device_name': 'a' * 100,
                },
                {
                    'uid': TEST_UID,
                    'device_id': 'a' * 50,
                    'device_name': 'a' * 100,
                },
            ),
        ]

        check_bundle_form(
            RecreateKolonkishTokenForm(),
            invalid,
            valid,
        )
