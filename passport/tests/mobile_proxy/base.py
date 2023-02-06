# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.utils import iterdiff

from .test_base_data import TEST_USER_IP


class BaseMobileProxyTestCase(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()
        del self.env

    def default_headers(self, **extra_headers):
        headers = {
            'Ya-Consumer-Client-Ip': TEST_USER_IP,
        }
        headers.update(extra_headers)
        return headers

    def make_request(self, url, method='POST', args=None, data=None, headers=None):
        method_func = getattr(self.env.client, method.lower())
        return method_func(
            path=url,
            query_string=args,
            data=data,
            headers=headers or self.default_headers(),
        )

    def check_json_ok(self, rv, **response_values):
        eq_(rv.status_code, 200)
        actual_values = json.loads(rv.data)
        if 'cookies' in actual_values:
            actual_values['cookies'] = sorted(actual_values['cookies'])
        iterdiff(eq_)(
            actual_values,
            dict(status='ok', **response_values),
        )

    def check_xml_ok(self, rv, root, **kwargs):
        eq_(rv.status_code, 200)
        body = ''.join(
            '<%(tag)s>%(value)s</%(tag)s>' % {'tag': tag, 'value': value}
            for tag, value in kwargs.items()
        )
        eq_(
            rv.data,
            '<?xml version="1.0" encoding="utf-8"?><%(root)s>%(body)s</%(root)s>' % {
                'root': root,
                'body': body,
            },
        )

    def check_xml_error(self, rv, error, status_code=400):
        eq_(rv.status_code, status_code)
        eq_(
            rv.data.decode('utf8'),
            '<?xml version="1.0" encoding="utf-8"?><error code="%s">%s</error>' % (status_code, error),
        )

    def check_json_error(self, rv, status_code=400, **response_values):
        eq_(rv.status_code, status_code)
        eq_(
            json.loads(rv.data),
            dict(status='error', **response_values),
        )
