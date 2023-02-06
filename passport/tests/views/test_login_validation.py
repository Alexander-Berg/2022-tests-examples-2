# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.utils import assert_errors
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_loginoccupation_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


TEST_USER_IP = '37.9.101.188'


@with_settings_hosts()
class TestLoginValidation(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.env.grants.set_grants_return_value(
            mock_grants(grants={'login': ['validate'], 'track': ['*']}))

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def login_validation_request(self, data, headers):
        return self.env.client.post(
            '/1/validation/login/?consumer=dev',
            data=data,
            headers=headers,
        )

    def test_bad_request(self):
        eq_(self.login_validation_request({}, {}).status_code, 400)

    def test_available(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'onevision': 'free'}),
        )
        rv = self.login_validation_request(
            {
                'login': 'onevision',
                'track_id': self.track_id,
            },
            mock_headers(user_ip=TEST_USER_IP),
        )
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok'})
        eq_(self.track_manager.read(self.track_id).login, 'onevision')

    def test_track_counter(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'onevision': 'free'}),
        )

        rv = self.login_validation_request(
            {
                'login': 'onevision',
                'track_id': self.track_id
            },
            headers=mock_headers(user_ip=TEST_USER_IP),
        )
        eq_(rv.status_code, 200)
        eq_(self.track_manager.read(self.track_id).login_validation_count.get(), 1)

    def test_track_timings(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'onevision': 'free'}),
        )
        args = {
            'login': 'onevision',
            'track_id': self.track_id,
        }
        headers = mock_headers(user_ip=TEST_USER_IP)
        rv = self.login_validation_request(args, headers=headers)
        eq_(rv.status_code, 200)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            eq_(track.login_validation_first_call, TimeNow())
            eq_(track.login_validation_last_call, TimeNow())
            track.login_validation_first_call = 123

        self.login_validation_request(args, headers=headers)
        track = self.track_manager.read(self.track_id)
        eq_(track.login_validation_first_call, '123')
        eq_(track.login_validation_last_call, TimeNow())

    def test_not_available(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'onevision': 'occupied'}),
        )
        rv = self.login_validation_request(
            {
                'login': 'onevision',
                'track_id': self.track_id,
            },
            headers=mock_headers(user_ip=TEST_USER_IP),
        )
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_errors'], {'login': 'notavailable'})

    def test_ignore_stoplist(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'reserved': 'free'}),
        )

        self.env.grants.set_grants_return_value(mock_grants(grants={'ignore_stoplist': ['*'], 'login': ['validate'], 'track': ['update']}))
        rv = self.login_validation_request(
            {
                'login': 'reserved',
                'ignore_stoplist': '1',
                'track_id': self.track_id,
            },
            headers=mock_headers(user_ip=TEST_USER_IP),
        )

        url = self.env.blackbox.request.call_args[0][1]
        ok_('logins=reserved' in url, self.env.blackbox.request.call_args)
        ok_('ignore_stoplist=1' in url, self.env.blackbox.request.call_args)

        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok'})

    def test_validate_test_yandex_login_ip_from_yandexnets(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'yandex-team': 'free'}),
        )

        rv = self.login_validation_request(
            {
                'login': 'yandex-team',
                'track_id': self.track_id,
            },
            headers=mock_headers(user_ip=TEST_USER_IP),
        )

        eq_(self.env.blackbox.request.call_count, 1)
        url = self.env.blackbox.request.call_args[0][1]
        ok_('logins=yandex-team' in url, self.env.blackbox.request.call_args)
        ok_('ignore_stoplist=1' in url, self.env.blackbox.request.call_args)

        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok'})

    def test_validate_test_yandex_login_ip_from_world(self):
        rv = self.login_validation_request(
            {
                'login': 'yandex-team',
                'track_id': self.track_id,
            },
            headers=mock_headers(user_ip='213.87.129.27'),
        )

        eq_(self.env.blackbox.request.call_count, 0)

        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        eq_(
            response['validation_errors'],
            [{'field': 'login', 'message': 'Login is not available', 'code': 'notavailable'}],
        )
