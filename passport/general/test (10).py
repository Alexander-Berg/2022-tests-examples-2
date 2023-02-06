import os
import subprocess
import sys
import time

from passport.infra.recipes.kolmogor.common import (
    check_started,
    gen_default_config,
    make_space,
    write_config,
)
import requests
import yatest.common as yc


SERVICE_TICKET = "3:serv:CBAQ__________9_IgYIlJEGEBs:Lr8FtdmjwGWin30Bj4h6wv9yRK1MrXaBKfChkVu-Il1w5xGXxdoODIAuaCiOrNJxA1OuV2TFyESMoI3aRwIn_OC_zlNJJNFwMO-B1FS1v4ilvAUxZh9ZkigJuD0eCczchIE76cKD3lIWqPwt1ZRkJ4P1lXIigvxj-mM-6i3Xgek"  # noqa
SERVICE_TICKET_BAD = "3:malformed"
SERVICE_TICKET_DISALLOWED = "3:serv:CBAQ__________9_IgYIlZEGEBs:N0bsFs7TCStzD1kJBqsfpDoNHCD5pKErKp0k5ZWhblBVGdw59dbxXfLnnRxqVK4Ui1im9ZXX-KtvRuRqR-qqdVz21njKiIzL5frrRyUvtwtBVHzUwRAi3hTo724fcdn62sZnOnmmuqERnYfChagFUz_EaMMp7XR3R8nsW6wl4PA"  # noqa
kolmo_bin = yc.build_path() + '/passport/infra/daemons/kolmogor/daemon/kolmogor'
env = os.environ.copy()

OK_AUTH_HEADER = {"X-Ya-Service-Ticket": SERVICE_TICKET}


