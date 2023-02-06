import ipaddress
import shelve
from pathlib import Path
from time import time
from unittest.mock import Mock, patch
from urllib.error import URLError

import pytest
from svc_announced import (
    check_svcs_announced,
    get_bgp_grt_export,
    get_system_addresses_as_prefixes,
    is_subnet_of,
    resolve_macro,
)
from tt_main.constants import CRIT_STATUS, OK_STATUS, WARN_STATUS

CACHE_FILE = "/tmp/svc_announced_macro_cache"
TEST_MACRO = "_SLBSUPERNETS_"
TEST_PFX = "2a02:6b8:0:3400::/64"


@pytest.fixture
def clear_hbf_cache():
    import os

    p = Path(f"{CACHE_FILE}.db")
    try:
        os.remove(p)
        return True
    except OSError:
        return False
    return False


def test_resolve_macro_ig(clear_hbf_cache):
    assert ipaddress.ip_network(TEST_PFX) in resolve_macro(TEST_MACRO, CACHE_FILE)
    assert Path(f"{CACHE_FILE}.db").exists()


def test_resolve_macro_ok(clear_hbf_cache):
    m = Mock()
    m.read.return_value = b"2a02:6b8::/64\n2a02:6b8:0:1::/64\n2a02:6b8:0:3400::/64\n2a02:6b8:4::/48\n2a02:6b8:6::/48"
    with patch("svc_announced.urlopen", return_value=m):
        pfxs = resolve_macro(TEST_MACRO, CACHE_FILE)
    m.read.assert_called_once()
    assert ipaddress.ip_network(TEST_PFX) in pfxs


def test_resolve_macro_empty_response(clear_hbf_cache):
    m = Mock()
    m.read.return_value = b""
    with patch("svc_announced.urlopen", return_value=m):
        pfxs = resolve_macro(TEST_MACRO, CACHE_FILE)
    m.read.assert_called_once()
    assert not pfxs


def test_resolve_macro_junk_response(clear_hbf_cache):
    m = Mock()
    m.read.return_value = b"2a02:6b8::/64\n2a02:6b8:0:1::/64\n2a02:6b8:0:3400::/64\n2a02:6b8:z::/48\nsome junk"
    with patch("svc_announced.urlopen", return_value=m):
        pfxs = resolve_macro(TEST_MACRO, CACHE_FILE)
    m.read.assert_called_once()
    assert ipaddress.ip_network(TEST_PFX) in pfxs


def test_resolve_macro_no_response(clear_hbf_cache):
    with patch("svc_announced.urlopen", side_effect=URLError("timeout")):
        with pytest.raises(URLError):
            resolve_macro(TEST_MACRO, CACHE_FILE)


def test_resolve_macro_fresh_cache_used(clear_hbf_cache):
    m = Mock()
    m.read.return_value = b"2a02:6b8::/64\n2a02:6b8:0:1::/64\n2a02:6b8:0:3400::/64\n2a02:6b8:4::/48\n2a02:6b8:6::/48"
    with patch("svc_announced.urlopen", return_value=m):
        resolve_macro(TEST_MACRO, CACHE_FILE)
    m.read.assert_called_once()

    with shelve.open(CACHE_FILE, flag="r") as cache_db:
        assert ipaddress.ip_network(TEST_PFX) in cache_db["pfxs"]

    r = Mock()
    r.read.return_value = b""
    with patch("svc_announced.urlopen", return_value=r):
        pfxs = resolve_macro(TEST_MACRO, CACHE_FILE)
    r.read.assert_not_called()
    assert ipaddress.ip_network(TEST_PFX) in pfxs


def test_resolve_macro_stale_cache_ignored(clear_hbf_cache):
    with shelve.open(CACHE_FILE) as cache_db:
        cache_db["pfxs"] = [ipaddress.ip_network("2a02:6b8:0:1::/64"), ipaddress.ip_network("2a02:6b8:0:4::/64")]
    m = Mock()
    m.read.return_value = b"2a02:6b8::/64\n2a02:6b8:0:1::/64\n2a02:6b8:0:3400::/64\n2a02:6b8:4::/48\n2a02:6b8:6::/48"
    p1 = patch("tt_main.utils.time.time", return_value=time() + 100000)
    p2 = patch("svc_announced.urlopen", return_value=m)
    p1.start()
    p2.start()
    pfxs = resolve_macro(TEST_MACRO, CACHE_FILE)
    m.read.assert_called_once()
    assert ipaddress.ip_network(TEST_PFX) in pfxs


