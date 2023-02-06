# -*- coding: utf-8 -*-
from django.test.utils import override_settings
from django.urls import reverse_lazy
from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.oauth.core.db.eav import DBTemporaryError
from passport.backend.oauth.core.db.eav.dbmanager import get_dbm
from passport.backend.oauth.core.test.framework import ApiTestCase
import yatest.common as yc


@override_settings(
    PING_TEST_FILE=yc.source_path('passport/backend/oauth/api/ping.html'),
)
class PingTestCase(ApiTestCase):
    default_url = reverse_lazy('ping')

    def default_params(self):
        return {
            'check': 'db,blackbox',
        }

    def test_simple_ok(self):
        rv = self.make_request(decode_response=False, exclude=['check'])
        eq_(rv, 'Pong\n')

    def test_db_blackbox_ok(self):
        rv = self.make_request(decode_response=False)
        eq_(rv, 'Pong\n')

    def test_unknown_args_ok(self):
        rv = self.make_request(decode_response=False, check='google_dns')
        eq_(rv, 'Pong\n')

    def test_file_not_accessible(self):
        with override_settings(PING_TEST_FILE='not_existing_file.html'):
            rv = self.make_request(expected_status=521)
        eq_(
            rv,
            {
                'error': 'service.shut_down',
            },
        )

    def test_db_failed(self):
        get_dbm('oauthdbcentral').ping.side_effect = DBTemporaryError('DB unavailable')
        rv = self.make_request(expected_status=521)
        eq_(
            rv,
            {
                'error': 'db.unavailable',
                'error_description': 'DB unavailable',
            },
        )

    def test_blackbox_failed(self):
        self.fake_blackbox.set_response_side_effect(
            'userinfo',
            BlackboxTemporaryError,
        )
        rv = self.make_request(expected_status=521)
        eq_(
            rv,
            {
                'error': 'blackbox.unavailable',
                'error_description': 'BlackboxTemporaryError',
            },
        )

    def test_blackbox_user_not_found(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        rv = self.make_request(decode_response=False)
        eq_(rv, 'Pong\n')

    def test_all_failed_but_not_checked(self):
        get_dbm('oauthdbcentral').ping.side_effect = DBTemporaryError('DB unavailable')
        self.fake_blackbox.set_response_side_effect(
            'userinfo',
            BlackboxTemporaryError,
        )
        rv = self.make_request(decode_response=False, check='')
        eq_(rv, 'Pong\n')
