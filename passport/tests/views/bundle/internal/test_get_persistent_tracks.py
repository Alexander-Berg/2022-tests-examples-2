# -*- coding: utf-8 -*-

from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_all_tracks_response,
    blackbox_track_item,
    blackbox_userinfo_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_UID = 1


@with_settings_hosts()
class TestGetPersistentTracks(BaseBundleTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'internal': ['get_persistent_tracks']}))
        self.env.blackbox.set_response_value(
            'get_all_tracks',
            blackbox_get_all_tracks_response(
                items=[
                    blackbox_track_item(content={'type': 1, 'secret': 123}),
                ],
            ),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def make_request(self, params, headers):
        return self.env.client.get(
            '/1/bundle/test/persistent_tracks/',
            query_string=params,
            headers=headers,
        )

    def query_params(self, **kwargs):
        base_params = {
            'consumer': 'dev',
            'uid': TEST_UID,
        }
        return dict(base_params, **kwargs)

    def test_no_grants_error(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={}))

        resp = self.make_request(self.query_params(), {})

        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_ok__track_masked(self):
        self.env.blackbox.set_response_value('userinfo', blackbox_userinfo_response())

        resp = self.make_request(
            self.query_params(),
            mock_headers(),
        )

        self.assert_ok_response(
            resp,
            persistent_tracks=[
                {
                    u'content': {
                        u'type': 1,
                        u'secret': u'*',
                    },
                    u'created': u'1123213213',
                    u'expired': u'1123513213',
                    u'track_id': u'bc96****************************',
                    u'uid': 1,
                },
            ],
        )

    def test_ok__track_not_masked_for_test_login(self):
        self.env.blackbox.set_response_value('userinfo', blackbox_userinfo_response(login='yndx-tester'))

        resp = self.make_request(
            self.query_params(),
            mock_headers(),
        )

        self.assert_ok_response(
            resp,
            persistent_tracks=[
                {
                    u'content': {
                        u'type': 1,
                        u'secret': 123,
                    },
                    u'created': u'1123213213',
                    u'expired': u'1123513213',
                    u'track_id': u'bc968a106e53c3a22ea1ceef3aa5ab12',
                    u'uid': 1,
                },
            ],
        )
