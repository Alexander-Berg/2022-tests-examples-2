# -*- coding: utf-8 -*-
import json
import time

from nose.tools import eq_
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_base import CheckAccountByLoginTests
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_step_base import BaseTestMultiStepRestoreView
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD,
    TEST_DEFAULT_HINT_QUESTION_TEXT,
    TEST_DEFAULT_LOGIN,
    TEST_DEFAULT_UID,
    TEST_EMAILS_IN_TRACK,
    TEST_IP,
    TEST_PDD_CYRILLIC_DOMAIN,
    TEST_PDD_CYRILLIC_LOGIN,
    TEST_PDD_DOMAIN,
    TEST_PDD_UID,
)
from passport.backend.api.views.bundle.restore.semi_auto.base import (
    STEP_1_PERSONAL_DATA,
    STEP_2_RECOVERY_TOOLS,
    STEP_3_REGISTRATION_DATA,
    STEP_4_USED_SERVICES,
    STEP_5_SERVICES_DATA,
    STEP_6_FINAL_INFO,
    STEP_FINISHED,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_hosted_domains_response
from passport.backend.core.counters import restore_semi_auto_compare_counter
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)


eq_ = iterdiff(eq_)


@with_settings_hosts(
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
)
class RestoreSemiAutoMultiStepGetStateViewTestCase(BaseTestMultiStepRestoreView, CheckAccountByLoginTests):

    def setUp(self):
        super(RestoreSemiAutoMultiStepGetStateViewTestCase, self).setUp()
        self.default_url = '/3/bundle/restore/semi_auto/get_state/'

    def query_params(self, **kwargs):
        # для совместимости с CheckAccountByLoginTests
        return {}

    def assert_submit_state_or_error_recorded_to_statbox(self, **kwargs):
        # для совместимости с CheckAccountByLoginTests
        return self.assert_state_or_error_recorded_to_statbox(**kwargs)

    def make_request(self, data=None, headers=None):
        return super(RestoreSemiAutoMultiStepGetStateViewTestCase, self).make_request(data, headers=headers)

    def assert_got_state_recorded_to_statbox(self, **kwargs):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('got_state', **kwargs)
        ])

    def assert_track_updated(self, questions=None, uid=TEST_DEFAULT_UID, login=TEST_DEFAULT_LOGIN,
                             emails=TEST_EMAILS_IN_TRACK, domain=None):
        orig_track_data = self.orig_track._data
        orig_track_data.update(uid=str(uid), login=login, country='ru', emails=emails)
        if questions is not None:
            orig_track_data.update(questions=json.dumps(questions))
        if domain is not None:
            orig_track_data.update(domain=domain)
        track = self.track_manager.read(self.track_id)
        new_track_data = track._data
        eq_(orig_track_data, new_track_data)

    def test_inconsistent_process_restart_required(self):
        self.set_track_values(semi_auto_step=STEP_4_USED_SERVICES, version='outdated_version')

        resp = self.make_request(headers=self.get_headers())

        self.assert_ok_response(resp, state='process_restart_required')
        self.assert_track_unchanged()
        self.assert_state_or_error_recorded_to_statbox(
            state='process_restart_required',
            version='outdated_version',
            step=STEP_4_USED_SERVICES,
            _exclude=['uid'],
        )

    def test_invalid_step_error(self):
        self.set_track_values(semi_auto_step='invalid_step')

        resp = self.make_request(headers=self.get_headers())

        self.assert_error_response(resp, ['track.invalid_state'])

    def test_ip_limit_exceeded_fails(self):
        self.set_track_values(uid=TEST_DEFAULT_UID)

        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        # установим счетчик вызовов на ip в limit
        for i in range(counter.limit):
            counter.incr(TEST_IP)
        eq_(counter.get(TEST_IP), counter.limit)

        resp = self.make_request(headers=self.get_headers())
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()

        eq_(counter.get(TEST_IP), counter.limit)  # счетчик не должен увеличиться
        self.assert_ok_response(resp, state='rate_limit_exceeded')
        self.assert_state_or_error_recorded_to_statbox(
            state='rate_limit_exceeded',
        )

    def test_uid_limit_exceeded_fails(self):
        self.set_track_values(uid=TEST_DEFAULT_UID)

        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        # установим счетчик вызовов на uid в limit + 1
        for i in range(counter.limit):
            counter.incr(TEST_DEFAULT_UID)
        eq_(counter.get(TEST_DEFAULT_UID), counter.limit)

        resp = self.make_request(headers=self.get_headers())
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()

        eq_(counter.get(TEST_DEFAULT_UID), counter.limit)  # счетчик не должен увеличиться
        self.assert_ok_response(resp, state='rate_limit_exceeded')
        self.assert_state_or_error_recorded_to_statbox(
            state='rate_limit_exceeded',
        )

    def test_autoregistered_password_changing_required_redirect(self):
        """Автозарегистрированный пользователь с требованием смены пароля"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(password_creating_required=True, subscribed_to=[100]),
        )

        resp = self.make_request(headers=self.get_headers())

        self.assert_ok_response(resp, state='complete_autoregistered')
        self.assert_state_or_error_recorded_to_statbox(
            state='complete_autoregistered',
        )
        self.assert_track_unchanged()

    def test_step_1_unconditional_pass_with_disabled_account_ok(self):
        """Флаг пропуска проверок позволяет пройти проверку предусловий заблокированному пользователю"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA, is_unconditional_pass=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(enabled=False),
        )

        resp = self.make_request(headers=self.get_headers())

        self.assert_get_state_response_ok(resp, track_state=STEP_1_PERSONAL_DATA)
        self.assert_got_state_recorded_to_statbox(step=STEP_1_PERSONAL_DATA, is_unconditional_pass='1')
        self.assert_track_updated()

    def test_step_1_with_disabled_on_deletion_account_ok(self):
        """Аккаунт заблокирован при удалении не слишком давно"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds() + 50
        userinfo = self.default_userinfo_response(
            attributes={
                'account.deletion_operation_started_at': deletion_started_at,
                'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)

        resp = self.make_request(headers=self.get_headers())

        self.assert_get_state_response_ok(resp, track_state=STEP_1_PERSONAL_DATA)
        self.assert_got_state_recorded_to_statbox(step=STEP_1_PERSONAL_DATA)
        self.assert_track_updated()

    def test_step_1_track_updated(self):
        """Данные аккаунта записываются в трек"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA, emails=None)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(headers=self.get_headers())

        self.assert_get_state_response_ok(resp, track_state=STEP_1_PERSONAL_DATA)
        self.assert_got_state_recorded_to_statbox(step=STEP_1_PERSONAL_DATA)
        self.assert_track_updated()

    def test_step_1_request_source_returned(self):
        """Возвращаем request_source из трека"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA, request_source='changepass')
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(headers=self.get_headers())

        self.assert_get_state_response_ok(resp, track_state=STEP_1_PERSONAL_DATA, request_source='changepass')
        self.assert_got_state_recorded_to_statbox(step=STEP_1_PERSONAL_DATA, request_source='changepass')
        self.assert_track_updated()

    def test_step_2_pdd_cyrillic_domain_served_ok(self):
        """ПДД-пользователь с кириллическим доменом, обслуживается саппортом Яндекса"""
        self.set_track_values(semi_auto_step=STEP_2_RECOVERY_TOOLS, user_entered_login=TEST_PDD_CYRILLIC_LOGIN)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                login=TEST_PDD_CYRILLIC_LOGIN,
                uid=TEST_PDD_UID,
                aliases={
                    'pdd': TEST_PDD_CYRILLIC_LOGIN,
                },
                subscribed_to=[102],
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='1',
                domain=TEST_PDD_CYRILLIC_DOMAIN,
            ),
        )

        resp = self.make_request(headers=self.get_headers())

        self.assert_get_state_response_ok(
            resp,
            track_state=STEP_2_RECOVERY_TOOLS,
            questions=[{'id': 0, 'text': TEST_DEFAULT_HINT_QUESTION_TEXT}],
            user_entered_login=TEST_PDD_CYRILLIC_LOGIN,
        )
        self.assert_got_state_recorded_to_statbox(
            step=STEP_2_RECOVERY_TOOLS,
            uid=str(TEST_PDD_UID),
            login=TEST_PDD_CYRILLIC_LOGIN,
        )
        self.assert_track_updated(
            questions=[{'id': 99, 'text': TEST_DEFAULT_HINT_QUESTION_TEXT}],
            login=TEST_PDD_CYRILLIC_LOGIN,
            uid=TEST_PDD_UID,
            domain=TEST_PDD_CYRILLIC_DOMAIN,
        )

    def test_step_2_no_questions_found(self):
        self.set_track_values(semi_auto_step=STEP_2_RECOVERY_TOOLS)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                hinta=None,
                hintq=None,
            ),
        )

        resp = self.make_request(headers=self.get_headers())

        self.assert_get_state_response_ok(resp, track_state=STEP_2_RECOVERY_TOOLS, questions=[])
        self.assert_got_state_recorded_to_statbox(step=STEP_2_RECOVERY_TOOLS)
        self.assert_track_updated(questions=[])

    def test_step_3_works(self):
        self.set_track_values(
            semi_auto_step=STEP_3_REGISTRATION_DATA,
            uid=str(TEST_DEFAULT_UID),
            login=TEST_DEFAULT_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(headers=self.get_headers())

        self.assert_get_state_response_ok(resp, track_state=STEP_3_REGISTRATION_DATA)
        self.assert_got_state_recorded_to_statbox(step=STEP_3_REGISTRATION_DATA)
        self.assert_track_unchanged()

    def test_step_4_works(self):
        self.set_track_values(
            semi_auto_step=STEP_4_USED_SERVICES,
            uid=str(TEST_DEFAULT_UID),
            login=TEST_DEFAULT_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(headers=self.get_headers())

        self.assert_get_state_response_ok(resp, track_state=STEP_4_USED_SERVICES)
        self.assert_got_state_recorded_to_statbox(step=STEP_4_USED_SERVICES)
        self.assert_track_unchanged()

    def test_step_5_works(self):
        self.set_track_values(
            semi_auto_step=STEP_5_SERVICES_DATA,
            uid=str(TEST_DEFAULT_UID),
            login=TEST_DEFAULT_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(headers=self.get_headers())

        self.assert_get_state_response_ok(resp, track_state=STEP_5_SERVICES_DATA)
        self.assert_got_state_recorded_to_statbox(step=STEP_5_SERVICES_DATA)
        self.assert_track_unchanged()

    def test_step_6_works(self):
        self.set_track_values(
            semi_auto_step=STEP_6_FINAL_INFO,
            uid=str(TEST_DEFAULT_UID),
            login=TEST_DEFAULT_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(headers=self.get_headers())

        self.assert_get_state_response_ok(resp, track_state=STEP_6_FINAL_INFO)
        self.assert_got_state_recorded_to_statbox(step=STEP_6_FINAL_INFO)
        self.assert_track_unchanged()

    def test_last_step_finished_works(self):
        self.set_track_values(
            semi_auto_step=STEP_FINISHED,
            uid=str(TEST_DEFAULT_UID),
            login=TEST_DEFAULT_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(headers=self.get_headers())

        self.assert_get_state_response_ok(resp, track_state=STEP_FINISHED)
        self.assert_got_state_recorded_to_statbox(step=STEP_FINISHED)
        self.assert_track_unchanged()
