from typing import Dict, Any

import pytest

import noc.grad.grad.test.data.jnx_chassis_inventory as jnx_chassis_inventory
import noc.grad.grad.test.data.jnx_chassis_inventory2 as jnx_chassis_inventory2
import noc.grad.grad.test.data.jnx_environment as jnx_environment
import noc.grad.grad.test.data.jnx_interface as jnx_interface
import noc.grad.grad.test.data.jnx_interface2 as jnx_interface2
import noc.grad.grad.test.data.jnx_interface_optics as jnx_interface_optics
import noc.grad.grad.test.data.jnx_interface_optics2 as jnx_interface_optics2
import noc.grad.grad.test.data.jnx_interface_terse as jnx_interface_terse
import noc.grad.grad.test.data.jnx_interface_terse2 as jnx_interface_terse2
import noc.grad.grad.test.data.jnx_lacp_interface_information as jnx_lacp_interface_information
import noc.grad.grad.test.data.jnx_mx_get_environment_information as jnx_mx_get_environment_information
import noc.grad.grad.test.data.jnx_qfx_get_environment_information as jnx_qfx_get_environment_information
import noc.grad.grad.test.data.jnx_route_engine_information as jnx_route_engine_information
import noc.grad.grad.test.data.jnx_route_engine_information2 as jnx_route_engine_information2
import noc.grad.grad.test.data.jnx_system_memory_information as jnx_system_memory_information
import noc.grad.grad.test.data.vrp_ne40_devm as vrp_ne40_devm
import noc.grad.grad.test.data.vrp_ne40_ifm as vrp_ne40_ifm
import noc.grad.grad.test.data.vrp_ne40_ifmtrunk as vrp_ne40_ifmtrunk
import noc.grad.grad.test.data.vrp_ne40_short_bgp as vrp_ne40_short_bgp
import noc.grad.grad.test.data.vrp_s6860_devm as vrp_s6860_devm
import noc.grad.grad.test.data.vrp_s6870_bgp as vrp_s6870_bgp
import noc.grad.grad.test.data.vrp_s6870_devm as vrp_s6870_devm
import noc.grad.grad.test.data.vrp_s6870_ifm as vrp_s6860_ifm
import noc.grad.grad.test.data.vrp_s6870_ifm as vrp_s6870_ifm
import noc.grad.grad.test.data.vrp_s6870_ifmtrunk as vrp_s6870_ifmtrunk
from noc.grad.grad.lib.functions import parse_xmlstring
from noc.grad.grad.lib.netconf_helper import (
    get_if_exists_dict,
    parse_juniper_netconf_xml_reply_new,
    parse_netconf_xml_reply_from_str,
    parse_huawei_capabilities,
)
from noc.grad.grad.lib.test_functions import get_data_content, wrap_from_json_to_mapdata, get_kvts_data_content
from noc.grad.grad.user_functions.netconf_huawei import (
    parse_huawei_ifm_network,
    parse_huawei_ne40_devm_transceiver,
    parse_huawei_devm_mem,
    parse_huawei_devm_cpu,
    parse_huawei_devm_iface_uptime,
    parse_huawei_s6860_devm_transceiver,
    parse_huawei_s6870_devm_transceiver,
    parse_huawei_ifmtrunkif,
    parse_huawei_psu,
    parse_huawei_bgp,
    parse_huawei_duration,
)
from noc.grad.grad.user_functions.netconf_juniper import (
    parse_jnx_network,
    parse_jnx_speed,
    parse_jnx_interface_optics,
    parse_jnx_inventory_optics,
    parse_ifaces_terse,
    parse_jnx_environment_psu,
    parse_jnx_netconf_ram,
    parse_jnx_netconf_cpu,
    parse_jnx_netconf_bundle,
)

ZEROTS = 0


def test_parse_huawei_ifm():
    # urn:huawei:yang:huawei-ifm?module=huawei-ifm&revision=2019-04-10
    exp = wrap_from_json_to_mapdata(get_data_content("vrp_ne40_ifm_res.json", is_json=True))
    res_raw, _ = parse_huawei_ifm_network(parse_xmlstring(vrp_ne40_ifm.xml), ts=ZEROTS)
    assert res_raw == exp
    exp = wrap_from_json_to_mapdata(get_data_content("vrp_s6870_ifm_res.json", is_json=True))
    res_raw, _ = parse_huawei_ifm_network(parse_xmlstring(vrp_s6870_ifm.xml), ts=ZEROTS)
    assert res_raw == exp
    exp = wrap_from_json_to_mapdata(get_data_content("vrp_s6860_ifm_res.json", is_json=True))
    res_raw, _ = parse_huawei_ifm_network(parse_xmlstring(vrp_s6860_ifm.xml), ts=ZEROTS)
    assert res_raw == exp


