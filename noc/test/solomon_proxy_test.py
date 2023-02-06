import asyncio
from copy import deepcopy

import solomon_telegraf_proxy
from noc.grad.grad.lib.solomon_proxy_functions import telegraf_to_solomon, from_buf_to_q, DEFAULT_CLUSTER

solomon_telegraf_proxy.BUF_SLEEP = 1


def get_q_data(data, project, cluster):
    inq = asyncio.Queue()
    outq = asyncio.Queue()
    inq.put_nowait((data, project, cluster))

    async def task():
        c = from_buf_to_q(inq, outq, solomon_token="test")
        try:
            await asyncio.wait_for(c, timeout=2)
        except Exception:
            pass

    asyncio.get_event_loop().run_until_complete(task())
    res = []
    while outq.qsize():
        res.append(outq.get_nowait())
    return res


def test_data1():
    indata = [
        {
            "fields": {"party_index": 3},
            "name": "server_zk",
            "tags": {
                "_cluster": "auto_DC",
                "_db": "grad",
                "host": "sas1-grad1",
                "identifier": "sas1-grad1.yndx.net",
                "path": "/grad/server",
            },
            "timestamp": 1627640343,
        },
        {
            "fields": {"bytes": 9249803279},
            "name": "iptables",
            "tags": {
                "_db": "grad",
                "chain": "OUTPUT",
                "host": "sas1-grad1",
                "iptables": "ip6tables",
                "ruleid": "snmp_out",
                "table": "filter",
                "target": "ACCEPT",
            },
            "timestamp": 1627641724,
        },
        {
            "fields": {"party_size": 6},
            "name": "server_zk",
            "tags": {
                "_cluster": "auto_DC",
                "_db": "grad",
                "host": "sas1-grad1",
                "identifier": "sas1-grad1.yndx.net",
                "path": "/grad/server",
            },
            "timestamp": 1627640343,
        },
    ]
    indata = {"metrics": indata}
    exp = {
        ('grad', 'all', 'iptables'): {
            'commonLabels': {},
            'sensors': [
                {
                    'labels': {
                        'chain': 'OUTPUT',
                        'host': 'sas1-grad1',
                        'iptables': 'ip6tables',
                        'ruleid': 'snmp_out',
                        'sensor': 'bytes',
                        'table': 'filter',
                        'target': 'ACCEPT',
                    },
                    'ts': 1627641724,
                    'value': 9249803279.0,
                }
            ],
        },
        ('grad', 'sas', 'server_zk'): {
            'commonLabels': {},
            'sensors': [
                {
                    'labels': {
                        'host': 'sas1-grad1',
                        'identifier': 'sas1-grad1.yndx.net',
                        'path': '/grad/server',
                        'sensor': 'party_index',
                    },
                    'ts': 1627640343,
                    'value': 3.0,
                },
                {
                    'labels': {
                        'host': 'sas1-grad1',
                        'identifier': 'sas1-grad1.yndx.net',
                        'path': '/grad/server',
                        'sensor': 'party_size',
                    },
                    'ts': 1627640343,
                    'value': 6.0,
                },
            ],
        },
    }
    res = telegraf_to_solomon(deepcopy(indata))
    assert res == exp
    res2 = get_q_data(deepcopy(indata), "project", DEFAULT_CLUSTER)
    exp2 = [
        'http://solomon.yandex.net/api/v2/push?project=grad&cluster=sas&service=server_zk',
        'http://solomon.yandex.net/api/v2/push?project=grad&cluster=all&service=iptables',
    ]
    assert [x[0] for x in res2] == exp2
