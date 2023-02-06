# -*- coding: utf-8 -*-
import json

import mock
from passport.backend.perimeter.auth_api.ldap.balancer import LdapBalancer
from passport.backend.perimeter.tests.views.base import BaseViewTestCase


TEST_TIMINGS = {'host1': 1, 'host2': 2, 'host3': 3}


class TestStatus(BaseViewTestCase):
    def setUp(self):
        super(TestStatus, self).setUp()

        self.balancer_get_timings_mock = mock.Mock(return_value=TEST_TIMINGS)
        self.balancer_patch = mock.patch.object(LdapBalancer, 'get_timings', self.balancer_get_timings_mock)
        self.balancer_patch.start()

    def tearDown(self):
        self.balancer_patch.stop()

    def test_ok(self):
        resp = self.client.get('/status')
        assert resp.status_code == 200
        assert json.loads(resp.data) == {
            'status': 'ok',
            'ldap_timings': TEST_TIMINGS,
        }
