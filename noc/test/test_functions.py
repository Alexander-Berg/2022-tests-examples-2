import asyncio
import json
import logging
import types
from functools import partial
from typing import Optional, Union, Dict, List
from unittest.mock import patch, MagicMock

import defusedxml.ElementTree
import pytest
from noc.grad.grad.lib import adva_rest, snmp_helper

from noc.grad.grad.lib.comocutor_helper import ios_transceiver
from noc.grad.grad.lib.functions import (
    kvts_to_mapdata,
    mapdata_to_kvts,
    call_sendgen,
    per_dc_split,
    oid_to_str,
    parse_fn_from_conf,
    equal_split_all,
    parse_netconf_vrp_s6870_power,
    oid_to_ip,
    make_shard_sha1_last4,
    xml_to_dict,
)
from noc.grad.grad.lib.netconf_helper import parse_netconf_xml_reply_from_str
from noc.grad.grad.lib.pipeline import (
    check_net_data_sanity,
    parse_jnx_counter_name,
    ekinops_int_transform_fn,
    huawei_hw_optical_filter,
    huawei_transform,
    blink_bug_fixer,
    sum_all_values,
    parse_cisco_power_unit,
    sum_counters,
    parse_conf_fn,
    drop_zero_value,
    huawei_network_pre,
    pdu_recalc,
    sum_ifmib_counters_old,
    sum_ifmib_counters_new,
    SR_RX_POWER_THRESHOLD_LOW,
    LAST_RESORT_THRESHOLD_LOW,
    calc_fraction,
    recalc_arista_queue,
    uptime_reset_count,
    strip_alias,
    _available_pp_functions,
    apply_fn_for_period,
)
from noc.grad.grad.lib.pipeline_generic_functions import filter_keys, rearrange_partial_data, ret_max_for_period
from noc.grad.grad.lib.snmp_helper import Oid
from noc.grad.grad.lib.structures import FrozenDict
from noc.grad.grad.lib.test_functions import MIBS, make_job, get_data_content, get_testdata, get_kvts_data_content
from noc.grad.grad.user_functions.arista_transceivers import arista_transceiver, parse_arista_ifaces_status

patches = []


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


def setup_module(module):
    patches.append(patch.dict(snmp_helper.MIBS, MIBS, clear=True))
    for p in patches:
        p.start()


def teardown_module(module):
    for p in patches:
        p.stop()


TS = 0
PORT_DOWN = 2
PORT_UP = 1
TEST_KEY = (("ifname", "eth0"), ("sensor", "rx"))
TEST_KEY_V2 = (("ifname", "eth0"), ("sensor", "tx"))
TEST_KEY2 = (("ifname", "eth1"), ("sensor", "rx"))
NODATA = []
PERIOD = 4
TS_PERIOD_0 = TS + PERIOD * 1
TS_PERIOD_1 = TS + PERIOD * 2
TS_PERIOD_2 = TS + PERIOD * 3
TS_PERIOD_3 = TS + PERIOD * 4
TS_PERIOD_4 = TS + PERIOD * 5
NO_LOG = None
TS_PERIOD_5 = TS + PERIOD * 6
DEBUG = True

IFNAME = "100GE3/0/21"
HOST = "localhost"

if DEBUG:
    # math_functions.DEBUG = True
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s() - %(levelname)s - %(message)s",
    )


def _partial_cmp(p1, p2):
    if p1.func == p2.func and p1.args == p2.args and p1.keywords == p2.keywords:
        return True
    return False


def gen_iface_stat(
    ifname,
    speed=None,
    oper_status: Optional[int] = PORT_UP,
    admin_status: Optional[int] = PORT_UP,
    rx: Union[int, float] = 0,
    tx: Union[int, float] = 0,
    auto_packets=True,
    tx_packets=False,
    rx_packets=False,
    mtu=9000,
):
    if auto_packets:
        assert tx_packets is False
        assert rx_packets is False

    keys = {"ifname": ifname}
    values = {}
    if speed is not None:
        values["speed"] = int(speed)
    if isinstance(oper_status, int):
        values["oper_status"] = oper_status
    if isinstance(admin_status, int):
        values["admin_status"] = admin_status
    values["rx"] = int(rx)
    values["tx"] = int(tx)
    if auto_packets:
        rx_pps = int(rx / mtu)
        tx_pps = int(rx / mtu)
        values["tx_packets"] = tx_pps
        values["rx_packets"] = rx_pps
    else:
        if tx_packets is not None:
            values["tx_packets"] = tx_packets
        if rx_packets is not None:
            values["rx_packets"] = rx_packets

    return [TS, keys, values]


def mock_get_supported_speed_for(ifname, speed=None):
    change_to = None
    supported = tuple()
    if_type = 0

    if ifname == "bsd_lagg":
        supported = (2000, 20000)
    elif ifname == "vlan2":
        supported = (None,)
    return change_to, supported, if_type


TEST_CASES = [
    # ["скорость выставляется в 0, если oper_status==PORT_DOWN",
    #  gen_iface_stat("lagg0", speed=10E3, rx=0, tx=0, oper_status=PORT_DOWN, admin_status=PORT_DOWN),
    #  gen_iface_stat("lagg0", speed=0, rx=0, tx=0, oper_status=PORT_DOWN, admin_status=PORT_DOWN),
    #  NO_LOG],
    [
        "если трафика значительно больше чем speed, то удаляем данные",
        gen_iface_stat("lagg0", speed=10e3, rx=10e12),
        NODATA,
        '%s rx traffic is too huge. speed=%s keys=%s values=%s',
    ],
    [
        "для интерфейсов с невменяемым speed удаляем speed",
        gen_iface_stat("bsd_lagg", speed=12345, rx=10e6, tx=10e6),
        gen_iface_stat("bsd_lagg", rx=10e6, tx=10e6),
        '%s unsupported speed. sup=%s keys=%s values=%s',
    ],
    [
        "если скорость вменяемая то данные пропускаются как есть",
        gen_iface_stat("eth0", speed=100, rx=10e4, tx=10e4),
        gen_iface_stat("eth0", speed=100, rx=10e4, tx=10e4),
        NO_LOG,
    ],
    [
        "на vlan интерфейсах уберем скорость",
        gen_iface_stat("vlan2", speed=100, rx=10000, tx=10000),
        gen_iface_stat("vlan2", speed=None, rx=10000, tx=10000),
        NO_LOG,
    ],
    # ["проверка на подозрительный размер пакета",
    #  gen_iface_stat("eth0", speed=100, rx=100, tx=100, mtu=6),
    #  NODATA,
    #  NO_LOG],
    # ["рейт пакетов меньше 1 округляется в 0. это не должно вызывать проблем",
    #  gen_iface_stat("eth0", speed=100, rx_packets=1, tx_packets=1, auto_packets=False),
    #  gen_iface_stat("eth0", speed=100, rx_packets=1, tx_packets=1, auto_packets=False),
    #  ['%s has rx_packets without bytes. keys=%s values=%s', '%s has tx_packets without bytes. keys=%s values=%s']],
    [
        "наличие трафика и пакетов. не должно быть ошибок",
        gen_iface_stat("eth0", speed=100, rx_packets=1, tx_packets=1, rx=1000, tx=1000, auto_packets=False),
        gen_iface_stat("eth0", speed=100, rx_packets=1, tx_packets=1, rx=1000, tx=1000, auto_packets=False),
        NO_LOG,
    ],
]

