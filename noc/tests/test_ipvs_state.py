import json
from copy import deepcopy
from unittest.mock import patch

import pytest
from ipvs_state import IPVSStateException, diff_ipvs_states, save_ipvs_state

TEST_IPVS_STATE_PATH_NEW = "/tmp/ipvs_data_new.json"
TEST_IPVS_STATE_PATH_PREV = "/tmp/ipvs_data_prev.json"
SAMPLE_IPVS_DATA = {
    "UDP  [2001:db8:cc::513]:53": 1,
    "TCP  198.51.100.16:443": 5,
    "TCP  [2001:db8:cc::812]:80": 0,
    "TCP  198.51.100.200:80": 60,
    "FWM  52587": 1002,
    "FWM  52587 IPv6": 1002
}


def test_save_ipvs_state():
    ipvs_data = [
        "IP Virtual Server version 1.2.1 (size=1048576)",
        "Prot LocalAddress:Port Scheduler Flags",
        "  -> RemoteAddress:Port         Forward Weight ActiveConn InActConn",
        "UDP  [2001:db8:cc::513]:53 wrr",
        "  -> [2001:db8:af:15::64d:32c]:53     Tunnel  1      0          0",
        "TCP  198.51.100.16:443 wrr",
        "  -> [2001:db8:af:62da::a5c2:18]:443  Tunnel  1      3          2",
        "  -> [2001:db8:af:15ee::a5c2:18]:443  Tunnel  1      6          2",
        "  -> [2001:db8:af:423a::a5c2:18]:443  Tunnel  1      8          2",
        "  -> [2001:db8:af:1110::a5c2:18]:443  Tunnel  1      5          2",
        "  -> [2001:db8:af:ff23::a5c2:18]:443  Tunnel  1      7          3",
        "TCP  [2001:db8:cc::812]:80 wrr", "FWM  52587 wrr",
        "  -> 203.0.113.5:0                    Tunnel  1000   0          2775",
        "  -> 203.0.113.22:0                   Tunnel  1      0          3",
        "  -> 203.0.113.101:0                  Tunnel  1      0          3",
        "FWM  52587 IPv6 wrr",
        "  -> [2001:db8:1542::4357:3f23]:0     Tunnel  1      3          1",
        "  -> [2001:db8:1542::2521:3a32]:0     Tunnel  1      3          1",
        "  -> [2001:db8:1542::8952:580e]:0     Tunnel  1000   1118       655"
    ]
    with patch("ipvs_state.make_cmd_call", return_value=ipvs_data):
        save_ipvs_state(TEST_IPVS_STATE_PATH_NEW)
    with open(TEST_IPVS_STATE_PATH_NEW, "r") as datafile:
        saved_data = json.load(datafile)
    assert len(saved_data) == 5
    assert saved_data["TCP  198.51.100.16:443"] == 5
    assert saved_data["UDP  [2001:db8:cc::513]:53"] == 1
    assert saved_data["TCP  [2001:db8:cc::812]:80"] == 0
    assert saved_data["FWM  52587"] == 1002
    assert saved_data["FWM  52587 IPv6"] == 1002


def test_save_ipvs_state_empty():
    ipvs_data = [
        "IP Virtual Server version 1.2.1 (size=1048576)",
        "Prot LocalAddress:Port Scheduler Flags",
        "  -> RemoteAddress:Port         Forward Weight ActiveConn InActConn"
    ]
    with patch("ipvs_state.make_cmd_call", return_value=ipvs_data):
        save_ipvs_state(TEST_IPVS_STATE_PATH_NEW)
    with open(TEST_IPVS_STATE_PATH_NEW, "r") as datafile:
        saved_data = json.load(datafile)
    assert not saved_data


def test_save_ipvs_state_impossible_syntax():
    ipvs_data = [
        "IP Virtual Server version 1.2.1 (size=1048576)",
        "Prot LocalAddress:Port Scheduler Flags",
        "  -> RemoteAddress:Port         Forward Weight ActiveConn InActConn",
        "UDP  [2001:db8:cc::513]:53 wrr",
        "  -> [2001:db8:af:15::64d:32c]:53     Tunnel  1      0          0",
        "TCP  198.51.100.16:443 wrr",
        "  -> [2001:db8:af:62da::a5c2:18]:443  Tunnel  Z!     3          2"
    ]
    with patch("ipvs_state.make_cmd_call", return_value=ipvs_data):
        with pytest.raises(IPVSStateException):
            save_ipvs_state(TEST_IPVS_STATE_PATH_NEW)


