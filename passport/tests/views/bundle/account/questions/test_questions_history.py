# -*- coding: utf-8 -*-

import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.counters import check_answer_per_ip_and_uid_counter
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import merge_dicts


TEST_UID = '1'
TEST_LOGIN = 'user1'
TEST_IP = '127.0.0.1'
TEST_HOST = 'passport.yandex.ru'
TEST_ANSWER = 'answer'
TEST_HINT_QUESTION = u'Ваш любимый учитель'
TEST_SECURE_PHONE_NUMBER = '+79261234567'


class TestTranslationSettings(object):

    QUESTIONS = {
        'ru': {'11': TEST_HINT_QUESTION},
    }
    TANKER_DEFAULT_KEYSET = 'NOTIFICATIONS'


class QuestionsHistoryTestCaseBase(BaseBundleTestViews):

    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'questions': ['base']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        self.setup_track()

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                dbfields={
                    'userinfo.reg_date.uid': '2010-10-10 00:00:00',
                    'userinfo_safe.hintq.uid': 'вопрос',
                    'userinfo_safe.hinta.uid': 'ответ',
                },
            ),
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.is_password_change = True

    def assert_ok_response(self, resp, **kwargs):
        base_response = {
            'status': 'ok',
        }
        body = json.loads(resp.data)
        eq_(resp.status_code, 200)
        eq_(
            body,
            merge_dicts(base_response, kwargs),
        )


class GetQuestionsHistoryTestCase(QuestionsHistoryTestCaseBase):

    default_url = '/1/account/questions/history/get/'
    http_method = 'get'

    def setUp(self):
        super(GetQuestionsHistoryTestCase, self).setUp()

        self.http_query_args = dict(
            consumer='dev',
            display_language='ru',
            track_id=self.track_id,
        )

    def test_track_id_empty_error(self):
        """
        Пришли без track_id
        """
        resp = self.make_request(exclude_args=['track_id'])
        self.assert_error_response(resp, ['track_id.empty'])

    def test_track_invalid_state_error(self):
        """
        Пришли с треком не от принудительной смены пароля
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = False
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])

    def test_account_disabled_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID, enabled=False),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled'])

    def test_account_disabled_on_deletion_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled_on_deletion'])

    def test_account_has_secured_number_error(self):
        phone_secured = build_phone_secured(
            1,
            TEST_SECURE_PHONE_NUMBER,
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                dbfields={
                    'userinfo_safe.hintq.uid': 'вопрос',
                    'userinfo_safe.hinta.uid': 'ответ',
                },
                **phone_secured
            ),
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            questions=[
                {
                    'id': 0,
                    'text': u'вопрос',
                },
            ],
        )

    def test_ok_with_no_hint(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                dbfields={
                    'userinfo.reg_date.uid': '2010-10-10 00:00:00',
                },
            ),
        )

        resp = self.make_request()
        self.assert_ok_response(resp, questions=[])


class CheckQuestionAnswerHistoryTestCase(QuestionsHistoryTestCaseBase):

    default_url = '/1/account/questions/history/check/?consumer=dev'
    http_method = 'post'

    def setUp(self):
        super(CheckQuestionAnswerHistoryTestCase, self).setUp()

        self.http_query_args = dict(
            track_id=self.track_id,
            display_language='ru',
            question_id='1',
            answer=TEST_ANSWER,
            question=TEST_HINT_QUESTION,
        )

    def assert_statbox_ok(self, action, **kwargs):
        entry = self.env.statbox.entry(
            'base',
            unixtime=TimeNow(),
            ip=TEST_IP,
            uid=TEST_UID,
            track_id=self.track_id,
            mode='account_questions_history_check',
            action=action,
            **kwargs
        )
        self.env.statbox.assert_has_written([entry])

    def test_track_id_empty_error(self):
        """
        Пришли без track_id
        """
        resp = self.make_request(exclude_args=['track_id'])
        self.assert_error_response(resp, ['track_id.empty'])

    def test_question_id_empty_error(self):
        """
        Пришли без question_id
        """
        resp = self.make_request(exclude_args=['question_id'])
        self.assert_error_response(resp, ['question_id.empty'])

    def test_answer_empty_error(self):
        """
        Пришли без answer
        """
        resp = self.make_request(exclude_args=['answer'])
        self.assert_error_response(resp, ['answer.empty'])

    def test_track_invalid_state_error(self):
        """
        Пришли с треком не от принудительной смены пароля
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = False
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])

    def test_account_disabled_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID, enabled=False),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled'])

    def test_account_disabled_on_deletion_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled_on_deletion'])

    def test_per_ip_and_uid_limit_exceeded_error(self):
        """
        Проверим, что защитились счетчиком по паре (ip, uid) от перебора
        """
        counter = check_answer_per_ip_and_uid_counter.get_per_ip_and_uid_buckets()
        # установим счетчик вызовов на (ip, uid) в limit + 1
        for i in range(counter.limit + 1):
            counter.incr('%s:%s' % (TEST_IP, TEST_UID))

        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_statbox_ok('limit_exceeded')

    def test_per_ip_limit_exceeded_error(self):
        """
        Проверим, что защитились счетчиком по ip от перебора
        """
        counter = check_answer_per_ip_and_uid_counter.get_per_ip_buckets()
        # установим счетчик вызовов на ip в limit + 1
        for i in range(counter.limit + 1):
            counter.incr(TEST_IP)

        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_statbox_ok('limit_exceeded')

    def test_check_hint_error(self):
        """
        Проверяем текущий КВ-КО на аккаунте.
        Ответ не совпадает.
        """
        resp = self.make_request()
        self.assert_error_response(resp, ['compare.not_matched'])
        self.assert_statbox_ok(
            'compared',
            answer_compare_factors='0, 1.00, 0.50, 0.00, 0.00, 1',
            check_passed='0',
        )
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_fuzzy_hint_answer_checked)

    def test_check_hint_ok(self):
        """
        Проверяем текущий КВ-КО на аккаунте.
        Ответ подходит.
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                dbfields={
                    'userinfo.reg_date.uid': '2010-10-10 00:00:00',
                    'userinfo_safe.hintq.uid': 'вопрос',
                    'userinfo_safe.hinta.uid': TEST_ANSWER[:-1],  # проверим что сравнение нечеткое
                },
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_statbox_ok(
            'compared',
            answer_compare_factors='0, 1.00, 0.83, 0.67, -1, -1',
            check_passed='1',
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.is_fuzzy_hint_answer_checked)
