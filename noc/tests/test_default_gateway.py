from copy import deepcopy
from unittest.mock import patch

from default_gateway import check_default_routes, identify_af
from tt_main.constants import CRIT_STATUS, OK_STATUS, WARN_STATUS

SYS_ADDRS = {
    "eth1": {
        "status": "BROADCAST,MULTICAST,UP,LOWER_UP",
        "state": "UP",
        "inet": {
            "5.45.248.101/27": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            }
        },
        "scope": "link",
        "inet6": {
            "2a02:6b8:0:814::b38a/64": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            },
            "fe80::9a03:9bff:fec9:c088/64": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            }
        }
    },
    "eth0": {
        "status": "BROADCAST,MULTICAST,UP,LOWER_UP",
        "state": "UP",
        "inet": {
            "5.45.248.69/27": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            }
        },
        "scope": "link",
        "inet6": {
            "2a02:6b8:0:84c::b38a/64": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            },
            "fe80::9a03:9bff:fec9:c089/64": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            }
        }
    }
}


def test_identify_af_both():
    with patch("default_gateway.get_addr_show", return_value=SYS_ADDRS):
        af = identify_af()
    assert af == set([4, 6])


def test_identify_af_both_different_ifaces():
    sys_addrs = deepcopy(SYS_ADDRS)
    del sys_addrs["eth1"]["inet"]
    del sys_addrs["eth0"]["inet6"]
    with patch("default_gateway.get_addr_show", return_value=sys_addrs):
        af = identify_af()
    assert af == set([4, 6])


def test_identify_af_v4_only():
    sys_addrs = deepcopy(SYS_ADDRS)
    del sys_addrs["eth1"]["inet6"]
    del sys_addrs["eth0"]["inet6"]
    with patch("default_gateway.get_addr_show", return_value=sys_addrs):
        af = identify_af()
    assert af == set([4])


def test_identify_af_v6_only():
    sys_addrs = deepcopy(SYS_ADDRS)
    del sys_addrs["eth1"]["inet"]
    del sys_addrs["eth0"]
    with patch("default_gateway.get_addr_show", return_value=sys_addrs):
        af = identify_af()
    assert af == set([6])


def test_identify_af_none():
    sys_addrs = deepcopy(SYS_ADDRS)
    del sys_addrs["eth1"]["inet"]
    del sys_addrs["eth1"]["inet6"]["2a02:6b8:0:814::b38a/64"]
    del sys_addrs["eth0"]
    with patch("default_gateway.get_addr_show", return_value=sys_addrs):
        af = identify_af()
    assert af == set()


def test_check_default_routes_both_ok():
    defv4 = ["default via 192.0.2.15 dev eth0 metric 1001"]
    defv6 = ["default via 2001:db8:315::1 dev eth0 metric 1001 pref medium"]
    with patch("default_gateway.make_cmd_call", side_effect=[defv4, defv6]):
        status, message = check_default_routes(set([4, 6]))
    assert status == OK_STATUS


def test_check_default_routes_v6_only_ok():
    defv6 = ["default via 2001:db8:315::1 dev eth0 metric 1001 pref medium"]
    with patch("default_gateway.make_cmd_call", return_value=defv6):
        status, message = check_default_routes(set([6]))
    assert status == OK_STATUS


def test_check_default_routes_v4_only_ok():
    defv4 = ["default via 192.0.2.15 dev eth0 metric 1001"]
    with patch("default_gateway.make_cmd_call", return_value=defv4):
        status, message = check_default_routes(set([4]))
    assert status == OK_STATUS


def test_check_default_routes_v4_only_no_route():
    with patch("default_gateway.make_cmd_call", return_value=[""]):
        status, message = check_default_routes(set([4]))
    assert status == CRIT_STATUS
    assert message == "IP version 4 has no default route"


def test_check_default_routes_v6_only_no_route():
    with patch("default_gateway.make_cmd_call", return_value=[""]):
        status, message = check_default_routes(set([6]))
    assert status == CRIT_STATUS
    assert message == "IP version 6 has no default route"


def test_check_default_routes_both_no_v4():
    defv4 = [""]
    defv6 = ["default via 2001:db8:315::1 dev eth0 metric 1001 pref medium"]
    with patch("default_gateway.make_cmd_call", side_effect=[defv4, defv6]):
        status, message = check_default_routes(set([4, 6]))
    assert status == CRIT_STATUS
    assert message == "IP version 4 has no default route"


def test_check_default_routes_both_no_both():
    with patch("default_gateway.make_cmd_call", side_effect=[[""], [""]]):
        status, message = check_default_routes(set([4, 6]))
    assert status == CRIT_STATUS
    assert message == ("IP version 4 has no default route; IP version 6 "
                       "has no default route")
