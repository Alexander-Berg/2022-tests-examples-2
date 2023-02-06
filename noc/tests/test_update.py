import unittest.mock
from textwrap import dedent

from . import BaseTest
import hbf.code as hbf
from hbf.ipaddress2 import ip_network

"""
Тесты корректности обновлений частей фаерволла
"""


class TestUpdates(BaseTest):
    HOSTS = {
        "testhost": ["10.1.1.1"],
         "test.yndx.net": ["10.0.0.10"],
         "test2.yndx.net": ["10.0.0.1"],
         "test3.yndx.net": ["10.0.0.2"],
    }

    MACROSES = {
        "_TEST1_": [
            "10.0.0.0/24",
            "10.1.1.1",
            "test2.yndx.net",
        ],
        "_TEST2_": [
            "10.0.0.0/24",
            "10.2.2.2",
            "test3.yndx.net",
        ],
        "_TESTMACROS_": [
            "2a02:6b8:a::/64",
            "2a02:6b8:b::/64",
        ],
    }

    @unittest.mock.patch('hbf.code.Hosts.update', return_value=True)
    def test_update_section(self, _):
        s_text = """
            add allow ip from { _TEST1_ } to { testhost }
            add allow ip from { _TEST1_ } to { test2.yndx.net or testhost }
            add allow ip from { _TEST1_ or _TEST2_ } to { test2.yndx.net or testhost }
            add allow ip from { _TEST1_ or _TEST2_ } to { test3.yndx.net }
            ALLOW_STD_ICMP(0.0.0.0/0)
        """
        sect = hbf.Section('TEST', s_text)

        self.assertEqual(4, sect.update_rules(macroses=['_TEST1_']))
        self.assertEqual(2, sect.update_rules(macroses=['_TEST2_']))  # 3,4
        self.assertEqual(4, sect.update_rules(macroses=['_TEST1_', '_TEST2_']))

        self.assertEqual(3, sect.update_rules(fqdns=['testhost']))  # 1-3
        self.assertEqual(4, sect.update_rules(fqdns=['test2.yndx.net']))
        self.assertEqual(2, sect.update_rules(fqdns=['test3.yndx.net']))  # 3,4

        self.assertEqual(0, sect.update_rules(fqdns=['test.yndx.net']))
        self.assertEqual(4, sect.update_rules(macroses=['_TEST1_', '_TEST2_'], fqdns=['test2.yndx.net', 'test3.yndx.net']))

    def test_scope_in_dummy(self):
        # проверка корректности применения scope секции до и после апдейта макроса
        # scope не должен применяться для dummy секций
        dummy_section = """
        add allow udp from any to { ::1 or _TESTMACROS_ }
        """
        section_content = """
        add allow tcp from ::1 to ::2
        ALLOW_STD_ICMP({ ::/0 })
        """
        dummy_section = dedent(dummy_section.strip("\n"))
        section_content = dedent(section_content.strip("\n"))

        fw = hbf.FW()
        fw.sections = {"dummy": hbf.DummySection("dummy", dummy_section),
                       "test": hbf.Section("test", section_content)}

        targets, errors = hbf.make_targets(["::1"])
        ip = list(targets.keys())[0]
        ruleset = fw.get_rules_for(ip, direction='out')
        ruleset = hbf.Ruleset.as_dict(ruleset)

        # тут должно быть 2 правило. из своей секции и из dummy
        self.assertEqual(2, len(ruleset))
        # проверим dst часть правила из dummy
        self.assertEqual(
            hbf.Hosts(items=[
                "2a02:6b8:b::/64",
                "2a02:6b8:a::/64",
                "::1"
            ]),
            ruleset[ip_network("::/0")][0].dst
        )

        # обновим макрос _TESTMACROS_ чтобы пересчитать dst часть правила в dummy
        test_macroses = {"_TESTMACROS_": ["2a02:6b8:a::/64"]}
        with unittest.mock.patch.object(self.__class__, "MACROSES", new=test_macroses):
            updated_macroses = hbf.Macroses().update()
            hbf.Hosts.cache_clear()
            fw.update_macroses(updated_macroses)
            # проверим, что в макросе остался только 1 элемент
            self.assertEqual(len(test_macroses["_TESTMACROS_"]),
                             len(hbf.Macroses()["_TESTMACROS_"]))

            new_ruleset = fw.get_rules_for(ip, direction='out')
            new_ruleset = hbf.Ruleset.as_dict(new_ruleset)

            self.assertEqual(2, len(new_ruleset))
            # должна была отъехать сеть 2a02:6b8:b::/64
            self.assertEqual(
                hbf.Hosts(items=["2a02:6b8:a::/64", "::1"]),
                new_ruleset[ip_network("::/0")][0].dst
            )


