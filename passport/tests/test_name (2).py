# -*- coding: utf-8 -*-
import socket
import unittest

import mock
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.cache.backend.locmem import LocalMemoryCache
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.useragent.name import (
    DNSError,
    DNSNoNameError,
    DNSResolver,
)


@with_settings(USE_GLOBAL_DNS_CACHE=False)
class TestDNSResolver(unittest.TestCase):
    def setUp(self):
        self.mock_getaddrinfo = mock.Mock()
        self.getaddrinfo_patch = mock.patch('socket.getaddrinfo', self.mock_getaddrinfo)
        self.getaddrinfo_patch.start()

    def tearDown(self):
        self.getaddrinfo_patch.stop()
        del self.mock_getaddrinfo
        del self.getaddrinfo_patch

    def getaddrinfo_response(self, ips):
        return [(0, 0, 0, 0, [ip]) for ip in ips]

    def test_ip_address_query(self):
        cache = LocalMemoryCache(ttl=10)
        d = DNSResolver(cache=cache)
        # getaddrinfo не должен вызываться для резолва IP
        eq_(self.mock_getaddrinfo.called, False)
        # резолвер возвращает IP для IP
        eq_(d.query('192.168.1.1'), ['192.168.1.1'])
        # результат сохранён в кеше
        eq_(cache.get('192.168.1.1'), ['192.168.1.1'])

    def test_localhost_query(self):
        self.mock_getaddrinfo.return_value = self.getaddrinfo_response(['::1', '127.0.0.1'])
        d = DNSResolver()
        eq_(d.query('localhost.'), ['::1', '127.0.0.1'])

    def test_resolver_cache(self):
        self.mock_getaddrinfo.return_value = self.getaddrinfo_response(['::1', '127.0.0.1'])

        cache = LocalMemoryCache(ttl=10)
        d = DNSResolver(cache=cache)

        d.query('localhost.')
        eq_(d.query('localhost.'), ['::1', '127.0.0.1'])

        # Not in cache, silently ignored
        d.invalidate('yandex.ru')

        # Removes localhost from cache
        d.invalidate('localhost.')
        eq_(cache.get('localhost.'), None)

    @raises(DNSNoNameError)
    def test_resolver_with_noname_error(self):
        self.mock_getaddrinfo.side_effect = socket.gaierror(socket.EAI_NONAME, 'error')
        d = DNSResolver()
        d.query('localhost')

    @raises(DNSError)
    def test_resolver_errors(self):
        self.mock_getaddrinfo.side_effect = socket.gaierror(socket.EAI_FAIL, 'error')
        d = DNSResolver()
        d.query('localhost.')

    @raises(DNSError)
    def test_nat64_resolve(self):
        self.mock_getaddrinfo.return_value = self.getaddrinfo_response(['64:ff9b::a1b2:c3d4'])
        d = DNSResolver()
        d.query('localhost.')
