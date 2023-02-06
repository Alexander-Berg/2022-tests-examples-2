# -*- coding: utf-8 -*-
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
from passport.backend.perimeter_api.perimeter_api.models import (
    LongUser,
    MDMUser,
    MotpUser,
    TotpUser,
)
from passport.backend.perimeter_api.tests.views.base import (
    BaseViewsTestCase,
    IDMAuthTests,
)


TEST_PASSWORD = 'pass'
TEST_PIN = 1234
TEST_SECRET = 'secret'


class TestAddRole(BaseViewsTestCase, IDMAuthTests):
    default_url = '/dostup/add-role/'
    http_method = 'POST'
    default_http_args = {
        'fields': 'null',
    }
    fixtures = ['default.json']

    def setUp(self):
        super(TestAddRole, self).setUp()
        self.pwgen_patch = mock.patch(
            'passport.backend.perimeter_api.perimeter_api.roles_hooks.run_pwgen',
            mock.Mock(return_value=TEST_PASSWORD),
        )
        self.randint_patch = mock.patch('random.randint', mock.Mock(return_value=TEST_PIN))
        self.fake_passport = FakePassport()
        self.patches = [
            self.pwgen_patch,
            self.randint_patch,
            self.fake_passport,
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        super(TestAddRole, self).tearDown()

    def test_long_ok(self):
        response = self.make_request(
            query_args={
                'login': 'petya',
                'role': '{"role": "long"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 0,
                'context': {
                    'password': TEST_PASSWORD,
                },
            },
        )
        ok_(LongUser.objects.filter(username='petya').exists())

    def test_long_role_exists(self):
        response = self.make_request(
            query_args={
                'login': 'vasya',
                'role': '{"role": "long"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 400,
                'fatal': 'Пользователь уже имеет такую роль',
            },
        )
        ok_(LongUser.objects.filter(username='vasya').exists())

    def test_mdm_ok(self):
        response = self.make_request(
            query_args={
                'login': 'petya',
                'role': '{"role": "mdm"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 0,
                'context': {},
            },
        )
        ok_(MDMUser.objects.filter(username='petya').exists())

    def test_mdm_role_exists(self):
        response = self.make_request(
            query_args={
                'login': 'vasya',
                'role': '{"role": "mdm"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 400,
                'fatal': 'Пользователь уже имеет такую роль',
            },
        )
        ok_(MDMUser.objects.filter(username='vasya').exists())

    def test_motp_ok(self):
        response = self.make_request(
            query_args={
                'login': 'vasya',
                'role': '{"role": "motp"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 0,
                'context': {
                    'initsecret': TEST_PASSWORD,
                    'pin': TEST_PIN,
                },
            },
        )
        ok_(MotpUser.objects.filter(username='vasya').exists())

    def test_motp_role_exists(self):
        response = self.make_request(
            query_args={
                'login': 'petya',
                'role': '{"role": "motp"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 400,
                'fatal': 'Пользователь уже имеет такую роль',
            },
        )
        ok_(MotpUser.objects.filter(username='petya').exists())

    def test_totp_ok(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_enable',
            passport_ok_response(secret=TEST_SECRET),
        )
        response = self.make_request(
            query_args={
                'login': 'vasya',
                'role': '{"role": "totp"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 0,
                'context': {
                    'secret': TEST_SECRET,
                },
            },
        )
        ok_(TotpUser.objects.filter(username='vasya').exists())
        eq_(len(self.fake_passport.requests), 1)

    def test_totp_passport_temporary_error(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_enable',
            passport_bundle_api_error_response(error='backend.blackbox_failed'),
        )
        response = self.make_request(
            query_args={
                'login': 'vasya',
                'role': '{"role": "totp"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 500,
                'error': 'PassportTemporaryError',
            },
        )
        ok_(not TotpUser.objects.filter(username='vasya').exists())

    def test_totp_passport_permanent_error(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_enable',
            passport_bundle_api_error_response(error='account.without_password'),
        )
        response = self.make_request(
            query_args={
                'login': 'vasya',
                'role': '{"role": "totp"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 500,
                'error': 'account.without_password',
            },
        )
        ok_(not TotpUser.objects.filter(username='vasya').exists())

    def test_totp_role_exists(self):
        response = self.make_request(
            query_args={
                'login': 'kolya',
                'role': '{"role": "totp"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 400,
                'fatal': 'Пользователь уже имеет такую роль',
            },
        )
        ok_(TotpUser.objects.filter(username='kolya').exists())
        eq_(len(self.fake_passport.requests), 0)

    def test_unknown_role(self):
        response = self.make_request(
            query_args={
                'login': 'vasya',
                'role': '{"role": "unknown"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 400,
                'fatal': 'Нет такой роли',
            },
        )
