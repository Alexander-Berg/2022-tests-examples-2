import json
import os.path

import yatest
from noc.grad.grad.lib import snmp_helper
from noc.grad.grad.lib.structures import Mapdata
from noc.grad.grad.lib.scheduler import Job
from noc.grad.grad.lib.snmp_helper import Oid
from noc.grad.grad.lib.structures import FrozenDict

MIBS = {
    "TESTMIB": {
        "1.2.1": {"name": "name", "type": "key"},
        "1.2.2": {"name": "port", "type": "key"},
        "1.3.3": {"name": "ip", "type": "key", "alias": "address"},
        "1.3.4": {"name": "rx", "type": "value", "fn": "delta"},
        "1.3.6": {"name": "cps", "type": "value", "fn": "delta"},
        "1.3.5": {"name": "tx", "type": "value", "fn": "delta"},
    },
    "TESTMIB2": {
        "1.5.1": {"name": "name", "type": "key"},
        "1.5.2.%s.8": {"name": "value", "type": "value", "fn": "delta"},
        "1.5.2.%s.9": {"name": "value", "type": "value", "fn": "delta"},
        "1.5.3": {"name": "value2", "type": "value", "fn": "delta"},
    },
}


def get_testdata(filename: str, test_data_dir="noc/grad/grad/test/data") -> bytes:
    test_data = yatest.common.source_path(test_data_dir)
    with open(os.path.join(test_data, filename), "rb") as f:
        return f.read()


def get_data_content(file_name, is_json=False):
    res = get_testdata(file_name)
    if is_json:
        res = json.loads(res)
    return res


def get_kvts_data_content(file_name: str):
    return wrap_from_json_to_mapdata(get_data_content(file_name=file_name, is_json=True))


def wrap_from_json_to_mapdata(data: list) -> Mapdata:
    return [tuple(i) for i in data]


def prepare_data(poll_count, ifcount):
    ts = 60
    polls_raw = []
    for _ in range(poll_count):  # poll count
        raw = []
        for index in range(ifcount):
            host = "testhost"
            raw.append((host, "1.2.1", ts, str(index), "ifname%s" % index))
            raw.append((host, "1.3.4", ts, str(index), ts * 100))
            raw.append((host, "1.3.5", ts, str(index), ts * 100))
            raw.append((host, "1.3.6", ts, str(index), ts))
        ts += 60
        polls_raw.append(raw)

    # group by mib
    polls_mib = []
    for data in polls_raw:
        pm = {}
        polls_mib.append(pm)
        for i in data:
            if i[0] not in pm:
                pm[i[0]] = {}
            if i[1] not in pm[i[0]]:
                pm[i[0]][i[1]] = []
            pm[i[0]][i[1]].append((i[2], i[3], i[4]))
    return polls_mib


def make_job(counters=tuple()):
    if not counters:
        counters = (Oid("TESTMIB.rx", tuple()), Oid("TESTMIB.tx", tuple()))
    res = Job(name="test job", key_data=FrozenDict({"interval": 60}))
    res.set_context(
        {
            "skip_key_cache": {},
            "keep_index": False,
            "index_to_seq": False,
            "keys_cache": {},
            "keys_hash": {},
            "poll_type": ["data", "index"],
            "key_fn_res_cache": {},
            "resolved_counters": snmp_helper.resolve_counters(counters),
        }
    )
    return res