class TestIncompleteSections(BaseTest):
    HOSTS = {
        "host1": ["10.0.0.1"],
        "host2": ["10.0.0.2"],
    }

    MACROSES = {
        "_TESTNETS_": [
            "192.168.0.0/16",
        ],
        "_TEST_SRV_": [
            "host1"
        ],
        "_BIG_MACRO_": [
            "notexits.host1",
            "host1",
            "host2",
            "notexits.host2",
        ]
    }

    def test_incomplete1(self):
        """
        Этот тест эмулирует "холодный старт" hbf, когда какого-то макроса или hostname нет.
        В этом случае он должен игнорировать секцию, использующую такой макрос, в IN-рулсете,
        но прменять все правила, которые может распарсить, в out-рулсете.

        Сама секция должна иметь при этом флаг 'incomplete'
        """
        sect_name = "TEST"
        sect_text = """
        add allow ip from { _NOTEXIST_ } to { _TESTNETS_ }
        add allow ip from { _TEST_SRV_ } to { _TESTNETS_ }
        ALLOW_STD_ICMP({ _TESTNETS_ })
        """

        fw = hbf.FW()

        # удалился макрос _NOTEXIST_
        # проверим, что секция без макроса создалась с 2 правилами и атрибутом incomplete

        hbf.Macroses().update()

        fw.sections = {sect_name: hbf.Section(sect_name, sect_text)}

        self.assertTrue(fw.sections[sect_name].incomplete)
        self.assertEqual(2, len(fw.sections[sect_name].rules))

        src_ip = ip_network("10.0.0.1")  # host1 in _TEST_SRV_
        dst_ip = ip_network("192.168.0.1")  # in _TESTNETS_
        fw.assert_section_for(dst_ip)

        # должно найтись 2 правила на in и 1 на out
        self.assertEqual(2, len(fw.get_rules_for(dst_ip, 'in')[0].rules))
        self.assertEqual(1, len(fw.get_rules_for(src_ip, 'out')[0].rules))

        # А теперь эмулируем ситуацию, когда макрос вернулся
        new_macroses = self.MACROSES.copy()
        new_macroses["_NOTEXIST_"] = ["host2"]
        with unittest.mock.patch.object(self.__class__, "MACROSES", new=new_macroses):
            # fw.sections = {sect_name: hbf.Section(sect_name, sect_text)}
            updated_macroses = hbf.Macroses().update()
            updated_rule_count = fw.update_macroses(updated_macroses)

            self.assertEqual(1, updated_rule_count)
            self.assertFalse(fw.sections[sect_name].incomplete)
            self.assertEqual(2, len(fw.sections[sect_name].rules))
            fw.assert_section_for(dst_ip)
            self.assertEqual(2, len(fw.get_rules_for(dst_ip, 'in')[0].rules))
            self.assertEqual(1, len(fw.get_rules_for(src_ip, 'out')[0].rules))

    def test_incomplete2(self):
        """
        Если в процессе работы в макрос добавился плохой хост,
        то секция должна пометиться как incomplete.
        Когда этот хост пропадёт из макроса, секция должна стать обратно complete
        """
        sect_name = "TEST"
        section = hbf.Section(sect_name, """
            add allow ip from { host1 } to { _TESTNETS_ }
            add allow ip from { _TEST_SRV_ } to { _TESTNETS_ }
            ALLOW_STD_ICMP({ _TESTNETS_ })
            """)
        fw = hbf.FW()
        fw.sections = {section.name: section}
        self.assertFalse(section.incomplete)

        new_macroses = self.MACROSES.copy()
        new_macroses["_TEST_SRV_"] = new_macroses["_TEST_SRV_"] + ["notexist.host"]
        with unittest.mock.patch.object(self.__class__, "MACROSES", new=new_macroses):
            updated_rule_count = fw.update_macroses(hbf.Macroses().update())
            self.assertTrue(section.incomplete)
            self.assertEqual(1, updated_rule_count)

        # секция должна выйти из incomplete
        updated_rule_count = fw.update_macroses(hbf.Macroses().update())
        self.assertFalse(section.incomplete)
        self.assertEqual(1, updated_rule_count)

    def test_incomplete3(self):
        """
        если секция содержит синтаксические ошибки, она помечается как incomplete
        если у неё при этом есть нерезолвящиеся хосты, то когда они вернутся,
        правила становятся complete, но секция остаётся incomplete
        """
        sect_name = "TEST"
        section = hbf.Section(sect_name, """
            add allow ip from { notexist.host } to { _TESTNETS_ }
            add allow ip from { _TEST_SRV_ } to { _TESTNETS_ }
            add allow ip from { 10.0.0.0/8 } to { _TESTNETS_ }
            # синтаксическая ошибка
            bla bla bla
            ALLOW_STD_ICMP({ _TESTNETS_ })
            """)
        fw = hbf.FW()
        fw.sections = {section.name: section}

        self.assertTrue(section.incomplete)

        def count_incomplete_rules(sect):
            return sum(1 for rule in sect.rules if any(s.incomplete for s in [rule.src, rule.dst]))

        # 1 incomplete-правило
        n_incomplete_rules = count_incomplete_rules(section)
        self.assertEqual(1, n_incomplete_rules)
        # 2 нормальных правила
        self.assertEqual(2, len(section.rules) - n_incomplete_rules)

        new_hosts = self.HOSTS.copy()
        new_hosts["notexist.host"] = ["192.168.0.1"]
        with unittest.mock.patch.object(self.__class__, "HOSTS", new=new_hosts):
            updated_rule_count = fw.update_fqdn(["notexist.host"])
            self.assertEqual(1, updated_rule_count)
            # больше нет incomplete-правил
            self.assertEqual(0, count_incomplete_rules(section))
            # а секция всё равно incomplete, т.к. есть синтаксически неверные правила
            self.assertTrue(section.incomplete)

    def test_incomplete4(self):
        """
        если в правиле что-то не резолвится, само правило работает, только
        не содержит нужных кусков
        """
        sect_name = "TEST"
        section = hbf.Section(sect_name, """
            add allow ip from { notexist.host or _BIG_MACRO_ or _TESTNETS_ } to { _TESTNETS_ or _NOTEXIST_MACRO_ or 192.168.2.2 }
            ALLOW_STD_ICMP({ _TESTNETS_ })
            """)
        fw = hbf.FW()
        fw.sections = {section.name: section}

        rule = section.rules[0]
        self.assertEqual(
            hbf.Hosts([
                "10.0.0.1",  # host1 from _BIG_MACRO_
                "10.0.0.2",  # host2 from _BIG_MACRO_
                "192.168.0.0/16",  # _TESTNETS_
            ]),
            rule.src
        )
        self.assertEqual(
            hbf.Hosts([
                "192.168.0.0/16",  # _TESTNETS_
                "192.168.2.2",
            ]),
            rule.dst
        )


