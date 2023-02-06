import shelve
from pathlib import Path
from time import time
from unittest.mock import Mock, patch
from urllib.error import URLError

import pytest
from check_mac import check_macs_consistency, get_rt_macs, parse_rules, scan_udev_data
from tt_main.constants import CRIT_STATUS, OK_STATUS, WARN_STATUS

CACHE_FILES_PATH = "/tmp"
CACHE_FILES_PREFIX = "racktables_macs_cache"


@pytest.fixture
def clear_rt_cache():
    import os

    count = 0
    p = Path(CACHE_FILES_PATH)
    for _file in p.glob(f"{CACHE_FILES_PREFIX}_*"):
        os.remove(_file)
        count += 1
    return count


def test_parse_rules_no_file():
    with pytest.raises(OSError):
        parse_rules("/tmp/non_existent_file")


def test_parse_rules_ok(tmp_path):
    content = (
        'SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", '
        'ATTR{address}=="0c:42:a1:5a:43:5c", ATTR{dev_id}=="0x0", '
        'ATTR{type}=="1", NAME="eth0"\n'
        'SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", '
        'ATTR{address}=="0c:42:a1:5a:43:5d", ATTR{dev_id}=="0x0", '
        'ATTR{type}=="1", NAME="eth1"\n'
    )
    p = tmp_path / "fake_udev"
    p.write_text(content)
    res = parse_rules(filepath=p)
    assert len(res) == 2
    assert len(res[0]) == 7
    assert "SUBSYSTEM" in res[0]
    assert res[0]["ATTR{address}"] == "0c:42:a1:5a:43:5c"


def test_udev_empty_file(tmp_path):
    p = tmp_path / "fake_udev"
    p.write_text(" ")
    res = parse_rules(filepath=p)
    assert not res


def test_udev_incorrect_data(tmp_path):
    content = (
        'SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", '
        'ATTR{address}, ATTR{dev_id}=="0x0", '
        'ATTR{type}=="1", NAME="eth0"\n'
    )
    p = tmp_path / "fake_udev"
    p.write_text(content)
    res = parse_rules(filepath=p)
    assert len(res) == 1
    assert len(res[0]) == 6
    assert "ATTR{dev_id}" in res[0]


def test_udev_no_mac(tmp_path):
    content = (
        'SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", '
        'ATTR{address}=="", ATTR{dev_id}=="0x0", '
        'ATTR{type}=="1", NAME="eth0"\n'
    )
    p = tmp_path / "fake_udev"
    p.write_text(content)
    res = parse_rules(filepath=p)
    assert len(res) == 1
    assert len(res[0]) == 7
    assert not res[0]["ATTR{address}"]


def test_get_rt_macs_ok(clear_rt_cache):
    m = Mock()
    m.read.return_value = b"ip= mask= dmask= gateway= netaddr= bgp= mac=24:8a:07:b4:ec:6a"
    with patch("check_mac.urlopen", return_value=m):
        status, data = get_rt_macs(cache_path=CACHE_FILES_PATH)
    m.read.assert_called_once()
    assert status
    assert len(data) == 7
    assert not data["ip"]
    assert data["mac"] == "24:8a:07:b4:ec:6a"


def test_get_rt_macs_rt_unreachable(clear_rt_cache):
    with patch("check_mac.urlopen", side_effect=URLError("timed out")):
        status, data = get_rt_macs(cache_path=CACHE_FILES_PATH)
    assert not status
    assert "timed out" in str(data)


def test_get_rt_macs_junk_response(clear_rt_cache):
    m = Mock()
    m.read.return_value = b"ip== mask 10fjljzg gateway=netaddr= bgpmac=24:zzz"
    with patch("check_mac.urlopen", return_value=m):
        status, data = get_rt_macs(cache_path=CACHE_FILES_PATH)
    m.read.assert_called()
    assert not status
    assert "too many values" in str(data)

    m.read.return_value = b"mask 10fjljzg gateway=netaddr= bgpmac=24:zzz"
    with patch("check_mac.urlopen", return_value=m):
        status, data = get_rt_macs(cache_path=CACHE_FILES_PATH)
    m.read.assert_called()
    assert not status
    assert "not enough values" in str(data)


