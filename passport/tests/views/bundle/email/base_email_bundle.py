# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.counters.buckets import get_buckets
from passport.backend.core.models.persistent_track import PERSISTENT_TRACK_ID_BYTES_COUNT
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.utils.common import (
    bytes_to_hex,
    remove_none_values,
)
from six.moves.urllib.parse import urlencode


def max_out_counter(prefix, key):
    counter = get_buckets(prefix)
    remainder = counter.limit - counter.get(key)

    for _ in range(remainder):
        counter.incr(key)
    return counter.get(key)


TEST_IP = '127.0.0.1'
TEST_UID = 123
TEST_LOGIN = 'user1'
TEST_EMAIL = 'some.email@gmail.com'
TEST_EMAIL_ID = 1
TEST_ANOTHER_EMAIL = 'another.email@gmail.com'
TEST_UNICODE_EMAIL = u'some.email@окна.рф'
TEST_PUNYCODE_EMAIL = 'some.email@xn--80atjc.xn--p1ai'
TEST_CYRILLIC_EMAIL_ID = 10
TEST_NATIVE_EMAIL = 'test@yandex.ru'
TEST_RETPATH = 'http://retpathurl.yandex.ru'
TEST_HOST = 'yandex.ru'
TEST_USER_AGENT = u'Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/60.0.3112.107 Mobile Safari/537.36'
TEST_PERSISTENT_TRACK_ID = bytes_to_hex(b'a' * PERSISTENT_TRACK_ID_BYTES_COUNT)
TEST_SHORT_CODE_DIGITS = [1, 2, 3, 4, 5]
TEST_SHORT_CODE = ''.join(map(str, TEST_SHORT_CODE_DIGITS))
TEST_VALIDATOR_UI_URL = 'https://passport.yandex.ru/email_endpoint?some_arg=value&uid=-'
TEST_VALIDATION_URL = 'https://passport.yandex.ru/email_endpoint?%s' % urlencode({
    'uid': TEST_UID,
    'key': TEST_PERSISTENT_TRACK_ID,
    'retpath': TEST_RETPATH,
})


class BaseEmailBundleTestCase(BaseBundleTestViews):
    track_type = 'register'
    http_method = 'POST'
    http_headers = {
        'host': TEST_HOST,
        'cookie': 'Session_id=foo',
        'user_agent': TEST_USER_AGENT,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'email_bundle': ['base', 'confirmation_email', 'manage', 'check_ownership'],
        }))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID

        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='email_bundle',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'send_confirmation_email',
            action='send_confirmation_email',
            mode='email_validation',
            uid=str(TEST_UID),
            email=mask_email_for_statbox(TEST_EMAIL),
        )
        self.env.statbox.bind_entry(
            'send_ownership_confirmation_code',
            action='send_code',
            mode='email_ownership_confirmation',
            uid=str(TEST_UID),
            consumer='dev',
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        )
        self.env.statbox.bind_entry(
            'check_ownership_confirmation_code',
            action='check_code',
            mode='email_ownership_confirmation',
            uid=str(TEST_UID),
            consumer='dev',
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        )

    def assert_statbox_log(self, **kwargs):
        kwargs = remove_none_values(kwargs)
        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry('local_base', **kwargs),
            ],
            offset=-1,
        )

    def assert_state_response(self, response, state):
        eq_(response.status_code, 200)
        eq_(
            json.loads(response.data),
            {
                'status': 'ok',
                'state': state,
            },
        )

    def get_headers(self, headers=None):
        return mock_headers() if headers is None else headers

    def get_post_data(self, **kwargs):
        return kwargs

    def check_blackbox_called(self, userinfo_request_index=0):
        self.env.blackbox.requests[userinfo_request_index].assert_post_data_contains({
            'method': 'userinfo',
            'uid': TEST_UID,
            'emails': 'getall',
            'getemails': 'all',
            'email_attributes': 'all',
        })

    def check_historydb_records(self, record, uid=TEST_UID):
        historydb_entries = [
            {
                'uid': str(uid),
                'name': k,
                'value': v,
            }
            for k, v in record if v is not None
        ]
        self.assert_events_are_logged(
            self.env.handle_mock,
            historydb_entries,
        )


class PasswordProtectedNewEmailBundleTests(object):
    def test_account_without_password(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                age=100500,
            ),
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['account.without_password'])

    def test_account_completion_required(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                aliases={
                    'social': TEST_LOGIN,
                },
                age=100500,
            ),
        )

        rv = self.make_request()
        self.assert_ok_response(rv, state='complete_social')
