import tempfile
from textwrap import dedent

from . import BaseTest
import hbf.code as hbf
from hbf.ipaddress2 import ip_network


# здесь тестируется только парсер правил - объекты Rule, Hosts, TransportMatch, Portlist
class ParseTest(BaseTest):
    HOSTS = {
        "testhost": ["10.1.1.1"],
         "localhost.domain": ["10.0.0.2"],
         "test.yndx.net": ["10.0.0.10"],
         "test2.yndx.net": ["10.0.0.1"],
    }

    MACROSES = {
        "_C_TEST_MACRO_": [
            "testhost",
        ],
    }

    def test_rule_parse1(self):
        rule = hbf.Rule("add allow tcp from test.yndx.net to test2.yndx.net 80")
        tr = hbf.TransportMatch(proto='tcp', dst_port=hbf.Portlist(single_ports=(80,)))
        self.assertEqual([tr], rule.transports)

    def test_rule_parse_block(self):
        # fw-loader не требует пробелов на границах блоков, хотя ipfw требует
        # к сожалению, мы должны быть совместимы с fw-loader
        hbf.Rule("add allow tcp from{test.yndx.net or 0.0.0.0}to{test2.yndx.net}80")

    def test_complex_rule_parse(self):
        rule = hbf.Rule("add allow tag 653 ip4 from { 172.20.0.0/16 } to { testhost } in { proto tcp or proto icmp }")
        src = hbf.Hosts(['172.20.0.0/16'])
        dst = hbf.Hosts(['testhost'])
        tr_list = sorted([
            hbf.TransportMatch(proto='tcp'),
            hbf.TransportMatch(proto='icmp'),
        ])

        self.assertEqual(src, rule.src)
        self.assertEqual(dst, rule.dst)
        self.assertEqual(tr_list, rule.transports)

    def test_rule_proto_family(self):
        rule = hbf.Rule("add allow ip4 from { 127.0.0.1 or ::1 } to { 127.0.0.2 or ::2 } 80 proto tcp")
        src = hbf.Hosts(['127.0.0.1'])
        dst = hbf.Hosts(['127.0.0.2'])
        tr_list = [hbf.TransportMatch(proto='tcp', dst_port=hbf.Portlist(text='80'))]

        self.assertEqual(src, rule.src)
        self.assertEqual(dst, rule.dst)
        self.assertEqual(tr_list, rule.transports)

    def test_rule_proto_gre(self):
        rule = hbf.Rule("add allow ip4 from { 127.0.0.1 or ::1 } to { 127.0.0.2 or ::2 } proto gre")
        src = hbf.Hosts(['127.0.0.1'])
        dst = hbf.Hosts(['127.0.0.2'])
        tr_list = [hbf.TransportMatch(proto='gre')]

        self.assertEqual(src, rule.src)
        self.assertEqual(dst, rule.dst)
        self.assertEqual(tr_list, rule.transports)

    def test_rule_parse_keepstate(self):
        rule1 = hbf.Rule("add allow ip from test.yndx.net to any keep-state in")
        rule2 = hbf.Rule("add allow ip from test.yndx.net to any in NAMED_KEEP_STATE(CURRENT_SECTION)")
        for r in (rule1, rule2):
            self.assertTrue(r.keepstate and r.direction == 'in')
        self.assertEqual(rule1, rule2)

    def test_rule_render_multiport(self):
        # iptables требует, чтобы (--sport/--dport) следовал ранее, чем (-m multiport --dports/--sport)
        rule1 = hbf.Rule("add allow tcp from any 1024-65535 to any 53")
        rule2 = hbf.Rule("add allow tcp from any 53 to any 1024-65535")

        tr1, tr2 = rule1.transports[0], rule2.transports[0]

        self.assertEqual([' --proto tcp --dport 53 -m multiport --sports 1024:65535'], tr1.expand_iptables())
        self.assertEqual([' --proto tcp --sport 53 -m multiport --dports 1024:65535'], tr2.expand_iptables())

    def test_parse_macro_list(self):
        s = "{ _NET1_ or _NET2_ or _NET4_ or _NET3_ }"
        actual = hbf.Rule.parse_macro_list(s)
        expected = ("_NET1_", "_NET2_", "_NET4_", "_NET3_")
        self.assertEqual(expected, actual)

    def test_Hosts_cls_1(self):
        expected_prefixes = ['10.1.1.1',
                             '10.0.0.0/24',
                             '10.0.0.2/32',
                             ]
        expected_hosts = ['localhost.domain']  # 10.0.0.2
        expected_macroses = ['_C_TEST_MACRO_']  # testhost = 10.1.1.1

        hosts = hbf.Hosts(expected_prefixes + expected_hosts + expected_macroses)

        self.assertEqual(tuple(map(ip_network, expected_prefixes)), hosts.nets)
        self.assertEqual(tuple(expected_macroses), hosts.macroses)
        self.assertEqual(tuple(expected_hosts), hosts.hosts)

        collapsed_expected = map(ip_network, [
            '10.0.0.0/24',
            '10.1.1.1',
        ])
        self.assertEqual(sorted(collapsed_expected), sorted(hosts.prefixes()))

    def test_m4_parser1(self):
        self.patches['macroses'].stop()
        curpath = hbf.MACROSINC_PATH

        s = "define(_TEST_,` _TESTNETS_ or test.domain.net')dnl"
        expected = {'_TEST_': ('_TESTNETS_', 'test.domain.net')}

        fp = tempfile.NamedTemporaryFile()
        fp.write(s.encode('utf-8')+b"\n")
        fp.flush()
        hbf.MACROSINC_PATH = fp.name
        actual = {k: v for k, v in hbf.Macroses().data_iter()}
        self.assertEqual(expected, actual)

        s2 = """
        define(_TEST2_,` _TEST2NETS_ or _TEST22_NETS_ ')dnl
        define(_TEST3_,` dnl
        _TEST3NETS_ or dnl
        test5.localhost.domain dnl
        ')dnl
        """
        expected2 = {'_TEST3_': ('_TEST3NETS_', 'test5.localhost.domain'),
                     '_TEST2_': ('_TEST2NETS_', '_TEST22_NETS_')}
        s2 = dedent(s2.strip("\n"))
        fp.seek(0)
        fp.truncate()
        fp.write(s2.encode('utf-8'))
        fp.flush()
        actual2 = {k: v for k, v in hbf.Macroses().data_iter()}
        self.assertEqual(expected2, actual2)
        hbf.MACROSINC_PATH = curpath

    def test_m4_parser2(self):
        self.assertEqual(
            ('ALLOW_FROM_ANY', ['tcp', '{ _DISKUPLOADERSRV_ or _C_DISK_UPLOADER_ }', 'https']),
            hbf.parse_m4_function_call("ALLOW_FROM_ANY(tcp, `{ _DISKUPLOADERSRV_ or _C_DISK_UPLOADER_ }', https)"),
        )

    def test_portlist(self):
        pl = hbf.Portlist(text='22,80,80,443,1433,3433,4433,5433,8080,8081,8082,8083,35999,60812,6001-6010')
        self.assertEqual(
            ['-m multiport --dports 22,80,80,443,1433,3433,4433,5433,8080,8081,8082,8083,35999,60812',
             '-m multiport --dports 6001:6010'],
            pl.iptables['dport']
        )


