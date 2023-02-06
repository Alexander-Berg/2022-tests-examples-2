# -*- coding: utf-8 -*-
import mock
from nose.tools import eq_
from passport.backend.api.common.logs import (
    get_external_request_id,
    get_param_value,
    get_track_id,
    log_response,
)
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.models.account import Account
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_UID = 123
TEST_USER_IP = '1.2.3.4'
TEST_HOST = 'yandex.ru'
TEST_LOGIN = 'test-login'


@with_settings_hosts()
class TestHelperFunctions(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_getting_uid(self):
        params = [
            ({'path': '/1/questions/?uid=11'}, '11'),
            ({'path': '/1/questions/?login=login'}, '-'),
            ({'path': '/1/questions/?uid=12&login=login'}, '12'),
            ({'path': '/1/questions/'}, '-'),
        ]

        for p, r in params:
            with self.env.client.application.test_request_context(**p):
                eq_(get_param_value('uid'), r)

    def test_getting_login(self):
        params = [
            ({'path': '/1/questions/?uid=11'}, '-'),
            ({'path': '/1/questions/?login=login'}, 'login'),
            ({'path': '/1/questions/?uid=12&login=login'}, 'login'),
            ({'path': '/1/questions/'}, '-'),
        ]

        for p, r in params:
            with self.env.client.application.test_request_context(**p):
                eq_(get_param_value('login'), r)

    def test_getting_track_id(self):
        params = [
            ({'path': '/1/questions/?track_id=11'}, '11'),
            ({'path': '/1/track/track_id/'}, 'track_id'),
            ({'path': '/1/track/track_id1/?track_id=track_id2'}, 'track_id1'),
            ({'path': '/1/questions/?track_id=бла'}, u'бла'),
            ({'path': '/1/questions/'}, None),
        ]

        for p, r in params:
            with self.env.client.application.test_request_context(**p):
                eq_(get_track_id(), r)

    def test_getting_bb_userinfo(self):
        bb_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        data = get_parsed_blackbox_response('userinfo', blackbox_response)
        with self.env.client.application.test_request_context() as context:
            env = mock.Mock()
            env.request_id = ''
            context.request.env = env
            account_data = Account().parse(data)

            eq_(get_param_value('uid', account_data), TEST_UID)
            eq_(get_param_value('login', account_data), TEST_LOGIN)

    def test_get_external_request_id(self):
        with self.env.client.application.test_request_context() as context:
            env = mock.Mock()
            env.request_id = ''
            context.request.env = env
            eq_(get_external_request_id(), '-')
            env.request_id = '123'
            eq_(get_external_request_id(), '123')


@with_settings_hosts()
class TestLoggingFunctions(BaseTestViews):
    def setUp(self):
        self._log_mock = mock.Mock()
        self._log_patch = mock.patch('passport.backend.api.common.logs.log', self._log_mock)
        self._log_patch.start()
        self._time_mock = mock.Mock()
        self._time_patch = mock.patch('passport.backend.api.common.logs.time', self._time_mock)
        self._time_patch.start()
        self._request_mock = mock.Mock()
        self._request_patch = mock.patch('passport.backend.api.common.logs.request', self._request_mock)
        self._request_patch.start()

    def tearDown(self):
        self._request_patch.stop()
        self._time_patch.stop()
        self._log_patch.stop()

    def make_response(self, data, status=200):
        return mock.Mock(data=data, status=status)

    def assert_logged(self, records_by_level):
        for level, records in records_by_level.items():
            method = getattr(self._log_mock, level)
            expected_calls = [mock.call(*record) for record in records]
            self.assertEqual(method.mock_calls, expected_calls)

    def test_log_request(self):
        self._request_mock.start_time = 1.0
        self._time_mock.time.return_value = 2.123456789
        log_response(self.make_response(b'abcde'))
        self.assert_logged({
            'info': [
                (u'Response status: %s', 200),
                (u'Response sent, %s: "%s"', u'duration=1.123457', u'abcde'),
            ],
        })