def test_get_bgp_grt_export_two_v4():
    v4_protos = [
        "BIRD 1.6.8 ready.",
        "direct0  Direct   master   up     2020-10-27",
        "kernel1  Kernel   master   up     2020-10-27",
        "device1  Device   master   up     2020-10-27",
        "b_core_2 BGP      master   up     2020-12-15  Established",
        "b_core_4 BGP      master   up     2020-10-27  Established",
        "b_bfd    BFD      master   up     2020-10-27",
    ]
    v4_c1_export = [
        "BIRD 1.6.8 ready.",
        "213.180.205.242/32 dev dummy12 [direct12 2020-12-22] * (1100)",
        "5.45.202.158/32    dev dummy12 [direct12 2020-12-14] * (1100)",
        "141.8.146.207/32   dev dummy12 [direct12 2020-12-22] * (1100)",
        "213.180.205.243/32 dev dummy12 [direct12 2020-12-14] * (1100)",
        "213.180.193.48/32  dev dummy12 [direct12 2020-12-22] * (1100)",
    ]
    v4_c2_export = v4_c1_export
    with patch("svc_announced.system.make_cmd_call", side_effect=[v4_protos, v4_c1_export, v4_c2_export]):
        bgp_data = get_bgp_grt_export("birdc")
    assert len(bgp_data) == 2
    assert "b_core_2" in bgp_data
    assert ipaddress.ip_network("5.45.202.158/32") in bgp_data["b_core_2"]
    assert ipaddress.ip_network("5.45.202.158/32") in bgp_data["b_core_4"]


def test_get_bgp_grt_export_two_v6():
    v6_protos = [
        "BIRD 1.6.8 ready.",
        "direct0  Direct   master   up     2020-10-27",
        "kernel1  Kernel   master   up     2020-10-27",
        "device1  Device   master   up     2020-10-27",
        "b_core_2 BGP      master   up     2020-12-15  Established",
        "b_vrf_hbf_3 BGP      master   up     2020-12-15  Established",
        "b_core_4 BGP      master   up     2020-10-27  Established",
        "b_vrf_hbf_5 BGP      master   up     2020-10-27  Established",
        "b_bfd    BFD      master   up     2020-10-27",
    ]
    v6_c1_export = [
        "BIRD 1.6.8 ready.",
        "2a02:6b8:0:300::2b4a/128 dev dummy255 [direct255 2020-10-27] * (2000)",
        "2a02:6b8:0:3400:0:bd7:0:2/128 dev dummy12 [direct12 2020-12-21] * (1100)",
        "2a02:6b8:0:3400:0:9b9:0:1/128 dev dummy12 [direct12 2020-10-27] * (1100)",
        "2a02:6b8:0:3400:0:9da:0:1/128 dev dummy12 [direct12 2020-12-16] * (1100)",
        "2a02:6b8:0:3400:0:e4c:0:3/128 dev dummy12 [direct12 2020-12-18] * (1100)",
        "2a02:6b8:0:3400:0:e4c:0:1/128 dev dummy12 [direct12 2020-12-18] * (1100)",
        "2a02:6b8:0:3400:0:3c9:0:141/128 dev dummy12 [direct12 2020-10-27] * (1100)",
    ]
    v6_c2_export = v6_c1_export
    with patch("svc_announced.system.make_cmd_call", side_effect=[v6_protos, v6_c1_export, v6_c2_export]):
        bgp_data = get_bgp_grt_export("birdc6")
    assert len(bgp_data) == 2
    assert "b_core_2" in bgp_data
    assert ipaddress.ip_network("2a02:6b8:0:3400:0:bd7:0:2/128") in bgp_data["b_core_2"]
    assert ipaddress.ip_network("2a02:6b8:0:300::2b4a/128") in bgp_data["b_core_4"]


