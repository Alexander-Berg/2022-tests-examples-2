from copy import deepcopy
from unittest.mock import patch

from tt_main.constants import CRIT_STATUS, OK_STATUS, WARN_STATUS
from tunnel_interfaces import check_tunnel_interfaces

MTU = 9000
# simplified version of what tt_main.system.get_addr_show return
TUN_DATA = [{
    'tunl0@NONE': {
        'status': 'NOARP,UP,LOWER_UP',
        'mtu': '9000',
        'state': 'UNKNOWN',
    }
}, {
    'ip6tnl0@NONE': {
        'status': 'NOARP,UP,LOWER_UP',
        'mtu': '9000',
        'state': 'UNKNOWN',
        'inet6': {
            'fe80::cc58:55ff:fe10:2b3c/64': {
                'valid_lft': 'forever',
                'preferred_lft': 'forever'
            }
        },
        'scope': 'link'
    }
}]


def test_check_tunnel_interfaces_ok():
    with patch("tunnel_interfaces.get_addr_show", side_effect=TUN_DATA):
        status, message = check_tunnel_interfaces()
    assert status == OK_STATUS


def test_check_tunnel_interfaces_nodata():
    tun_data = deepcopy(TUN_DATA)
    tun_data[1] = {}
    with patch("tunnel_interfaces.get_addr_show", side_effect=tun_data):
        status, message = check_tunnel_interfaces()
    assert status == CRIT_STATUS
    assert message == "can not get information on ip6tnl0"


def test_check_tunnel_interfaces_wrong_mtu():
    tun_data = deepcopy(TUN_DATA)
    tun_data[0]["tunl0@NONE"]["mtu"] = 8900
    with patch("tunnel_interfaces.get_addr_show", side_effect=tun_data):
        status, message = check_tunnel_interfaces()
    assert status == CRIT_STATUS
    assert message == f"tunl0 MTU lower than {MTU}"

    tun_data[0]["tunl0@NONE"]["mtu"] = 9000
    del tun_data[1]["ip6tnl0@NONE"]["mtu"]
    with patch("tunnel_interfaces.get_addr_show", side_effect=tun_data):
        status, message = check_tunnel_interfaces()
    assert status == CRIT_STATUS
    assert message == f"ip6tnl0 MTU lower than {MTU}"


def test_check_tunnel_interfaces_wrong_status():
    tun_data = deepcopy(TUN_DATA)
    tun_data[0]["tunl0@NONE"]["status"] = "DOWN"
    with patch("tunnel_interfaces.get_addr_show", side_effect=tun_data):
        status, message = check_tunnel_interfaces()
    assert status == CRIT_STATUS
    assert message == "tunl0 has empty or wrong status"

    tun_data[0]["tunl0@NONE"]["status"] = "UP,NOARP"
    del tun_data[1]["ip6tnl0@NONE"]["status"]
    with patch("tunnel_interfaces.get_addr_show", side_effect=tun_data):
        status, message = check_tunnel_interfaces()
    assert status == CRIT_STATUS
    assert message == "ip6tnl0 has empty or wrong status"


def test_check_tunnel_interfaces_multiple_problems():
    tun_data = deepcopy(TUN_DATA)
    tun_data[0]["tunl0@NONE"]["status"] = "DOWN"
    tun_data[1]["ip6tnl0@NONE"]["mtu"] = 1500
    with patch("tunnel_interfaces.get_addr_show", side_effect=tun_data):
        status, message = check_tunnel_interfaces()
    assert status == CRIT_STATUS
    assert message == ("tunl0 has empty or wrong status; "
                       f"ip6tnl0 MTU lower than {MTU}")