BLINK_BUG_TEST_CASES = [
    ["3 плохих значения подряд", 4, [0, 5, 10, 70000, 70000, 70000, 30, 35, 40, 45, 50, 55], [0, 5, 10, 30, 35]],
]

KVTS_TO_MAPDATA_CASES = [
    [
        "несколько ключей",
        [((('addr', 'addr'), ('service_name', 'service_name'), ('proto', 6), ('sensor', 'conn')), 0, 1484150760)],
        [[1484150760, {'proto': 6, 'addr': 'addr', 'service_name': 'service_name'}, {'conn': 0}]],
    ],
    [
        "несколько значений у одного ключа",
        [
            ((('name', 'eth1'), ('sensor', 'rx')), 1, 1482918740),
            ((('name', 'eth1'), ('sensor', 'tx')), 1, 1482918740),
            ((('name', 'eth1'), ('sensor', 'rx')), 2, 1482918790),
            ((('name', 'eth1'), ('sensor', 'tx')), 2, 1482918790),
            ((('name', 'eth1'), ('sensor', 'rx')), 3, 1482918700),
            ((('name', 'eth1'), ('sensor', 'tx')), 3, 1482918700),
        ],
        [
            [1482918700, {'name': 'eth1'}, {'rx': 3, 'tx': 3}],
            [1482918740, {'name': 'eth1'}, {'rx': 1, 'tx': 1}],
            [1482918790, {'name': 'eth1'}, {'rx': 2, 'tx': 2}],
        ],
    ],
]


@pytest.mark.parametrize("comment, test_input, expected, expected_log", TEST_CASES)
def test_check_net_data_sanity(comment, test_input, expected, mocker, expected_log):
    if expected:
        expected = [expected]
    mocker.patch("noc.grad.grad.lib.pipeline.get_supported_speed_for", side_effect=mock_get_supported_speed_for)
    mocked_l = mocker.patch("noc.grad.grad.lib.pipeline._logger")
    fn = check_net_data_sanity(make_job())
    res = fn.send([test_input])
    logged_msgs = []
    for i in mocked_l.method_calls:
        logged_msgs.append(i[1][0])
    if expected_log:
        if not isinstance(expected_log, list):
            expected_log = [expected_log]
        for i in expected_log:
            assert any(i in log_msg for log_msg in logged_msgs)
    else:
        assert not logged_msgs
    assert len(expected) == len(res)
    if res:
        assert res == expected, comment


@pytest.mark.parametrize("comment, max_retention, test_input, expected", BLINK_BUG_TEST_CASES)
def test_blink_bug(comment, max_retention, test_input, expected, mocker):
    fixer = blink_bug_fixer(make_job(), max_retention=max_retention, target_sensor="rx")
    res = []
    ts = 0
    for data in test_input:
        ts += 10
        kvts_list = [(TEST_KEY, data, ts)]
        tmp_res = fixer.send(kvts_list)
        for k, v, ts in tmp_res:
            res.append(v)
    assert res == expected, comment


@pytest.mark.parametrize("comment, test_input, expected", KVTS_TO_MAPDATA_CASES)
def test_kvts_to_mapdata(comment, test_input, expected):
    res = kvts_to_mapdata(test_input)
    assert res == expected, comment


@pytest.mark.parametrize("comment, test_input, expected", KVTS_TO_MAPDATA_CASES)
def test_mapdata_to_kvts(comment, test_input, expected):
    mapdata = kvts_to_mapdata(test_input)
    kvts = mapdata_to_kvts(mapdata)
    assert sorted(kvts) == sorted(test_input), comment


JNX_COUNTER_CASES = [
    ["RETRANSMIT_RX_vla1-x7-ae7.0-i", {'counter': 'RETRANSMIT_RX_vla1-x7', 'iface': 'ae7.0', 'direction': 'input'}],
    ["FROM-CDN-ae6.2-o", {"counter": "FROM-CDN", "direction": "output", "iface": "ae6.2"}],
    ["RETRANSMIT_RX_vla1-5s36", {"counter": "RETRANSMIT_RX_vla1-5s36", "direction": None, "iface": None}],
    ["UDP-INv6-xe-3/2/0.0-i", {"counter": "UDP-INv6", "direction": "input", "iface": "xe-3/2/0.0"}],
    ["stp_flavors", {"counter": "stp_flavors", "direction": None, "iface": None}],
    ["__default_arp_policer__", {"counter": "__default_arp_policer__", "direction": None, "iface": None}],
    ["200Mb-TCPSYN-2-SLB-ae0.0-i", {'counter': '200Mb-TCPSYN-2-SLB', 'direction': 'input', 'iface': 'ae0.0'}],
]


@pytest.mark.parametrize("test_input, expected", JNX_COUNTER_CASES)
def test_parse_jnx_counter_name(test_input: str, expected: Dict):
    assert parse_jnx_counter_name(test_input) == expected


def test_ekinops_int_transform_fn():
    assert ekinops_int_transform_fn(32000, length=2) == 32000
    assert ekinops_int_transform_fn(50000, length=2) == -15536