def test_get_bgp_grt_export_v4_no_bgp():
    v4_protos = [
        "BIRD 1.6.8 ready.",
        "direct0  Direct   master   up     2020-10-27",
        "kernel1  Kernel   master   up     2020-10-27",
        "device1  Device   master   up     2020-10-27",
    ]
    with patch("svc_announced.system.make_cmd_call", return_value=v4_protos):
        bgp_data = get_bgp_grt_export("birdc")
    assert len(bgp_data) == 0


def test_get_bgp_grt_export_v4_no_protocols():
    v4_protos = [
        "BIRD 1.6.8 ready.",
    ]
    with patch("svc_announced.system.make_cmd_call", return_value=v4_protos):
        bgp_data = get_bgp_grt_export("birdc")
    assert len(bgp_data) == 0


def test_get_bgp_grt_export_v4_no_export():
    v4_protos = [
        "BIRD 1.6.8 ready.",
        "direct0  Direct   master   up     2020-10-27",
        "kernel1  Kernel   master   up     2020-10-27",
        "device1  Device   master   up     2020-10-27",
        "b_core_2 BGP      master   up     2020-12-15  Established",
        "b_core_4 BGP      master   up     2020-10-27  Established",
        "b_bfd    BFD      master   up     2020-10-27",
    ]
    v4_c1_export = [
        "BIRD 1.6.8 ready.",
    ]
    v4_c2_export = v4_c1_export
    with patch("svc_announced.system.make_cmd_call", side_effect=[v4_protos, v4_c1_export, v4_c2_export]):
        bgp_data = get_bgp_grt_export("birdc")
    assert len(bgp_data) == 2
    assert "b_core_4" in bgp_data
    assert len(bgp_data["b_core_4"]) == 0


def test_get_bgp_grt_export_one_session_down():
    v6_protos = [
        "BIRD 1.6.8 ready.",
        "direct0  Direct   master   up     2020-10-27",
        "kernel1  Kernel   master   up     2020-10-27",
        "device1  Device   master   up     2020-10-27",
        "b_core_2 BGP      master   up     2020-12-15  Established",
        "b_vrf_hbf_3 BGP      master   up     2020-12-15  Established",
        "b_core_4 BGP      master   start     2020-10-27  Active",
        "b_vrf_hbf_5 BGP      master   up     2020-10-27  Established",
        "b_bfd    BFD      master   up     2020-10-27",
    ]
    v6_c1_export = [
        "BIRD 1.6.8 ready.",
        "2a02:6b8:0:300::2b4a/128 dev dummy255 [direct255 2020-10-27] * (2000)",
        "2a02:6b8:0:3400:0:bd7:0:2/128 dev dummy12 [direct12 2020-12-21] * (1100)",
        "2a02:6b8:0:3400:0:9b9:0:1/128 dev dummy12 [direct12 2020-10-27] * (1100)",
        "2a02:6b8:0:3400:0:9da:0:1/128 dev dummy12 [direct12 2020-12-16] * (1100)",
        "2a02:6b8:0:3400:0:e4c:0:3/128 dev dummy12 [direct12 2020-12-18] * (1100)",
        "2a02:6b8:0:3400:0:e4c:0:1/128 dev dummy12 [direct12 2020-12-18] * (1100)",
        "2a02:6b8:0:3400:0:3c9:0:141/128 dev dummy12 [direct12 2020-10-27] * (1100)",
    ]
    v6_c2_export = ["BIRD 1.6.8 ready.", "Protocol is down"]

    with patch("svc_announced.system.make_cmd_call", side_effect=[v6_protos, v6_c1_export, v6_c2_export]):
        bgp_data = get_bgp_grt_export("birdc6")
    assert len(bgp_data) == 1
    assert "b_core_2" in bgp_data
    assert ipaddress.ip_network("2a02:6b8:0:3400:0:bd7:0:2/128") in bgp_data["b_core_2"]


