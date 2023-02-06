import os
import pytest

import modules.ip as ip


class Testip(object):
    @pytest.yield_fixture
    def ipaddr(self):
        yield "10.10.10.10"

    @pytest.yield_fixture
    def interface(self):
        yield "dummy0"

    @pytest.yield_fixture
    def ip_rule(self):
        rule = {"from": "10.0.0.0/8", "lookup": "1", "pref": "1000"}
        yield rule
        ip.del_rule(rule)

    def test_dummy_ip_operations(self, ipaddr, interface):
        ip.del_dummy_ip(ipaddr, interface)
        assert ip.add_dummy_ip(ipaddr, interface), \
            "add_dummy_ip: return wrong status code"
        assert not ip.add_dummy_ip(ipaddr, interface), \
            "add_dummy_ip: has address beed added second time?"

        assert ip.del_dummy_ip(ipaddr, interface), \
            "del_dummy_ip: return wrong status code"
        assert not ip.del_dummy_ip(ipaddr, interface), \
            "del_dummy_ip: has address beed deleted second time??"

    def test_is_ip_exist_on_dummy(self, ipaddr, interface):
        ip.del_dummy_ip(ipaddr, interface)
        assert not ip.is_ip_exist_on_dummy(ipaddr), \
            "ip address has found, but it doesn't exist"

        ip.add_dummy_ip(ipaddr, interface)
        assert ip.is_ip_exist_on_dummy(ipaddr), \
            "ip address doesn't found"

    def test_is_ip_in_networks(self, ipaddr):
        assert ip.is_ip_in_networks(ipaddr, ["0.0.0.0/0"]), \
            "0.0.0.0/0 doesn't include ip address"

        assert not ip.is_ip_in_networks(ipaddr, ["255.255.255.255/32"]), \
            "255.255.255.255/32 network includes ip address"

    def test_rule_operations(self, ip_rule):
        ip.del_rule(ip_rule)
        assert not ip.filter_rules(ip_rule), "ip rule exists after delete"

        assert ip.add_rule(ip_rule), "cannot add ip rule"
        assert ip.filter_rules(ip_rule), "rule doesn't found after add"
        assert ip.del_rule(ip_rule), "cannot delete ip rule"
        assert not ip.filter_rules(ip_rule), "rule has found after delete actions"

    def test_get_rules_list(self, ip_rule):
        assert ip.add_rule(ip_rule), "cannot add ip rule"
        assert ip_rule in ip.get_rules_list(), \
            "ip rule doesn't exists in rules list"
