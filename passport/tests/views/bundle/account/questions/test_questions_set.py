# -*- coding: utf-8 -*-

import freezegun
from nose.tools import eq_
from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    EmailTestMixin,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.mdapi.base_test_data import (
    TEST_ACCEPT_LANGUAGE,
    TEST_HOST,
    TEST_IP,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.test.consts import TEST_LOGIN1
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts


# FIXME: грязный хак - надо почистить вместе с чисткой всех данных для тестирования

TEST_QUESTIONS_BASE_GRANT = 'questions.base'
TEST_QUESTIONS_EDIT_NORMAL_GRANT = 'questions.edit_normal'
TEST_QUESTIONS_EDIT_PDD_GRANT = 'questions.edit_pdd'

TEST_PDD_LOGIN = 'amy@tard.is'
TEST_LITE_LOGIN = 'test_user@okna.ru'
TEST_UID = 1
TEST_PDD_UID = 1130000000000001
TEST_HINT_QUESTION = 'Доктор?'
TEST_PREDEFINED_HINT_QUESTION = 'Девичья фамилия матери'
TEST_HINT_ANSWER = 'Кто'
TEST_DISPLAY_LANGUAGE = 'ru'
TEST_QUESTION_ID = 1
TEST_FREE_QUESTION_ID = 99


@with_settings_hosts(
    ACCOUNT_MODIFICATION_MAIL_ENABLE={'hint_change'},
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'hint_change'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'email:hint_change': 5,
            'push:hint_change': 5,
        },
    )
)
class TestQuestionsSetQuestionView(
    EmailTestMixin,
    BaseBundleTestViews,
    AccountModificationNotifyTestMixin,
):
    default_url = '/1/account/questions/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        question=TEST_HINT_QUESTION,
        answer=TEST_HINT_ANSWER,
    )
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='questions_set',
            user_agent='curl',
        )
        for action_name in ['submitted', 'hint_set']:
            self.env.statbox.bind_entry(
                action_name,
                action=action_name,
                ip='3.3.3.3',
            )
        self.env.statbox.bind_entry(
            'account_modification',
            _exclude=['mode'],
            event='account_modification',
            ip='3.3.3.3',
            consumer='dev',
            user_agent='curl',
        )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_manager = self.env.track_manager.get_manager()

        self.env.grants.set_grant_list([
            TEST_QUESTIONS_BASE_GRANT,
            TEST_QUESTIONS_EDIT_NORMAL_GRANT,
            TEST_QUESTIONS_EDIT_PDD_GRANT,
        ])

        self.setup_statbox_templates()

        self.userinfo = dict(
            login=TEST_LOGIN1,
            uid=TEST_UID,
        )
        self.setup_blackbox()
        self.start_account_modification_notify_mocks(
            ip=TEST_IP,
        )
        self.setup_kolmogor()

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_blackbox(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**self.userinfo),
        )

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ] * 2,
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'] * 2)

    def check_historydb_entries(self, uid=TEST_UID,
                                question_id=TEST_FREE_QUESTION_ID,
                                question=TEST_HINT_QUESTION, answer=TEST_HINT_ANSWER):
        historydb_record = [
            ('info.hintq', '%d:%s' % (question_id, question) if question_id or question else '-'),
            ('info.hinta', answer or '-'),
            ('action', 'questions_set'),
            ('consumer', 'dev'),
            ('user_agent', 'curl'),
        ]

        historydb_entries = [
            {
                'uid': str(uid),
                'name': k,
                'value': v,
            }
            for k, v in historydb_record if v is not None
        ]

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            historydb_entries,
        )

        parsed_events = self.env.event_logger.parse_events()
        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'questions')
        eq_(
            parsed_events[0].actions,
            [{
                'type': 'questions_change',
            }],
        )

    def check_db_entries(self, uid=TEST_UID, question_id=TEST_FREE_QUESTION_ID,
                         question=TEST_HINT_QUESTION, answer=TEST_HINT_ANSWER):
        present_attributes = []
        if question or question_id:
            present_attributes.append(('hint.question.serialized', '%d:%s' % (question_id, question)))
        if answer:
            present_attributes.append(('hint.answer.encrypted', answer))

        for attribute_name, value in present_attributes:
            self.env.db.check(
                'attributes',
                attribute_name,
                value,
                uid=uid,
                db='passportdbshard1' if uid == TEST_UID else 'passportdbshard2',
            )

    def check_statbox_entries(self, uid=TEST_UID, answer=True, question=True, with_check_cookies=False):
        expected_entries = [self.env.statbox.entry('submitted')]
        if with_check_cookies:
            expected_entries.append(self.env.statbox.entry('check_cookies'))
        if question:
            expected_entries += [
                self.env.statbox.entry(
                    'account_modification',
                    operation='created',
                    uid=str(uid),
                    entity='hint.question',
                ),
            ]
        if answer:
            expected_entries += [
                self.env.statbox.entry(
                    'account_modification',
                    operation='created',
                    uid=str(uid),
                    entity='hint.answer',
                ),
            ]
        expected_entries += [self.env.statbox.entry('hint_set')]

        self.env.statbox.assert_has_written(expected_entries)

    def test_set_plain_text_question(self):
        resp = self.make_request()

        self.assert_ok_response(resp)
        self.check_historydb_entries()
        self.check_statbox_entries(with_check_cookies=True)
        self.check_db_entries()
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='hint_change',
            uid=TEST_UID,
            title='Контрольный вопрос в аккаунте %s изменён' % self.userinfo['login'],
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
        )

    @freezegun.freeze_time()
    def test_send_mail_when_password_changed(self):
        email = self.create_native_email(TEST_LOGIN1, 'yandex.ru')
        self.userinfo.update(emails=[email])
        self.setup_blackbox()

        resp = self.make_request()

        self.assert_ok_response(resp)

        self.assert_emails_sent([
            self.create_account_modification_mail(
                'hint_change',
                email['address'],
                dict(login=self.userinfo['login']),
            ),
        ])

    def test_set_plain_text_question_for_pdd(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_PDD_UID,
                aliases=dict(pdd=TEST_PDD_LOGIN),
            ),
        )

        resp = self.make_request()

        self.assert_ok_response(resp)
        self.check_historydb_entries(uid=TEST_PDD_UID)
        self.check_statbox_entries(uid=TEST_PDD_UID, with_check_cookies=True)
        self.check_db_entries(uid=TEST_PDD_UID)

    def test_set_plain_text_question_for_pdd_by_uid__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_PDD_UID),
        )
        resp = self.make_request(query_args={'uid': TEST_PDD_UID}, exclude_headers=['cookie'])

        self.assert_ok_response(resp)
        self.check_historydb_entries(uid=TEST_PDD_UID)
        self.check_statbox_entries(uid=TEST_PDD_UID)
        self.check_db_entries(uid=TEST_PDD_UID)

    def test_no_by_uid_grant(self):
        self.env.grants.set_grant_list([
            TEST_QUESTIONS_BASE_GRANT,
            TEST_QUESTIONS_EDIT_NORMAL_GRANT,
        ])
        resp = self.make_request(query_args={'uid': TEST_UID}, exclude_headers=['cookie'])

        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_error_edit_normal_without_grants(self):
        self.env.grants.set_grant_list([
            TEST_QUESTIONS_BASE_GRANT,
            TEST_QUESTIONS_EDIT_PDD_GRANT,
        ])

        resp = self.make_request()
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_error_edit_pdd_without_grants(self):
        self.env.grants.set_grant_list([
            TEST_QUESTIONS_BASE_GRANT,
            TEST_QUESTIONS_EDIT_NORMAL_GRANT,
        ])
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_PDD_UID,
                aliases=dict(pdd=TEST_PDD_LOGIN),
            ),
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_set_question_by_id(self):
        resp = self.make_request(
            query_args=dict(
                question_id=TEST_QUESTION_ID,
                display_language=TEST_DISPLAY_LANGUAGE,
            ),
            exclude_args=['question'],
        )
        self.assert_ok_response(resp)
        self.check_historydb_entries(
            question=TEST_PREDEFINED_HINT_QUESTION,
            question_id=TEST_QUESTION_ID,
        )
        self.check_statbox_entries(with_check_cookies=True)
        self.check_db_entries(
            question=TEST_PREDEFINED_HINT_QUESTION,
            question_id=TEST_QUESTION_ID,
        )

    def test_error_account_invalid_type(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_PDD_UID,
                aliases=dict(phonish='+79033123456'),
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_pdd_without_answer__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_PDD_UID,
                aliases=dict(pdd=TEST_PDD_LOGIN),
            ),
        )

        resp = self.make_request(exclude_args=['answer'])

        self.assert_ok_response(resp)
        self.check_historydb_entries(uid=TEST_PDD_UID, answer=None)
        self.check_statbox_entries(uid=TEST_PDD_UID, answer=False, with_check_cookies=True)
        self.check_db_entries(uid=TEST_PDD_UID, answer=None)

    def test_pdd_question_id__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_PDD_UID,
                aliases=dict(pdd=TEST_PDD_LOGIN),
            ),
        )
        resp = self.make_request(
            query_args=dict(
                question_id=TEST_QUESTION_ID,
                display_language=TEST_DISPLAY_LANGUAGE,
            ),
            exclude_args=['question', 'answer'],
        )
        self.assert_ok_response(resp)
        self.check_historydb_entries(
            question=TEST_PREDEFINED_HINT_QUESTION,
            question_id=TEST_QUESTION_ID,
            uid=TEST_PDD_UID,
            answer=False,
        )
        self.check_statbox_entries(uid=TEST_PDD_UID, answer=False, with_check_cookies=True)
        self.check_db_entries(
            question=TEST_PREDEFINED_HINT_QUESTION,
            question_id=TEST_QUESTION_ID,
            uid=TEST_PDD_UID,
            answer=None,
        )

    def test_pdd_without_questions__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_PDD_UID,
                aliases=dict(pdd=TEST_PDD_LOGIN),
            ),
        )

        resp = self.make_request(exclude_args=['question'])

        self.assert_ok_response(resp)
        self.check_statbox_entries(uid=TEST_PDD_UID, question=False, with_check_cookies=True)
        self.check_db_entries(uid=TEST_PDD_UID, question=None, question_id=None)
        self.check_historydb_entries(uid=TEST_PDD_UID, question=None, question_id=None)

    def test_normal_without_answer__error(self):
        resp = self.make_request(exclude_args=['answer'])
        self.assert_error_response(resp, ['answer.empty'])

    def test_normal_without_question__error(self):
        resp = self.make_request(exclude_args=['question'])
        self.assert_error_response(resp, ['question.empty'])
