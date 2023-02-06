import json
import os
import subprocess
import sys
import time

# import time
from passport.infra.recipes.kolmogor.common import (
    check_started,
    gen_default_config,
    make_space,
    write_config,
)
import requests
import yatest.common as yc


SERVICE_TICKET = "3:serv:CBAQ__________9_IgYIlJEGEBs:Lr8FtdmjwGWin30Bj4h6wv9yRK1MrXaBKfChkVu-Il1w5xGXxdoODIAuaCiOrNJxA1OuV2TFyESMoI3aRwIn_OC_zlNJJNFwMO-B1FS1v4ilvAUxZh9ZkigJuD0eCczchIE76cKD3lIWqPwt1ZRkJ4P1lXIigvxj-mM-6i3Xgek"  # noqa
kolmo_bin = yc.build_path() + '/passport/infra/daemons/kolmogor/daemon/kolmogor'
env = os.environ.copy()

OK_HEADERS = {
    "Content-type": "application/json",
    "X-Ya-Service-Ticket": SERVICE_TICKET,
}


def test_common_errors():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
    cfg1["component"]["spaces"].append(make_space())
    cfg1["component"]["spaces"][0]["allowed_client_id"] = [100500]
    write_config(config_path, cfg1)

    p = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    check_started(kolmo_url)

    r = requests.get(kolmo_url + "/2/qwe")
    assert r.status_code == 400, r.text
    assert r.text == '{"error":"Bad request: POST only allowed: GET"}'

    r = requests.post(kolmo_url + "/2/inc")
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: Content-type must be 'application\\/json'. Got ''"}"""

    r = requests.post(kolmo_url + "/2/inc", data='', headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == '{"error":"Bad request: Invalid json"}'

    r = requests.post(kolmo_url + "/2/erase", data='', headers=OK_HEADERS)
    assert r.status_code == 501, r.text
    assert r.text == '{"error":"Not implemented: Path: \\/2\\/erase"}'

    data = {'test_space': {'keys': ['bar']}}
    r = requests.post(kolmo_url + "/2/get?foo=bar&foo=kek", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: Duplicated args are not supporeted, got several values of 'foo'"}"""

    p.send_signal(2)
    assert p.wait() == 0


def test_get_errors():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
    cfg1["component"]["spaces"].append(make_space())
    cfg1["component"]["spaces"][0]["allowed_client_id"] = [100500]
    cfg1["component"]["spaces"].append(make_space(name="untouchable"))
    cfg1["component"]["spaces"][1]["allowed_client_id"] = [42]
    write_config(config_path, cfg1)

    p = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    check_started(kolmo_url)

    data = {}
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: There is no one space in request"}"""

    data = {'foo': {}}
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: In space 'foo' must be array 'keys'"}"""

    data = {'foo': {'keys': {}}}
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: In space 'foo' must be array 'keys'"}"""

    data = {'foo': {'keys': {}}}
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: In space 'foo' must be array 'keys'"}"""

    data = {'foo': {'keys': []}}
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: There is no one key for space 'foo'"}"""

    data = {'foo': {'keys': [42]}}
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: Expecting array of strings in keys for 'foo'. Got number"}"""

    data = {
        'foo': {
            'keys': [
                'bar',
                'kek',
            ]
        }
    }
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: Space is not found (get): foo"}"""

    data = {
        'test_space': {
            'keys': [
                'bar',
                'kek',
            ]
        }
    }
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert r.text == """{"test_space":{"bar":{"value":0},"kek":{"value":0}}}"""

    data = {
        'untouchable': {
            'keys': [
                'bar',
                'kek',
            ]
        }
    }
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 403, r.text
    assert (
        r.text
        == """{"error":"Authorization failed: Service ticket is not allowed for 'untouchable'. Your tvm_id: 100500"}"""
    )

    p.send_signal(2)
    assert p.wait() == 0


def test_inc_errors():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
    cfg1["component"]["spaces"].append(make_space())
    cfg1["component"]["spaces"][0]["allowed_client_id"] = [100500]
    cfg1["component"]["spaces"].append(make_space(name="untouchable"))
    cfg1["component"]["spaces"][1]["allowed_client_id"] = [42]
    write_config(config_path, cfg1)

    p = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    check_started(kolmo_url)

    data = {}
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: There is no one space in request"}"""

    data = {
        'foo': {},
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: Value must be array for space 'foo'"}"""

    data = {
        'foo': [],
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: There is no one key for space 'foo'"}"""

    data = {
        'foo': [
            {
                'keys': {},
            },
        ],
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: In every object for space 'foo' must be array 'keys'"}"""

    data = {
        'foo': [
            {
                'keys': [
                    42,
                ],
            },
        ],
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: Expecting array of strings 'foo'. Got number"}"""

    data = {
        'foo': [
            {
                'keys': [
                    "bar",
                ],
            },
        ],
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: Space is not found (inc): foo"}"""

    data = {
        'untouchable': [
            {
                'keys': [
                    'bar',
                    'kek',
                ],
            }
        ],
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 403, r.text
    assert (
        r.text
        == """{"error":"Authorization failed: Service ticket is not allowed for 'untouchable'. Your tvm_id: 100500"}"""
    )

    data = {
        'test_space': [
            {
                'keys': ['zxc'],
                'inc_if_less_than': True,
            },
        ],
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: 'inc_if_less_than' must be uint64. Got bool"}"""

    data = {
        'test_space': [
            {
                'keys': ['zxc', 'zxc'],
                'inc_if_less_than': 10,
            },
            {
                'keys': ['asd', 'zxc'],
            },
        ],
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert (
        r.text
        == """{"error":"Bad request: key 'zxc' was used in several keysets and with 'inc_if_less_than'; this scenerio is not supported"}"""
    )

    p.send_signal(2)
    assert p.wait() == 0


def test_solo_base():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
    cfg1["component"]["spaces"].append(make_space())
    write_config(config_path, cfg1)

    p = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    check_started(kolmo_url)

    data = {
        'test_space': {
            'keys': ['asd', 'qwe', 'zxc'],
        },
    }
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert r.text == '{"test_space":{"asd":{"value":0},"qwe":{"value":0},"zxc":{"value":0}}}'

    data = {
        'test_space': [
            {
                'keys': ['qwe'],
            }
        ],
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert r.text == '{"test_space":{"qwe":{"value":1}}}'

    data = {
        'test_space': {
            'keys': ['asd', 'qwe', 'zxc'],
        },
    }
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert r.text == '{"test_space":{"asd":{"value":0},"qwe":{"value":1},"zxc":{"value":0}}}'

    data = {
        'test_space': [
            {
                'keys': ['qwe', 'zxc'],
            }
        ],
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {"test_space": {"qwe": {"value": 2}, "zxc": {"value": 1}}}

    # api v1 compatability
    r = requests.post(kolmo_url + "/inc?space=test_space&keys=qwe,zxc")
    assert r.status_code == 200, r.text
    assert r.text == 'OK\n'

    r = requests.get(kolmo_url + "/get?space=test_space&keys=asd,qwe,zxc")
    assert r.status_code == 200, r.text
    assert r.text == '0,3,2\n'

    data = {
        'test_space': {
            'keys': ['asd', 'qwe', 'zxc'],
        },
    }
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert r.text == '{"test_space":{"asd":{"value":0},"qwe":{"value":3},"zxc":{"value":2}}}'

    data = {
        'test_space': [
            {
                'keys': ['qwe', 'zxc'],
            }
        ],
        'missing_space': [
            {
                'keys': ['abc', 'def'],
            }
        ],
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == '{"error":"Bad request: Space is not found (inc): missing_space"}'

    data = {
        'test_space': {
            'keys': ['asd', 'qwe', 'zxc'],
        },
    }
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert r.text == '{"test_space":{"asd":{"value":0},"qwe":{"value":3},"zxc":{"value":2}}}'

    p.send_signal(2)
    assert p.wait() == 0


def test_solo_multispace():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
    cfg1["component"]["spaces"].append(make_space())
    cfg1["component"]["spaces"].append(make_space(name="test_space_2"))
    write_config(config_path, cfg1)

    p = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    check_started(kolmo_url)

    data = {
        'test_space': {
            'keys': ['asd', 'qwe', 'qwe', 'zxc', 'asd2', 'qwe2', 'zxc2'],
        },
        'test_space_2': {
            'keys': ['asd', 'qwe', 'asd2', 'qwe2', 'zxc2', 'zxc', 'asd2', 'qwe2', 'zxc2'],
        },
    }
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert (
        r.text
        == '{"test_space":{"asd":{"value":0},"asd2":{"value":0},"qwe":{"value":0},"qwe2":{"value":0},"zxc":{"value":0},"zxc2":{"value":0}},'
        '"test_space_2":{"asd":{"value":0},"asd2":{"value":0},"qwe":{"value":0},"qwe2":{"value":0},"zxc":{"value":0},"zxc2":{"value":0}}}'
    )

    data = {
        'test_space': [
            {
                'keys': ['zxc', 'zxc'],
            },
            {
                'keys': ['asd', 'zxc'],
            },
        ],
        'test_space_2': [
            {
                'keys': ['qwe2'],
            }
        ],
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {
        "test_space": {"asd": {"value": 1}, "zxc": {"value": 3}},
        "test_space_2": {"qwe2": {"value": 1}},
    }

    data = {
        'test_space': {
            'keys': ['asd', 'qwe', 'zxc', 'asd2', 'qwe2', 'zxc2'],
        },
        'test_space_2': {
            'keys': ['asd', 'qwe', 'zxc', 'asd2', 'qwe2', 'zxc2'],
        },
    }
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert (
        r.text
        == '{"test_space":{"asd":{"value":1},"asd2":{"value":0},"qwe":{"value":0},"qwe2":{"value":0},"zxc":{"value":3},"zxc2":{"value":0}},'
        '"test_space_2":{"asd":{"value":0},"asd2":{"value":0},"qwe":{"value":0},"qwe2":{"value":1},"zxc":{"value":0},"zxc2":{"value":0}}}'
    )

    p.send_signal(2)
    assert p.wait() == 0


def test_inc_if_less_than():
    config_path1 = './1.cfg'
    cfg1, kolmo_url_1 = gen_default_config()
    cfg1["component"]["spaces"].append(make_space())
    cfg1["component"]["spaces"].append(make_space(name="test_space_2"))

    config_path2 = './2.cfg'
    cfg2, kolmo_url_2 = gen_default_config()
    cfg2["component"]["logger"]["file"] = './2.log'
    cfg2["component"]["spaces"].append(make_space())
    cfg2["component"]["spaces"].append(make_space(name="test_space_2"))

    cfg1["component"]["replication"]["dest"].append("localhost:%d" % cfg1["component"]["replication"]["port"])
    cfg1["component"]["replication"]["dest"].append("localhost:%d" % cfg2["component"]["replication"]["port"])
    cfg2["component"]["replication"]["dest"].append("localhost:%d" % cfg1["component"]["replication"]["port"])
    cfg2["component"]["replication"]["dest"].append("localhost:%d" % cfg2["component"]["replication"]["port"])

    write_config(config_path1, cfg1)
    write_config(config_path2, cfg2)

    p1 = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path1,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    p2 = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path2,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    # start second
    check_started(kolmo_url_1)
    check_started(kolmo_url_2)
    time.sleep(3)  # to init replication

    data = {
        'test_space': [{'keys': ['asd', 'asd', 'asd', 'asd']}],
        'test_space_2': [{'keys': ['asd', 'asd', 'asd', 'asd', 'asd', 'qwe', 'qwe', 'qwe']}],
    }
    r = requests.post(kolmo_url_1 + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {
        "test_space": {"asd": {"value": 4}},
        "test_space_2": {"asd": {"value": 5}, "qwe": {"value": 3}},
    }

    data = {
        'test_space': [
            {'keys': ['asd', 'asd', 'asd'], 'inc_if_less_than': 5},
            {'keys': ['qwe', 'qwe', 'qwe', 'qwe', 'qwe'], 'inc_if_less_than': 4},
        ],
        'test_space_2': [{'keys': ['asd', 'asd', 'asd', 'asd', 'asd', 'qwe', 'qwe', 'qwe']}],
    }
    r = requests.post(kolmo_url_1 + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {
        "test_space": {
            "asd": {"value": 5, 'was_incremented': True},
            "qwe": {"value": 4, 'was_incremented': True},
        },
        "test_space_2": {"asd": {"value": 10}, "qwe": {"value": 6}},
    }

    data = {
        'test_space': [
            {'keys': ['asd', 'asd', 'asd'], 'inc_if_less_than': 15},
            {'keys': ['qwe', 'qwe', 'qwe'], 'inc_if_less_than': 20},
        ],
        'test_space_2': [{'keys': ['asd', 'asd', 'asd', 'asd', 'asd', 'qwe', 'qwe', 'qwe']}],
    }
    r = requests.post(kolmo_url_1 + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {
        "test_space": {
            "asd": {"value": 8, 'was_incremented': True},
            "qwe": {"value": 7, 'was_incremented': True},
        },
        "test_space_2": {"asd": {"value": 15}, "qwe": {"value": 9}},
    }

    data = {
        'test_space': [
            {'keys': ['asd', 'asd', 'asd'], 'inc_if_less_than': 8},
            {'keys': ['qwe', 'qwe', 'qwe'], 'inc_if_less_than': 3},
        ],
        'test_space_2': [{'keys': ['asd', 'asd', 'asd', 'asd', 'asd', 'qwe', 'qwe', 'qwe']}],
    }
    r = requests.post(kolmo_url_1 + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {
        "test_space": {
            "asd": {"value": 8, 'was_incremented': False},
            "qwe": {"value": 7, 'was_incremented': False},
        },
        "test_space_2": {"asd": {"value": 20}, "qwe": {"value": 12}},
    }

    data = {
        'test_space': [
            {'keys': ['asd'], 'inc_if_less_than': 9},
        ],
    }
    r = requests.post(kolmo_url_1 + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {
        "test_space": {
            "asd": {"value": 9, 'was_incremented': True},
        },
    }

    # waiting replication
    time.sleep(1)

    data = {
        'test_space': {'keys': ['asd', 'qwe']},
        'test_space_2': {'keys': ['asd', 'qwe']},
    }
    r = requests.post(kolmo_url_1 + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert (
        r.text
        == '{"test_space":{"asd":{"value":9},"qwe":{"value":7}},"test_space_2":{"asd":{"value":20},"qwe":{"value":12}}}'
    )
    r = requests.post(kolmo_url_2 + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert (
        r.text
        == '{"test_space":{"asd":{"value":9},"qwe":{"value":7}},"test_space_2":{"asd":{"value":20},"qwe":{"value":12}}}'
    )

    p1.send_signal(2)
    p2.send_signal(2)
    assert p1.wait() == 0
    assert p2.wait() == 0


def test_limited():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
    cfg1["component"]["spaces"].append(make_space(memory_limit=256))
    write_config(config_path, cfg1)

    p = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    check_started(kolmo_url)

    data = {
        'test_space': {
            'keys': ['asd', 'qwe', 'zxc'],
        },
    }
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert r.text == '{"test_space":{"asd":{"value":0},"qwe":{"value":0},"zxc":{"value":0}}}'

    def check_sum(resp):
        resp = json.loads(resp)  # '{"test_space":{"zxc":{"value":0},"qwe":{"value":1},"asd":{"value":0}}}'
        count = 0
        for k in ['asd', 'qwe', 'zxc']:
            count += resp["test_space"][k]["value"]
        assert count == 1, resp

    data = {
        'test_space': [
            {
                'keys': ['asd', 'qwe', 'zxc'],
            }
        ],
    }
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    check_sum(r.text)

    data = {
        'test_space': {
            'keys': ['asd', 'qwe', 'zxc'],
        },
    }
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    check_sum(r.text)

    p.send_signal(2)
    assert p.wait() == 0


def test_debt_queue():
    config_path1 = './1.cfg'
    cfg1, kolmo_url_1 = gen_default_config()
    cfg1["component"]["spaces"].append(make_space())
    cfg1["component"]["spaces"].append(make_space(name="test_space_2"))

    config_path2 = './2.cfg'
    cfg2, kolmo_url_2 = gen_default_config()
    cfg2["component"]["logger"]["file"] = './2.log'
    cfg2["component"]["spaces"].append(make_space())
    cfg2["component"]["spaces"].append(make_space(name="test_space_2"))

    cfg1["component"]["replication"]["dest"].append("localhost:%d" % cfg1["component"]["replication"]["port"])
    cfg1["component"]["replication"]["dest"].append("localhost:%d" % cfg2["component"]["replication"]["port"])
    cfg2["component"]["replication"]["dest"].append("localhost:%d" % cfg1["component"]["replication"]["port"])
    cfg2["component"]["replication"]["dest"].append("localhost:%d" % cfg2["component"]["replication"]["port"])

    # 40 bytes (returned by ByteSizeLong protobuf method)
    inc_data = {"test_space": [{"keys": ["a", "b", "c"]}]}
    get_data = {"test_space": {"keys": ["a", "b", "c"]}}

    cfg1["component"]["replication"]["max_queue_size"] = 120  # can send <= 3 incs
    cfg2["component"]["replication"]["max_queue_size"] = 210  # can send <= 5 incs

    write_config(config_path1, cfg1)
    write_config(config_path2, cfg2)

    p1 = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path1,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    p2 = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path2,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    # start second
    check_started(kolmo_url_1)
    check_started(kolmo_url_2)

    def wait_sync_replication():
        sync_inc_data = {"test_space": [{"keys": ["sync"]}]}

        sync_get_data = {"test_space": {"keys": ["sync"]}}

        i = 0
        while i < 100:
            r1 = requests.post(kolmo_url_1 + "/2/get", data=json.dumps(sync_get_data), headers=OK_HEADERS)
            r2 = requests.post(kolmo_url_2 + "/2/get", data=json.dumps(sync_get_data), headers=OK_HEADERS)

            assert r1.status_code == 200, r1.text
            assert r2.status_code == 200, r2.text

            old_value1 = int(json.loads(r1.text)["test_space"]["sync"]["value"])
            old_value2 = int(json.loads(r2.text)["test_space"]["sync"]["value"])

            requests.post(kolmo_url_1 + "/2/inc", data=json.dumps(sync_inc_data), headers=OK_HEADERS)

            time.sleep(0.2)

            r1 = requests.post(kolmo_url_1 + "/2/get", data=json.dumps(sync_get_data), headers=OK_HEADERS)
            r2 = requests.post(kolmo_url_2 + "/2/get", data=json.dumps(sync_get_data), headers=OK_HEADERS)

            assert r1.status_code == 200, r1.text
            assert r2.status_code == 200, r2.text

            new_value1 = int(json.loads(r1.text)["test_space"]["sync"]["value"])
            new_value2 = int(json.loads(r2.text)["test_space"]["sync"]["value"])

            if new_value1 == old_value1 + 1 and new_value2 == old_value2 + 1:
                return
            time.sleep(0.2)
            i += 1
        assert False

    # init replication
    wait_sync_replication()

    # kill p2 to start collecting debt at p1
    p2.send_signal(2)
    assert p2.wait() == 0

    # after 3 incs debt should be full, so p2 will only get 3 incs
    for i in range(4):
        # each inc should be different item in debt queue
        time.sleep(0.5)

        r = requests.post(kolmo_url_1 + "/2/inc", data=json.dumps(inc_data), headers=OK_HEADERS)
        assert r.status_code == 200, r.text
        assert json.loads(r.text) == {
            "test_space": {"a": {"value": i + 1}, "b": {"value": i + 1}, "c": {"value": i + 1}},
        }

    r = requests.post(kolmo_url_1 + "/2/get", data=json.dumps(get_data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {
        "test_space": {"a": {"value": 4}, "b": {"value": 4}, "c": {"value": 4}},
    }

    # start p2
    p2 = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path2,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    check_started(kolmo_url_2)

    # wait until all debt will be send
    gotDebt = False
    i = 0
    while not gotDebt and i < 100:
        time.sleep(0.1)
        r = requests.post(kolmo_url_2 + "/2/get", data=json.dumps(get_data), headers=OK_HEADERS)
        assert r.status_code == 200, r.text

        if json.loads(r.text) == {"test_space": {"a": {"value": 3}, "b": {"value": 3}, "c": {"value": 3}}}:
            gotDebt = True

        i += 1

    assert gotDebt

    p1.send_signal(2)
    p2.send_signal(2)
    assert p1.wait() == 0
    assert p2.wait() == 0


def test_eraseall_errors():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
    cfg1["component"]["spaces"].append(make_space(name="test_space"))
    cfg1["component"]["spaces"][0]["erase_count"] = 1024
    write_config(config_path, cfg1)

    p = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    check_started(kolmo_url)

    data = {"spice": "testt"}
    r = requests.post(kolmo_url + "/2/eraseall", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: Failed to get 'space' from request"}"""

    data = {"space": 79}
    r = requests.post(kolmo_url + "/2/eraseall", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: Failed to get 'space' from request"}"""

    data = {"space": "dds"}
    r = requests.post(kolmo_url + "/2/eraseall", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 400, r.text
    assert r.text == """{"error":"Bad request: Space is not found (eraseall): dds"}"""

    p.send_signal(2)
    assert p.wait() == 0


def test_eraseall():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
    cfg1["component"]["spaces"].append(make_space(name="test_space"))
    cfg1["component"]["spaces"].append(make_space(name="test_space2"))
    cfg1["component"]["spaces"][0]["erase_count"] = 1024
    cfg1["component"]["spaces"][1]["erase_count"] = 512

    write_config(config_path, cfg1)

    p = subprocess.Popen(
        [
            kolmo_bin,
            '-c',
            config_path,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    check_started(kolmo_url)

    data = {
        "test_space": [{"keys": ["abc", "ing", "kek", "abc", "kek"]}],
        "test_space2": [{"keys": ["abc", "def", "yan", "dex", "yan"]}],
    }

    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {
        "test_space": {"kek": {"value": 2}, "ing": {"value": 1}, "abc": {"value": 2}},
        "test_space2": {"dex": {"value": 1}, "def": {"value": 1}, "yan": {"value": 2}, "abc": {"value": 1}},
    }

    data = {"space": "test_space"}

    r = requests.post(kolmo_url + "/2/eraseall", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {"test_space": {"keys": 3}}

    data = {
        "test_space": {"keys": ["abc", "ing", "kek", "abc", "kek"]},
        "test_space2": {"keys": ["abc", "def", "yan", "dex", "yan"]},
    }

    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {
        "test_space": {"abc": {"value": 0}, "ing": {"value": 0}, "kek": {"value": 0}},
        "test_space2": {"abc": {"value": 1}, "def": {"value": 1}, "dex": {"value": 1}, "yan": {"value": 2}},
    }

    data = {"test_space": [{"keys": ["ing", "ing", "kek", "fft", "xor"]}]}
    r = requests.post(kolmo_url + "/2/inc", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {
        "test_space": {"kek": {"value": 1}, "ing": {"value": 2}, "fft": {"value": 1}, "xor": {"value": 1}}
    }

    data = {"space": "test_space2"}
    r = requests.post(kolmo_url + "/2/eraseall", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {"test_space2": {"keys": 4}}

    data = {
        "test_space": {"keys": ["abc", "ing", "kek", "abc", "kek", "fft", "xor"]},
        "test_space2": {"keys": ["abc", "def", "yan", "dex", "yan"]},
    }

    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {
        "test_space": {
            "abc": {"value": 0},
            "ing": {"value": 2},
            "kek": {"value": 1},
            "fft": {"value": 1},
            "xor": {"value": 1},
        },
        "test_space2": {"abc": {"value": 0}, "def": {"value": 0}, "dex": {"value": 0}, "yan": {"value": 0}},
    }

    data = {"space": "test_space"}
    r = requests.post(kolmo_url + "/2/eraseall", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {"test_space": {"keys": 5}}

    data = {
        "test_space": {"keys": ["abc", "ing", "kek", "abc", "kek", "fft", "xor"]},
        "test_space2": {"keys": ["abc", "def", "yan", "dex", "yan"]},
    }
    r = requests.post(kolmo_url + "/2/get", data=json.dumps(data), headers=OK_HEADERS)
    assert r.status_code == 200, r.text
    assert json.loads(r.text) == {
        "test_space": {
            "abc": {"value": 0},
            "ing": {"value": 0},
            "kek": {"value": 0},
            "fft": {"value": 0},
            "xor": {"value": 0},
        },
        "test_space2": {"abc": {"value": 0}, "def": {"value": 0}, "dex": {"value": 0}, "yan": {"value": 0}},
    }

    p.send_signal(2)
    assert p.wait() == 0
