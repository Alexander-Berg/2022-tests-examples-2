import os.path

import importlib
import importlib.util
import pytest
import yatest
from typing import Callable

import comocutor_contrib.parsers as parsers
from comocutor_contrib.parsers import (parse_ios_bgp_neighbors, parse_xr_bgp_neighbors, parse_ios_inventory,
                                       nexus_transceiver_parse, parse_vrp_transceiver_information,
                                       parse_vrp_ipv6_routing, parse_vrp_ipv6_routing_brief, parse_vrp_ipv4_routing, parse_vrp_ipv6_fib, parse_vrp_ipv4_fib)
from data import (ios_bgp_neighbors, xr_bgp_neighbors, xr_bgp_neighbors2, nexus_show_inventory,
                  nexus_show_interface_transceiver)
from data.lib import Data


def test_ios_bgp_bgp_neighbors():
    res = parse_ios_bgp_neighbors(ios_bgp_neighbors.content)
    assert res[1] == {
        "neighbor": "5.45.247.180",
        "remote AS": "13238",
        "address family": {
            "VPNv4 Unicast": {"prefix activity": {"Prefixes Current": {"Sent": "351", "Rcvd": "2"},
                                                  "Prefixes Total": {"Sent": "14677", "Rcvd": "7"},
                                                  "Implicit Withdraw": {"Sent": "374", "Rcvd": "0"},
                                                  "Explicit Withdraw": {"Sent": "14322", "Rcvd": "5"},
                                                  "Used as bestpath": {"Sent": "n/a", "Rcvd": "2"},
                                                  "Used as multipath": {"Sent": "n/a", "Rcvd": "0"}}},
            "VPNv6 Unicast": {"prefix activity": {"Prefixes Current": {"Sent": "817", "Rcvd": "2"},
                                                  "Prefixes Total": {"Sent": "3046", "Rcvd": "4"},
                                                  "Implicit Withdraw": {"Sent": "921", "Rcvd": "0"},
                                                  "Explicit Withdraw": {"Sent": "2097", "Rcvd": "2"},
                                                  "Used as bestpath": {"Sent": "n/a", "Rcvd": "2"},
                                                  "Used as multipath": {"Sent": "n/a", "Rcvd": "0"}},
                              "Maximum prefixes allowed": "3000"}}}
    res = parse_xr_bgp_neighbors(xr_bgp_neighbors.content)
    assert res[1] == {
        'neighbor': '5.45.247.180',
        'state': 'Established', 'address family': {
            'VPNv4 Unicast': {'accepted prefixes': '2', 'Prefix advertised': '63282',
                              'Maximum prefixes allowed': '1000'},
            'VPNv6 Unicast': {'accepted prefixes': '2', 'Prefix advertised': '1945',
                              'Maximum prefixes allowed': '3000'}}}
    res = parse_xr_bgp_neighbors(xr_bgp_neighbors2.content)
    assert res[1] == {'neighbor': '5.45.247.180', 'state': 'Established', 'address family': {
        'IPv4 Unicast': {'accepted prefixes': '156', 'Prefix advertised': '14388', 'Maximum prefixes allowed': '5000'},
        'IPv6 Labeled-unicast': {'accepted prefixes': '86', 'Prefix advertised': '26140',
                                 'Maximum prefixes allowed': '5000'}}}


def test_parse_ios_inventory():
    parse_ios_inventory(nexus_show_inventory.content)


def test_nexus_transceiver_parse():
    nexus_transceiver_parse(nexus_show_interface_transceiver.content)


def _generic_parse_test(parse_fn: Callable, module_path: str):
    outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    test_data = yatest.common.source_path("noc/comocutor-contrib/tests/data")
    spec = importlib.util.spec_from_file_location(module_path,
                                                  os.path.join(outfile, os.path.join(test_data, module_path + ".py")))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for cls in dir(module):
        attr = getattr(module, cls)
        if isinstance(attr, type) and issubclass(attr, Data) and attr != Data:
            test_cls: Data = attr()
            res = parse_fn(test_cls.content)
            assert test_cls.result == res