class TestCollapse(BaseTest):
    def _check_collapse(self, expected, list_to_collapse):
        expand = lambda rules_list: tuple(sorted([t for r in rules_list for t in r.transports]))
        collapsed = tuple([x[0] for x in hbf.TransportMatch.collapse(expand(list_to_collapse))])
        self.assertEqual(expand(expected), collapsed)

    def test_rule_collapse(self):
        rule_ip = hbf.Rule('add allow ip from any to any')
        rule_tun = hbf.Rule('add allow ip from any to any proto ipencap')
        rule_tun2 = hbf.Rule('add allow ip from any to any proto ipencap')
        rule_http = hbf.Rule('add allow tcp from any to any 80,443')
        rule_ssh = hbf.Rule('add allow tcp from any to any telnet,ssh')
        rule_dns = hbf.Rule('add allow udp from any to any 53')
        rule_dhcp = hbf.Rule('add allow udp from any 67 to any 68')
        rule_sport1 = hbf.Rule('add allow udp from any 1-65000 to any')
        rule_sport2 = hbf.Rule('add allow udp from any 1024-65535 to any')

        self._check_collapse([rule_ip],
                             [rule_ip, rule_http, rule_ssh, rule_dns, rule_dhcp])
        self._check_collapse(
            [
                hbf.Rule('add allow tcp from any to any 80,443,telnet,ssh'),
                rule_dns,
                rule_dhcp,
            ],
            [rule_http, rule_ssh, rule_dns, rule_dhcp]
        )
        self._check_collapse(
            [
                hbf.Rule('add allow udp from any 1-65000,1024-65535 to any'),  # TODO: склеивать port range
                rule_tun,
                rule_dns,
                rule_dhcp,
            ],
            [rule_sport1, rule_sport2, rule_tun, rule_tun2, rule_dns, rule_dhcp]
        )