HUAWEI_HW_OPTICAL_TRANSFORM_CASES = [
    [
        [((("ifname", "100GE3/0/19"), ("sensor", "rx_power")), b"102.78,9.88,-0.09,-14.89", 1525684324)],
        [
            ((("ifname", "100GE3/0/19"), ("lane", 0), ("sensor", "rx_power")), 102.78, 1525684324),
            ((("ifname", "100GE3/0/19"), ("lane", 1), ("sensor", "rx_power")), 9.88, 1525684324),
            ((("ifname", "100GE3/0/19"), ("lane", 2), ("sensor", "rx_power")), -0.09, 1525684324),
            ((("ifname", "100GE3/0/19"), ("lane", 3), ("sensor", "rx_power")), -14.89, 1525684324),
        ],
    ],
    # корректная работа с несколькими ключами(ifname, phys_class)
    [
        [((('ifname', '100GE7/0/25:2'), ('phys_class', '10'), ('sensor', 'rx_power')), b'-262.33', 1526054847)],
        [
            (
                (('ifname', '100GE7/0/25:2'), ('lane', 0), ('phys_class', '10'), ('sensor', 'rx_power')),
                -262.33,
                1526054847,
            )
        ],
    ],
    [
        [
            (
                (
                    ('phys_class', '10'),
                    ('ifname', '40GE5/0/28'),
                    ('optical_type', '40GBASE_SR4'),
                    ('sensor', 'rx_power'),
                ),
                b'-170.76,-156.27,-561.93,-495.94',
                1556653500,
            )
        ],
        [
            (
                (
                    ('phys_class', '10'),
                    ('lane', 0),
                    ('ifname', '40GE5/0/28'),
                    ('optical_type', '40GBASE_SR4'),
                    ('sensor', 'rx_power'),
                ),
                -170.76,
                1556653500,
            ),
            (
                (
                    ('phys_class', '10'),
                    ('lane', 1),
                    ('ifname', '40GE5/0/28'),
                    ('optical_type', '40GBASE_SR4'),
                    ('sensor', 'rx_power'),
                ),
                -156.27,
                1556653500,
            ),
            (
                (
                    ('phys_class', '10'),
                    ('lane', 2),
                    ('ifname', '40GE5/0/28'),
                    ('optical_type', '40GBASE_SR4'),
                    ('sensor', 'rx_power'),
                ),
                -561.93,
                1556653500,
            ),
            (
                (
                    ('phys_class', '10'),
                    ('lane', 3),
                    ('ifname', '40GE5/0/28'),
                    ('optical_type', '40GBASE_SR4'),
                    ('sensor', 'rx_power'),
                ),
                -495.94,
                1556653500,
            ),
        ],
    ],
]


@pytest.mark.parametrize("test_input, expected", HUAWEI_HW_OPTICAL_TRANSFORM_CASES)
def test_huawei_transform(test_input, expected):
    res = call_sendgen(huawei_transform, send=test_input)
    assert res == expected


HUAWEI_HW_OPTICAL_CASES = [
    (
        "два элемента должны быть склеены",
        [
            [
                1527253980,
                {'ifname': IFNAME, 'host': HOST, 'phys_class': '10', 'optical_type': '10GBASE_XZ'},
                {
                    'rx_power_threshold_high': 200.0,
                    'rx_power_threshold_low': -1390.0,
                    'temp': 33.0,
                    'oper_status': 15.0,
                },
            ],
            [
                1527253980,
                {
                    'ifname': IFNAME,
                    'lane': 0,
                    'host': HOST,
                    'phys_class': '10',
                    'optical_type': '10GBASE_XZ',
                    'oper_status': 15.0,
                },
                {'rx_power': -3698.0},
            ],
        ],
        [
            [
                1527253980,
                {'ifname': IFNAME, 'host': HOST, 'lane': 0},
                {
                    'rx_power': -36.98,
                    'rx_power_threshold_high': 2,
                    'rx_power_threshold_low': LAST_RESORT_THRESHOLD_LOW,
                    'temp': 33.0,
                    'oper_status': 1,
                },
            ]
        ],
    ),
    (
        "удаляем данные если нет rx_power",
        [
            [
                1525685280,
                {"ifname": IFNAME, "host": HOST, 'phys_class': '10', 'optical_type': '10GBASE_XZ'},
                {"rx_power_threshold_high": 0.0, "temp": -255.0, "rx_power_threshold_low": 0.0, 'oper_status': 15.0},
            ]
        ],
        NODATA,
    ),
    (
        "для SR трансиверов используем другой порог",
        [
            [
                1527253980,
                {'ifname': IFNAME, 'host': HOST, 'phys_class': '10', 'optical_type': '10GBASE_SR'},
                {
                    'rx_power_threshold_high': 200.0,
                    'rx_power_threshold_low': -1390.0,
                    'temp': 33.0,
                    'oper_status': 15.0,
                },
            ],
            [
                1527253980,
                {'ifname': IFNAME, 'lane': 0, 'host': HOST, 'phys_class': '10', 'optical_type': '10GBASE_SR'},
                {'rx_power': -3698.0},
            ],
        ],
        [
            [
                1527253980,
                {'ifname': IFNAME, 'host': HOST, 'lane': 0},
                {
                    'rx_power': -36.98,
                    'rx_power_threshold_high': 2,
                    'rx_power_threshold_low': SR_RX_POWER_THRESHOLD_LOW,
                    'temp': 33.0,
                    'oper_status': 1,
                },
            ]
        ],
    ),
    (
        "порядок элементов не должен влиять на результат",
        [
            [
                1527253980,
                {'ifname': IFNAME, 'lane': 0, 'host': HOST, 'phys_class': '10', 'optical_type': '10GBASE_SR'},
                {'rx_power': -3698.0},
            ],
            [
                1527253980,
                {'ifname': IFNAME, 'host': HOST, 'phys_class': '10', 'optical_type': '10GBASE_SR'},
                {
                    'rx_power_threshold_high': 200.0,
                    'rx_power_threshold_low': -1390.0,
                    'temp': 33.0,
                    'oper_status': 15.0,
                },
            ],
        ],
        [
            [
                1527253980,
                {'ifname': IFNAME, 'host': HOST, 'lane': 0},
                {
                    'rx_power': -36.98,
                    'rx_power_threshold_high': 2,
                    'rx_power_threshold_low': SR_RX_POWER_THRESHOLD_LOW,
                    'temp': 33.0,
                    'oper_status': 1,
                },
            ]
        ],
    ),
]


@pytest.mark.parametrize("comment, in_data, expected", HUAWEI_HW_OPTICAL_CASES)
def test_huawei_hw_optical_filter(comment, in_data, expected):
    gen = huawei_hw_optical_filter(make_job())
    res = gen.send(in_data)
    assert res == expected, comment


def _run_fn_or_gen(fn, in_data):
    fn_prev_data = {}
    if isinstance(fn, types.GeneratorType):
        data = fn.send(in_data)
    else:
        data = fn(fn_prev_data, in_data)
    return data


def test_sum_all_values():
    in_data = [
        [TS, {"host": HOST}, {"current": 10}],
        [TS, {"host": HOST}, {"current": 10}],
        [TS, {"host": HOST}, {"current": 10}],
    ]
    exp = [[TS, {"host": HOST}, {"current": 10 * 3}]]
    assert exp == _run_fn_or_gen(sum_all_values(), in_data=in_data)

    in_data = [
        [TS, {"host": HOST}, {"current": 10}],
        [TS, {"host": HOST}, {"current2": 10}],
        [TS, {"host": HOST}, {"current": 10}],
    ]
    exp = [[TS, {"host": HOST}, {"current": 10 * 2, "current2": 10}]]
    assert exp == _run_fn_or_gen(sum_all_values(), in_data=in_data)
    in_data = [
        [1535368600, {"index": "470", "host": "man1-5s44"}, {"current": 34920}],
        [1535368600, {"index": "471", "host": "man1-5s44"}, {"current": 34920}],
        [1535368600, {"index": "472", "host": "man1-5s44"}, {"current": 34920}],
    ]
    exp = [[1535368600, {"host": "man1-5s44"}, {"current": 34920 + 34920 + 34920}]]
    assert exp == _run_fn_or_gen(sum_all_values(drop_keys=["index"]), in_data=in_data)