def test_get_system_addresses():
    sys_addrs = {
        "dummy12": {
            "status": "BROADCAST,NOARP,UP,LOWER_UP",
            "mtu": "1500",
            "qdisc": "noqueue",
            "state": "UNKNOWN",
            "group": "default",
            "qlen": "1000",
            "link/ether": "4e:e4:17:0b:4a:75",
            "brd": "ff:ff:ff:ff:ff:ff",
            "inet": {
                "5.255.240.205/32": {"valid_lft": "forever", "preferred_lft": "forever"},
                "93.158.157.215/32": {"valid_lft": "forever", "preferred_lft": "forever"},
                "213.180.193.47/32": {"valid_lft": "forever", "preferred_lft": "forever"},
            },
            "scope": "link",
            "inet6": {
                "2a02:6b8:0:3400:0:7cc:0:2/128": {"valid_lft": "forever", "preferred_lft": "forever"},
                "2a02:6b8:0:3400::1:225/128": {"valid_lft": "forever", "preferred_lft": "forever"},
                "2a02:6b8:0:3400:0:1c1:0:1/128": {"valid_lft": "forever", "preferred_lft": "forever"},
                "fe80::4ce4:17ff:fe0b:4a75/64": {"valid_lft": "forever", "preferred_lft": "forever"},
            },
        },
        "dummy13": {
            "status": "BROADCAST,NOARP,UP,LOWER_UP",
            "mtu": "1500",
            "qdisc": "noqueue",
            "state": "UNKNOWN",
            "group": "default",
            "qlen": "1000",
            "link/ether": "46:b7:91:32:61:6b",
            "brd": "ff:ff:ff:ff:ff:ff",
            "inet6": {"fe80::44b7:91ff:fe32:616b/64": {"valid_lft": "forever", "preferred_lft": "forever"}},
            "scope": "link",
        },
    }
    with patch("svc_announced.system.get_addr_show", return_value=sys_addrs):
        result = get_system_addresses_as_prefixes()
    assert len(result) == 7
    assert ipaddress.ip_network("2a02:6b8:0:3400:0:1c1:0:1/128") in result


def test_check_svcs_announced_ok():
    patch1 = patch(
        "svc_announced.resolve_macro",
        return_value=[ipaddress.ip_network(TEST_PFX), ipaddress.ip_network("87.250.250.0/24")],
    )
    patch2 = patch(
        "svc_announced.get_bgp_grt_export",
        side_effect=[
            {
                "b_core_2": [
                    ipaddress.ip_network("92.254.254.1/32"),
                    ipaddress.ip_network("87.250.250.3/32"),
                    ipaddress.ip_network("87.250.250.15/32"),
                    ipaddress.ip_network("87.250.250.66/32"),
                ],
                "b_core_4": [
                    ipaddress.ip_network("92.254.254.1/32"),
                    ipaddress.ip_network("87.250.250.3/32"),
                    ipaddress.ip_network("87.250.250.15/32"),
                    ipaddress.ip_network("87.250.250.66/32"),
                ],
            },
            {
                "b_core_2": [
                    ipaddress.ip_network("2a02:6b8:0:ff::1/128"),
                    ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
                    ipaddress.ip_network("2a02:6b8:0:3400::af/128"),
                ],
                "b_core_4": [
                    ipaddress.ip_network("2a02:6b8:0:ff::1/128"),
                    ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
                    ipaddress.ip_network("2a02:6b8:0:3400::af/128"),
                ],
            },
        ],
    )
    patch3 = patch(
        "svc_announced.get_system_addresses_as_prefixes",
        return_value={
            ipaddress.ip_network("92.254.254.1/32"),
            ipaddress.ip_network("2a02:6b8:0:ff::1/128"),
            ipaddress.ip_network("87.250.250.3/32"),
            ipaddress.ip_network("87.250.250.15/32"),
            ipaddress.ip_network("87.250.250.66/32"),
            ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
            ipaddress.ip_network("2a02:6b8:0:3400::af/128"),
            ipaddress.ip_network("92.150.16.0/26"),
        },
    )
    patch1.start()
    patch2.start()
    patch3.start()
    status, message = check_svcs_announced()
    assert status == OK_STATUS
    assert message == "OK"


def test_check_svcs_announced_different_export():
    bgp_data = [
        {
            "b_core_2": [
                ipaddress.ip_network("87.250.250.3/32"),
                ipaddress.ip_network("87.250.250.15/32"),
                ipaddress.ip_network("87.250.250.66/32"),
            ],
            "b_core_4": [ipaddress.ip_network("87.250.250.15/32"), ipaddress.ip_network("87.250.250.66/32")],
        },
        {
            "b_core_2": [
                ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
            ],
            "b_core_4": [
                ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
                ipaddress.ip_network("2a02:6b8:0:3400::af/128"),
            ],
        },
    ]
    with patch("svc_announced.get_bgp_grt_export", side_effect=bgp_data):
        status, message = check_svcs_announced()
    assert status == CRIT_STATUS
    assert "route exports differ" in message


