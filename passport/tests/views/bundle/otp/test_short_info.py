# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.exceptions import (
    BaseBlackboxError,
    BlackboxTemporaryError,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.counters import userinfo_counter
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import merge_dicts


TEST_UID = 1
TEST_LOGIN = 'user1'
TEST_DISPLAY_NAME = u'Пушистое пельмешко'
TEST_USER_IP = '37.9.101.188'


@with_settings_hosts(
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    **mock_counters()
)
class TestTotpShortInfo(BaseBundleTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['app']}))
        self.setup_blackbox()

    def setup_blackbox(self, uid=TEST_UID, login=TEST_LOGIN, display_name=TEST_DISPLAY_NAME,
                       account_2fa_on='1', **kwargs):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=uid,
                login=login,
                display_name={'name': display_name},
                attributes={'account.2fa_on': account_2fa_on},
                **kwargs
            ),
        )

    def setup_track(self, track_type='authorize', uid=TEST_UID, is_it_otp_enable=True):
        track_manager, track_id = self.env.track_manager.get_manager_and_trackid(track_type)
        with track_manager.transaction(track_id).rollback_on_error() as track:
            track.uid = uid
            track.is_it_otp_enable = is_it_otp_enable
        return track_manager, track_id

    def tearDown(self):
        self.env.stop()
        del self.env

    def query_params(self, **kwargs):
        base_params = {
            'login': TEST_LOGIN,
        }
        return merge_dicts(base_params, kwargs)

    def make_request(self, data, headers=None):
        if not headers:
            headers = {}
        return self.env.client.post(
            '/1/bundle/account/otp/short_info/?consumer=dev',
            data=data,
            headers=merge_dicts(mock_headers(), headers),
        )

    def assert_userinfo_called(self):
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'login': TEST_LOGIN,
        })

    def test_rate_limit_exceed__degradation(self):
        """При превышении счетчика посещений, ответ содержит только серверное время"""
        counter = userinfo_counter.get_short_userinfo_bucket()
        for i in range(counter.limit):
            counter.incr(TEST_USER_IP)
        eq_(
            userinfo_counter.get_short_userinfo_bucket().get(TEST_USER_IP),
            counter.limit,
        )

        resp = self.make_request(
            self.query_params(),
            headers={
                'Ya-Consumer-Client-Ip': TEST_USER_IP,
            },
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'ok',
                'server_time': TimeNow(),
            },
        )

    def test_login_empty_error(self):
        resp = self.make_request({})
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'errors': ['login.empty'],
            },
        )

    def test_account_not_found_error(self):
        self.setup_blackbox(uid=None),

        resp = self.make_request(self.query_params())
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'errors': ['account.not_found'],
            },
        )
        self.assert_userinfo_called()

    def test_account_disabled_error(self):
        self.setup_blackbox(enabled=False),
        resp = self.make_request(self.query_params())
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'errors': ['account.disabled'],
            },
        )
        self.assert_userinfo_called()

    def test_blackbox_temporary_error(self):
        def userinfo(*args, **kwargs):
            raise BlackboxTemporaryError()

        self.env.blackbox.set_response_side_effect('userinfo', userinfo)

        resp = self.make_request(self.query_params())
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'errors': ['internal.temporary'],
            },
        )
        self.assert_userinfo_called()

    def test_blackbox_non_temporary_error(self):
        def userinfo(*args, **kwargs):
            raise BaseBlackboxError()

        self.env.blackbox.set_response_side_effect('userinfo', userinfo)

        resp = self.make_request(self.query_params())
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(
            resp,
            {
                'status': 'error',
                'errors': ['internal.permanent'],
            },
        )
        self.assert_userinfo_called()

    def test_ok_no_avatar(self):
        resp = self.make_request(self.query_params())

        self.assert_ok_response(
            resp,
            server_time=TimeNow(),
            avatar_url=None,
            display_name=TEST_DISPLAY_NAME,
            uid=TEST_UID,
            **{'2fa': True}
        )

        self.assert_userinfo_called()
        self.env.statbox.assert_has_written([])
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_ok_with_unicode_entities(self):
        html = "<script>alert('&')</script>"
        escaped = r'\u003cscript\u003ealert(\u0027\u0026\u0027)\u003c/script\u003e'
        self.setup_blackbox(display_name=html)

        resp = self.make_request(self.query_params())

        self.assert_ok_response(
            resp,
            server_time=TimeNow(),
            avatar_url=None,
            display_name=html,
            uid=TEST_UID,
            **{'2fa': True}
        )

        # json.parse() заменит символы, представленные как unicode-entity на их ascii-аналоги
        # поэтому проверяем "сырой" ответ
        expected_json_encoded = '"display_name": "%s"' % escaped
        ok_(expected_json_encoded in resp.data)

    def test_ok_with_default_avatar(self):
        self.setup_blackbox(default_avatar_key='123'),

        resp = self.make_request(self.query_params())

        self.assert_ok_response(
            resp,
            server_time=TimeNow(),
            avatar_url='https://localhost/get-yapic/123/islands-75',
            display_name=TEST_DISPLAY_NAME,
            uid=TEST_UID,
            **{'2fa': True}
        )

        self.assert_userinfo_called()
        self.env.statbox.assert_has_written([])
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_ok_with_avatar_sizes(self):
        self.setup_blackbox(default_avatar_key='123'),

        for size, yapic_code in [
            (49, 'islands-50'),  # меньше, чем у нас есть
            (55, 'islands-50'),
            (75, 'islands-75'),
            (86, 'islands-retina-middle'),  # 86 -> 84
            (100, 'islands-retina-50'),  # максимальный что есть
            (101, 'islands-retina-50'),  # больше максимального
            # В случае нечисловых размеров, просто вернем дефолтный аватар, падать не будем
            ('', 'islands-75'),
            ('badnumber', 'islands-75'),
        ]:
            resp = self.make_request(self.query_params(avatar_size=size))

            self.assert_ok_response(
                resp,
                server_time=TimeNow(),
                avatar_url='https://localhost/get-yapic/123/%s' % yapic_code,
                display_name=TEST_DISPLAY_NAME,
                uid=TEST_UID,
                **{'2fa': True}
            )

            self.assert_userinfo_called()

    def test_wrong_track__error(self):
        _, track_id = self.setup_track(is_it_otp_enable=False)

        resp = self.make_request(
            self.query_params(track_id=track_id),
        )

        self.assert_error_response(resp, ['internal.permanent'])

    def test_wrong_uid_in_track__error(self):
        self.setup_blackbox()
        _, track_id = self.setup_track(uid='123')

        resp = self.make_request(
            self.query_params(
                track_id=track_id,
                login=TEST_LOGIN,
            ),
        )

        self.assert_error_response(resp, ['internal.permanent'])

    def test_with_2fa_track__params_saved(self):
        """В случае, когда пришел track_id, счетчики не проверяются и не увеличиваются"""
        self.setup_blackbox()
        track_manager, track_id = self.setup_track()
        # Подогреем счетчик вызовов ручки запредельно
        counter = userinfo_counter.get_short_userinfo_bucket()
        for _ in range(counter.limit):
            counter.incr(TEST_USER_IP)
        eq_(
            userinfo_counter.get_short_userinfo_bucket().get(TEST_USER_IP),
            counter.limit,
        )

        resp = self.make_request(
            self.query_params(
                track_id=track_id,
                app_id='app_id',
                app_version='app_version',
                app_platform='app_platform',
                os_version='os_version',
                manufacturer='manufacturer',
                model='model',
                uuid='uuid',
                deviceid='deviceid',
                ifv='ifv',
                device_name=u'имя устройства',
            ),
            headers={
                'Ya-Consumer-Client-Ip': TEST_USER_IP,
            },
        )

        self.assert_ok_response(
            resp,
            server_time=TimeNow(),
            avatar_url=None,
            display_name=TEST_DISPLAY_NAME,
            uid=TEST_UID,
            **{'2fa': True}
        )

        eq_(
            userinfo_counter.get_short_userinfo_bucket().get(TEST_USER_IP),
            counter.limit,
        )

        track = track_manager.read(track_id)
        eq_(track.device_application, 'app_id')
        eq_(track.device_application_version, 'app_version')
        eq_(track.device_os_id, 'app_platform')
        eq_(track.device_os_version, 'os_version')
        eq_(track.device_manufacturer, 'manufacturer')
        eq_(track.device_hardware_model, 'model')
        eq_(track.device_app_uuid, 'uuid')
        eq_(track.device_hardware_id, 'deviceid')

    def test_ok_2fa_disabled(self):
        self.setup_blackbox(account_2fa_on=None)

        resp = self.make_request(self.query_params())

        self.assert_ok_response(
            resp,
            server_time=TimeNow(),
            avatar_url=None,
            display_name=TEST_DISPLAY_NAME,
            uid=TEST_UID,
            **{'2fa': False}
        )

        self.assert_userinfo_called()
        self.env.statbox.assert_has_written([])
        self.assert_events_are_logged(self.env.handle_mock, {})
