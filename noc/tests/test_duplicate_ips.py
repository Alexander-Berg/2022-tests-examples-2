from copy import deepcopy
from unittest.mock import patch

from duplicate_ips import find_duplicate_ips
from tt_main.constants import CRIT_STATUS, OK_STATUS, WARN_STATUS

SYS_ADDRS = {
    "dummy12": {
        "status": "BROADCAST,NOARP,UP,LOWER_UP",
        "inet": {
            "5.255.240.205/32": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            },
            "93.158.157.215/32": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            },
            "213.180.193.47/32": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            }
        },
        "scope": "link",
        "inet6": {
            "2a02:6b8:0:3400:0:7cc:0:2/128": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            },
            "2a02:6b8:0:3400::1:225/128": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            },
            "2a02:6b8:0:3400:0:1c1:0:1/128": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            },
            "fe80::4ce4:17ff:fe0b:4a75/64": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            }
        }
    },
    "dummy13": {
        "status": "BROADCAST,NOARP,UP,LOWER_UP",
        "inet6": {
            "fe80::44b7:91ff:fe32:616b/64": {
                "valid_lft": "forever",
                "preferred_lft": "forever"
            }
        },
        "scope": "link"
    },
    "dummy14": {
        "status": "BROADCAST,NOARP"
    }
}


def test_find_duplicate_ips_ok():
    with patch("duplicate_ips.get_addr_show", return_value=SYS_ADDRS):
        status, message = find_duplicate_ips()
    assert status == OK_STATUS


def test_find_duplicate_ips_nodata():
    with patch("duplicate_ips.get_addr_show", return_value={}):
        status, message = find_duplicate_ips()
    assert status == CRIT_STATUS
    assert message == "can not get interfaces data"


def test_find_duplicate_ips_one_duplicate():
    sys_addrs = deepcopy(SYS_ADDRS)
    sys_addrs["dummy14"]["inet6"] = {
        "2a02:6b8:0:3400:0:7cc:0:2/128": {
            "valid_lft": "forever",
            "preferred_lft": "forever"
        }
    }
    with patch("duplicate_ips.get_addr_show", return_value=sys_addrs):
        status, message = find_duplicate_ips()
    assert status == CRIT_STATUS
    assert message == "2a02:6b8:0:3400:0:7cc:0:2 is duplicated"


def test_find_duplicate_ips_multiple_duplicates():
    sys_addrs = deepcopy(SYS_ADDRS)
    sys_addrs["dummy14"]["inet6"] = {
        "2a02:6b8:0:3400:0:7cc:0:2/128": {
            "valid_lft": "forever",
            "preferred_lft": "forever"
        }
    }
    sys_addrs["dummy14"]["inet"] = {
        "213.180.193.47/32": {
            "valid_lft": "forever",
            "preferred_lft": "forever"
        }
    }
    with patch("duplicate_ips.get_addr_show", return_value=sys_addrs):
        status, message = find_duplicate_ips()
    assert status == CRIT_STATUS
    assert "213.180.193.47" in message
    assert "2a02:6b8:0:3400:0:7cc:0:2" in message