def test_sum_all_values2():
    in_data = [
        [
            1553513180,
            {'counter': 'TO-SPIDER', 'direction': 'input', 'ifname': 'ae5.0', 'card': 10, 'host': 'styri'},
            {'traff': 70000, 'packets': 80},
        ],
        [
            1553513180,
            {'counter': 'TO-SPIDER', 'direction': 'input', 'ifname': 'ae5.0', 'card': 11, 'host': 'styri'},
            {'traff': 90000, 'packets': 100},
        ],
        [
            1553513180,
            {'counter': 'TO-SPIDER2', 'direction': 'input', 'ifname': 'ae5.0', 'card': 10, 'host': 'styri'},
            {'traff': 70000, 'packets': 80},
        ],
        [
            1553513180,
            {'counter': 'TO-SPIDER2', 'direction': 'input', 'ifname': 'ae5.0', 'card': 11, 'host': 'styri'},
            {'traff': 90000, 'packets': 100},
        ],
    ]

    exp = [
        [
            1553513180,
            {'counter': 'TO-SPIDER', 'direction': 'input', 'ifname': 'ae5.0', 'host': 'styri'},
            {'traff': 160000, 'packets': 180},
        ],
        [
            1553513180,
            {'counter': 'TO-SPIDER2', 'direction': 'input', 'ifname': 'ae5.0', 'host': 'styri'},
            {'traff': 160000, 'packets': 180},
        ],
    ]
    assert exp == _run_fn_or_gen(sum_all_values(drop_keys=["card"]), in_data=in_data)


def test_parse_cisco_power_unit():
    for in_data, exp in [
        [b"centiAmpsAt42v", 0.42],
        [b"Amps @ 12V", 12],
    ]:
        res = call_sendgen(parse_cisco_power_unit, send=[(TEST_KEY, in_data, TS)])
        assert res[0][1] == exp


@patch("noc.grad.grad.lib.pipeline_generic_functions.monotonic")  # freezegun doesn't support monotonic
def test_rearrange_partial_data(monotonic):
    counters = (Oid("TESTMIB.name", tuple()), Oid("TESTMIB.rx", tuple()), Oid("TESTMIB.tx", tuple()))
    max_duration = 300
    test_job = make_job(counters)

    fn = rearrange_partial_data(test_job, max_duration=max_duration)

    in_data = [
        [TS_PERIOD_0, {'name': 'host1'}, {'rx': 123, 'tx': 123}],
        [TS_PERIOD_0, {'name': 'host2'}, {'rx': 123, 'tx': 123}],
    ]
    monotonic.return_value = TS_PERIOD_0 + 1
    res = fn.send(in_data)
    assert in_data == res

    in_data = [[TS_PERIOD_1, {'name': 'host1'}, {'tx': 123}], [TS_PERIOD_1, {'name': 'host2'}, {'rx': 456}]]
    exp = []
    monotonic.return_value = TS_PERIOD_1 + 1
    res = fn.send(in_data)
    assert exp == res

    in_data = [
        [TS_PERIOD_1, {'name': 'host1'}, {'rx': 321}],
        [TS_PERIOD_1, {'name': 'host2'}, {'tx': 654}],
        [TS_PERIOD_2, {'name': 'host1'}, {'tx': 333, "rx": 333}],
        [TS_PERIOD_2, {'name': 'host2'}, {'tx': 333, "rx": 333}],
    ]
    exp = [
        [TS_PERIOD_1, {'name': 'host1'}, {'rx': 321, 'tx': 123}],
        [TS_PERIOD_1, {'name': 'host2'}, {'rx': 456, 'tx': 654}],
        [TS_PERIOD_2, {'name': 'host1'}, {'tx': 333, "rx": 333}],
        [TS_PERIOD_2, {'name': 'host2'}, {'tx': 333, "rx": 333}],
    ]
    monotonic.return_value = TS_PERIOD_2 + 1
    res = fn.send(in_data)

    assert exp == res

    in_data1 = [[TS_PERIOD_3, {'name': 'host1'}, {'rx': 666}], [TS_PERIOD_4, {'name': 'host1'}, {'rx': 666}]]
    in_data2 = [[TS_PERIOD_4, {'name': 'host1'}, {'tx': 777}]]
    exp = [[TS_PERIOD_4, {'name': 'host1'}, {'rx': 666, 'tx': 777}]]
    monotonic.return_value = TS_PERIOD_3 + 1
    res = fn.send(in_data1)
    assert not res

    monotonic.return_value = TS_PERIOD_4 + 1
    res = fn.send(in_data2)
    assert exp == res

    monotonic.return_value = TS_PERIOD_4 + max_duration + 1
    res = fn.send([])
    assert not res
    assert not fn.gi_frame.f_locals["tmp_data"]
    assert not fn.gi_frame.f_locals["ts_deque"]


