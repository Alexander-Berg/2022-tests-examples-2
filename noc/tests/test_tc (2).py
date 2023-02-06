import os
import pytest

import modules.tc as tc


class Testtc(object):
    @pytest.yield_fixture
    def arguments(self):
        iface = "dummy0"
        os.system('/sbin/tc qdisc add dev %s ingress' % iface)
        os.system('/sbin/tc qdisc add dev %s root handle 1: htb' % iface)
        yield {
            "interface": iface,
            "pref": 65535,
            "internal_ip": "127.0.0.127",
            "external_ip": "10.10.10.10",
            "internal_ip_prefix": "127.0.0.127/32",
            "external_ip_prefix": "10.10.10.10/32",
        }

    def test_tc_rules_operations(self, arguments):
        assert tc.add_tc_rules(**arguments), \
            "tc rule hasn't beed added"
        tc_rules = tc.get_tc_rules(arguments['interface'])
        assert tc_rules, "tc rules is empty"

        assert tc.is_tc_rule_exist(tc_rules,
                arguments['internal_ip_prefix'], arguments['external_ip_prefix']), \
            "tc rule doesn't exist"

        # clean exist rules
        for line in tc_rules:
            if tc.is_tc_rule_exist([line],
                    arguments['internal_ip_prefix'], arguments['external_ip_prefix']):
                arguments['pref'] = line[line.index('pref') + 1]
                filter_type = line[line.index('nat') + 1]
                if filter_type == 'ingress':
                    arguments['parent'] = 'ffff:'
                else:
                    arguments['parent'] = '1:'
                assert tc.del_tc_rule(**arguments), "tc rule has not beed removed"

        tc_rules = tc.get_tc_rules(arguments['interface'])
        assert not tc.is_tc_rule_exist(tc_rules,
                arguments['internal_ip_prefix'], arguments['external_ip_prefix']), \
            "Does tc rule exist?"
