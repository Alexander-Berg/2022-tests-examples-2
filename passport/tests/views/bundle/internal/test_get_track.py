# -*- coding: utf-8 -*-
from passport.backend.api.common.processes import (
    PROCESS_LOGIN_RESTORE,
    PROCESS_RESTORE,
    PROCESS_WEB_REGISTRATION,
    PROCESS_YAKEY_BACKUP,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import merge_dicts
from six.moves.urllib.parse import urlencode


TEST_USER_IP = '37.9.101.188'


def build_headers():
    return mock_headers(
        user_ip=TEST_USER_IP,
    )


@with_settings_hosts()
class TestGetTrack(BaseBundleTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'internal': ['track']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def make_request(self, data, headers):
        return self.env.client.get(
            '/1/bundle/test/track/?consumer=dev&%s' % urlencode(data),
            headers=headers,
        )

    def query_params(self, **kwargs):
        base_params = {
            'track_id': self.track_id,
        }
        return merge_dicts(base_params, kwargs)

    def test_empty_request(self):
        resp = self.make_request(self.query_params(), {})

        self.assert_error_response(resp, ['ip.empty'])

    def test_no_track_id_error(self):
        resp = self.make_request(
            {},
            build_headers(),
        )

        self.assert_error_response(resp, ['track_id.empty'])

    def test_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_operation_confirmations.append('hello')

        resp = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_ok_response(
            resp,
            track_type='authorize',
            consumer='dev',
            created=TimeNow(),
            phone_operation_confirmations=['hello'],
            restore_methods_select_order=[],
            suggested_logins=[],
            totp_push_device_ids=[],
        )

    def test_ok_with_protected_track(self):
        for process_name in (
            PROCESS_RESTORE,
            PROCESS_LOGIN_RESTORE,
            PROCESS_WEB_REGISTRATION,
            PROCESS_YAKEY_BACKUP,
        ):

            with self.track_manager.transaction(self.track_id).commit_on_error() as track:
                track.process_name = process_name

            resp = self.make_request(
                self.query_params(),
                build_headers(),
            )

            self.assert_ok_response(
                resp,
                process_name=process_name,
                track_type='authorize',
                consumer='dev',
                created=TimeNow(),
                phone_operation_confirmations=[],
                restore_methods_select_order=[],
                suggested_logins=[],
                totp_push_device_ids=[],
            )

    def test_ok_with_counters(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.email_confirmation_checks_count.incr()

        resp = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_ok_response(
            resp,
            track_type='authorize',
            consumer='dev',
            created=TimeNow(),
            email_confirmation_checks_count=1,
            phone_operation_confirmations=[],
            restore_methods_select_order=[],
            suggested_logins=[],
            totp_push_device_ids=[],
        )
