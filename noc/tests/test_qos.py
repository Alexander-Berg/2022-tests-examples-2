import unittest
import hbf.code as hbf
from . import BaseTest


class TestQos(BaseTest):
    def test_test1(self):
        qos_data = "*mangle\nCOMMIT\n\n"

        with unittest.mock.patch("builtins.open", unittest.mock.mock_open(read_data=qos_data)):
            hbf.FW().update_qos()

            targets, _ = hbf.make_targets("1.1.1.1")
            _, ruleset = hbf.build_iptables_ruleset(targets)
            fw_text = hbf.render_iptables_text(ruleset, qos=True)
            self.assertEqual(
                fw_text, """
#BEGIN IP6TABLES
*filter
:Y_FW -
:Y_FW_OUT -

COMMIT
*mangle
COMMIT
#END IP6TABLES
#BEGIN IPTABLES
*filter
:Y_FW -
:Y_FW_OUT -

COMMIT
*mangle
COMMIT
#END IPTABLES
""")
