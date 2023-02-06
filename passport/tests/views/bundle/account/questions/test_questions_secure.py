# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.account.questions.controllers import (
    QUESTIONS_BASE_GRANT,
    QUESTIONS_SECURE_BY_UID_GRANT,
    QUESTIONS_SECURE_GRANT,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.counters import check_answer_counter
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow


TEST_LOGIN = 'login'
TEST_UID = 1
TEST_PDD_UID = 1130000000000001
TEST_COMMENT = 'comment'
TEST_TIMESTAMP = 123456
TEST_WEAK_PASSWORD_HASH = '$1$y0aXFE9w$JqrpPZ74WT1Hi/Mb53cTe.'
TEST_SESSIONID = 'sessionid'
TEST_COOKIE = 'Session_id=%s' % TEST_SESSIONID
TEST_EDA_COOKIE = 'Eda_id=%s' % TEST_SESSIONID
TEST_HOST = 'passport-test.yandex.ru'
TEST_USER_IP = '3.3.3.3'
TEST_QUESTION_ID = 99
TEST_QUESTION_TEXT = 'question'
TEST_QUESTION = '%d:%s' % (TEST_QUESTION_ID, TEST_QUESTION_TEXT)
TEST_ANSWER = 'answer'
TEST_NO_MATCH_COMPARE_REASON = 'FuzzyComparatorBase.no_match'
TEST_MATCH_COMPARE_REASON = 'InitialComparator.equal'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
)
class TestQuestionAnswerBase(BaseBundleTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.set_grants()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            unixtime=TimeNow(),
            mode='account_questions_secure_check',
            ip=TEST_USER_IP,
            track_id=self.track_id,
            uid=str(TEST_UID),

        )
        self.env.statbox.bind_entry(
            'compared',
            action='compared',
        )
        self.env.statbox.bind_entry(
            'limit_exceeded',
            action='limit_exceeded',
        )
        self.env.statbox.bind_entry(
            'captcha_limit_exceeded',
            action='captcha_limit_exceeded',
        )

    def set_grants(self, by_uid=False):
        grants = {}
        for grant in (QUESTIONS_BASE_GRANT, QUESTIONS_SECURE_GRANT):
            prefix, suffix = grant.split('.')
            grants.setdefault(prefix, []).append(suffix)
        if by_uid:
            prefix, suffix = QUESTIONS_SECURE_BY_UID_GRANT.split('.')
            grants.setdefault(prefix, []).append(suffix)
        self.env.grants.set_grants_return_value(mock_grants(grants=grants))

    def _hint_dbfields(self, return_hint, question, answer):
        if not return_hint:
            return {}
        return {
            'userinfo_safe.hintq.uid': question,
            'userinfo_safe.hinta.uid': answer,
        }

    def default_userinfo_response(self, uid=TEST_UID, enabled=True, return_hint=True,
                                  question=TEST_QUESTION, answer=TEST_ANSWER, attributes=None):
        dbfields = self._hint_dbfields(
            return_hint,
            question,
            answer,
        )
        return blackbox_userinfo_response(
            uid=uid,
            enabled=enabled,
            dbfields=dbfields,
            attributes=attributes,
        )

    def default_sessionid_response(self, uid=TEST_UID, return_hint=True,
                                   question=TEST_QUESTION, answer=TEST_ANSWER):
        dbfields = self._hint_dbfields(return_hint, question, answer)
        return blackbox_sessionid_multi_response(uid=uid, dbfields=dbfields)