def test_missing_config():
    p = subprocess.Popen(
        [
            kolmo_bin,
            'missing_config',
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )
    assert p.wait() == 1


def test_bad_config():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
    cfg1["component"] = None
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
    assert p.wait() == 1


def test_SIGINT():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
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
    p.send_signal(2)
    assert p.wait() == 0


def test_SIGTERM():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
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
    p.send_signal(15)
    assert p.wait() == 0


def test_SIGHUP():
    log1 = './1.log'
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
    cfg1["component"]["logger"]["file"] = log1
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
    assert os.path.isfile(log1)
    os.remove(log1)
    assert not os.path.isfile(log1)
    p.send_signal(1)

    idx = 0
    while not os.path.isfile(log1) and ++idx < 4:
        time.sleep(1)
    assert os.path.isfile(log1)

    p.send_signal(2)
    assert p.wait() == 0


def test_force_down():
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

    r = requests.get(kolmo_url + "/ping")
    assert r.status_code == 200, r.text
    open(cfg1["component"]["misc"]["force_down_file"], 'a').close()

    r = requests.get(kolmo_url + "/ping")
    assert r.status_code == 503
    os.remove(cfg1["component"]["misc"]["force_down_file"])

    r = requests.get(kolmo_url + "/ping")
    assert r.status_code == 200, r.text

    p.send_signal(2)
    assert p.wait() == 0


def test_errors_auth():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
    cfg1["component"]["spaces"].append(make_space(allowed_client_id=100500))
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

    # no ServiceTicket (get)
    r = requests.get(kolmo_url + "/get?space=test_space&keys=asd,qwe,zxc")
    assert r.status_code == 403, r.text
    assert r.text == "Authorization failed: Service ticket required but not found for 'test_space'\n"

    r = requests.get(kolmo_url + "/get?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text

    # no ServiceTicket (inc)
    r = requests.get(kolmo_url + "/inc?space=test_space&keys=asd,qwe,zxc")
    assert r.status_code == 403, r.text
    assert r.text == "Authorization failed: Service ticket required but not found for 'test_space'\n"

    r = requests.get(kolmo_url + "/inc?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text

    # malformed ServiceTicket
    r = requests.get(
        kolmo_url + "/inc?space=test_space&keys=asd,qwe,zxc", headers={"X-Ya-Service-Ticket": SERVICE_TICKET_BAD}
    )
    assert r.status_code == 403, r.text
    assert r.text == "Authorization failed: Invalid service ticket. Invalid ticket type: 3:\n"

    # src is not allowed
    r = requests.get(
        kolmo_url + "/inc?space=test_space&keys=asd,qwe,zxc", headers={"X-Ya-Service-Ticket": SERVICE_TICKET_DISALLOWED}
    )
    assert r.status_code == 403, r.text
    assert r.text == "Authorization failed: Service ticket is not allowed for 'test_space'. Your tvm_id: 100501\n"

    p.send_signal(2)
    assert p.wait() == 0


def test_errors():
    config_path = './1.cfg'
    cfg1, kolmo_url = gen_default_config()
    cfg1["component"]["spaces"].append(make_space(allowed_client_id=100500))
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

    r = requests.get(kolmo_url + "/qwe")
    assert r.status_code == 400, r.text
    assert r.text == 'Error: Path is unknown: /qwe\n'

    r = requests.get(kolmo_url + "/inc?keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 400, r.text
    assert r.text == "Error: arg is empty: 'space'\n"

    r = requests.get(kolmo_url + "/inc?space=foo&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 400, r.text
    assert r.text == 'Error: Space is not found (inc): foo\n'

    r = requests.get(kolmo_url + "/erase?space=foo&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 400, r.text
    assert r.text == 'Error: Space is not found (erase): foo\n'

    r = requests.get(kolmo_url + "/erase?space=test_space&keys=asd,qwe,zxc", headers={"X-Ya-Service-Ticket": "qwerty"})
    assert r.status_code == 403, r.text
    assert r.text == 'Authorization failed: Invalid service ticket. Malformed ticket: qwerty\n'

    r = requests.request('OPTIONS', kolmo_url + "/inc")
    assert r.status_code == 400, r.text
    assert r.text == 'POST and GET only allowed: OPTIONS.\n'

    r = requests.get(kolmo_url + "/get?space=test_space&keys=asd&keys=qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 400, r.text
    assert r.text == "Error: Duplicated args are not supporeted, got several values of 'keys'\n"

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

    r = requests.get(kolmo_url + "/get?space=test_space&keys=asd,qwe,zxc")
    assert r.status_code == 200, r.text
    assert r.text == '0,0,0\n'

    r = requests.get(kolmo_url + "/inc?space=test_space&keys=qwe")
    assert r.status_code == 200, r.text
    assert r.text == 'OK\n'

    r = requests.post(kolmo_url + "/get?space=test_space&keys=asd,qwe,zxc")
    assert r.status_code == 200, r.text
    assert r.text == '0,1,0\n'

    r = requests.post(kolmo_url + "/inc?space=test_space&keys=qwe,zxc")
    assert r.status_code == 200, r.text
    assert r.text == 'OK\n'

    r = requests.get(kolmo_url + "/get?space=test_space&keys=asd,qwe,zxc")
    assert r.status_code == 200, r.text
    assert r.text == '0,2,1\n'

    r = requests.get(kolmo_url + "/get?space=test_space&keys=asd,qwe,zxc,asd,qwe,zxc")
    assert r.status_code == 200, r.text
    assert r.text == '0,2,1,0,2,1\n'

    r = requests.get(kolmo_url + "/erase?space=test_space&keys=qwe")
    assert r.status_code == 403, r.text
    assert r.text == "Authorization failed: Auth was not configured for space 'test_space'\n"

    r = requests.get(kolmo_url + "/get?space=test_space&keys=asd,qwe,zxc")
    assert r.status_code == 200, r.text
    assert r.text == '0,2,1\n'

    p.send_signal(2)
    assert p.wait() == 0


def test_pair():
    config_path1 = './1.cfg'
    cfg1, kolmo_url_1 = gen_default_config()
    cfg1["component"]["logger"]["file"] = './1.log'
    cfg1["component"]["spaces"].append(make_space(allowed_client_id=100500))
    cfg1["component"]["spaces"].append(make_space(name="foo", allowed_client_id=100500))

    config_path2 = './2.cfg'
    cfg2, kolmo_url_2 = gen_default_config()
    cfg2["component"]["logger"]["file"] = './2.log'
    cfg2["component"]["spaces"].append(make_space(allowed_client_id=100500))
    cfg2["component"]["spaces"].append(make_space(name="foo", allowed_client_id=100500))

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

    # solo operation
    check_started(kolmo_url_1)
    r = requests.get(kolmo_url_1 + "/inc?space=test_space&keys=qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    r = requests.get(kolmo_url_1 + "/erase?space=test_space&keys=zxc", headers=OK_AUTH_HEADER)
    assert r.text.startswith('localhost:%s:status_code=UNAVAILABLE; message' % cfg2["component"]["replication"]["port"])
    assert r.status_code == 206

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
    check_started(kolmo_url_2)
    time.sleep(3)

    r = requests.get(kolmo_url_1 + "/get?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '0,1,0\n'
    r = requests.get(kolmo_url_2 + "/get?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '0,0,0\n'

    # test replication 1 -> 2
    r = requests.get(kolmo_url_1 + "/inc?space=test_space&keys=qwe", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    time.sleep(1)
    r = requests.get(kolmo_url_1 + "/get?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '0,2,0\n'
    r = requests.get(kolmo_url_2 + "/get?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '0,1,0\n'

    r = requests.get(kolmo_url_1 + "/erase?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.text == 'OK\n'
    assert r.status_code == 200, r.text
    r = requests.get(kolmo_url_1 + "/get?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '0,0,0\n'
    r = requests.get(kolmo_url_2 + "/get?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '0,0,0\n'

    # test replication 2 -> 1
    r = requests.get(kolmo_url_2 + "/inc?space=test_space&keys=asd", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    r = requests.get(kolmo_url_2 + "/inc?space=test_space&keys=asd", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    r = requests.get(kolmo_url_2 + "/inc?space=test_space&keys=asd", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    time.sleep(1)
    r = requests.get(kolmo_url_1 + "/get?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '3,0,0\n'
    r = requests.get(kolmo_url_2 + "/get?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '3,0,0\n'

    r = requests.get(kolmo_url_2 + "/erase?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.text == 'OK\n'
    assert r.status_code == 200, r.text
    r = requests.get(kolmo_url_1 + "/get?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '0,0,0\n'
    r = requests.get(kolmo_url_2 + "/get?space=test_space&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '0,0,0\n'

    # switch to 'foo'
    r = requests.get(kolmo_url_1 + "/inc?space=foo&keys=qwe", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    time.sleep(3)

    r = requests.get(kolmo_url_1 + "/get?space=foo&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '0,1,0\n'
    r = requests.get(kolmo_url_2 + "/get?space=foo&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '0,1,0\n'

    # stop 1
    p1.send_signal(2)
    assert p1.wait() == 0
    time.sleep(3)

    r = requests.get(kolmo_url_2 + "/inc?space=foo&keys=zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    r = requests.get(kolmo_url_2 + "/inc?space=foo&keys=zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    r = requests.get(kolmo_url_2 + "/inc?space=foo&keys=zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    r = requests.get(kolmo_url_2 + "/inc?space=foo&keys=zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text

    # start 1
    cfg1["component"]["spaces"].pop(0)
    assert cfg1["component"]["spaces"][0]["name"] == "foo"
    write_config(config_path1, cfg1)
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
    check_started(kolmo_url_1)

    __tries = 0
    while (
        requests.get(kolmo_url_1 + "/get?space=foo&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER).text != '0,0,4\n'
        and __tries < 30
    ):
        __tries += 1
        time.sleep(1)

    # 2 sent debt for 1
    r = requests.get(kolmo_url_1 + "/get?space=foo&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '0,0,4\n'
    r = requests.get(kolmo_url_2 + "/get?space=foo&keys=asd,qwe,zxc", headers=OK_AUTH_HEADER)
    assert r.status_code == 200, r.text
    assert r.text == '0,1,4\n'

    p1.send_signal(2)
    p2.send_signal(2)
    assert p1.wait() == 0
    assert p2.wait() == 0
