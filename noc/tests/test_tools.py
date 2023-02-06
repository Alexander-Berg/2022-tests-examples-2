from django.test import SimpleTestCase, tag, override_settings
from parameterized import parameterized

from .. import _tools


class ABCPrefixComputeTest(SimpleTestCase):
    @parameterized.expand(
        (
            (741, "2a02:6b8:0:3400:0:2e5::/96"),
            (1821, "2a02:6b8:0:3400:0:71d::/96"),
            (131072, "2a02:6b8:0:3400:0:2::/96"),
        )
    )
    @tag("core")
    def test_abc_prefix(self, abc_id, prefix):
        self.assertEqual(_tools.get_abc_network_perfix(abc_id), prefix)

    @tag("core")
    @override_settings(ABC_INTERNAL_IPV6_PREFIX_FORMAT="ZZZZ:6b8:0:3400:0:%s::/96")
    def test_abc_wrong_format(self):
        self.assertRaisesRegex(
            ValueError, "does not appear to be an IPv4 or IPv6 network", _tools.get_abc_network_perfix, 0
        )
