# -*- coding: utf-8 -*-

from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.restore.test.test_base import (
    AccountValidityTestsMixin,
    CommonMethodTestsMixin,
    CommonTestsMixin,
    RestoreBaseTestCase,
)
from passport.backend.api.views.bundle.restore.base import *
from passport.backend.core.builders.messenger_api.faker.fake_messenger_api import messenger_api_response
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeSpan


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    ANSWER_CHECK_ERRORS_CAPTCHA_THRESHOLD=3,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class RestoreCheckAnswerTestCase(RestoreBaseTestCase, CommonTestsMixin,
                                 AccountValidityTestsMixin, CommonMethodTestsMixin):

    restore_step = 'check_answer'

    default_url = '/1/bundle/restore/hint/check/'

    account_validity_tests_extra_statbox_params = {
        'is_captcha_required': '0',
    }

    def setUp(self):
        super(RestoreCheckAnswerTestCase, self).setUp()
        self.env.messenger_api.set_response_value('check_user_lastseen', messenger_api_response(TEST_DEFAULT_UID))

    def set_track_values(self, restore_state=RESTORE_STATE_METHOD_SELECTED,
                         current_restore_method=RESTORE_METHOD_HINT,
                         **params):
        params.update(
            restore_state=restore_state,
            current_restore_method=current_restore_method,
        )
        super(RestoreCheckAnswerTestCase, self).set_track_values(**params)

    def query_params(self, answer=TEST_DEFAULT_HINT_ANSWER, **kwargs):
        return dict(
            answer=answer,
        )

    def test_global_counter_overflow_fails(self):
        """Глобальный счетчик попыток восстановления переполнен"""
        self.global_counter_overflow_case(RESTORE_METHOD_HINT)

    def test_captcha_required_and_not_passed_fails(self):
        """Требуется ввод капчи, капча не пройдена"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(
            answer_checks_count=4,
            is_captcha_recognized=False,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['user.not_verified'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='user.not_verified',
                current_restore_method=RESTORE_METHOD_HINT,
                is_captcha_required='1',
                answer_checks_count='4',
            ),
        ])

    def test_restore_method_no_more_available_fails(self):
        """Восстановление по КВ/КО стало недоступно"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(hinta=None, hintq=None),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['method.not_allowed'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='method.not_allowed',
                suitable_restore_methods=RESTORE_METHOD_SEMI_AUTO_FORM,
                current_restore_method=RESTORE_METHOD_HINT,
                is_captcha_required='0',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_invalid_answer_fails(self):
        """Введен неправильный КО"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()

        resp = self.make_request(
            self.query_params(answer=TEST_INVALID_HINT_ANSWER),
            headers=self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['answer.not_matched'],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            answer_checks_count=1,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='answer.not_matched',
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_HINT,
                is_captcha_required='0',
                answer_checks_count='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_invalid_answer_with_captcha_invalidation(self):
        """Введен неправильный КО, выставлено требование капчи"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(
            answer_checks_count=2,
        )

        resp = self.make_request(self.query_params(answer='bad answer!'), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['answer.not_matched'],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            answer_checks_count=3,
            is_captcha_checked=False,
            is_captcha_recognized=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='answer.not_matched',
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_HINT,
                is_captcha_required='0',
                answer_checks_count='3',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_valid_answer_ok(self):
        """Введен правильный КО"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()

        resp = self.make_request(
            self.query_params(answer=TEST_DEFAULT_HINT_ANSWER.upper()),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_updated(
            restore_state=RESTORE_STATE_METHOD_PASSED,
            is_strong_password_policy_required=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_HINT,
                is_captcha_required='0',
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_blackbox_userinfo_called()
