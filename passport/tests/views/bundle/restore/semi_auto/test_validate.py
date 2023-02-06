# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_base import BaseTestRestoreSemiAutoView
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_step_base import (
    BaseTestMultiStepRestoreView,
    ProcessStepFormErrorsTests,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_CONTACT_EMAIL,
    TEST_DEFAULT_LOGIN,
    TEST_DEFAULT_UID,
    TEST_DELIVERY_ADDRESS_1,
    TEST_DELIVERY_ADDRESS_2,
    TEST_EMAIL,
    TEST_EMAILS_IN_TRACK,
    TEST_EMAILS_WITH_PHONE_ALIASES,
    TEST_IP,
    TEST_PDD_CYRILLIC_LOGIN,
    TEST_PDD_CYRILLIC_LOGIN_PUNYCODE,
    TEST_PDD_DOMAIN,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_PHONE,
    TEST_PHONE_LOCAL_FORMAT,
)
from passport.backend.api.tests.views.bundle.restore.test.test_base import RestoreTestUtilsMixin
from passport.backend.api.views.bundle.restore.semi_auto.base import (
    STEP_1_PERSONAL_DATA,
    STEP_2_RECOVERY_TOOLS,
    STEP_3_REGISTRATION_DATA,
    STEP_4_USED_SERVICES,
    STEP_5_SERVICES_DATA,
    STEP_6_FINAL_INFO,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_hosted_domains_response
from passport.backend.core.counters import restore_semi_auto_compare_counter
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)


eq_ = iterdiff(eq_)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    HISTORYDB_API_RETRIES=1,
)
class TestRestoreSemiAutoValidateView(BaseTestRestoreSemiAutoView, RestoreTestUtilsMixin):
    def setUp(self):
        super(TestRestoreSemiAutoValidateView, self).setUp()
        self.default_url = '/1/bundle/restore/semi_auto/validate/'

    def make_request(self, contact_email=TEST_CONTACT_EMAIL, headers=None):
        return self.env.client.post(
            self.default_url + '?consumer=dev',
            data={'track_id': self.track_id, 'contact_email': contact_email},
            headers=headers,
        )

    def set_track_values(self, user_entered_login=TEST_DEFAULT_LOGIN, emails=TEST_EMAILS_IN_TRACK,
                         country='ru', **params):
        params['user_entered_login'] = user_entered_login
        if emails is not None:
            params['emails'] = emails
        if country is not None:
            params['country'] = country

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for attr_name, value in params.items():
                setattr(track, attr_name, value)
            self.orig_track = track.snapshot()

    def test_contact_email_no_emails_in_track(self):
        """В треке не сохранены email'ы аккаунта - пропускаем для обратной совместимости"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(emails=None)
        resp = self.make_request(headers=self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_contact_email_invalid(self):
        """Контактный email невалиден"""
        self.set_track_values()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        resp = self.make_request(contact_email='login@yandex.ru', headers=self.get_headers())

        self.assert_error_response(resp, ['contact_email.from_same_account'])
        self.assert_track_unchanged()

    def test_contact_email_invalid_for_portal_account(self):
        """Контактный email сопадает с одним из возможных портальных адресов"""
        self.set_track_values(emails=None)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        resp = self.make_request(contact_email='login@ya.ru', headers=self.get_headers())

        self.assert_error_response(resp, ['contact_email.from_same_account'])
        self.assert_track_unchanged()

    def test_contact_email_invalid_for_pdd_account(self):
        """Контактный email сопадает с адресом pdd-пользователя"""
        self.set_track_values(emails=None)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                login=TEST_PDD_LOGIN,
                uid=TEST_PDD_UID,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                subscribed_to=[102],
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='1',
                domain=TEST_PDD_DOMAIN,
            ),
        )
        resp = self.make_request(contact_email=TEST_PDD_LOGIN, headers=self.get_headers())

        self.assert_error_response(resp, ['contact_email.from_same_account'])
        self.assert_track_unchanged()

    def test_contact_email_invalid_phonenumber_alias_ok(self):
        """Контактный email невалиден, является телефонным алиасом, не раскрываем информацию"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        for email in ('79123456789@ya.ru', '+79123456789@ya.ru', '89123456789@ya.ru', '9123456789@ya.ru'):
            self.set_track_values(emails=' '.join(TEST_EMAILS_WITH_PHONE_ALIASES))
            resp = self.make_request(contact_email=email, headers=self.get_headers())

            self.assert_ok_response(resp)
            self.assert_track_unchanged()

    def test_contact_email_invalid_with_cyrillic_value(self):
        """Контактный email невалиден - нативный для аккаунта, имеет кириллический домен. """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(emails=TEST_PDD_CYRILLIC_LOGIN_PUNYCODE)
        resp = self.make_request(contact_email=TEST_PDD_CYRILLIC_LOGIN, headers=self.get_headers())

        self.assert_error_response(resp, ['contact_email.from_same_account'])
        self.assert_track_unchanged()

    def test_contact_email_invalid_phonenumber_alias_no_country_ok(self):
        """Контактный email невалиден, является телефонным алиасом, страна не задана, не раскрываем информацию"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        for email in ('+7-912-345-67-89@ya.ru', '+79123456789@yandex.kz'):
            self.set_track_values(emails=' '.join(TEST_EMAILS_WITH_PHONE_ALIASES), country=None)
            resp = self.make_request(contact_email=email, headers=self.get_headers())

            self.assert_ok_response(resp)
            self.assert_track_unchanged()

    def test_contact_email_valid(self):
        """Контактный email валиден"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        for email in (
                TEST_CONTACT_EMAIL,
                'a79123456789@ya.ru',  # есть буква, номер-алиас
                u'+ф79123456789@ya.ru',  # есть кириллическая буква, номер-алиас
                '89123456790@ya.ru',  # другой номер
                '79123456789@google.ru',  # номер-алиас, не-яндексовый домен
        ):
            self.set_track_values(emails=' '.join(TEST_EMAILS_WITH_PHONE_ALIASES))
            resp = self.make_request(contact_email=email, headers=self.get_headers())

            self.assert_ok_response(resp)
            self.assert_track_unchanged()


