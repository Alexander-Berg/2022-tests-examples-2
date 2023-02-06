import unittest

from hbf.ipaddress2 import ip_network, TrypoNetwork, collapse_addresses


class Ipaddress2TestCase(unittest.TestCase):
    def test_supernet(self):
        self.assertEqual('2a02:6b8:c01:105:0:639:0:44/127',
                         str(ip_network('2a02:6b8:c01:105:0:639:0:45').supernet()))

        self.assertEqual('126.0.0.0/7',
                         str(ip_network('127.0.0.0/8').supernet()))

    def test_TrypoNetwork(self):
        trypo_net = TrypoNetwork('25c@2a02:6b8:c00::/40')
        self.assertIn(ip_network("2a02:06b8:c00::0000:025c:0000:0001"), trypo_net)
        self.assertNotIn(ip_network("2a02:06b8:c00::125c:0000:0001"), trypo_net)
        self.assertEqual(ip_network("2a02:6b8:c00::25c:0:0/96"),
                         TrypoNetwork("25c@2a02:6b8:c00::/40").zero_cidr())

        # проверка TrypoNetwork.zero_cidr()
        t = TrypoNetwork("25c@2a02:6b8:c00::/40")
        self.assertEqual("2a02:6b8:c00::25c:0:0/96", str(t.zero_cidr()))

        # проверка трипо-префикса с битами в geo
        t = TrypoNetwork("25c@2a02:6b8:c00:1::25c:0:0/40")
        self.assertEqual("2a02:6b8:c00::25c:0:0/96", str(t.zero_cidr()))

        # проверка конструктора с /31
        self.assertEqual(trypo_net, ip_network(str(trypo_net)))
        strypo = trypo_net.supernet()
        self.assertEqual(strypo, ip_network(str(strypo)))

    def test_TrypoNetwork_supernet(self):
        t = TrypoNetwork("23@2a02:6b8:c00::/40")
        super_t = t.supernet()
        self.assertEqual("22/31@2a02:6b8:c00::/40", str(super_t))
        self.assertEqual("20/30@2a02:6b8:c00::/40", str(super_t.supernet()))
        for i in range(31):
            super_t = super_t.supernet()
        # когда кончится project id u32 маска
        self.assertEqual(ip_network("2a02:6b8:c00::/40"), super_t)

    def test_TrypoNetwork_contains(self):
        t = TrypoNetwork("23@2a02:6b8:c00::/40")
        self.assertIn(t, t)
        super_t = t.supernet()
        self.assertIn(TrypoNetwork("22@2a02:6b8:c00::/40"), super_t)
        self.assertIn(TrypoNetwork("23@2a02:6b8:c00::/40"), super_t.supernet())
        self.assertNotIn(TrypoNetwork("323@2a02:6b8:c00::/40"), super_t.supernet())
        # сравнение обычной сети и трипо
        t = TrypoNetwork("2@2a02:6b8:c00::/40")
        super_t = t.supernet()
        super_t = super_t.supernet()
        self.assertNotIn(ip_network("2a02:6b8::/51"), super_t.supernet())

        # проверить вхождение в root network
        self.assertIn(t, ip_network("::/0"))
        self.assertNotIn(ip_network("::/0"), t)

    def test_TrypoNetwork_collapse1(self):
        t1 = TrypoNetwork("640@2a02:6b8:c00::/40")
        t2 = TrypoNetwork("641@2a02:6b8:c00::/40")
        coll = collapse_addresses([t1, t2])
        self.assertEqual([ip_network("640/31@2a02:6b8:c00::/40")], coll)
        self.assertIn(t1, coll[0])
        self.assertIn(t2, coll[0])

    def test_TrypoNetwork_collapse2(self):
        t1 = TrypoNetwork("604@2a02:6b8:c00::/40")
        t2 = TrypoNetwork("1000000/8@2a02:6b8:c00::/40")
        self.assertEqual([t1, t2], collapse_addresses([t1, t2]))

    def test_TrypoNetwork_str(self):
        pairs = [
            ("640@2a02:6b8:c00::/40", "640@2a02:6b8:c00::/40"),
            ("2a02:6b8:c00:0:1:2:3:4", "2a02:6b8:c00:0:1:2:3:4"),
            ("2a02:6b8:c00::2:3:0/112", "2@2a02:6b8:c00:0:0:2:3:0/112"),
            ("2a02:6b8:c00::2:3:0/112", "2@2a02:6b8:c00:0:0:0:3:0/112"),
            ("2a02:6b8:c00::2:0:0/96", "2@2a02:6b8:c00::/64"),
            ("2@2a02:6b8:c00::/63", "2@2a02:6b8:c00::/63"),
        ]
        for (expected, orig) in pairs:
            self.assertEqual(expected, str(TrypoNetwork(orig)))

    def test_is_host(self):
        self.assertTrue(ip_network("::1").is_host)
        self.assertFalse(ip_network("640@2a02:6b8:c00::/40").is_host)
        self.assertFalse(ip_network("2a02:6b8:c00::/40").is_host)

    def test_entire_pid(self):
        self.assertFalse(ip_network("2a02:6b8::/32").has_entire_project_id())
        self.assertFalse(ip_network("2a02:6b8:c00::/40").has_entire_project_id())

        self.assertFalse(ip_network("2a02:6b8:c00::/95").has_entire_project_id())
        self.assertTrue(ip_network("2a02:6b8:c00::/96").has_entire_project_id())

        self.assertTrue(ip_network("604@2a02:6b8:c00::/95").has_entire_project_id())

        self.assertFalse(ip_network("604/30@2a02:6b8:c00::/40").has_entire_project_id())
        self.assertTrue(ip_network("604@2a02:6b8:c00::/40").has_entire_project_id())

        self.assertTrue(ip_network("2a02:6b8:c00:0:1:2:3:4").has_entire_project_id())
        self.assertTrue(ip_network("::1").has_entire_project_id())

    def test_invalid_ip_network(self):
        with self.assertRaises(ValueError):
            # This previously resulted in segfault.
            ip_network('/40')
