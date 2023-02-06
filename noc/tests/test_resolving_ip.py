import mock
import socket
import unittest

from django import test
from parameterized import parameterized

from .. import _tools
import l3mgr.tests.base as base_test


class ResolvingIPv4TestCase(test.TestCase):
    def setUp(self):
        try:
            socket.getaddrinfo("ya.ru", 80, socket.AF_INET)
        except Exception:
            raise unittest.SkipTest("Internet connection isn't available")

    @parameterized.expand(
        (
            "any4-lb-check.yndx.net",
            "any3-lb-check.yndx.net",
        ),
    )
    def test_resolving_no_ipv4(self, fqdn: str):
        with self.assertRaises(socket.gaierror):
            socket.getaddrinfo(fqdn, 80, socket.AF_INET)
        with self.assertRaises(_tools.NoIPsException):
            _tools.resolve_ip(fqdn, False)

    @parameterized.expand(
        (
            "mnt-myt.yandex.net",
            "mnt-sas.yandex.net",
            "man1-lb2b.yndx.net",
            "ya.ru",
            "77.88.1.115",
            "93.158.158.87",
            "141.8.136.155",
        ),
    )
    def test_resolving_one_ipv4(self, fqdn: str):
        addresses = socket.getaddrinfo(fqdn, 80, socket.AF_INET)
        ips_v4 = {res[-1][0] for res in addresses}
        self.assertEqual(_tools.resolve_ip(fqdn, False), ips_v4.pop())

    @parameterized.expand(
        (
            "amazon.com",
            "yandex.ru",
        ),
    )
    def test_resolving_many_ipv4(self, fqdn: str):
        addresses = socket.getaddrinfo(fqdn, 80, socket.AF_INET)
        ips_v4 = {res[-1][0] for res in addresses}
        self.assertNotEqual(1, len(ips_v4))
        with self.assertRaises(_tools.ManyIPsException):
            _tools.resolve_ip(fqdn, False)


class ResolvingIPv6TestCase(test.TestCase):
    def setUp(self):
        try:
            socket.getaddrinfo("ya.ru", 80, socket.AF_INET6)
        except Exception:
            raise unittest.SkipTest("Internet connection isn't available")

    @parameterized.expand(
        (
            "lbkp-man-009.search.yandex.net",
            "mnt-myt.yandex.net",
            "mnt-sas.yandex.net",
            "man1-lb2b.yndx.net",
            "ya.ru",
            "yandex.ru",
            "2a02:6b8:c08:d99:0:640:88ab:8725",
            "2a02:6b8:0:1482::115",
            "2a02:6b8:a::a",
        ),
    )
    def test_resolving_one_ipv6(self, fqdn: str):
        addresses = socket.getaddrinfo(fqdn, 80, socket.AF_INET6)
        ips_v6 = {res[-1][0] for res in addresses}
        self.assertEqual(1, len(ips_v6))
        self.assertEqual(_tools.resolve_ip(fqdn, True), ips_v6.pop())

    @parameterized.expand(
        ("google.com",),
    )
    @mock.patch(
        "l3mgr.utils._tools.resolve_by_type", side_effect=base_test.resolve_by_type_mock_side_effect(), autospec=True
    )
    def test_resolving_many_ipv6(self, fqdn: str, _mock):
        with self.assertRaises(_tools.ManyIPsException):
            _tools.resolve_ip(fqdn, True)


class ResolvingBothUPsTestCase(test.TestCase):
    def setUp(self):
        try:
            socket.getaddrinfo("ya.ru", 80, socket.AF_INET)
            socket.getaddrinfo("ya.ru", 80, socket.AF_INET6)
        except Exception:
            raise unittest.SkipTest("Internet connection isn't available")

    @parameterized.expand(
        (
            "amazon.com",
            "ok.ru",
            "twitter.com",
            "vk.com",
            "ebay.com",
            "205.251.242.103",
            "151.101.193.140",
            "104.244.42.193",
        ),
    )
    def test_resolving_no_ipv6(self, fqdn: str):
        with self.assertRaises(socket.gaierror):
            socket.getaddrinfo(fqdn, 80, socket.AF_INET6)
        with self.assertRaises(_tools.NoIPsException):
            _tools.resolve_ip(fqdn, True)

    @parameterized.expand(
        (
            "lbkp-man-009.search.yandex.net",
            "2a02:6b8:b040:310a:feaa:14ff:fe65:ca65",
        ),
    )
    def test_resolving_ipv6_only(self, fqdn: str):
        with self.assertRaises(socket.gaierror):
            socket.getaddrinfo(fqdn, 80, socket.AF_INET)
        addresses = socket.getaddrinfo(fqdn, 80, socket.AF_INET6)
        ips_v6 = {res[-1][0] for res in addresses}
        self.assertEqual(_tools.resolve_ip(fqdn, False), ips_v6.pop())