# def _check_blink_bug(test_data, max_retention=1):
#     fixer = blink_bug_fixer("test job", max_retention=max_retention)
#     for data in test_data:
#         send, expected = data
#         if expected:
#             expected = [(TEST_KEY, expected[1], expected[0])]
#         logging.debug("data     %s", data)
#         logging.debug("expected %s", expected)
#         kvts_list = [(TEST_KEY, send[1], send[0])]
#         res = fixer.send(kvts_list)
#         assert res == expected
#
# def test_blink_bug_multi_key():
#     fixer = blink_bug_fixer("test job")
#     test_data = (((TEST_KEY, [0, 100], []), (TEST_KEY2, [0, 100], [])),
#                  ((TEST_KEY, [30, 300], [0, 100]), (TEST_KEY2, [30, 300], [0, 100])),
#                  ((TEST_KEY, [60, 600], [30, 300]), (TEST_KEY2, [60, 600], [30, 300])),
#                  ((TEST_KEY, [90, 0], [60, 600]), (TEST_KEY2, [90, 900], [60, 600])),
#                  ((TEST_KEY, [120, 0], []), (TEST_KEY2, [120, 1200], [90, 900])),
#                  ((TEST_KEY, [150, 1500], []), (TEST_KEY2, [150, 1500], [120, 1200])),
#                  ((TEST_KEY, [180, 1800], [150, 1500]), (TEST_KEY2, [180, 1800], [150, 1500])),
#                  )
#     for data in test_data:
#         new_kvts = fixer.send([(d[0], d[1][1], d[1][0]) for d in data])
#         expected = [(d[0], d[2][1], d[2][0]) for d in data if d[2]]
#         assert (sorted(expected), sorted(new_kvts))
#
# def test_blink_bug_low():
#     # тест бага когда в SNMP счетчике иногда появляется 0 вместо реального значения
#     test_data = ([[1000, 100],  []],
#                  [[1005, 300], [1000, 100]],
#                  [[1010, 700], [1005, 300]],
#                  [[1015, 0], [1010, 700]],  # вот это баг. тут должно было прилететь значние 900
#                  [[1019, 1100], []],  # тут счетчик заработал правильно
#                  [[1020, 1200], [1019, 1100]],
#                  )
#     _check_blink_bug(test_data)
#
# def test_blink_bug_high():
#     test_data = ([[1000, 100],  []],
#                  [[1005, 300], [1000, 100]],
#                  [[1010, 700], [1005, 300]],
#                  [[1015, 70000], [1010, 700]],  # вот это баг. тут должно было прилететь значние 900
#                  [[1016, 800], []],  # а это отложенная реакция на баг
#                  [[1018, 900], [1016, 800]],
#                  [[1019, 1100], [1018, 900]],
#                  [[1020, 1200], [1019, 1100]],
#                  )
#     _check_blink_bug(test_data)
#
# def test_blink_bug_and_reboot():
#     # проверка что blink_bug режим нормально сработает в случае нулевых значение после сброса счетчика
#     test_data = ([[1000, 100], []],
#                  [[1005, 300], [1000, 100]],
#                  [[1010, 700], [1005, 300]],
#                  [[1011, 700], [1010, 700]],  # счетчик не меняется
#                  [[1015, 0], [1011, 700]],  # счетчик сброшен
#                  [[1600, 0], []],
#                  [[1700, 0], []],
#                  [[1750, 0], []],
#                  [[1800, 0], []],
#                  [[1825, 0], [1800, 0]],
#                  )
#     _check_blink_bug(test_data)
#
# def test_blink_bug_not_null():
#     test_data = ([[1000, 100],  []],
#                  [[1005, 300], [1000, 100]],
#                  [[1010, 700], [1005, 300]],
#                  [[1015, 50], [1010, 700]],  # вот это баг. тут должно было прилететь значние 900
#                  [[1020, 1100], []],  # тут счетчик заработал правильно. должны получить (1100 - 700)/(1020-1010)
#                  [[1030, 1200], [1020, 1100]],
#                  )
#     _check_blink_bug(test_data)


# def _test_profile_kvts_to_mapdata():
#     ts = 10
#     data = []
#     for sensor in range(200):
#         for index in range(800):
#             kvts = ((("name", "i%s" % index), ('sensor', 'sensor%s' % sensor)), 0, ts)
#             data.append(kvts)
#     with tempfile.NamedTemporaryFile() as f:
#         cProfile.runctx("kvts_to_mapdata(data)", globals(), locals(), f.name)
#         s = pstats.Stats(f.name)
#         s.strip_dirs().sort_stats("time").print_stats()


def test_sum_counters():
    data = [
        [
            TS,
            {'ifname': IFNAME, 'host': HOST},
            {
                'tx': 1,
                'rx': 1,
                'rx_nunicast': 1,
                'rx_drop': 1,
                'rx_errs': 1,
                'tx_nunicast': 1,
                'tx_drop': 1,
                'tx_errs': 1,
                'tx_unicast': 1,
                'rx_unicast': 1,
                'flap': 0.0,
                'oper_status': 1.0,
                'speed': 14100.0,
            },
        ]
    ]
    exp = [
        [
            TS,
            {'ifname': IFNAME, 'host': HOST},
            {
                'tx': 1,
                'rx': 1,
                'rx_nunicast': 1,
                'rx_drop': 1,
                'rx_errs': 1,
                'tx_nunicast': 1,
                'tx_drop': 1,
                'tx_errs': 1,
                'tx_unicast': 1,
                'rx_unicast': 1,
                'flap': 0.0,
                'oper_status': 1.0,
                'speed': 14100.0,
                'tx_packets': 4,
                'rx_packets': 4,
            },
        ]
    ]
    res = call_sendgen(sum_counters, send=data, job=make_job())
    assert res == exp
    data = [
        [
            TS,
            {'ifname': IFNAME, 'host': HOST},
            {
                'tx': 0.0,
                'rx': 0.0,
                'rx_nunicast': 0.0,
                'rx_drop': 0.0,
                'rx_errs': 0.0,
                'tx_nunicast': 0.0,
                'tx_drop': 0.0,
                'tx_errs': 0.0,
                'tx_unicast': 0.0,
                'rx_unicast': 0.0,
                'oper_status': 2.0,
            },
        ]
    ]
    exp = [
        [
            TS,
            {'ifname': IFNAME, 'host': HOST},
            {
                'tx': 0.0,
                'rx': 0.0,
                'rx_nunicast': 0.0,
                'rx_drop': 0.0,
                'rx_errs': 0.0,
                'tx_nunicast': 0.0,
                'tx_drop': 0.0,
                'tx_errs': 0.0,
                'tx_unicast': 0.0,
                'rx_unicast': 0.0,
                'oper_status': 2.0,
                'tx_packets': 0.0,
                'rx_packets': 0.0,
            },
        ]
    ]
    res = call_sendgen(sum_counters, send=data, job=make_job())
    assert res == exp


def test_sum_counters_old():
    data = [
        [
            TS,
            {"ifname": IFNAME, "host": HOST},
            {
                "rx": 10000,
                "rx_nunicast": 1,
                "rx_drop": 1,
                "rx_errs": 1,
                "rx_unicast": 1,
                "tx": 10000,
                "tx_nunicast": 1,
                "tx_drop": 1,
                "tx_errs": 1,
                "tx_unicast": 1,
                "flap": 0,
                "oper_status": 2,
                "speed": 0,
            },
        ]
    ]

    exp = [
        [
            TS,
            {"ifname": IFNAME, "host": HOST},
            {
                "rx": 10000,
                "rx_packets": 4,
                "rx_drop": 1,
                "rx_errs": 1,
                "rx_unicast": 1,
                "tx": 10000,
                "tx_packets": 4,
                "tx_drop": 1,
                "tx_errs": 1,
                "tx_unicast": 1,
                "flap": 0,
                "oper_status": 2,
                "speed": 0,
            },
        ]
    ]
    res = call_sendgen(sum_ifmib_counters_old, send=data, job=make_job())
    assert res == exp


def test_sum_counters_new():
    data = [
        [
            TS,
            {"ifname": IFNAME, "host": HOST},
            {
                "rx": 10000,
                "rx_broadcast": 1,
                "rx_multicast": 1,
                "rx_drop": 1,
                "rx_errs": 1,
                "rx_unicast": 1,
                "tx": 10000,
                "tx_broadcast": 1,
                "tx_multicast": 1,
                "tx_drop": 1,
                "tx_errs": 1,
                "tx_unicast": 1,
                "flap": 0,
                "oper_status": 2,
                "speed": 0,
            },
        ]
    ]

    exp = [
        [
            TS,
            {"ifname": IFNAME, "host": HOST},
            {
                "rx": 10000,
                "rx_packets": 5,
                "rx_drop": 1,
                "rx_errs": 1,
                "rx_unicast": 1,
                "tx": 10000,
                "tx_packets": 5,
                "tx_drop": 1,
                "tx_errs": 1,
                "tx_unicast": 1,
                "flap": 0,
                "oper_status": 2,
                "speed": 0,
            },
        ]
    ]
    res = call_sendgen(sum_ifmib_counters_new, send=data, job=make_job())
    assert res == exp


