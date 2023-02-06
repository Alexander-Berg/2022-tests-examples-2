import json
from unittest.mock import patch
from copy import deepcopy

from ipaddrs_state import diff_ipaddrs_states, save_ipaddrs_state

TEST_IPADDRS_STATE_PATH_NEW = "/tmp/ipaddrs_data_new.json"
TEST_IPADDRS_STATE_PATH_PREV = "/tmp/ipaddrs_data_prev.json"
SAMPLE_IPADDRS_DATA = {
    "dummy12": [
        "192.0.2.15", "192.0.2.33", "192.0.2.64", "2001:db8:0::ff:16",
        "2001:db8:0::ff:25", "2001:db8:0::ff:aa"
    ],
    "dummy13": [
        "192.0.2.88", "192.0.2.99", "192.0.2.126", "2001:db8:0::ff:2852",
        "2001:db8:0::ff:6407", "2001:db8:0::ff:dddd"
    ]
}


def test_save_ipaddrs_state():
    # stripped version of tt_main.system.get_addr_show output
    sys_addrs = {
        "dummy12": {
            "status": "BROADCAST,NOARP,UP,LOWER_UP",
            "mtu": "1500",
            "inet": {
                "192.0.2.15/32": {
                    "valid_lft": "forever",
                    "preferred_lft": "forever"
                },
                "192.0.2.33/32": {
                    "valid_lft": "forever",
                    "preferred_lft": "forever"
                },
                "192.0.2.64/32": {
                    "valid_lft": "forever",
                    "preferred_lft": "forever"
                }
            },
            "scope": "link",
            "inet6": {
                "2001:db8:0::ff:16/128": {
                    "valid_lft": "forever",
                    "preferred_lft": "forever"
                },
                "2001:db8:0::ff:aa/128": {
                    "valid_lft": "forever",
                    "preferred_lft": "forever"
                },
                "2001:db8:0::ff:25/128": {
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
            "mtu": "1500",
            "inet6": {
                "fe80::44b7:91ff:fe32:616b/64": {
                    "valid_lft": "forever",
                    "preferred_lft": "forever"
                },
                "2001:db8:0::ff:99/128": {
                    "valid_lft": "forever",
                    "preferred_lft": "forever"
                }
            },
            "scope": "link"
        }
    }
    with patch("ipaddrs_state.get_addr_show", return_value=sys_addrs):
        save_ipaddrs_state(TEST_IPADDRS_STATE_PATH_NEW)
    with open(TEST_IPADDRS_STATE_PATH_NEW, "r") as datafile:
        saved_data = json.load(datafile)
    assert len(saved_data) == 2
    assert len(saved_data["dummy12"]) == 6
    assert len(saved_data["dummy13"]) == 1
    assert "192.0.2.64" in saved_data["dummy12"]


def test_save_ipaddrs_state_empty():
    # stripped version of tt_main.system.get_addr_show output
    sys_addrs = {
        "dummy12": {
            "status": "BROADCAST,NOARP,UP,LOWER_UP",
            "mtu": "1500",
            "scope": "link",
            "inet6": {
                "fe80::4ce4:17ff:fe0b:4a75/64": {
                    "valid_lft": "forever",
                    "preferred_lft": "forever"
                }
            }
        },
        "dummy13": {
            "status": "BROADCAST,NOARP,UP,LOWER_UP",
            "mtu": "1500",
            "inet6": {
                "fe80::44b7:91ff:fe32:616b/64": {
                    "valid_lft": "forever",
                    "preferred_lft": "forever"
                }
            }
        }
    }
    with patch("ipaddrs_state.get_addr_show", return_value=sys_addrs):
        save_ipaddrs_state(TEST_IPADDRS_STATE_PATH_NEW)
    with open(TEST_IPADDRS_STATE_PATH_NEW, "r") as datafile:
        saved_data = json.load(datafile)
    assert not saved_data


def test_diff_ipaddrs_states_same():
    prev_data = deepcopy(SAMPLE_IPADDRS_DATA)
    with open(TEST_IPADDRS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    with open(TEST_IPADDRS_STATE_PATH_NEW, "w") as new_file:
        json.dump(prev_data, new_file)
    status, message = diff_ipaddrs_states(TEST_IPADDRS_STATE_PATH_PREV,
                                          TEST_IPADDRS_STATE_PATH_NEW)
    assert status == 0
    assert not message


def test_diff_ipaddrs_states_less_addresses():
    prev_data = deepcopy(SAMPLE_IPADDRS_DATA)
    with open(TEST_IPADDRS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    new_data = deepcopy(SAMPLE_IPADDRS_DATA)
    new_data["dummy12"].pop()
    new_data["dummy13"].pop(0)
    new_data["dummy13"].pop(0)
    with open(TEST_IPADDRS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)

    with patch("ipaddrs_state.IP_THRESHOLD_MIN", new=1):
        status, message = diff_ipaddrs_states(TEST_IPADDRS_STATE_PATH_PREV,
                                              TEST_IPADDRS_STATE_PATH_NEW)
    assert status == 1
    # IPs in brackets appears unsorted
    assert ("Less IPs found: dummy12 (2001:db8:0::ff:aa), "
            "dummy13 (192.0.2.") in message
    assert "192.0.2.88" in message
    assert "192.0.2.99" in message


def test_diff_ipaddrs_states_more_addresses():
    prev_data = deepcopy(SAMPLE_IPADDRS_DATA)
    with open(TEST_IPADDRS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    new_data = deepcopy(SAMPLE_IPADDRS_DATA)
    new_data["dummy13"].append("2001:db8:0::ff:a0a0")
    with open(TEST_IPADDRS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)

    status, message = diff_ipaddrs_states(TEST_IPADDRS_STATE_PATH_PREV,
                                          TEST_IPADDRS_STATE_PATH_NEW)
    assert status == 0
    assert message == ("More IPs found: dummy13 (2001:db8:0::ff:a0a0); "
                       "WAS=12 / FOUND=13 / NEW=1")


def test_diff_ipaddrs_states_more_and_less_addresses():
    prev_data = deepcopy(SAMPLE_IPADDRS_DATA)
    with open(TEST_IPADDRS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    new_data = deepcopy(SAMPLE_IPADDRS_DATA)
    new_data["dummy13"].append("2001:db8:0::ff:a0a0")
    new_data["dummy12"].pop()
    with open(TEST_IPADDRS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)

    status, message = diff_ipaddrs_states(TEST_IPADDRS_STATE_PATH_PREV,
                                          TEST_IPADDRS_STATE_PATH_NEW)
    assert status == 0  # threshold was not hit
    assert message == ("Less IPs found: dummy12 (2001:db8:0::ff:aa); "
                       "More IPs found: dummy13 (2001:db8:0::ff:a0a0); "
                       "WAS=12 / FOUND=12 / LOST=1 / NEW=1")


def test_less_ifaces():
    prev_data = deepcopy(SAMPLE_IPADDRS_DATA)
    with open(TEST_IPADDRS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    new_data = deepcopy(SAMPLE_IPADDRS_DATA)
    del new_data["dummy13"]
    with open(TEST_IPADDRS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)
    status, message = diff_ipaddrs_states(TEST_IPADDRS_STATE_PATH_PREV,
                                          TEST_IPADDRS_STATE_PATH_NEW)
    assert status == 1
    assert message == ("Some interfaces disappeared: dummy13; WAS=12 / "
                       "FOUND=6 / LOST=6")


def test_more_ifaces():
    prev_data = deepcopy(SAMPLE_IPADDRS_DATA)
    with open(TEST_IPADDRS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    new_data = deepcopy(SAMPLE_IPADDRS_DATA)
    new_data["dummy20"] = ["192.0.2.250", "2001:db8:0::ff:bb"]
    with open(TEST_IPADDRS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)
    status, message = diff_ipaddrs_states(TEST_IPADDRS_STATE_PATH_PREV,
                                          TEST_IPADDRS_STATE_PATH_NEW)
    assert status == 0
    assert message == ("New interfaces appears: dummy20; WAS=12 / FOUND=14 / "
                       "NEW=2")


def test_more_and_less_ifaces():
    prev_data = deepcopy(SAMPLE_IPADDRS_DATA)
    with open(TEST_IPADDRS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    new_data = deepcopy(SAMPLE_IPADDRS_DATA)
    del new_data["dummy13"]
    new_data["dummy20"] = ["192.0.2.250", "2001:db8:0::ff:bb"]
    with open(TEST_IPADDRS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)
    status, message = diff_ipaddrs_states(TEST_IPADDRS_STATE_PATH_PREV,
                                          TEST_IPADDRS_STATE_PATH_NEW)
    assert status == 1
    assert message == ("New interfaces appears: dummy20; "
                       "Some interfaces disappeared: dummy13; "
                       "WAS=12 / FOUND=8 / LOST=6 / NEW=2")

def test_less_ifaces_and_less_ips():
    prev_data = deepcopy(SAMPLE_IPADDRS_DATA)
    with open(TEST_IPADDRS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    new_data = deepcopy(SAMPLE_IPADDRS_DATA)
    new_data["dummy12"].pop()
    del new_data["dummy13"]
    with open(TEST_IPADDRS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)
    status, message = diff_ipaddrs_states(TEST_IPADDRS_STATE_PATH_PREV,
                                          TEST_IPADDRS_STATE_PATH_NEW)
    assert status == 1
    assert message == ("Some interfaces disappeared: dummy13; "
                       "Less IPs found: dummy12 (2001:db8:0::ff:aa); "
                       "WAS=12 / FOUND=5 / LOST=7")
