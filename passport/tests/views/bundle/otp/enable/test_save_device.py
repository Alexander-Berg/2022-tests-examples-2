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
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts

from .test_base import (
    get_headers,
    TEST_APP_SECRET,
    TEST_DEVICE_ID,
    TEST_PIN,
    TEST_PUSH_SETUP_SECRET,
    TEST_UID,
)


@with_settings_hosts
class GetSecretTestCase(BaseBundleTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['edit']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('register')

        self.default_headers = get_headers()
        self.default_params = self.query_params()

        self.setup_track()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_track(self, uid=TEST_UID, is_it_otp_enable=True,
                    totp_app_secret=TEST_APP_SECRET, totp_pin=TEST_PIN,
                    push_setup_secret=TEST_PUSH_SETUP_SECRET, push_device_ids=None):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.is_it_otp_enable = is_it_otp_enable
            if totp_app_secret:
                track.totp_app_secret = totp_app_secret
            if totp_pin:
                track.totp_pin = totp_pin
            if push_setup_secret:
                track.push_setup_secret = push_setup_secret
            if push_device_ids:
                for dev_id in push_device_ids:
                    track.totp_push_device_ids.append(dev_id)

    def query_params(self, **kwargs):
        params = {
            'device_id': TEST_DEVICE_ID,
            'push_setup_secret': TEST_PUSH_SETUP_SECRET,
            'track_id': self.track_id,
        }
        params.update(kwargs)
        return params

    def make_request(self, params=None, headers=None):
        if not headers:
            headers = self.default_headers
        if not params:
            params = self.default_params
        return self.env.client.post(
            '/1/bundle/otp/enable/save_device/?consumer=dev',
            data=params,
            headers=headers,
        )

    def assert_track_ok(self, push_device_ids=[TEST_DEVICE_ID]):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        ok_(track.is_it_otp_enable)
        eq_(track.totp_app_secret, TEST_APP_SECRET)
        eq_(track.push_setup_secret, TEST_PUSH_SETUP_SECRET)
        eq_(track.totp_pin, TEST_PIN)
        eq_(list(track.totp_push_device_ids.get()), push_device_ids)

    def assert_ok_response(self, resp, **kwargs):
        base_response = {
            'status': 'ok',
            'track_id': self.track_id,
        }
        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            merge_dicts(base_response, kwargs),
        )

    def test_first_device_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_track_ok()

    def test_second_device_ok(self):
        self.setup_track(push_device_ids=['1'])
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_track_ok(push_device_ids=['1', TEST_DEVICE_ID])

    def test_duplicate_device_ok(self):
        self.setup_track(push_device_ids=[TEST_DEVICE_ID])
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_track_ok()

    def test_devices_limit_exceeded_error(self):
        self.setup_track(push_device_ids=map(str, range(30)))
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_invalid_push_secret_error(self):
        resp = self.make_request(params=self.query_params(push_setup_secret='invalid'))
        self.assert_error_response_with_track_id(resp, ['csrf_token.invalid'])

    def test_params_empty_error(self):
        for param in ['push_setup_secret', 'track_id', 'device_id']:
            rv = self.make_request(params=self.query_params(**{param: ''}))
            self.assert_error_response(rv, ['%s.empty' % param])

    def test_track_id_invalid_error(self):
        rv = self.make_request(params=self.query_params(track_id='123'))
        self.assert_error_response(rv, ['track_id.invalid'])
