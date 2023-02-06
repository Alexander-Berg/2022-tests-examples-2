import unittest.mock

import hbf.code as hbf

from textwrap import dedent

from . import BaseTest
from hbf.ipaddress2 import ip_network, ip_address


class TestRuleLookup(BaseTest):
    HOSTS = {
        "test2.yndx.net": ["10.0.0.1"],
        "test3.yndx.net": ["10.0.0.2"],
        "test4.yndx.net": ["10.0.0.4"],
        "test5.yndx.net": ["10.0.0.5"],
    }

    MACROSES = {
        "_EMPTY_MACRO_": [],
        "_TEST_": [
            "10.0.0.1",
        ],
        "_TRYPO_TEST_": [
            "25c@2a02:6b8:c00::/40",
        ],
    }

    def test_prepare_ip_lookup(self):
        pairs = {
            # lookup key: expected radix lookup sequence
            '::1': ['::1'],
            '2a02:6b8:c10::10:2:3': ['2a02:6b8:c10::10:2:3', '2a02:6b8:c00::10:0:0'],
            '2a02:6b8:c00:1234:10::': ['2a02:6b8:c00:1234:10::', '2a02:6b8:c00:0:10::'],
            'ee@2a02:6b8:c00::/40': ['2a02:6b8:c00::ee:0:0/96'],
            '2a02:6b8:c01:102:0:671:0:12': ['2a02:6b8:c01:102:0:671:0:12', '2a02:6b8:c00::671:0:0'],
            '670/31@2a02:6b8:c00::/40': ['2a02:6b8:c00::670:0:0/95'],
            '2a02:6b8:c23:4:5:6:f000:0/100': ['2a02:6b8:c23:4:5:6:f000:0/100', '2a02:6b8:c00:0:5:6:0:0/100'],
            '4d2@2a02:6b8:c00:abcd::/64': ['2a02:6b8:c00:abcd:0:4d2::/96', '2a02:6b8:c00:0:0:4d2::/96'],
        }
        for (key, expected) in pairs.items():
            self.assertEqual([ip_network(e) for e in expected],
                             hbf.RadixTrypo._prepare_ip_lookup(ip_network(key)))

    # не запускаем update_macroses и update_sections
    @unittest.mock.patch('hbf.code.FW.update_macroses', return_value=None)
    @unittest.mock.patch('hbf.code.FW.update_sections', return_value=None)
    def test_get_rules_for(self, *_):
        actual_rule = "add allow tcp from { _TEST_ } to test2.yndx.net 80"
        section_content = """
        %s
        add allow tcp from { _TEST_ } to test3.yndx.net 80
        add allow tcp from { _EMPTY_MACRO_ } to test4.yndx.net 80
        add allow tcp from { _EMPTY_MACRO_ } to test5.yndx.net 82
        add allow tcp from 10.1.0.0/24 to test5.yndx.net 83

        # правила, которые должны игнорироваться
        add allow ip from any to any in
        add allow ip from any to any in keep-state
        add allow ip from any to any keep-state in
        add allow ip from any to any established
        add allow tcp from any smtp to { _TEST_ } 1024-65535 established
        add allow tcp from any to { _TEST_ } out via vlan999 established
        ALLOW_STD_ICMP(0.0.0.0/0)
        """ % actual_rule
        section_content = dedent(section_content.strip("\n"))

        actual_parsed_rules = hbf.Rule(actual_rule)

        fw = hbf.FW()
        fw.sections = {"testsection": hbf.Section("testsection", section_content)}
        ip_bin = ip_address(hbf.resolve("test2.yndx.net")[0])
        test2_rules = fw.get_rules_for(ip_bin)
        self.assertEqual({ip_bin: [actual_parsed_rules]}, hbf.Ruleset.as_dict(test2_rules))

        # проверим дырки до test5.yndx.net
        ip_bin = ip_address(hbf.resolve("test5.yndx.net")[0])
        test5_rules = hbf.Ruleset.as_dict(fw.get_rules_for(ip_bin))

        # должно быть 2 правила
        self.assertEqual(1, len(test5_rules))
        self.assertIn(ip_bin, test5_rules)
        self.assertEqual(2, len(test5_rules[ip_bin]))

    # не запускаем update_macroses и update_sections
    @unittest.mock.patch('hbf.code.FW.update_macroses', return_value=None)
    @unittest.mock.patch('hbf.code.FW.update_sections', return_value=None)
    def test_get_rules_by_trypo(self, *_):
        fw = hbf.FW()

        rules = "\n".join([
            "add allow tcp from 1::1:%s to 2a02:6b8:c00:0:10:: 80" % x for x in range(130)
        ])
        section_content = """
            # trypo в dst макросе
            add allow tcp from 1::1 to _TRYPO_TEST_ 80
            # trypo dst. project 1234 = 0x4d2
            add allow tcp from 1::1 to 4d2@2a02:6b8:c00::/40 80
            # ищем trypo network в большей сети
            add allow tcp from 1::1 to 2a00::/8 80
            # ищем правила в конкретной geo-сети
            add allow tcp from 1::1 to 2a02:6b8:c00:abcd::/64 80
            add allow tcp from 1::1 to 12@2a02:6b8:c00:abcd::/64 80
            add allow tcp from 1::1 to 4d2@2a02:6b8:c00:eeee::/64 80
            add allow tcp from 1::1 to 4d2@2a02:6b8:c00:abcd::/64 80

            # куча правила
            ALLOW_STD_ICMP({ ::/0 or 4d2@2a02:6b8:c00::/40 })
            %s
        """ % rules
        section_content = dedent(section_content.strip("\n"))
        fw.sections = {"testsection": hbf.Section("testsection", section_content)}

        ip_bin = ip_network("2a02:06b8:0c00::025c:0:1")  # geo=0, project=604
        self.assertEqual(
            {
                ip_network("25c@2a02:6b8:c00::/40"): [
                    hbf.Rule('add allow ip from 25c@2a02:6b8:c00::/40 to 25c@2a02:6b8:c00::/40'),
                    hbf.Rule('add allow tcp from 1::1 to _TRYPO_TEST_ 80'),
                ],
                ip_network('2a00::/8'): [
                    hbf.Rule('add allow tcp from 1::1 to 2a00::/8 80'),
                ],
            },
            hbf.Ruleset.as_dict(fw.get_rules_for(ip_bin))
        )

        ip_bin = ip_address("2a02:6b8:c00:abcd:0:04d2:0:1")  # geo=abcd, project=1234
        self.assertEqual(
            {
                ip_network("4d2@2a02:6b8:c00::/40"): [
                    hbf.Rule('add allow ip from 4d2@2a02:6b8:c00::/40 to 4d2@2a02:6b8:c00::/40'),
                    hbf.Rule('add allow tcp from 1::1 to 4d2@2a02:6b8:c00::/40 80'),
                ],
                ip_network('4d2@2a02:6b8:c00:abcd::/64'): [
                    hbf.Rule('add allow tcp from 1::1 to 4d2@2a02:6b8:c00:abcd::/64 80'),
                ],
                ip_network('2a02:6b8:c00:abcd::/64'): [
                    hbf.Rule('add allow tcp from 1::1 to 2a02:6b8:c00:abcd::/64 80'),
                ],
                ip_network('2a00::/8'): [
                    hbf.Rule('add allow tcp from 1::1 to 2a00::/8 80'),
                ],
            },
            hbf.Ruleset.as_dict(fw.get_rules_for(ip_bin))
        )

        ip_bin = ip_network("12@2a02:6b8:c00::/40")  # cidr, geo=0, project=12
        self.assertEqual(
            {
                ip_network("12@2a02:6b8:c00::/40"): [
                    hbf.Rule('add allow ip from 12@2a02:6b8:c00::/40 to 12@2a02:6b8:c00::/40'),
                ],
                ip_network('2a00::/8'): [
                    hbf.Rule('add allow tcp from 1::1 to 2a00::/8 80'),
                ],
            },
            hbf.Ruleset.as_dict(fw.get_rules_for(ip_bin))
        )

        ip_bin = ip_network("4d2@2a02:6b8:c00:abcd::/64")  # cidr, geo=abcd, project=1234
        self.assertEqual(
            {
                ip_network("4d2@2a02:6b8:c00::/40"): [
                    hbf.Rule('add allow ip from 4d2@2a02:6b8:c00::/40 to 4d2@2a02:6b8:c00::/40'),
                    hbf.Rule('add allow tcp from 1::1 to 4d2@2a02:6b8:c00::/40 80'),
                ],
                ip_network('4d2@2a02:6b8:c00:abcd::/64'): [
                    hbf.Rule('add allow tcp from 1::1 to 4d2@2a02:6b8:c00:abcd::/64 80'),
                ],
                ip_network('2a02:6b8:c00:abcd::/64'): [
                    hbf.Rule('add allow tcp from 1::1 to 2a02:6b8:c00:abcd::/64 80'),
                ],
                ip_network('2a00::/8'): [
                    hbf.Rule('add allow tcp from 1::1 to 2a00::/8 80'),
                ],
            },
            hbf.Ruleset.as_dict(fw.get_rules_for(ip_bin))
        )

        ip_bin = ip_network("25c@2a02:6b8:c00::/40")  # cidr, geo=0, project=604
        self.assertEqual(
            {
                ip_network("25c@2a02:6b8:c00::/40"): [
                    hbf.Rule('add allow ip from 25c@2a02:6b8:c00::/40 to 25c@2a02:6b8:c00::/40'),
                    hbf.Rule('add allow tcp from 1::1 to _TRYPO_TEST_ 80'),
                ],
                ip_network('2a00::/8'): [
                    hbf.Rule('add allow tcp from 1::1 to 2a00::/8 80'),
                ],
            },
            hbf.Ruleset.as_dict(fw.get_rules_for(ip_bin)),
        )

        # если правил много
        rules = fw.get_rules_for(ip_address("2a02:6b8:c00:0:10::"))
        self.assertEqual(132, sum((len(r) for r in rules)))

    @unittest.mock.patch('hbf.code.FW.update_macroses', return_value=None)
    @unittest.mock.patch('hbf.code.FW.update_sections', return_value=None)
    def test_trypo_interconnect(self, *_):
        # Проверить автоматически вставляемое interconnect правило внутри секции

        fw = hbf.FW()
        section_content = """
        add allow ip from :: to _TRYPO_TEST_
        ALLOW_STD_ICMP({ _TRYPO_TEST_ })
        """
        fw.sections = {"testsection": hbf.Section("testsection", section_content)}

        ip_bin = ip_address("2a02:06b8:0c00::025c:0:1")
        self.assertEqual(
            {
                ip_network("25c@2a02:6b8:c00::/40"): [
                    hbf.Rule('add allow ip from 25c@2a02:6b8:c00::/40 to 25c@2a02:6b8:c00::/40'),
                    hbf.Rule('add allow ip from :: to 25c@2a02:6b8:c00::/40'),
                ],
            },
            hbf.Ruleset.as_dict(fw.get_rules_for(ip_bin))
        )
