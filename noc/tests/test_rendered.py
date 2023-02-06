import asyncio
import json
import re
import unittest.mock
from textwrap import dedent

from aiohttp.web_exceptions import HTTPBadRequest

import hbf.code as hbf
from . import BaseTest


class TestRendered(BaseTest):
    HOSTS = {
        "testhost": ["10.1.1.1"],
    }
    MACROSES = {
        "_YANDEXNETS_": ["93.158.0.0/18", "2a02:6b8::/32"],
        "_TARGET1_": ["400/24@2a02:6b8:c00::/40"],
        "_FASTBONE_": [
            "2620:10f:d00f::/48",
            "2a02:6b8:0:a00::/56",
            "2a02:6b8:0:1603::/64",
            "2a02:6b8:f000::/36",
        ],
    }

    def setUp(self):
        super().setUp()
        hbf.FW().sections = {
            hbf.constants.INET_SECTION_NAME: hbf.InetSection(
                hbf.constants.INET_SECTION_NAME,
                """
                    # интернет включен на всех адресах
                    add allow ip from any to { inet }
                """,
                no_index=True,
            )
        }
        self._register_patch('art_siblings', unittest.mock.patch('hbf.art.MAX_SIBLINGS', 4))

    def _assert_ruleset(self, expected, section_content, targets, *_, prelog_hook=False, log_drop=False, **kwargs):
        self._assert_ruleset_with_sections(
            expected,
            [hbf.Section("testsection", dedent(section_content.strip("\n")))],
            targets,
            prelog_hook=prelog_hook,
            log_drop=log_drop,
            **kwargs,
        )

    def _assert_ruleset_with_sections(
        self,
        expected,
        sections,
        targets,
        *,
        prelog_hook=False,
        log_drop=False,
        include_pre_end=False,
        **kwargs,
    ):
        expected = dedent(expected).strip()

        fw = hbf.FW()
        fw.macroses = list()
        for section in sections:
            fw.sections[section.name] = section
        fw.sections = fw.sections  # стриггерить пересчёт индексов

        targets, errors = hbf.make_targets(targets.split(','))
        classification_targets = None
        if include_pre_end:
            classification_targets = targets
        rules_count, ruleset = hbf.build_iptables_ruleset(targets, **kwargs)
        fw_text = hbf.render_iptables_text(
            ruleset,
            prelog_hook=prelog_hook,
            log_drop=log_drop,
            classification_targets=classification_targets,
            output="out" in kwargs.get("directions", []),
        )
        fw_text = re.sub(r"(\s*\n){3,}", "\n\n", fw_text)
        self.assertEqual(expected, fw_text.strip())

    def test_fw_filter_nested_rules(self):
        expected = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y_testhost -

            :Y1_TO_10.1.1.1 -
            :Y1_10.0.0.0/24 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -f -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_END_IN -j DROP

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"
            -A Y_FW --destination 10.1.1.1 -j Y_testhost

            -A Y_testhost -j Y_BEGIN_IN
            -A Y_testhost --destination 10.1.1.1 -j Y1_TO_10.1.1.1
            -A Y_testhost --destination 10.1.1.1 --proto 1 -j ACCEPT
            -A Y_testhost -j Y_END_IN

            -A Y1_TO_10.1.1.1 --source 10.0.0.0/24 -g Y1_10.0.0.0/24

            -A Y1_10.0.0.0/24 -j ACCEPT

            COMMIT
            #END IPTABLES
        """

        section_content = """
        add allow ip from 10.0.0.0/24 to { testhost }

        add allow tcp from 10.0.0.0 to { testhost }
        add allow udp from 10.0.0.0 to { testhost }

        add allow tcp from 10.0.0.1 to 10.1.1.1
        add allow udp from 10.0.0.1 to 10.1.1.1

        ALLOW_STD_ICMP(0.0.0.0/0)
        """

        self._assert_ruleset(expected, section_content, 'testhost=10.1.1.1')

    def test_fw_icmp(self):
        fw = hbf.FW()
        fw.sections["ALLOW_ICMP_YANDEXNETS"] = hbf.DummySection(
            "ALLOW_ICMP_YANDEXNETS",
            rs_key=hbf.RulesetKey(root_name='ALLOW_ICMP_YANDEXNETS', sort_prio=100),
            content="""
            # Разрешаем ICMP между _YANDEXNETS_
            add allow icmp from { _YANDEXNETS_ or _NOT_SO_EXTERNAL_NETS_ } to { _YANDEXNETS_ or _NOT_SO_EXTERNAL_NETS_ }
            add allow ip from { _YANDEXNETS_ or _NOT_SO_EXTERNAL_NETS_ } to { _YANDEXNETS_ or _NOT_SO_EXTERNAL_NETS_ } proto ipv6-icmp
            """,
        )
        # Правило из Яндекс в inet. Тут icmp должен работать из/в этого IP в/из inet.
        fw.sections[hbf.constants.INET_SECTION_NAME] = hbf.InetSection(
            hbf.constants.INET_SECTION_NAME,
            """
            add allow tcp from 2a02:6b8::1 to { inet }
            """,
            no_index=True,
        )

        expected = """
        #BEGIN IP6TABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -

        :Y_BEGIN_IN -
        :Y_END_IN -

        :Y_BEGIN_OUT -
        :Y_END_OUT -
        :Y_END_OUT_INET -

        :Y_ya::1_OUT -
        :Y_ya::1 -
        :Y_ya::2_OUT -
        :Y_ya::2 -

        :Y1_ALLOW_ICMP_YANDEXNETS -
        :Y1_ya::/32 -

        :Y2_ALLOW_ICMP_YANDEXNETS -
        :Y2_ya::/32 -

        :Y3_FROM_ya::2 -

        :Y4_TO_ya::2 -

        -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_IN -i lo -j ACCEPT

        -A Y_BEGIN_OUT -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_OUT -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_OUT -o lo -j ACCEPT
        -A Y_BEGIN_OUT -p udp -m multiport --dports 33434:33529 -j ACCEPT

        -A Y_END_IN -j DROP

        -A Y_END_OUT -j REJECT --reject-with icmp6-adm-prohibited

        -A Y_FW --destination 2a02:6b8::1 -j Y_ya::1
        -A Y_FW --destination 2a02:6b8::2 -j Y_ya::2

        -A Y_FW_OUT --source 2a02:6b8::1 -j Y_ya::1_OUT
        -A Y_FW_OUT --source 2a02:6b8::2 -j Y_ya::2_OUT

        -A Y_ya::1_OUT -j Y_BEGIN_OUT
        -A Y_ya::1_OUT --source 2a02:6b8::/32 -j Y1_ALLOW_ICMP_YANDEXNETS
        -A Y_ya::1_OUT --source 2a02:6b8::1 --proto 58 -j ACCEPT
        -A Y_ya::1_OUT -j Y_DRP
        -A Y_ya::1_OUT -j Y_END_OUT_INET
        -A Y_ya::1_OUT -j ACCEPT

        -A Y_ya::1 -j Y_BEGIN_IN
        -A Y_ya::1 --destination 2a02:6b8::/32 -j Y2_ALLOW_ICMP_YANDEXNETS
        -A Y_ya::1 --destination 2a02:6b8::1 --proto 58 -j ACCEPT
        -A Y_ya::1 -j Y_END_IN

        -A Y_ya::2_OUT -j Y_BEGIN_OUT
        -A Y_ya::2_OUT --source 2a02:6b8::2 --proto tcp --dport 22 -j Y3_FROM_ya::2
        -A Y_ya::2_OUT --source 2a02:6b8::/32 -j Y1_ALLOW_ICMP_YANDEXNETS
        -A Y_ya::2_OUT -j Y_END_OUT

        -A Y_ya::2 -j Y_BEGIN_IN
        -A Y_ya::2 --destination 2a02:6b8::2 --proto tcp --dport 22 -j Y4_TO_ya::2
        -A Y_ya::2 --destination 2a02:6b8::/32 -j Y2_ALLOW_ICMP_YANDEXNETS
        -A Y_ya::2 -j Y_END_IN

        -A Y1_ALLOW_ICMP_YANDEXNETS --destination 2a02:6b8::/32 -g Y1_ya::/32

        -A Y1_ya::/32 -j ACCEPT --proto 1
        -A Y1_ya::/32 -j ACCEPT --proto 58

        -A Y2_ALLOW_ICMP_YANDEXNETS --source 2a02:6b8::/32 -g Y2_ya::/32

        -A Y2_ya::/32 -j ACCEPT --proto 1
        -A Y2_ya::/32 -j ACCEPT --proto 58

        -A Y3_FROM_ya::2 --destination 2a02:6b8::2 -j ACCEPT --proto tcp --dport 22

        -A Y4_TO_ya::2 --source 2a02:6b8::2 -j ACCEPT --proto tcp --dport 22

        COMMIT
        #END IP6TABLES
        #BEGIN IPTABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -

        COMMIT
        #END IPTABLES
        """

        # Второе правило из Яндекс в Яндекс. Тут icmp ТОЛЬКО между _YANDEXNETS_. В inet и из него - не должен.
        section_content = """
            add allow tcp from 2a02:6b8::2 to 2a02:6b8::2 22

            ALLOW_STD_ICMP(::/0)
            """

        self._assert_ruleset(
            expected,
            section_content,
            '2a02:6b8::1,2a02:6b8::2',
            directions=('in', 'out'),
        )

    def test_fw_filter_nested_rules_with_debug(self):
        expected = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y_testhost -

            :Y1_TO_10.1.1.1 -
            :Y1_10.0.0.0/24 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -f -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_END_IN -j DROP

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"
            -A Y_FW --destination 10.1.1.1 -j Y_testhost

            -A Y_testhost -j Y_BEGIN_IN
            -A Y_testhost --destination 10.1.1.1 -j Y1_TO_10.1.1.1
            -A Y_testhost --destination 10.1.1.1 --proto 1 -j ACCEPT
            -A Y_testhost -j Y_END_IN

            -A Y1_TO_10.1.1.1 --source 10.0.0.0/24 -g Y1_10.0.0.0/24

            -A Y1_10.0.0.0/24 -j ACCEPT -m comment --comment "testsection:1" -m comment --comment "rule from Inet to 10.0.0.0/24, filtering by MSS"

            COMMIT
            #END IPTABLES
        """

        section_content = """
        add allow ip from 10.0.0.0/24 to { testhost }

        add allow tcp from 10.0.0.0 to { testhost }
        add allow udp from 10.0.0.0 to { testhost }

        add allow tcp from 10.0.0.1 to 10.1.1.1
        add allow udp from 10.0.0.1 to 10.1.1.1

        ALLOW_STD_ICMP(0.0.0.0/0)
        """

        self._assert_ruleset(expected, section_content, 'testhost=10.1.1.1', debug=True)

    def test_fw_filter_nested_rules_with_reject(self):
        expected = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y_testhost -

            :Y1_TO_10.1.1.1 -
            :Y1_10.0.0.0/24 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -f -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_END_IN -j DROP

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"
            -A Y_FW --destination 10.1.1.1 -j Y_testhost

            -A Y_testhost -j Y_BEGIN_IN
            -A Y_testhost --destination 10.1.1.1 -j Y1_TO_10.1.1.1
            -A Y_testhost --destination 10.1.1.1 --proto 1 -j ACCEPT
            -A Y_testhost -j Y_END_IN

            -A Y1_TO_10.1.1.1 --source 10.0.0.0/24 -g Y1_10.0.0.0/24

            -A Y1_10.0.0.0/24 -j ACCEPT

            COMMIT
            #END IPTABLES
        """

        section_content = """
        add allow ip from 10.0.0.0/24 to { testhost }

        add allow tcp from 10.0.0.0 to { testhost }
        add allow udp from 10.0.0.0 to { testhost }

        add allow tcp from 10.0.0.1 to 10.1.1.1
        add deny udp from 10.0.0.1 to 10.1.1.1

        ALLOW_STD_ICMP(0.0.0.0/0)
        """

        self._assert_ruleset(expected, section_content, 'testhost=10.1.1.1')

    def test_fw1(self):
        expected = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y_testhost -

            :Y1_TO_10.1.1.1 -
            :Y1_10.0.0.0/14 -
            :Y1_10.0.0.0/24 -
            :Y1_10.2.0.0/24 -
            :Y1_10.7.4.0/29 -
            :Y1_10.7.4.1 -
            :Y1_10.7.4.2 -
            :Y1_10.7.4.4 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -f -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_END_IN -j DROP

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"
            -A Y_FW --destination 10.1.1.1 -j Y_testhost

            -A Y_testhost -j Y_BEGIN_IN
            -A Y_testhost --destination 10.1.1.1 -j Y1_TO_10.1.1.1
            -A Y_testhost --destination 10.1.1.1 --proto 1 -j ACCEPT
            -A Y_testhost -j Y_END_IN

            -A Y1_TO_10.1.1.1 -j ACCEPT --proto tcp --dport 80
            -A Y1_TO_10.1.1.1 --source 10.0.0.0/14 -g Y1_10.0.0.0/14
            -A Y1_TO_10.1.1.1 --source 10.7.4.0/29 -g Y1_10.7.4.0/29
            -A Y1_TO_10.1.1.1 --source 10.6.0.1 -j ACCEPT --proto udp --sport 53 --dport 80

            -A Y1_10.0.0.0/14 --source 10.0.0.0/24 -g Y1_10.0.0.0/24
            -A Y1_10.0.0.0/14 --source 10.1.0.0/24 -j ACCEPT
            -A Y1_10.0.0.0/14 --source 10.2.0.0/24 -g Y1_10.2.0.0/24

            -A Y1_10.0.0.0/24 -j ACCEPT

            -A Y1_10.2.0.0/24 -j ACCEPT

            -A Y1_10.7.4.0/29 --source 10.7.4.1 -g Y1_10.7.4.1
            -A Y1_10.7.4.0/29 --source 10.7.4.2 -g Y1_10.7.4.2
            -A Y1_10.7.4.0/29 --source 10.7.4.4 -g Y1_10.7.4.4

            -A Y1_10.7.4.1 -j ACCEPT --proto udp -m multiport --dports 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14
            -A Y1_10.7.4.1 -j ACCEPT --proto udp -m multiport --dports 15,16,17,18,19

            -A Y1_10.7.4.2 -j ACCEPT --proto udp -m multiport --sports 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14
            -A Y1_10.7.4.2 -j ACCEPT --proto udp -m multiport --sports 15,16,17,18,19

            -A Y1_10.7.4.4 -j ACCEPT --proto udp -m multiport --sports 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14 -m multiport --dports 20,21,22,23,24,25,26,27,28,29,30,31,32,33,34
            -A Y1_10.7.4.4 -j ACCEPT --proto udp -m multiport --sports 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14 -m multiport --dports 35,36,37,38,39
            -A Y1_10.7.4.4 -j ACCEPT --proto udp -m multiport --sports 15,16,17,18,19 -m multiport --dports 20,21,22,23,24,25,26,27,28,29,30,31,32,33,34
            -A Y1_10.7.4.4 -j ACCEPT --proto udp -m multiport --sports 15,16,17,18,19 -m multiport --dports 35,36,37,38,39

            COMMIT
            #END IPTABLES
        """

        section_content = """
        add allow ip from 10.0.0.0/24 to { testhost }
        add allow ip from 10.1.0.0/24 to { testhost }
        add allow ip from 10.2.0.0/24 to { testhost }
        add allow ip from 10.2.0.0/25 to { testhost }

        add allow tcp from 10.0.0.0 to { testhost }
        add allow udp from 10.0.0.0 to { testhost }

        add allow tcp from 10.0.0.1 to 10.1.1.1
        add allow udp from 10.0.0.1 to 10.1.1.1

        add allow tcp from any to 10.1.1.1 80
        add allow udp from 10.6.0.1 domain to 10.1.1.1 80

        # более 15 портов в dstport
        add allow udp from 10.7.4.1 to 10.1.1.1 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19
        # более 15 портов в srcport
        add allow udp from 10.7.4.2 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 to 10.1.1.1
        # более 15 портов в srcport и dstport
        add allow udp from 10.7.4.4 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 to 10.1.1.1 20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39

        ALLOW_STD_ICMP(0.0.0.0/0)
        """
        self._assert_ruleset(expected, section_content, 'testhost=10.1.1.1')

    def test_fw2(self):
        expected = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y_::1 -

            :Y1_TO_::1 -
            :Y1_ya:c00::/40 -
            :Y1_0/30@ya:c00::/40 -
            :Y1_1000/30@ya:c00::/40 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_END_IN -j DROP

            -A Y_FW --destination ::1 -j Y_::1

            -A Y_::1 -j Y_BEGIN_IN
            -A Y_::1 --destination ::1 -j Y1_TO_::1
            -A Y_::1 --destination ::1 --proto 58 -j ACCEPT
            -A Y_::1 -j Y_END_IN

            -A Y1_TO_::1 --source 2a02:6b8:c00::/40 -g Y1_ya:c00::/40

            -A Y1_ya:c00::/40 -m u32 --u32 "16 & 0xfffffffc = 0x0" -g Y1_0/30@ya:c00::/40
            -A Y1_ya:c00::/40 -m u32 --u32 "16 & 0xfffffffc = 0x1000" -g Y1_1000/30@ya:c00::/40
            -A Y1_ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x4" -j ACCEPT

            -A Y1_0/30@ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x1" -j ACCEPT
            -A Y1_0/30@ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x2" -j ACCEPT
            -A Y1_0/30@ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x3" -j ACCEPT

            -A Y1_1000/30@ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x1001" -j ACCEPT
            -A Y1_1000/30@ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x1002" -j ACCEPT
            -A Y1_1000/30@ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x1003" -j ACCEPT

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            COMMIT
            #END IPTABLES
        """

        section_content = """
        add allow ip from 1@2a02:6b8:c00::/40 to ::1
        add allow ip from 2@2a02:6b8:c00::/40 to ::1
        add allow ip from 3@2a02:6b8:c00::/40 to ::1
        add allow ip from 4@2a02:6b8:c00::/40 to ::1
        add allow ip from 1001@2a02:6b8:c00::/40 to ::1
        add allow ip from 1002@2a02:6b8:c00::/40 to ::1
        add allow ip from 1003@2a02:6b8:c00::/40 to ::1

        ALLOW_STD_ICMP(::/0)
        """
        self._assert_ruleset(expected, section_content, '::1')

    def test_fw_fastbone_backbone_preemption(self):
        """
        Note that there should be exactly two rules in Y_FW chain. The order
        of input targets doesn't matter.
        """

        expected = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y_ya:c01:737:0:604:b2a9:7b16 -
            :Y_JhKH:1a21:100:1538:0:6989 -

            :Y1_TO_lIoX:0:604:b2a9:7b16 -
            :Y1_ya:c00::/40 -
            :Y1_0@ya:c00::/40 -

            :Y2_TO_604@ya:c00::/40 -
            :Y2_ya:c00::/40 -

            :Y3_TO_1001538@ya:fc00::/40 -
            :Y3_ya:fc00::/40 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_END_IN -j DROP

            -A Y_FW --destination 2a02:6b8:c01:737:0:604:b2a9:7b16 -j Y_ya:c01:737:0:604:b2a9:7b16
            -A Y_FW --destination 2a02:6b8:fc11:1a21:100:1538:0:6989 -j Y_JhKH:1a21:100:1538:0:6989

            -A Y_ya:c01:737:0:604:b2a9:7b16 -j Y_BEGIN_IN
            -A Y_ya:c01:737:0:604:b2a9:7b16 --destination 2a02:6b8:c01:737:0:604:b2a9:7b16 --proto tcp --dport 80 -j Y1_TO_lIoX:0:604:b2a9:7b16
            -A Y_ya:c01:737:0:604:b2a9:7b16 --destination 2a02:6b8:c00::/40 -m u32 --u32 "32 & 0xffffffff = 0x604" -j Y2_TO_604@ya:c00::/40
            -A Y_ya:c01:737:0:604:b2a9:7b16 --destination 2a02:6b8:c01:737:0:604:b2a9:7b16 --proto 58 -j ACCEPT
            -A Y_ya:c01:737:0:604:b2a9:7b16 -j Y_END_IN

            -A Y_JhKH:1a21:100:1538:0:6989 -j Y_BEGIN_IN
            -A Y_JhKH:1a21:100:1538:0:6989 --destination 2a02:6b8:fc00::/40 -m u32 --u32 "32 & 0xffffffff = 0x1001538" -j Y3_TO_1001538@ya:fc00::/40
            -A Y_JhKH:1a21:100:1538:0:6989 --destination 2a02:6b8:fc11:1a21:100:1538:0:6989 --proto 58 -j ACCEPT
            -A Y_JhKH:1a21:100:1538:0:6989 -j Y_END_IN

            -A Y1_TO_lIoX:0:604:b2a9:7b16 --source 2a02:6b8:c00::/40 -g Y1_ya:c00::/40

            -A Y1_ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x0" -g Y1_0@ya:c00::/40

            -A Y1_0@ya:c00::/40 --source 2a02:6b8:c00::2 -j ACCEPT --proto tcp --dport 80

            -A Y2_TO_604@ya:c00::/40 --source 2a02:6b8:c00::/40 -g Y2_ya:c00::/40

            -A Y2_ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x604" -j ACCEPT

            -A Y3_TO_1001538@ya:fc00::/40 --source 2a02:6b8:fc00::/40 -g Y3_ya:fc00::/40

            -A Y3_ya:fc00::/40 -m u32 --u32 "16 & 0xffffffff = 0x1001538" -j ACCEPT

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            COMMIT
            #END IPTABLES
        """

        section_content_bb = """
        add allow tcp from 2a02:6b8:c00::2 to 2a02:6b8:c01:737:0:604:b2a9:7b16 80
        ALLOW_STD_ICMP(::/0)
        """
        section_content_fb = """
        add allow tcp from 2a02:6b8:c00::20 to 2a02:6b8:fc11:1a21:100:1538:0:6989 8080
        ALLOW_STD_ICMP(::/0)
        """

        self._assert_ruleset_with_sections(
            expected,
            [
                hbf.Section("bb", dedent(section_content_bb.strip("\n")), namespace=hbf.SectionNamespace.Backbone),
                hbf.Section("fb", dedent(section_content_fb.strip("\n")), namespace=hbf.SectionNamespace.Fastbone),
            ],
            '2a02:6b8:c01:737:0:604:b2a9:7b16,2a02:6b8:fc11:1a21:100:1538:0:6989',
        )

    def test_fw_magic(self):
        expected = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y_::1 -

            :Y1_TO_::1 -
            :Y1_ya:c00::/40 -
            :Y1_ya:c00::/40* -
            :Y1_ya:c00::/42 -
            :Y1_0/30@ya:c00::/40 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_END_IN -j DROP

            -A Y_FW --destination ::1 -j Y_::1

            -A Y_::1 -j Y_BEGIN_IN
            -A Y_::1 --destination ::1 -j Y1_TO_::1
            -A Y_::1 --destination ::1 --proto 58 -j ACCEPT
            -A Y_::1 -j Y_END_IN

            -A Y1_TO_::1 --source 2a02:6b8:c00::/40 -g Y1_ya:c00::/40

            -A Y1_ya:c00::/40 -j Y1_ya:c00::/40*
            -A Y1_ya:c00::/40 -m u32 --u32 "16 & 0xfffffffc = 0x0" -g Y1_0/30@ya:c00::/40
            -A Y1_ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x4" -j ACCEPT
            -A Y1_ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x5" -j ACCEPT

            -A Y1_ya:c00::/40* --source 2a02:6b8:c00::/42 -g Y1_ya:c00::/42
            -A Y1_ya:c00::/40* --source 2a02:6b8:c56:200::/64 -j ACCEPT

            -A Y1_ya:c00::/42 --source 2a02:6b8:c12:500::/56 -j ACCEPT
            -A Y1_ya:c00::/42 --source 2a02:6b8:c15:200::/56 -j ACCEPT
            -A Y1_ya:c00::/42 --source 2a02:6b8:c20:500::/64 -j ACCEPT
            -A Y1_ya:c00::/42 --source 2a02:6b8:c30:300::/56 -j ACCEPT

            -A Y1_0/30@ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x1" -j ACCEPT
            -A Y1_0/30@ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x2" -j ACCEPT
            -A Y1_0/30@ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x3" -j ACCEPT

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            COMMIT
            #END IPTABLES
        """

        section_content = """
        add allow ip from 2a02:6b8:c12:500::/56 to ::1
        add allow ip from 2a02:6b8:c15:200::/56 to ::1
        add allow ip from 2a02:6b8:c20:500::/64 to ::1
        add allow ip from 2a02:6b8:c30:300::/56 to ::1
        add allow ip from 2a02:6b8:c56:200::/64 to ::1

        add allow ip from 1@2a02:6b8:c00::/40 to ::1
        add allow ip from 2@2a02:6b8:c00::/40 to ::1
        add allow ip from 3@2a02:6b8:c00::/40 to ::1
        add allow ip from 4@2a02:6b8:c00::/40 to ::1
        add allow ip from 5@2a02:6b8:c00::/40 to ::1

        ALLOW_STD_ICMP(::/0)
        """

        self._assert_ruleset(expected, section_content, '::1')

    def test_trypo_ic(self):
        # нужно всегда вставлять разрешающее правило между одним project id
        expected = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y_ya:c00:100:0:640:0:1 -

            :Y1_TO_ya:c00:100:0:640:0:1 -

            :Y2_TO_640@ya:c00::/40 -
            :Y2_ya:c00::/40 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_END_IN -j DROP

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"
            -A Y_FW --destination 2a02:6b8:c00:100:0:640:0:1 -j Y_ya:c00:100:0:640:0:1

            -A Y_ya:c00:100:0:640:0:1 -j Y_BEGIN_IN
            -A Y_ya:c00:100:0:640:0:1 --destination 2a02:6b8:c00:100:0:640:0:1 --proto udp --dport 88 -j Y1_TO_ya:c00:100:0:640:0:1
            -A Y_ya:c00:100:0:640:0:1 --destination 2a02:6b8:c00::/40 -m u32 --u32 "32 & 0xffffffff = 0x640" -j Y2_TO_640@ya:c00::/40
            -A Y_ya:c00:100:0:640:0:1 --destination 2a02:6b8:c00:100:0:640:0:1 --proto 58 -j ACCEPT
            -A Y_ya:c00:100:0:640:0:1 -j Y_END_IN

            -A Y1_TO_ya:c00:100:0:640:0:1 -j ACCEPT --proto udp --dport 88 -m comment --comment "testsection:1" -m comment --comment "rule from Inet to ::/0, filtering by MSS"

            -A Y2_TO_640@ya:c00::/40 --source 2a02:6b8:c00::/40 -g Y2_ya:c00::/40

            -A Y2_ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x640" -j ACCEPT -m comment --comment "project-id interconnect auto rule DUMMY_AUTO_IC:0"

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"

            COMMIT
            #END IPTABLES
        """
        # в этой секции нет специального правила для IC. ожидаем что автоматика его сама вставит
        section_content = """
        add allow udp from any to 2a02:6b8:c00:100:0:640:0:1 88

        ALLOW_STD_ICMP(::/0)
        """

        self._assert_ruleset(expected, section_content, '2a02:6b8:c00:100:0:640:0:1', debug=True)

    def test_fw_cache(self):
        # проверка rewrite_ruleset_chain_prefix
        # тут воспроизводится ситуация когда в кеше есть срендеренный рулсет, но с другим chain_prefix
        expected1 = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y_::1 -

            :Y1_TO_::/127 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_END_IN -j DROP

            -A Y_FW --destination ::1 -j Y_::1

            -A Y_::1 -j Y_BEGIN_IN
            -A Y_::1 --destination ::/127 -j Y1_TO_::/127
            -A Y_::1 --destination ::1 --proto 58 -j ACCEPT
            -A Y_::1 -j Y_END_IN

            -A Y1_TO_::/127 --source 2a02:6b8:c:500::/56 -j ACCEPT

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            COMMIT
            #END IPTABLES
        """
        expected2 = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y_::1 -

            :Y1_TO_::/120 -

            :Y2_TO_::/126 -

            :Y3_TO_::/127 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_END_IN -j DROP

            -A Y_FW --destination ::1 -j Y_::1

            -A Y_::1 -j Y_BEGIN_IN
            -A Y_::1 --destination ::/120 -j Y1_TO_::/120
            -A Y_::1 --destination ::/126 -j Y2_TO_::/126
            -A Y_::1 --destination ::/127 -j Y3_TO_::/127
            -A Y_::1 --destination ::1 --proto 58 -j ACCEPT
            -A Y_::1 -j Y_END_IN

            -A Y1_TO_::/120 --source 2a02:6b8:d:500::/56 -j ACCEPT

            -A Y2_TO_::/126 --source 2a02:6b8:d:500::/56 -j ACCEPT

            -A Y3_TO_::/127 --source 2a02:6b8:c:500::/56 -j ACCEPT

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            COMMIT
            #END IPTABLES
        """
        section1 = """
        add allow ip from 2a02:6b8:c:500::/56 to ::/127

        ALLOW_STD_ICMP(::/0)
        """

        section2 = """
        add allow ip from 2a02:6b8:c:500::/56 to ::/127
        add allow ip from 2a02:6b8:d:500::/56 to ::/126
        add allow ip from 2a02:6b8:d:501::/56 to ::/126
        add allow ip from 2a02:6b8:d:500::/56 to ::/120

        ALLOW_STD_ICMP(::/0)
        """

        self._assert_ruleset(expected1, section1, '::1', caching=False)
        self._assert_ruleset(expected1, section1, '::1', caching=True)
        # тут из кеша будут данные
        self._assert_ruleset(expected1, section1, '::1', caching=True)

        self._assert_ruleset(expected2, section2, '::1', caching=False)
        self._assert_ruleset(expected2, section2, '::1', caching=True)

    def test_prelog_hook(self):
        section1 = """
        add allow ip from 10.0.0.0 to { 10.0.0.0 or fc00:: }
        ALLOW_STD_ICMP({10.0.0.0 or fc00:: })
        """
        expected1 = """
        #BEGIN IP6TABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -

        :Y_BEGIN_IN -
        :Y_END_IN -
        :Y_PRELOG_HOOK_IN -

        :Y_BEGIN_OUT -
        :Y_END_OUT -
        :Y_END_OUT_INET -
        :Y_PRELOG_HOOK_OUT -

        :Y_fc00::_OUT -
        :Y_fc00:: -

        :Y1_TO_fc00:: -

        -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_IN -i lo -j ACCEPT

        -A Y_BEGIN_OUT -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_OUT -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_OUT -o lo -j ACCEPT
        -A Y_BEGIN_OUT -p udp -m multiport --dports 33434:33529 -j ACCEPT

        -A Y_END_IN -j Y_PRELOG_HOOK_IN
        -A Y_END_IN -j LOG --log-prefix "Y_FW drop: "
        -A Y_END_IN -j DROP

        -A Y_END_OUT -j Y_PRELOG_HOOK_OUT
        -A Y_END_OUT -j LOG --log-prefix "Y_FW_OUT drop: "
        -A Y_END_OUT -j REJECT --reject-with icmp6-adm-prohibited

        -A Y_FW --destination fc00:: -j Y_fc00::

        -A Y_FW_OUT --source fc00:: -j Y_fc00::_OUT

        -A Y_fc00::_OUT -j Y_BEGIN_OUT
        -A Y_fc00::_OUT --source fc00:: --proto 58 -j ACCEPT
        -A Y_fc00::_OUT -j Y_DRP
        -A Y_fc00::_OUT -j Y_END_OUT_INET
        -A Y_fc00::_OUT -j ACCEPT

        -A Y_fc00:: -j Y_BEGIN_IN
        -A Y_fc00:: --destination fc00:: -j Y1_TO_fc00::
        -A Y_fc00:: --destination fc00:: --proto 58 -j ACCEPT
        -A Y_fc00:: -j Y_END_IN

        COMMIT
        #END IP6TABLES
        #BEGIN IPTABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -

        :Y_BEGIN_IN -
        :Y_END_IN -
        :Y_PRELOG_HOOK_IN -

        :Y_BEGIN_OUT -
        :Y_END_OUT -
        :Y_END_OUT_INET -
        :Y_PRELOG_HOOK_OUT -

        :Y_10.0.0.0_OUT -
        :Y_10.0.0.0 -

        :Y1_FROM_10.0.0.0 -

        :Y2_TO_10.0.0.0 -

        -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_IN -f -j ACCEPT
        -A Y_BEGIN_IN -i lo -j ACCEPT

        -A Y_BEGIN_OUT -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_OUT -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_OUT -f -j ACCEPT
        -A Y_BEGIN_OUT -o lo -j ACCEPT
        -A Y_BEGIN_OUT -p udp -m multiport --dports 33434:33529 -j ACCEPT

        -A Y_END_IN -j Y_PRELOG_HOOK_IN
        -A Y_END_IN -j LOG --log-prefix "Y_FW drop: "
        -A Y_END_IN -j DROP

        -A Y_END_OUT -j Y_PRELOG_HOOK_OUT
        -A Y_END_OUT -j LOG --log-prefix "Y_FW_OUT drop: "
        -A Y_END_OUT -j REJECT --reject-with icmp-net-prohibited

        -A Y_FW --destination 10.0.0.0 -j Y_10.0.0.0

        -A Y_FW_OUT --source 10.0.0.0 -j Y_10.0.0.0_OUT

        -A Y_10.0.0.0_OUT -j Y_BEGIN_OUT
        -A Y_10.0.0.0_OUT --source 10.0.0.0 -j Y1_FROM_10.0.0.0
        -A Y_10.0.0.0_OUT --source 10.0.0.0 --proto 1 -j ACCEPT
        -A Y_10.0.0.0_OUT -j Y_DRP
        -A Y_10.0.0.0_OUT -j Y_END_OUT_INET
        -A Y_10.0.0.0_OUT -j ACCEPT

        -A Y_10.0.0.0 -j Y_BEGIN_IN
        -A Y_10.0.0.0 --destination 10.0.0.0 -j Y2_TO_10.0.0.0
        -A Y_10.0.0.0 --destination 10.0.0.0 --proto 1 -j ACCEPT
        -A Y_10.0.0.0 -j Y_END_IN

        -A Y1_FROM_10.0.0.0 --destination 10.0.0.0 -j ACCEPT

        -A Y2_TO_10.0.0.0 --source 10.0.0.0 -j ACCEPT

        COMMIT
        #END IPTABLES
        """
        self._assert_ruleset(expected1, section1, '10.0.0.0,fc00::', log_drop=True, directions=('in', 'out'))

    def test_training(self):
        fw = hbf.FW()
        section1 = """
        add allow ip from 10.0.0.0 to { 10.0.0.0 or fc00:: }
        ALLOW_STD_ICMP({10.0.0.0 or fc00:: })
        """
        fw.sections[hbf.TRAINING_SECTION_NAME] = hbf.DummySection(
            hbf.TRAINING_SECTION_NAME,
            no_index=True,
            content="""
                add allow tcp from any 48000 to { _YANDEXNETS_ } 80
                """
        )
        expected1 = """
        #BEGIN IP6TABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -

        COMMIT
        #END IP6TABLES
        #BEGIN IPTABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -
        :Y_FW_orig -
        :Y_FW_OUT_orig -

        :Y_BEGIN_IN -
        :Y_END_IN -

        :Y_BEGIN_OUT -
        :Y_END_OUT -
        :Y_END_OUT_INET -

        :Y_TR_10.0.0.0_OUT -
        :Y_TR_10.0.0.0 -
        :Y_10.0.0.0_OUT -
        :Y_10.0.0.0 -

        :Y1_TTO_ANY -

        :Y2_TFROM_ANY -

        :Y3_FROM_10.0.0.0 -

        :Y4_TO_10.0.0.0 -

        -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_IN -f -j ACCEPT
        -A Y_BEGIN_IN -i lo -j ACCEPT

        -A Y_BEGIN_OUT -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_OUT -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_OUT -f -j ACCEPT
        -A Y_BEGIN_OUT -o lo -j ACCEPT
        -A Y_BEGIN_OUT -p udp -m multiport --dports 33434:33529 -j ACCEPT

        -A Y_END_IN -j DROP

        -A Y_END_OUT -j REJECT --reject-with icmp-net-prohibited

        -A Y_FW --destination 10.0.0.0 -j Y_TR_10.0.0.0

        -A Y_FW_orig --destination 10.0.0.0 -j Y_10.0.0.0

        -A Y_FW_OUT --source 10.0.0.0 -j Y_TR_10.0.0.0_OUT

        -A Y_FW_OUT_orig --source 10.0.0.0 -j Y_10.0.0.0_OUT

        -A Y_TR_10.0.0.0_OUT  --proto tcp --sport 48000 --dport 80 -j Y2_TFROM_ANY
        -A Y_TR_10.0.0.0_OUT -j DROP

        -A Y_TR_10.0.0.0  --proto tcp --dport 48000 --sport 80 -j Y1_TTO_ANY
        -A Y_TR_10.0.0.0 -j DROP

        -A Y_10.0.0.0_OUT -j Y_BEGIN_OUT
        -A Y_10.0.0.0_OUT --source 10.0.0.0 -j Y3_FROM_10.0.0.0
        -A Y_10.0.0.0_OUT --source 10.0.0.0 --proto 1 -j ACCEPT
        -A Y_10.0.0.0_OUT -j Y_DRP
        -A Y_10.0.0.0_OUT -j Y_END_OUT_INET
        -A Y_10.0.0.0_OUT -j ACCEPT

        -A Y_10.0.0.0 -j Y_BEGIN_IN
        -A Y_10.0.0.0 --destination 10.0.0.0 -j Y4_TO_10.0.0.0
        -A Y_10.0.0.0 --destination 10.0.0.0 --proto 1 -j ACCEPT
        -A Y_10.0.0.0 -j Y_END_IN

        -A Y1_TTO_ANY --source 93.158.0.0/18 -j Y_FW_orig --proto tcp --dport 48000 --sport 80

        -A Y2_TFROM_ANY --destination 93.158.0.0/18 -j Y_FW_OUT_orig --proto tcp --sport 48000 --dport 80

        -A Y3_FROM_10.0.0.0 --destination 10.0.0.0 -j ACCEPT

        -A Y4_TO_10.0.0.0 --source 10.0.0.0 -j ACCEPT

        COMMIT
        #END IPTABLES
        """
        self._assert_ruleset(expected1, section1, '10.0.0.0', directions=('in', 'out'), force_training=True)

    def test_training_no_out(self):
        fw = hbf.FW()
        section1 = """
        add allow ip from 10.0.0.0 to { 10.0.0.0 or fc00:: }
        ALLOW_STD_ICMP({10.0.0.0 or fc00:: })
        """
        fw.sections[hbf.TRAINING_SECTION_NAME] = hbf.DummySection(
            hbf.TRAINING_SECTION_NAME,
            no_index=True,
            content="""
                add allow tcp from any 48000 to { _YANDEXNETS_ } 80
                """
        )
        expected1 = """
        #BEGIN IP6TABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -

        COMMIT
        #END IP6TABLES
        #BEGIN IPTABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -
        :Y_FW_orig -
        :Y_FW_OUT_orig -

        :Y_BEGIN_IN -
        :Y_END_IN -

        :Y_TR_10.0.0.0_OUT -
        :Y_TR_10.0.0.0 -
        :Y_10.0.0.0 -

        :Y1_TTO_ANY -

        :Y2_TFROM_ANY -

        :Y3_TO_10.0.0.0 -

        -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_IN -f -j ACCEPT
        -A Y_BEGIN_IN -i lo -j ACCEPT

        -A Y_END_IN -j DROP

        -A Y_FW --destination 10.0.0.0 -j Y_TR_10.0.0.0

        -A Y_FW_orig --destination 10.0.0.0 -j Y_10.0.0.0

        -A Y_FW_OUT --source 10.0.0.0 -j Y_TR_10.0.0.0_OUT

        -A Y_FW_OUT_orig -j ACCEPT

        -A Y_TR_10.0.0.0_OUT  --proto tcp --sport 48000 --dport 80 -j Y2_TFROM_ANY
        -A Y_TR_10.0.0.0_OUT -j DROP

        -A Y_TR_10.0.0.0  --proto tcp --dport 48000 --sport 80 -j Y1_TTO_ANY
        -A Y_TR_10.0.0.0 -j DROP

        -A Y_10.0.0.0 -j Y_BEGIN_IN
        -A Y_10.0.0.0 --destination 10.0.0.0 -j Y3_TO_10.0.0.0
        -A Y_10.0.0.0 --destination 10.0.0.0 --proto 1 -j ACCEPT
        -A Y_10.0.0.0 -j Y_END_IN

        -A Y1_TTO_ANY --source 93.158.0.0/18 -j Y_FW_orig --proto tcp --dport 48000 --sport 80

        -A Y2_TFROM_ANY --destination 93.158.0.0/18 -j Y_FW_OUT_orig --proto tcp --sport 48000 --dport 80

        -A Y3_TO_10.0.0.0 --source 10.0.0.0 -j ACCEPT

        COMMIT
        #END IPTABLES
        """
        self._assert_ruleset(expected1, section1, '10.0.0.0', directions=('in',), force_training=True)

    def test_training_symmetry(self):
        """
        Проверяет, что для того, чтобы исключить хост из учений, правило нужно написать только в 1 сторону
        """
        fw = hbf.FW()
        section1 = """
        add allow ip from 10.0.0.0 to { 10.0.0.0 or fc00:: }
        ALLOW_STD_ICMP({10.0.0.0/8 or fc00::/7 })
        """
        fw.sections[hbf.TRAINING_SECTION_NAME] = hbf.DummySection(
            hbf.TRAINING_SECTION_NAME,
            no_index=True,
            content="""
                add allow ip from { testhost } to any
                """
        )
        expected1 = """
        #BEGIN IP6TABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -

        COMMIT
        #END IP6TABLES
        #BEGIN IPTABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -
        :Y_FW_orig -
        :Y_FW_OUT_orig -

        :Y_BEGIN_IN -
        :Y_END_IN -

        :Y_BEGIN_OUT -
        :Y_END_OUT -
        :Y_END_OUT_INET -

        :Y_TR_10.1.1.1_OUT -
        :Y_TR_10.1.1.1 -
        :Y_10.1.1.1_OUT -
        :Y_10.1.1.1 -

        :Y1_TTO_10.1.1.1 -

        :Y2_TFROM_10.1.1.1 -

        :Y3_TTO_ANY -

        :Y4_TFROM_ANY -

        -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_IN -f -j ACCEPT
        -A Y_BEGIN_IN -i lo -j ACCEPT

        -A Y_BEGIN_OUT -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_OUT -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_OUT -f -j ACCEPT
        -A Y_BEGIN_OUT -o lo -j ACCEPT
        -A Y_BEGIN_OUT -p udp -m multiport --dports 33434:33529 -j ACCEPT

        -A Y_END_IN -j DROP

        -A Y_END_OUT -j REJECT --reject-with icmp-net-prohibited

        -A Y_FW --destination 10.1.1.1 -j Y_TR_10.1.1.1

        -A Y_FW_orig --destination 10.1.1.1 -j Y_10.1.1.1

        -A Y_FW_OUT --source 10.1.1.1 -j Y_TR_10.1.1.1_OUT

        -A Y_FW_OUT_orig --source 10.1.1.1 -j Y_10.1.1.1_OUT

        -A Y_TR_10.1.1.1_OUT  -j Y4_TFROM_ANY
        -A Y_TR_10.1.1.1_OUT --source 10.1.1.1 -j Y2_TFROM_10.1.1.1
        -A Y_TR_10.1.1.1_OUT -j DROP

        -A Y_TR_10.1.1.1  -j Y3_TTO_ANY
        -A Y_TR_10.1.1.1 --destination 10.1.1.1 -j Y1_TTO_10.1.1.1
        -A Y_TR_10.1.1.1 -j DROP

        -A Y_10.1.1.1_OUT -j Y_BEGIN_OUT
        -A Y_10.1.1.1_OUT --source 10.1.1.1 --proto 1 -j ACCEPT
        -A Y_10.1.1.1_OUT -j Y_DRP
        -A Y_10.1.1.1_OUT -j Y_END_OUT_INET
        -A Y_10.1.1.1_OUT -j ACCEPT

        -A Y_10.1.1.1 -j Y_BEGIN_IN
        -A Y_10.1.1.1 --destination 10.1.1.1 --proto 1 -j ACCEPT
        -A Y_10.1.1.1 -j Y_END_IN

        -A Y1_TTO_10.1.1.1 -j Y_FW_orig

        -A Y2_TFROM_10.1.1.1 -j Y_FW_OUT_orig

        -A Y3_TTO_ANY --source 10.1.1.1 -j Y_FW_orig

        -A Y4_TFROM_ANY --destination 10.1.1.1 -j Y_FW_OUT_orig

        COMMIT
        #END IPTABLES
        """
        self._assert_ruleset(expected1, section1, '10.1.1.1', directions=('in', 'out'), force_training=True)

    def test_training_mixed(self):
        """
        Проверяет случай, когда на одном IP учения включены, на другом - нет
        """
        fw = hbf.FW()

        self.patch_drills(fw.drills, """[{
            "begin": 1400000000,
            "duration": 600000000,
            "project": "10.101.0.0/24",
            "location": "10.101.0.0/24",
            "exclude": []
        }]""")

        section1 = """
        add allow ip from 10.0.0.0 to { 10.0.0.0 or fc00:: }
        ALLOW_STD_ICMP({10.0.0.0/8 or fc00::/7 })
        """
        fw.sections[hbf.TRAINING_SECTION_NAME] = hbf.DummySection(
            hbf.TRAINING_SECTION_NAME,
            no_index=True,
            content="""
                add allow ip from { testhost } to any
                """
        )
        expected1 = """
        #BEGIN IP6TABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -

        COMMIT
        #END IP6TABLES
        #BEGIN IPTABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -
        :Y_FW_orig -
        :Y_FW_OUT_orig -

        :Y_BEGIN_IN -
        :Y_END_IN -

        :Y_BEGIN_OUT -
        :Y_END_OUT -
        :Y_END_OUT_INET -

        :Y_TR_10.101.0.1_OUT -
        :Y_TR_10.101.0.1 -
        :Y_10.2.0.2_OUT -
        :Y_10.2.0.2 -
        :Y_10.101.0.1_OUT -
        :Y_10.101.0.1 -

        :Y1_TTO_ANY -

        :Y2_TFROM_ANY -

        -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_IN -f -j ACCEPT
        -A Y_BEGIN_IN -i lo -j ACCEPT

        -A Y_BEGIN_OUT -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_OUT -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_OUT -f -j ACCEPT
        -A Y_BEGIN_OUT -o lo -j ACCEPT
        -A Y_BEGIN_OUT -p udp -m multiport --dports 33434:33529 -j ACCEPT

        -A Y_END_IN -j DROP

        -A Y_END_OUT -j REJECT --reject-with icmp-net-prohibited

        -A Y_FW --destination 10.2.0.2 -j Y_10.2.0.2
        -A Y_FW --destination 10.101.0.1 -j Y_TR_10.101.0.1

        -A Y_FW_orig --destination 10.101.0.1 -j Y_10.101.0.1

        -A Y_FW_OUT --source 10.2.0.2 -j Y_10.2.0.2_OUT
        -A Y_FW_OUT --source 10.101.0.1 -j Y_TR_10.101.0.1_OUT

        -A Y_FW_OUT_orig --source 10.101.0.1 -j Y_10.101.0.1_OUT

        -A Y_TR_10.101.0.1_OUT  -j Y2_TFROM_ANY
        -A Y_TR_10.101.0.1_OUT -j DROP

        -A Y_TR_10.101.0.1  -j Y1_TTO_ANY
        -A Y_TR_10.101.0.1 -j DROP

        -A Y_10.2.0.2_OUT -j Y_BEGIN_OUT
        -A Y_10.2.0.2_OUT --source 10.2.0.2 --proto 1 -j ACCEPT
        -A Y_10.2.0.2_OUT -j Y_DRP
        -A Y_10.2.0.2_OUT -j Y_END_OUT_INET
        -A Y_10.2.0.2_OUT -j ACCEPT

        -A Y_10.2.0.2 -j Y_BEGIN_IN
        -A Y_10.2.0.2 --destination 10.2.0.2 --proto 1 -j ACCEPT
        -A Y_10.2.0.2 -j Y_END_IN

        -A Y_10.101.0.1_OUT -j Y_BEGIN_OUT
        -A Y_10.101.0.1_OUT --source 10.101.0.1 --proto 1 -j ACCEPT
        -A Y_10.101.0.1_OUT -j Y_DRP
        -A Y_10.101.0.1_OUT -j Y_END_OUT_INET
        -A Y_10.101.0.1_OUT -j ACCEPT

        -A Y_10.101.0.1 -j Y_BEGIN_IN
        -A Y_10.101.0.1 --destination 10.101.0.1 --proto 1 -j ACCEPT
        -A Y_10.101.0.1 -j Y_END_IN

        -A Y1_TTO_ANY --source 10.1.1.1 -j Y_FW_orig

        -A Y2_TFROM_ANY --destination 10.1.1.1 -j Y_FW_OUT_orig

        COMMIT
        #END IPTABLES

        """
        self._assert_ruleset(expected1, section1, '10.101.0.1,10.2.0.2', directions=('in', 'out'))

    def test_training_close_from(self):
        fw = hbf.FW()
        section1 = """
        add allow ip from {10.0.0.0 or 10.0.0.1} to { 10.0.0.0 or fc00:: }
        ALLOW_STD_ICMP({10.0.0.0 or fc00:: })
        """

        self.patch_drills(fw.drills, """[{
            "begin": 1400000000,
            "duration": 600000000,
            "project": "10.0.0.0/32",
            "location": "10.0.0.0/24",
            "exclude": [],
            "close_from": ["10.0.0.1"]
        }]""")

        expected1 = """
        #BEGIN IP6TABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -

        COMMIT
        #END IP6TABLES
        #BEGIN IPTABLES
        *filter
        :Y_FW -
        :Y_FW_OUT -
        :Y_FW_orig -
        :Y_FW_OUT_orig -

        :Y_BEGIN_IN -
        :Y_END_IN -

        :Y_BEGIN_OUT -
        :Y_END_OUT -
        :Y_END_OUT_INET -

        :Y_TR_10.0.0.0_OUT -
        :Y_TR_10.0.0.0 -
        :Y_10.0.0.0_OUT -
        :Y_10.0.0.0 -

        :Y1_FROM_10.0.0.0/31 -

        :Y2_TFROM_10.0.0.0 -

        :Y3_TO_10.0.0.0 -

        :Y4_TTO_10.0.0.0 -

        -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_IN -f -j ACCEPT
        -A Y_BEGIN_IN -i lo -j ACCEPT

        -A Y_BEGIN_OUT -p tcp ! --syn -j ACCEPT
        -A Y_BEGIN_OUT -m state --state RELATED,ESTABLISHED -j ACCEPT
        -A Y_BEGIN_OUT -f -j ACCEPT
        -A Y_BEGIN_OUT -o lo -j ACCEPT
        -A Y_BEGIN_OUT -p udp -m multiport --dports 33434:33529 -j ACCEPT

        -A Y_END_IN -j DROP

        -A Y_END_OUT -j REJECT --reject-with icmp-net-prohibited

        -A Y_FW --destination 10.0.0.0 -j Y_TR_10.0.0.0

        -A Y_FW_orig --destination 10.0.0.0 -j Y_10.0.0.0

        -A Y_FW_OUT --source 10.0.0.0 -j Y_TR_10.0.0.0_OUT

        -A Y_FW_OUT_orig --source 10.0.0.0 -j Y_10.0.0.0_OUT

        -A Y_TR_10.0.0.0_OUT --source 10.0.0.0 -j Y2_TFROM_10.0.0.0
        -A Y_TR_10.0.0.0_OUT -j Y_FW_OUT_orig

        -A Y_TR_10.0.0.0 --destination 10.0.0.0 -j Y4_TTO_10.0.0.0
        -A Y_TR_10.0.0.0 -j Y_FW_orig

        -A Y_10.0.0.0_OUT -j Y_BEGIN_OUT
        -A Y_10.0.0.0_OUT --source 10.0.0.0/31 -j Y1_FROM_10.0.0.0/31
        -A Y_10.0.0.0_OUT --source 10.0.0.0 --proto 1 -j ACCEPT
        -A Y_10.0.0.0_OUT -j Y_DRP
        -A Y_10.0.0.0_OUT -j Y_END_OUT_INET
        -A Y_10.0.0.0_OUT -j ACCEPT

        -A Y_10.0.0.0 -j Y_BEGIN_IN
        -A Y_10.0.0.0 --destination 10.0.0.0 -j Y3_TO_10.0.0.0
        -A Y_10.0.0.0 --destination 10.0.0.0 --proto 1 -j ACCEPT
        -A Y_10.0.0.0 -j Y_END_IN

        -A Y1_FROM_10.0.0.0/31 --destination 10.0.0.0 -j ACCEPT

        -A Y2_TFROM_10.0.0.0 --destination 10.0.0.1 -j DROP

        -A Y3_TO_10.0.0.0 --source 10.0.0.0/31 -j ACCEPT

        -A Y4_TTO_10.0.0.0 --source 10.0.0.1 -j DROP

        COMMIT
        #END IPTABLES
        """
        self._assert_ruleset(expected1, section1, '10.0.0.0', directions=('in', 'out'))

    def test_drp_chain(self):
        fw = hbf.FW()
        fw.sections['DROP_TO_YANDEX'] = hbf.DummySection(
            'DROP_TO_YANDEX',
            rs_key=hbf.RulesetKey(root_name='Y_DRP', sort_prio=999),
            no_index=True,
            allow_deny=True,
            content="""
                add deny ip from any to { _YANDEXNETS_ }
                """
        )

        section1 = """
        add allow ip from 10.0.0.0 to { 10.0.0.0 or fc00:: }
        ALLOW_STD_ICMP({10.0.0.0 or fc00:: })
        """
        expected1 = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y_BEGIN_OUT -
            :Y_END_OUT -
            :Y_END_OUT_INET -

            :Y_10.0.0.0_OUT -

            :Y1_FROM_10.0.0.0 -

            :Y_DRP -

            -A Y_BEGIN_OUT -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_OUT -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_OUT -f -j ACCEPT
            -A Y_BEGIN_OUT -o lo -j ACCEPT
            -A Y_BEGIN_OUT -p udp -m multiport --dports 33434:33529 -j ACCEPT

            -A Y_END_OUT -j REJECT --reject-with icmp-net-prohibited

            -A Y_FW_OUT --source 10.0.0.0 -j Y_10.0.0.0_OUT

            -A Y_10.0.0.0_OUT -j Y_BEGIN_OUT
            -A Y_10.0.0.0_OUT --source 10.0.0.0 -j Y1_FROM_10.0.0.0
            -A Y_10.0.0.0_OUT --source 10.0.0.0 --proto 1 -j ACCEPT
            -A Y_10.0.0.0_OUT -j Y_DRP
            -A Y_10.0.0.0_OUT -j Y_END_OUT_INET
            -A Y_10.0.0.0_OUT -j ACCEPT

            -A Y1_FROM_10.0.0.0 --destination 10.0.0.0 -j ACCEPT

            -A Y_DRP --destination 93.158.0.0/18 -j Y_END_OUT

            COMMIT
            #END IPTABLES
            """
        self._assert_ruleset(expected1, section1, '10.0.0.0', directions=('out',))

    def test_macro_arg(self):
        section = """
            add allow ip from any to any
        """

        expected = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y__TARGET1_ -

            :Y1_TO_ANY -

            :Y_FW_ya:c00::/40 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_END_IN -j DROP

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"
            -A Y_FW --destination 2a02:6b8:c00::/40 -g Y_FW_ya:c00::/40

            -A Y_FW_ya:c00::/40 -m u32 --u32 "32 & 0xffffff00 = 0x400" -j Y__TARGET1_

            -A Y__TARGET1_ -j Y_BEGIN_IN
            -A Y__TARGET1_  -j Y1_TO_ANY
            -A Y__TARGET1_ --destination 2a02:6b8:c00::/40 -m u32 --u32 "32 & 0xffffff00 = 0x400" --proto 58 -j ACCEPT
            -A Y__TARGET1_ -j Y_END_IN

            -A Y1_TO_ANY -j ACCEPT

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"

            COMMIT
            #END IPTABLES

        """

        self._assert_ruleset(expected, section, '_TARGET1_', directions=('in',))

    def test_gre_proto(self):
        section = """
            add allow ip from any to any proto gre
        """

        expected = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -

            :Y__TARGET1_ -

            :Y1_TO_ANY -

            :Y_FW_ya:c00::/40 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_END_IN -j DROP

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"
            -A Y_FW --destination 2a02:6b8:c00::/40 -g Y_FW_ya:c00::/40

            -A Y_FW_ya:c00::/40 -m u32 --u32 "32 & 0xffffff00 = 0x400" -j Y__TARGET1_

            -A Y__TARGET1_ -j Y_BEGIN_IN
            -A Y__TARGET1_  --proto 47 -j Y1_TO_ANY
            -A Y__TARGET1_ --destination 2a02:6b8:c00::/40 -m u32 --u32 "32 & 0xffffff00 = 0x400" --proto 58 -j ACCEPT
            -A Y__TARGET1_ -j Y_END_IN

            -A Y1_TO_ANY -j ACCEPT --proto 47

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            -A Y_FW -p tcp -m tcpmss --mss 1:56 -j DROP -m comment --comment "security fix, HBF-47"

            COMMIT
            #END IPTABLES

        """

        self._assert_ruleset(expected, section, '_TARGET1_', directions=('in',))

    def test_pre_end(self):
        section = """
            add allow ip from 10.0.0.0 to { 10.0.0.0 or fc00:: }
            add allow tcp from 1234@2a02:6b8:c00::/40 to any 22
            ALLOW_STD_ICMP({10.0.0.0/8 or ::/0})
        """

        expected = """
            #BEGIN IP6TABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -
            :Y_END_IN_PRE -

            :Y_BEGIN_OUT -
            :Y_END_OUT -
            :Y_END_OUT_INET -
            :Y_END_OUT_PRE -

            :Y_1234@ya:c00::/40_OUT -
            :Y_1234@ya:c00::/40 -
            :Y__TARGET1__OUT -
            :Y__TARGET1_ -

            :Y1_FROM_1234@ya:c00::/40 -
            :Y1_ya:c00::/40 -

            :Y2_TO_ANY -
            :Y2_ya:c00::/40 -

            :Y3_TO_1234@ya:c00::/40 -
            :Y3_ya:c00::/40 -

            :Y_FW_ya:c00::/40 -

            :Y_FW_OUT_ya:c00::/40 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_BEGIN_OUT -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_OUT -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_OUT -o lo -j ACCEPT
            -A Y_BEGIN_OUT -p udp -m multiport --dports 33434:33529 -j ACCEPT

            -A Y_END_IN -j Y_END_IN_PRE
            -A Y_END_IN -j DROP

            -A Y_END_OUT -j Y_END_OUT_PRE
            -A Y_END_OUT -j REJECT --reject-with icmp6-adm-prohibited

            -A Y_END_IN_PRE --destination 2a02:6b8:c00::/40 -m u32 --u32 "32 & 0xffffffff = 0x1234" -m comment --comment "1234@2a02:6b8:c00::/40" -j RETURN
            -A Y_END_IN_PRE --destination 2a02:6b8:c00::/40 -m u32 --u32 "32 & 0xffffff00 = 0x400" -m comment --comment "_TARGET1_" -j RETURN

            -A Y_END_OUT_PRE --source 2a02:6b8:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x1234" -m comment --comment "1234@2a02:6b8:c00::/40" -j RETURN
            -A Y_END_OUT_PRE --source 2a02:6b8:c00::/40 -m u32 --u32 "16 & 0xffffff00 = 0x400" -m comment --comment "_TARGET1_" -j RETURN

            -A Y_FW --destination 2a02:6b8:c00::/40 -g Y_FW_ya:c00::/40

            -A Y_FW_ya:c00::/40 -m u32 --u32 "32 & 0xffffff00 = 0x400" -j Y__TARGET1_
            -A Y_FW_ya:c00::/40 -m u32 --u32 "32 & 0xffffffff = 0x1234" -j Y_1234@ya:c00::/40

            -A Y_FW_OUT --source 2a02:6b8:c00::/40 -g Y_FW_OUT_ya:c00::/40

            -A Y_FW_OUT_ya:c00::/40 -m u32 --u32 "16 & 0xffffff00 = 0x400" -j Y__TARGET1__OUT
            -A Y_FW_OUT_ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x1234" -j Y_1234@ya:c00::/40_OUT

            -A Y_1234@ya:c00::/40_OUT -j Y_BEGIN_OUT
            -A Y_1234@ya:c00::/40_OUT --source 2a02:6b8:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x1234" -j Y1_FROM_1234@ya:c00::/40
            -A Y_1234@ya:c00::/40_OUT --source 2a02:6b8:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x1234" --proto 58 -j ACCEPT
            -A Y_1234@ya:c00::/40_OUT -j Y_DRP
            -A Y_1234@ya:c00::/40_OUT -j Y_END_OUT_INET
            -A Y_1234@ya:c00::/40_OUT -j ACCEPT

            -A Y_1234@ya:c00::/40 -j Y_BEGIN_IN
            -A Y_1234@ya:c00::/40  --proto tcp --dport 22 -j Y2_TO_ANY
            -A Y_1234@ya:c00::/40 --destination 2a02:6b8:c00::/40 -m u32 --u32 "32 & 0xffffffff = 0x1234" -j Y3_TO_1234@ya:c00::/40
            -A Y_1234@ya:c00::/40 --destination 2a02:6b8:c00::/40 -m u32 --u32 "32 & 0xffffffff = 0x1234" --proto 58 -j ACCEPT
            -A Y_1234@ya:c00::/40 -j Y_END_IN

            -A Y__TARGET1__OUT -j Y_BEGIN_OUT
            -A Y__TARGET1__OUT --source 2a02:6b8:c00::/40 -m u32 --u32 "16 & 0xffffff00 = 0x400" --proto 58 -j ACCEPT
            -A Y__TARGET1__OUT -j Y_DRP
            -A Y__TARGET1__OUT -j Y_END_OUT_INET
            -A Y__TARGET1__OUT -j ACCEPT

            -A Y__TARGET1_ -j Y_BEGIN_IN
            -A Y__TARGET1_  --proto tcp --dport 22 -j Y2_TO_ANY
            -A Y__TARGET1_ --destination 2a02:6b8:c00::/40 -m u32 --u32 "32 & 0xffffff00 = 0x400" --proto 58 -j ACCEPT
            -A Y__TARGET1_ -j Y_END_IN

            -A Y1_FROM_1234@ya:c00::/40 -j ACCEPT --proto tcp --dport 22 -m comment --comment "testsection:2"
            -A Y1_FROM_1234@ya:c00::/40 --destination 2a02:6b8:c00::/40 -g Y1_ya:c00::/40

            -A Y1_ya:c00::/40 -m u32 --u32 "32 & 0xffffffff = 0x1234" -j ACCEPT -m comment --comment "project-id interconnect auto rule DUMMY_AUTO_IC:0"

            -A Y2_TO_ANY --source 2a02:6b8:c00::/40 -g Y2_ya:c00::/40

            -A Y2_ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x1234" -j ACCEPT --proto tcp --dport 22 -m comment --comment "testsection:2"

            -A Y3_TO_1234@ya:c00::/40 --source 2a02:6b8:c00::/40 -g Y3_ya:c00::/40

            -A Y3_ya:c00::/40 -m u32 --u32 "16 & 0xffffffff = 0x1234" -j ACCEPT -m comment --comment "project-id interconnect auto rule DUMMY_AUTO_IC:0"

            COMMIT
            #END IP6TABLES
            #BEGIN IPTABLES
            *filter
            :Y_FW -
            :Y_FW_OUT -

            :Y_BEGIN_IN -
            :Y_END_IN -
            :Y_END_IN_PRE -

            :Y_BEGIN_OUT -
            :Y_END_OUT -
            :Y_END_OUT_INET -
            :Y_END_OUT_PRE -

            :Y_10.0.0.0_OUT -
            :Y_10.0.0.0 -

            :Y1_FROM_10.0.0.0 -

            :Y2_TO_10.0.0.0/8 -

            :Y3_TO_10.0.0.0 -

            -A Y_BEGIN_IN -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_IN -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_IN -f -j ACCEPT
            -A Y_BEGIN_IN -i lo -j ACCEPT

            -A Y_BEGIN_OUT -p tcp ! --syn -j ACCEPT
            -A Y_BEGIN_OUT -m state --state RELATED,ESTABLISHED -j ACCEPT
            -A Y_BEGIN_OUT -f -j ACCEPT
            -A Y_BEGIN_OUT -o lo -j ACCEPT
            -A Y_BEGIN_OUT -p udp -m multiport --dports 33434:33529 -j ACCEPT

            -A Y_END_IN -j Y_END_IN_PRE
            -A Y_END_IN -j DROP

            -A Y_END_OUT -j Y_END_OUT_PRE
            -A Y_END_OUT -j REJECT --reject-with icmp-net-prohibited

            -A Y_END_IN_PRE --destination 10.0.0.0 -m comment --comment "10.0.0.0" -j RETURN

            -A Y_END_OUT_PRE --source 10.0.0.0 -m comment --comment "10.0.0.0" -j RETURN

            -A Y_FW --destination 10.0.0.0 -j Y_10.0.0.0

            -A Y_FW_OUT --source 10.0.0.0 -j Y_10.0.0.0_OUT

            -A Y_10.0.0.0_OUT -j Y_BEGIN_OUT
            -A Y_10.0.0.0_OUT --source 10.0.0.0 -j Y1_FROM_10.0.0.0
            -A Y_10.0.0.0_OUT --source 10.0.0.0 --proto 1 -j ACCEPT
            -A Y_10.0.0.0_OUT -j Y_DRP
            -A Y_10.0.0.0_OUT -j Y_END_OUT_INET
            -A Y_10.0.0.0_OUT -j ACCEPT

            -A Y_10.0.0.0 -j Y_BEGIN_IN
            -A Y_10.0.0.0 --destination 10.0.0.0/8 --proto tcp --dport 22 -j Y2_TO_10.0.0.0/8
            -A Y_10.0.0.0 --destination 10.0.0.0 -j Y3_TO_10.0.0.0
            -A Y_10.0.0.0 --destination 10.0.0.0 --proto 1 -j ACCEPT
            -A Y_10.0.0.0 -j Y_END_IN

            -A Y1_FROM_10.0.0.0 --destination 10.0.0.0 -j ACCEPT -m comment --comment "testsection:1"

            -A Y3_TO_10.0.0.0 --source 10.0.0.0 -j ACCEPT -m comment --comment "testsection:1"

            COMMIT
            #END IPTABLES

        """

        self._assert_ruleset(
            expected,
            section,
            "_TARGET1_,10.0.0.0,1234@2a02:6b8:c00::/40",
            directions=("in", "out"),
            include_pre_end=True,
            debug=True,
        )


class TestExpandMacro(BaseTest):
    MACROSES = {
        "_EMPTY_": [],
        "_TEST1_": [
            "604@2a02:6b8:c00::/40"
        ],
        "_C_SRV_": [
            "host1.yandex.net",
            "host2.yandex.net",
        ],
        "_TEST_NETS_": [
            "10.0.0.0/8",
            "192.168.0.1",
            "fdef:abcd::/64",
            "fdef:abce::/64",
            "999@2a02:6b8:c00::/40",
            "666@2a02:6b8:c00::/40",
        ]
    }

    def _macro_request(self, macro_name, **kwargs):
        request = unittest.mock.MagicMock()
        request.GET = kwargs
        request.match_info = {'name': macro_name}

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(hbf.expand_macro_handler(request))
        self.assertEqual(200, response.status)
        return response.body.decode()

    def test_exists(self):
        self.assertIsInstance(self._macro_request('_TEST1_'), str)
        self.assertRaises(HTTPBadRequest, lambda: self._macro_request('_NOT_EXISTS_'))

    def test_params(self):
        for (param, values) in {
            'format': ['text', 'json'],
            'trypo_format': ['trypo', 'dottedquad', 'none'],
        }.items():
            for val in values:
                self.assertIsInstance(self._macro_request('_TEST1_', **{param: val}), str)
            self.assertRaises(HTTPBadRequest, lambda: self._macro_request('_TEST1_', **{param: 'blabla'}))

        # test default params (format=json, trypo_format=trypo)
        self.assertCountEqual(self.MACROSES['_TEST1_'],
                              json.loads(self._macro_request('_TEST1_')))

    def test_json_parse(self):
        for mname, items in self.MACROSES.items():
            data = json.loads(self._macro_request(mname, format='json'))
            self.assertCountEqual(data, items)

    def test_render_formats(self):
        self.assertEqual(
            "10.0.0.0/8\n"
            "192.168.0.1\n"
            "666@2a02:6b8:c00::/40\n"
            "999@2a02:6b8:c00::/40\n"
            "fdef:abcd::/64\n"
            "fdef:abce::/64\n"
            , self._macro_request('_TEST_NETS_', format='text', trypo_format='trypo')
        )

        self.assertEqual(
            "10.0.0.0/255.0.0.0\n"
            "192.168.0.1/255.255.255.255\n"
            "2a02:6b8:c00::666:0:0/ffff:ffff:ff00:0:ffff:ffff::\n"
            "2a02:6b8:c00::999:0:0/ffff:ffff:ff00:0:ffff:ffff::\n"
            "fdef:abcd::/ffff:ffff:ffff:ffff::\n"
            "fdef:abce::/ffff:ffff:ffff:ffff::\n"
            , self._macro_request('_TEST_NETS_', format='text', trypo_format='dottedquad')
        )

        self.assertEqual(
            "10.0.0.0/8\n"
            "192.168.0.1\n"
            "2a02:6b8:c00::/40\n"
            "fdef:abcd::/64\n"
            "fdef:abce::/64\n"
            , self._macro_request('_TEST_NETS_', format='text', trypo_format='none')
        )


if __name__ == "__main__":
    unittest.main()
