# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import eq_
from passport.backend.api.common.authorization import (
    AUTHORIZATION_SESSION_POLICY_PERMANENT,
    AUTHORIZATION_SESSION_POLICY_SESSIONAL,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import merge_dicts


TEST_CSRF_TOKEN = '708ab6a91d336ba09b5aa1cec5bde098'


@with_settings_hosts()
class TestTotpAuthSubmit(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['auth']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)

        create_csrf_token_mock = mock.Mock(return_value=TEST_CSRF_TOKEN)

        self.setup_statbox_templates()
        self.patches = [
            self.track_id_generator,
            mock.patch('passport.backend.api.views.bundle.auth.otp.submit.create_csrf_token', create_csrf_token_mock),
        ]
        for patch in self.patches:
            patch.start()

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            yandexuid='yandexuid',
            user_agent='curl',
            track_id=self.track_id,
            ip='127.0.0.1',
        )
        self.env.statbox.bind_entry(
            'submitted',
            action='submitted',
            type='2fa',
        )

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches

    def assert_statbox_log(self, **kwargs):
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry(
                    'submitted',
                    **kwargs
                ),
            ],
        )
        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            ["auth_2fa.rps"],
            {"auth_2fa.rps.total_dmmm": 1}
        )

    def make_request(self, headers=None, data=None):
        if not headers:
            headers = {}
        if not data:
            data = {}

        return self.env.client.post(
            '/2/bundle/auth/otp/submit/?consumer=dev',
            data=data,
            headers=merge_dicts(
                mock_headers(
                    user_ip='127.0.0.1',
                    cookie='yandexuid=yandexuid;',
                    user_agent='curl',
                ),
                headers,
            ),
        )

    def assert_track_ok(self, **kwargs):
        """Трек заполнен полностью и корректно"""
        params = dict(
            is_allow_otp_magic=True,
            csrf_token=TEST_CSRF_TOKEN,
            authorization_session_policy=AUTHORIZATION_SESSION_POLICY_PERMANENT,
        )
        params.update(kwargs)
        track = self.track_manager.read(self.track_id)
        for attr_name, value in params.items():
            actual_value = getattr(track, attr_name)
            expected_value = str(value) if type(value) == int else value
            eq_(actual_value, expected_value, [attr_name, actual_value, expected_value])

    def test_wrong_policy_error(self):
        resp = self.make_request(data=dict(policy='123'))
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                u'errors': ['policy.invalid'],
            }
        )

    def test_ok(self):
        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'ok',
                'track_id': self.track_id,
                'csrf_token': TEST_CSRF_TOKEN,
            },
        )
        self.assert_track_ok(
            retpath=None,
            origin=None,
            service=None,
            fretpath=None,
            clean=None,
        )

    def test_ok_with_retpath_and_other_auth_params(self):
        """
        Проверим, что сохраняем переданные дополнительные параметры в трек:
        retpath, fretpath, clean, origin, service
        """
        expected_retpath = 'http://yandex.ru'
        expected_origin = 'test-origin'
        expected_fretpath = 'http://test.yandex.com'
        expected_service = 'lenta'

        resp = self.make_request(
            data=dict(
                retpath=expected_retpath,
                fretpath=expected_fretpath,
                clean='yes',
                origin=expected_origin,
                service=expected_service,
                policy=AUTHORIZATION_SESSION_POLICY_SESSIONAL,
            ),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'ok',
                'track_id': self.track_id,
                'csrf_token': TEST_CSRF_TOKEN,
            },
        )

        self.assert_track_ok(
            retpath=expected_retpath,
            origin=expected_origin,
            service=expected_service,
            fretpath=expected_fretpath,
            clean='yes',
            authorization_session_policy=AUTHORIZATION_SESSION_POLICY_SESSIONAL,
        )

        self.assert_statbox_log(origin=expected_origin)

    def test_ok_with_invalid_retpath(self):
        expected_retpath = 'http://blackfun.com'
        resp = self.make_request(data=dict(retpath=expected_retpath))
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'ok',
                'track_id': self.track_id,
                'csrf_token': TEST_CSRF_TOKEN,
            },
        )

        self.assert_track_ok(
            retpath=None,
        )

        self.assert_statbox_log()
