# -*- coding: utf8 -*-
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import BaseViewTestCase
from passport.backend.adm_api.tests.views.base_test_data import *
from passport.backend.adm_api.views.account.forms import Sms2FAForm
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_response
from passport.backend.core.builders.passport.faker.fake_passport import (
    passport_bundle_api_error_response,
    passport_ok_response,
)


@with_settings_hosts()
class Sms2FAToggleViewTestCase(BaseViewTestCase):
    path = '/1/account/set_sms_2fa/'
    query_params = {
        'uid': TEST_UID,
        'sms_2fa': 'true',
        'forbid_disabling_sms_2fa': 'true',
    }

    def setUp(self):
        super(Sms2FAToggleViewTestCase, self).setUp()

        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.passport.set_response_value('account_options', passport_ok_response())

    def test_form(self):
        form = Sms2FAForm()
        valid = [
            (
                {
                    'uid': TEST_UID,
                    'sms_2fa': 'true',
                    'forbid_disabling_sms_2fa': 'true',
                    'comment': ' foo bar ',
                },
                {
                    'uid': TEST_UID,
                    'sms_2fa': True,
                    'forbid_disabling_sms_2fa': True,
                    'comment': 'foo bar',
                },
            ),
            (
                {
                    'uid': TEST_UID,
                    'sms_2fa': 'true',
                },
                {
                    'uid': TEST_UID,
                    'sms_2fa': True,
                    'forbid_disabling_sms_2fa': None,
                    'comment': None,
                },
            ),
            (
                {
                    'uid': TEST_UID,
                    'forbid_disabling_sms_2fa': 'true',
                },
                {
                    'uid': TEST_UID,
                    'sms_2fa': None,
                    'forbid_disabling_sms_2fa': True,
                    'comment': None,
                },
            ),
        ]

        for input_params, expected in valid:
            assert form.to_python(input_params, None) == expected

    def test_ok(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.env.passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://127.0.0.1:6000/2/account/{}/options/?consumer=adminka'.format(TEST_UID),
            post_args=dict(
                sms_2fa_on=1,
                forbid_disabling_sms_2fa=1,
                admin_name='admin',
                comment='no comment',
            ),
        )

    def test_ok_disable_sms_2fa(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=dict(self.query_params, sms_2fa='false', forbid_disabling_sms_2fa='false'),
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.env.passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://127.0.0.1:6000/2/account/{}/options/?consumer=adminka'.format(TEST_UID),
            post_args=dict(
                sms_2fa_on=0,
                forbid_disabling_sms_2fa=0,
                admin_name='admin',
                comment='no comment',
            ),
        )

    def test_ok_with_comment(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=dict(self.query_params, comment='some comment'),
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.env.passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://127.0.0.1:6000/2/account/{}/options/?consumer=adminka'.format(TEST_UID),
            post_args=dict(
                sms_2fa_on=1,
                forbid_disabling_sms_2fa=1,
                admin_name='admin',
                comment='some comment',
            ),
        )

    def test_no_sms_2fa_and_no_forbid(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['form.invalid'])

    def test_no_uid(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'sms_2fa': 'true', 'forbid_disabling_sms_2fa': 'true'},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['uid.empty'])

    def test_disabled_account(self):
        self.env.passport.set_response_value('account_options', passport_bundle_api_error_response('account.disabled'))
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['account.disabled'])

    def test_account_not_found(self):
        self.env.passport.set_response_value('account_options', passport_bundle_api_error_response('account.not_found'))
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['account.not_found'])
