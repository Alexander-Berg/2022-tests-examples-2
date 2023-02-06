# -*- coding: utf-8 -*-
from time import time

from django.conf import settings
from django.test.utils import override_settings
from nose.tools import (
    assert_false,
    ok_,
)
from passport.backend.core.builders.blackbox import BlackboxInvalidParamsError
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.oauth.api.tests.old.issue_token.base import (
    BaseIssueTokenTestCase,
    CommonIssueTokenTests,
)
from passport.backend.oauth.core.db.token import issue_token
from passport.backend.oauth.core.test.base_test_data import TEST_UID
from passport.backend.oauth.core.test.fake_configs import mock_scope_grant


class TestIssueTokenByAssertion(BaseIssueTokenTestCase, CommonIssueTokenTests):
    grant_type = 'assertion'

    def setUp(self):
        super(TestIssueTokenByAssertion, self).setUp()
        self.fake_grants.set_data({
            keyword: mock_scope_grant(grant_types=['assertion'])
            for keyword in [
                'grant_type:assertion',
                'test:foo',
                'test:bar',
                'test:ttl',
                'test:xtoken',
                'test:default_phone',
                'test:basic_scope',
            ]
        })

    def credentials(self):
        return {
            'assertion': self.uid,
        }

    def specific_statbox_values(self):
        return {
            'assertion': str(self.uid),
        }

    def test_no_reuse_for_glogouted(self):
        token = issue_token(uid=self.uid, client=self.test_client, grant_type=self.grant_type, env=self.env)
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=self.uid,
                attributes={settings.BB_ATTR_GLOGOUT: time() + 10},
            ),
        )
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        ok_(rv['access_token'] != token.access_token)

    def test_assertion_invalid(self):
        rv = self.make_request(expected_status=400, assertion='foo')
        self.assert_error(rv, error='invalid_grant', error_description='assertion must be a number')
        self.check_statbox_last_entry(status='error', reason='assertion.invalid', assertion='foo')
        assert_false(self.fake_blackbox.requests)

    def test_blackbox_user_not_found(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='User does not exist')
        self.check_statbox_last_entry(status='error', reason='user.not_found', **self.specific_statbox_values())

    def test_blackbox_user_disabled(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(enabled=False),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='User does not exist')
        self.check_statbox_last_entry(status='error', reason='user.disabled', **self.specific_statbox_values())

    def test_blackbox_invalid_params(self):
        self.fake_blackbox.set_response_side_effect(
            'userinfo',
            BlackboxInvalidParamsError,
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='Invalid parameters passed to Blackbox')
        self.check_statbox_last_entry(status='error', reason='blackbox_params.invalid', **self.specific_statbox_values())

    def test_account_type_forbidden__special_client(self):
        for alias_type, alias in (
            ('social', 'uid-123'),
            ('lite', 'admin@gmail.com'),
        ):
            self.fake_blackbox.set_response_value(
                'userinfo',
                blackbox_userinfo_response(
                    uid=self.uid,
                    aliases={alias_type: alias},
                ),
            )
            with override_settings(
                CLIENTS_LIMITED_BY_ACCOUNT_TYPE={self.test_client.display_id: ['pdd', 'portal']},
            ):
                rv = self.make_request(expected_status=400)
            self.assert_error(rv, error='invalid_grant', error_description='forbidden account type')
            self.check_statbox_last_entry(
                uid=str(TEST_UID),
                status='error',
                reason='account_type.forbidden',
                allowed_account_types='pdd,portal',
                **self.specific_statbox_values()
            )
