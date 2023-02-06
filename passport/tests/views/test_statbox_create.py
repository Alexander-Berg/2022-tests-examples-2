# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestStatbox(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'statbox': ['*']}))

    def tearDown(self):
        self.env.stop()
        del self.env

    def statbox_request(self, data):
        return self.env.client.post('/1/statbox/?consumer=dev', data=data)

    def test_simple_statbox(self):
        manager, track_id = self.env.track_manager.get_manager_and_trackid()
        rv = self.statbox_request(
            {
                'track_id': track_id,
                 'data': 'blablbla',
                 'action': 'open',
            },
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'base',
                _is_external_event='1',
                track_id=track_id,
                data='blablbla',
                action='open',
                consumer='dev',
            ),
        ])

    def test_simple_statbox_without_track_id(self):
        rv = self.statbox_request(
            {
                'data': 'blablbla',
                'action': 'open',
            },
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'base',
                _is_external_event='1',
                data='blablbla',
                action='open',
                consumer='dev',
            ),
        ])

    def test_unable_to_override_event_type(self):
        rv = self.statbox_request(
            {
                'data': 'blablbla',
                '_is_external_event': '0',
            },
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'base',
                _is_external_event='1',
                data='blablbla',
                consumer='dev',
            ),
        ])

    def test_failed_statbox(self):
        rv = self.env.client.post(
            '/1/statbox/',
            data={
                'data': 'blablbla',
                'action': 'open',
            },
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        self.env.statbox.assert_has_written([])