CASES = (
    (parsers.parse_vrp_version, "vrp_display_version"),
    (parsers.parse_vrp_patch, "vrp_display_patch"),
    (parsers.parse_freebsd_ndp, "freebsd_ndp"),
    (parse_vrp_transceiver_information, "vrp_transceiver"),
    (parse_vrp_ipv6_routing, "vrp_ipv6_routing"),
    (parse_vrp_ipv4_routing, "vrp_ipv4_routing"),
    (parse_vrp_ipv6_routing_brief, "vrp_ipv6_routing_brief"),
    (parse_vrp_ipv4_fib, "vrp_ipv4_fib"),
    (parse_vrp_ipv6_fib, "vrp_ipv6_fib"),
    (parsers.parse_vrp_traffic_policy_stat_iface, "vrp_traffic_policy_stat_iface"),
    (parsers.parse_vrp_traffic_policy_stat_iface, "vrp_traffic_policy_stat_group"),
    (parsers.parse_adva_interface, "adva_show_int_c_phy_opr"),
    (parsers.parse_vrp_nd, "vrp_nd"),
    (parsers.parse_vrp_arp, "vrp_arp"),
    (parsers.parse_junos_arp, "junos_arp_human"),
    (parsers.parse_junos_arp, "junos_arp_xml"),
    (parsers.parse_junos_arp, "junos_arp_json"),
    (parsers.parse_junos_nd, "junos_nd_human"),
    (parsers.parse_junos_nd, "junos_nd_xml"),
    (parsers.parse_junos_nd, "junos_nd_json"),
    (parsers.parse_cisco_arp_nd, "nexus_arp_human"),
    (parsers.parse_cisco_arp_nd, "nexus_arp_xml"),
    (parsers.parse_cisco_arp_nd, "nexus_arp_json"),
    (parsers.parse_cisco_arp_nd, "nexus_nd_json"),
    (parsers.parse_cisco_arp_nd, "nexus_nd_xml"),
    (parsers.parse_vrp_int_brief, "vrp_display_int_brief"),
    (parsers.parse_vrp_intstatus, "vrp_intstatus_human"),
    (parsers.parse_vrp_mactable, "vrp_mactable_human"),
    (parsers.parse_cisco_intstatus, "ios_intstatus_human"),
    (parsers.parse_cisco_intstatus, "nexus_intstatus_human"),
    (parsers.parse_cisco_mactable, "ios_mactable_human"),
    (parsers.parse_cisco_mactable, "nexus_mactable_human"),
    (parsers.parse_elabel, "vrp_display_device_elabel"),
    (parsers.parse_jun_inventory, "jnx_show_chassis_hardware"),
    (parsers.parse_junos_intstatus, "junos_intstatus_human"),
    (parsers.parse_junos_intstatus, "junos_intstatus_json"),
    (parsers.parse_junos_intstatus, "junos_intstatus_xml"),
    (parsers.parse_cum_net_intstatus, "cum_net_show_interface_all"),
    (parsers.parse_cum_net_mactable, "cum_net_show_bidge_macs"),
    (parsers.parse_cum_ip_link, "cum_ip_link"),
    (parsers.parse_cum_bridge_fdb, "cum_bridge_fdb"),
    (parsers.parse_junos_mactable, "junos_mactable_human"),
    (parsers.parse_junos_mactable, "junos_mactable_json"),
    (parsers.parse_junos_mactable, "junos_mactable_xml"),
    (parsers.parse_linux_ip_addr, "linux_ip_addr"),
    (parsers.parse_linux_ip_neigh_show, "linux_ip_neigh_show"),
    (parsers.parse_freebsd_arp, "freebsd_arp"),
    (parsers.parse_cumulus_transceiver_information, "cumulus_transceiver_information"),
    (parsers.parse_ekinops_table, "ekinops_hwlist"),
    (parsers.parse_ekinops_table, "ekinops_get_measurements"),
    (parsers.parse_ekinops_table, "ekinops_get_counters"),
    (parsers.parse_vrp_system_forwarding_resource, "vrp_system_forwarding_resource"),
    (parsers.parse_vrp_ce_alarms, "vrp_ce_dis_alarm"),
    (parsers.parse_vrp_quidway_alarms, "vrp_quidway_dis_alarm"),
)


@pytest.mark.parametrize("fn, file", CASES)
def test_cases(file, fn):
    _generic_parse_test(fn, file)
