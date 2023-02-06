# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import (
    TEST_AUTH_ID,
    TEST_IP,
    TEST_LOGIN_ID,
    TEST_USER_AGENT,
    TEST_YANDEXUID_COOKIE,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_RETPATH,
    TEST_UID,
)
from passport.backend.core.builders.antifraud import AntifraudApiTemporaryError
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .base import (
    BaseStandaloneTestCase,
    TEST_ANTIFRAUD_EXTERNAL_ID,
)


@with_settings(
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
)
class StandaloneSaveTestcase(BaseStandaloneTestCase):
    default_url = '/1/bundle/challenge/standalone/save/'

    def setUp(self):
        super(StandaloneSaveTestcase, self).setUp()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.retpath = TEST_RETPATH
            track.auth_challenge_type = 'phone_confirmation'
            track.antifraud_external_id = TEST_ANTIFRAUD_EXTERNAL_ID

        self.env.antifraud_api.set_response_value('save', '')

    @property
    def http_query_args(self):
        return dict(
            track_id=self.track_id,
        )

    def assert_antifraud_api_called(self, challenge='phone_confirmation', external_id=TEST_ANTIFRAUD_EXTERNAL_ID):
        ok_(self.env.antifraud_api.requests)
        request = self.env.antifraud_api.requests[0]
        request_data = json.loads(request.post_args)
        expected_features = dict(
            status='OK',
            external_id=external_id,
            ip=TEST_IP,
            channel='challenge',
            sub_channel='chaas',
            uid=TEST_UID,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_COOKIE,
            retpath=TEST_RETPATH,
            authid=TEST_AUTH_ID,
            login_id=TEST_LOGIN_ID,
            challenge=challenge,
            AS=None,
            t=TimeNow(as_milliseconds=True),
        )
        eq_(request_data, expected_features)

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            retpath=TEST_RETPATH,
        )
        self.assert_antifraud_api_called()

    def test_ok_with_default_external_id(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_external_id = None

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            retpath=TEST_RETPATH,
        )
        self.assert_antifraud_api_called(
            external_id='track-{}'.format(self.track_id),
        )

    def test_invalid_track_state_error(self):
        with self.track_transaction() as track:
            track.auth_challenge_type = None

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['track.invalid_state'],
        )

    def test_antifraud_error(self):
        self.env.antifraud_api.set_response_side_effect('save', AntifraudApiTemporaryError())

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['backend.antifraud_api_failed'],
            retpath=TEST_RETPATH,
        )
