# -*- coding: utf-8 -*-
from copy import deepcopy

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import AccountModificationNotifyTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    NOTIFICATIONS_URL_BEGIN,
    NOTIFICATIONS_URL_END,
    TEST_ACCOUNT_DATA,
    TEST_DISPLAY_NAME,
    TEST_FIRSTNAME,
    TEST_HINT_ANSWER,
    TEST_HINT_ANSWER_MAX,
    TEST_HINT_QUESTION,
    TEST_HINT_QUESTION_ID,
    TEST_HINT_QUESTION_TEXT,
    TEST_HOST,
    TEST_LOGIN,
    TEST_PASSWORD_HASH,
    TEST_PASSWORD_VERIFICATION_AGE,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
    TEST_YANDEXUID_VALUE,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.counters import (
    check_answer_counter,
    question_change_email_counter,
)
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.utils.common import merge_dicts
from passport.backend.utils.time import datetime_to_integer_unixtime


QUESTIONS_BASE_GRANT = 'questions.base'
QUESTIONS_CHANGE_GRANT = 'questions.change'
TEST_HINT_QUESTION_ID1 = 1
TEST_HINT_QUESTION_TEXT1 = 'Девичья фамилия матери'
TEST_HINT_ANSWER_LONG = 'a' * 1024
TEST_AUTH_ID = 'auth_id'