def test_parse_conf_fn():
    assert _partial_cmp(
        parse_conf_fn(("sum_all_values", {"drop_keys": "card"}), _available_pp_functions, job=make_job()),
        partial(sum_all_values, drop_keys="card"),
    )


PARTY_CASES = [
    [
        [
            "iva-b-host1",
            "iva-b-host2",
            "sas1-host1",
            "vla1-host1",
            "vla1-host2",
            "vla-grad1",
            "sas-grad1",
            "iva-grad1",
            "iva-grad2",
        ],
        ["vla-grad1", "sas-grad1", "iva-grad1", "iva-grad2"],
        {
            "vla-grad1": ["vla1-host1", "vla1-host2", "vla-grad1"],
            "sas-grad1": ["sas1-host1", "sas-grad1"],
            "iva-grad1": ["iva-b-host1", "iva-grad2"],
            "iva-grad2": ["iva-b-host2", "iva-grad1"],
        },
    ],
    [
        [
            "vla1-host1",
            "vla1-host2",
            "sas1-host1",
            "iva-b-host1",
            "iva-b-host2",
            "man1-host1",
            "man-host2",
            "myt-host1",
            "myt-host2",
            "myt-host3",
            "vla-grad1",
            "sas-grad1",
            "iva-grad1",
            "iva-grad2",
        ],
        ["vla-grad1", "sas-grad1", "iva-grad1", "iva-grad2"],
        {
            "vla-grad1": ["vla1-host1", "vla1-host2", "myt-host1", "vla-grad1"],
            "sas-grad1": ["sas1-host1", "myt-host2", "sas-grad1", "man-host2"],
            "iva-grad1": ["iva-b-host1", "man1-host1", "iva-grad2"],
            "iva-grad2": ["iva-b-host2", "iva-grad1", "myt-host3"],
        },
    ],
    # # дефолтное распределние при наличии в party сервера не из ДЦ:
    [
        [
            "iva-b-host1",
            "iva-b-host2",
            "sas1-host1",
            "vla1-host1",
            "vla1-host2",
            "man1-host1",
            "man1-host6",
            "man1-host5",
            "man1-host4",
            "man1-host3",
            "man1-host2",
            "myt-host1",
            "vla1-host33",
            "vla2-host32",
            "iva-hostX",
            "myt-host2",
            "vla-grad1",
            "sas-grad1",
            "iva-grad1",
            "fake-grad2",
        ],
        ["vla-grad1", "sas-grad1", "iva-grad1", "fake-grad2"],
        {
            "vla-grad1": [
                "vla1-host1",
                "vla1-host2",
                "vla1-host33",
                "vla2-host32",
                "vla-grad1",
                "man1-host6",
                "man1-host3",
                "myt-host1",
            ],
            "sas-grad1": ["sas1-host1", "sas-grad1", "myt-host2", "fake-grad2"],
            "iva-grad1": [
                "iva-b-host1",
                "iva-b-host2",
                "iva-hostX",
                "iva-grad1",
                "man1-host5",
                "man1-host4",
                "man1-host2",
            ],
            "fake-grad2": ["man1-host1"],
        },
    ],
]


# TODO: AsyncMock python3.8
def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


def _add_auto_tags(dc_tags, hosts):
    res = {}
    for host in hosts:
        res[host] = None
        for dc_tag_id, dc in dc_tags.items():
            if host.startswith(dc):
                res[host] = dc_tag_id
                break

    return res


@pytest.mark.parametrize("hosts, comrades, expect", PARTY_CASES)
def test_per_dc_split(hosts: List[str], comrades: List[str], expect: Dict[str, List[str]]):
    assert len(hosts) == len(set(hosts))  # no dups
    seen_hosts = []
    dc_tags = {"iva": "iva", "vla": "vla", "sas": "sas", "man": "man", "myt": "myt"}
    hosts_tags = _add_auto_tags(dc_tags, hosts)
    for my_id, my_hosts in expect.items():
        res = per_dc_split(hosts_tags, comrades, my_id)
        assert sorted(my_hosts) == sorted(res)
        seen_hosts += res

    assert sorted(seen_hosts) == sorted(hosts)


SPLIT_CASES = [
    [
        [
            'cipt-cms-storage-test.yndx.net',
            'cipt-cms-recorder1.yndx.net',
            'cipt-cms-recorder-test.yndx.net',
            'cipt-cms-recorder2.yndx.net',
            'cipt-cms-storage1.yndx.net',
            'cipt-cms-storage2.yndx.net',
        ],
        ['myt-grad1.yndx.net', 'sas1-grad2.yndx.net'],
        {
            'myt-grad1.yndx.net': [
                'cipt-cms-storage-test.yndx.net',
                'cipt-cms-recorder1.yndx.net',
                'cipt-cms-recorder-test.yndx.net',
                'cipt-cms-storage1.yndx.net',
                'cipt-cms-storage2.yndx.net',
            ],
            'sas1-grad2.yndx.net': ['cipt-cms-recorder2.yndx.net'],
        },
    ],
]


@pytest.mark.parametrize("hosts, comrades, expect", SPLIT_CASES)
def test_equal_split_all_order(hosts: List[str], comrades: List[str], expect: Dict[str, List[str]]):
    comrades = comrades.copy()
    hosts = hosts.copy()
    for exp_hosts in expect.values():
        exp_hosts.sort()
    for _ in range(len(comrades)):
        comrades.append(comrades.pop(0))
        for _ in range(len(hosts)):
            hosts.append(hosts.pop(0))
            res = equal_split_all(hosts, comrades)
            for res_hosts in res.values():
                res_hosts.sort()
            assert res == expect


def test_drop_zero_value():
    data = [
        ((('component', ''), ('sensor', 'temp')), 0, 1554390786),
        ((('component', 'Power Supply 0 @ 0/0/*'), ('sensor', 'temp')), 0, 1554390786),
        ((('component', 'FPC: JNP48Y8C-CHAS @ 0/*/*'), ('sensor', 'temp')), 40, 1554390786),
        ((('component', 'PIC: 48x25G-8x100G @ 0/0/*'), ('sensor', 'temp')), 0, 1554390786),
        ((('component', 'Routing Engine 0'), ('sensor', 'temp')), 25, 1554390786),
    ]
    res = call_sendgen(drop_zero_value, send=data)
    exp = [
        ((('component', 'FPC: JNP48Y8C-CHAS @ 0/*/*'), ('sensor', 'temp')), 40, 1554390786),
        ((('component', 'Routing Engine 0'), ('sensor', 'temp')), 25, 1554390786),
    ]
    assert res == exp


