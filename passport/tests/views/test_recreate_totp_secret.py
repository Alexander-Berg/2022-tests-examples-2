# -*- coding: utf-8 -*-
from django.db import DatabaseError
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.passport.faker.fake_passport import (
    FakePassport,
    passport_bundle_api_error_response,
    passport_ok_response,
)
from passport.backend.perimeter_api.perimeter_api.models import TotpUser
from passport.backend.perimeter_api.tests.views.base import BaseViewsTestCase


TEST_SECRET = 'secret'


class TestRecreateTotpSecret(BaseViewsTestCase):
    http_method = 'GET'
    fixtures = ['default.json']

    def setUp(self):
        super(TestRecreateTotpSecret, self).setUp()
        self.pwgen_patch = mock.patch(
            'passport.backend.perimeter_api.perimeter_api.roles_hooks.run_pwgen',
            mock.Mock(return_value=TEST_SECRET),
        )
        self.fake_passport = FakePassport()
        self.patches = [
            self.pwgen_patch,
            self.fake_passport,
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        super(TestRecreateTotpSecret, self).tearDown()

    def test_create_new(self):
        ok_(not TotpUser.objects.filter(username='vasya').exists())
        self.fake_passport.set_response_value(
            'rfc_2fa_enable',
            passport_ok_response(secret=TEST_SECRET),
        )
        response = self.make_request(
            url='/passport/recreate-totp-secret/vasya',
        )
        self.assert_response_ok(
            response,
            {
                'status': 'ok',
                'secret': TEST_SECRET,
            },
        )
        ok_(TotpUser.objects.filter(username='vasya').exists())
        eq_(len(self.fake_passport.requests), 1)

    def test_recreate_existing(self):
        ok_(TotpUser.objects.filter(username='kolya').exists())
        self.fake_passport.set_response_value(
            'rfc_2fa_enable',
            passport_ok_response(secret=TEST_SECRET),
        )
        response = self.make_request(
            url='/passport/recreate-totp-secret/kolya',
        )
        self.assert_response_ok(
            response,
            {
                'status': 'ok',
                'secret': TEST_SECRET,
            },
        )
        ok_(TotpUser.objects.filter(username='kolya').exists())
        eq_(len(self.fake_passport.requests), 1)

    def test_passport_temporary_error(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_enable',
            passport_bundle_api_error_response(error='backend.blackbox_failed'),
        )
        response = self.make_request(
            url='/passport/recreate-totp-secret/vasya',
        )
        self.assert_response_ok(
            response,
            {
                'status': 'error',
                'error': 'passport.failed',
            },
        )
        ok_(not TotpUser.objects.filter(username='vasya').exists())

    def test_passport_permanent_error(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_enable',
            passport_bundle_api_error_response(error='account.without_password'),
        )
        response = self.make_request(
            url='/passport/recreate-totp-secret/vasya',
        )
        self.assert_response_ok(
            response,
            {
                'status': 'error',
                'error': 'passport.permanent_error',
            },
        )
        ok_(not TotpUser.objects.filter(username='vasya').exists())

    def test_database_temporary_error(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_enable',
            passport_ok_response(secret=TEST_SECRET),
        )
        with mock.patch('django.db.backends.utils.CursorWrapper', mock.Mock(side_effect=DatabaseError)):
            response = self.make_request(
                url='/passport/recreate-totp-secret/vasya',
            )
        self.assert_response_ok(
            response,
            {
                'status': 'error',
                'error': 'database.failed',
            },
        )
        ok_(not TotpUser.objects.filter(username='vasya').exists())

    def test_unhandled_error(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_enable',
            passport_ok_response(secret=TEST_SECRET),
        )
        with mock.patch('django.db.backends.utils.CursorWrapper', mock.Mock(side_effect=SyntaxError)):
            response = self.make_request(
                url='/passport/recreate-totp-secret/vasya',
            )
        self.assert_response_ok(
            response,
            {
                'status': 'error',
                'error': 'exception.unhandled',
            },
        )
        ok_(not TotpUser.objects.filter(username='vasya').exists())
