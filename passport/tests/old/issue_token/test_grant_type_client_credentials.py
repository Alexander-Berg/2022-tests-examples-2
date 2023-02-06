# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.oauth.api.tests.old.issue_token.base import (
    BaseIssueTokenTestCase,
    CommonIssueTokenTests,
    CommonRateLimitsTests,
)
from passport.backend.oauth.core.test.utils import assert_params_in_tskv_log_entry


class TestIssueTokenByClientCredentials(BaseIssueTokenTestCase, CommonIssueTokenTests, CommonRateLimitsTests):
    grant_type = 'client_credentials'
    uid = 0

    def credentials(self):
        return {}

    def assert_blackbox_ok(self):
        eq_(len(self.fake_blackbox.requests), 0)

    def test_limited_by_karma(self):
        # тест неприменим, т.к. в этом процессе не участвует пользователь
        pass

    def test_is_child_error(self):
        # тест неприменим, т.к. в этом процессе не участвует пользователь
        pass

    def test_is_child_and_client_is_yandex_ok(self):
        # тест неприменим, т.к. в этом процессе не участвует пользователь
        pass

    def test_ok_with_counters(self):
        # Оверрайдим тест родителя
        self.fake_kolmogor.set_response_value('get', '2')
        with self.override_rate_limit_settings():
            rv = self.make_request()
        self.assert_token_response_ok(rv)
        eq_(len(self.fake_kolmogor.requests), 2)
        eq_(len(self.fake_kolmogor.get_requests_by_method('get')), 1)
        eq_(len(self.fake_kolmogor.get_requests_by_method('inc')), 1)

    def test_rate_limit_exceeded_client_id(self):
        self.fake_kolmogor.set_response_value('get', '3')
        with self.override_rate_limit_settings():
            rv = self.make_request(expected_status=429)
        self.assert_error(
            rv,
            error='invalid_request',
            error_description='Too many requests',
        )
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            dict(
                reason='rate_limit_exceeded',
                status='error',
                key='grant_type:%s:client_id:%s' % (self.grant_type, self.test_client.display_id),
                value='3',
                limit='2',
                client_id=self.test_client.display_id,
            ),
        )
        eq_(len(self.fake_kolmogor.requests), 1)
        eq_(len(self.fake_kolmogor.get_requests_by_method('get')), 1)