def test_get_rt_macs_empty_response(clear_rt_cache):
    m = Mock()
    m.read.return_value = b""
    with patch("check_mac.urlopen", return_value=m):
        status, data = get_rt_macs(cache_path=CACHE_FILES_PATH)
    m.read.assert_called_once()
    assert status
    assert not data


def test_get_rt_macs_fresh_cache_used(clear_rt_cache):
    m = Mock()
    m.read.return_value = b"ip= mask= dmask= gateway= netaddr= bgp= mac=24:8a:07:b4:ec:6a"
    with patch("check_mac.urlopen", return_value=m):
        status, data = get_rt_macs(cache_path=CACHE_FILES_PATH)
    m.read.assert_called_once()
    assert status

    with shelve.open(f"{CACHE_FILES_PATH}/{CACHE_FILES_PREFIX}_eth0", flag="r") as cached_data:
        data = cached_data["eth0"]
    assert "mac" in data
    assert data["mac"] == "24:8a:07:b4:ec:6a"

    m = Mock()
    m.read.return_value = b""
    with patch("check_mac.urlopen", return_value=m):
        status, data = get_rt_macs(cache_path=CACHE_FILES_PATH)
    m.read.assert_not_called()
    assert status
    assert len(data) == 7
    assert data["mac"] == "24:8a:07:b4:ec:6a"


def test_get_rt_macs_stale_cache_ignored(clear_rt_cache):
    data = {"ip": "", "mask": "", "mac": "00:00:52:aa:bb:cc"}
    with shelve.open(f"{CACHE_FILES_PATH}/{CACHE_FILES_PREFIX}_eth0") as cached_data:
        cached_data["eth0"] = data
    m = Mock()
    m.read.return_value = b"ip= mask= dmask= gateway= netaddr= bgp= mac=24:8a:07:b4:ec:6a"
    p1 = patch("tt_main.utils.time.time", return_value=time() + 10000)
    p2 = patch("check_mac.urlopen", return_value=m)
    p1.start()
    p2.start()
    status, data = get_rt_macs(cache_path=CACHE_FILES_PATH)
    m.read.assert_called_once()
    assert status
    assert len(data) == 7
    assert not data["ip"]
    assert data["mac"] == "24:8a:07:b4:ec:6a"


def test_scan_udev_data_ok():
    data = [
        {"NAME": "eth0", "ATTR{address}": "00:00:52:cc:dd:ee"},
        {"NAME": "eth1", "ATTR{address}": "00:00:52:ff:ff:cc"},
    ]
    status, msg = scan_udev_data("eth1", "00:00:52:ff:ff:cc", data)
    assert status
    assert not msg


def test_scan_udev_data_no_mac():
    data = [{"NAME": "eth0", "ATTR{address}": "00:00:52:cc:dd:ee"}, {"NAME": "eth1"}]
    status, msg = scan_udev_data("eth1", "00:00:52:ff:ff:cc", data)
    assert not status
    assert msg == "eth1 MAC not found in udev"


def test_scan_udev_data_no_iface():
    data = [{"NAME": "eth0", "ATTR{address}": "00:00:52:cc:dd:ee"}]
    status, msg = scan_udev_data("eth1", "00:00:52:ff:ff:cc", data)
    assert not status
    assert msg == "can not find eth1 in udev"


def test_scan_udev_mac_diff():
    data = [
        {"NAME": "eth0", "ATTR{address}": "00:00:52:cc:dd:ee"},
        {"NAME": "eth1", "ATTR{address}": "00:00:52:dd:ff:cc"},
    ]
    status, msg = scan_udev_data("eth1", "00:00:52:ff:ff:cc", data)
    assert not status
    assert "different MAC between udev file and state" in msg