def test_parse_huawei_devm_transceiver():
    exp = wrap_from_json_to_mapdata(get_data_content("vrp_ne40_huawei_devm_transceiver_res.json", is_json=True))
    res = parse_huawei_ne40_devm_transceiver(parse_xmlstring(vrp_ne40_devm.xml), ts=ZEROTS, threshold_overrides={})
    assert res == exp
    exp = wrap_from_json_to_mapdata(get_data_content("vrp_s6860_huawei_devm_transceiver_res.json", is_json=True))
    res = parse_huawei_s6860_devm_transceiver(parse_xmlstring(vrp_s6860_devm.xml), ts=ZEROTS, threshold_overrides={})
    assert res == exp
    exp = wrap_from_json_to_mapdata(get_data_content("vrp_s6870_huawei_devm_transceiver_res.json", is_json=True))
    res = parse_huawei_s6870_devm_transceiver(parse_xmlstring(vrp_s6870_devm.xml), ts=ZEROTS, threshold_overrides={})
    assert res == exp


def test_parse_huawei_devm_iface_uptime():
    # urn:huawei:yang:huawei-devm?module=huawei-devm&revision=2019-09-09&deviations=huawei-devm-deviations-NE-F1A
    exp = get_data_content("vrp_ne40_devm_iface_uptime_res.json", is_json=True)
    res = parse_huawei_devm_iface_uptime(parse_xmlstring(vrp_ne40_devm.xml))
    assert res == exp

    res = parse_huawei_devm_iface_uptime(parse_xmlstring(vrp_s6860_devm.xml))
    exp = get_data_content("vrp_s6860_devm_iface_uptime_res.json", is_json=True)
    assert res == exp

    res = parse_huawei_devm_iface_uptime(parse_xmlstring(vrp_s6870_devm.xml))
    exp = get_data_content("vrp_s6870_devm_iface_uptime_res.json", is_json=True)
    assert res == exp


def test_parse_huawei_devm_mem():
    # urn:huawei:yang:huawei-devm?module=huawei-devm&revision=2019-09-09&deviations=huawei-devm-deviations-NE-F1A
    exp = [
        (0, {"mem_type": "os"}, {"usage": 24}),
        (0, {"mem_type": "do_memory"}, {"usage": 92}),
        (0, {"mem_type": "simple_memory"}, {"usage": 91}),
    ]
    res = parse_huawei_devm_mem(parse_xmlstring(vrp_ne40_devm.xml), ts=ZEROTS)
    assert res == exp

    exp = [
        (0, {"mem_type": "os"}, {"usage": 34}),
        (0, {"mem_type": "do_memory"}, {"usage": 87}),
        (0, {"mem_type": "simple_memory"}, {"usage": 94}),
    ]
    res = parse_huawei_devm_mem(parse_xmlstring(vrp_s6860_devm.xml), ts=ZEROTS)
    assert res == exp

    exp = [
        (0, {"mem_type": "os"}, {"usage": 41}),
        (0, {"mem_type": "do_memory"}, {"usage": 91}),
        (0, {"mem_type": "simple_memory"}, {"usage": 91}),
    ]
    res = parse_huawei_devm_mem(parse_xmlstring(vrp_s6870_devm.xml), ts=ZEROTS)
    assert res == exp


def test_parse_huawei_devm_cpu():
    # urn:huawei:yang:huawei-devm?module=huawei-devm&revision=2019-09-09&deviations=huawei-devm-deviations-NE-F1A
    exp = [(0, {"component": "1/1/1"}, {"utilization": 12})]
    res = parse_huawei_devm_cpu(parse_xmlstring(vrp_ne40_devm.xml), ts=ZEROTS)
    assert res == exp

    exp = [(0, {"component": "1/1/1"}, {"utilization": 10})]
    res = parse_huawei_devm_cpu(parse_xmlstring(vrp_s6870_devm.xml), ts=ZEROTS)
    assert res == exp

    exp = [(0, {"component": "1/1/1"}, {"utilization": 17})]
    res = parse_huawei_devm_cpu(parse_xmlstring(vrp_s6860_devm.xml), ts=ZEROTS)
    assert res == exp


