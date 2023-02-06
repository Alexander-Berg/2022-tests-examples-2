# -*- coding: utf-8 -*-
import json
import random

import mock
from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import merge_dicts


TEST_UID = '1'
TEST_LOGIN = 'user1'
TEST_TOTP_SECRET = '12345'
TEST_USER_IP = '37.9.101.188'
TOTP_SECRET_LENGTH = 16


def build_headers():
    return mock_headers(
        user_ip=TEST_USER_IP,
    )


class TestTotpEditBase(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'internal': ['totp_edit']}))
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:crypt',
            ),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)

        self.expected_secret = 'a' * TOTP_SECRET_LENGTH
        self.expected_pin = 123
        self.urandom_mock = mock.Mock(return_value=self.expected_secret)
        self.system_random_mock = mock.Mock(return_value=self.expected_pin)
        self.patches = [
            mock.patch(
                'os.urandom',
                self.urandom_mock,
            ),
            mock.patch.object(
                random.SystemRandom,
                'uniform',
                self.system_random_mock,
            ),
            self.track_id_generator,
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches
        del self.urandom_mock
        del self.system_random_mock

    def get_url(self):
        raise NotImplementedError()

    def make_request(self, data, headers):
        return self.env.client.post(
            self.get_url(),
            data=data,
            headers=headers,
        )


@with_settings_hosts()
class TestTotpEdit(TestTotpEditBase):

    def get_url(self):
        return '/1/bundle/test/totp_edit/?consumer=dev'

    def query_params(self, **kwargs):
        base_params = {
            'uid': TEST_UID,
            'totp_secret': TEST_TOTP_SECRET,
        }
        return merge_dicts(base_params, kwargs)

    def test_empty_request(self):
        rv = self.make_request({}, {})

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['ip.empty'],
            },
        )

    def test_no_uid_error(self):
        rv = self.make_request(
            {'totp_secret': TEST_TOTP_SECRET},
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['uid.empty'],
            },
        )

    def test_no_secret_error(self):
        rv = self.make_request(
            {'uid': 1},
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['totp_secret.empty'],
            },
        )

    def test_ok_create(self):
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )

        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check('attributes', 'account.totp.secret', TEST_TOTP_SECRET, uid=1, db='passportdbshard1')

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            [
                # не пишем тут событие включения 2fa: мы не знаем, что реально записали в качестве секрета
                {'name': 'info.totp_update_time', 'value': TimeNow()},
                {'name': 'action', 'value': 'test_totp_edit'},
                {'name': 'consumer', 'value': 'dev'},
            ],
        )


@with_settings_hosts()
class TestTotpDelete(TestTotpEditBase):

    def get_url(self):
        return '/1/bundle/test/totp_delete/?consumer=dev'

    def query_params(self, **kwargs):
        base_params = {
            'uid': TEST_UID,
        }
        return merge_dicts(base_params, kwargs)

    def test_no_totp_on_account_error(self):
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['action.not_required'],
            },
        )

    def test_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:crypt',
                attributes={'account.2fa_on': '1'},
            ),
        )
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )

        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check_missing('attributes', 'account.totp.secret', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.2fa_on', uid=1, db='passportdbshard1')

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            [
                {'name': 'info.totp', 'value': 'disabled'},
                {'name': 'info.totp_update_time', 'value': '-'},
                {'name': 'action', 'value': 'test_totp_delete'},
                {'name': 'consumer', 'value': 'dev'},
            ],
        )


@with_settings_hosts()
class TestTotpGenerate(TestTotpEditBase):

    def get_url(self):
        return '/1/bundle/test/totp_generate/?consumer=dev'

    def query_params(self, **kwargs):
        base_params = {}
        return merge_dicts(base_params, kwargs)

    def test_ok(self):
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'pin': '0123',
                'app_secret': 'MFQWCYLBMFQWCYLBMFQWCYLBME',
            },
        )

    def test_ok_with_track(self):
        rv = self.make_request(
            self.query_params(track_id=self.track_id),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'pin': '0123',
                'app_secret': 'MFQWCYLBMFQWCYLBMFQWCYLBME',
            },
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.totp_app_secret, 'MFQWCYLBMFQWCYLBMFQWCYLBME')
        eq_(track.totp_pin, '0123')
