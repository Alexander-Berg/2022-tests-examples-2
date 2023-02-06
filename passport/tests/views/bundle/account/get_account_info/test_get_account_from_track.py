# -*- coding: utf-8 -*-

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_LOGIN = 'test-afk'
ACCOUNT_FROM_TRACK_GRANT = 'from_track'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
)
class TestGetAccountFromTrackView(BaseBundleTestViews):

    default_url = '/1/bundle/account/from_track/'
    http_method = 'get'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants=dict(account=[ACCOUNT_FROM_TRACK_GRANT])))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        bb_response = blackbox_userinfo_response(login=TEST_LOGIN)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            bb_response,
        )

        self.http_query_args = dict(
            consumer='dev',
            track_id=self.track_id,
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def expected_response(self):
        account_dict = dict(
            uid=self.env.TEST_UID,
            login=TEST_LOGIN,
            display_login=TEST_LOGIN,
            is_yandexoid=False,
            is_2fa_enabled=False,
            is_rfc_2fa_enabled=False,
            is_workspace_user=False,
            person=dict(
                gender=1,
                firstname='\\u0414',
                language='ru',
                country='ru',
                birthday='1963-05-15',
                lastname='\\u0424',
            ),
            display_name=dict(
                default_avatar='',
                name='',
            ),
        )
        response = dict(
            account=account_dict,
            track_id=self.track_id,
        )
        return response

    def test_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = self.env.TEST_UID
        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.expected_response()
        )

    def test_no_track(self):
        resp = self.make_request(exclude_args=['track_id'])
        self.assert_error_response(
            resp,
            ['track_id.empty'],
        )

    def test_no_track_uid(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = None

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['track.invalid_state'],
        )

    def test_no_consumer(self):
        resp = self.make_request(exclude_args=['consumer'])
        self.assert_error_response(
            resp,
            ['consumer.empty'],
        )

    def test_no_account_by_uid(self):
        bb_response = blackbox_userinfo_response(uid=None)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            bb_response,
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = '123'

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['account.not_found'],
        )

        self.env.blackbox.requests[0].assert_post_data_contains(
            dict(
                uid='123',
            ),
        )