class SpecialRuleParse(BaseTest):
    MACROSES = {
        "_TESTMACRO1_": ["10.0.1.0/24"],
        "_TESTMACRO2_": ["10.0.2.0/24"],
        "_YANDEXNETS_": ["10.0.3.0/24"],
    }

    def _assert_scope(self, scope_map):
        for (sect_text, host_items) in scope_map:
            sect = hbf.Section('SECT', sect_text)
            self.assertEqual(hbf.Hosts(host_items), sect.scope)

    def _assert_rules(self, rule_map):
        for (sect_text, rules) in rule_map:
            sect = hbf.DummySection('SECT', sect_text)
            self.assertEqual([hbf.Rule(r) for r in rules], sect.rules)

    def test_ALLOW_STD_ICMP(self):
        self._assert_scope([
            ("ALLOW_STD_ICMP({ _TESTMACRO1_ })", ["_TESTMACRO1_"]),
            ("ALLOW_STD_ICMP({ _TESTMACRO1_ or _TESTMACRO2_ })", ["_TESTMACRO2_", "_TESTMACRO1_"]),
            ("ALLOW_STD_ICMP({ _TESTMACRO1_ }, { _TESTMACRO2_ })", ["_TESTMACRO1_"]),
        ])

    def test_DYNAMICACCESS(self):
        self._assert_scope([
            ("DYNAMICACCESS(tcp, `{ _TESTMACRO1_ }')", ['_TESTMACRO1_']),
            ("DYNAMICACCESS(tcp, `{ _TESTMACRO1_ or _TESTMACRO2_ })'", ['_TESTMACRO2_', '_TESTMACRO1_']),
            ("DYNAMICACCESS({ tcp }, `{ _TESTMACRO1_ }')", ["_TESTMACRO1_"]),
            ("DYNAMICACCESS(tcp, `{ _TESTMACRO1_ } 8888,37265')", ['_TESTMACRO1_']),
        ])

    def test_STD_SECTION_FOOTER_OUT(self):
        self._assert_scope([
            ("STD_SECTION_FOOTER_OUT({ _TESTMACRO1_ })", ["_TESTMACRO1_"]),
            ("STD_SECTION_FOOTER_OUT({ _TESTMACRO1_ or _TESTMACRO2_ })", ["_TESTMACRO2_", "_TESTMACRO1_"]),
            ("STD_SECTION_FOOTER_OUT({ _TESTMACRO1_ }, { _TESTMACRO2_ })", ["_TESTMACRO1_"]),
        ])

    def test_ALLOW_FROM_ANY(self):
        self._assert_rules([
            ("ALLOW_FROM_ANY(tcp, `{ _TESTMACRO1_ }', http,https,8080)", ["add allow tcp from any to { _TESTMACRO1_ } http,https,8080"]),
            ("ALLOW_FROM_ANY(tcp, { _TESTMACRO1_ }, `3478,3479,5349,5350')", ["add allow tcp from any to { _TESTMACRO1_ } 3478,3479,5349,5350"]),
            ("ALLOW_FROM_ANY(ip, `{ _TESTMACRO1_ }', `')", ["add allow ip from any to { _TESTMACRO1_ }"]),
            ("ALLOW_FROM_ANY(esp, `{ _TESTMACRO1_ }')", ["add allow esp from any to { _TESTMACRO1_ }"]),
            ("ALLOW_FROM_ANY({ tcp or udp }, `{ _TESTMACRO1_ }', domain)", ["add allow { tcp or udp } from any to { _TESTMACRO1_ } domain"]),
        ])

    def test_ALLOW_FROM_YANDEXNETS(self):
        self._assert_rules([
            ("ALLOW_FROM_YANDEXNETS(tcp, `{ _TESTMACRO1_ }', http,https,8080)", ["add allow tcp from { _YANDEXNETS_ } to { _TESTMACRO1_ } http,https,8080"]),
            ("ALLOW_FROM_YANDEXNETS(tcp, { _TESTMACRO1_ }, `3478,3479,5349,5350')", ["add allow tcp from { _YANDEXNETS_ } to { _TESTMACRO1_ } 3478,3479,5349,5350"]),
            ("ALLOW_FROM_YANDEXNETS(ip, `{ _TESTMACRO1_ }', `')", ["add allow ip from { _YANDEXNETS_ } to { _TESTMACRO1_ }"]),
            ("ALLOW_FROM_YANDEXNETS(esp, `{ _TESTMACRO1_ }')", ["add allow esp from { _YANDEXNETS_ } to { _TESTMACRO1_ }"]),
            ("ALLOW_FROM_YANDEXNETS({ tcp or udp }, `{ _TESTMACRO1_ }', domain)", ["add allow { tcp or udp } from { _YANDEXNETS_ } to { _TESTMACRO1_ } domain"]),
        ])
