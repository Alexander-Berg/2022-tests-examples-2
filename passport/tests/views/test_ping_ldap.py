# -*- coding: utf-8 -*-
import mock
from passport.backend.perimeter.auth_api.ldap.checker import LdapChecker
from passport.backend.perimeter.tests.views.base import BaseViewTestCase


class TestPingLdap(BaseViewTestCase):
    def setUp(self):
        super(TestPingLdap, self).setUp()
        self.checker_mock = mock.Mock()
        self.checker_patch = mock.patch.object(LdapChecker, 'check', self.checker_mock)
        self.checker_patch.start()

    def tearDown(self):
        self.checker_patch.stop()

    def test_ok(self):
        resp = self.client.get('/ping_ldap')
        assert resp.status_code == 200
        assert resp.data == b'ok'
        assert not self.checker_mock.call_args_list[-1][1]['use_best_server']
