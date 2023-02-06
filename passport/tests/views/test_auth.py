# -*- coding: utf-8 -*-
import mock
from passport.backend.perimeter.auth_api.auth_logic.logic import AuthLogic
from passport.backend.perimeter.auth_api.common.base_checker import CheckStatus
from passport.backend.perimeter.tests.views.base import BaseViewTestCase


class TestAuth(BaseViewTestCase):
    def setUp(self):
        super(TestAuth, self).setUp()
        self.logic_mock = mock.Mock(return_value=CheckStatus(True, 'LDAP auth successful'))
        self.binascii_mock = mock.Mock(return_value=b'generated_rid')
        self.patches = [
            mock.patch.object(
                AuthLogic,
                'perform_auth',
                self.logic_mock,
            ),
            mock.patch(
                'binascii.hexlify',
                self.binascii_mock,
            ),
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        super(TestAuth, self).tearDown()

    def assert_post_data(self, **kwargs):
        post_data = {
            'login': 'test-login',
            'password': 'password',
            'ip': '127.0.0.1',
            'is_ip_internal': False,
            'is_ip_robot': False,
            'is_robot': False,
            'auth_type': 'web',
        }
        post_data.update(**kwargs)
        assert self.logic_mock.call_args_list[-1][1] == post_data

    def base_post_data(self):
        return {
            'login': 'test-login',
            'password': 'password',
            'ip': '127.0.0.1',
            'is_ip_internal': 'no',
            'is_ip_robot': 'no',
            'is_robot': 'no',
            'auth_type': 'web',
            'some_unused_param': 'some unuzed value',
        }

    def make_request(self, exclude=None, headers=None, **kwargs):
        if headers is None:
            headers = {'X-Request-Id': 'rid'}
        data = dict(self.base_post_data(), **kwargs)
        for param in exclude or []:
            data.pop(param, None)

        return self.client.post(
            '/auth',
            data=data,
            headers=headers,
        )

    def test_ok(self):
        resp = self.make_request()
        self.check_response(
            resp,
            {
                'status': 'ok',
                'description': 'LDAP auth successful',
                'request_id': 'rid',
            },
        )
        self.assert_post_data()

    def test_ok_without_request_id(self):
        resp = self.make_request(headers={})
        self.check_response(
            resp,
            {
                'status': 'ok',
                'description': 'LDAP auth successful',
                'request_id': 'generated_rid',
            },
        )
        self.assert_post_data()

    def test_param_missing(self):
        for missing_param in ['login', 'password', 'ip', 'is_ip_internal', 'auth_type']:
            resp = self.make_request(exclude=[missing_param])
            self.check_response(
                resp,
                {
                    'status': 'error',
                    'description': '`%s` is missing' % missing_param,
                    'request_id': 'rid',
                },
            )

        assert not self.logic_mock.called

    def test_nonascii_param_ok(self):
        resp = self.make_request(login='логин')
        self.check_response(
            resp,
            {
                'status': 'ok',
                'description': 'LDAP auth successful',
                'request_id': 'rid',
            },
        )
        self.assert_post_data(login='логин')

    def test_password_invalid(self):
        self.logic_mock.return_value = CheckStatus(False, 'LDAP password invalid')
        resp = self.make_request()
        self.check_response(
            resp,
            {
                'status': 'password_invalid',
                'description': 'LDAP password invalid',
                'request_id': 'rid',
            },
        )
        self.assert_post_data()

    def test_error(self):
        self.logic_mock.return_value = CheckStatus(False, 'LDAP server unavailable', got_errors=True)
        resp = self.make_request()
        self.check_response(
            resp,
            {
                'status': 'error',
                'description': 'LDAP server unavailable',
                'request_id': 'rid',
            },
        )
        self.assert_post_data()

    def test_second_step_required(self):
        self.logic_mock.return_value = CheckStatus(True, 'LDAP+TOTP password correct', require_second_steps=['totp'])
        resp = self.make_request()
        self.check_response(
            resp,
            {
                'status': 'second_step_required',
                'second_steps': ['totp'],
                'description': 'LDAP+TOTP password correct',
                'request_id': 'rid',
            },
        )
        self.assert_post_data()