HUAWEI_CAPABILITIES = [
    [
        "urn:huawei:yang:huawei-devm?module=huawei-devm&revision=2019-09-09&deviations=huawei-devm-deviations-NE-F1A",
        {"module": "huawei-devm", "revision": "2019-09-09", "deviations": "huawei-devm-deviations-NE-F1A"},
    ],
    [
        "urn:huawei:yang:huawei-devm-deviations-NE-F1A?module=huawei-devm-deviations-NE-F1A&revision=2019-04-03",
        {"module": "huawei-devm-deviations-NE-F1A", "revision": "2019-04-03"},
    ],
    [
        "http://www.huawei.com/netconf/vrp/huawei-devm?module=huawei-devm&revision=2019-04-02&deviations=huawei-devm-deviations-s6860",
        {"module": "huawei-devm", "revision": "2019-04-02", "deviations": "huawei-devm-deviations-s6860"},
    ],
    [
        "http://www.huawei.com/netconf/vrp/huawei-devm-deviations-s6860?module=huawei-devm-deviations-s6860&revision=2017-12-23",
        {"module": "huawei-devm-deviations-s6860", "revision": "2017-12-23"},
    ],
    [
        "http://www.huawei.com/netconf/vrp/huawei-devm?module=huawei-devm&amp;revision=2017-03-23&amp;deviations=huawei-devm-deviations-s6870",
        {"deviations": "huawei-devm-deviations-s6870", "module": "huawei-devm", "revision": "2017-03-23"},
    ],
]


@pytest.mark.parametrize("test_input, expected", HUAWEI_CAPABILITIES)
def test_parse_capabilities(test_input, expected):
    res = parse_huawei_capabilities([test_input])
    assert res == [expected]


def test_parse_huawei_trunkif():
    res = parse_huawei_ifmtrunkif(parse_xmlstring(vrp_ne40_ifmtrunk.xml), ts=ZEROTS)
    exp = wrap_from_json_to_mapdata(get_data_content("vrp_ne40_ifmtrunk_res.json", is_json=True))
    assert res == exp
    res = parse_huawei_ifmtrunkif(parse_xmlstring(vrp_s6870_ifmtrunk.xml), ts=ZEROTS)
    exp = []
    assert res == exp


def test_parse_huawei_psu():
    res = parse_huawei_psu(parse_xmlstring(vrp_ne40_devm.xml), ts=ZEROTS)
    exp = [
        (0, {"name": "2"}, {"voltage": 12.07, "status": 1, "power": 147, "temperature": 26}),
        (0, {"name": "3"}, {"voltage": 12.06, "status": 1, "power": 178, "temperature": 28}),
    ]
    assert res == exp
    res = parse_huawei_psu(parse_xmlstring(vrp_s6870_devm.xml), ts=ZEROTS)
    exp = [
        (0, {"name": "1/3"}, {"voltage": 12.2, "status": 1, "power": 98}),
        (0, {"name": "1/4"}, {"voltage": 0.0, "status": 0, "power": 0}),
    ]
    assert res == exp
    res = parse_huawei_psu(parse_xmlstring(vrp_s6860_devm.xml), ts=ZEROTS)
    exp = [
        (0, {"name": "1/3"}, {"voltage": 12.2, "status": 1, "power": 70}),
        (0, {"name": "1/4"}, {"voltage": 12.2, "status": 1, "power": 84}),
    ]
    assert res == exp


def test_parse_huawei_bgp():
    exp = wrap_from_json_to_mapdata(get_data_content("vrp_ne40_short_bgp_res.json", is_json=True))
    res = parse_huawei_bgp(parse_xmlstring(vrp_ne40_short_bgp.xml), ts=ZEROTS)
    assert list(res[0]) == exp
    exp = wrap_from_json_to_mapdata(get_data_content("vrp_s6870_bgp_res.json", is_json=True))
    res = parse_huawei_bgp(parse_xmlstring(vrp_s6870_bgp.xml), ts=ZEROTS)
    assert list(res[0]) == exp


def test_parse_jnx_interfaces():
    exp = get_kvts_data_content("jnx_interface_res.json")
    res, _ = parse_jnx_network(parse_xmlstring(jnx_interface.xml), ts=ZEROTS)
    assert res == exp
    exp = get_kvts_data_content("jnx_interface2_res.json")
    res, _ = parse_jnx_network(parse_xmlstring(jnx_interface2.xml), ts=ZEROTS)
    assert res == exp


def test_jnx_interface_optics():
    exp = get_kvts_data_content("jnx_transceivers.json")
    transceivers_types = parse_jnx_inventory_optics(parse_xmlstring(jnx_chassis_inventory.xml))
    terse_data = parse_netconf_xml_reply_from_str(jnx_interface_terse.xml)
    ifaces_status = parse_ifaces_terse(terse_data)
    res = parse_jnx_interface_optics(
        parse_xmlstring(jnx_interface_optics.xml),
        transceivers_types=transceivers_types,
        ts=ZEROTS,
        ifaces_status=ifaces_status,
        threshold_overrides={},
    )
    assert res == exp
    exp = get_kvts_data_content("jnx_transceivers2.json")
    transceivers_types2 = parse_jnx_inventory_optics(parse_xmlstring(jnx_chassis_inventory2.xml))
    terse_data2 = parse_juniper_netconf_xml_reply_new(parse_xmlstring(jnx_interface_terse2.xml))
    ifaces_status2 = parse_ifaces_terse(terse_data2)
    res = parse_jnx_interface_optics(
        parse_xmlstring(jnx_interface_optics2.xml),
        transceivers_types=transceivers_types2,
        ts=ZEROTS,
        ifaces_status=ifaces_status2,
        threshold_overrides={},
    )
    assert res == exp