@with_settings_hosts()
class TestRestoreSemiAutoMultiStepValidateView(BaseTestMultiStepRestoreView, ProcessStepFormErrorsTests, RestoreTestUtilsMixin):
    # TODO: перенести тесты валидации contact_email из TestRestoreSemiAutoValidateView после
    # перехода на новую версию ручки
    def setUp(self):
        super(TestRestoreSemiAutoMultiStepValidateView, self).setUp()
        self.default_url = '/3/bundle/restore/semi_auto/validate/'

    def test_inconsistent_process_restart_required(self):
        self.set_track_values(semi_auto_step=STEP_4_USED_SERVICES, version='outdated_version')

        resp = self.make_request({'json_data': '{}'}, self.get_headers())

        self.assert_ok_response(resp, state='process_restart_required')
        self.assert_track_unchanged()
        self.assert_state_or_error_recorded_to_statbox(
            state='process_restart_required',
            version='outdated_version',
            step=STEP_4_USED_SERVICES,
            _exclude=['uid'],
        )

    def test_ip_limit_exceeded_fails(self):
        self.set_track_values(uid=TEST_DEFAULT_UID)

        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        # установим счетчик вызовов на ip в limit
        for i in range(counter.limit):
            counter.incr(TEST_IP)
        eq_(counter.get(TEST_IP), counter.limit)

        resp = self.make_request(self.request_params_step_1(), self.get_headers())
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

        resp = self.make_request(self.request_params_step_1(), self.get_headers())
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()

        eq_(counter.get(TEST_DEFAULT_UID), counter.limit)  # счетчик не должен увеличиться
        self.assert_ok_response(resp, state='rate_limit_exceeded')
        self.assert_state_or_error_recorded_to_statbox(
            state='rate_limit_exceeded',
        )

    def test_step_1_validation_passed(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)

        resp = self.make_request(self.request_params_step_1(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_1_empty_request_validation_passed(self):
        """Ручка валидации не требует обязательных параметров"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)

        resp = self.make_request({'json_data': '{}'}, self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_2_empty_request_validation_passed(self):
        self.set_track_values(semi_auto_step=STEP_2_RECOVERY_TOOLS)

        resp = self.make_request({'json_data': '{}'}, self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_2_validation_passed(self):
        self.set_track_values(semi_auto_step=STEP_2_RECOVERY_TOOLS)

        resp = self.make_request(
            self.request_params_step_2(phone_numbers=[TEST_PHONE], emails=[TEST_EMAIL]),
            self.get_headers(),
        )

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_2_duplicate_phone_numbers_with_wrong_country(self):
        """Из-за того, что телефонный номер не соответствует стране, не можем определить совпадение"""
        self.set_track_values(semi_auto_step=STEP_2_RECOVERY_TOOLS, country='tr')

        resp = self.make_request(
            self.request_params_step_2(phone_numbers=[TEST_PHONE_LOCAL_FORMAT, TEST_PHONE]),
            self.get_headers(),
        )

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_3_empty_request_validation_passed(self):
        """Ручка валидации не требует обязательных параметров"""
        self.set_track_values(semi_auto_step=STEP_3_REGISTRATION_DATA)

        resp = self.make_request({'json_data': '{}'}, self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_3_minimal_request_validation_passed(self):
        self.set_track_values(semi_auto_step=STEP_3_REGISTRATION_DATA)

        resp = self.make_request(
            self.request_params_step_3(
                registration_city=None,
                registration_city_id=None,
                registration_country_id=None,
            ),
            self.get_headers(),
        )

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_3_validation_passed(self):
        self.set_track_values(semi_auto_step=STEP_3_REGISTRATION_DATA)

        resp = self.make_request(self.request_params_step_3(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_4_empty_request_validation_passed(self):
        self.set_track_values(semi_auto_step=STEP_4_USED_SERVICES)

        resp = self.make_request({'json_data': '{}'}, self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_4_validation_passed(self):
        self.set_track_values(semi_auto_step=STEP_4_USED_SERVICES)

        resp = self.make_request(self.request_params_step_4(services=['mail', 'music']), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_5_empty_request_validation_passed(self):
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA)

        resp = self.make_request({'json_data': '{}'}, self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_5_validation_passed(self):
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA)

        resp = self.make_request(
            self.request_params_step_5(
                delivery_addresses=[TEST_DELIVERY_ADDRESS_1, TEST_DELIVERY_ADDRESS_2],
                email_folders=[u'папка'],
                outbound_emails=[u'вася@yandex.ru', u'петя@ya.ru'],
                email_collectors=[u'сборщик1@mail.ru', 'сборщик2@gmail.com'],
                email_whitelist=[u'белый@white.ru'],
                email_blacklist=[u'черный@black.ru'],
            ),
            self.get_headers(),
        )

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_6_empty_request_validation_passed(self):
        self.set_track_values(semi_auto_step=STEP_6_FINAL_INFO)

        resp = self.make_request({'json_data': '{}'}, self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_step_6_validation_passed(self):
        self.set_track_values(semi_auto_step=STEP_6_FINAL_INFO)

        resp = self.make_request(self.request_params_step_6(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_unchanged()
