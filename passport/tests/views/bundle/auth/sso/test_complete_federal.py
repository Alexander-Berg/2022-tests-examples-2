# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    TEST_IP,
    TEST_LOGIN,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_USER_AGENT,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)


eq_ = iterdiff(eq_)


@with_settings_hosts()
class CompleteFederalTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/auth/sso/complete_federal/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_IP,
        'user_agent': TEST_USER_AGENT,
    }
    http_query_args = {
        'eula_accepted': '1',
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_by_sso': ['base']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.http_query_args.update(track_id=self.track_id)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_PDD_UID

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                    'federal': TEST_PDD_LOGIN,
                },
            ),
        )

    def tearDown(self):
        self.env.stop()

    def assert_db_ok(self):
        self.env.db.check('attributes', 'account.is_pdd_agreement_accepted', '1', uid=TEST_PDD_UID, db='passportdbshard2')

    def assert_history_db_ok(self):
        expected_values = {
            'action': 'complete_federal',
            'consumer': 'dev',
            'sid.add': '102',
            'user_agent': TEST_USER_AGENT,
        }
        self.assert_events_are_logged(self.env.handle_mock, expected_values)

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv)
        self.assert_db_ok()
        self.assert_history_db_ok()

    def test_not_federal(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 1
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=1, login=TEST_LOGIN),
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['action.not_required'])

    def test_eula_not_accepted(self):
        rv = self.make_request(
            query_args=dict(eula_accepted=0),
        )
        self.assert_error_response(rv, ['eula_accepted.not_accepted'])
