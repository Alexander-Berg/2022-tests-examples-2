import json
from copy import deepcopy
from unittest.mock import patch

import pytest
from bgp_state import BGPStateException, diff_bgp_states, save_bgp_state

TEST_BGP_STATE_PATH_NEW = "/tmp/bgp_data_new.json"
TEST_BGP_STATE_PATH_PREV = "/tmp/bgp_data_prev.json"
SAMPLE_BGP_V4_DATA = {
    "b_core_2": [
        "192.0.2.16/32",
        "198.51.100.4/32",
        "198.51.100.8/32",
        "198.51.100.16/32",
    ],
    "b_core_4": [
        "192.0.2.16/32",
        "198.51.100.4/32",
        "198.51.100.8/32",
        "198.51.100.16/32",
    ],
    "b_vrf_hbf_3": [],
    "b_vrf_hbf_5": []
}

SAMPLE_BGP_V6_DATA = {
    "b_core_2": [
        "2001:db8:ff::b14a/128",
        "2001:db8:cc::315/128",
        "2001:db8:cc::812/128",
        "2001:db8:cc::d4d/128",
    ],
    "b_core_4": [
        "2001:db8:ff::b14a/128",
        "2001:db8:cc::315/128",
        "2001:db8:cc::812/128",
        "2001:db8:cc::d4d/128",
    ],
    "b_vrf_hbf_3": [],
    "b_vrf_hbf_5": []
}


def test_bgp_state_saved_ok():
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[
                   deepcopy(SAMPLE_BGP_V4_DATA),
                   deepcopy(SAMPLE_BGP_V6_DATA)
               ]):
        save_bgp_state(TEST_BGP_STATE_PATH_NEW)
    with open(TEST_BGP_STATE_PATH_NEW, "r") as datafile:
        saved_data = json.load(datafile)
    assert len(saved_data) == 4
    assert "b_core_4" in saved_data
    assert "b_vrf_hbf_3" in saved_data
    assert len(saved_data["b_core_2"]) == 8
    assert "2001:db8:cc::812/128" in saved_data["b_core_4"]
    assert "192.0.2.16/32" in saved_data["b_core_2"]
    assert not saved_data["b_vrf_hbf_5"]


def test_bgp_state_no_sessions():
    with patch("bgp_state.get_bgp_grt_export", return_value={}):
        with pytest.raises(BGPStateException):
            save_bgp_state(TEST_BGP_STATE_PATH_NEW)
    with open(TEST_BGP_STATE_PATH_NEW, "r") as datafile:
        saved_data = json.load(datafile)
    assert not saved_data


def test_bgp_state_no_announcments():
    with patch("bgp_state.get_bgp_grt_export",
               return_value={
                   "b_core_2": [],
                   "b_core_4": []
               }):
        with pytest.raises(BGPStateException):
            save_bgp_state(TEST_BGP_STATE_PATH_NEW)
    with open(TEST_BGP_STATE_PATH_NEW, "r") as datafile:
        saved_data = json.load(datafile)
    assert len(saved_data) == 2
    assert "b_core_4" in saved_data
    assert not saved_data["b_core_4"]


def test_diff_bgp_states_no_diff():
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[
                   deepcopy(SAMPLE_BGP_V4_DATA),
                   deepcopy(SAMPLE_BGP_V6_DATA)
               ]):
        save_bgp_state(TEST_BGP_STATE_PATH_PREV)
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[
                   deepcopy(SAMPLE_BGP_V4_DATA),
                   deepcopy(SAMPLE_BGP_V6_DATA)
               ]):
        save_bgp_state(TEST_BGP_STATE_PATH_NEW)
    status, message = diff_bgp_states(TEST_BGP_STATE_PATH_PREV,
                                      TEST_BGP_STATE_PATH_NEW)
    assert status == 0
    assert not message


def test_diff_bgp_states_more_prefixes():
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[
                   deepcopy(SAMPLE_BGP_V4_DATA),
                   deepcopy(SAMPLE_BGP_V6_DATA)
               ]):
        save_bgp_state(TEST_BGP_STATE_PATH_PREV)
    changed_data = deepcopy(SAMPLE_BGP_V6_DATA)
    changed_data["b_core_2"].append("2001:db8:cc::4/128")
    changed_data["b_core_4"].append("2001:db8:cc::4/128")
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[deepcopy(SAMPLE_BGP_V4_DATA), changed_data]):
        save_bgp_state(TEST_BGP_STATE_PATH_NEW)
    status, message = diff_bgp_states(TEST_BGP_STATE_PATH_PREV,
                                      TEST_BGP_STATE_PATH_NEW)
    assert status == 0
    assert "b_core_4 has more prefixes:\n+\t2001:db8:cc::4/128" in message