class TestGetQuestionView(TestQuestionAnswerBase):

    default_url = '/1/account/questions/secure/'
    http_method = 'get'
    http_headers = dict(
        user_ip=TEST_USER_IP,
        cookie=TEST_COOKIE,
        host=TEST_HOST,
    )

    def setUp(self):
        super(TestGetQuestionView, self).setUp()

        self.http_query_args = dict(
            consumer='dev',
            track_id=self.track_id,
        )

    def get_expected_response(self):
        return {
            'question': {
                'id': TEST_QUESTION_ID,
                'text': TEST_QUESTION_TEXT,
            },
            'track_id': self.track_id,
        }

    def assert_track_ok(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))

    def test_no_uid_and_session_fails(self):
        resp = self.make_request(exclude_headers=['cookie'])
        self.assert_error_response(resp, ['request.credentials_all_missing'], track_id=self.track_id)

    def test_both_uid_sessionid_fails(self):
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            headers=dict(cookie='Session_id='),
        )
        self.assert_error_response(resp, ['request.credentials_several_present'], track_id=self.track_id)

    def test_unknown_uid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        self.set_grants(by_uid=True)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        self.assert_error_response(resp, ['account.not_found'], track_id=self.track_id)

    def test_by_uid_no_grant_fails(self):
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_disabled_uid_account_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(enabled=False),
        )
        self.set_grants(by_uid=True)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        self.assert_error_response(resp, ['account.disabled'], track_id=self.track_id)

    def test_disabled_uid_on_deletion_account_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        self.set_grants(by_uid=True)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        self.assert_error_response(resp, ['account.disabled_on_deletion'], track_id=self.track_id)

    def test_invalid_sessionid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                uid=TEST_UID,
            ),
        )
        resp = self.make_request(headers=dict(cookie='Session_id='))
        self.assert_error_response(resp, ['sessionid.invalid'], track_id=self.track_id)

    def test_invalid_sessionid_fails_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                uid=TEST_UID,
            ),
        )
        resp = self.make_request(headers=dict(cookie='Session_id='))
        self.assert_error_response(resp, ['sessionid.invalid'], track_id=self.track_id)

    def test_disabled_sessionid_account_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                uid=TEST_UID,
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled'], track_id=self.track_id)

    def test_disabled_on_deletion_sessionid_account_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                uid=TEST_UID,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled_on_deletion'], track_id=self.track_id)

    def test_disabled_sessionid_account_fails_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                uid=TEST_UID,
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled'], track_id=self.track_id)

    def test_disabled_on_deletion_sessionid_account_fails_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                uid=TEST_UID,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled_on_deletion'], track_id=self.track_id)

    def test_by_uid_no_question_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(return_hint=False),
        )
        self.set_grants(by_uid=True)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        self.assert_error_response(resp, ['account.no_question'], track_id=self.track_id)

    def test_by_uid_empty_question_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(question=''),
        )
        self.set_grants(by_uid=True)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        self.assert_error_response(resp, ['account.no_question'], track_id=self.track_id)

    def test_by_uid_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_grants(by_uid=True)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        self.assert_ok_response(resp, **self.get_expected_response())
        self.assert_track_ok()

    def test_by_sessionid_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **self.get_expected_response())
        self.assert_track_ok()

    def test_by_track_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID

        resp = self.make_request()
        self.assert_ok_response(resp, **self.get_expected_response())
        self.assert_track_ok()


class TestCheckAnswerViewBase(TestQuestionAnswerBase):

    default_url = '/1/account/questions/secure/check/?consumer=dev'
    http_method = 'post'
    http_headers = dict(
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        super(TestCheckAnswerViewBase, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID

        self.http_query_args = dict(
            track_id=self.track_id,
            answer=TEST_ANSWER,
        )

    def setup_blackbox_response(self, uid=TEST_UID, return_hint=True, enabled=True, attributes=None):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                uid=uid,
                return_hint=return_hint,
                enabled=enabled,
                attributes=attributes,
            ),
        )

    def assert_track_ok(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        ok_(track.is_secure_hint_answer_checked)

    def assert_statbox_clean(self):
        self.env.statbox.assert_has_written([])

    def assert_compared_recorded_to_statbox(self, check_passed):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'compared',
                check_passed=tskv_bool(check_passed),
            ),
        ])

    def assert_limits_exceeded_recorded_to_statbox(self):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'compared',
                check_passed=tskv_bool(True),
            ),
            self.env.statbox.entry('limit_exceeded'),
        ])


