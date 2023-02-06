import unittest
from hbf.ipaddr import ip_addr


class IPaddrTest(unittest.TestCase):
    def test_str(self):
        ip1 = ip_addr("127.0.0.1")
        assert(str(ip1) == "127.0.0.1")
        assert(ip1.version == 4)

        ip2 = ip_addr("0:0::1")
        assert(str(ip2) == "::1")
        assert(ip2.version == 6)

    def test_construct(self):
        self.assertEqual("10.0.0.1", str(ip_addr("10.0.0.1")))
        self.assertEqual("10.0.0.1", str(ip_addr(0xa000001, version=4)))
        self.assertEqual("10.0.0.1", str(ip_addr(b"\x0a\0\0\1", version=4)))
        self.assertEqual("10.0.0.1", str(ip_addr(ip_addr("10.0.0.1"))))

        self.assertRaises(ValueError, lambda: ip_addr(None))
        self.assertRaises(ValueError, lambda: ip_addr([]))
        self.assertRaises(ValueError, lambda: ip_addr({}))
        self.assertRaises(ValueError, lambda: ip_addr("::", version=4))
        self.assertRaises(ValueError, lambda: ip_addr("10.0.0.1", version=6))
        self.assertRaises(ValueError, lambda: ip_addr(b"\x0a\0\0\1", version=6))

    def test_version(self):
        ip4 = ip_addr("10.0.0.1")
        self.assertEqual(4, ip4.version)

        ip6 = ip_addr("fe80::1")
        self.assertEqual(6, ip6.version)

        def _assign_ver(ip, value):
            ip.version = value

        self.assertRaises(AttributeError, lambda: _assign_ver(ip4, 4))
        self.assertRaises(AttributeError, lambda: _assign_ver(ip4, 6))

    def test_eq(self):
        self.assertEqual(ip_addr("10.0.0.1"), ip_addr(0xa000001, version=4))
        self.assertEqual(ip_addr("fe80::1"), ip_addr(0xfe800000000000000000000000000001, version=6))

        self.assertNotEqual(ip_addr("10.0.0.2"), ip_addr(0xa000001, version=4))
        self.assertNotEqual(ip_addr("fe80::2"), ip_addr(0xfe800000000000000000000000000001, version=6))

        self.assertNotEqual(ip_addr("10.0.0.2"), ip_addr("fe80::2"))
        self.assertNotEqual(ip_addr("10.0.0.2"), "")
        self.assertNotEqual(ip_addr("10.0.0.2"), "")
        self.assertNotEqual(None, ip_addr("10.0.0.2"))

    def test_cmp(self):
        ip4_10_0_0_0 = ip_addr("10.0.0.0")
        ip4_10_0_0_1 = ip_addr("10.0.0.1")
        ip6_0 = ip_addr("::")
        ip6_2 = ip_addr("::2")
        ip6_fe80_1 = ip_addr("fe80::1")

        lst = [ip4_10_0_0_0, ip4_10_0_0_1, ip6_0, ip6_2, ip6_fe80_1]
        self.assertEqual(sorted(lst), lst)
        self.assertEqual(sorted(reversed(lst)), lst)

        self.assertTrue(ip4_10_0_0_1 > ip4_10_0_0_0)
        self.assertTrue(ip6_fe80_1 > ip4_10_0_0_0)
        self.assertTrue(ip6_fe80_1 > ip6_2)

        self.assertTrue(ip4_10_0_0_0 <= ip4_10_0_0_1)
        self.assertTrue(ip4_10_0_0_0 <= ip6_fe80_1)
        self.assertTrue(ip6_0 <= ip6_fe80_1)

        self.assertTrue(ip4_10_0_0_0 < ip4_10_0_0_1)
        self.assertTrue(ip4_10_0_0_0 < ip6_fe80_1)
        self.assertTrue(ip6_0 < ip6_fe80_1)

        self.assertTrue(ip4_10_0_0_0 <= ip4_10_0_0_1)
        self.assertTrue(ip4_10_0_0_0 <= ip6_fe80_1)
        self.assertTrue(ip6_0 <= ip6_fe80_1)

        #  invert op
        self.assertFalse(ip4_10_0_0_1 < ip4_10_0_0_0)
        self.assertFalse(ip6_fe80_1 < ip4_10_0_0_0)
        self.assertFalse(ip6_fe80_1 < ip6_2)

        self.assertFalse(ip4_10_0_0_0 >= ip4_10_0_0_1)
        self.assertFalse(ip4_10_0_0_0 >= ip6_fe80_1)
        self.assertFalse(ip6_0 >= ip6_fe80_1)

        self.assertFalse(ip4_10_0_0_0 > ip4_10_0_0_1)
        self.assertFalse(ip4_10_0_0_0 > ip6_fe80_1)
        self.assertFalse(ip6_0 > ip6_fe80_1)

        self.assertFalse(ip4_10_0_0_0 >= ip4_10_0_0_1)
        self.assertFalse(ip4_10_0_0_0 >= ip6_fe80_1)
        self.assertFalse(ip6_0 >= ip6_fe80_1)

        # equal
        self.assertTrue(ip4_10_0_0_0 <= ip4_10_0_0_0)
        self.assertTrue(ip6_0 <= ip6_0)
        self.assertTrue(ip4_10_0_0_0 >= ip4_10_0_0_0)
        self.assertTrue(ip6_0 >= ip6_0)

        self.assertRaises(TypeError, lambda: ip6_0 < 0)
        self.assertRaises(TypeError, lambda: 0 < ip6_0)
        self.assertRaises(TypeError, lambda: ip6_0 < None)
        self.assertRaises(TypeError, lambda: None < ip6_0)

    def test_hashable(self):
        d = {
            ip_addr("10.0.0.1"): "ipv4",
            ip_addr("fe80::1"): "ipv6",
        }
        v4 = ip_addr(b"\x0a\0\0\1")
        v6 = ip_addr(b"\xfe\x80" + b"\0"*13 + b"\1")
        self.assertEqual(d[v4], "ipv4")
        self.assertEqual(d[v6], "ipv6")

    def test_convertions(self):
        self.assertEqual(0xa000001, int(ip_addr("10.0.0.1")))
        self.assertEqual(0xff000001, int(ip_addr("::ff00:1")))
        self.assertEqual(0x100000000000000000000ff000001, int(ip_addr("1::ff00:1")))

        self.assertEqual(b'\x0a\0\0\1', bytes(ip_addr("10.0.0.1")))
        self.assertEqual(b'\0\0\0\0\0\0\0\0\0\0\0\0\xff\0\0\1', bytes(ip_addr("::ff00:1")))
        self.assertEqual(b'\0\1\0\0\0\0\0\0\0\0\0\0\xff\0\0\1', bytes(ip_addr("1::ff00:1")))

    def test_bitwise(self):
        ip1 = ip_addr("0.255.3.0")
        ip2 = ip_addr("192.192.192.192")

        self.assertEqual(ip_addr("0.192.0.0"), ip1 & ip2)
        self.assertEqual(ip_addr("192.255.195.192"), ip1 | ip2)
        self.assertEqual(ip_addr("192.63.195.192"), ip1 ^ ip2)
        self.assertEqual(ip_addr("255.0.252.255"), ~ip1)
        self.assertEqual(ip_addr("63.63.63.63"), ~ip2)

        ip3 = ip_addr("a123:b123:c123:d123:e123:f123:aa12:ab12")
        ip4 = ip_addr("ffff:ffff:ff00:0:ffff:ffff:0:0")

        self.assertEqual(ip_addr("a123:b123:c100:0:e123:f123::"), ip3 & ip4)
        self.assertEqual(ip_addr("ffff:ffff:ff23:d123:ffff:ffff:aa12:ab12"), ip3 | ip4)
        self.assertEqual(ip_addr("5edc:4edc:3e23:d123:1edc:edc:aa12:ab12"), ip3 ^ ip4)
        self.assertEqual(ip_addr("5edc:4edc:3edc:2edc:1edc:edc:55ed:54ed"), ~ip3)
        self.assertEqual(ip_addr("::ff:ffff:0:0:ffff:ffff"), ~ip4)

        self.assertRaises(ValueError, lambda: ip1 & ip3)
        self.assertRaises(ValueError, lambda: ip1 | ip3)
        self.assertRaises(ValueError, lambda: ip3 ^ ip1)

    def test_shift(self):
        self.assertEqual(ip_addr("1.2.3.4"), ip_addr("1.2.3.4") << 0)
        self.assertEqual(ip_addr("16.32.48.64"), ip_addr("1.2.3.4") << 4)
        self.assertEqual(ip_addr("8.0.0.0"), ip_addr("1.2.3.4") << 25)
        self.assertEqual(ip_addr("0.16.32.48"), ip_addr("1.2.3.4") >> 4)
        self.assertEqual(ip_addr("0.0.0.0"), ip_addr("1.2.3.4") >> 25)

        self.assertEqual(ip_addr("a123:b123:c100:0:e123:f123:12:f40"), ip_addr("a123:b123:c100:0:e123:f123:12:f40") << 0)
        self.assertEqual(ip_addr("123b:123c:1000:e:123f:1230:120:f400"), ip_addr("a123:b123:c100:0:e123:f123:12:f40") << 4)
        self.assertEqual(ip_addr("12:f40::"), ip_addr("a123:b123:c100:0:e123:f123:12:f40") << 96)
        self.assertEqual(ip_addr("a12:3b12:3c10:0:e12:3f12:3001:20f4"), ip_addr("a123:b123:c100:0:e123:f123:12:f40") >> 4)
        self.assertEqual(ip_addr("::a123:b123"), ip_addr("a123:b123:c100:0:e123:f123:12:f40") >> 96)
