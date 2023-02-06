# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)


class TestSSOSubmit(BaseBundleTestViews):
    http_method = 'get'
    default_url = '/1/bundle/auth/sso/metadata/get/'
    consumer = 'dev'
    mocked_grants = []

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(self.mocked_grants)

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_ok(self):
        resp = self.make_request()
        eq_(resp.status_code, 200)
        ok_(resp.data.startswith('<?xml version="1.0" ?>'))
        ok_('xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"' in resp.data)