HUAWEI_NETWORK_PRE = [
    [
        "проставляем pause и jumbo для Eth-Trunk",
        [
            TS_PERIOD_0,
            {"ifname": "Eth-Trunk1", "host": "host"},
            {
                "tx": 0,
                "rx": 0,
                "rx_nunicast": 0,
                "rx_drop": 0,
                "rx_errs": 0,
                "tx_nunicast": 0,
                "tx_drop": 0,
                "tx_errs": 0,
                "tx_unicast": 0,
                "rx_multicast": 0,
                "rx_broadcast": 0,
                "tx_multicast": 0,
                "tx_broadcast": 0,
                "rx_unicast": 0,
                "flap": 0,
                "oper_status": 1,
                "speed": 1000,
            },
        ],
        [
            TS_PERIOD_0,
            {"ifname": "Eth-Trunk1", "host": "host"},
            {
                "tx": 0,
                "rx": 0,
                "rx_nunicast": 0,
                "rx_drop": 0,
                "rx_errs": 0,
                "tx_nunicast": 0,
                "tx_drop": 0,
                "tx_errs": 0,
                "tx_unicast": 0,
                "rx_multicast": 0,
                "rx_broadcast": 0,
                "tx_multicast": 0,
                "tx_broadcast": 0,
                "rx_unicast": 0,
                "flap": 0,
                "oper_status": 1,
                "speed": 1000,
                "rx_pause": 0,
                "tx_pause": 0,
                "rx_jumbo": 0,
                "tx_jumbo": 0,
            },
        ],
    ],
]


@pytest.mark.parametrize("comment, test_input, expected", HUAWEI_NETWORK_PRE)
def test_huawei_network_pre(comment, test_input, expected):
    res = call_sendgen(huawei_network_pre, send=[test_input])
    assert res[0] == expected, comment


def test_pdu_recalc():
    test_input = [TS, {'inlet_label': 'I1', 'host': HOST}, {'frequency_decimal_digits': 1.0, 'frequency': 500.0}]
    expected = [[TS, {'inlet_label': 'I1', 'host': HOST}, {'frequency': 50.0}]]
    res = call_sendgen(pdu_recalc, send=[test_input])
    assert res == expected


def test_jnx_xml_to_json():
    environment = get_data_content("jnx_environment_xml")
    environment = parse_netconf_xml_reply_from_str(environment)
    thresholds = get_data_content("jnx_thresholds_xml")
    thresholds = parse_netconf_xml_reply_from_str(thresholds)
    assert environment == json.loads(get_data_content("jnx_environment_res_json"))
    assert thresholds == {
        'temperature-threshold-information': {
            'temperature-threshold': [
                {
                    'name': {'$': 'Chassis default'},
                    'fan-normal-speed': {'$': 48},
                    'fan-high-speed': {'$': 54},
                    'bad-fan-yellow-alarm': {'$': 55},
                    'bad-fan-red-alarm': {'$': 75},
                    'yellow-alarm': {'$': 65},
                    'red-alarm': {'$': 75},
                    'fire-shutdown': {'$': 100},
                },
                {
                    'name': {'$': 'Routing Engine'},
                    'fan-normal-speed': {'$': 65},
                    'fan-high-speed': {'$': 70},
                    'bad-fan-yellow-alarm': {'$': 75},
                    'bad-fan-red-alarm': {'$': 80},
                    'yellow-alarm': {'$': 85},
                    'red-alarm': {'$': 95},
                    'fire-shutdown': {'$': 100},
                },
            ]
        },
        'cli': {'banner': {}},
    }


def test_ios_transceiver():
    content = get_testdata("ios_transceiver_details_xml").decode()
    res = ios_transceiver(content, 1223, {})
    exp = get_kvts_data_content("ios_transceiver_details_res")
    assert res == exp


def test_arista_transceiver():
    transceiver_data = get_data_content("arista_show_interfaces_transceiver_detail_json", is_json=True)
    ifaces_status_data = get_data_content("arista_show_interfaces_status_json", is_json=True)
    expected = get_kvts_data_content("arista_show_interfaces_transceiver_result_json")
    ifaces_status = parse_arista_ifaces_status(ifaces_status_data)
    result = arista_transceiver(transceiver_data, ts=TS, ifaces_status=ifaces_status)
    assert result == expected


OID_STRS = [
    ["50.55.49.48", "2710"],
]


@pytest.mark.parametrize("test_input, expected", OID_STRS)
def test_oid_to_str(test_input, expected):
    assert oid_to_str(test_input) == expected


def test_calc_fraction():
    fn = calc_fraction("tx", "rx", "r", True)
    res = fn.send([(TS, {"tag": "value"}, {"rx": 200, "tx": 200})])
    assert res == [(TS, {"tag": "value"}, {"rx": 200, "tx": 200, "r": 100.0})]
    res = fn.send([(TS, {"tag": "value"}, {"rx": 200, "tx": 50})])
    assert res == [(TS, {"tag": "value"}, {"rx": 200, "tx": 50, "r": 25.0})]
    res = fn.send([(TS, {"tag": "value"}, {"rx": 0, "tx": 0})])
    assert res == [(TS, {"tag": "value"}, {"rx": 0, "tx": 0, "r": 0})]
    fn2 = calc_fraction("used", "total", "free_perc", percent=True, percent_invert=True)
    res = fn2.send([(TS, {"tag": "value"}, {"used": 20, "total": 200})])
    assert res == [(TS, {"tag": "value"}, {"free_perc": 90, "used": 20, "total": 200})]


ADVA_ENTITY = [
    [
        "/mit/me/1/eqh/shelf,1/eqh/slot,5/eq/card/ptp/cl,1/ctp/et100/mac/pm/crnt/m15,MacNIrx",
        (
            "1/5/c1",
            "et100/mac",
            "m15",
            "MacNIrx",
        ),
    ],
    [
        "/mit/me/1/eqh/shelf,1/eqh/slot,4/eq/card/ptp/nw,2/ctp/ot100/ctp/odu4/odu4/pm/crnt/day,NearEnd",
        (
            "1/4/n2",
            "ot100/odu4",
            "day",
            "NearEnd",
        ),
    ],
    [
        "/mit/me/1/eqh/shelf,1/eqh/slot,5/eq/card/ptp/nw,2/opt/pm/crnt/day,Power",
        (
            "1/5/n2",
            "/opt",
            "day",
            "Power",
        ),
    ],
]


@pytest.mark.parametrize("test_input, expected", ADVA_ENTITY)
def test_adva_convert_entity(test_input, expected):
    assert adva_rest.convert_entity(test_input) == expected


CONF_FNS = [
    ["test", [("test", FrozenDict())]],
    [["test", {1: 2}], [("test", FrozenDict({1: 2}))]],
    [["test", "test2"], [("test", FrozenDict()), ("test2", FrozenDict())]],
    [["test", ["test2"]], [("test", FrozenDict()), ("test2", FrozenDict())]],
]


