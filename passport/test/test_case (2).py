# -*- coding: utf-8 -*-


from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.social.common.test.fake_useragent import FakeUseragent
from passport.backend.social.common.test.test_case import (
    TestCase as _TestCase,
    TvmTestCaseMixin,
)
from passport.backend.social.common.useragent import build_http_pool_manager


class TestCase(TvmTestCaseMixin, _TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self._fake_useragent = FakeUseragent()
        self._fake_useragent.start()

        self._fake_http_pool_manager = build_http_pool_manager()
        LazyLoader.register('http_pool_manager', lambda: self._fake_http_pool_manager)

    def tearDown(self):
        self._fake_useragent.stop()
        super(TestCase, self).tearDown()