JNX_SPEED = [
    [
        "800mbps",
        800,
    ],
]


@pytest.mark.parametrize("test_input, expected", JNX_SPEED)
def test_parse_jnx_speed(test_input, expected):
    res = parse_jnx_speed(test_input)
    assert res == expected


JNX_RPC = [
    [
        """
        <rpc-reply xmlns:junos="http://xml.juniper.net/junos/18.4R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
        <software-information>
        <host-name>lab-vla-e1</host-name>
        </software-information>
        </rpc-reply>
        """,
        {"@message-id": 1, "software-information": {"host-name": {"$": "lab-vla-e1"}}},
    ],
    [
        """<nc:rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:junos="http://xml.juniper.net/junos/18.3R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
        <interface-information xmlns="http://xml.juniper.net/junos/18.3R3/junos-interface" junos:style="terse">
        <physical-interface></physical-interface>
        </interface-information>
        </nc:rpc-reply>
    """,
        {"@message-id": 1, "interface-information": {"@style": "terse", "physical-interface": {}}},
    ],
    [
        """
    <rpc-reply xmlns:junos="http://xml.juniper.net/junos/18.4R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
    <environment-information xmlns="http://xml.juniper.net/junos/18.4R3/junos-chassis">
    <environment-item></environment-item>
    </environment-information>
    </rpc-reply>
    """,
        {"@message-id": 1, "environment-information": {"environment-item": {}}},
    ],
]


@pytest.mark.parametrize("test_input, expected", JNX_RPC)
def test_parse_jnx_xml(test_input: str, expected: Dict[str, Any]):
    res = parse_juniper_netconf_xml_reply_new(parse_xmlstring(test_input))
    assert res == expected


def test_parse_jnx_environment_psu():
    exp = get_kvts_data_content("jnx_environment_netconf_res.json")
    res = parse_jnx_environment_psu(parse_xmlstring(jnx_environment.xml), ZEROTS)
    assert res == exp
    exp = get_kvts_data_content("jnx_mx_get_environment_information_res.json")
    res = parse_jnx_environment_psu(parse_xmlstring(jnx_mx_get_environment_information.xml), ZEROTS)
    assert res == exp
    exp = get_kvts_data_content("jnx_qfx_get_environment_information_res.json")
    res = parse_jnx_environment_psu(parse_xmlstring(jnx_qfx_get_environment_information.xml), ZEROTS)
    assert res == exp


HUAWEI_BGP_UPTIME = [
    ["6982h18m", 25136280],
    ["Up for 48d19h47m31s", 4218451],
    ["****h04m", 3600000],
]


@pytest.mark.parametrize("test_input, expected", HUAWEI_BGP_UPTIME)
def test_parse_huawei_duration(test_input, expected):
    res = parse_huawei_duration(test_input)
    assert res == expected


def test_parse_jnx_netconf_ram():
    res = parse_jnx_netconf_ram(parse_xmlstring(jnx_system_memory_information.xml), ZEROTS)
    expected = [(0, {'mem_type': 'os'}, {'usage': 32})]
    assert res == expected


def test_parse_jnx_netconf_cpu():
    res = parse_jnx_netconf_cpu(parse_xmlstring(jnx_route_engine_information.xml), ZEROTS)
    expected = [(0, {'component': 're/0'}, {'utilization': 4})]
    assert res == expected
    res = parse_jnx_netconf_cpu(parse_xmlstring(jnx_route_engine_information2.xml), ZEROTS)
    expected = [(0, {'component': 're'}, {'utilization': 2})]
    assert res == expected


def test_parse_jnx_netconf_bundle():
    res = parse_jnx_netconf_bundle(parse_xmlstring(jnx_lacp_interface_information.xml), ZEROTS)
    expected = [
        (0, {'ifname': 'ae1'}, {'up': 2, 'total': 2}),
        (0, {'ifname': 'ae2'}, {'up': 2, 'total': 2}),
        (0, {'ifname': 'ae321'}, {'up': 2, 'total': 2}),
    ]
    assert res == expected


def test_get_if_exists_dict():
    data = {'carrier-transitions': {'$': 1}, 'output-errors': {'$': 0}, 'output-collisions': {}}
    assert get_if_exists_dict(data) == {'carrier-transitions': 1, 'output-errors': 0}