def test_check_macs_consistency_ok():
    ip_addr_data = {
        "dummy0": {
            "state": "UP",
            "mtu": "1500",
            "link/ether": "00:00:52:ff:ff:ff",
        },
        "eth0": {
            "inet": {"37.9.102.104/27": {"preferred_lft": "forever", "valid_lft": "forever"}},
            "link/ether": "90:e2:ba:4a:ca:e5",
            "mtu": "9000",
            "state": "UP",
        },
    }
    udev_data = [
        {"NAME": "eth0", "ATTR{address}": "90:e2:ba:4a:ca:e5"},
        {"NAME": "eth1", "ATTR{address}": "00:00:52:dd:ff:cc"},
    ]
    rt_data = {"ip": "37.9.102.104", "mac": "90:e2:ba:4a:ca:e5"}
    with patch("check_mac.get_rt_macs", return_value=(True, rt_data)):
        status, msg = check_macs_consistency(ip_addr_data, udev_data)
    assert status == OK_STATUS
    assert msg == "OK"


def test_check_macs_consistency_empty_ip_addr():
    status, msg = check_macs_consistency({}, [])
    assert status == CRIT_STATUS
    assert msg == "empty ip addr show?"


def test_check_macs_consistency_no_eth():
    ip_addr_data = {
        "dummy0": {
            "state": "UP",
            "mtu": "1500",
            "link/ether": "00:00:52:ff:ff:ff",
        },
        "eth0.1600": {
            "state": "UP",
            "mtu": "1500",
            "link/ether": "00:00:52:ff:aa:ff",
        },
    }
    status, msg = check_macs_consistency(ip_addr_data, [])
    assert status == CRIT_STATUS
    assert msg == "ip addr data has 0 eth interfaces"


def test_check_macs_consistency_down_int_ignored():
    ip_addr_data = {
        "eth0": {
            "inet": {"37.9.102.104/27": {"preferred_lft": "forever", "valid_lft": "forever"}},
            "link/ether": "90:e2:ba:4a:ca:e5",
            "mtu": "9000",
            "state": "DOWN",
        },
    }
    udev_data = [
        {"NAME": "eth0", "ATTR{address}": "90:e2:ba:4a:ca:e5"},
        {"NAME": "eth1", "ATTR{address}": "00:00:52:dd:ff:cc"},
    ]
    rt_data = {"ip": "37.9.102.104", "mac": "00:ff:ff:ff:ff:ff"}
    with patch("check_mac.get_rt_macs", return_value=(True, rt_data)):
        status, msg = check_macs_consistency(ip_addr_data, udev_data)
    assert status == OK_STATUS
    assert msg == "OK"


def test_check_macs_consistency_rt_timeout():
    ip_addr_data = {
        "eth0": {
            "inet": {"37.9.102.104/27": {"preferred_lft": "forever", "valid_lft": "forever"}},
            "link/ether": "90:e2:ba:4a:ca:e5",
            "mtu": "9000",
            "state": "UP",
        },
    }
    udev_data = [
        {"NAME": "eth0", "ATTR{address}": "90:e2:ba:4a:ca:e5"},
        {"NAME": "eth1", "ATTR{address}": "00:00:52:dd:ff:cc"},
    ]
    with patch("check_mac.get_rt_macs", return_value=(False, "timeout")):
        status, msg = check_macs_consistency(ip_addr_data, udev_data)
    assert status == CRIT_STATUS
    assert "can not get RT info about eth0" in msg


def test_check_macs_consistency_rt_no_mac():
    ip_addr_data = {
        "eth0": {
            "inet": {"37.9.102.104/27": {"preferred_lft": "forever", "valid_lft": "forever"}},
            "link/ether": "90:e2:ba:4a:ca:e5",
            "mtu": "9000",
            "state": "UP",
        },
    }
    udev_data = [
        {"NAME": "eth0", "ATTR{address}": "90:e2:ba:4a:ca:e5"},
        {"NAME": "eth1", "ATTR{address}": "00:00:52:dd:ff:cc"},
    ]
    rt_data = {"ip": "37.9.102.104"}
    with patch("check_mac.get_rt_macs", return_value=(True, rt_data)):
        status, msg = check_macs_consistency(ip_addr_data, udev_data)
    assert status == CRIT_STATUS
    assert msg == "RT not returns MAC for eth0"