def test_diff_bgp_states_less_prefixes_but_ok():
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[
                   deepcopy(SAMPLE_BGP_V4_DATA),
                   deepcopy(SAMPLE_BGP_V6_DATA)
               ]):
        save_bgp_state(TEST_BGP_STATE_PATH_PREV)
    with open(TEST_BGP_STATE_PATH_PREV, "r") as datafile:
        saved_data = json.load(datafile)
    assert "b_core_2" in saved_data
    assert len(saved_data["b_core_2"]) == 8
    changed_data = deepcopy(SAMPLE_BGP_V6_DATA)
    changed_data["b_core_2"].pop()
    changed_data["b_core_4"].pop()
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[deepcopy(SAMPLE_BGP_V4_DATA), changed_data]):
        save_bgp_state(TEST_BGP_STATE_PATH_NEW)
    with open(TEST_BGP_STATE_PATH_NEW, "r") as datafile:
        saved_data = json.load(datafile)
    assert "b_core_2" in saved_data
    assert len(saved_data["b_core_2"]) == 7
    status, message = diff_bgp_states(TEST_BGP_STATE_PATH_PREV,
                                      TEST_BGP_STATE_PATH_NEW)
    assert status == 0
    assert "b_core_2 has less prefixes:\n-\t2001:db8:cc::d4d/128" in message


def test_diff_bgp_states_less_prefixes_bad():
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[
                   deepcopy(SAMPLE_BGP_V4_DATA),
                   deepcopy(SAMPLE_BGP_V6_DATA)
               ]):
        save_bgp_state(TEST_BGP_STATE_PATH_PREV)
    changed_data = deepcopy(SAMPLE_BGP_V6_DATA)
    changed_data["b_core_2"].pop()
    changed_data["b_core_2"].pop()
    changed_data["b_core_4"].pop()
    changed_data["b_core_4"].pop()
    changed_data["b_core_4"].pop()
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[deepcopy(SAMPLE_BGP_V4_DATA), changed_data]):
        save_bgp_state(TEST_BGP_STATE_PATH_NEW)
    status, message = diff_bgp_states(TEST_BGP_STATE_PATH_PREV,
                                      TEST_BGP_STATE_PATH_NEW)
    assert status == 1
    assert "b_core_4 has less prefixes:\n-\t" in message
    assert "2001:db8:cc::812/128" in message
    assert "2001:db8:cc::d4d/128" in message


def test_diff_bgp_states_less_sessions():
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[
                   deepcopy(SAMPLE_BGP_V4_DATA),
                   deepcopy(SAMPLE_BGP_V6_DATA)
               ]):
        save_bgp_state(TEST_BGP_STATE_PATH_PREV)
    changed_v4_data = deepcopy(SAMPLE_BGP_V4_DATA)
    changed_v4_data.pop("b_core_2")
    changed_v6_data = deepcopy(SAMPLE_BGP_V6_DATA)
    changed_v6_data.pop("b_core_2")
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[changed_v4_data, changed_v6_data]):
        save_bgp_state(TEST_BGP_STATE_PATH_NEW)
    status, message = diff_bgp_states(TEST_BGP_STATE_PATH_PREV,
                                      TEST_BGP_STATE_PATH_NEW)
    assert status == 1
    assert "BGP session b_core_2 either became down or deleted" in message


def test_diff_bgp_states_less_and_more_prefixes():
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[
                   deepcopy(SAMPLE_BGP_V4_DATA),
                   deepcopy(SAMPLE_BGP_V6_DATA)
               ]):
        save_bgp_state(TEST_BGP_STATE_PATH_PREV)
    changed_data = deepcopy(SAMPLE_BGP_V6_DATA)
    changed_data["b_core_2"].pop()
    changed_data["b_core_4"].pop()
    changed_data["b_core_2"].append("198.51.100.253/32")
    changed_data["b_core_4"].append("198.51.100.253/32")
    with patch("bgp_state.get_bgp_grt_export",
               side_effect=[deepcopy(SAMPLE_BGP_V4_DATA), changed_data]):
        save_bgp_state(TEST_BGP_STATE_PATH_NEW)
    status, message = diff_bgp_states(TEST_BGP_STATE_PATH_PREV,
                                      TEST_BGP_STATE_PATH_NEW)
    assert status == 0
    assert "b_core_2 has less prefixes:\n-\t2001:db8:cc::d4d/128" in message
    assert "b_core_4 has additional prefixes:\n+\t198.51.100.253/32" in message
