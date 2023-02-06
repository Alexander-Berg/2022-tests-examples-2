# -*- coding: utf-8 -*-
import unittest

import mock
from netaddr import IPAddress
from nose.tools import (
    assert_is_none,
    eq_,
)
from passport.backend.core.geobase import (
    ASLookup,
    get_as_lookup,
)
from passport.backend.core.test.test_utils import (
    OPEN_PATCH_TARGET,
    with_settings,
)


try:
    from io import TextIOWrapper as file  # for py3 compatibility
except ImportError:
    pass


@with_settings()
class ASLookupTestCase(unittest.TestCase):
    def setUp(self):
        self.actual_lookup = get_as_lookup()

        self.open_mock = mock.MagicMock(name='open', spec=open)
        self.open_mock_patch = mock.patch(OPEN_PATCH_TARGET, self.open_mock, create=True)

        self.open_mock_patch.start()

    def tearDown(self):
        self.open_mock_patch.stop()
        del self.open_mock
        del self.open_mock_patch

    def build_fake_lookup(self, as_name=None, ipv4_origin=None, ipv6_origin=None):
        mocks = []
        for data in [as_name or [], ipv4_origin or [], ipv6_origin or []]:
            file_mock = mock.MagicMock(spec=file)
            file_mock.__enter__.return_value = data
            mocks.append(file_mock)
        self.open_mock.side_effect = mocks
        return ASLookup()

    def test_actual_lookup_with_localhost_ip(self):
        result = self.actual_lookup.ip_lookup('127.0.0.1')
        assert_is_none(result)

    def test_actual_lookup_with_yandex_ip(self):
        result = self.actual_lookup.ip_lookup('87.250.235.4')
        eq_(result.subnet.cidr, result.subnet)
        eq_(str(result.subnet.cidr), '87.250.224.0/19')
        eq_(result.as_list, ['as13238'])

    def test_actual_lookup_with_unknown_as(self):
        result = self.actual_lookup.as_name_lookup('no_such_as_for_sure')
        assert_is_none(result)

    def test_actual_lookup_with_yandex_as(self):
        result = self.actual_lookup.as_name_lookup('as13238')
        eq_(result.aliases, ['YANDEX'])
        eq_(result.descriptions, [''])

    def test_ip_lookup_ipv4_multiple_cidrs(self):
        lookup = self.build_fake_lookup(
            ipv4_origin=['%s\t%s\tAS100500\n' % (int(IPAddress('2.0.0.0')), int(IPAddress('2.6.0.0')) - 1)],
        )

        assert_is_none(lookup.ip_lookup('2.6.0.0'))
        for ip, cidr in [('2.0.0.1', '2.0.0.0/14'), ('2.5.255.11', '2.4.0.0/15')]:
            result = lookup.ip_lookup(ip)
            eq_(result.subnet.cidr, result.subnet)
            eq_(str(result.subnet.cidr), cidr)

    def test_ip_lookup_ipv6(self):
        lookup = self.build_fake_lookup(
            ipv6_origin=[
                '%s\t%s\tAS100500\n' % (
                    int(IPAddress('0000:0000:0000:0000:0000:ffff:0210:4c00')),
                    int(IPAddress('0000:0000:0000:0000:0000:ffff:0210:53ff')),
                ),
                '%s\t%s\tAS100500000\n' % (
                    int(IPAddress('2c0f:f988:0000:0000:0000:0000:0000:0000')),
                    int(IPAddress('2c0f:f988:ffff:ffff:ffff:ffff:ffff:ffff')),
                ),
            ],
        )

        assert_is_none(lookup.ip_lookup('0000:0000:0000:0000:0000:ffff:0210:4bff'))
        for ip, cidr in [
            ('0000:0000:0000:0000:0000:ffff:0210:4d00', '::ffff:2.16.76.0/118'),
            ('::ffff:2.16.76.10', '::ffff:2.16.76.0/118'),
            ('::ffff:2.16.80.200', '::ffff:2.16.80.0/118'),
            ('2c0f:f988:0000:abcd:0000:ffff:0000:1234', '2c0f:f988::/32'),
        ]:
            result = lookup.ip_lookup(ip)
            eq_(result.subnet.cidr, result.subnet)
            eq_(str(result.subnet.cidr), cidr)

    def test_as_lookup_multiple_records_for_as(self):
        lookup = self.build_fake_lookup(
            as_name=[
                b'AS1\talias1\tdescr1\n',
                b'as1\talias2\tdescr2\n',
                b'AS2\talias1\tdescr1\n',
            ],
        )

        result = lookup.as_name_lookup('AS1')
        eq_(result.aliases, ['alias1', 'alias2'])
        eq_(result.descriptions, [u'descr1', u'descr2'])

    def test_as_lookup_valid_description(self):
        lookup = self.build_fake_lookup(
            as_name=[
                b'AS1\talias1\tGutenbergstra\xdfe Austria\n',
            ],
        )

        result = lookup.as_name_lookup('AS1')
        eq_(result.descriptions, [u'Gutenbergstra�e Austria'])