def test_check_svcs_announced_some_prefixes_not_announced():
    patch1 = patch(
        "svc_announced.resolve_macro",
        return_value=[ipaddress.ip_network(TEST_PFX), ipaddress.ip_network("87.250.250.0/24")],
    )
    patch2 = patch(
        "svc_announced.get_bgp_grt_export",
        side_effect=[
            {
                "b_core_2": [
                    ipaddress.ip_network("92.254.254.1/32"),
                    ipaddress.ip_network("87.250.250.3/32"),
                    ipaddress.ip_network("87.250.250.66/32"),
                ],
                "b_core_4": [
                    ipaddress.ip_network("92.254.254.1/32"),
                    ipaddress.ip_network("87.250.250.3/32"),
                    ipaddress.ip_network("87.250.250.66/32"),
                ],
            },
            {
                "b_core_2": [
                    ipaddress.ip_network("2a02:6b8:0:ff::1/128"),
                    ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
                ],
                "b_core_4": [
                    ipaddress.ip_network("2a02:6b8:0:ff::1/128"),
                    ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
                ],
            },
        ],
    )
    patch3 = patch(
        "svc_announced.get_system_addresses_as_prefixes",
        return_value={
            ipaddress.ip_network("92.254.254.1/32"),
            ipaddress.ip_network("2a02:6b8:0:ff::1/128"),
            ipaddress.ip_network("87.250.250.3/32"),
            ipaddress.ip_network("87.250.250.15/32"),
            ipaddress.ip_network("87.250.250.66/32"),
            ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
            ipaddress.ip_network("2a02:6b8:0:3400::af/128"),
            ipaddress.ip_network("92.150.16.0/26"),
        },
    )
    patch1.start()
    patch2.start()
    patch3.start()
    status, message = check_svcs_announced()
    assert status == CRIT_STATUS
    assert "87.250.250.15/32" in message
    assert "2a02:6b8:0:3400::af/128" in message


def test_check_svcs_announced_hbf_fail():
    patch1 = patch("svc_announced.resolve_macro", side_effect=URLError("timeout"))
    patch2 = patch(
        "svc_announced.get_bgp_grt_export",
        side_effect=[
            {
                "b_core_2": [ipaddress.ip_network("87.250.250.3/32"), ipaddress.ip_network("87.250.250.66/32")],
                "b_core_4": [ipaddress.ip_network("87.250.250.3/32"), ipaddress.ip_network("87.250.250.66/32")],
            },
            {
                "b_core_2": [
                    ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
                ],
                "b_core_4": [
                    ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
                ],
            },
        ],
    )
    patch1.start()
    patch2.start()
    status, message = check_svcs_announced()
    assert status == CRIT_STATUS
    assert "timeout" in message


def test_check_svcs_announced_too_little_exports():
    patch1 = patch(
        "svc_announced.resolve_macro",
        return_value=[ipaddress.ip_network(TEST_PFX), ipaddress.ip_network("87.250.250.0/24")],
    )
    patch2 = patch(
        "svc_announced.get_bgp_grt_export",
        side_effect=[
            {
                "b_core_2": [
                    ipaddress.ip_network("92.250.250.15/32"),
                ],
                "b_core_4": [
                    ipaddress.ip_network("92.250.250.15/32"),
                ],
            },
            {
                "b_core_2": [
                    ipaddress.ip_network("2a02:6b8:0:f::aa/128"),
                ],
                "b_core_4": [
                    ipaddress.ip_network("2a02:6b8:0:f::aa/128"),
                ],
            },
        ],
    )
    patch3 = patch(
        "svc_announced.get_system_addresses_as_prefixes",
        return_value={
            ipaddress.ip_network("92.254.254.1/32"),
            ipaddress.ip_network("2a02:6b8:0:ff::1/128"),
            ipaddress.ip_network("87.250.250.3/32"),
            ipaddress.ip_network("92.250.250.15/32"),
            ipaddress.ip_network("87.250.250.66/32"),
            ipaddress.ip_network("2a02:6b8:0:f::aa/128"),
            ipaddress.ip_network("2a02:6b8:0:3400::af/128"),
            ipaddress.ip_network("92.150.16.0/26"),
        },
    )
    patch1.start()
    patch2.start()
    patch3.start()
    status, message = check_svcs_announced()
    assert status == WARN_STATUS
    assert message == "announces disabled?"


