# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.common.format_response import JsonLoggedResponse
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class LoggedJsonResponseTestCase(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_ok(self):
        kwargs = {
            'sensitive_fields': ['baz', 'foo.bar'],
            'baz': 'original-secret',
            'foo': {
                'bar': 'nested-secret',
            }
        }

        with self.env.client.application.test_request_context():
            resp = JsonLoggedResponse(**kwargs)

            logdata = json.loads(resp.log_data())
            eq_(logdata['baz'], '*****')
            eq_(logdata['foo']['bar'], '*****')

            eq_(resp.dict_['baz'], 'original-secret')
            eq_(resp.dict_['foo']['bar'], 'nested-secret')
