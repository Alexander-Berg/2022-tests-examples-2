# -*- coding: utf-8 -*-
import base64
import json
from time import time

from django.test.utils import override_settings
import mock
from nose.tools import eq_
from passport.backend.core.builders.blackbox import BlackboxInvalidParamsError
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.tvm import (
    TVM_STATUS_INVALID_CREDENTIALS,
    TVMTemporaryError,
)
from passport.backend.core.builders.tvm.faker import tvm_error_response
from passport.backend.oauth.api.tests.old.issue_token.base import (
    BaseIssueTokenTestCase,
    CommonIssueTokenTests,
)
from passport.backend.oauth.core.test.base_test_data import TEST_LOGIN
from passport.backend.oauth.core.test.utils import assert_params_in_tskv_log_entry


TEST_PUBLIC_CERT = base64.urlsafe_b64encode(b'some-cert').decode()


@override_settings(ALLOW_GRANT_TYPE_SSH_KEY=True)
class TestIssueTokenBySshKey(BaseIssueTokenTestCase, CommonIssueTokenTests):
    grant_type = 'ssh_key'

    def setUp(self):
        super(TestIssueTokenBySshKey, self).setUp()
        self.fake_tvm.set_response_value(
            'verify_ssh',
            json.dumps({'status': 'OK', 'fingerprint': 'fp'}),
        )

    def credentials(self):
        return {
            'ts': int(time()),
            'ssh_sign': 'foo',
            'uid': self.uid,
        }

    def assert_statbox_ok(self):
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            dict(ssh_key_fingerprint='fp'),
        )

    def test_credentials_missing(self):
        # оверрайдим тест из миксина
        for key in ['ts', 'ssh_sign']:
            rv = self.make_request(expected_status=400, exclude=[key])
            self.assert_error(rv, error='invalid_request', error_description='%s not in POST' % key)

    def test_uid_and_login_missing(self):
        rv = self.make_request(expected_status=400, exclude=['uid'])
        self.assert_error(rv, error='invalid_request', error_description='uid or login not in POST')

    def test_ok_with_public_cert(self):
        rv = self.make_request(public_cert=TEST_PUBLIC_CERT)
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()
        self.fake_tvm.requests[0].assert_post_data_contains({'public_cert': TEST_PUBLIC_CERT})

    def test_ok_with_login(self):
        rv = self.make_request(login=TEST_LOGIN, exclude=['uid'])
        self.assert_token_response_ok(rv)
        self.assert_historydb_ok(rv)
        self.assert_statbox_ok()
        self.fake_tvm.requests[0].assert_post_data_contains({'login': TEST_LOGIN})

    def test_both_login_and_uid_present(self):
        rv = self.make_request(expected_status=400, login=TEST_LOGIN)
        self.assert_error(
            rv,
            error='invalid_request',
            error_description='uid and login are mutually exclusive: only one can be passed',
        )

    def test_uid_not_integer(self):
        rv = self.make_request(expected_status=400, uid=TEST_LOGIN)
        self.assert_error(
            rv,
            error='invalid_request',
            error_description='uid must be a number',
        )

    def test_wrong_ts(self):
        with mock.patch('passport.backend.oauth.api.api.old.bundle_views.views.time', return_value=100500):
            rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_request', error_description='ts is wrong (server time is 100500)')

    def test_ssh_sign_empty(self):
        rv = self.make_request(expected_status=400, ssh_sign='')
        self.assert_error(rv, error='invalid_grant', error_description='ssh_sign is not valid')
        self.check_statbox_last_entry(status='error', reason='ssh_sign.empty', uid=str(self.uid))

    def test_user_not_found(self):
        self.fake_tvm.set_response_value(
            'verify_ssh',
            tvm_error_response(
                status=TVM_STATUS_INVALID_CREDENTIALS,
                error='BB_REJECT',
            )
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='User does not exist')
        self.check_statbox_last_entry(status='error', reason='user.not_found', uid=str(self.uid))

    def test_ssh_keys_not_found(self):
        self.fake_tvm.set_response_value(
            'verify_ssh',
            tvm_error_response(
                status=TVM_STATUS_INVALID_CREDENTIALS,
                error='NO_SSH_KEY',
            )
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='No ssh keys found')
        self.check_statbox_last_entry(status='error', reason='ssh_keys.not_found', uid=str(self.uid))

    def test_ssh_sign_invalid(self):
        self.fake_tvm.set_response_value(
            'verify_ssh',
            tvm_error_response(
                status=TVM_STATUS_INVALID_CREDENTIALS,
                error='SSH_BROKEN',
            )
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='ssh_sign is not valid')
        self.check_statbox_last_entry(status='error', reason='ssh_sign.invalid', uid=str(self.uid))

    def test_unknown_credentials_failure(self):
        self.fake_tvm.set_response_value(
            'verify_ssh',
            tvm_error_response(
                status=TVM_STATUS_INVALID_CREDENTIALS,
                error='SMTH_WEIRD',
            )
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Something went wrong')
        self.check_statbox_last_entry(
            status='error',
            uid=str(self.uid),
            tvm_status=TVM_STATUS_INVALID_CREDENTIALS,
            tvm_error='SMTH_WEIRD',
        )

    def test_tvm_temporary_error(self):
        self.fake_tvm.set_response_side_effect('verify_ssh', TVMTemporaryError)
        rv = self.make_request(expected_status=503, decode_response=False)
        eq_(rv, 'Service temporarily unavailable')

    def test_blackbox_user_not_found(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='User does not exist')
        self.check_statbox_last_entry(status='error', reason='user.not_found', uid=str(self.uid), ssh_key_fingerprint='fp')

    def test_blackbox_invalid_params(self):
        self.fake_blackbox.set_response_side_effect(
            'userinfo',
            BlackboxInvalidParamsError,
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Invalid parameters passed to Blackbox')
        self.check_statbox_last_entry(status='error', reason='blackbox_params.invalid', uid=str(self.uid), ssh_key_fingerprint='fp')

    @override_settings(ALLOW_GRANT_TYPE_SSH_KEY=False)
    def test_not_intranet(self):
        rv = self.make_request(expected_status=400)
        self.assert_error(
            rv,
            error='unsupported_grant_type',
            error_description='Unknown grant_type (must be \'authorization_code\')',
        )
