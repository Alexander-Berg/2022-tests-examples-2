from unittest.mock import patch

from noc.grad.grad.lib import snmp_helper
from noc.grad.grad.lib.pipeline import pipeline
from noc.grad.grad.lib.snmp_helper import get_fns_per_sensor, Oid, DEFAULT_OID_OPTIONS
from noc.grad.grad.lib.snmp_mib import snmp_oid_schema
from noc.grad.grad.lib.structures import FrozenDict
from noc.grad.grad.pollers.snmp_poller import Poller
from noc.grad.grad.lib.test_functions import MIBS, make_job

snmp_oid_schema.validate(MIBS)

patches = []


def setup_module(module):
    patches.append(patch.dict(snmp_helper.MIBS, MIBS, clear=True))
    for p in patches:
        p.start()


def teardown_module(module):
    for p in patches:
        p.stop()


def test_get_oid_by_name():
    assert snmp_helper.get_oid_config("TESTMIB", "name") == ('1.2.1', {'type': 'key', 'name': 'name'})


def test_resolve_counters():
    counters = (Oid("TESTMIB.rx", tuple()), Oid("TESTMIB.tx", tuple()))
    # mibs, oid_groups, oid_types, oid_to_name, oid_postproc, _, _, _, _, oid_data_type = snmp_helper.resolve_counters(counters)
    counters_data = snmp_helper.resolve_counters(counters)

    assert counters_data.oid_postproc == {'TESTMIB': {'rx': 'delta', 'tx': 'delta'}}
    assert counters_data.oid_types == {'value': ('1.3.4', '1.3.5'), 'key': (), 'nokey': ('TESTMIB',)}
    assert counters_data.oid_to_name == {'1.3.4': ('TESTMIB', 'rx'), '1.3.5': ('TESTMIB', 'tx')}
    assert counters_data.oid_groups_by_option == {'TESTMIB': {DEFAULT_OID_OPTIONS: ('1.3.4', '1.3.5')}}
    assert counters_data.oid_data_type == {'TESTMIB': {'rx': None, "tx": None}}


def test_parse_snmp_data():
    data = [
        ("1.2.1", "1", "test_name", 1),
        ("1.3.4", "1", "123", 1),
    ]
    counters = (
        Oid("TESTMIB.name", tuple()),
        Oid("TESTMIB.rx", tuple()),
    )
    res, _ = snmp_helper.prepare_snmp_data(data, make_job(counters), counters)
    assert res == [((('name', 'test_name'), ('sensor', 'rx')), '123', 1)]


# def test_duplicated_keys(caplog):
#     """не должно быть дубликата индексов"""
#     data = [("1.2.1", "2", "test_ifname0", 1),
#             ("1.2.1", "1", "test_ifname", 1),
#             ("1.2.1", "1", "test_ifname2", 1),
#             ]
#     counters = (Oid("TESTMIB.name", tuple()), Oid("TESTMIB.rx", tuple()),)
#     with caplog.at_level(logging.DEBUG):
#         snmp_helper.prepare_snmp_data(data, make_job(counters), counters, consistency_check=True)
#     assert caplog.record_tuples[0][2] == 'duplicated key. mib=1.2.1, indexes=[\'1\']'


# def test_duplicated_values(caplog):
#     data = [("1.2.1", "1", "test_ifname", 1234),
#             ("1.3.4", "1", "ok", 1234),
#             ("1.3.4", "1", "notok", 1234),
#             ]
#     counters = (Oid("TESTMIB.name", tuple()), Oid("TESTMIB.rx", tuple()),)
#     with caplog.at_level(logging.DEBUG):
#         snmp_helper.prepare_snmp_data(data, make_job(counters), counters, consistency_check=True)
#     assert "duplicated value. mib=TESTMIB, oid_name=rx, index=1 new_value=notok, prev_value=(\'ok\', 1234)" == caplog.record_tuples[0][2]


# def test_no_keys(caplog):
#     data = [("1.2.1", "1", "test_ifname", 1234),
#             ("1.3.4", "3", "ok", 1234),
#             ]
#     counters = (Oid("TESTMIB.name", tuple()), Oid("TESTMIB.rx", tuple()),)
#     with caplog.at_level(logging.DEBUG):
#         snmp_helper.prepare_snmp_data(data, make_job(counters), counters, consistency_check=True)
#     assert caplog.record_tuples[0][2] == "found extra keys. mib=TESTMIB, indexes={'1'}"
#     assert caplog.record_tuples[1][2] == "found extra values. mib=TESTMIB, indexes={'3'}"


# def test_no_index2(caplog):
#     data = [("1.3.4", "3", "ok", 1234),
#             ]
#     counters = (Oid("TESTMIB.name", tuple()), Oid("TESTMIB.rx", tuple()),)
#     with caplog.at_level(logging.DEBUG):
#         snmp_helper.prepare_snmp_data(data, make_job(counters), counters, consistency_check=True)
#     assert caplog.record_tuples[0][2] == "found extra values. mib=TESTMIB, indexes={'3'}"