class TestSectionRemove(BaseTest):
    HOSTS = {
        'testhost' : ['192.168.0.1'],
    }
    MACROSES = {
        '_TEST1NETS_': ["10.1.0.0/24"],
        '_TEST2NETS_': ["10.2.0.0/24"]
    }

    def test1(self):
        fw = hbf.FW()
        # сначала есть обе секции
        fw.sections = {
            'TEST1': hbf.Section('TEST1', """
                add allow ip from { testhost } to { _TEST1NETS_ }
                ALLOW_STD_ICMP({ _TEST1NETS_ })
                """),
            'TEST2': hbf.Section('TEST2', """
                add allow ip from { testhost } to { _TEST2NETS_ }
                ALLOW_STD_ICMP({ _TEST2NETS_ })
                """),
        }

        # и они находятся по ip в scope
        fw.assert_section_for(ip_network('10.1.0.100'))
        fw.assert_section_for(ip_network('10.2.0.100'))

        removed_sections = {
            'TEST2',
        }
        new_sections = {sname: sect for (sname, sect) in fw.sections.items() if sname not in removed_sections}
        self.assertEqual(1, len(new_sections))

        # затем удаляется секция TEST2 из cvs
        with unittest.mock.patch('hbf.code.FW._get_sections', return_value=(new_sections, removed_sections)):
            for sname in removed_sections:
                fw.update_sections(sname)

            # и в fw.sections остаётся только одна - new_sections
            self.assertEqual(fw.sections, new_sections)
            # IP из TEST1 по-прежнему находится
            fw.assert_section_for(ip_network('10.1.0.100'))
            # а из TEST2 - уже нет
            self.assertRaises(hbf.FWSectionNotFound, lambda: fw.assert_section_for(ip_network('10.2.0.100')))