@pytest.mark.parametrize("test_input, expected", CONF_FNS)
def test_parse_fn_from_conf(test_input, expected):
    res = parse_fn_from_conf(test_input)
    assert res == expected


def test_recalc_arista_queue():
    data = [[TS, {"index": "65.0.0", "host": HOST}, {"queue_passed_bytes": 0.0}]]
    job = make_job()
    job.set_context({"index_cache": {"ifmib": {"65": {"ifname": IFNAME}}}})
    res = call_sendgen(recalc_arista_queue, send=data, job=job)
    exp = [[TS, {"host": HOST, "ifname": IFNAME, "packet_type": "unicast", "queue": "0"}, {"queue_passed_bytes": 0.0}]]
    assert res == exp


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ["Lane0:-0.04, Lane1:-0.21, Lane2:0.10, Lane3:-0.05", [-0.04, -0.21, 0.10, -0.05]],
        ["-2.22", [-2.22]],
    ],
)
def test_parse_netconf_vrp_s6870_power(test_input, expected):
    res = parse_netconf_vrp_s6870_power(test_input)
    assert res == expected


@pytest.mark.parametrize(
    "filtr, test_keys, expected",
    [
        [
            {"ifname": r"^local$"},
            {"ifname": "local", "olo": "123"},
            [],
        ],
        [
            {"ifname": r"^local$"},
            {"ifname": "olo"},
            [{"ifname": "olo"}],
        ],
    ],
)
def test_filter_keys(filtr, test_keys, expected):
    res = call_sendgen(filter_keys, filtr=filtr, send=[[0, test_keys, {}]])
    res_ret = []
    for i in res:
        res_ret.append(i[1])
    assert res_ret == expected


@pytest.mark.parametrize(
    "data, expected",
    [
        [
            [[0, {"k": "v"}, {"test": 10}], [10, {"k": "v"}, {"test": 1}]],
            [[0, {"k": "v"}, {"test": 0}], [10, {"k": "v"}, {"test": 1}]],
        ],
    ],
)
def test_uptime_reset_count(data, expected):
    res = call_sendgen(uptime_reset_count, keys=["test"], max_ts_delta=720, send=data)
    assert res == expected


IFALIAS = [
    ['"FABERLIK"', "FABERLIK"],
    ["'FABERLIK'", "FABERLIK"],
]


@pytest.mark.parametrize("test_input, expected", IFALIAS)
def test_strip_alias(test_input, expected):
    assert strip_alias(test_input) == expected


def test_ret_max_for_period():
    keys = {"ifname": IFNAME, "host": HOST}
    gen = ret_max_for_period(keys=["rx"], duration=30)
    res = gen.send([[0, keys, {"rx": 0, "tx": 1}]])
    assert res == [[0, keys, {"tx": 1}]]
    res = gen.send([[20, keys, {"rx": 100, "tx": 2}]])
    assert res == [[20, keys, {"tx": 2}]]
    res = gen.send([[40, keys, {"rx": 2, "tx": 3}]])
    assert res == [[40, keys, {"tx": 3}], [40, keys, {"rx": 100}]]
    res = gen.send([[61, keys, {"rx": 2, "tx": 3}]])
    assert res == [[61, keys, {"tx": 3}], [61, keys, {"rx": 100}]]
    res = gen.send([[91, keys, {"rx": 2, "tx": 3}]])
    assert res == [[91, keys, {"tx": 3}], [91, keys, {"rx": 2}]]


FN_FOR_PERIOD_CASES = [
    ["много нулей", 30, [0, 100, 0, 0], [100]],
    ["всё норм", 30, [100, 100, 100, 100, 100], [100, 100]],
]


@pytest.mark.parametrize("comment, duration, test_input, expected", FN_FOR_PERIOD_CASES)
def test_apply_fn_for_period(comment, duration, test_input, expected):
    fixer = apply_fn_for_period(fn=max, duration=duration)
    step = 10
    res = []
    ts = 0
    for data in test_input:
        ts += step
        kvts_list = [(TEST_KEY, data, ts)]
        tmp_res = fixer.send(kvts_list)
        for k, v, ts in tmp_res:
            res.append(v)
    assert res == expected, comment


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ["10.1.2.1", "10.1.2.1"],
        ["254.128.0.0.0.0.0.0.0.0.0.0.0.0.10.26.0.0.0.4", "fe80::a1a"],
    ],
)
def test_oid_to_ip(test_input, expected):
    res = oid_to_ip(test_input)
    assert res == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ["host1", "shard57"],
        ["host2", "shard85"],
        ["host3", "shard81"],
    ],
)
def test_make_shard_sha1_last4(test_input, expected):
    res = make_shard_sha1_last4(test_input)
    assert res == expected


# badger
@pytest.mark.parametrize(
    "test_input, expected",
    [
        ["<alice>bob</alice>", {"alice": {"$": "bob"}}],
        [
            "<alice><bob>charlie</bob><david>edgar</david></alice>",
            {"alice": {"bob": {"$": "charlie"}, "david": {"$": "edgar"}}},
        ],
        ["<alice><bob>charlie</bob><bob>david</bob></alice>", {"alice": {"bob": [{"$": "charlie"}, {"$": "david"}]}}],
        ['<alice charlie="david">bob</alice>', {"alice": {"$": "bob", "@charlie": "david"}}],
        # one lane
        [
            """<TABLE_lane><ROW_lane><lane_number>1</lane_number></ROW_lane></TABLE_lane>""",
            {"TABLE_lane": {"ROW_lane": {"lane_number": {"$": 1}}}},
        ],
        # two lanes
        [
            """<TABLE_lane><ROW_lane><lane_number>1</lane_number></ROW_lane><ROW_lane><lane_number>2</lane_number></ROW_lane></TABLE_lane>""",
            {"TABLE_lane": {"ROW_lane": [{"lane_number": {"$": 1}}, {"lane_number": {"$": 2}}]}},
        ],
        # namespace test
        [
            """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/20.4R0/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
        <commit-information>
        <commit-history>
        <sequence-number>49</sequence-number>
        <user>gslv</user>
        <client>cli</client>
        <date-time junos:seconds="1625483477">2021-07-05 14:11:17 MSK</date-time>
        </commit-history>
        </commit-information>
        </rpc-reply>""",
            {
                'rpc-reply': {
                    'commit-information': {
                        'commit-history': {
                            'sequence-number': {'$': 49},
                            'user': {'$': 'gslv'},
                            'client': {'$': 'cli'},
                            'date-time': {'@seconds': 1625483477, '$': '2021-07-05 14:11:17 MSK'},
                        }
                    },
                    '@message-id': 1,
                }
            },
        ],
    ],
)
def test_xml_to_dict(test_input, expected):
    res = xml_to_dict(defusedxml.ElementTree.fromstring(test_input))
    assert res == expected
