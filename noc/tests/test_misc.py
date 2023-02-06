import hbf.code as hbf

from . import BaseTest
from hbf.ipaddress2 import ip_network


class InetRules(BaseTest):

    SECTIONS = {
        hbf.INET_SECTION_NAME: hbf.InetSection(hbf.INET_SECTION_NAME, no_index=True, content="""
            add allow ip from 604@2a02:6b8:c00::/40 to { inet }
            add allow ip from abcd@2a02:6b8:c00::/40 to { inet }
        """),
    }

    def test_inet_allowed(self):
        ip4 = ip_network("10.0.0.0")
        ip6 = ip_network("2a02:6b8:0:100:a:b:c:d")

        proj_604 = ip_network("604@2a02:6b8:c00::/40")
        host96_604 = ip_network("2a02:6b8:c12:234:0:604::/96")
        ip_proj_604 = ip_network("2a02:6b8:c00:0:0:604:aaaa:bbbb")

        proj_abcd = ip_network("abcd@2a02:6b8:c00::/40")
        host96_abcd = ip_network("2a02:6b8:c12:234:0:abcd::/96")
        ip_proj_abcd = ip_network("2a02:6b8:c12:234:0:abcd:aaaa:bbbb")

        # совсем без таргетов - включен
        self.assertTrue(hbf.is_inet_allowed_for_targets([]))

        # таргеты в отдельности
        inet_status = {
            ip4: False,
            ip6: False,
            proj_604: True,
            proj_abcd: True,
            host96_604: True,
            ip_proj_604: True,
            host96_abcd: True,
            ip_proj_abcd: True,
        }
        for ip, expected_status in inet_status.items():
            v = hbf.is_inet_allowed_for_targets([ip])
            self.assertEqual(v, expected_status, "Inet status for %s is %s, expected %s" % (ip, v, expected_status))
