# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import *
from passport.backend.core.conf import settings
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts


TEST_USER_IP = '3.3.3.3'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    ALLOWED_PDD_HOSTS=TEST_ALLOWED_PDD_HOSTS,
)
class GetStateTestCase(BaseBundleTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'auth_password': ['base'],
        }))

        self.default_url = '/1/bundle/auth/password/get_state/?consumer=dev'

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def query_params(self, track_id=None):
        return dict(track_id=track_id if track_id else self.track_id)

    def make_request(self, data={}):
        return self.env.client.post(
            self.default_url,
            data=data,
            headers=mock_headers(),
        )

    def check_ok(self, rv, expected_response):
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            expected_response,
        )

    def get_expected_response(self, status='ok',
                              retpath=TEST_RETPATH, uid=TEST_UID,
                              domain=None, hint=None, **kwargs):
        expected = {
            'status': status,
            'track_id': self.track_id,
            'account': {
                'uid': uid,
                # Этот хардкод отсылает нас к `passport.test.blackbox.py:_blackbox_userinfo`
                'display_name': {'name': '', 'default_avatar': ''},
                'person': {
                    'firstname': u'\\u0414',
                    'lastname': u'\\u0424',
                    'birthday': '1963-05-15',
                    'gender': 1,
                    'language': 'ru',
                    'country': 'ru',
                },
                'display_login': 'login',
            },
            'retpath': retpath,
        }

        if domain:
            expected['account']['domain'] = {
                'punycode': domain,
                'unicode': domain,
            }
        if hint:
            expected['account']['hint'] = hint

        return merge_dicts(expected, kwargs)

    def get_expected_error_response(self, errors):
        return {
            'status': 'error',
            'errors': errors,
        }

    def test_missing_track_id(self):
        rv = self.make_request(
            data=dict(),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['track_id.empty'],
            },
        )

    def test_wrong_track_id(self):
        rv = self.make_request(
            data=self.query_params(track_id='0a' * settings.TRACK_RANDOM_BYTES_COUNT + '00'),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['track.not_found'],
            },
        )

    def test_incomplete_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.submit_response_cache = None

        rv = self.make_request(
            data=self.query_params(),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['track.invalid_state'],
            },
        )

    def test_auth_already_passed(self):
        expected_response = self.get_expected_error_response(['account.auth_passed'])

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.submit_response_cache = expected_response

        rv = self.make_request(
            data=self.query_params(),
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['account.auth_passed'],
            },
        )

    def test_need_completion(self):

        expected_response = self.get_expected_response(state='complete_autoregistered')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.submit_response_cache = expected_response

        rv = self.make_request(
            data=self.query_params(),
        )

        self.check_ok(rv, expected_response)