class TestSkipMacroUpdate(BaseTest):
    MACROSES = {
        "_SKIP_MACRO_": ["93.158.0.0/24"],
    }

    def _is_critical_notfound_error(self, ip_str):
        try:
            hbf.FW().assert_section_for(ip_network(ip_str))
        except hbf.FWSectionNotFound as e:
            return not bool(e.tag)
        else:
            raise AssertionError("expected FWSectionNotFound not raised")

    @unittest.mock.patch('hbf.code.FW.MACROS_WITHOUT_SECTIONS', {"_SKIP_MACRO_", })
    def test1(self):
        hbf.FW().update_macroses(None)  # read MACROS_WITHOUT_SECTIONS

        # rfc1918 - не critical
        self.assertFalse(self._is_critical_notfound_error('10.0.0.1'))

        # IP из _SKIP_MACRO_ - не critical
        self.assertFalse(self._is_critical_notfound_error('93.158.0.12'))

        # случайные белые IP - critical
        self.assertTrue(self._is_critical_notfound_error('93.158.1.1'))

        with unittest.mock.patch.object(self.__class__, "MACROSES", {"_SKIP_MACRO_": self.MACROSES["_SKIP_MACRO_"] + ["93.158.1.0/24"]}):
            updated_macroses = hbf.Macroses().update()
            hbf.FW().update_macroses(updated_macroses)

            # тот же самый случайный белые IP - уже не critical
            self.assertFalse(self._is_critical_notfound_error('93.158.1.1'))


class TestMacroUpdate(BaseTest):
    HOSTS = {
        "testhost1": ["10.1.0.1"],
        "testhost2": ["10.1.0.2"],
        "testhost3": ["192.168.0.1", "2001:a:b:c::1"],
    }

    MACROSES = {
        "_TEST1NETS_": [
            "192.168.0.0/16",
            # "2001:a:b:c::/64",  # будет добавлено по ходу теста
        ],
        "_TEST2NETS_": [
            "192.168.0.0/16",
            "2001:a:b:c::/64",
        ]
    }

    def test_scope_update(self):
        fw = hbf.FW()
        sect = hbf.Section('TEST1', """
                add allow ip from { testhost1 } to { testhost3 }
                add allow ip from { testhost2 } to { _TEST1NETS_ }
                ALLOW_STD_ICMP({ _TEST1NETS_ })
                """)
        fw.sections = {'TEST1': sect}

        self.assertCountEqual(sect.rules[0].dst.prefixes(), [ip_network("192.168.0.1")])
        self.assertCountEqual(sect.rules[1].dst.prefixes(), [ip_network("192.168.0.0/16")])

        # в scope добавилась новая сеть
        new_macroses = self.MACROSES.copy()
        new_macroses["_TEST1NETS_"].append("2001:a:b:c::/64")
        with unittest.mock.patch.object(self.__class__, "MACROSES", new=new_macroses):
            self.assertEqual(fw.update_macroses(hbf.Macroses().update()), 2)

            self.assertCountEqual(sect.rules[0].dst.prefixes(), [ip_network("192.168.0.1"),
                                                                 ip_network("2001:a:b:c::1")])
            self.assertCountEqual(sect.rules[1].dst.prefixes(), [ip_network("192.168.0.0/16"),
                                                                 ip_network("2001:a:b:c::/64")])

    def test_host_intersect1(self):
        h1 = hbf.Hosts(["testhost3"])
        h2 = hbf.Hosts(["_TEST2NETS_"])

        self.assertEqual(h1.intersect(h2), h1)
        self.assertEqual(h2.intersect(h1), h1)

    def test_host_intersect2(self):
        h1 = hbf.Hosts(["testhost3"])
        h2 = hbf.Hosts(["_TEST1NETS_"])

        h1_v4 = hbf.Hosts(["192.168.0.1"])

        self.assertEqual(h1.intersect(h2), h1_v4)
        self.assertEqual(h2.intersect(h1), h1_v4)

        new_macroses = self.MACROSES.copy()
        new_macroses["_TEST1NETS_"] = self.MACROSES["_TEST2NETS_"]
        with unittest.mock.patch.object(self.__class__, "MACROSES", new=new_macroses):
            hbf.Macroses().update()
            h2.update()

            # здесь в h2 добавилась новая сеть и кеш _radix внутри должен обновиться
            self.assertEqual(h1.intersect(h2), h1)
            self.assertEqual(h2.intersect(h1), h1)
