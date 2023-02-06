# -*- coding: utf-8 -*-
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


class TestRemoveRole(BaseViewsTestCase, IDMAuthTests):
    default_url = '/dostup/remove-role/'
    http_method = 'POST'
    default_http_args = {
        'data': 'null',
    }
    fixtures = ['default.json']

    def setUp(self):
        super(TestRemoveRole, self).setUp()
        self.fake_passport = FakePassport()
        self.fake_passport.start()

    def tearDown(self):
        self.fake_passport.stop()
        super(TestRemoveRole, self).tearDown()

    def test_long_ok(self):
        response = self.make_request(
            query_args={
                'login': 'vasya',
                'role': '{"role": "long"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 0,
            },
        )
        ok_(not LongUser.objects.filter(username='vasya').exists())

    def test_mdm_ok(self):
        response = self.make_request(
            query_args={
                'login': 'vasya',
                'role': '{"role": "mdm"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 0,
            },
        )
        ok_(not MDMUser.objects.filter(username='vasya').exists())

    def test_motp_ok(self):
        response = self.make_request(
            query_args={
                'login': 'petya',
                'role': '{"role": "motp"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 0,
            },
        )
        ok_(not MotpUser.objects.filter(username='petya').exists())

    def test_totp_ok(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_disable',
            passport_ok_response(),
        )
        response = self.make_request(
            query_args={
                'login': 'kolya',
                'role': '{"role": "totp"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 0,
            },
        )
        ok_(not TotpUser.objects.filter(username='kolya').exists())
        eq_(len(self.fake_passport.requests), 1)

    def test_totp_passport_temporary_error(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_disable',
            passport_bundle_api_error_response(error='backend.blackbox_failed'),
        )
        response = self.make_request(
            query_args={
                'login': 'kolya',
                'role': '{"role": "totp"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 0,
            },
        )
        ok_(not TotpUser.objects.filter(username='kolya').exists())

    def test_totp_passport_permanent_error(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_disable',
            passport_bundle_api_error_response(error='exception.unhandled'),
        )
        response = self.make_request(
            query_args={
                'login': 'kolya',
                'role': '{"role": "totp"}',
            },
        )
        self.assert_response_ok(
            response,
            {
                'code': 0,
            },
        )
        ok_(not TotpUser.objects.filter(username='kolya').exists())

    def test_totp_not_added(self):
        self.fake_passport.set_response_value(
            'rfc_2fa_disable',
            passport_bundle_api_error_response(error='action.not_required'),
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
            },
        )
        ok_(not TotpUser.objects.filter(username='vasya').exists())
        eq_(len(self.fake_passport.requests), 1)

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
