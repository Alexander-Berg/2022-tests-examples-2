# -*- coding: utf-8 -*-
from passport.backend.api.test.mixins import AccountModificationNotifyTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_HINT_ANSWER,
    TEST_HINT_QUESTION,
    TEST_HINT_QUESTION_ID,
    TEST_HINT_QUESTION_TEXT,
    TEST_HOST,
    TEST_PASSWORD,
    TEST_PASSWORD_HASH,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_login_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.captcha.faker import captcha_response_check
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts


QUESTIONS_BASE_GRANT = 'questions.base'
QUESTIONS_SECURE_GRANT = 'questions.secure'
QUESTIONS_CHANGE_GRANT = 'questions.change'
CAPTCHA_BASE_GRANT = 'captcha.*'


@with_settings_hosts(
    CHECK_ANSWER_UNTIL_CAPTCHA_LIMIT_BY_UID=3,
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'hint_change'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:hint_change': 5},
    )
)
class TestQuestionsChangeIntegrational(BaseBundleTestViews, AccountModificationNotifyTestMixin):

    http_method = 'post'
    http_headers = dict(
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        host=TEST_HOST,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(
            [
                QUESTIONS_BASE_GRANT,
                QUESTIONS_SECURE_GRANT,
                QUESTIONS_CHANGE_GRANT,
                CAPTCHA_BASE_GRANT,
            ],
        )
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.env.captcha_mock.set_response_value(
            'check',
            captcha_response_check(),
        )
        account_data = {
            'uid': TEST_UID,
            'crypt_password': TEST_PASSWORD_HASH,
            'dbfields': {
                'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
                'userinfo_safe.hintq.uid': TEST_HINT_QUESTION,
            },
        }
        sessionid_response = blackbox_sessionid_multi_response(
            **account_data
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**account_data),
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**account_data),
        )
        self.env.db.serialize(sessionid_response)
        self.start_account_modification_notify_mocks(ip=TEST_USER_IP)
        self.setup_kolmogor()

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
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

    def make_captcha_check_request(self):
        return self.make_request(
            url='/1/captcha/check/?consumer=dev',
            query_args=dict(
                answer='a',
                key='b',
                track_id=self.track_id,
            ),
        )

    def make_get_hint_request(self):
        return self.make_request(
            url='/1/account/questions/secure/',
            method='get',
            query_args=dict(
                display_language='ru',
                track_id=self.track_id,
                consumer='dev',
            ),
        )

    def make_change_hint_request(self, **kwargs):
        data = merge_dicts(
            dict(
                track_id=self.track_id,
                current_password=TEST_PASSWORD,
                question_id=1,
                display_language='ru',
                answer=TEST_HINT_ANSWER,
                new_answer='New answer',
            ),
            kwargs,
        )
        return self.make_request(
            url='/1/account/questions/change/?consumer=dev',
            query_args=data,
        )

    def get_hint_expected_response(self):
        return dict(
            question={
                'id': TEST_HINT_QUESTION_ID,
                'text': TEST_HINT_QUESTION_TEXT,
            },
            track_id=self.track_id,
        )

    def test_ok(self):
        get_hint_resp = self.make_get_hint_request()
        self.assert_ok_response(
            get_hint_resp,
            **self.get_hint_expected_response()
        )
        change_resp = self.make_change_hint_request()
        self.assert_ok_response(change_resp, need_to_bind_phone=True)
