import unittest.mock
from textwrap import dedent

from . import BaseTest
import hbf.art as art
from hbf.ipaddress2 import ip_network


class TestTree(BaseTest):
    def setUp(self):
        super().setUp()
        self._register_patch('art_siblings', unittest.mock.patch('hbf.art.MAX_SIBLINGS', 4))

    def _assert_tree(self, expected, prefix_list, ipversion):
        expected = dedent(expected).strip() + "\n"

        items = [(pref, []) for pref in prefix_list]
        tree = art.build(items, ipversion)
        fmt_tree = tree._dump().strip() + "\n"

        self.assertEqual(expected, fmt_tree)

    def test_tree1(self):
        """
        простой тест на вставку доп. ноды в дерево
        """
        str_prefixes = """
            2a02:6b8:0:e00::/56
            2a02:6b8:0:e00::/64
            2a02:6b8:0:e02::/64
            2a02:6b8:0:eba::/63
            2a02:6b8:0:ebc::/64
            2a02:6b8:0:efa::/64
            """

        expected = """
            ::/0
              2a02:6b8:0:e00::/56
                2a02:6b8:0:e00::/62
                  2a02:6b8:0:e00::/64
                  2a02:6b8:0:e02::/64
                2a02:6b8:0:eba::/63
                2a02:6b8:0:ebc::/64
                2a02:6b8:0:efa::/64
            """

        prefix_list = map(ip_network, [x for x in dedent(str_prefixes).split("\n") if x])
        self._assert_tree(expected, prefix_list, ipversion=6)

    def test_tree2(self):
        """
        Комбинации trypo- и plain- сетей
        """

        # 1. plain больше proj_id
        str_prefixes = """
            1@2a02:6b8:c00::/40
            2a02:6b8:c10::1:a:1
            2a02:6b8:c10::1:a:2
            2a02:6b8:c10::1:a:3
            2a02:6b8:c10::1:a:4
            2a02:6b8:c10::1:1:0/124
        """

        expected = """
            ::/0
              2a02:6b8:c00::/40
                1@2a02:6b8:c00::/40
                  2a02:6b8:c10::1:1:0/124
                  2a02:6b8:c10::1:a:0/126
                    2a02:6b8:c10::1:a:1
                    2a02:6b8:c10::1:a:2
                    2a02:6b8:c10::1:a:3
                  2a02:6b8:c10::1:a:4

            """

        prefix_list = map(ip_network, [x for x in dedent(str_prefixes).split("\n") if x])
        self._assert_tree(expected, prefix_list, ipversion=6)

        # 2. вставка доп. нод на каждый trypo-агрегат и project_id в нём
        str_prefixes = """
            2a02:6b8:800::/37
            1@2a02:6b8:c10::/60
            2a02:6b8:c10::2:1:0
            3@2a02:6b8:c10::/60
            4@2a02:6b8:c10::/60
            5@2a02:6b8:c10::/60
        """

        expected = """
            ::/0
              2a02:6b8:800::/37
                2a02:6b8:c00::/40
                  0/30@2a02:6b8:c00::/40
                    1@2a02:6b8:c00::/40
                      1@2a02:6b8:c10::/60
                    2@2a02:6b8:c00::/40
                      2a02:6b8:c10::2:1:0
                    3@2a02:6b8:c00::/40
                      3@2a02:6b8:c10::/60
                  4@2a02:6b8:c00::/40
                    4@2a02:6b8:c10::/60
                  5@2a02:6b8:c00::/40
                    5@2a02:6b8:c10::/60
            """

        prefix_list = map(ip_network, [x for x in dedent(str_prefixes).split("\n") if x])
        self._assert_tree(expected, prefix_list, ipversion=6)

        # 3. plain пересекается с proj_id (magic nodes)
        str_prefixes = """
            1@2a02:6b8:c00::/40
            2@2a02:6b8:c00::/40
            2a02:6b8:c10:12::3:0:0/96
            2a02:6b8:c10:12::/64
            2a02:6b8:c12:11::/64
            2a02:6b8:c14:10::/64
            2a02:6b8:c12:500::/56
            2a02:6b8:c22:600::/56
            2a02:6b8:c32:700::/56
        """

        expected = """
            ::/0
              2a02:6b8:c00::/40
                2a02:6b8:c00::/40 *
                  2a02:6b8:c10::/46
                    2a02:6b8:c10:12::/64
                    2a02:6b8:c12:11::/64
                    2a02:6b8:c12:500::/56
                  2a02:6b8:c14:10::/64
                  2a02:6b8:c22:600::/56
                  2a02:6b8:c32:700::/56
                1@2a02:6b8:c00::/40
                2@2a02:6b8:c00::/40
                3@2a02:6b8:c00::/40
                  2a02:6b8:c10:12:0:3::/96
            """
        prefix_list = map(ip_network, [x for x in dedent(str_prefixes).split("\n") if x])
        self._assert_tree(expected, prefix_list, ipversion=6)

    def test_tree3(self):
        str_prefixes = """
            2a02:6b8:c00::/40
            2232df5@2a02:6b8:c00::/40
            2282028@2a02:6b8:c00::/40
            5f779ac@2a02:6b8:c00::/40
            6203de7@2a02:6b8:c00::/40
            6210234@2a02:6b8:c00::/40
            6211f93@2a02:6b8:c00::/40
            6d8af4f@2a02:6b8:c00::/40
            6e476e5@2a02:6b8:c00::/40
            6fa172d@2a02:6b8:c00::/40
            706ef7d@2a02:6b8:c00::/40
            2a02:6b8:c01:105:0:639:0:45
            2a02:6b8:c01:105:0:639:0:47
            2a02:6b8:c01:106:0:639:0:19
            2a02:6b8:c01:108:0:639:0:13
            2a02:6b8:c01:108:0:639:0:14
            2a02:6b8:c02:108:0:639:0:b9
            2a02:6b8:c03:105:0:640:0:45
            2a02:6b8:c04:105:0:640:0:47
            2a02:6b8:c02:106:0:640:0:19
            2a02:6b8:c02:108:0:640:0:13
            2a02:6b8:c02:108:0:640:0:14
            2a02:6b8:c02:108:0:640:0:b9
            639@2a02:6b8:c00::/40
            """
        expected = """
            ::/0
              2a02:6b8:c00::/40
                0/6@2a02:6b8:c00::/40
                  639@2a02:6b8:c00::/40
                    639@2a02:6b8:c01:104::/62
                      2a02:6b8:c01:105:0:639:0:45
                      2a02:6b8:c01:105:0:639:0:47
                      2a02:6b8:c01:106:0:639:0:19
                    2a02:6b8:c01:108:0:639:0:13
                    2a02:6b8:c01:108:0:639:0:14
                    2a02:6b8:c02:108:0:639:0:b9
                  640@2a02:6b8:c00::/40
                    2a02:6b8:c02:108:0:640::/120
                      2a02:6b8:c02:108:0:640:0:13
                      2a02:6b8:c02:108:0:640:0:14
                      2a02:6b8:c02:108:0:640:0:b9
                    2a02:6b8:c02:106:0:640:0:19
                    2a02:6b8:c03:105:0:640:0:45
                    2a02:6b8:c04:105:0:640:0:47
                  2232df5@2a02:6b8:c00::/40
                  2282028@2a02:6b8:c00::/40
                6000000/8@2a02:6b8:c00::/40
                  6200000/15@2a02:6b8:c00::/40
                    6203de7@2a02:6b8:c00::/40
                    6210234@2a02:6b8:c00::/40
                    6211f93@2a02:6b8:c00::/40
                  6d8af4f@2a02:6b8:c00::/40
                  6e476e5@2a02:6b8:c00::/40
                  6fa172d@2a02:6b8:c00::/40
                5f779ac@2a02:6b8:c00::/40
                706ef7d@2a02:6b8:c00::/40
            """

        prefix_list = map(ip_network, [x for x in dedent(str_prefixes).split("\n") if x])
        self._assert_tree(expected, prefix_list, ipversion=6)

    def test_tree4(self):
        str_prefixes = """
            2a02:6b8:c00::/48
            2a02:6b8:c08::/46
            2a02:6b8:c0c::/47
            2a02:6b8:c0f::/48
            2a02:6b8:c10::/46
            507@2a02:6b8:c00::/40
            516@2a02:6b8:c00::/40
            519@2a02:6b8:c00::/40
            522@2a02:6b8:c00::/40
            2a02:6b8:c01:101:0:516:0:11
            2a02:6b8:c01:101:0:516:0:12/127
            2a02:6b8:c01:101:0:639:0:12b
            2a02:6b8:c01:101:0:639:0:225
            2a02:6b8:c01:102:0:639:0:187
            2a02:6b8:c01:102:0:639:0:18b
            2a02:6b8:c01:102:0:639:0:19e
            """

        expected = """
            ::/0
              2a02:6b8:c00::/40
                2a02:6b8:c00::/40 *
                  2a02:6b8:c00::/48
                  2a02:6b8:c08::/45
                    2a02:6b8:c08::/46
                    2a02:6b8:c0c::/47
                    2a02:6b8:c0f::/48
                  2a02:6b8:c10::/46
                500/27@2a02:6b8:c00::/40
                  507@2a02:6b8:c00::/40
                  516@2a02:6b8:c00::/40
                    2a02:6b8:c01:101:0:516:0:12/127
                    2a02:6b8:c01:101:0:516:0:11
                  519@2a02:6b8:c00::/40
                522@2a02:6b8:c00::/40
                639@2a02:6b8:c00::/40
                  2a02:6b8:c01:102:0:639:0:180/123
                    2a02:6b8:c01:102:0:639:0:187
                    2a02:6b8:c01:102:0:639:0:18b
                    2a02:6b8:c01:102:0:639:0:19e
                  2a02:6b8:c01:101:0:639:0:12b
                  2a02:6b8:c01:101:0:639:0:225
            """

        prefix_list = map(ip_network, [x for x in dedent(str_prefixes).split("\n") if x])
        self._assert_tree(expected, prefix_list, ipversion=6)
