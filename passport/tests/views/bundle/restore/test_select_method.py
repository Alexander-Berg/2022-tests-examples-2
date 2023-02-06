# -*- coding: utf-8 -*-

from passport.backend.api.settings.constants.restore import (
    RESTORE_REQUEST_SOURCE_FOR_AUTO_RESTORE,
    RESTORE_REQUEST_SOURCE_FOR_AUTO_RESTORE_WITH_METHODS,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.restore.test.test_base import (
    AccountValidityTestsMixin,
    CommonTestsMixin,
    eq_,
    RestoreBaseTestCase,
)
from passport.backend.api.views.bundle.restore.base import (
    RESTORE_METHOD_EMAIL,
    RESTORE_METHOD_HINT,
    RESTORE_METHOD_PHONE,
    RESTORE_STATE_METHOD_SELECTED,
    RESTORE_STATE_SUBMIT_PASSED,
)
from passport.backend.api.views.bundle.restore.semi_auto.base import (
    MULTISTEP_FORM_VERSION,
    STEP_1_PERSONAL_DATA,
)
from passport.backend.core.counters import restore_counter
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts


class RestoreSelectMethodTestCaseBase(RestoreBaseTestCase):
    restore_step = 'select_method'

    default_url = '/1/bundle/restore/select_method/'

    def set_track_values(self, restore_state=RESTORE_STATE_SUBMIT_PASSED, **params):
        params.update(
            restore_state=restore_state,
        )
        super(RestoreSelectMethodTestCaseBase, self).set_track_values(**params)

    def query_params(self, method=RESTORE_METHOD_HINT, **kwargs):
        return dict(method=method)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    RESTORE_SEMI_AUTO_LEARNING_DENOMINATORS={
        RESTORE_REQUEST_SOURCE_FOR_AUTO_RESTORE: 0,
    },
    **mock_counters()
)
class RestoreSelectMethodTestCase(RestoreSelectMethodTestCaseBase, CommonTestsMixin, AccountValidityTestsMixin):

    def setUp(self):
        super(RestoreSelectMethodTestCase, self).setUp()

    def test_global_counter_overflow_fails(self):
        """Глобальный счетчик попыток восстановления переполнен"""
        self.set_track_values()
        counter = restore_counter.get_per_ip_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_IP)
        eq_(counter.get(TEST_IP), counter.limit)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['rate.limit_exceeded'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        eq_(counter.get(TEST_IP), counter.limit)  # счетчик не увеличивается
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='rate.limit_exceeded',
            ),
        ])

    def test_select_current_method_ok(self):
        """При выборе текущего способа восстановления, ничего не делаем"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM)

        resp = self.make_request(
            self.query_params(method=RESTORE_METHOD_SEMI_AUTO_FORM),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([])
        self.assert_blackbox_userinfo_called()

    def test_select_method_with_semi_auto_form_already_selected_fails(self):
        """Нельзя вызывать ручку выбора метода восстановления после выбора анкеты"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM)

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
                current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
                previous_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_select_not_suitable_method_fails(self):
        """Нельзя выбрать способ восстановления, недоступный для аккаунта"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(method=RESTORE_METHOD_PHONE), headers=self.get_headers())

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
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_select_method_for_the_first_time_ok(self):
        """Успешный выбор способа восстановления впервые"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(method=RESTORE_METHOD_PHONE), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_updated(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            current_restore_method=RESTORE_METHOD_PHONE,
            restore_methods_select_counters={RESTORE_METHOD_PHONE: 1},
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                current_restore_method=RESTORE_METHOD_PHONE,
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                selected_methods_order=RESTORE_METHOD_PHONE,
                phone_select_count='1',
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_change_method_ok(self):
        """Успешный выбор другого способа восстановления"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=TEST_EMAILS,
                emails_native=False,
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            current_restore_method=RESTORE_METHOD_PHONE,
            restore_methods_select_counters={RESTORE_METHOD_PHONE: 1},
            restore_methods_select_order=[RESTORE_METHOD_PHONE],
        )

        resp = self.make_request(self.query_params(method=RESTORE_METHOD_EMAIL), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_updated(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            current_restore_method=RESTORE_METHOD_EMAIL,
            restore_methods_select_counters={RESTORE_METHOD_PHONE: 1, RESTORE_METHOD_EMAIL: 1},
            restore_methods_select_order=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL],
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                previous_restore_method=RESTORE_METHOD_PHONE,
                current_restore_method=RESTORE_METHOD_EMAIL,
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                selected_methods_order=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL]),
                phone_select_count='1',
                email_select_count='1',
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_change_method_back_ok(self):
        """Успешный выбор предыдущего способа восстановления после выбора другого"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=TEST_EMAILS,
                emails_native=False,
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            current_restore_method=RESTORE_METHOD_EMAIL,
            restore_methods_select_counters={RESTORE_METHOD_PHONE: 1, RESTORE_METHOD_EMAIL: 1},
            restore_methods_select_order=[RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL],
        )

        resp = self.make_request(self.query_params(method=RESTORE_METHOD_PHONE), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        order = [RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_PHONE]
        self.assert_track_updated(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            current_restore_method=RESTORE_METHOD_PHONE,
            restore_methods_select_counters={RESTORE_METHOD_PHONE: 2, RESTORE_METHOD_EMAIL: 1},
            restore_methods_select_order=order,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                previous_restore_method=RESTORE_METHOD_EMAIL,
                current_restore_method=RESTORE_METHOD_PHONE,
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                selected_methods_order=','.join(order),
                phone_select_count='2',
                email_select_count='1',
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_select_semi_auto_form_with_other_suitable_methods_ok(self):
        """При выборе анкеты восстановления происходит настройка трека для работы анкеты"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(method=RESTORE_METHOD_SEMI_AUTO_FORM), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_updated(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
            restore_methods_select_counters={RESTORE_METHOD_SEMI_AUTO_FORM: 1},
            restore_methods_select_order=[RESTORE_METHOD_SEMI_AUTO_FORM],
            # Поля, выставляемые для инициализации анкеты
            request_source=RESTORE_REQUEST_SOURCE_FOR_AUTO_RESTORE_WITH_METHODS,
            is_for_learning=False,
            semi_auto_step=STEP_1_PERSONAL_DATA,
            version=MULTISTEP_FORM_VERSION,
            emails=TEST_EMAILS_IN_TRACK,
            country='ru',
            is_unconditional_pass=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
                selected_methods_order=RESTORE_METHOD_SEMI_AUTO_FORM,
                semi_auto_select_count='1',
                version=MULTISTEP_FORM_VERSION,
            ),
        ])
        self.assert_blackbox_userinfo_called()


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=0,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    RESTORE_SEMI_AUTO_LEARNING_DENOMINATORS={
        RESTORE_REQUEST_SOURCE_FOR_AUTO_RESTORE: 0,
    },
    **mock_counters()
)
class RestoreSelectMethodNoSemiAutoFormTestCase(RestoreSelectMethodTestCaseBase, CommonTestsMixin, AccountValidityTestsMixin):

    def setUp(self):
        super(RestoreSelectMethodNoSemiAutoFormTestCase, self).setUp()

    def test_select_semi_auto_form_other_methods_available_fails(self):
        """Пользователь не может выбрать анкету, т.к. не попадает в долю "на обучение", и у него есть другие средства"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(method=RESTORE_METHOD_SEMI_AUTO_FORM), headers=self.get_headers())

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
                suitable_restore_methods=RESTORE_METHOD_HINT,
                selected_methods_order='',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_select_semi_auto_form_other_methods_not_available_ok(self):
        """Пользователь может выбрать анкету, т.к. у него нет других средств, хотя и не попадает в долю на обучение"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(hintq=None, hinta=None),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(method=RESTORE_METHOD_SEMI_AUTO_FORM), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_updated(
            restore_state=RESTORE_STATE_METHOD_SELECTED,
            current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
            restore_methods_select_counters={RESTORE_METHOD_SEMI_AUTO_FORM: 1},
            restore_methods_select_order=[RESTORE_METHOD_SEMI_AUTO_FORM],
            # Поля, выставляемые для инициализации анкеты
            request_source=RESTORE_REQUEST_SOURCE_FOR_AUTO_RESTORE,
            is_for_learning=False,
            semi_auto_step=STEP_1_PERSONAL_DATA,
            version=MULTISTEP_FORM_VERSION,
            emails=TEST_EMAILS_IN_TRACK,
            country='ru',
            is_unconditional_pass=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
                suitable_restore_methods=RESTORE_METHOD_SEMI_AUTO_FORM,
                selected_methods_order=RESTORE_METHOD_SEMI_AUTO_FORM,
                semi_auto_select_count='1',
                version=MULTISTEP_FORM_VERSION,
            ),
        ])
        self.assert_blackbox_userinfo_called()