def test_check_macs_consistency_rt_mac_diff():
    ip_addr_data = {
        "eth0": {
            "inet": {"37.9.102.104/27": {"preferred_lft": "forever", "valid_lft": "forever"}},
            "link/ether": "90:e2:ba:4a:ca:e5",
            "mtu": "9000",
            "state": "UP",
        },
    }
    udev_data = [
        {"NAME": "eth0", "ATTR{address}": "90:e2:ba:4a:ca:e5"},
        {"NAME": "eth1", "ATTR{address}": "00:00:52:dd:ff:cc"},
    ]
    rt_data = {"ip": "37.9.102.104", "mac": "00:ff:ff:ff:ff:ff"}
    with patch("check_mac.get_rt_macs", return_value=(True, rt_data)):
        status, msg = check_macs_consistency(ip_addr_data, udev_data)
    assert status == CRIT_STATUS
    assert "RT MAC and real MAC are different" in msg


def test_check_macs_consistency_udev_mac_diff():
    ip_addr_data = {
        "eth0": {
            "inet": {"37.9.102.104/27": {"preferred_lft": "forever", "valid_lft": "forever"}},
            "link/ether": "90:e2:ba:4a:ca:e5",
            "mtu": "9000",
            "state": "UP",
        },
    }
    udev_data = [
        {"NAME": "eth0", "ATTR{address}": "90:e2:ba:4a:cc:ff"},
        {"NAME": "eth1", "ATTR{address}": "00:00:52:dd:ff:cc"},
    ]
    rt_data = {"ip": "37.9.102.104", "mac": "90:e2:ba:4a:ca:e5"}
    with patch("check_mac.get_rt_macs", return_value=(True, rt_data)):
        status, msg = check_macs_consistency(ip_addr_data, udev_data)
    assert status == CRIT_STATUS
    assert "different MAC between udev file and state" in msg


def test_check_macs_consistency_multiple_problems():
    ip_addr_data = {
        "dummy255": {
            "state": "UP",
            "mtu": "1500",
            "link/ether": "00:00:52:ff:ff:ff",
        },
        "eth0": {
            "inet": {"37.9.102.104/27": {"preferred_lft": "forever", "valid_lft": "forever"}},
            "link/ether": "90:e2:ba:4a:ca:e5",
            "mtu": "9000",
            "state": "UP",
        },
        "eth1": {
            "inet": {"37.9.108.112/27": {"preferred_lft": "forever", "valid_lft": "forever"}},
            "link/ether": "90:e2:ba:4a:ca:e6",
            "mtu": "9000",
            "state": "UP",
        },
        "eth2": {
            "link/ether": "00:25:bb:cc:01:01",
            "mtu": "9000",
            "state": "UP",
        },
        "eth3": {
            "link/ether": "00:25:bb:cc:01:02",
            "mtu": "9000",
            "state": "DOWN",
        },
    }
    udev_data = [
        {"NAME": "eth0", "ATTR{address}": "90:e2:ba:4a:ca:e5"},
        {"NAME": "eth1", "ATTR{address}": "90:e3:ba:4a:ca:e6"},
        {"NAME": "eth2", "ATTR{address}": "00:25:bb:cc:01:01"},
        {"NAME": "eth3", "ATTR{address}": "00:25:bb:cc:01:02"},
    ]
    rt_data = [
        (True, {"ip": "37.9.102.104", "mac": "90:e2:ba:4a:ca:e5"}),
        (True, {"ip": "37.9.108.112", "mac": "90:e2:ba:4a:ca:e6"}),
        (True, {"mac": "00:25:bb:cc:0f:01"}),
        (True, {"mac": "00:25:bb:cc:0f:02"}),
    ]
    with patch("check_mac.get_rt_macs", side_effect=rt_data):
        status, msg = check_macs_consistency(ip_addr_data, udev_data)
    assert status == CRIT_STATUS
    assert "different MAC between udev file and state on eth1" in msg
    assert "RT MAC and real MAC are different, int=eth2" in msg