def test_data1():
    counters = (
        Oid("TESTMIB.name", tuple()),
        Oid("TESTMIB.rx", tuple()),
        Oid("TESTMIB.cps", tuple()),
    )
    fns_per_sensor = get_fns_per_sensor(counters, sample_period=False)
    job = make_job(counters)
    dp = pipeline(job, fns_per_sensor)
    ts = 100
    data = [
        ("1.2.1", "1", "test_ifname", ts),
        ("1.3.6", "1", 100, ts),
        ("1.3.4", "1", 100, ts),
    ]
    raw_data, _ = snmp_helper.prepare_snmp_data(data, job, counters)
    dp.send(raw_data)

    data = [
        ("1.2.1", "1", "test_ifname", ts + 10),
        ("1.3.6", "1", 100, ts + 10),
        ("1.3.4", "1", 200, ts + 10),
    ]
    raw_data, _ = snmp_helper.prepare_snmp_data(data, job, counters)
    d1 = dp.send(raw_data)
    assert d1 == [[110, {'name': 'test_ifname'}, {'cps': 0, 'rx': 10}]]


def test_build_oid_groups1():
    oid_limit = 3
    conf_counters = (Oid("TESTMIB.name", tuple()), Oid("TESTMIB.rx", tuple()), Oid("TESTMIB.cps", tuple()))
    counters = snmp_helper.resolve_counters(conf_counters)
    indexes = FrozenDict.from_rec({"TESTMIB": {str(x): {"index": str(x)} for x in range(5)}})
    target_oid_group = ('1.3.4', '1.3.6')
    res = Poller.build_oid_groups(target_oid_group, indexes, oid_limit, counters, method="get")
    exp = (
        {
            '1.3.4.0': ('1.3.4', '0'),
            '1.3.4.1': ('1.3.4', '1'),
            '1.3.4.2': ('1.3.4', '2'),
            '1.3.4.3': ('1.3.4', '3'),
            '1.3.4.4': ('1.3.4', '4'),
            '1.3.6.0': ('1.3.6', '0'),
            '1.3.6.1': ('1.3.6', '1'),
            '1.3.6.2': ('1.3.6', '2'),
            '1.3.6.3': ('1.3.6', '3'),
            '1.3.6.4': ('1.3.6', '4'),
        },
        [
            ('1.3.4.0', '1.3.6.0'),
            ('1.3.4.1', '1.3.6.1'),
            ('1.3.4.2', '1.3.6.2'),
            ('1.3.4.3', '1.3.6.3'),
            ('1.3.4.4', '1.3.6.4'),
        ],
    )
    assert res == exp


def test_extra_index():
    oid_limit = 3
    conf_counters = (Oid("TESTMIB2.name", tuple()), Oid("TESTMIB2.value", tuple()), Oid("TESTMIB2.value2", tuple()))
    counters = snmp_helper.resolve_counters(conf_counters)
    indexes = FrozenDict.from_rec({"TESTMIB2": {str(x): {"index": str(x)} for x in range(1, 6)}})
    target_oid_group = (
        "1.5.2.%s.8",
        "1.5.2.%s.9",
    )
    res = Poller.build_oid_groups(target_oid_group, indexes, oid_limit, counters, method="get")
    exp = (
        {
            '1.5.2.1.8': ('1.5.2.%s.8', '1'),
            '1.5.2.2.8': ('1.5.2.%s.8', '2'),
            '1.5.2.3.8': ('1.5.2.%s.8', '3'),
            '1.5.2.4.8': ('1.5.2.%s.8', '4'),
            '1.5.2.5.8': ('1.5.2.%s.8', '5'),
            '1.5.2.1.9': ('1.5.2.%s.9', '1'),
            '1.5.2.2.9': ('1.5.2.%s.9', '2'),
            '1.5.2.3.9': ('1.5.2.%s.9', '3'),
            '1.5.2.4.9': ('1.5.2.%s.9', '4'),
            '1.5.2.5.9': ('1.5.2.%s.9', '5'),
        },
        [
            ('1.5.2.1.8', '1.5.2.1.9'),
            ('1.5.2.2.8', '1.5.2.2.9'),
            ('1.5.2.3.8', '1.5.2.3.9'),
            ('1.5.2.4.8', '1.5.2.4.9'),
            ('1.5.2.5.8', '1.5.2.5.9'),
        ],
    )
    assert res == exp
    res = Poller.build_oid_groups(target_oid_group, indexes, oid_limit, counters, method="next")
    exp = (
        {
            '1.5.2.1.8': ('1.5.2.%s.8', '1'),
            '1.5.2.2.8': ('1.5.2.%s.8', '2'),
            '1.5.2.3.8': ('1.5.2.%s.8', '3'),
            '1.5.2.4.8': ('1.5.2.%s.8', '4'),
            '1.5.2.5.8': ('1.5.2.%s.8', '5'),
            '1.5.2.1.9': ('1.5.2.%s.9', '1'),
            '1.5.2.2.9': ('1.5.2.%s.9', '2'),
            '1.5.2.3.9': ('1.5.2.%s.9', '3'),
            '1.5.2.4.9': ('1.5.2.%s.9', '4'),
            '1.5.2.5.9': ('1.5.2.%s.9', '5'),
        },
        [
            ('1.5.2.1.7', '1.5.2.1.8'),
            ('1.5.2.2.7', '1.5.2.2.8'),
            ('1.5.2.3.7', '1.5.2.3.8'),
            ('1.5.2.4.7', '1.5.2.4.8'),
            ('1.5.2.5.7', '1.5.2.5.8'),
        ],
    )
    assert res == exp
