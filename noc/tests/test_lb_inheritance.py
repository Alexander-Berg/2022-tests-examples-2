from l3mgr.tests.base import RESTAPITest


class LBInheritanceTest(RESTAPITest):
    def test_parent_has_balancers(self):
        user = self._get_auth_client()
        self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        abc = self._get_abc(user, "logbroker_child")
        self.assertEqual(0, len(abc["lb"]))
        self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "logbroker_child",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ],
        )
        abc = self._get_abc(user, "logbroker_child")
        self.assertEqual(1, len(abc["lb"]))

    def test_parent_has_no_balancers(self):
        user = self._get_auth_client()
        abc = self._get_abc(user, "Logbroker")
        self.assertEqual(0, len(abc["lb"]))
        abc = self._get_abc(user, "logbroker_child")
        self.assertEqual(0, len(abc["lb"]))
        self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "logbroker_child",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ],
        )
        abc = self._get_abc(user, "logbroker_child")
        self.assertEqual(0, len(abc["lb"]))

    def test_grandparent_has_balancers(self):
        user = self._get_auth_client()
        self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        abc = self._get_abc(user, "logbroker_grandchild")
        self.assertEqual(0, len(abc["lb"]))
        self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "logbroker_grandchild",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ],
        )
        abc = self._get_abc(user, "logbroker_grandchild")
        self.assertEqual(1, len(abc["lb"]))

    def test_grandparent_and_parent_both_has_balancers(self):
        user = self._get_auth_client()
        self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        self._prepare_balancer(user, "man1-lb4b.yndx.net", ["logbroker_child"])
        abc = self._get_abc(user, "logbroker_grandchild")
        self.assertEqual(0, len(abc["lb"]))
        abc = self._get_abc(user, "logbroker_child")
        self.assertEqual(1, len(abc["lb"]))
        abc = self._get_abc(user, "Logbroker")
        self.assertEqual(1, len(abc["lb"]))
        self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "logbroker_grandchild",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ],
        )
        abc = self._get_abc(user, "logbroker_grandchild")
        self.assertEqual(1, len(abc["lb"]))
        self.assertEqual("man1-lb4b.yndx.net", abc["lb"][0]["fqdn"])
