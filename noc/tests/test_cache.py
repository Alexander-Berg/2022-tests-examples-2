import unittest

import hbf.code as hbf

from . import BaseTest
from hbf.ipaddress2 import ip_network


class InputItemsTest(BaseTest):
    HOSTS = {
        "test10.yndx.net": ["10.0.0.10"],
    }

    MACROSES = {
        "TESTMACRO1": [
            "10.0.0.0/24",
            "10.1.1.1",
            "test10.yndx.net",
        ],
    }

    def test_Macros1(self):
        macroses = hbf.Macroses()
        # проверка исключания на поиск несуществующего макроса
        self.assertRaises(KeyError, macroses.__getitem__, 'NOTEXISTS')

        # проверим что get_prefixes_by_macros выдаст корректные префиксы
        expected_prefixes = [ip_network('10.1.1.1'),
                             ip_network('10.0.0.0/24'),
                             ip_network('10.0.0.10')]
        actual_prefixes = macroses.get_prefixes_by_macros('TESTMACRO1')
        self.assertCountEqual(expected_prefixes, actual_prefixes)


class TestCache(hbf.BaseCache):
    pass


class BaseCacheTest(BaseTest):
    def tearDown(self):
        TestCache().clear()
        super().tearDown()

    def gen_data_iter(self, n=3, mult=100, exception=None):
        def data_iter(self):
            for i in range(1, n + 1):
                yield (i, i * mult)
            if exception is not None:
                raise exception()
        return data_iter

    def test1(self):
        with unittest.mock.patch.object(TestCache, 'data_iter', new=self.gen_data_iter(3, 100, None)):
            cache = TestCache()
            cache.update()
        self.assertEqual(len(cache), 3)
        self.assertEqual(cache[1], 100)

        with unittest.mock.patch.object(TestCache, 'data_iter', new=self.gen_data_iter(2, 200, None)):
            cache = TestCache()
            cache.update()
        self.assertEqual(len(cache), 2)
        self.assertEqual(cache[1], 200)

        with unittest.mock.patch.object(TestCache, 'data_iter', new=self.gen_data_iter(4, 1000, Exception)):
            cache = TestCache()
            cache.update()
        # ничего не изменилось, т.к. в конце выкинули exception
        self.assertEqual(len(cache), 2)
        self.assertEqual(cache[1], 200)


class IncludeStaleMacroTest(BaseTest):
    """
    Проверяет, что при появлении нераскрываемого элемента в макросе парсер правила не выкидывает исключения
    """
    MACROSES = {
        "_SOMENETS_": [
            "10.0.1.0/24",
            "10.0.2.0/24",
            "_MISSINGNETS_",
        ],
        # "_MISSINGNETS_" is missing
    }

    def test1(self):
        rule = hbf.Rule("add allow ip from { _SOMENETS_ } to { _SOMENETS_ }")
        self.assertEqual(rule.src, hbf.Hosts(["10.0.1.0/24", "10.0.2.0/24"]))
        self.assertEqual(rule.dst, hbf.Hosts(["10.0.1.0/24", "10.0.2.0/24"]))


class CloudRangeCacheTest(BaseTest):
    MACROSES = {
        "_CLOUD_PID_RANGE_": [
            "f800/21@2a02:6b8:c00::/40",
        ]
    }

    def test1(self):
        fw = hbf.FW()
        fw.sections = {
            "A": hbf.Section("A", """
                add allow tcp from { _CLOUD_PID_RANGE_ } to { _CLOUD_PID_RANGE_ } 80
                add allow tcp from any to { _CLOUD_PID_RANGE_ } 443
                STD_SECTION_FOOTER_OUT({ _CLOUD_PID_RANGE_ })
            """)
        }
        targets, errs = hbf.make_targets(["2a02:6b8:c01:2:0:f801:1:2"])
        self.assertFalse(errs)
        fw.assert_section_for(list(targets.keys())[0])

        _, ipt1 = hbf.build_iptables_ruleset(targets, del_qloud_pid_range=False)
        _, ipt2 = hbf.build_iptables_ruleset(targets, del_qloud_pid_range=True)
        rs1 = ipt1["ip6tables"]["all"]['Y1_TO_f800/21@ya:c00::/40']
        rs2 = ipt2["ip6tables"]["all"]['Y1_TO_f800/21@ya:c00::/40']
        self.assertNotEqual(rs1, rs2)