@with_settings_hosts(
    PASSWORD_VERIFICATION_MAX_AGE=300,
    CHECK_ANSWER_UNTIL_CAPTCHA_LIMIT_BY_UID=3,
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'hint_change'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        QUESTION_CHANGE_EMAIL_NOTIFICATION_COUNTER=(1, 600, 1),
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:hint_change': 5},
    )
)
class TestQuestionsChangeView(BaseBundleTestViews, AccountModificationNotifyTestMixin):

    default_url = '/1/account/questions/change/?consumer=dev'
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
    )
    mocked_grants = [QUESTIONS_BASE_GRANT, QUESTIONS_CHANGE_GRANT]

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(self.mocked_grants)

        self.account_data = deepcopy(TEST_ACCOUNT_DATA['account']['person'])
        self.account_data = merge_dicts(
            self.account_data,
            {
                'birthdate': self.account_data.pop('birthday'),
                'uid': TEST_UID,
                'login': TEST_LOGIN,
                'display_name': {'name': TEST_DISPLAY_NAME},
            },
        )
        self.default_track_data = {
            'uid': TEST_UID,
        }
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.http_query_args = {
            'answer': TEST_HINT_ANSWER_MAX,
            'track_id': self.track_id,
            'question_id': 1,
            'display_language': 'ru',
            'new_answer': TEST_HINT_ANSWER,
        }
        self.setup_statbox_templates()
        self.start_account_modification_notify_mocks(
            ip=TEST_USER_IP,
        )
        self.setup_kolmogor()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])

    def setup_track(self, track_data=None):
        track_data = track_data if track_data is not None else self.default_track_data
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for name, value in track_data.items():
                setattr(track, name, value)

    def set_blackbox_response(self, have_password=True, password_age=TEST_PASSWORD_VERIFICATION_AGE,
                              with_hint=True, old_hint=TEST_HINT_ANSWER_MAX,
                              with_emails=True, with_phones=True, is_2fa_on=False,
                              **account_data):
        account_data = account_data or self.account_data

        if with_hint:
            account_data['dbfields'] = {
                'userinfo_safe.hintq.uid': TEST_HINT_QUESTION,
                'userinfo_safe.hinta.uid': old_hint,
            }
        account_data['crypt_password'] = TEST_PASSWORD_HASH if have_password else ''
        if with_phones:
            account_data.update(
                build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164),
            )
        if with_emails:
            account_data['emails'] = [
                self.env.email_toolkit.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ]
        if is_2fa_on:
            account_data.setdefault('attributes', {})['account.2fa_on'] = True

        sessionid_response = blackbox_sessionid_multi_response(
            age=password_age,
            authid=TEST_AUTH_ID,
            **account_data
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )
        self.env.db.serialize(sessionid_response)

    def check_db_entries(self, question_id=TEST_HINT_QUESTION_ID, question_text=TEST_HINT_QUESTION_TEXT,
                         answer=TEST_HINT_ANSWER_MAX):
        hint_attributes = [
            ('hint.question.serialized', '%d:%s' % (question_id, question_text)),
            ('hint.answer.encrypted', answer),
        ]

        for attribute_name, value in hint_attributes:
            self.env.db.check_db_attr(TEST_UID, attribute_name, value)

    def check_emails_sent(self, is_2fa_on=False, is_hint_created=False):
        self.env.email_toolkit.assert_emails_sent([
            self.build_email(
                address='%s@%s' % (TEST_LOGIN, 'gmail.com'),
                is_native=False,
                is_2fa_on=is_2fa_on,
                is_hint_created=is_hint_created,
            ),
            self.build_email(
                address='%s@%s' % (TEST_LOGIN, 'yandex.ru'),
                is_native=True,
                is_2fa_on=is_2fa_on,
                is_hint_created=is_hint_created,
            ),
        ])

    def build_email(self, address, is_native, is_2fa_on=False, is_hint_created=False):
        masked_login = TEST_LOGIN if is_native else TEST_LOGIN[:2] + '***'
        data = {
            'language': 'ru',
            'addresses': [address],
            'subject': 'hint_created.subject' if is_hint_created else 'hint_changed.subject',
            'tanker_keys': {
                'greeting': {'FIRST_NAME': TEST_FIRSTNAME},
                'in_this_case': {},
                'hint_common.info': {},
                'hint_common.phone_promo': {},
                'hint_common.phone_info': {
                    'HELP_PHONES_URL_BEGIN': NOTIFICATIONS_URL_BEGIN % 'https://yandex.ru/support/passport/authorization/phone.html',
                    'HELP_PHONES_URL_END': NOTIFICATIONS_URL_END,
                },
                'signature.secure': {},
            },
        }
        if is_hint_created:
            data['tanker_keys'].update({
                'hint_created.notice': {'MASKED_LOGIN': masked_login},
                'hint_created.warning_info': {},
                'hint_created.correct_hint': {
                    'CHANGE_HINT_URL_BEGIN': NOTIFICATIONS_URL_BEGIN % 'https://passport.yandex.ru/passport?mode=changehint',
                    'CHANGE_HINT_URL_END': NOTIFICATIONS_URL_END,
                },
            })
        else:
            data['tanker_keys'].update({
                'hint_changed.notice': {'MASKED_LOGIN': masked_login},
                'hint_changed.warning_info': {},
                'hint_changed.correct_hint': {
                    'CHANGE_HINT_URL_BEGIN': NOTIFICATIONS_URL_BEGIN % 'https://passport.yandex.ru/passport?mode=changehint',
                    'CHANGE_HINT_URL_END': NOTIFICATIONS_URL_END,
                },
            })

        if is_2fa_on:
            data['tanker_keys']['restore'] = {
                'RESTORE_URL_BEGIN': NOTIFICATIONS_URL_BEGIN % 'https://passport.yandex.ru/restoration',
                'RESTORE_URL_END': NOTIFICATIONS_URL_END,
            }
        else:
            data['tanker_keys']['change_password'] = {
                'CHANGE_PASSWORD_URL_BEGIN': NOTIFICATIONS_URL_BEGIN % 'https://passport.yandex.ru/profile/password',
                'CHANGE_PASSWORD_URL_END': NOTIFICATIONS_URL_END,
            }
            data['tanker_keys']['restore_after_change_password'] = {
                'RESTORE_URL_BEGIN': NOTIFICATIONS_URL_BEGIN % 'https://passport.yandex.ru/restoration',
                'RESTORE_URL_END': NOTIFICATIONS_URL_END,
            }
        return data

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='questions_change',
        )
        self.env.statbox.bind_entry(
            'local_base',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_VALUE,
            host=TEST_HOST,
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'committed',
            _inherit_from='local_base',
            action='committed',
            authid=TEST_AUTH_ID,
            track_id=self.track_id,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'local_account_modification',
            _exclude=['mode', 'host', 'yandexuid'],
            _inherit_from=['account_modification', 'local_base'],
            operation='updated',
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'limit_exceeded',
            _inherit_from='local_base',
            action='limit_exceeded',
            track_id=self.track_id,
            uid=str(TEST_UID),
        )

    def test_ok(self):
        self.set_blackbox_response()
        self.setup_track()

        self.check_db_entries()
        resp = self.make_request()

        self.assert_ok_response(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'local_account_modification',
                entity='hint.question',
            ),
            self.env.statbox.entry(
                'local_account_modification',
                entity='hint.answer',
                operation='updated',
            ),
            self.env.statbox.entry('committed'),
        ])
        self.check_emails_sent()
        self.check_db_entries(
            question_id=TEST_HINT_QUESTION_ID1,
            question_text=TEST_HINT_QUESTION_TEXT1,
            answer=TEST_HINT_ANSWER,
        )
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP,
            event_name='hint_change',
            uid=TEST_UID,
            title='Контрольный вопрос в аккаунте login изменён',
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
            context='{"track_id": "%s"}' % self.track_id,
        )

    def test_no_track_error(self):
        resp = self.make_request(exclude_args=['track_id'])
        self.assert_error_response(resp, ['track_id.empty'])
        self.env.email_toolkit.assert_no_emails_sent()

    def test_wrong_track(self):
        resp = self.make_request(query_args=dict(track_id='111'))
        self.assert_error_response(resp, ['track_id.invalid'])
        self.env.email_toolkit.assert_no_emails_sent()

    def test_no_uid_in_track_error(self):
        no_uid_track_data = deepcopy(self.default_track_data)
        no_uid_track_data.pop('uid')
        self.setup_track(no_uid_track_data)
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        self.env.email_toolkit.assert_no_emails_sent()

    def test_form_invalid(self):
        resp = self.make_request(query_args=dict(question='question2'))
        self.assert_error_response(resp, ['form.invalid'])
        self.env.email_toolkit.assert_no_emails_sent()

    def test_no_password_social_redirect_state(self):
        account_data = deepcopy(self.account_data)
        account_data.update(aliases={'social': TEST_LOGIN})
        self.set_blackbox_response(have_password=False, **account_data)
        self.setup_track()
        resp = self.make_request()
        expected_response = deepcopy(TEST_ACCOUNT_DATA)
        expected_response['account'].update(display_login='')
        expected_response['account'].pop('is_2fa_enabled')
        expected_response['account'].pop('is_rfc_2fa_enabled')
        expected_response['account'].pop('is_yandexoid')
        expected_response['account'].pop('is_workspace_user')
        self.assert_ok_response(
            resp,
            state='complete_social',
            track_id=self.track_id,
            **expected_response
        )
        self.env.email_toolkit.assert_no_emails_sent()
        self.check_db_entries()

    def test_no_password_error(self):
        self.set_blackbox_response(have_password=False)
        self.setup_track()
        resp = self.make_request()
        self.assert_error_response(resp, ['account.without_password'])
        self.env.email_toolkit.assert_no_emails_sent()
        self.check_db_entries()

    def test_account_disabled_error(self):
        account_data = deepcopy(self.account_data)
        account_data.update(enabled=False)
        self.set_blackbox_response(**account_data)
        self.setup_track()
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled'])
        self.env.email_toolkit.assert_no_emails_sent()
        self.check_db_entries()

    def test_no_hint_ok(self):
        self.set_blackbox_response(with_hint=False)
        self.setup_track()
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'local_account_modification',
                entity='hint.question',
                operation='created',
            ),
            self.env.statbox.entry(
                'local_account_modification',
                entity='hint.answer',
                operation='created',
            ),
            self.env.statbox.entry('committed'),
        ])
        self.check_emails_sent(is_hint_created=True)
        self.check_db_entries(
            question_id=TEST_HINT_QUESTION_ID1,
            question_text=TEST_HINT_QUESTION_TEXT1,
            answer=TEST_HINT_ANSWER,
        )

    def test_phones_state_to_response(self):
        self.set_blackbox_response(with_phones=False)
        self.setup_track()
        resp = self.make_request()
        self.assert_ok_response(resp, need_to_bind_phone=True)
        self.check_emails_sent()
        self.check_db_entries(
            question_id=TEST_HINT_QUESTION_ID1,
            question_text=TEST_HINT_QUESTION_TEXT1,
            answer=TEST_HINT_ANSWER,
        )

    def test_2fa_enabled_ok(self):
        self.set_blackbox_response(is_2fa_on=True)
        self.setup_track()
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_emails_sent(is_2fa_on=True)
        self.check_db_entries(
            question_id=TEST_HINT_QUESTION_ID1,
            question_text=TEST_HINT_QUESTION_TEXT1,
            answer=TEST_HINT_ANSWER,
        )

    def test_last_password_verified_by_track(self):
        self.set_blackbox_response(password_age=400)
        track_data = deepcopy(self.default_track_data)
        track_data.update(password_verification_passed_at=datetime_to_integer_unixtime(DatetimeNow()))
        self.setup_track(track_data)
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_emails_sent()
        self.check_db_entries(
            question_id=TEST_HINT_QUESTION_ID1,
            question_text=TEST_HINT_QUESTION_TEXT1,
            answer=TEST_HINT_ANSWER,
        )

    def test_wrong_answer_no_need_captcha(self):
        self.set_blackbox_response()
        self.setup_track()
        resp = self.make_request(query_args=dict(answer='abc'))
        self.assert_error_response(resp, ['compare.not_matched'])
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        ok_(not track.is_captcha_required)
        self.check_db_entries()
        self.env.email_toolkit.assert_no_emails_sent()

    def test_compare_answers_ok(self):
        self.set_blackbox_response()
        self.setup_track()
        resp = self.make_request(query_args=dict(answer=self.http_query_args['answer'] + 'bbb'))
        self.assert_ok_response(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'local_account_modification',
                entity='hint.question',
            ),
            self.env.statbox.entry(
                'local_account_modification',
                entity='hint.answer',
                operation='updated',
            ),
            self.env.statbox.entry('committed'),
        ])
        self.check_db_entries(
            question_id=TEST_HINT_QUESTION_ID1,
            question_text=TEST_HINT_QUESTION_TEXT1,
            answer=TEST_HINT_ANSWER,
        )
        self.check_emails_sent()

    def test_compare_answers_with_long_previous_one(self):
        self.set_blackbox_response(old_hint=TEST_HINT_ANSWER_LONG)
        self.setup_track()
        resp = self.make_request(query_args=dict(answer=self.http_query_args['answer'] + 'bbb'))
        self.assert_ok_response(resp)
        self.check_db_entries(
            question_id=TEST_HINT_QUESTION_ID1,
            question_text=TEST_HINT_QUESTION_TEXT1,
            answer=TEST_HINT_ANSWER,
        )
        self.check_emails_sent()

    def test_compare_answers_empty_error(self):
        self.set_blackbox_response()
        self.setup_track()
        resp = self.make_request(exclude_args=['answer'])
        self.assert_error_response(resp, ['compare.not_matched'])
        self.check_db_entries()
        self.env.email_toolkit.assert_no_emails_sent()

    def test_rate_limits_exceeded_by_uid(self):
        self.set_blackbox_response()
        self.setup_track()

        counter = check_answer_counter.get_per_uid_buckets()
        # установим счетчик вызовов на uid в limit
        for _ in range(counter.limit):
            counter.incr(TEST_UID)

        # сразу падаем
        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.check_db_entries()
        self.env.email_toolkit.assert_no_emails_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('limit_exceeded'),
        ])

    def test_rate_limit_exceeded_by_ip_first(self):
        self.set_blackbox_response()
        self.setup_track()

        counter_uid = check_answer_counter.get_per_uid_buckets()
        # установим счетчик вызовов на uid в limit - 1
        for _ in range(counter_uid.limit - 1):
            counter_uid.incr(TEST_UID)

        counter_ip = check_answer_counter.get_per_ip_buckets()
        # установим счетчик вызовов на ip в limit
        for _ in range(counter_ip.limit):
            counter_ip.incr(TEST_USER_IP)

        # Какая ирония, мы угадали ответ. Падаем по лимиту IP
        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.check_db_entries()
        self.env.email_toolkit.assert_no_emails_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('limit_exceeded'),
        ])

    def test_ok_with_email_limit_exceed(self):
        self.set_blackbox_response()
        self.setup_track()

        self.check_db_entries()
        question_change_email_counter.incr(TEST_UID)

        resp = self.make_request()
        self.assert_ok_response(resp)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'local_account_modification',
                entity='hint.question',
            ),
            self.env.statbox.entry(
                'local_account_modification',
                entity='hint.answer',
                operation='updated',
            ),
            self.env.statbox.entry('committed'),
        ])

        self.env.email_toolkit.assert_no_emails_sent()
        self.check_db_entries(
            question_id=TEST_HINT_QUESTION_ID1,
            question_text=TEST_HINT_QUESTION_TEXT1,
            answer=TEST_HINT_ANSWER,
        )