def test_check_svcs_announced_some_session_down():
    patch1 = patch(
        "svc_announced.resolve_macro",
        return_value=[ipaddress.ip_network(TEST_PFX), ipaddress.ip_network("87.250.250.0/24")],
    )
    patch2 = patch(
        "svc_announced.get_bgp_grt_export",
        side_effect=[
            {
                "b_core_2": [
                    ipaddress.ip_network("92.254.254.1/32"),
                    ipaddress.ip_network("87.250.250.3/32"),
                    ipaddress.ip_network("87.250.250.66/32"),
                ]
            },
            {
                "b_core_2": [
                    ipaddress.ip_network("2a02:6b8:0:ff::1/128"),
                    ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
                ],
                "b_core_4": [
                    ipaddress.ip_network("2a02:6b8:0:ff::1/128"),
                    ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
                ],
            },
        ],
    )
    patch3 = patch(
        "svc_announced.get_system_addresses_as_prefixes",
        return_value={
            ipaddress.ip_network("92.254.254.1/32"),
            ipaddress.ip_network("2a02:6b8:0:ff::1/128"),
            ipaddress.ip_network("87.250.250.3/32"),
            ipaddress.ip_network("87.250.250.66/32"),
            ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
            ipaddress.ip_network("92.150.16.0/26"),
        },
    )
    patch1.start()
    patch2.start()
    patch3.start()
    status, message = check_svcs_announced()
    assert status == OK_STATUS


def test_is_subnet_of():
    assert is_subnet_of(ipaddress.ip_network("192.168.1.0/26"), ipaddress.ip_network("2001:db8::/32")) is False
    assert is_subnet_of(ipaddress.ip_network("192.168.8.0/26"), ipaddress.ip_network("192.168.1.0/24")) is False
    assert is_subnet_of(ipaddress.ip_network("192.168.1.0/26"), ipaddress.ip_network("192.168.1.0/24")) is True
    assert is_subnet_of(ipaddress.ip_network("192.168.0.0/16"), ipaddress.ip_network("192.168.1.0/24")) is False
    assert is_subnet_of(ipaddress.ip_network("2001:db8::/64"), ipaddress.ip_network("2001:db8::/32")) is True
    assert is_subnet_of(ipaddress.ip_network("2001:db8::/64"), ipaddress.ip_network("2001:db8::8/128")) is False
    assert is_subnet_of(ipaddress.ip_network("2001:db8:15::/64"), ipaddress.ip_network("2001:db8:16::/64")) is False


def test_aggregated_exports():
    patch1 = patch(
        "svc_announced.resolve_macro",
        return_value=[ipaddress.ip_network(TEST_PFX), ipaddress.ip_network("87.250.248.0/22")],
    )
    patch2 = patch(
        "svc_announced.get_bgp_grt_export",
        side_effect=[
            {
                "b_core_2": [
                    ipaddress.ip_network("87.250.250.0/24"),
                    ipaddress.ip_network("92.158.64.16/32"),
                ],
            },
            {
                "b_core_2": [
                    ipaddress.ip_network("2a02:6b8:0:ff::1/128"),
                    ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
                ],
            },
        ],
    )
    patch3 = patch(
        "svc_announced.get_system_addresses_as_prefixes",
        return_value={
            ipaddress.ip_network("2a02:6b8:0:ff::1/128"),
            ipaddress.ip_network("87.250.250.3/32"),
            ipaddress.ip_network("87.250.250.15/32"),
            ipaddress.ip_network("2a02:6b8:0:3400::aa/128"),
        },
    )
    patch1.start()
    patch2.start()
    patch3.start()
    status, message = check_svcs_announced()

    assert status == OK_STATUS
    assert message == "OK"