def test_diff_ipvs_states_same():
    prev_data = deepcopy(SAMPLE_IPVS_DATA)
    with open(TEST_IPVS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    with open(TEST_IPVS_STATE_PATH_NEW, "w") as new_file:
        json.dump(prev_data, new_file)
    status, message = diff_ipvs_states(TEST_IPVS_STATE_PATH_PREV,
                                       TEST_IPVS_STATE_PATH_NEW)
    assert status == 0
    assert not message


def test_diff_ipvs_states_vs_absent():
    prev_data = deepcopy(SAMPLE_IPVS_DATA)
    new_data = deepcopy(SAMPLE_IPVS_DATA)
    new_data.pop("FWM  52587")
    with open(TEST_IPVS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    with open(TEST_IPVS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)
    status, message = diff_ipvs_states(TEST_IPVS_STATE_PATH_PREV,
                                       TEST_IPVS_STATE_PATH_NEW)
    assert status == 1
    assert message == "VS disappear from IPVS data:\n-\tFWM  52587"


def test_diff_ipvs_states_new_vs_came():
    prev_data = deepcopy(SAMPLE_IPVS_DATA)
    new_data = deepcopy(SAMPLE_IPVS_DATA)
    new_data["UDP 198.51.100.77:22"] = 15
    with open(TEST_IPVS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    with open(TEST_IPVS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)
    status, message = diff_ipvs_states(TEST_IPVS_STATE_PATH_PREV,
                                       TEST_IPVS_STATE_PATH_NEW)
    assert status == 0
    assert message == "New VS appeared in IPVS data:\n+\tUDP 198.51.100.77:22"


def test_diff_ipvs_changes_small():
    prev_data = deepcopy(SAMPLE_IPVS_DATA)
    new_data = deepcopy(SAMPLE_IPVS_DATA)
    new_data["UDP  [2001:db8:cc::513]:53"] = 0
    new_data["TCP  198.51.100.16:443"] = 3
    new_data["TCP  [2001:db8:cc::812]:80"] = 1
    with open(TEST_IPVS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    with open(TEST_IPVS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)
    status, message = diff_ipvs_states(TEST_IPVS_STATE_PATH_PREV,
                                       TEST_IPVS_STATE_PATH_NEW)
    assert status == 0
    assert "TCP  198.51.100.16:443 OLD/NEW: 5 / 3" in message
    assert "UDP  [2001:db8:cc::513]:53 OLD/NEW: 1 / 0" in message
    assert "TCP  [2001:db8:cc::812]:80 OLD/NEW: 0 / 1" in message


def test_diff_ipvs_changes_big():
    prev_data = deepcopy(SAMPLE_IPVS_DATA)
    new_data = deepcopy(SAMPLE_IPVS_DATA)
    new_data["UDP  [2001:db8:cc::513]:53"] = 0
    new_data["TCP  198.51.100.16:443"] = 2
    new_data["TCP  198.51.100.200:80"] = 50
    with open(TEST_IPVS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    with open(TEST_IPVS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)
    status, message = diff_ipvs_states(TEST_IPVS_STATE_PATH_PREV,
                                       TEST_IPVS_STATE_PATH_NEW)
    assert status == 0
    assert "TCP  198.51.100.16:443 OLD/NEW: 5 / 2" in message
    assert "TCP  198.51.100.200:80 OLD/NEW: 60 / 50" in message
    assert "UDP  [2001:db8:cc::513]:53 OLD/NEW: 1 / 0" in message


def test_diff_ipvs_multiple_issues():
    prev_data = deepcopy(SAMPLE_IPVS_DATA)
    new_data = deepcopy(SAMPLE_IPVS_DATA)
    new_data["TCP  198.51.100.200:80"] = 50
    new_data.pop("FWM  52587")
    with open(TEST_IPVS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    with open(TEST_IPVS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)
    status, message = diff_ipvs_states(TEST_IPVS_STATE_PATH_PREV,
                                       TEST_IPVS_STATE_PATH_NEW)
    assert status == 1
    assert "TCP  198.51.100.200:80 OLD/NEW: 60 / 50" in message
    assert "VS disappear from IPVS data:\n-\tFWM  52587" in message


def test_diff_ipvs_states_vs_more_and_less():
    prev_data = deepcopy(SAMPLE_IPVS_DATA)
    new_data = deepcopy(SAMPLE_IPVS_DATA)
    new_data.pop("FWM  52587")
    new_data["UDP  198.51.100.16:443"] = 5
    with open(TEST_IPVS_STATE_PATH_PREV, "w") as old_file:
        json.dump(prev_data, old_file)
    with open(TEST_IPVS_STATE_PATH_NEW, "w") as new_file:
        json.dump(new_data, new_file)
    status, message = diff_ipvs_states(TEST_IPVS_STATE_PATH_PREV,
                                       TEST_IPVS_STATE_PATH_NEW)
    assert status == 1
    assert message == ("VS disappear from IPVS data:\n-\tFWM  52587\n"
                       "New VS appeared in IPVS data:\n+\tUDP  "
                       "198.51.100.16:443")
