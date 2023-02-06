# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.mdapi.base_test_data import TEST_USER_COOKIES
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_UID = 123
TEST_HOST = 'yandex.ru'
TEST_USER_IP = '1.2.3.4'


@with_settings_hosts()
class QuestionsAddOptionalCase(BaseBundleTestViews):

    default_url = '/1/account/questions/optional/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        answer1='a1',
        answer2='a2',
        answer3='a3',
        question1='q1',
        question2='q2',
        question3='q3',
    )
    http_headers = dict(
        user_ip=TEST_USER_IP,
        host=TEST_HOST,
        cookie=TEST_USER_COOKIES,
    )

    def setUp(self):
        super(QuestionsAddOptionalCase, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(mock_grants(grants={
            'questions': ['base', 'optional'],
        }))

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
            ),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_ok(self):
        rv = self.make_request()
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
            },
        )
        log_entries = dict(self.http_query_args)
        expected_log_entries = {
            'info.hints_optional': json.dumps(dict(sorted(log_entries.items()))),
        }
        self.assert_events_are_logged(self.env.handle_mock, expected_log_entries)

    def test_missing_client_ip(self):
        rv = self.make_request(exclude_headers=['host', 'user_ip'])
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['ip.empty'],
            },
        )

    def test_missing_questions(self):
        exclude = self.http_query_args.keys()
        rv = self.make_request(exclude_args=exclude)
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': [
                    'answer1.empty',
                    'answer2.empty',
                    'answer3.empty',
                    'question1.empty',
                    'question2.empty',
                    'question3.empty',
                ],
            },
        )

    def test_disabled_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                enabled=False,
            ),
        )
        rv = self.make_request()
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['account.disabled'],
            },
        )

    def test_disabled_on_deletion_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        rv = self.make_request()
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['account.disabled_on_deletion'],
            },
        )