class TestCheckAnswerView(TestCheckAnswerViewBase):
    def test_unknown_uid_fails(self):
        self.setup_blackbox_response(uid=None)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'])
        self.assert_statbox_clean()

    def test_invalid_track_state_fails(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = None
        self.setup_blackbox_response(uid=None)
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        self.assert_statbox_clean()

    def test_account_no_answer_fails(self):
        self.setup_blackbox_response(return_hint=False)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.no_answer'])
        self.assert_statbox_clean()

    def test_wrong_answer_ok(self):
        self.setup_blackbox_response()
        resp = self.make_request(query_args=dict(answer=list(reversed(TEST_ANSWER))))
        self.assert_error_response(resp, ['compare.not_matched'])
        self.assert_compared_recorded_to_statbox(check_passed=False)

    def test_right_answer_ok(self):
        self.setup_blackbox_response()
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_compared_recorded_to_statbox(check_passed=True)
        self.assert_track_ok()

    def test_check_per_uid_overflow_fails(self):
        self.setup_blackbox_response()

        counter = check_answer_counter.get_per_uid_buckets()
        # установим счетчик вызовов на uid в limit - 1
        for i in range(counter.limit - 1):
            counter.incr(TEST_UID)

        # первый вызов должен отработать нормально
        resp = self.make_request()
        self.assert_ok_response(resp)

        # второй вызов должен сообщить о превышении лимита запросов
        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_limits_exceeded_recorded_to_statbox()

    def test_disabled_uid_on_deletion_account_fails(self):
        attributes = {
            'account.is_disabled': '2',
        }
        self.setup_blackbox_response(enabled=False, attributes=attributes)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled_on_deletion'])


class TestCheckAnswerViewV2(TestCheckAnswerViewBase):
    def setUp(self):
        super(TestCheckAnswerViewV2, self).setUp()
        self.default_url = '/1/bundle/account/questions/secure/check/?consumer=dev'
        self.setup_blackbox_response()

    def setup_track_captcha_passed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

    def assert_captcha_required(self):
        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('captcha_limit_exceeded'),
        ])

    def test_right_answer_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp)
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_captcha_required)

    def test_wrong_answer_till_captcha_by_uid__clean_track(self):
        with settings_context(CHECK_ANSWER_UNTIL_CAPTCHA_LIMIT_BY_UID=2):
            counter = check_answer_counter.get_per_uid_buckets()
            for _ in range(settings.CHECK_ANSWER_UNTIL_CAPTCHA_LIMIT_BY_UID):
                counter.incr(TEST_UID)
            resp = self.make_request(query_args=dict(answer=list(reversed(TEST_ANSWER))))
        self.assert_error_response(resp, ['captcha.required'])
        self.assert_captcha_required()

    def test_wrong_answer_till_captcha_by_ip__clean_track(self):
        with settings_context(CHECK_ANSWER_UNTIL_CAPTCHA_LIMIT_BY_IP=3):
            counter = check_answer_counter.get_per_ip_buckets()
            for _ in range(settings.CHECK_ANSWER_UNTIL_CAPTCHA_LIMIT_BY_IP):
                counter.incr(TEST_USER_IP)
            resp = self.make_request(query_args=dict(answer=list(reversed(TEST_ANSWER))))
        self.assert_error_response(resp, ['captcha.required'])
        self.assert_captcha_required()

    def test_wrong_answer_till_captcha_by_uid__captcha_passed(self):
        self.setup_track_captcha_passed()

        with settings_context(CHECK_ANSWER_UNTIL_CAPTCHA_LIMIT_BY_UID=2):
            counter = check_answer_counter.get_per_uid_buckets()
            for _ in range(settings.CHECK_ANSWER_UNTIL_CAPTCHA_LIMIT_BY_UID + 1):
                counter.incr(TEST_UID)
            resp = self.make_request(query_args=dict(answer=list(reversed(TEST_ANSWER))))
        self.assert_error_response(resp, ['compare.not_matched'])
        self.assert_compared_recorded_to_statbox(check_passed=False)
        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        ok_(not track.is_captcha_checked)
        ok_(not track.is_captcha_recognized)

    def test_rate_limit_by_uid_exceeded(self):
        self.setup_track_captcha_passed()

        counter = check_answer_counter.get_per_uid_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_UID)

        resp = self.make_request(query_args=dict(answer=list(reversed(TEST_ANSWER))))
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('limit_exceeded'),
        ])

    def test_rate_limit_by_ip_exceeded(self):
        self.setup_track_captcha_passed()

        counter = check_answer_counter.get_per_ip_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_USER_IP)

        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('limit_exceeded'),
        ])
