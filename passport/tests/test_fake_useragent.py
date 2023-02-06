# -*- coding: utf-8 -*-

from unittest import TestCase

from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.useragent.faker.useragent import (
    FakedConnectionError,
    FakedDnsError,
    FakedHttpResponse,
    FakedTimeoutError,
    UserAgentFaker,
)
from passport.backend.core.useragent.sync import (
    RequestError,
    UserAgent,
)


@with_settings()
class UserAgentTestCase(TestCase):
    def setUp(self):
        self.faker = UserAgentFaker()
        self.faker.start()
        self.ua = UserAgent()
        self.url = 'http://localhost/'

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.ua

    def test_set_responses_on_success(self):
        self.faker.set_responses([FakedHttpResponse(200, 'hello')])
        resp = self.ua.request('GET', self.url)
        assert resp.status_code == 200
        assert resp.content == 'hello'

    def test_set_responses_on_many_errors(self):
        self.faker.set_responses([
            FakedConnectionError(),
            FakedDnsError(),
            FakedTimeoutError(),
            FakedTimeoutError(),
            FakedHttpResponse(200),
        ])
        for _ in range(4):
            self.assertRaises(RequestError, self.ua.request, 'GET', self.url)
        self.ua.request('GET', self.url)
