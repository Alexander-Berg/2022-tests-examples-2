# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.mixins.account import GetAccountBySessionOrTokenMixin
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AUTH_HEADER,
    TEST_HOST,
    TEST_OAUTH_SCOPE,
    TEST_OTHER_LOGIN,
    TEST_OTHER_UID,
    TEST_TRACK_TYPE,
    TEST_UID,
    TEST_USER_COOKIE,
    TEST_USER_IP,
    TEST_YANDEXUID_VALUE,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import merge_dicts


@with_settings_hosts
class TestInitializeTrack(BaseBundleTestViews, GetAccountBySessionOrTokenMixin):

    url = '/1/bundle/track/init/?consumer=dev'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['track.initialize'])

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.set_blackbox_response()
        self.setup_statbox_templates()

    def tearDown(self):
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator

    def build_headers(self, **kwargs):
        base_headers = dict(
            user_ip=TEST_USER_IP,
            cookie=None,
            host=TEST_HOST,
            authorization=None,
        )
        headers = merge_dicts(
            base_headers,
            kwargs,
        )
        return mock_headers(**headers)

    def make_request(self, headers=None, **data):
        if headers is None:
            headers = self.build_headers(cookie=TEST_USER_COOKIE)

        response = self.env.client.post(
            self.url,
            headers=headers,
            data=data,
        )
        return response

    def set_blackbox_response(self, uid=TEST_UID, scope=TEST_OAUTH_SCOPE):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=uid,
                ),
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=scope,
            ),
        )

    def assert_track_ok(self, uid=TEST_UID, track_type=TEST_TRACK_TYPE, process_name=None):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(uid))
        eq_(track.track_type, track_type)
        eq_(track.process_name, process_name)

    def assert_no_lines_are_logged_to_statbox(self):
        self.env.statbox_logger.assert_has_written([])

    def assert_statbox_check_entries_log(self):
        self.env.statbox_logger.assert_has_written([self.env.statbox.entry('check_cookies')])

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'initialize_track',
            consumer='dev',
            mode='initialize_track',
            track_id=self.track_id,
            yandexuid=TEST_YANDEXUID_VALUE,
        )

    def assert_statbox_ok(self, uid=TEST_UID, exclude_fields=None, with_check_cookies=False):
        if exclude_fields is None:
            exclude_fields = []
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(
            self.env.statbox.entry(
                'initialize_track',
                _exclude=exclude_fields,
                uid=str(uid),
            ),
        )
        self.env.statbox_logger.assert_has_written(entries)

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv, track_id=self.track_id)
        self.assert_track_ok()
        self.assert_statbox_ok(with_check_cookies=True)

    def test_ok_with_other_track_type(self):
        rv = self.make_request(track_type='register')
        self.assert_ok_response(rv, track_id=self.track_id)
        self.assert_track_ok(track_type='register')
        self.assert_statbox_ok(with_check_cookies=True)

    def test_ok_with_other_uid(self):
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_ok_response(rv, track_id=self.track_id)
        self.assert_track_ok(uid=TEST_OTHER_UID)
        self.assert_statbox_ok(uid=TEST_OTHER_UID, with_check_cookies=True)

    def test_ok_with_other_process_name(self):
        rv = self.make_request(process_name='account_delete_v2_process')
        self.assert_ok_response(rv, track_id=self.track_id)
        self.assert_track_ok(process_name='account_delete_v2_process')
        self.assert_statbox_ok(with_check_cookies=True)

    def test_unknown_uid_error(self):
        rv = self.make_request(uid=42)
        self.assert_error_response(rv, ['sessionid.no_uid'])
        self.assert_statbox_check_entries_log()

    def test_ok_by_token(self):
        rv = self.make_request(headers=self.build_headers(authorization=TEST_AUTH_HEADER))
        self.assert_ok_response(rv, track_id=self.track_id)
        self.assert_track_ok()
        self.assert_statbox_ok(exclude_fields=['yandexuid'])


@with_settings_hosts
class TestInitializeInfectedTrack(BaseBundleTestViews):

    url = '/1/bundle/track/init_infected/?consumer=dev'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['track.initialize_infected'])

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.set_blackbox_response()
        self.setup_statbox_templates()

    def tearDown(self):
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator

    def build_headers(self, **kwargs):
        headers = dict(
            user_ip=TEST_USER_IP,
            cookie=None,
            host=TEST_HOST,
            authorization=None,
        )
        headers.update(kwargs)
        return mock_headers(**headers)

    def make_request(self, headers=None, **data):
        return self.env.client.post(
            self.url,
            headers=headers or self.build_headers(cookie=TEST_USER_COOKIE),
            data=data,
        )

    def set_blackbox_response(self, uid=TEST_UID):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=uid,
                ),
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
            ),
        )

    def assert_track_ok(self, uid=TEST_UID, track_type=TEST_TRACK_TYPE):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(uid))
        eq_(track.track_type, track_type)
        ok_(track.allow_authorization)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'initialize_infected_track',
            consumer='dev',
            mode='initialize_infected_track',
            track_id=self.track_id,
            yandexuid=TEST_YANDEXUID_VALUE,
        )

    def assert_statbox_ok(self, uid=TEST_UID):
        self.env.statbox_logger.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'initialize_infected_track',
                uid=str(uid),
            ),
        ])

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv, track_id=self.track_id)
        self.assert_track_ok()
        self.assert_statbox_ok()
